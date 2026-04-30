from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Sequence

import numpy as np
import pandas as pd
from joblib import load

from src.baseline_models import MODEL_FILE_NAMES


DEFAULT_ENSEMBLE_SEEDS = (42, 7, 13, 99, 21)
ROOT_DIR = Path(__file__).resolve().parent.parent

_LOADED_BASELINE_ENSEMBLE: BaselineEnsemble | None = None


def _coerce_input_features(input_features: np.ndarray) -> np.ndarray:
    """Normalize input features to a 2D array while preserving mixed tabular dtypes."""
    features = np.asarray(input_features)
    if features.ndim == 1:
        return features.reshape(1, -1)
    if features.ndim != 2:
        raise ValueError("input_features must be a 1D feature vector or 2D feature matrix")
    return features


def _prepare_model_input(model: Any, input_features: np.ndarray) -> pd.DataFrame | np.ndarray:
    """Rebuild a DataFrame when the saved pipeline was fitted with named columns."""
    if isinstance(input_features, pd.DataFrame):
        return input_features.copy()

    features = _coerce_input_features(input_features)
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is None and hasattr(model, "named_steps"):
        preprocessor = model.named_steps.get("preprocessor")
        feature_names = getattr(preprocessor, "feature_names_in_", None)

    if feature_names is None:
        return features

    if features.shape[1] != len(feature_names):
        raise ValueError(
            f"Expected {len(feature_names)} features but received {features.shape[1]}"
        )
    return pd.DataFrame(features, columns=list(feature_names))


def _predict_with_model(model: Any, input_features: np.ndarray) -> np.ndarray:
    """Run model prediction and return a flat float array."""
    prepared_features = _prepare_model_input(model, input_features)
    predictions = np.asarray(model.predict(prepared_features), dtype=np.float64).ravel()
    if predictions.size == 0:
        raise ValueError("Model returned no predictions")
    return predictions


def _normalize_weights(
    model_names: Sequence[str],
    weights: Mapping[str, float] | None,
) -> Dict[str, float]:
    """Validate and normalize ensemble weights."""
    ordered_names = list(model_names)
    if not ordered_names:
        raise ValueError("At least one model is required for ensembling")

    if weights is None:
        equal_weight = 1.0 / len(ordered_names)
        return {name: equal_weight for name in ordered_names}

    unknown_names = sorted(set(weights) - set(ordered_names))
    if unknown_names:
        raise ValueError(f"Unknown model weight keys: {unknown_names}")

    missing_names = [name for name in ordered_names if name not in weights]
    if missing_names:
        raise ValueError(f"Missing weights for models: {missing_names}")

    ordered_weights = np.asarray([float(weights[name]) for name in ordered_names], dtype=np.float64)
    if np.any(ordered_weights < 0):
        raise ValueError("Ensemble weights must be non-negative")

    weight_sum = float(np.sum(ordered_weights))
    if weight_sum <= 0:
        raise ValueError("Ensemble weights must sum to a positive value")

    normalized = ordered_weights / weight_sum
    return {name: float(weight) for name, weight in zip(ordered_names, normalized)}


def _format_prediction_output(predictions: np.ndarray) -> float | list[float]:
    """Return floats for single-item output and lists for batched output."""
    if predictions.size == 1:
        return float(predictions[0])
    return predictions.astype(float).tolist()


def load_baseline_models(model_dir: str | Path) -> Dict[str, Any]:
    """Load the baseline `.pkl` pipelines from a dataset-specific model directory."""
    directory = Path(model_dir)
    expected_paths = {
        model_name: directory / file_name
        for model_name, file_name in MODEL_FILE_NAMES.items()
    }
    missing_paths = [str(path) for path in expected_paths.values() if not path.exists()]
    if missing_paths:
        raise FileNotFoundError(
            "Missing baseline model artifacts: " + ", ".join(missing_paths)
        )

    return {
        model_name: load(model_path)
        for model_name, model_path in expected_paths.items()
    }


def simple_average_predictions(
    models: Mapping[str, Any],
    input_features: np.ndarray,
) -> np.ndarray:
    """Average predictions from all loaded baseline models."""
    features = _coerce_input_features(input_features)
    stacked_predictions = np.vstack(
        [_predict_with_model(model, features) for model in models.values()]
    )
    return np.mean(stacked_predictions, axis=0)


def weighted_average_predictions(
    models: Mapping[str, Any],
    input_features: np.ndarray,
    weights: Mapping[str, float],
) -> np.ndarray:
    """Average predictions using validated configurable weights."""
    features = _coerce_input_features(input_features)
    normalized_weights = _normalize_weights(list(models.keys()), weights)
    stacked_predictions = np.vstack(
        [_predict_with_model(models[name], features) for name in models]
    )
    ordered_weights = np.asarray(
        [normalized_weights[name] for name in models],
        dtype=np.float64,
    )
    return np.average(stacked_predictions, axis=0, weights=ordered_weights)


@dataclass
class BaselineEnsemble:
    """Cached baseline-model ensemble for API-style startup and request handling."""

    models: Dict[str, Any]
    method: str = "simple"
    weights: Dict[str, float] | None = None

    @classmethod
    def from_model_dir(
        cls,
        model_dir: str | Path,
        *,
        method: str = "simple",
        weights: Mapping[str, float] | None = None,
    ) -> BaselineEnsemble:
        return cls(
            models=load_baseline_models(model_dir),
            method=method,
            weights=dict(weights) if weights is not None else None,
        )

    def predict_array(self, input_features: np.ndarray) -> np.ndarray:
        """Return ensemble predictions for one or more rows."""
        if self.method == "simple":
            return simple_average_predictions(self.models, input_features)
        if self.method == "weighted":
            if self.weights is None:
                raise ValueError("Weighted ensemble prediction requires weights")
            return weighted_average_predictions(self.models, input_features, self.weights)
        raise ValueError(f"Unsupported ensemble method: {self.method}")

    def predict(self, input_features: np.ndarray) -> float:
        """Return a single prediction for a single input row."""
        predictions = self.predict_array(input_features)
        if predictions.size != 1:
            raise ValueError(
                "predict returns a float only for a single input row; use predict_array for batched input"
            )
        return float(predictions[0])

    def compare_predictions(self, input_features: np.ndarray) -> Dict[str, float | list[float] | str]:
        """Compare each model prediction against the configured ensemble output."""
        return compare_predictions(
            self.models,
            input_features,
            method=self.method,
            weights=self.weights,
        )


def initialize_ensemble(
    model_dir: str | Path,
    *,
    method: str = "simple",
    weights: Mapping[str, float] | None = None,
) -> BaselineEnsemble:
    """Load and cache baseline models once for repeated prediction calls."""
    global _LOADED_BASELINE_ENSEMBLE
    _LOADED_BASELINE_ENSEMBLE = BaselineEnsemble.from_model_dir(
        model_dir,
        method=method,
        weights=weights,
    )
    return _LOADED_BASELINE_ENSEMBLE


def get_loaded_ensemble() -> BaselineEnsemble:
    """Return the cached baseline ensemble or raise if it has not been initialized."""
    if _LOADED_BASELINE_ENSEMBLE is None:
        raise RuntimeError(
            "Baseline ensemble is not initialized. Call initialize_ensemble(model_dir=...) first."
        )
    return _LOADED_BASELINE_ENSEMBLE


def predict_ensemble(input_features: np.ndarray) -> float:
    """Predict with the cached baseline ensemble using the configured averaging method."""
    return get_loaded_ensemble().predict(input_features)


def compare_predictions(
    models: Mapping[str, Any],
    input_features: np.ndarray,
    *,
    method: str = "simple",
    weights: Mapping[str, float] | None = None,
) -> Dict[str, float | list[float] | str]:
    """Return individual model predictions and the ensemble prediction in one payload."""
    features = _coerce_input_features(input_features)
    comparison: Dict[str, float | list[float] | str] = {
        model_name: _format_prediction_output(_predict_with_model(model, features))
        for model_name, model in models.items()
    }

    if method == "simple":
        ensemble_predictions = simple_average_predictions(models, features)
    elif method == "weighted":
        if weights is None:
            raise ValueError("Weighted comparison requires weights")
        ensemble_predictions = weighted_average_predictions(models, features, weights)
    else:
        raise ValueError(f"Unsupported ensemble method: {method}")

    comparison["ensemble"] = _format_prediction_output(ensemble_predictions)
    comparison["method"] = method
    return comparison


def compare_loaded_predictions(input_features: np.ndarray) -> Dict[str, float | list[float] | str]:
    """Compare cached baseline-model predictions against the cached ensemble output."""
    return get_loaded_ensemble().compare_predictions(input_features)


def ensemble_predict(
    build_fn: Callable[..., object],
    best_params: Dict[str, float | int],
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    seeds: Sequence[int] = DEFAULT_ENSEMBLE_SEEDS,
    epochs: int = 200,
    validation_split: float = 0.1,
    verbose: int = 0,
) -> np.ndarray:
    """Average predictions from multiple seeded neural-network fits."""
    try:
        import tensorflow as tf
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    except ImportError as exc:
        raise ImportError("tensorflow is required for ensemble prediction") from exc

    if not seeds:
        raise ValueError("ensemble_predict requires at least one seed")

    cleaned_params = {key: value for key, value in best_params.items() if key != "learning_rate_exp"}
    batch_size = int(cleaned_params.get("batch_size", 32))
    preds = []

    for seed in seeds:
        tf.keras.backend.clear_session()
        tf.random.set_seed(seed)
        np.random.seed(seed)
        model = build_fn(**cleaned_params)
        model.fit(
            X_train,
            y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[
                EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True),
                ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=7, min_lr=1e-6),
            ],
            verbose=verbose,
        )
        preds.append(model.predict(X_test, verbose=0).flatten())

    return np.mean(np.asarray(preds, dtype=np.float32), axis=0)
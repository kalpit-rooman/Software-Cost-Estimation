from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from joblib import load

from src.baseline_models import MODEL_FILE_NAMES
from src.config import (
    DATASET_MODEL_DIRS,
    DEFAULT_ENSEMBLE_METHOD,
    DEFAULT_ENSEMBLE_WEIGHTS,
    MODEL_OUTPUT_KEYS,
    MODEL_RMSE_SCORES,
)


class PredictionServiceError(Exception):
    """Base exception for prediction service failures."""


class InvalidDatasetError(PredictionServiceError):
    """Raised when a request targets an unknown dataset key."""


class InvalidInputError(PredictionServiceError):
    """Raised when raw input cannot be converted into a valid model payload."""


@dataclass(frozen=True)
class DatasetModelBundle:
    """Cached model bundle and feature schema for one dataset."""

    models: Dict[str, Any]
    feature_names: tuple[str, ...]
    loaded_model_names: tuple[str, ...]


class PredictionService:
    """Lazy-loading prediction service for dataset-specific baseline pipelines."""

    def __init__(
        self,
        dataset_model_dirs: Mapping[str, Path] | None = None,
        rmse_scores: Mapping[str, Mapping[str, float]] | None = None,
        default_weights: Mapping[str, Mapping[str, float]] | None = None,
    ) -> None:
        self.dataset_model_dirs = {
            dataset_name: Path(model_dir)
            for dataset_name, model_dir in (dataset_model_dirs or DATASET_MODEL_DIRS).items()
        }
        self.rmse_scores = {
            dataset_name: {model_name: float(score) for model_name, score in scores.items()}
            for dataset_name, scores in (rmse_scores or MODEL_RMSE_SCORES).items()
        }
        self.default_weights = {
            dataset_name: {model_name: float(weight) for model_name, weight in weights.items()}
            for dataset_name, weights in (default_weights or DEFAULT_ENSEMBLE_WEIGHTS).items()
        }
        self._dataset_cache: Dict[str, DatasetModelBundle] = {}

    def load_models(self, dataset_name: str | None = None) -> None:
        """Load models once for one dataset or for all configured datasets."""
        if dataset_name is None:
            for configured_dataset in self.dataset_model_dirs:
                self._get_dataset_bundle(configured_dataset)
            return
        self._get_dataset_bundle(dataset_name)

    def predict(
        self,
        dataset_name: str,
        input_payload: Mapping[str, Any],
        *,
        ensemble_method: str = DEFAULT_ENSEMBLE_METHOD,
        weights: Mapping[str, float] | None = None,
    ) -> Dict[str, float | str]:
        """Predict individual baseline outputs and ensemble output for one dataset."""
        bundle = self._get_dataset_bundle(dataset_name)
        input_frame = self._build_input_frame(bundle.feature_names, input_payload)
        predictions = self._predict_individual_models(bundle.models, input_frame)
        ensemble_prediction = self._predict_ensemble(
            predictions,
            dataset_name,
            model_names=bundle.loaded_model_names,
            ensemble_method=ensemble_method,
            weights=weights,
        )

        fallback_prediction = float(ensemble_prediction)
        return {
            MODEL_OUTPUT_KEYS["RandomForest"]: predictions.get("RandomForest", fallback_prediction),
            MODEL_OUTPUT_KEYS["XGBoost"]: predictions.get("XGBoost", fallback_prediction),
            MODEL_OUTPUT_KEYS["LinearRegression"]: predictions.get("LinearRegression", fallback_prediction),
            "ensemble_prediction": ensemble_prediction,
            "best_model": self._select_best_model(dataset_name, bundle.loaded_model_names),
        }

    def _get_dataset_bundle(self, dataset_name: str) -> DatasetModelBundle:
        """Return a cached dataset bundle or load it on first use."""
        normalized_dataset = dataset_name.lower().strip()
        if normalized_dataset not in self.dataset_model_dirs:
            raise InvalidDatasetError(
                f"Unsupported dataset '{dataset_name}'. Supported datasets: {sorted(self.dataset_model_dirs)}"
            )
        if normalized_dataset not in self._dataset_cache:
            self._dataset_cache[normalized_dataset] = self._load_dataset_bundle(normalized_dataset)
        return self._dataset_cache[normalized_dataset]

    def _load_dataset_bundle(self, dataset_name: str) -> DatasetModelBundle:
        """Load and validate the saved baseline pipelines for a dataset."""
        model_dir = self.dataset_model_dirs[dataset_name]
        missing_files = [
            str(model_dir / file_name)
            for file_name in MODEL_FILE_NAMES.values()
            if not (model_dir / file_name).exists()
        ]
        if missing_files:
            raise FileNotFoundError("Missing model artifacts: " + ", ".join(missing_files))

        models: Dict[str, Any] = {}
        for model_name, file_name in MODEL_FILE_NAMES.items():
            try:
                models[model_name] = load(model_dir / file_name)
            except ModuleNotFoundError as exc:
                if model_name == "XGBoost" and "xgboost" in str(exc).lower():
                    # Keep the service available when XGBoost is not installed locally.
                    continue
                raise

        if not models:
            raise PredictionServiceError(
                f"No models could be loaded for dataset '{dataset_name}'"
            )

        first_model_name = next(iter(models))
        feature_names = self._resolve_feature_names(models[first_model_name])
        for model_name, model in models.items():
            model_feature_names = self._resolve_feature_names(model)
            if model_feature_names != feature_names:
                raise PredictionServiceError(
                    f"Feature schema mismatch for dataset '{dataset_name}' in model '{model_name}'"
                )

        return DatasetModelBundle(
            models=models,
            feature_names=feature_names,
            loaded_model_names=tuple(models.keys()),
        )

    def _resolve_feature_names(self, model: Any) -> tuple[str, ...]:
        """Resolve the input feature names embedded in a saved sklearn pipeline."""
        feature_names = getattr(model, "feature_names_in_", None)
        if feature_names is None and hasattr(model, "named_steps"):
            preprocessor = model.named_steps.get("preprocessor")
            feature_names = getattr(preprocessor, "feature_names_in_", None)
        if feature_names is None:
            raise PredictionServiceError("Saved model does not expose feature names")
        return tuple(str(name) for name in feature_names)

    def _build_input_frame(
        self,
        feature_names: tuple[str, ...],
        input_payload: Mapping[str, Any],
    ) -> pd.DataFrame:
        """Convert a raw input dictionary to a single-row DataFrame with stable column order."""
        if not isinstance(input_payload, Mapping):
            raise InvalidInputError("input_payload must be a dictionary-like object")

        matching_fields = [feature_name for feature_name in feature_names if feature_name in input_payload]
        if not matching_fields:
            raise InvalidInputError("input_payload does not contain any expected feature names")

        row = {
            feature_name: input_payload.get(feature_name, np.nan)
            for feature_name in feature_names
        }
        return pd.DataFrame([row], columns=list(feature_names))

    def _predict_individual_models(
        self,
        models: Mapping[str, Any],
        input_frame: pd.DataFrame,
    ) -> Dict[str, float]:
        """Run one prediction per model and return scalar floats."""
        try:
            return {
                model_name: float(np.asarray(model.predict(input_frame), dtype=np.float64).ravel()[0])
                for model_name, model in models.items()
            }
        except Exception as exc:
            raise InvalidInputError(f"Model prediction failed: {exc}") from exc

    def _predict_ensemble(
        self,
        predictions: Mapping[str, float],
        dataset_name: str,
        *,
        model_names: tuple[str, ...],
        ensemble_method: str,
        weights: Mapping[str, float] | None,
    ) -> float:
        """Combine model predictions using simple or weighted averaging."""
        ordered_model_names = list(model_names)
        ordered_predictions = np.asarray(
            [float(predictions[model_name]) for model_name in ordered_model_names],
            dtype=np.float64,
        )

        if ensemble_method == "simple":
            return float(np.mean(ordered_predictions))
        if ensemble_method != "weighted":
            raise InvalidInputError(
                "ensemble_method must be either 'simple' or 'weighted'"
            )

        normalized_weights = self._normalize_weights(
            dataset_name,
            model_names=ordered_model_names,
            weights=weights,
        )
        ordered_weights = np.asarray(
            [normalized_weights[model_name] for model_name in ordered_model_names],
            dtype=np.float64,
        )
        return float(np.average(ordered_predictions, weights=ordered_weights))

    def _normalize_weights(
        self,
        dataset_name: str,
        *,
        model_names: list[str],
        weights: Mapping[str, float] | None,
    ) -> Dict[str, float]:
        """Resolve, validate, and normalize ensemble weights."""
        if not model_names:
            raise InvalidInputError("No models available for ensemble weighting")

        all_known_model_names = list(MODEL_OUTPUT_KEYS.keys())
        if weights is not None:
            unknown_keys = sorted(set(weights) - set(all_known_model_names))
            if unknown_keys:
                raise InvalidInputError(f"Unknown ensemble weight keys: {unknown_keys}")
            resolved_weights = {model_name: float(weights.get(model_name, 0.0)) for model_name in model_names}
        else:
            configured_defaults = self.default_weights.get(dataset_name, {})
            resolved_weights = {
                model_name: float(configured_defaults.get(model_name, 0.0))
                for model_name in model_names
            }

        weight_values = np.asarray(
            [resolved_weights[model_name] for model_name in model_names],
            dtype=np.float64,
        )
        if np.any(weight_values < 0):
            raise InvalidInputError("Ensemble weights must be non-negative")

        weight_sum = float(np.sum(weight_values))
        if weight_sum <= 0:
            equal_weight = 1.0 / len(model_names)
            return {model_name: equal_weight for model_name in model_names}

        normalized_values = weight_values / weight_sum
        return {
            model_name: float(weight)
            for model_name, weight in zip(model_names, normalized_values)
        }

    def _select_best_model(self, dataset_name: str, model_names: tuple[str, ...]) -> str:
        """Select the best production model for a dataset using the lowest RMSE."""
        dataset_scores = self.rmse_scores.get(dataset_name)
        if not dataset_scores:
            raise PredictionServiceError(
                f"No RMSE scores configured for dataset '{dataset_name}'"
            )

        scored_models = {
            model_name: score
            for model_name, score in dataset_scores.items()
            if model_name in model_names
        }
        if not scored_models:
            return model_names[0]
        return min(scored_models, key=scored_models.get)


_PREDICTION_SERVICE: PredictionService | None = None


def get_prediction_service() -> PredictionService:
    """Return the process-wide prediction service singleton."""
    global _PREDICTION_SERVICE
    if _PREDICTION_SERVICE is None:
        _PREDICTION_SERVICE = PredictionService()
    return _PREDICTION_SERVICE


def load_prediction_service() -> PredictionService:
    """Warm all model bundles once, typically from a FastAPI startup hook."""
    service = get_prediction_service()
    service.load_models()
    return service


def predict_cost(
    dataset_name: str,
    input_payload: Mapping[str, Any],
    *,
    ensemble_method: str = DEFAULT_ENSEMBLE_METHOD,
    weights: Mapping[str, float] | None = None,
) -> Dict[str, float | str]:
    """FastAPI-friendly convenience wrapper around the singleton prediction service."""
    return get_prediction_service().predict(
        dataset_name,
        input_payload,
        ensemble_method=ensemble_method,
        weights=weights,
    )
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Callable, Dict, Iterable, Sequence, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import StandardScaler

from src.baseline_models import get_baseline_model_builders as build_baseline_model_builders
from src.cnn_model import build_cnn_regressor, reshape_for_cnn, train_cnn_model
from src.data_loader import load_all_raw_datasets
from src.ensemble import DEFAULT_ENSEMBLE_SEEDS, ensemble_predict
from src.evaluate import compute_regression_metrics, save_metrics
from src.feature_engineering import inverse_log_transform, log_transform_target
from src.mlp_model import build_mlp_regressor, train_mlp_model
from src.preprocess import preprocess_dataset
from src.pso_mlp import build_mlp_pso_objective, decode_mlp_hyperparameters, get_mlp_pso_bounds, tune_mlp_with_pso
from src.pso_optimizer import build_cnn_pso_objective, decode_cnn_hyperparameters, get_cnn_pso_bounds, tune_cnn_with_pso


ROOT_DIR = Path(__file__).resolve().parent.parent
METRICS_DIR = ROOT_DIR / "results" / "metrics"
MODELS_DIR = ROOT_DIR / "models"

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

DATASET_DISPLAY_NAMES = {
    "china": "China",
    "cocomo81": "COCOMO81",
    "desharnais": "Desharnais",
}

MODEL_ORDER = [
    "LinearRegression",
    "RandomForest",
    "XGBoost",
    "CNN_baseline",
    "CNN_PSO",
    "MLP_baseline",
    "MLP_PSO",
    "CNN_PSO_ensemble",
    "MLP_PSO_ensemble",
]

_METRIC_NAME_MAP = {
    "rmse": "RMSE",
    "mae": "MAE",
    "r2": "R2",
    "mape": "MAPE",
    "mdmre": "MdMRE",
    "pred25": "Pred25",
}


def _as_float_array(values: np.ndarray) -> np.ndarray:
    """Normalize targets/features to flat float arrays for reproducible training."""
    return np.asarray(values, dtype=np.float32)


def _identity_features(values: np.ndarray) -> np.ndarray:
    """Return MLP-ready tabular features unchanged."""
    return values


def _reset_training_seed(seed: int = SEED) -> None:
    """Reset Python, NumPy, and TensorFlow state before each neural-model build."""
    tf.keras.backend.clear_session()
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def _scale_training_eval_features(
    X_train: np.ndarray,
    X_eval: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, StandardScaler]:
    """Fit a scaler on the training split only, then transform the paired eval split."""
    # Always fit on the current training split only; fitting earlier would leak fold statistics.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit(X_train).transform(X_train)
    X_eval_scaled = scaler.transform(X_eval)
    return _as_float_array(X_train_scaled), _as_float_array(X_eval_scaled), scaler


def _build_model(model_builder: Callable[..., object], n_samples: int) -> object:
    """Create a model, passing fold size when the builder accepts dataset-aware caps."""
    try:
        return model_builder(n_samples=n_samples)
    except TypeError:
        try:
            return model_builder(n_samples)
        except TypeError:
            return model_builder()


def _format_holdout_row(dataset_name: str, model_name: str, metrics: Dict[str, float]) -> Dict[str, float | str]:
    """Convert raw metric values into the standardized holdout-results schema."""
    return {
        "Dataset": dataset_name,
        "Model": model_name,
        "RMSE": float(metrics["rmse"]),
        "MAE": float(metrics["mae"]),
        "R2": float(metrics["r2"]),
        "MAPE": float(metrics["mape"]),
        "MdMRE": float(metrics["mdmre"]),
        "Pred25": float(metrics["pred25"]),
    }


def _sort_results(frame: pd.DataFrame, metric_column: str) -> pd.DataFrame:
    """Sort result tables in stable dataset/model order for easier downstream review."""
    sorted_frame = frame.copy()
    sorted_frame["Dataset"] = pd.Categorical(
        sorted_frame["Dataset"],
        categories=[DATASET_DISPLAY_NAMES[key] for key in ("china", "cocomo81", "desharnais")],
        ordered=True,
    )
    sorted_frame["Model"] = pd.Categorical(
        sorted_frame["Model"],
        categories=MODEL_ORDER,
        ordered=True,
    )
    return sorted_frame.sort_values(["Dataset", "Model", metric_column]).reset_index(drop=True)


def summarize_fold_metrics(fold_metrics: Iterable[Dict[str, float]]) -> Dict[str, float]:
    """Aggregate 5-fold metrics into mean/std fields used by the final results table."""
    metrics_list = list(fold_metrics)
    if not metrics_list:
        raise ValueError("Expected at least one fold metric dictionary")

    summary: Dict[str, float] = {}
    for metric_key, metric_label in _METRIC_NAME_MAP.items():
        values = np.asarray([fold_metric[metric_key] for fold_metric in metrics_list], dtype=np.float64)
        summary[f"{metric_label}_mean"] = float(np.mean(values))
        summary[f"{metric_label}_std"] = float(np.std(values))
    return summary


def make_cnn_builder(
    input_length: int,
    hyperparameters: Dict[str, float | int] | None = None,
) -> Callable[..., object]:
    """Create a CNN builder that accepts an optional fold-size hint."""
    params = hyperparameters or {}

    def builder(n_samples: int | None = None) -> object:
        return build_cnn_regressor(
            input_length=input_length,
            filters=int(params.get("filters", 32)),
            kernel_size=int(params.get("kernel_size", 3)),
            dense_units=int(params.get("dense_units", 64)),
            learning_rate=float(params.get("learning_rate", 1e-3)),
            dropout_rate=float(params.get("dropout_rate", 0.2)),
            num_conv_layers=int(params.get("num_conv_layers", 1)),
            batch_size=int(params.get("batch_size", 32)),
            n_samples=n_samples,
        )

    return builder


def make_mlp_builder(
    input_length: int,
    hyperparameters: Dict[str, float | int] | None = None,
) -> Callable[..., object]:
    """Create an MLP builder that accepts an optional fold-size hint."""
    params = hyperparameters or {}

    def builder(n_samples: int | None = None) -> object:
        return build_mlp_regressor(
            input_length=input_length,
            learning_rate=float(params.get("learning_rate", 1e-3)),
            dropout_rate=float(params.get("dropout_rate", 0.2)),
            n_layers=int(params.get("n_layers", 1)),
            units_per_layer=int(params.get("units_per_layer", 64)),
            batch_size=int(params.get("batch_size", 32)),
            n_samples=n_samples,
        )

    return builder


def make_cnn_ensemble_builder_factory(input_length: int) -> Callable[[int], Callable[..., object]]:
    """Create a CNN builder factory for seeded ensembles."""

    def factory(n_samples: int) -> Callable[..., object]:
        return lambda **params: build_cnn_regressor(
            input_length=input_length,
            n_samples=n_samples,
            **params,
        )

    return factory


def make_mlp_ensemble_builder_factory(input_length: int) -> Callable[[int], Callable[..., object]]:
    """Create an MLP builder factory for seeded ensembles."""

    def factory(n_samples: int) -> Callable[..., object]:
        return lambda **params: build_mlp_regressor(
            input_length=input_length,
            n_samples=n_samples,
            **params,
        )

    return factory


def get_baseline_model_builders() -> Dict[str, Callable[[], object]]:
    """Return fresh sklearn baseline builders for the standardized comparison table."""
    return build_baseline_model_builders()


def prepare_dataset_for_benchmark(
    df: pd.DataFrame,
    target_col: str | None = None,
    use_log_transform: bool = True,
) -> Dict[str, np.ndarray | str]:
    """Prepare encoded features and carve out the untouched final holdout split."""
    features_df, targets_series, resolved_target = preprocess_dataset(df, target_col=target_col)
    features = _as_float_array(features_df.to_numpy())
    targets_raw = _as_float_array(targets_series.to_numpy()).ravel()
    targets_fit = log_transform_target(targets_raw, use_log_transform=use_log_transform).astype(np.float32)
    indices = np.arange(len(targets_raw))

    # Split off the final holdout before any scaler fit, PSO tuning, or CV so it stays untouched.
    main_index, holdout_index = train_test_split(
        indices,
        test_size=0.2,
        random_state=SEED,
    )

    return {
        "target_col": resolved_target,
        "X_all": features,
        "y_all_raw": targets_raw,
        "y_all_fit": targets_fit,
        "X_main": features[main_index],
        "X_holdout": features[holdout_index],
        "y_main_raw": targets_raw[main_index],
        "y_main_fit": targets_fit[main_index],
        "y_holdout_raw": targets_raw[holdout_index],
        "y_holdout_fit": targets_fit[holdout_index],
        "n_features": int(features.shape[1]),
    }


def cross_validate_estimator(
    model_builder: Callable[[], object],
    X: np.ndarray,
    y: np.ndarray,
    use_log_transform: bool = True,
) -> Dict[str, float]:
    """Run 5-fold CV for sklearn-style estimators that implement fit/predict."""
    features = _as_float_array(X)
    targets_raw = _as_float_array(y).ravel()
    targets_fit = log_transform_target(targets_raw, use_log_transform=use_log_transform).astype(np.float32)
    kfold = KFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_metrics: list[Dict[str, float]] = []

    for train_index, test_index in kfold.split(features):
        X_train_scaled, X_test_scaled, _ = _scale_training_eval_features(
            features[train_index],
            features[test_index],
        )
        y_train_fit = targets_fit[train_index]
        y_test_raw = targets_raw[test_index]

        random.seed(SEED)
        np.random.seed(SEED)
        tf.random.set_seed(SEED)

        model = model_builder()
        model.fit(X_train_scaled, y_train_fit)
        predictions_fit = np.asarray(model.predict(X_test_scaled), dtype=np.float32).ravel()
        predictions = inverse_log_transform(predictions_fit, use_log_transform=use_log_transform)
        fold_metrics.append(compute_regression_metrics(y_test_raw, predictions))

    return summarize_fold_metrics(fold_metrics)


def _cross_validate_neural_regressor(
    model_builder: Callable[..., object],
    train_model_fn: Callable[..., Tuple[object, Dict[str, list]]],
    prepare_features_fn: Callable[[np.ndarray], np.ndarray],
    X: np.ndarray,
    y: np.ndarray,
    batch_size: int = 32,
    epochs: int = 100,
    use_log_transform: bool = True,
    verbose: int = 0,
    validation_split: float = 0.1,
) -> Dict[str, float]:
    """Run 5-fold CV for Keras regressors, rebuilding the model on every fold."""
    features = _as_float_array(X)
    targets_raw = _as_float_array(y).ravel()
    targets_fit = log_transform_target(targets_raw, use_log_transform=use_log_transform).astype(np.float32)
    kfold = KFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_metrics: list[Dict[str, float]] = []

    for train_index, test_index in kfold.split(features):
        X_train_scaled, X_test_scaled, _ = _scale_training_eval_features(
            features[train_index],
            features[test_index],
        )
        X_train_prepared = prepare_features_fn(X_train_scaled)
        X_test_prepared = prepare_features_fn(X_test_scaled)
        y_train_fit = targets_fit[train_index]
        y_test_raw = targets_raw[test_index]

        _reset_training_seed()
        model = _build_model(model_builder, len(X_train_scaled))
        model, _ = train_model_fn(
            model=model,
            x_train=X_train_prepared,
            y_train=y_train_fit,
            epochs=epochs,
            batch_size=batch_size,
            verbose=verbose,
            use_callbacks=True,
            validation_split=validation_split,
        )
        predictions_fit = model.predict(X_test_prepared, verbose=0).ravel()
        predictions = inverse_log_transform(predictions_fit, use_log_transform=use_log_transform)
        fold_metrics.append(compute_regression_metrics(y_test_raw, predictions))

    return summarize_fold_metrics(fold_metrics)


def cross_validate_cnn(
    model_builder: Callable[..., object],
    X: np.ndarray,
    y: np.ndarray,
    batch_size: int = 32,
    epochs: int = 100,
    use_log_transform: bool = True,
    verbose: int = 0,
    validation_split: float = 0.1,
) -> Dict[str, float]:
    """Run 5-fold CV for CNN models with fold-local scaling and internal validation."""
    return _cross_validate_neural_regressor(
        model_builder=model_builder,
        train_model_fn=train_cnn_model,
        prepare_features_fn=reshape_for_cnn,
        X=X,
        y=y,
        batch_size=batch_size,
        epochs=epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
        validation_split=validation_split,
    )


def cross_validate_mlp(
    model_builder: Callable[..., object],
    X: np.ndarray,
    y: np.ndarray,
    batch_size: int = 32,
    epochs: int = 100,
    use_log_transform: bool = True,
    verbose: int = 0,
    validation_split: float = 0.1,
) -> Dict[str, float]:
    """Run 5-fold CV for MLP models with fold-local scaling and internal validation."""
    return _cross_validate_neural_regressor(
        model_builder=model_builder,
        train_model_fn=train_mlp_model,
        prepare_features_fn=_identity_features,
        X=X,
        y=y,
        batch_size=batch_size,
        epochs=epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
        validation_split=validation_split,
    )


def cross_validate_neural_ensemble(
    build_fn_factory: Callable[[int], Callable[..., object]],
    best_params: Dict[str, float | int],
    prepare_features_fn: Callable[[np.ndarray], np.ndarray],
    X: np.ndarray,
    y: np.ndarray,
    use_log_transform: bool = True,
    ensemble_seeds: Sequence[int] = DEFAULT_ENSEMBLE_SEEDS,
    ensemble_epochs: int = 200,
    verbose: int = 0,
) -> Dict[str, float]:
    """Run 5-fold CV for seeded neural ensembles using fixed tuned hyperparameters."""
    features = _as_float_array(X)
    targets_raw = _as_float_array(y).ravel()
    targets_fit = log_transform_target(targets_raw, use_log_transform=use_log_transform).astype(np.float32)
    kfold = KFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_metrics: list[Dict[str, float]] = []

    for train_index, test_index in kfold.split(features):
        X_train_scaled, X_test_scaled, _ = _scale_training_eval_features(
            features[train_index],
            features[test_index],
        )
        X_train_prepared = prepare_features_fn(X_train_scaled)
        X_test_prepared = prepare_features_fn(X_test_scaled)
        y_train_fit = targets_fit[train_index]
        y_test_raw = targets_raw[test_index]
        build_fn = build_fn_factory(len(X_train_scaled))

        predictions_fit = ensemble_predict(
            build_fn=build_fn,
            best_params=best_params,
            X_train=X_train_prepared,
            y_train=y_train_fit,
            X_test=X_test_prepared,
            seeds=ensemble_seeds,
            epochs=ensemble_epochs,
            verbose=verbose,
        )
        predictions = inverse_log_transform(predictions_fit, use_log_transform=use_log_transform)
        fold_metrics.append(compute_regression_metrics(y_test_raw, predictions))

    return summarize_fold_metrics(fold_metrics)


def tune_cnn_pso_once(
    X: np.ndarray,
    y: np.ndarray,
    input_length: int,
    use_log_transform: bool = True,
    tuning_epochs: int = 30,
    n_particles: int = 15,
    iters: int = 25,
    verbose: int = 0,
) -> Tuple[Dict[str, float | int], float]:
    """Tune CNN hyperparameters once on the caller-provided main split only."""
    features = _as_float_array(X)
    targets = _as_float_array(y).ravel()

    X_train, X_val, y_train, y_val = train_test_split(
        features,
        targets,
        test_size=0.2,
        random_state=SEED,
    )

    lower_bounds, upper_bounds = get_cnn_pso_bounds()
    objective_fn = build_cnn_pso_objective(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        input_length=input_length,
        epochs=tuning_epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
    )
    best_cost, best_position = tune_cnn_with_pso(
        objective_fn=objective_fn,
        dimensions=6,
        lower_bounds=lower_bounds,
        upper_bounds=upper_bounds,
        n_particles=n_particles,
        iters=iters,
    )
    return decode_cnn_hyperparameters(best_position), float(best_cost)


def tune_mlp_pso_once(
    X: np.ndarray,
    y: np.ndarray,
    input_length: int,
    use_log_transform: bool = True,
    tuning_epochs: int = 30,
    n_particles: int = 15,
    iters: int = 25,
    verbose: int = 0,
) -> Tuple[Dict[str, float | int], float]:
    """Tune MLP hyperparameters once on the caller-provided main split only."""
    features = _as_float_array(X)
    targets = _as_float_array(y).ravel()

    X_train, X_val, y_train, y_val = train_test_split(
        features,
        targets,
        test_size=0.2,
        random_state=SEED,
    )

    lower_bounds, upper_bounds = get_mlp_pso_bounds()
    objective_fn = build_mlp_pso_objective(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        input_length=input_length,
        epochs=tuning_epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
    )
    best_cost, best_position = tune_mlp_with_pso(
        objective_fn=objective_fn,
        dimensions=5,
        lower_bounds=lower_bounds,
        upper_bounds=upper_bounds,
        n_particles=n_particles,
        iters=iters,
    )
    return decode_mlp_hyperparameters(best_position), float(best_cost)


def cross_validate_cnn_pso(
    X: np.ndarray,
    y: np.ndarray,
    input_length: int,
    use_log_transform: bool = True,
    tuning_epochs: int = 30,
    training_epochs: int = 100,
    n_particles: int = 15,
    iters: int = 25,
    verbose: int = 0,
) -> Tuple[Dict[str, float | int], float, Dict[str, float]]:
    """Tune CNN+PSO once, then report 5-fold CV with those fixed hyperparameters."""
    best_hyperparameters, best_cost = tune_cnn_pso_once(
        X=X,
        y=y,
        input_length=input_length,
        use_log_transform=use_log_transform,
        tuning_epochs=tuning_epochs,
        n_particles=n_particles,
        iters=iters,
        verbose=verbose,
    )

    summary = cross_validate_cnn(
        model_builder=make_cnn_builder(input_length, hyperparameters=best_hyperparameters),
        X=X,
        y=y,
        batch_size=int(best_hyperparameters.get("batch_size", 32)),
        epochs=training_epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
    )
    return best_hyperparameters, best_cost, summary


def cross_validate_mlp_pso(
    X: np.ndarray,
    y: np.ndarray,
    input_length: int,
    use_log_transform: bool = True,
    tuning_epochs: int = 30,
    training_epochs: int = 100,
    n_particles: int = 15,
    iters: int = 25,
    verbose: int = 0,
) -> Tuple[Dict[str, float | int], float, Dict[str, float]]:
    """Tune MLP+PSO once, then report 5-fold CV with those fixed hyperparameters."""
    best_hyperparameters, best_cost = tune_mlp_pso_once(
        X=X,
        y=y,
        input_length=input_length,
        use_log_transform=use_log_transform,
        tuning_epochs=tuning_epochs,
        n_particles=n_particles,
        iters=iters,
        verbose=verbose,
    )

    summary = cross_validate_mlp(
        model_builder=make_mlp_builder(input_length, hyperparameters=best_hyperparameters),
        X=X,
        y=y,
        batch_size=int(best_hyperparameters.get("batch_size", 32)),
        epochs=training_epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
    )
    return best_hyperparameters, best_cost, summary


def _evaluate_holdout_estimator(
    model_builder: Callable[[], object],
    X_main: np.ndarray,
    y_main_fit: np.ndarray,
    X_holdout: np.ndarray,
    y_holdout_raw: np.ndarray,
    use_log_transform: bool = True,
) -> Dict[str, float]:
    """Train an sklearn estimator on X_main only and score it once on the untouched holdout."""
    X_main_scaled, X_holdout_scaled, _ = _scale_training_eval_features(X_main, X_holdout)
    model = model_builder()
    model.fit(X_main_scaled, y_main_fit)
    predictions_fit = np.asarray(model.predict(X_holdout_scaled), dtype=np.float32).ravel()
    predictions = inverse_log_transform(predictions_fit, use_log_transform=use_log_transform)
    return compute_regression_metrics(y_holdout_raw, predictions)


def _evaluate_holdout_neural_model(
    model_builder: Callable[..., object],
    train_model_fn: Callable[..., Tuple[object, Dict[str, list]]],
    prepare_features_fn: Callable[[np.ndarray], np.ndarray],
    X_main: np.ndarray,
    y_main_fit: np.ndarray,
    X_holdout: np.ndarray,
    y_holdout_raw: np.ndarray,
    batch_size: int = 32,
    epochs: int = 100,
    use_log_transform: bool = True,
    verbose: int = 0,
) -> Tuple[object, Dict[str, list], Dict[str, float]]:
    """Train a neural regressor on X_main only and score it once on the untouched holdout."""
    X_main_scaled, X_holdout_scaled, _ = _scale_training_eval_features(X_main, X_holdout)
    X_main_prepared = prepare_features_fn(X_main_scaled)
    X_holdout_prepared = prepare_features_fn(X_holdout_scaled)

    _reset_training_seed()
    model = _build_model(model_builder, len(X_main_scaled))
    model, history = train_model_fn(
        model=model,
        x_train=X_main_prepared,
        y_train=y_main_fit,
        epochs=epochs,
        batch_size=batch_size,
        verbose=verbose,
        use_callbacks=True,
        validation_split=0.1,
    )
    predictions_fit = model.predict(X_holdout_prepared, verbose=0).ravel()
    predictions = inverse_log_transform(predictions_fit, use_log_transform=use_log_transform)
    metrics = compute_regression_metrics(y_holdout_raw, predictions)
    return model, history, metrics


def _evaluate_holdout_ensemble(
    build_fn_factory: Callable[[int], Callable[..., object]],
    best_params: Dict[str, float | int],
    prepare_features_fn: Callable[[np.ndarray], np.ndarray],
    X_main: np.ndarray,
    y_main_fit: np.ndarray,
    X_holdout: np.ndarray,
    y_holdout_raw: np.ndarray,
    use_log_transform: bool = True,
    ensemble_seeds: Sequence[int] = DEFAULT_ENSEMBLE_SEEDS,
    ensemble_epochs: int = 200,
    verbose: int = 0,
) -> Dict[str, float]:
    """Score a seeded ensemble on the untouched holdout using only X_main for fitting."""
    X_main_scaled, X_holdout_scaled, _ = _scale_training_eval_features(X_main, X_holdout)
    X_main_prepared = prepare_features_fn(X_main_scaled)
    X_holdout_prepared = prepare_features_fn(X_holdout_scaled)
    predictions_fit = ensemble_predict(
        build_fn=build_fn_factory(len(X_main_scaled)),
        best_params=best_params,
        X_train=X_main_prepared,
        y_train=y_main_fit,
        X_test=X_holdout_prepared,
        seeds=ensemble_seeds,
        epochs=ensemble_epochs,
        verbose=verbose,
    )
    predictions = inverse_log_transform(predictions_fit, use_log_transform=use_log_transform)
    return compute_regression_metrics(y_holdout_raw, predictions)


def run_dataset_benchmark(
    dataset_name: str,
    dataset_key: str,
    df: pd.DataFrame,
    use_log_transform: bool = True,
    training_epochs: int = 100,
    tuning_epochs: int = 30,
    n_particles: int = 15,
    iters: int = 25,
    ensemble_seeds: Sequence[int] = DEFAULT_ENSEMBLE_SEEDS,
    ensemble_epochs: int = 200,
    verbose: int = 0,
) -> Dict[str, object]:
    """Run the clean CV + holdout benchmark for one dataset."""
    splits = prepare_dataset_for_benchmark(df, use_log_transform=use_log_transform)
    X_main = splits["X_main"]
    X_holdout = splits["X_holdout"]
    y_main_raw = splits["y_main_raw"]
    y_main_fit = splits["y_main_fit"]
    y_holdout_raw = splits["y_holdout_raw"]
    input_length = int(splits["n_features"])

    holdout_rows: list[Dict[str, float | str]] = []
    final_rows: list[Dict[str, float | str]] = []
    histories: Dict[str, Dict[str, list]] = {}
    hyperparams: Dict[str, Dict[str, float | int]] = {}
    models: Dict[str, object] = {}

    for model_name, model_builder in get_baseline_model_builders().items():
        holdout_metrics = _evaluate_holdout_estimator(
            model_builder=model_builder,
            X_main=X_main,
            y_main_fit=y_main_fit,
            X_holdout=X_holdout,
            y_holdout_raw=y_holdout_raw,
            use_log_transform=use_log_transform,
        )
        holdout_rows.append(_format_holdout_row(dataset_name, model_name, holdout_metrics))
        final_rows.append(
            {
                "Dataset": dataset_name,
                "Model": model_name,
                **cross_validate_estimator(
                    model_builder=model_builder,
                    X=X_main,
                    y=y_main_raw,
                    use_log_transform=use_log_transform,
                ),
            }
        )

    cnn_builder = make_cnn_builder(input_length)
    cnn_model, cnn_history, cnn_holdout_metrics = _evaluate_holdout_neural_model(
        model_builder=cnn_builder,
        train_model_fn=train_cnn_model,
        prepare_features_fn=reshape_for_cnn,
        X_main=X_main,
        y_main_fit=y_main_fit,
        X_holdout=X_holdout,
        y_holdout_raw=y_holdout_raw,
        batch_size=32,
        epochs=training_epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
    )
    models["cnn_baseline"] = cnn_model
    histories["cnn_baseline"] = {key: [float(value) for value in values] for key, values in cnn_history.items()}
    holdout_rows.append(_format_holdout_row(dataset_name, "CNN_baseline", cnn_holdout_metrics))
    final_rows.append(
        {
            "Dataset": dataset_name,
            "Model": "CNN_baseline",
            **cross_validate_cnn(
                model_builder=cnn_builder,
                X=X_main,
                y=y_main_raw,
                batch_size=32,
                epochs=training_epochs,
                use_log_transform=use_log_transform,
                verbose=verbose,
            ),
        }
    )

    best_cnn_hyperparameters, best_cnn_cost = tune_cnn_pso_once(
        X=X_main,
        y=y_main_raw,
        input_length=input_length,
        use_log_transform=use_log_transform,
        tuning_epochs=tuning_epochs,
        n_particles=n_particles,
        iters=iters,
        verbose=verbose,
    )
    hyperparams["cnn_pso"] = {**best_cnn_hyperparameters, "best_cost": float(best_cnn_cost)}
    tuned_cnn_builder = make_cnn_builder(input_length, hyperparameters=best_cnn_hyperparameters)
    tuned_cnn_model, tuned_cnn_history, tuned_cnn_holdout_metrics = _evaluate_holdout_neural_model(
        model_builder=tuned_cnn_builder,
        train_model_fn=train_cnn_model,
        prepare_features_fn=reshape_for_cnn,
        X_main=X_main,
        y_main_fit=y_main_fit,
        X_holdout=X_holdout,
        y_holdout_raw=y_holdout_raw,
        batch_size=int(best_cnn_hyperparameters.get("batch_size", 32)),
        epochs=training_epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
    )
    models["cnn_pso"] = tuned_cnn_model
    histories["cnn_pso"] = {key: [float(value) for value in values] for key, values in tuned_cnn_history.items()}
    holdout_rows.append(_format_holdout_row(dataset_name, "CNN_PSO", tuned_cnn_holdout_metrics))
    holdout_rows.append(
        _format_holdout_row(
            dataset_name,
            "CNN_PSO_ensemble",
            _evaluate_holdout_ensemble(
                build_fn_factory=make_cnn_ensemble_builder_factory(input_length),
                best_params=best_cnn_hyperparameters,
                prepare_features_fn=reshape_for_cnn,
                X_main=X_main,
                y_main_fit=y_main_fit,
                X_holdout=X_holdout,
                y_holdout_raw=y_holdout_raw,
                use_log_transform=use_log_transform,
                ensemble_seeds=ensemble_seeds,
                ensemble_epochs=ensemble_epochs,
                verbose=verbose,
            ),
        )
    )
    final_rows.append(
        {
            "Dataset": dataset_name,
            "Model": "CNN_PSO",
            **cross_validate_cnn(
                model_builder=tuned_cnn_builder,
                X=X_main,
                y=y_main_raw,
                batch_size=int(best_cnn_hyperparameters.get("batch_size", 32)),
                epochs=training_epochs,
                use_log_transform=use_log_transform,
                verbose=verbose,
            ),
        }
    )
    final_rows.append(
        {
            "Dataset": dataset_name,
            "Model": "CNN_PSO_ensemble",
            **cross_validate_neural_ensemble(
                build_fn_factory=make_cnn_ensemble_builder_factory(input_length),
                best_params=best_cnn_hyperparameters,
                prepare_features_fn=reshape_for_cnn,
                X=X_main,
                y=y_main_raw,
                use_log_transform=use_log_transform,
                ensemble_seeds=ensemble_seeds,
                ensemble_epochs=ensemble_epochs,
                verbose=verbose,
            ),
        }
    )

    mlp_builder = make_mlp_builder(input_length)
    mlp_model, mlp_history, mlp_holdout_metrics = _evaluate_holdout_neural_model(
        model_builder=mlp_builder,
        train_model_fn=train_mlp_model,
        prepare_features_fn=_identity_features,
        X_main=X_main,
        y_main_fit=y_main_fit,
        X_holdout=X_holdout,
        y_holdout_raw=y_holdout_raw,
        batch_size=32,
        epochs=training_epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
    )
    models["mlp_baseline"] = mlp_model
    histories["mlp_baseline"] = {key: [float(value) for value in values] for key, values in mlp_history.items()}
    holdout_rows.append(_format_holdout_row(dataset_name, "MLP_baseline", mlp_holdout_metrics))
    final_rows.append(
        {
            "Dataset": dataset_name,
            "Model": "MLP_baseline",
            **cross_validate_mlp(
                model_builder=mlp_builder,
                X=X_main,
                y=y_main_raw,
                batch_size=32,
                epochs=training_epochs,
                use_log_transform=use_log_transform,
                verbose=verbose,
            ),
        }
    )

    best_mlp_hyperparameters, best_mlp_cost = tune_mlp_pso_once(
        X=X_main,
        y=y_main_raw,
        input_length=input_length,
        use_log_transform=use_log_transform,
        tuning_epochs=tuning_epochs,
        n_particles=n_particles,
        iters=iters,
        verbose=verbose,
    )
    hyperparams["mlp_pso"] = {**best_mlp_hyperparameters, "best_cost": float(best_mlp_cost)}
    tuned_mlp_builder = make_mlp_builder(input_length, hyperparameters=best_mlp_hyperparameters)
    tuned_mlp_model, tuned_mlp_history, tuned_mlp_holdout_metrics = _evaluate_holdout_neural_model(
        model_builder=tuned_mlp_builder,
        train_model_fn=train_mlp_model,
        prepare_features_fn=_identity_features,
        X_main=X_main,
        y_main_fit=y_main_fit,
        X_holdout=X_holdout,
        y_holdout_raw=y_holdout_raw,
        batch_size=int(best_mlp_hyperparameters.get("batch_size", 32)),
        epochs=training_epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
    )
    models["mlp_pso"] = tuned_mlp_model
    histories["mlp_pso"] = {key: [float(value) for value in values] for key, values in tuned_mlp_history.items()}
    holdout_rows.append(_format_holdout_row(dataset_name, "MLP_PSO", tuned_mlp_holdout_metrics))
    holdout_rows.append(
        _format_holdout_row(
            dataset_name,
            "MLP_PSO_ensemble",
            _evaluate_holdout_ensemble(
                build_fn_factory=make_mlp_ensemble_builder_factory(input_length),
                best_params=best_mlp_hyperparameters,
                prepare_features_fn=_identity_features,
                X_main=X_main,
                y_main_fit=y_main_fit,
                X_holdout=X_holdout,
                y_holdout_raw=y_holdout_raw,
                use_log_transform=use_log_transform,
                ensemble_seeds=ensemble_seeds,
                ensemble_epochs=ensemble_epochs,
                verbose=verbose,
            ),
        )
    )
    final_rows.append(
        {
            "Dataset": dataset_name,
            "Model": "MLP_PSO",
            **cross_validate_mlp(
                model_builder=tuned_mlp_builder,
                X=X_main,
                y=y_main_raw,
                batch_size=int(best_mlp_hyperparameters.get("batch_size", 32)),
                epochs=training_epochs,
                use_log_transform=use_log_transform,
                verbose=verbose,
            ),
        }
    )
    final_rows.append(
        {
            "Dataset": dataset_name,
            "Model": "MLP_PSO_ensemble",
            **cross_validate_neural_ensemble(
                build_fn_factory=make_mlp_ensemble_builder_factory(input_length),
                best_params=best_mlp_hyperparameters,
                prepare_features_fn=_identity_features,
                X=X_main,
                y=y_main_raw,
                use_log_transform=use_log_transform,
                ensemble_seeds=ensemble_seeds,
                ensemble_epochs=ensemble_epochs,
                verbose=verbose,
            ),
        }
    )

    return {
        "dataset_name": dataset_name,
        "dataset_key": dataset_key,
        "holdout_rows": holdout_rows,
        "final_rows": final_rows,
        "histories": histories,
        "hyperparams": hyperparams,
        "models": models,
    }


def run_full_benchmark(
    raw_datasets: Dict[str, pd.DataFrame] | None = None,
    use_log_transform: bool = True,
    training_epochs: int = 100,
    tuning_epochs: int = 30,
    n_particles: int = 15,
    iters: int = 25,
    ensemble_seeds: Sequence[int] = DEFAULT_ENSEMBLE_SEEDS,
    ensemble_epochs: int = 200,
    verbose: int = 0,
) -> Dict[str, object]:
    """Run the clean benchmark for all three datasets and return the assembled artifacts."""
    datasets = raw_datasets or load_all_raw_datasets()
    holdout_rows: list[Dict[str, float | str]] = []
    final_rows: list[Dict[str, float | str]] = []
    histories: Dict[str, Dict[str, Dict[str, list]]] = {}
    hyperparams: Dict[str, Dict[str, Dict[str, float | int]]] = {}
    models: Dict[str, Dict[str, object]] = {}

    for dataset_key in ("china", "cocomo81", "desharnais"):
        dataset_result = run_dataset_benchmark(
            dataset_name=DATASET_DISPLAY_NAMES[dataset_key],
            dataset_key=dataset_key,
            df=datasets[dataset_key],
            use_log_transform=use_log_transform,
            training_epochs=training_epochs,
            tuning_epochs=tuning_epochs,
            n_particles=n_particles,
            iters=iters,
            ensemble_seeds=ensemble_seeds,
            ensemble_epochs=ensemble_epochs,
            verbose=verbose,
        )
        holdout_rows.extend(dataset_result["holdout_rows"])
        final_rows.extend(dataset_result["final_rows"])
        histories[dataset_key] = dataset_result["histories"]
        hyperparams[dataset_key] = dataset_result["hyperparams"]
        models[dataset_key] = dataset_result["models"]

    holdout_results = pd.DataFrame(holdout_rows)[
        ["Dataset", "Model", "RMSE", "MAE", "R2", "MAPE", "MdMRE", "Pred25"]
    ]
    full_comparison_final = pd.DataFrame(final_rows)[
        [
            "Dataset",
            "Model",
            "RMSE_mean",
            "RMSE_std",
            "MAE_mean",
            "MAE_std",
            "R2_mean",
            "R2_std",
            "MAPE_mean",
            "MAPE_std",
            "MdMRE_mean",
            "MdMRE_std",
            "Pred25_mean",
            "Pred25_std",
        ]
    ]

    return {
        "holdout_results": _sort_results(holdout_results, "RMSE"),
        "full_comparison_final": _sort_results(full_comparison_final, "RMSE_mean"),
        "histories": histories,
        "hyperparams": hyperparams,
        "models": models,
    }


def save_benchmark_artifacts(
    benchmark_results: Dict[str, object],
    metrics_dir: Path = METRICS_DIR,
    models_dir: Path = MODELS_DIR,
) -> Dict[str, Path]:
    """Persist result tables, saved models, histories, and tuned hyperparameters."""
    metrics_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: Dict[str, Path] = {}

    holdout_results = benchmark_results["holdout_results"]
    full_comparison_final = benchmark_results["full_comparison_final"]
    saved_paths["holdout_results"] = save_metrics(
        holdout_results,
        file_name="holdout_results.csv",
        output_dir=metrics_dir,
    )
    saved_paths["full_comparison_final"] = save_metrics(
        full_comparison_final,
        file_name="full_comparison_final.csv",
        output_dir=metrics_dir,
    )

    cnn_comparison = holdout_results[
        holdout_results["Model"].isin(["CNN_baseline", "CNN_PSO", "CNN_PSO_ensemble"])
    ].rename(
        columns={
            "Dataset": "dataset",
            "Model": "model",
            "RMSE": "rmse",
            "MAE": "mae",
            "R2": "r2",
            "MAPE": "mape",
            "MdMRE": "mdmre",
            "Pred25": "pred25",
        }
    )
    saved_paths["cnn_vs_pso_metrics"] = save_metrics(
        cnn_comparison,
        file_name="cnn_vs_pso_metrics.csv",
        output_dir=metrics_dir,
    )

    with (models_dir / "best_hyperparams.json").open("w", encoding="utf-8") as file_handle:
        json.dump(benchmark_results["hyperparams"], file_handle, indent=2)
    saved_paths["best_hyperparams"] = models_dir / "best_hyperparams.json"

    with (models_dir / "training_histories.json").open("w", encoding="utf-8") as file_handle:
        json.dump(benchmark_results["histories"], file_handle, indent=2)
    saved_paths["training_histories"] = models_dir / "training_histories.json"

    for dataset_key, dataset_models in benchmark_results["models"].items():
        for model_key, model in dataset_models.items():
            model_path = models_dir / f"{model_key}_{dataset_key}.h5"
            model.save(model_path)
            saved_paths[f"{model_key}_{dataset_key}"] = model_path

    return saved_paths
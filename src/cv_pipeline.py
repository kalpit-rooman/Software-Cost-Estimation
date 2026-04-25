from __future__ import annotations

import random
from typing import Callable, Dict, Iterable, Tuple

import numpy as np
import tensorflow as tf
from sklearn.model_selection import KFold, train_test_split

from src.cnn_model import build_cnn_regressor, reshape_for_cnn, train_cnn_model
from src.evaluate import compute_regression_metrics
from src.feature_engineering import inverse_log_transform, log_transform_target
from src.pso_optimizer import build_cnn_pso_objective, decode_cnn_hyperparameters, get_cnn_pso_bounds, tune_cnn_with_pso


SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

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


def cross_validate_estimator(
    model_builder: Callable[[], object],
    X: np.ndarray,
    y: np.ndarray,
    use_log_transform: bool = True,
) -> Dict[str, float]:
    """Run 5-fold CV for sklearn-style estimators that implement fit/predict."""
    features = _as_float_array(X)
    targets = _as_float_array(y).ravel()
    kfold = KFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_metrics: list[Dict[str, float]] = []

    for train_index, test_index in kfold.split(features):
        X_train, X_test = features[train_index], features[test_index]
        y_train_raw, y_test_raw = targets[train_index], targets[test_index]
        y_train_fit = log_transform_target(y_train_raw, use_log_transform=use_log_transform)

        random.seed(SEED)
        np.random.seed(SEED)
        tf.random.set_seed(SEED)

        model = model_builder()
        model.fit(X_train, y_train_fit)
        predictions_fit = np.asarray(model.predict(X_test), dtype=np.float32).ravel()
        predictions = inverse_log_transform(predictions_fit, use_log_transform=use_log_transform)
        fold_metrics.append(compute_regression_metrics(y_test_raw, predictions))

    return summarize_fold_metrics(fold_metrics)


def cross_validate_cnn(
    model_builder: Callable[[], object],
    X: np.ndarray,
    y: np.ndarray,
    batch_size: int = 32,
    epochs: int = 100,
    use_log_transform: bool = True,
    verbose: int = 0,
) -> Dict[str, float]:
    """Run 5-fold CV for CNN models, rebuilding the model on every fold."""
    features = _as_float_array(X)
    targets = _as_float_array(y).ravel()
    kfold = KFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_metrics: list[Dict[str, float]] = []

    for train_index, test_index in kfold.split(features):
        X_train, X_test = features[train_index], features[test_index]
        y_train_raw, y_test_raw = targets[train_index], targets[test_index]
        y_train_fit = log_transform_target(y_train_raw, use_log_transform=use_log_transform).astype(np.float32)
        y_test_fit = log_transform_target(y_test_raw, use_log_transform=use_log_transform).astype(np.float32)

        X_train_cnn = reshape_for_cnn(X_train)
        X_test_cnn = reshape_for_cnn(X_test)

        random.seed(SEED)
        np.random.seed(SEED)
        tf.random.set_seed(SEED)

        model = model_builder()
        model, _ = train_cnn_model(
            model=model,
            x_train=X_train_cnn,
            y_train=y_train_fit,
            x_val=X_test_cnn,
            y_val=y_test_fit,
            epochs=epochs,
            batch_size=batch_size,
            verbose=verbose,
            use_callbacks=True,
        )
        predictions_fit = model.predict(X_test_cnn, verbose=0).ravel()
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
    """Tune CNN hyperparameters once on an 80% train/validation subset.

    The remaining 20% is kept outside PSO so tuning never scores on the final holdout split.
    """
    features = _as_float_array(X)
    targets = _as_float_array(y).ravel()

    # Keep 20% completely outside PSO to prevent the tuner from leaking into final evaluation.
    X_trainval, _, y_trainval, _ = train_test_split(
        features,
        targets,
        test_size=0.2,
        random_state=SEED,
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval,
        y_trainval,
        test_size=0.25,
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

    model_builder = lambda: build_cnn_regressor(
        input_length=input_length,
        filters=int(best_hyperparameters["filters"]),
        kernel_size=int(best_hyperparameters["kernel_size"]),
        dense_units=int(best_hyperparameters.get("dense_units", 64)),
        learning_rate=float(best_hyperparameters["learning_rate"]),
        dropout_rate=float(best_hyperparameters.get("dropout_rate", 0.2)),
        num_conv_layers=int(best_hyperparameters.get("num_conv_layers", 1)),
    )
    summary = cross_validate_cnn(
        model_builder=model_builder,
        X=X,
        y=y,
        batch_size=int(best_hyperparameters.get("batch_size", 32)),
        epochs=training_epochs,
        use_log_transform=use_log_transform,
        verbose=verbose,
    )
    return best_hyperparameters, best_cost, summary
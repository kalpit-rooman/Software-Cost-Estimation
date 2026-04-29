from __future__ import annotations

import random
from typing import Callable, Dict, Tuple

import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

from src.feature_engineering import inverse_log_transform, log_transform_target
from src.mlp_model import build_mlp_regressor, train_mlp_model


SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

_VALID_BATCH_SIZES = np.array([16, 32, 64], dtype=int)


def tune_mlp_with_pso(
    objective_fn: Callable[[np.ndarray], np.ndarray],
    dimensions: int,
    lower_bounds: np.ndarray,
    upper_bounds: np.ndarray,
    n_particles: int = 15,
    iters: int = 25,
    options: Dict[str, float] | None = None,
) -> Tuple[float, np.ndarray]:
    """Run global-best PSO and return best score and best MLP hyperparameter vector."""
    try:
        import pyswarms as ps
    except ImportError as exc:
        raise ImportError("pyswarms is required for PSO tuning") from exc

    if options is None:
        options = {"c1": 0.5, "c2": 0.3, "w": 0.9}

    optimizer = ps.single.GlobalBestPSO(
        n_particles=n_particles,
        dimensions=dimensions,
        options=options,
        bounds=(lower_bounds, upper_bounds),
    )

    best_cost, best_position = optimizer.optimize(objective_fn, iters=iters)
    return float(best_cost), best_position


def get_mlp_pso_bounds() -> Tuple[np.ndarray, np.ndarray]:
    """Return PSO bounds for MLP tuning.

    Order: [learning_rate_exp, dropout_rate, n_layers, units_per_layer, batch_size]
    where the actual learning rate is computed as ``10 ** learning_rate_exp``.
    """
    lower_bounds = np.array([-4.0, 0.1, 1, 32, 16], dtype=float)
    upper_bounds = np.array([-3.0, 0.4, 3, 256, 64], dtype=float)
    return lower_bounds, upper_bounds


def _decode_batch_size(batch_size_value: float) -> int:
    """Snap the searched batch size to the nearest supported value."""
    batch_index = int(np.argmin(np.abs(_VALID_BATCH_SIZES - batch_size_value)))
    return int(_VALID_BATCH_SIZES[batch_index])


def decode_mlp_hyperparameters(position: np.ndarray) -> Dict[str, float | int]:
    """Map a PSO position vector to typed MLP hyperparameters."""
    learning_rate_exp = float(np.clip(position[0], -4.0, -3.0))
    return {
        "learning_rate": float(10 ** learning_rate_exp),
        "learning_rate_exp": learning_rate_exp,
        "dropout_rate": float(np.clip(position[1], 0.1, 0.4)),
        "n_layers": int(np.clip(round(position[2]), 1, 3)),
        "units_per_layer": int(np.clip(round(position[3]), 32, 256)),
        "batch_size": _decode_batch_size(position[4]),
    }


def build_mlp_pso_objective(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    input_length: int,
    epochs: int = 30,
    use_log_transform: bool = True,
    verbose: int = 0,
) -> Callable[[np.ndarray], np.ndarray]:
    """Build a PSO objective that scores MLP particles on validation RMSE only."""
    X_train_array = np.asarray(X_train, dtype=np.float32)
    X_val_array = np.asarray(X_val, dtype=np.float32)
    # Fit on the PSO training split only so validation metrics stay leakage-free.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit(X_train_array).transform(X_train_array)
    X_val_scaled = scaler.transform(X_val_array)
    y_train_raw = np.asarray(y_train, dtype=np.float32).ravel()
    y_val_raw = np.asarray(y_val, dtype=np.float32).ravel()
    y_train_fit = log_transform_target(y_train_raw, use_log_transform=use_log_transform).astype(np.float32)

    def objective_fn(particles: np.ndarray) -> np.ndarray:
        scores = np.full(shape=(len(particles),), fill_value=1e6, dtype=float)
        for particle_index, particle in enumerate(particles):
            hyperparameters = decode_mlp_hyperparameters(particle)
            try:
                random.seed(SEED)
                np.random.seed(SEED)
                tf.random.set_seed(SEED)
                model = build_mlp_regressor(
                    input_length=input_length,
                    learning_rate=float(hyperparameters["learning_rate"]),
                    dropout_rate=float(hyperparameters["dropout_rate"]),
                    n_layers=int(hyperparameters["n_layers"]),
                    units_per_layer=int(hyperparameters["units_per_layer"]),
                    batch_size=int(hyperparameters["batch_size"]),
                    n_samples=len(X_train_scaled),
                )
                model, _ = train_mlp_model(
                    model=model,
                    x_train=np.asarray(X_train_scaled, dtype=np.float32),
                    y_train=y_train_fit,
                    epochs=epochs,
                    batch_size=int(hyperparameters["batch_size"]),
                    verbose=verbose,
                    use_callbacks=True,
                    validation_split=0.1,
                )
                val_predictions_fit = model.predict(np.asarray(X_val_scaled, dtype=np.float32), verbose=0).ravel()
                val_predictions = inverse_log_transform(
                    val_predictions_fit,
                    use_log_transform=use_log_transform,
                )
                scores[particle_index] = float(np.sqrt(mean_squared_error(y_val_raw, val_predictions)))
            except Exception:
                scores[particle_index] = 1e6
        return scores

    return objective_fn
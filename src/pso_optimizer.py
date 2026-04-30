from __future__ import annotations

import random
from typing import Callable, Dict, Tuple

import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

from src.cnn_model import build_cnn_regressor, reshape_for_cnn, train_cnn_model
from src.feature_engineering import inverse_log_transform, log_transform_target


SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

_VALID_BATCH_SIZES = np.array([8, 16, 32], dtype=int)


def tune_cnn_with_pso(
	objective_fn: Callable[[np.ndarray], np.ndarray],
	dimensions: int,
	lower_bounds: np.ndarray,
	upper_bounds: np.ndarray,
	n_particles: int = 6,
	iters: int = 6,
	options: Dict[str, float] | None = None,
) -> Tuple[float, np.ndarray]:
	"""Run global-best PSO and return best score and best hyperparameter vector."""
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


def get_cnn_pso_bounds() -> Tuple[np.ndarray, np.ndarray]:
	"""Return narrowed PSO bounds for stable CNN tuning.

	Order: [filters, kernel_size, learning_rate_exp, dropout_rate, num_conv_layers, batch_size]
	where the actual learning rate is computed as ``10 ** learning_rate_exp``.
	"""
	# Filters: 8 -> 32
	# Kernel size: keep 2 -> 5
	# Learning rate searched in log10 space: 0.0005 -> 0.01 -> log10 -> [-3.30103, -2.0]
	# Dropout: keep 0.1 -> 0.4
	# Num conv layers: 1 -> 3
	# Batch size: 8 -> 32
	lower_bounds = np.array([8, 2, -3.30103, 0.1, 1, 8], dtype=float)
	upper_bounds = np.array([32, 5, -2.0, 0.4, 3, 32], dtype=float)
	return lower_bounds, upper_bounds


def _decode_batch_size(batch_size_value: float) -> int:
	"""Snap the searched batch size to the nearest supported power-of-two value."""
	batch_index = int(np.argmin(np.abs(_VALID_BATCH_SIZES - batch_size_value)))
	return int(_VALID_BATCH_SIZES[batch_index])


def decode_cnn_hyperparameters(position: np.ndarray) -> Dict[str, float | int]:
	"""Map a PSO position vector to typed CNN hyperparameters.

	Primary 6D search order:
	[filters, kernel_size, learning_rate_exp, dropout_rate, num_conv_layers, batch_size]

	The learning rate is searched in log space and decoded with ``10 ** learning_rate_exp``.
	A legacy 4D vector is still accepted for backward compatibility.
	"""
	filters = int(np.clip(round(position[0]), 8, 32))
	kernel_size = int(np.clip(round(position[1]), 2, 5))

	params: Dict[str, float | int] = {
		"filters": filters,
		"kernel_size": kernel_size,
		"dense_units": 64,
		"learning_rate": 1e-3,
		"dropout_rate": 0.2,
		"num_conv_layers": 1,
		"batch_size": 32,
	}

	if len(position) >= 6:
		learning_rate_exp = float(np.clip(position[2], -3.30103, -2.0))
		params["learning_rate"] = float(10 ** learning_rate_exp)
		params["dropout_rate"] = float(np.clip(position[3], 0.1, 0.4))
		params["num_conv_layers"] = int(np.clip(round(position[4]), 1, 3))
		params["batch_size"] = _decode_batch_size(position[5])
		params["learning_rate_exp"] = learning_rate_exp
		return params

	if len(position) >= 4:
		params["dense_units"] = int(np.clip(round(position[2]), 8, 256))
		params["learning_rate"] = float(np.clip(position[3], 1e-4, 1e-2))

	return params


def build_cnn_pso_objective(
	X_train: np.ndarray,
	y_train: np.ndarray,
	X_val: np.ndarray,
	y_val: np.ndarray,
	input_length: int,
	epochs: int = 5,
	use_log_transform: bool = True,
	verbose: int = 0,
) -> Callable[[np.ndarray], np.ndarray]:
	"""Build a PSO objective that scores particles on validation RMSE only.

	The provided validation split is reserved for PSO scoring, while the final test split
	should remain untouched until the very end of evaluation.
	"""
	X_train_array = np.asarray(X_train, dtype=np.float32)
	X_val_array = np.asarray(X_val, dtype=np.float32)
	# Fit on the PSO training split only so validation metrics do not see future statistics.
	scaler = StandardScaler()
	X_train_scaled = scaler.fit(X_train_array).transform(X_train_array)
	X_val_scaled = scaler.transform(X_val_array)
	X_train_cnn = reshape_for_cnn(np.asarray(X_train_scaled, dtype=np.float32))
	X_val_cnn = reshape_for_cnn(np.asarray(X_val_scaled, dtype=np.float32))
	y_train_raw = np.asarray(y_train, dtype=np.float32).ravel()
	y_val_raw = np.asarray(y_val, dtype=np.float32).ravel()
	y_train_fit = log_transform_target(y_train_raw, use_log_transform=use_log_transform).astype(np.float32)

	def objective_fn(particles: np.ndarray) -> np.ndarray:
		scores = np.full(shape=(len(particles),), fill_value=1e6, dtype=float)
		for particle_index, particle in enumerate(particles):
			hyperparameters = decode_cnn_hyperparameters(particle)
			try:
				random.seed(SEED)
				np.random.seed(SEED)
				tf.random.set_seed(SEED)
				model = build_cnn_regressor(
					input_length=input_length,
					filters=int(hyperparameters["filters"]),
					kernel_size=int(hyperparameters["kernel_size"]),
					dense_units=int(hyperparameters.get("dense_units", 64)),
					learning_rate=float(hyperparameters["learning_rate"]),
					dropout_rate=float(hyperparameters.get("dropout_rate", 0.2)),
					num_conv_layers=int(hyperparameters.get("num_conv_layers", 1)),
					batch_size=int(hyperparameters.get("batch_size", 32)),
					n_samples=len(X_train_scaled),
				)
				model, _ = train_cnn_model(
					model=model,
					x_train=X_train_cnn,
					y_train=y_train_fit,
					epochs=epochs,
					batch_size=int(hyperparameters.get("batch_size", 32)),
					verbose=verbose,
					use_callbacks=False,
					validation_split=0.0,
				)
				val_predictions_fit = model.predict(X_val_cnn, verbose=0).ravel()
				val_predictions = inverse_log_transform(
					val_predictions_fit,
					use_log_transform=use_log_transform,
				)
				# Score particles on validation RMSE only so the final test split stays untouched.
				scores[particle_index] = float(np.sqrt(mean_squared_error(y_val_raw, val_predictions)))
			except Exception:
				scores[particle_index] = 1e6
		return scores

	return objective_fn


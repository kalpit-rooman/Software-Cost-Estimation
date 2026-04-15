from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


def build_cnn_regressor(
	input_length: int,
	filters: int = 32,
	kernel_size: int = 3,
	dense_units: int = 64,
	learning_rate: float = 1e-3,
):
	"""Build a simple 1D CNN for tabular-regression style feature vectors."""
	try:
		import tensorflow as tf
		from tensorflow.keras import Sequential
		from tensorflow.keras.layers import Conv1D, Dense, Flatten, Input
		from tensorflow.keras.optimizers import Adam
	except ImportError as exc:
		raise ImportError("tensorflow is required to build the CNN model") from exc

	model = Sequential(
		[
			Input(shape=(input_length, 1)),
			Conv1D(filters=filters, kernel_size=kernel_size, activation="relu", padding="same"),
			Flatten(),
			Dense(dense_units, activation="relu"),
			Dense(1),
		]
	)

	model.compile(optimizer=Adam(learning_rate=learning_rate), loss="mse", metrics=[tf.keras.metrics.MeanAbsoluteError()])
	return model


def reshape_for_cnn(x: np.ndarray) -> np.ndarray:
	"""Reshape tabular 2D features to (samples, features, channels)."""
	if x.ndim != 2:
		raise ValueError("Expected a 2D array for CNN input reshaping")
	return x.reshape((x.shape[0], x.shape[1], 1))


def train_cnn_model(
	model,
	x_train: np.ndarray,
	y_train: np.ndarray,
	x_val: np.ndarray,
	y_val: np.ndarray,
	epochs: int = 50,
	batch_size: int = 32,
	verbose: int = 0,
) -> Tuple[object, Dict[str, list]]:
	"""Train model and return the fitted model and training history."""
	history = model.fit(
		x_train,
		y_train,
		validation_data=(x_val, y_val),
		epochs=epochs,
		batch_size=batch_size,
		verbose=verbose,
	)
	return model, history.history

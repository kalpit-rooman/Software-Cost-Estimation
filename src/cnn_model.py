from __future__ import annotations

import random
from typing import Dict, List, Tuple

import numpy as np
import tensorflow as tf


SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)


def build_cnn_regressor(
	input_length: int,
	filters: int = 32,
	kernel_size: int = 3,
	dense_units: int = 64,
	learning_rate: float = 1e-3,
	dropout_rate: float = 0.2,
	num_conv_layers: int = 1,
):
	"""Build a 1D CNN with BatchNorm and Dropout for tabular regression.

	Parameters
	----------
	input_length : int
		Number of input features.
	filters : int
		Number of Conv1D filters per layer.
	kernel_size : int
		Kernel size for Conv1D layers.
	dense_units : int
		Neurons in the hidden Dense layer.
	learning_rate : float
		Adam optimizer learning rate.
	dropout_rate : float
		Dropout fraction after Dense layers (0-1).
	num_conv_layers : int
		Number of Conv1D + BatchNorm blocks (1-3).
	"""
	try:
		from tensorflow.keras import Sequential
		from tensorflow.keras.layers import (
			BatchNormalization,
			Conv1D,
			Dense,
			Dropout,
			Flatten,
			Input,
			MaxPooling1D,
		)
		from tensorflow.keras.optimizers import Adam
	except ImportError as exc:
		raise ImportError("tensorflow is required to build the CNN model") from exc

	layers: List = [Input(shape=(input_length, 1))]

	for i in range(num_conv_layers):
		layers.append(
			Conv1D(filters=filters, kernel_size=kernel_size, activation="relu", padding="same")
		)
		layers.append(BatchNormalization())
		# Add MaxPooling between conv layers only if sequence length allows
		if i < num_conv_layers - 1 and input_length > 2:
			layers.append(MaxPooling1D(pool_size=2, padding="same"))

	layers.append(Flatten())
	layers.append(Dense(dense_units, activation="relu"))
	layers.append(Dropout(dropout_rate))
	layers.append(Dense(1))

	model = Sequential(layers)
	model.compile(
		optimizer=Adam(learning_rate=learning_rate),
		loss="mse",
		metrics=[tf.keras.metrics.MeanAbsoluteError()],
	)
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
	epochs: int = 100,
	batch_size: int = 32,
	verbose: int = 0,
	use_callbacks: bool = True,
) -> Tuple[object, Dict[str, list]]:
	"""Train model with EarlyStopping and ReduceLROnPlateau callbacks."""
	try:
		from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
	except ImportError as exc:
		raise ImportError("tensorflow is required for training callbacks") from exc

	callbacks = []
	if use_callbacks:
		callbacks = [
			EarlyStopping(
				monitor="val_loss",
				patience=10,
				restore_best_weights=True,
				verbose=0,
			),
			ReduceLROnPlateau(
				monitor="val_loss",
				factor=0.5,
				patience=5,
				min_lr=1e-6,
				verbose=0,
			),
		]

	history = model.fit(
		x_train,
		y_train,
		validation_data=(x_val, y_val),
		epochs=epochs,
		batch_size=batch_size,
		verbose=verbose,
		callbacks=callbacks,
	)
	return model, history.history

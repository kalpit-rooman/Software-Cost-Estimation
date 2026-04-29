from __future__ import annotations

import random
from typing import Dict, List, Tuple

import numpy as np
import tensorflow as tf


SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)


def build_mlp_regressor(
    input_length: int,
    learning_rate: float = 1e-3,
    dropout_rate: float = 0.2,
    n_layers: int = 1,
    units_per_layer: int = 64,
    batch_size: int = 32,
    n_samples: int | None = None,
):
    """Build an MLP regressor for tabular effort estimation."""
    try:
        from tensorflow.keras import Sequential
        from tensorflow.keras.layers import Activation, BatchNormalization, Dense, Dropout, Input
        from tensorflow.keras.optimizers import Adam
    except ImportError as exc:
        raise ImportError("tensorflow is required to build the MLP model") from exc

    if n_samples is not None and n_samples < 100:
        # Keep the MLP shallow on very small datasets to reduce overfitting.
        n_layers = 1
        units_per_layer = min(units_per_layer, 64)

    layers: List = [Input(shape=(input_length,))]
    for _ in range(max(1, n_layers)):
        layers.append(Dense(units_per_layer))
        layers.append(BatchNormalization())
        layers.append(Activation("relu"))
        layers.append(Dropout(dropout_rate))
    layers.append(Dense(1))

    model = Sequential(layers)
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss="mse",
        metrics=[tf.keras.metrics.MeanAbsoluteError()],
    )
    return model


def get_default_callbacks() -> List[object]:
    """Return the default callback stack used across MLP training paths."""
    try:
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    except ImportError as exc:
        raise ImportError("tensorflow is required for training callbacks") from exc

    return [
        EarlyStopping(
            monitor="val_loss",
            patience=15,
            restore_best_weights=True,
            verbose=0,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=7,
            min_lr=1e-6,
            verbose=0,
        ),
    ]


def train_mlp_model(
    model,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray | None = None,
    y_val: np.ndarray | None = None,
    epochs: int = 100,
    batch_size: int = 32,
    verbose: int = 0,
    use_callbacks: bool = True,
    validation_split: float = 0.1,
) -> Tuple[object, Dict[str, list]]:
    """Train an MLP with the shared callback defaults."""
    callbacks = get_default_callbacks() if use_callbacks else []
    fit_kwargs = {
        "epochs": epochs,
        "batch_size": batch_size,
        "verbose": verbose,
        "callbacks": callbacks,
    }

    if x_val is not None and y_val is not None:
        fit_kwargs["validation_data"] = (x_val, y_val)
    elif validation_split > 0.0:
        fit_kwargs["validation_split"] = validation_split

    history = model.fit(x_train, y_train, **fit_kwargs)
    return model, history.history
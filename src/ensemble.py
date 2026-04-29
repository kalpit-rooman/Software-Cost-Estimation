from __future__ import annotations

from typing import Callable, Dict, Sequence

import numpy as np
import tensorflow as tf


DEFAULT_ENSEMBLE_SEEDS = (42, 7, 13, 99, 21)


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
from __future__ import annotations

from pathlib import Path
from typing import Dict

from src.baseline_models import MODEL_FILE_NAMES


ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"

DATASET_MODEL_DIRS: Dict[str, Path] = {
    "china": MODELS_DIR / "china",
    "cocomo81": MODELS_DIR / "cocomo81",
    "desharnais": MODELS_DIR / "desharnais",
}

MODEL_OUTPUT_KEYS: Dict[str, str] = {
    "RandomForest": "rf_prediction",
    "XGBoost": "xgb_prediction",
    "LinearRegression": "lr_prediction",
}

MODEL_RMSE_SCORES: Dict[str, Dict[str, float]] = {
    "china": {
        "RandomForest": 1636.3238338522758,
        "XGBoost": 1467.3213518914497,
        "LinearRegression": 53165.28424556006,
    },
    "cocomo81": {
        "RandomForest": 482.4925319563499,
        "XGBoost": 451.19558709684895,
        "LinearRegression": 395.08088778481056,
    },
    "desharnais": {
        "RandomForest": 2363.717631202568,
        "XGBoost": 2548.4416951395297,
        "LinearRegression": 1997.9362501688217,
    },
}

DEFAULT_ENSEMBLE_METHOD = "simple"


def build_inverse_rmse_weights(
    rmse_scores: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, float]]:
    """Derive normalized ensemble weights from inverse RMSE values."""
    dataset_weights: Dict[str, Dict[str, float]] = {}
    for dataset_name, dataset_scores in rmse_scores.items():
        inverse_scores = {
            model_name: 1.0 / float(score)
            for model_name, score in dataset_scores.items()
            if float(score) > 0
        }
        total = sum(inverse_scores.values())
        dataset_weights[dataset_name] = {
            model_name: float(weight / total)
            for model_name, weight in inverse_scores.items()
        }
    return dataset_weights


DEFAULT_ENSEMBLE_WEIGHTS: Dict[str, Dict[str, float]] = build_inverse_rmse_weights(MODEL_RMSE_SCORES)

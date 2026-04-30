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
        "RandomForest": 1604.754387,
        "XGBoost": 1503.300169,
        "LinearRegression": 1296.143319,
    },
    "cocomo81": {
        "RandomForest": 430.002079,
        "XGBoost": 620.308905,
        "LinearRegression": 1922.377594,
    },
    "desharnais": {
        "RandomForest": 2294.399361,
        "XGBoost": 2245.187760,
        "LinearRegression": 1943.914123,
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

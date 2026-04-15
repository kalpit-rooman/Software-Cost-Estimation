from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


ROOT_DIR = Path(__file__).resolve().parent.parent
METRICS_DIR = ROOT_DIR / "results" / "metrics"


def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
	"""Compute MAE and RMSE for regression outputs."""
	mae = float(mean_absolute_error(y_true, y_pred))
	rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
	return {"mae": mae, "rmse": rmse}


def evaluate_predictions(name: str, y_true: np.ndarray, y_pred: np.ndarray) -> pd.DataFrame:
	"""Return a single-row DataFrame containing model name and metrics."""
	metrics = compute_regression_metrics(y_true, y_pred)
	return pd.DataFrame([{"model": name, **metrics}])


def save_metrics(metrics_df: pd.DataFrame, file_name: str = "metrics.csv", output_dir: Path = METRICS_DIR) -> Path:
	"""Persist metrics table under results/metrics/."""
	output_dir.mkdir(parents=True, exist_ok=True)
	output_path = output_dir / file_name
	metrics_df.to_csv(output_path, index=False)
	return output_path

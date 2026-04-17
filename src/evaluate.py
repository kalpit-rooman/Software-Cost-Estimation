from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT_DIR = Path(__file__).resolve().parent.parent
METRICS_DIR = ROOT_DIR / "results" / "metrics"


def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
	"""Compute standard software-cost-estimation regression metrics.

	Returns dict with: mae, rmse, r2, mape, mdmre, pred25.
	"""
	y_true = np.asarray(y_true, dtype=np.float64).ravel()
	y_pred = np.asarray(y_pred, dtype=np.float64).ravel()

	mae = float(mean_absolute_error(y_true, y_pred))
	rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
	r2 = float(r2_score(y_true, y_pred))

	# Relative errors — guard against zero actuals
	nonzero_mask = y_true != 0
	if nonzero_mask.any():
		mre = np.abs((y_true[nonzero_mask] - y_pred[nonzero_mask]) / y_true[nonzero_mask])
		mape = float(np.mean(mre) * 100)
		mdmre = float(np.median(mre))
		pred25 = float(np.mean(mre <= 0.25) * 100)
	else:
		mape = float("nan")
		mdmre = float("nan")
		pred25 = float("nan")

	return {
		"mae": mae,
		"rmse": rmse,
		"r2": r2,
		"mape": mape,
		"mdmre": mdmre,
		"pred25": pred25,
	}


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

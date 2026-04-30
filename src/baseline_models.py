from __future__ import annotations

from typing import Callable, Dict

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression


SEED = 42

MODEL_FILE_NAMES = {
	"LinearRegression": "lr_model.pkl",
	"RandomForest": "rf_model.pkl",
	"XGBoost": "xgb_model.pkl",
}


def get_baseline_model_builders() -> Dict[str, Callable[[], object]]:
	"""Return fresh sklearn baseline builders with the project's standard settings."""
	builders: Dict[str, Callable[[], object]] = {
		"LinearRegression": lambda: LinearRegression(),
		"RandomForest": lambda: RandomForestRegressor(
			n_estimators=300,
			random_state=SEED,
			n_jobs=-1,
		),
	}
	try:
		from xgboost import XGBRegressor
	except ImportError:
		return builders

	builders["XGBoost"] = lambda: XGBRegressor(
		n_estimators=300,
		learning_rate=0.05,
		max_depth=6,
		subsample=0.8,
		colsample_bytree=0.8,
		objective="reg:squarederror",
		random_state=SEED,
		n_jobs=-1,
		verbosity=0,
	)
	return builders
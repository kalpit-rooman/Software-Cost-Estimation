from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple

import pandas as pd
from joblib import dump, load
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
	sys.path.insert(0, str(ROOT_DIR))

from src.baseline_models import MODEL_FILE_NAMES, get_baseline_model_builders
from src.data_loader import load_all_raw_datasets
from src.evaluate import compute_regression_metrics
from src.preprocess import build_feature_preprocessor, identify_effort_column, split_features_target


MODELS_DIR = ROOT_DIR / "models"
SEED = 42


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Train or reload baseline software-cost estimators.")
	parser.add_argument(
		"--dataset",
		choices=["all", "cocomo81", "desharnais", "china"],
		default="all",
		help="Dataset to process. Use 'all' to export models for every dataset.",
	)
	parser.add_argument(
		"--reuse-existing",
		action="store_true",
		help="Load an existing model artifact when present instead of retraining it.",
	)
	parser.add_argument(
		"--test-size",
		type=float,
		default=0.2,
		help="Holdout fraction for RMSE and MAE evaluation.",
	)
	return parser.parse_args()


def select_datasets(dataset_name: str) -> Dict[str, pd.DataFrame]:
	datasets = load_all_raw_datasets()
	if dataset_name == "all":
		return datasets
	return {dataset_name: datasets[dataset_name]}


def split_dataset(
	df: pd.DataFrame,
	target_col: str | None = None,
	*,
	test_size: float = 0.2,
	random_state: int = SEED,
) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
	resolved_target = identify_effort_column(df, preferred=target_col)
	prepared_df = df.drop_duplicates().dropna(subset=[resolved_target]).reset_index(drop=True)
	train_df, test_df = train_test_split(
		prepared_df,
		test_size=test_size,
		random_state=random_state,
	)
	return train_df.copy(), test_df.copy(), resolved_target


def build_model_pipeline(model_name: str, train_df: pd.DataFrame, target_col: str, estimator: object) -> Pipeline:
	preprocessor, _ = build_feature_preprocessor(
		train_df,
		target_col=target_col,
		scale_numeric=model_name == "LinearRegression",
	)
	return Pipeline(
		steps=[
			("preprocessor", preprocessor),
			("model", estimator),
		],
	)


def train_model(model_name: str, model_builder: object, train_df: pd.DataFrame, target_col: str) -> Pipeline:
	pipeline = build_model_pipeline(model_name, train_df, target_col, model_builder())
	X_train, y_train = split_features_target(train_df, target_col)
	pipeline.fit(X_train, y_train)
	return pipeline


def save_model(model: Pipeline, artifact_path: Path) -> None:
	artifact_path.parent.mkdir(parents=True, exist_ok=True)
	dump(model, artifact_path)


def load_saved_model(artifact_path: Path) -> Pipeline:
	return load(artifact_path)


def load_or_train_model(
	model_name: str,
	model_builder: object,
	train_df: pd.DataFrame,
	target_col: str,
	artifact_path: Path,
	*,
	reuse_existing: bool,
) -> Tuple[Pipeline, str]:
	if reuse_existing and artifact_path.exists():
		return load_saved_model(artifact_path), "loaded"

	model = train_model(model_name, model_builder, train_df, target_col)
	save_model(model, artifact_path)
	return model, "trained"


def evaluate_model(model: Pipeline, test_df: pd.DataFrame, target_col: str) -> Dict[str, float]:
	X_test, y_test = split_features_target(test_df, target_col)
	predictions = model.predict(X_test)
	metrics = compute_regression_metrics(y_test.to_numpy(), predictions)
	return {
		"rmse": float(metrics["rmse"]),
		"mae": float(metrics["mae"]),
	}


def process_dataset(
	dataset_name: str,
	df: pd.DataFrame,
	model_builders: Dict[str, object],
	*,
	reuse_existing: bool,
	test_size: float,
) -> list[Dict[str, str | float]]:
	train_df, test_df, target_col = split_dataset(df, test_size=test_size)
	dataset_model_dir = MODELS_DIR / dataset_name
	results: list[Dict[str, str | float]] = []

	for model_name, model_builder in model_builders.items():
		artifact_path = dataset_model_dir / MODEL_FILE_NAMES[model_name]
		model, status = load_or_train_model(
			model_name,
			model_builder,
			train_df,
			target_col,
			artifact_path,
			reuse_existing=reuse_existing,
		)
		metrics = evaluate_model(model, test_df, target_col)
		results.append(
			{
				"dataset": dataset_name,
				"model": model_name,
				"status": status,
				"rmse": metrics["rmse"],
				"mae": metrics["mae"],
				"artifact": str(artifact_path.relative_to(ROOT_DIR)),
			}
		)

	return results


def print_results(rows: Iterable[Dict[str, str | float]]) -> None:
	results_df = pd.DataFrame(rows)
	if results_df.empty:
		print("No results to display.")
		return

	results_df = results_df.sort_values(["dataset", "model"]).reset_index(drop=True)
	print(results_df.to_string(index=False))


def main() -> None:
	args = parse_args()
	model_builders = get_baseline_model_builders()
	selected_datasets = select_datasets(args.dataset)
	all_results: list[Dict[str, str | float]] = []

	for dataset_name, df in selected_datasets.items():
		all_results.extend(
			process_dataset(
				dataset_name,
				df,
				model_builders,
				reuse_existing=args.reuse_existing,
				test_size=args.test_size,
			)
		)

	print_results(all_results)


if __name__ == "__main__":
	main()
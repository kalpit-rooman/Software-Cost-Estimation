from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

from src.predictor import load_prediction_service, predict_cost
from src.preprocess import identify_effort_column


ROOT_DIR = Path(__file__).resolve().parent
DATASET_NAME = "cocomo81"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "processed" / f"{DATASET_NAME}_processed.csv"
CUSTOM_WEIGHTS = {
    "RandomForest": 0.5,
    "XGBoost": 0.3,
    "LinearRegression": 0.2,
}


def print_section(title: str) -> None:
    line = "=" * 80
    print(f"\n{line}\n{title}\n{line}")


def to_builtin(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): to_builtin(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_builtin(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def print_json(value: Any) -> None:
    print(json.dumps(to_builtin(value), indent=2, sort_keys=True))


def build_sample_input(dataset_name: str) -> dict[str, Any]:
    data_path = ROOT_DIR / "data" / "processed" / f"{dataset_name}_processed.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Processed dataset not found: {data_path}")

    dataframe = pd.read_csv(data_path)
    if dataframe.empty:
        raise ValueError(f"Processed dataset is empty: {data_path}")

    target_column = identify_effort_column(dataframe)
    feature_row = dataframe.iloc[0].drop(labels=[target_column])
    return {str(column): value for column, value in feature_row.to_dict().items()}


def run_case(
    title: str,
    action: Callable[[], Any],
    summary: list[tuple[str, str]],
    *,
    expect_error: bool = False,
) -> None:
    print_section(title)
    try:
        result = action()
        if expect_error:
            print("Unexpected success")
            print_json(result)
            summary.append((title, "UNEXPECTED SUCCESS"))
            return

        if result is not None:
            print_json(result)
        summary.append((title, "PASS"))
    except Exception as exc:
        if expect_error:
            print(f"Caught expected error: {type(exc).__name__}: {exc}")
            summary.append((title, "PASS"))
            return

        print(f"Error: {type(exc).__name__}: {exc}")
        summary.append((title, "FAIL"))


def main() -> None:
    summary: list[tuple[str, str]] = []

    print_section("Prediction Service Initialization")
    try:
        load_prediction_service()
        print("Service initialized successfully.")
    except Exception as exc:
        print(f"Failed to initialize prediction service: {type(exc).__name__}: {exc}")
        print_section("Summary")
        print("Initialization failed. No prediction scenarios were executed.")
        return

    try:
        sample_input = build_sample_input(DATASET_NAME)
    except Exception as exc:
        print_section("Sample Input Setup")
        print(f"Failed to build sample input: {type(exc).__name__}: {exc}")
        print_section("Summary")
        print("Sample input preparation failed. No prediction scenarios were executed.")
        return

    print_section("Sample Input Preview")
    print(f"Dataset: {DATASET_NAME}")
    print(f"Processed data file: {PROCESSED_DATA_PATH}")
    print(f"Feature count: {len(sample_input)}")
    preview_items = list(sample_input.items())[:5]
    print_json({key: value for key, value in preview_items})

    run_case(
        "A. Valid Prediction (Happy Path)",
        lambda: predict_cost(DATASET_NAME, sample_input),
        summary,
    )

    missing_field_input = dict(sample_input)
    removed_fields = list(missing_field_input)[:2]
    for field_name in removed_fields:
        missing_field_input.pop(field_name, None)

    run_case(
        "B. Missing Field Case",
        lambda: {
            "removed_fields": removed_fields,
            "prediction": predict_cost(DATASET_NAME, missing_field_input),
        },
        summary,
    )

    run_case(
        "C. Invalid Dataset",
        lambda: predict_cost("invalid_dataset", sample_input),
        summary,
        expect_error=True,
    )

    run_case(
        "D. Invalid Input Type",
        lambda: predict_cost(DATASET_NAME, "not a dictionary"),
        summary,
        expect_error=True,
    )

    run_case(
        "E1. Simple Ensemble",
        lambda: predict_cost(DATASET_NAME, sample_input, ensemble_method="simple"),
        summary,
    )

    run_case(
        "E2. Weighted Ensemble",
        lambda: {
            "weights": CUSTOM_WEIGHTS,
            "prediction": predict_cost(
                DATASET_NAME,
                sample_input,
                ensemble_method="weighted",
                weights=CUSTOM_WEIGHTS,
            ),
        },
        summary,
    )

    print_section("Summary")
    for title, status in summary:
        print(f"{status:<18} {title}")


if __name__ == "__main__":
    main()

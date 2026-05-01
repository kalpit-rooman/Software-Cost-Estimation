from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUPPORTED_DATASETS = ["china", "cocomo81", "desharnais"]
INSIGHT_TEMPLATE = "Best model for this dataset is {best_model}"

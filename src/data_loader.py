from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"


def load_csv_dataset(file_name: str, raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
	"""Load a CSV dataset from the raw data directory."""
	path = raw_dir / file_name
	return pd.read_csv(path)


def load_arff_dataset(file_name: str, raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
	"""Load an ARFF dataset into a pandas DataFrame."""
	try:
		from scipy.io import arff
	except ImportError as exc:
		raise ImportError("scipy is required to load ARFF files") from exc

	data, _ = arff.loadarff(raw_dir / file_name)
	df = pd.DataFrame(data)

	for col in df.columns:
		if df[col].dtype == object:
			df[col] = df[col].apply(lambda v: v.decode("utf-8") if isinstance(v, bytes) else v)

	return df


def load_all_raw_datasets(raw_dir: Path = RAW_DATA_DIR) -> Dict[str, pd.DataFrame]:
	"""Load all datasets used in this project with stable names."""
	return {
		"cocomo81": load_csv_dataset("COCOMO-81.csv", raw_dir=raw_dir),
		"desharnais": load_csv_dataset("Desharnais.csv", raw_dir=raw_dir),
		"china": load_arff_dataset("china.arff", raw_dir=raw_dir),
	}

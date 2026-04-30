from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder, StandardScaler


ROOT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"


def identify_effort_column(df: pd.DataFrame, preferred: Optional[str] = None) -> str:
	"""Try to identify the effort target column with common naming heuristics."""
	if preferred and preferred in df.columns:
		return preferred

	normalized = {c.lower().strip(): c for c in df.columns}
	for candidate in ("effort", "actual effort", "actual_effort", "personhours", "actual"):
		if candidate in normalized:
			return normalized[candidate]

	return df.columns[-1]


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
	"""Drop duplicates and fill missing values (median for numeric, mode for categorical)."""
	clean_df = df.drop_duplicates().copy()

	numeric_cols = clean_df.select_dtypes(include=["number"]).columns
	categorical_cols = clean_df.select_dtypes(exclude=["number"]).columns

	for col in numeric_cols:
		if clean_df[col].isna().any():
			clean_df[col] = clean_df[col].fillna(clean_df[col].median())

	for col in categorical_cols:
		if clean_df[col].isna().any():
			mode_series = clean_df[col].mode(dropna=True)
			fill_value = mode_series.iloc[0] if not mode_series.empty else "unknown"
			clean_df[col] = clean_df[col].fillna(fill_value)

	return clean_df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
	"""Label-encode categorical features without expanding the feature space."""
	categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()
	if not categorical_cols:
		return df.copy()
	encoded_df = df.copy()
	for column in categorical_cols:
		encoder = LabelEncoder()
		encoded_df[column] = encoder.fit_transform(encoded_df[column].astype(str))
	return encoded_df


def split_features_target(df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.Series]:
	"""Split DataFrame into features and target."""
	x = df.drop(columns=[target_col])
	y = df[target_col]
	return x, y


def build_feature_preprocessor(
	df: pd.DataFrame,
	target_col: Optional[str] = None,
	*,
	scale_numeric: bool = False,
) -> Tuple[ColumnTransformer, str]:
	"""Build a train-only tabular preprocessor for leakage-safe model fitting."""
	target = identify_effort_column(df, preferred=target_col)
	features, _ = split_features_target(df, target)

	numeric_cols = features.select_dtypes(include=["number"]).columns.tolist()
	categorical_cols = features.select_dtypes(exclude=["number"]).columns.tolist()

	transformers = []
	if numeric_cols:
		numeric_steps: list[tuple[str, object]] = [("imputer", SimpleImputer(strategy="median"))]
		if scale_numeric:
			numeric_steps.append(("scaler", StandardScaler()))
		transformers.append(("numeric", Pipeline(steps=numeric_steps), numeric_cols))

	if categorical_cols:
		transformers.append(
			(
				"categorical",
				Pipeline(
					steps=[
						("imputer", SimpleImputer(strategy="most_frequent")),
						(
							"encoder",
							OrdinalEncoder(
								handle_unknown="use_encoded_value",
								unknown_value=-1,
							),
						),
					],
				),
				categorical_cols,
			)
		)

	preprocessor = ColumnTransformer(
		transformers=transformers,
		remainder="drop",
		verbose_feature_names_out=False,
	)
	return preprocessor, target


def scale_numeric_features(
	df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Optional[StandardScaler]]:
	"""Scale numeric columns for notebook-style preprocessing workflows."""
	numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
	if not numeric_cols:
		return df.copy(), None

	scaler = StandardScaler()
	scaled_df = df.copy()
	scaled_values = pd.DataFrame(
		scaler.fit_transform(df[numeric_cols]),
		columns=numeric_cols,
		index=df.index,
	)
	for column in numeric_cols:
		scaled_df[column] = scaled_values[column].astype(float)
	return scaled_df, scaler


def preprocess_dataset(
	df: pd.DataFrame,
	target_col: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.Series, str]:
	"""Run full preprocessing and return model-ready X, y, and target column name."""
	target = identify_effort_column(df, preferred=target_col)
	cleaned = clean_dataframe(df)
	encoded = encode_categoricals(cleaned)

	if target not in encoded.columns:
		raise ValueError(f"Target column '{target}' was lost during encoding")

	x, y = split_features_target(encoded, target)
	# Do not fit a scaler here: fitting on the full dataset leaks fold statistics into CV.
	return x, y, target


def save_processed_dataset(df: pd.DataFrame, file_name: str, output_dir: Path = PROCESSED_DATA_DIR) -> Path:
	"""Save processed dataset under data/processed/."""
	output_dir.mkdir(parents=True, exist_ok=True)
	output_path = output_dir / file_name
	df.to_csv(output_path, index=False)
	return output_path


def save_multiple_processed(datasets: Dict[str, pd.DataFrame], output_dir: Path = PROCESSED_DATA_DIR) -> Dict[str, Path]:
	"""Save multiple DataFrames with a stable file naming convention."""
	output_paths: Dict[str, Path] = {}
	for name, df in datasets.items():
		output_paths[name] = save_processed_dataset(df, f"{name}_processed.csv", output_dir=output_dir)
	return output_paths

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd


def log_transform_target(y: pd.Series | np.ndarray) -> np.ndarray:
    """Apply log1p transform to effort target to reduce right-skew.

    Use ``inverse_log_transform`` on predictions before evaluation.
    """
    return np.log1p(np.asarray(y, dtype=np.float64))


def inverse_log_transform(y_pred: np.ndarray) -> np.ndarray:
    """Reverse log1p transform to get predictions back to original scale."""
    return np.expm1(np.asarray(y_pred, dtype=np.float64))


def remove_low_variance_features(
    x: pd.DataFrame,
    threshold: float = 0.01,
) -> Tuple[pd.DataFrame, list[str]]:
    """Drop features whose variance is below *threshold*.

    Returns the filtered DataFrame and list of dropped column names.
    """
    numeric = x.select_dtypes(include=["number"])
    variances = numeric.var()
    low_var_cols = variances[variances < threshold].index.tolist()
    return x.drop(columns=low_var_cols), low_var_cols


def select_correlated_features(
    x: pd.DataFrame,
    y: pd.Series,
    min_correlation: float = 0.1,
) -> Tuple[pd.DataFrame, list[str]]:
    """Keep only features whose absolute correlation with y >= *min_correlation*.

    Returns filtered DataFrame and list of kept column names.
    """
    numeric = x.select_dtypes(include=["number"])
    correlations = numeric.corrwith(y).abs()
    keep_cols = correlations[correlations >= min_correlation].index.tolist()
    # Always keep non-numeric columns
    non_numeric = x.select_dtypes(exclude=["number"]).columns.tolist()
    return x[keep_cols + non_numeric], keep_cols

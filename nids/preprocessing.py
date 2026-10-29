"""Training-only imputation/scaling and strict prediction validation."""
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from .schema import FEATURES


def signed_log1p(x):
    return np.sign(x) * np.log1p(np.abs(x))


def numeric_features(frame, strict=False):
    frame = frame.copy()
    frame.columns = frame.columns.astype(str).str.strip()
    if frame.columns.duplicated().any():
        raise ValueError("Duplicate column names after whitespace normalization.")
    missing = [c for c in FEATURES if c not in frame]
    if missing:
        raise ValueError("Missing required flow features: " + ", ".join(missing))
    if frame.empty:
        raise ValueError("The input CSV contains no flows.")
    raw = frame.loc[:, FEATURES]
    values = raw.apply(pd.to_numeric, errors="coerce")
    invalid = raw.notna() & values.isna() & raw.astype(str).apply(lambda c: c.str.strip().ne(""))
    if strict and invalid.any().any():
        columns = invalid.columns[invalid.any()].tolist()
        raise ValueError("Non-numeric values in: " + ", ".join(columns))
    values = values.replace([np.inf, -np.inf], np.nan)
    if strict and values.isna().all(axis=1).any():
        raise ValueError("One or more rows have no usable numeric feature values.")
    return values.astype("float64")


def build_preprocessor():
    # keep_empty_features preserves the input contract even for all-missing columns.
    return Pipeline([
        ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("log", FunctionTransformer(signed_log1p)),
        ("scale", StandardScaler()),
    ])


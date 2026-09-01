"""Schema validation for the raw/cleaned dataset."""

from __future__ import annotations

import pandas as pd

from ml.data.config import REQUIRED_COLUMNS


class SchemaValidationError(ValueError):
    """Raised when the dataset does not match the expected schema."""


def validate_schema(df: pd.DataFrame) -> None:
    """Ensure all required columns are present."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise SchemaValidationError(f"Missing required columns: {missing}")


def find_empty_rows(df: pd.DataFrame) -> pd.Series:
    """Return a boolean mask of rows with a blank/NaN value in any required column."""
    mask = pd.Series(False, index=df.index)
    for column in REQUIRED_COLUMNS:
        mask = mask | df[column].isna() | (df[column].astype(str).str.strip() == "")
    return mask

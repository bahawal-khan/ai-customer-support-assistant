"""Cleaning and normalization of the raw dataset."""

from __future__ import annotations

import re

import pandas as pd

from ml.data.config import REQUIRED_COLUMNS
from ml.data.schema import find_empty_rows, validate_schema

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse internal whitespace and strip leading/trailing whitespace."""
    return _WHITESPACE_RE.sub(" ", str(text).strip())


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Validate schema, normalize text columns, and drop empty rows.

    Returns the cleaned DataFrame and the number of rows removed for being
    empty in a required column.
    """
    validate_schema(df)

    # Drop empty/NaN rows before stringifying: astype(str) would otherwise turn a
    # real NaN/None into the literal text "nan"/"None", hiding it from later checks.
    empty_mask = find_empty_rows(df)
    removed = int(empty_mask.sum())
    cleaned = df.loc[~empty_mask].copy().reset_index(drop=True)

    for column in REQUIRED_COLUMNS:
        cleaned[column] = cleaned[column].astype(str).map(normalize_text)

    return cleaned, removed

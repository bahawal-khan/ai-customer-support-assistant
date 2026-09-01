"""Exact duplicate removal."""

from __future__ import annotations

import pandas as pd

from ml.data.config import REQUIRED_COLUMNS


def deduplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Drop exact duplicate rows (identical instruction/category/intent/response).

    Returns the deduplicated DataFrame and the number of rows removed.
    """
    before = len(df)
    deduped = df.drop_duplicates(subset=REQUIRED_COLUMNS).reset_index(drop=True)
    removed = before - len(deduped)
    return deduped, removed

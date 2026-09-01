"""Dataset statistics/metadata manifest."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ml.data.config import DATASET_FILENAME, DATASET_REPO_ID, SEED, SPLIT_RATIOS


def class_distribution(df: pd.DataFrame) -> dict[str, int]:
    return {str(k): int(v) for k, v in df["intent"].value_counts().sort_index().items()}


def build_manifest(
    *,
    raw_row_count: int,
    rows_removed_empty: int,
    rows_removed_duplicate: int,
    cleaned_row_count: int,
    label_mapping: dict[str, int],
    splits: dict[str, pd.DataFrame],
    seed: int = SEED,
    split_ratios: dict[str, float] = SPLIT_RATIOS,
) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "repo_id": DATASET_REPO_ID,
            "filename": DATASET_FILENAME,
        },
        "seed": seed,
        "split_ratios": split_ratios,
        "row_counts": {
            "raw": raw_row_count,
            "removed_empty": rows_removed_empty,
            "removed_duplicate": rows_removed_duplicate,
            "cleaned": cleaned_row_count,
            "splits": {name: len(split_df) for name, split_df in splits.items()},
        },
        "label_mapping": label_mapping,
        "class_distribution": {
            name: class_distribution(split_df) for name, split_df in splits.items()
        },
    }


def write_manifest(manifest: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

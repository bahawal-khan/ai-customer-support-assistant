import json
from pathlib import Path

import pandas as pd

from ml.data.manifest import build_manifest, write_manifest


def _splits() -> dict[str, pd.DataFrame]:
    return {
        "train": pd.DataFrame({"intent": ["a", "a", "b"]}),
        "validation": pd.DataFrame({"intent": ["a", "b"]}),
        "test": pd.DataFrame({"intent": ["a"]}),
    }


def test_build_manifest_reports_row_counts_and_distribution():
    manifest = build_manifest(
        raw_row_count=10,
        rows_removed_empty=1,
        rows_removed_duplicate=2,
        cleaned_row_count=6,
        label_mapping={"a": 0, "b": 1},
        splits=_splits(),
    )

    assert manifest["row_counts"]["raw"] == 10
    assert manifest["row_counts"]["removed_empty"] == 1
    assert manifest["row_counts"]["removed_duplicate"] == 2
    assert manifest["row_counts"]["cleaned"] == 6
    assert manifest["row_counts"]["splits"] == {"train": 3, "validation": 2, "test": 1}
    assert manifest["class_distribution"]["train"] == {"a": 2, "b": 1}
    assert manifest["label_mapping"] == {"a": 0, "b": 1}
    assert manifest["seed"] == 42


def test_write_manifest_produces_valid_json(tmp_path: Path):
    manifest = build_manifest(
        raw_row_count=10,
        rows_removed_empty=0,
        rows_removed_duplicate=0,
        cleaned_row_count=6,
        label_mapping={"a": 0, "b": 1},
        splits=_splits(),
    )
    destination = tmp_path / "metadata" / "dataset_manifest.json"

    write_manifest(manifest, destination)

    assert destination.exists()
    loaded = json.loads(destination.read_text(encoding="utf-8"))
    assert loaded == manifest

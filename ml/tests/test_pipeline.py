import json
from pathlib import Path

import pandas as pd
import pytest

from ml.data import pipeline
from ml.data.split import assert_no_leakage


def _write_fixture_csv(path: Path) -> Path:
    rows = []
    n_classes = 6
    unique_per_class = 25
    for class_index in range(n_classes):
        intent = f"intent_{class_index}"
        for i in range(unique_per_class):
            instruction = f"  intent {class_index}   example {i}  "
            rows.append(
                {
                    "flags": "B",
                    "instruction": instruction,
                    "category": "CATEGORY",
                    "intent": intent,
                    "response": f"response {class_index}-{i}",
                }
            )
    # exact duplicate row
    rows.append(dict(rows[0]))
    # empty instruction row (must be rejected)
    rows.append(
        {
            "flags": "B",
            "instruction": "   ",
            "category": "CATEGORY",
            "intent": "intent_0",
            "response": "response",
        }
    )

    df = pd.DataFrame(rows)
    csv_path = path / "fixture.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def fixture_csv(tmp_path: Path) -> Path:
    return _write_fixture_csv(tmp_path)


def test_run_pipeline_produces_processed_splits_and_manifest(monkeypatch, tmp_path, fixture_csv):
    monkeypatch.setattr(pipeline, "download_raw_dataset", lambda dest_dir: fixture_csv)

    processed_dir = tmp_path / "processed"
    metadata_dir = tmp_path / "metadata"

    manifest = pipeline.run_pipeline(
        raw_dir=tmp_path / "raw",
        processed_dir=processed_dir,
        metadata_dir=metadata_dir,
        seed=42,
    )

    assert (processed_dir / "train.csv").exists()
    assert (processed_dir / "validation.csv").exists()
    assert (processed_dir / "test.csv").exists()
    manifest_path = metadata_dir / "dataset_manifest.json"
    assert manifest_path.exists()
    assert json.loads(manifest_path.read_text(encoding="utf-8")) == manifest

    assert manifest["row_counts"]["raw"] == 6 * 25 + 2
    assert manifest["row_counts"]["removed_empty"] == 1
    assert manifest["row_counts"]["removed_duplicate"] == 1
    assert manifest["row_counts"]["cleaned"] == 6 * 25

    splits = {
        name: pd.read_csv(processed_dir / f"{name}.csv") for name in ("train", "validation", "test")
    }
    assert sum(len(df) for df in splits.values()) == manifest["row_counts"]["cleaned"]
    assert_no_leakage(splits)  # should not raise


def test_run_pipeline_is_reproducible_with_same_seed(monkeypatch, tmp_path, fixture_csv):
    monkeypatch.setattr(pipeline, "download_raw_dataset", lambda dest_dir: fixture_csv)

    manifest_a = pipeline.run_pipeline(
        raw_dir=tmp_path / "raw_a",
        processed_dir=tmp_path / "processed_a",
        metadata_dir=tmp_path / "metadata_a",
        seed=42,
    )
    manifest_b = pipeline.run_pipeline(
        raw_dir=tmp_path / "raw_b",
        processed_dir=tmp_path / "processed_b",
        metadata_dir=tmp_path / "metadata_b",
        seed=42,
    )

    assert manifest_a["row_counts"]["splits"] == manifest_b["row_counts"]["splits"]
    assert manifest_a["label_mapping"] == manifest_b["label_mapping"]
    assert manifest_a["class_distribution"] == manifest_b["class_distribution"]

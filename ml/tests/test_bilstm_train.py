from pathlib import Path

import pandas as pd
import pytest

from ml.bilstm import train as bilstm_train
from ml.bilstm.artifacts import load_artifact


def _write_split(path: Path, name: str, offset: int) -> None:
    rows = []
    n_classes = 4
    examples_per_class = 10
    for class_index in range(n_classes):
        intent = f"intent_{class_index}"
        for i in range(examples_per_class):
            rows.append(
                {
                    "instruction": (
                        f"topic{class_index} keyword{class_index} sample{offset}_{i} "
                        "extra words here"
                    ),
                    "category": "CATEGORY",
                    "intent": intent,
                    "response": "response",
                }
            )
    pd.DataFrame(rows).to_csv(path / f"{name}.csv", index=False)


@pytest.fixture
def processed_dir(tmp_path: Path) -> Path:
    processed = tmp_path / "processed"
    processed.mkdir()
    _write_split(processed, "train", offset=0)
    _write_split(processed, "validation", offset=1)
    _write_split(processed, "test", offset=2)
    return processed


def test_run_training_saves_artifact_and_evaluates_all_splits(tmp_path: Path, processed_dir: Path):
    artifacts_dir = tmp_path / "artifacts"

    result = bilstm_train.run_training(
        processed_dir=processed_dir, artifacts_dir=artifacts_dir, seed=42
    )

    assert result["version"] == "v1"
    version_dir = result["artifact_dir"]
    assert version_dir == artifacts_dir / "v1"
    for filename in (
        "model_state.pt",
        "vocabulary.json",
        "label_mapping.json",
        "config.json",
        "manifest.json",
        "metrics.json",
        "VERSION",
        "REPORT.md",
    ):
        assert (version_dir / filename).exists(), f"missing {filename}"

    assert set(result["metrics"]) == {"validation", "test"}
    for metrics in result["metrics"].values():
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert "macro_f1" in metrics
        assert "weighted_f1" in metrics
        assert len(metrics["confusion_matrix_labels"]) == 4


def test_run_training_manifest_records_early_stopping_fields(tmp_path: Path, processed_dir: Path):
    artifacts_dir = tmp_path / "artifacts"

    result = bilstm_train.run_training(
        processed_dir=processed_dir, artifacts_dir=artifacts_dir, seed=42
    )

    artifact = load_artifact(result["version"], artifacts_dir=artifacts_dir)
    manifest = artifact["manifest"]
    assert manifest["epochs_run"] >= manifest["best_epoch"] >= 1
    assert isinstance(manifest["stopped_early"], bool)


def test_run_training_second_run_increments_version(tmp_path: Path, processed_dir: Path):
    artifacts_dir = tmp_path / "artifacts"

    bilstm_train.run_training(processed_dir=processed_dir, artifacts_dir=artifacts_dir, seed=42)
    second = bilstm_train.run_training(
        processed_dir=processed_dir, artifacts_dir=artifacts_dir, seed=42
    )

    assert second["version"] == "v2"


def test_run_training_is_reproducible_for_the_same_seed(tmp_path: Path, processed_dir: Path):
    result_a = bilstm_train.run_training(
        processed_dir=processed_dir, artifacts_dir=tmp_path / "artifacts_a", seed=42
    )
    result_b = bilstm_train.run_training(
        processed_dir=processed_dir, artifacts_dir=tmp_path / "artifacts_b", seed=42
    )

    assert result_a["metrics"] == result_b["metrics"]


def test_run_training_builds_vocabulary_only_from_training_split(
    tmp_path: Path, processed_dir: Path
):
    """A word appearing only in validation/test text must not leak into the fit vocabulary."""
    leaked_word = "onlyinvalidationtext"
    validation_csv = processed_dir / "validation.csv"
    validation_df = pd.read_csv(validation_csv)
    validation_df.loc[0, "instruction"] = leaked_word
    validation_df.to_csv(validation_csv, index=False)

    artifacts_dir = tmp_path / "artifacts"
    result = bilstm_train.run_training(
        processed_dir=processed_dir, artifacts_dir=artifacts_dir, seed=42
    )

    artifact = load_artifact(result["version"], artifacts_dir=artifacts_dir)
    assert leaked_word not in artifact["vocabulary"].to_dict()

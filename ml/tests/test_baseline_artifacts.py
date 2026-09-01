from pathlib import Path

import pytest

from ml.baseline.artifacts import load_artifact, load_latest_version, next_version, save_artifact


def test_next_version_starts_at_v1_for_empty_directory(tmp_path: Path):
    assert next_version(tmp_path / "artifacts") == "v1"


def test_next_version_increments_past_existing_versions(tmp_path: Path):
    artifacts_dir = tmp_path / "artifacts"
    (artifacts_dir / "v1").mkdir(parents=True)
    (artifacts_dir / "v2").mkdir(parents=True)
    (artifacts_dir / "not-a-version").mkdir(parents=True)

    assert next_version(artifacts_dir) == "v3"


def test_save_and_load_artifact_roundtrip(tmp_path: Path):
    artifacts_dir = tmp_path / "artifacts"
    label_mapping = {"cancel_order": 0, "track_refund": 1}
    config = {"model_name": "tfidf_logreg", "seed": 42}
    manifest = {"row_counts": {"train": 10}}
    metrics = {"validation": {"accuracy": 0.9}}

    version_dir = save_artifact(
        version="v1",
        model={"kind": "fake-model"},
        vectorizer={"kind": "fake-vectorizer"},
        label_mapping=label_mapping,
        config=config,
        manifest=manifest,
        metrics=metrics,
        artifacts_dir=artifacts_dir,
    )

    assert version_dir == artifacts_dir / "v1"
    assert (version_dir / "model.joblib").exists()
    assert (version_dir / "vectorizer.joblib").exists()
    assert load_latest_version(artifacts_dir) == "v1"

    loaded = load_artifact(artifacts_dir=artifacts_dir)
    assert loaded["version"] == "v1"
    assert loaded["model"] == {"kind": "fake-model"}
    assert loaded["vectorizer"] == {"kind": "fake-vectorizer"}
    assert loaded["label_mapping"] == label_mapping
    assert loaded["config"] == config
    assert loaded["manifest"] == manifest
    assert loaded["metrics"] == metrics


def test_load_artifact_by_explicit_version(tmp_path: Path):
    artifacts_dir = tmp_path / "artifacts"
    for version in ("v1", "v2"):
        save_artifact(
            version=version,
            model={"kind": version},
            vectorizer={"kind": version},
            label_mapping={"a": 0},
            config={},
            manifest={},
            metrics={},
            artifacts_dir=artifacts_dir,
        )

    assert load_latest_version(artifacts_dir) == "v2"
    assert load_artifact("v1", artifacts_dir=artifacts_dir)["model"] == {"kind": "v1"}


def test_load_latest_version_raises_when_untrained(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_latest_version(tmp_path / "artifacts")


def test_load_artifact_raises_for_unknown_version(tmp_path: Path):
    artifacts_dir = tmp_path / "artifacts"
    save_artifact(
        version="v1",
        model={},
        vectorizer={},
        label_mapping={},
        config={},
        manifest={},
        metrics={},
        artifacts_dir=artifacts_dir,
    )

    with pytest.raises(FileNotFoundError):
        load_artifact("v99", artifacts_dir=artifacts_dir)

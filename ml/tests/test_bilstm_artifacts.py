from pathlib import Path

import pytest

from ml.bilstm.artifacts import load_artifact, load_latest_version, next_version, save_artifact
from ml.bilstm.model import build_model
from ml.bilstm.tokenizer import build_vocabulary


def _make_model_and_vocab():
    vocabulary = build_vocabulary(["hello world", "foo bar"], min_token_freq=1)
    model = build_model(vocab_size=len(vocabulary), num_classes=2)
    return model, vocabulary


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
    model, vocabulary = _make_model_and_vocab()
    label_mapping = {"cancel_order": 0, "track_refund": 1}
    config = {
        "model_name": "embedding_bilstm",
        "seed": 42,
        "vocab_size": len(vocabulary),
        "num_classes": 2,
        "max_seq_len": 32,
        "model": {
            "embedding_dim": model.embedding.embedding_dim,
            "hidden_dim": model.lstm.hidden_size,
            "num_lstm_layers": model.lstm.num_layers,
            "dropout": model.dropout.p,
        },
        "train": {},
    }
    manifest = {"row_counts": {"train": 10}}
    metrics = {"validation": {"accuracy": 0.9}}

    version_dir = save_artifact(
        version="v1",
        model=model,
        vocabulary=vocabulary,
        label_mapping=label_mapping,
        config=config,
        manifest=manifest,
        metrics=metrics,
        artifacts_dir=artifacts_dir,
    )

    assert version_dir == artifacts_dir / "v1"
    assert (version_dir / "model_state.pt").exists()
    assert (version_dir / "vocabulary.json").exists()
    assert load_latest_version(artifacts_dir) == "v1"

    loaded = load_artifact(artifacts_dir=artifacts_dir)
    assert loaded["version"] == "v1"
    assert loaded["label_mapping"] == label_mapping
    assert loaded["config"] == config
    assert loaded["manifest"] == manifest
    assert loaded["metrics"] == metrics
    assert loaded["vocabulary"].to_dict() == vocabulary.to_dict()

    # Reconstructed model weights must match the originally trained weights.
    for (name, original_param), (_, loaded_param) in zip(
        model.state_dict().items(), loaded["model"].state_dict().items()
    ):
        assert original_param.equal(loaded_param), name


def test_load_latest_version_raises_when_untrained(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_latest_version(tmp_path / "artifacts")


def test_load_artifact_raises_for_unknown_version(tmp_path: Path):
    artifacts_dir = tmp_path / "artifacts"
    model, vocabulary = _make_model_and_vocab()
    save_artifact(
        version="v1",
        model=model,
        vocabulary=vocabulary,
        label_mapping={"a": 0, "b": 1},
        config={
            "vocab_size": len(vocabulary),
            "num_classes": 2,
            "max_seq_len": 32,
            "model": {
                "embedding_dim": model.embedding.embedding_dim,
                "hidden_dim": model.lstm.hidden_size,
                "num_lstm_layers": model.lstm.num_layers,
                "dropout": model.dropout.p,
            },
            "train": {},
        },
        manifest={},
        metrics={},
        artifacts_dir=artifacts_dir,
    )

    with pytest.raises(FileNotFoundError):
        load_artifact("v99", artifacts_dir=artifacts_dir)

from pathlib import Path

import pandas as pd
import pytest

from ml.distilbert import train as distilbert_train
from ml.distilbert.artifacts import load_artifact
from ml.tests.distilbert_test_utils import build_tiny_model, build_tiny_tokenizer

N_CLASSES = 4
EXAMPLES_PER_CLASS = 10


def _vocab_words() -> list[str]:
    words = ["sample", "words", "extra", "here"]
    for class_index in range(N_CLASSES):
        words += [f"topic{class_index}", f"keyword{class_index}"]
    return words


def _write_split(path: Path, name: str, examples_per_class: int = EXAMPLES_PER_CLASS) -> None:
    rows = []
    for class_index in range(N_CLASSES):
        intent = f"intent_{class_index}"
        for i in range(examples_per_class):
            rows.append(
                {
                    "instruction": (
                        f"topic{class_index} keyword{class_index} sample words extra here"
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
    _write_split(processed, "train")
    _write_split(processed, "validation")
    _write_split(processed, "test")
    return processed


def _tiny_tokenizer():
    return build_tiny_tokenizer(_vocab_words())


def _tiny_model_builder(tokenizer):
    def builder(num_classes: int):
        return build_tiny_model(vocab_size=len(tokenizer), num_classes=num_classes)

    return builder


def test_run_training_saves_artifact_and_evaluates_all_splits(tmp_path: Path, processed_dir: Path):
    artifacts_dir = tmp_path / "artifacts"
    tokenizer = _tiny_tokenizer()

    result = distilbert_train.run_training(
        processed_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=_tiny_model_builder(tokenizer),
    )

    assert result["version"] == "v1"
    version_dir = result["artifact_dir"]
    assert version_dir == artifacts_dir / "v1"
    for dirname in ("model", "tokenizer"):
        assert (version_dir / dirname).exists(), f"missing {dirname}"
    for filename in (
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
        assert len(metrics["confusion_matrix_labels"]) == N_CLASSES


def test_run_training_manifest_records_early_stopping_fields(tmp_path: Path, processed_dir: Path):
    artifacts_dir = tmp_path / "artifacts"
    tokenizer = _tiny_tokenizer()

    result = distilbert_train.run_training(
        processed_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=_tiny_model_builder(tokenizer),
    )

    artifact = load_artifact(result["version"], artifacts_dir=artifacts_dir)
    manifest = artifact["manifest"]
    assert manifest["epochs_run"] >= manifest["best_epoch"] >= 1
    assert isinstance(manifest["stopped_early"], bool)
    assert manifest["mode"] == "smoke"


def test_run_training_best_checkpoint_selected_via_validation_not_test(
    tmp_path: Path, processed_dir: Path
):
    """The reported validation metrics must match the checkpoint chosen during training.

    Guards against test-set leakage into model/checkpoint selection: only
    ``best_validation_macro_f1`` (computed on the validation split) may drive
    which epoch's weights are kept.
    """
    artifacts_dir = tmp_path / "artifacts"
    tokenizer = _tiny_tokenizer()

    result = distilbert_train.run_training(
        processed_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=_tiny_model_builder(tokenizer),
    )

    manifest = load_artifact(result["version"], artifacts_dir=artifacts_dir)["manifest"]
    assert result["metrics"]["validation"]["macro_f1"] == pytest.approx(
        manifest["best_validation_macro_f1"]
    )


def test_run_training_second_run_increments_version(tmp_path: Path, processed_dir: Path):
    artifacts_dir = tmp_path / "artifacts"
    tokenizer = _tiny_tokenizer()
    builder = _tiny_model_builder(tokenizer)

    distilbert_train.run_training(
        processed_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=builder,
    )
    second = distilbert_train.run_training(
        processed_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=builder,
    )

    assert second["version"] == "v2"


def test_run_training_is_reproducible_for_the_same_seed(tmp_path: Path, processed_dir: Path):
    tokenizer = _tiny_tokenizer()
    builder = _tiny_model_builder(tokenizer)

    result_a = distilbert_train.run_training(
        processed_dir=processed_dir,
        artifacts_dir=tmp_path / "artifacts_a",
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=builder,
    )
    result_b = distilbert_train.run_training(
        processed_dir=processed_dir,
        artifacts_dir=tmp_path / "artifacts_b",
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=builder,
    )

    assert result_a["metrics"] == result_b["metrics"]


def test_run_training_smoke_mode_caps_row_counts_via_subsampling(tmp_path: Path):
    """End-to-end check that smoke-mode subsampling (not just the unit above)
    survives the full run_training path without dropping the label column.
    """
    processed = tmp_path / "processed_large"
    processed.mkdir()
    _write_split(processed, "train", examples_per_class=100)
    _write_split(processed, "validation", examples_per_class=50)
    _write_split(processed, "test", examples_per_class=50)

    artifacts_dir = tmp_path / "artifacts"
    tokenizer = _tiny_tokenizer()

    result = distilbert_train.run_training(
        processed_dir=processed,
        artifacts_dir=artifacts_dir,
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=_tiny_model_builder(tokenizer),
    )

    manifest = load_artifact(result["version"], artifacts_dir=artifacts_dir)["manifest"]
    smoke_config = distilbert_train.TRAIN_CONFIGS["smoke"]
    # Per-class flooring (max_examples // n_classes) means the capped count can land
    # slightly below the configured max, but it must always be less than the raw
    # (uncapped) row count and never exceed the configured cap.
    assert 0 < manifest["row_counts"]["train"] <= smoke_config["max_train_examples"]
    assert manifest["row_counts"]["train"] < N_CLASSES * 100
    assert 0 < manifest["row_counts"]["validation"] <= smoke_config["max_eval_examples"]
    assert 0 < manifest["row_counts"]["test"] <= smoke_config["max_eval_examples"]


def test_stratified_subsample_keeps_intent_column_and_per_class_coverage():
    """Regression test: pandas 3.x's groupby(...).apply(...) silently drops the
    grouping column unless handled explicitly, which previously crashed
    _encode_labels downstream with a KeyError on 'intent'.
    """
    df = pd.DataFrame(
        {
            "instruction": [f"text {i}" for i in range(30)],
            "intent": ["a"] * 10 + ["b"] * 10 + ["c"] * 10,
        }
    )

    sampled = distilbert_train._stratified_subsample(df, max_examples=9, seed=42)

    assert "intent" in sampled.columns
    assert len(sampled) == 9
    assert set(sampled["intent"].unique()) == {"a", "b", "c"}


def test_run_training_rejects_unknown_mode(tmp_path: Path, processed_dir: Path):
    with pytest.raises(ValueError):
        distilbert_train.run_training(
            processed_dir=processed_dir,
            artifacts_dir=tmp_path / "artifacts",
            seed=42,
            mode="bogus",
        )

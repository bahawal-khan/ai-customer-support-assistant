import inspect
from pathlib import Path

import pandas as pd
import pytest

from ml.baseline import train as baseline_train
from ml.baseline.predict import IntentClassifier as BaselineClassifier
from ml.bilstm import train as bilstm_train
from ml.bilstm.predict import IntentClassifier as BiLSTMClassifier
from ml.distilbert import train as distilbert_train
from ml.distilbert.predict import IntentClassifier as DistilBertClassifier
from ml.evaluation.compare import (
    artifact_size_bytes,
    build_comparison,
    evaluate_model,
    select_production_model,
)
from ml.evaluation.report import render_report
from ml.tests.distilbert_test_utils import build_tiny_model, build_tiny_tokenizer

N_CLASSES = 3
EXAMPLES_PER_CLASS = 8


def _write_split(path: Path, name: str, offset: int) -> None:
    rows = []
    for class_index in range(N_CLASSES):
        intent = f"intent_{class_index}"
        for i in range(EXAMPLES_PER_CLASS):
            rows.append(
                {
                    "instruction": (
                        f"topic{class_index} keyword{class_index} sample{offset}_{i} words"
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


@pytest.fixture
def label_names() -> list[str]:
    return sorted(f"intent_{i}" for i in range(N_CLASSES))


@pytest.fixture
def baseline_result(tmp_path: Path, processed_dir: Path, label_names: list[str]) -> dict:
    artifacts_dir = tmp_path / "baseline_artifacts"
    trained = baseline_train.run_training(
        processed_dir=processed_dir, artifacts_dir=artifacts_dir, seed=42
    )
    classifier = BaselineClassifier(version=trained["version"], artifacts_dir=artifacts_dir)
    test_df = pd.read_csv(processed_dir / "test.csv")
    return evaluate_model(
        model_name="tfidf_logreg",
        version=trained["version"],
        classifier=classifier,
        label_names=label_names,
        test_df=test_df,
        artifact_dir=trained["artifact_dir"],
    )


@pytest.fixture
def bilstm_result(tmp_path: Path, processed_dir: Path, label_names: list[str]) -> dict:
    artifacts_dir = tmp_path / "bilstm_artifacts"
    trained = bilstm_train.run_training(
        processed_dir=processed_dir, artifacts_dir=artifacts_dir, seed=42
    )
    classifier = BiLSTMClassifier(version=trained["version"], artifacts_dir=artifacts_dir)
    test_df = pd.read_csv(processed_dir / "test.csv")
    return evaluate_model(
        model_name="embedding_bilstm",
        version=trained["version"],
        classifier=classifier,
        label_names=label_names,
        test_df=test_df,
        artifact_dir=trained["artifact_dir"],
    )


@pytest.fixture
def distilbert_result(tmp_path: Path, processed_dir: Path, label_names: list[str]) -> dict:
    words = ["sample", "words"]
    for class_index in range(N_CLASSES):
        words += [f"topic{class_index}", f"keyword{class_index}"]
    tokenizer = build_tiny_tokenizer(words)

    def builder(num_classes: int):
        return build_tiny_model(vocab_size=len(tokenizer), num_classes=num_classes)

    artifacts_dir = tmp_path / "distilbert_artifacts"
    trained = distilbert_train.run_training(
        processed_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=builder,
    )
    classifier = DistilBertClassifier(version=trained["version"], artifacts_dir=artifacts_dir)
    test_df = pd.read_csv(processed_dir / "test.csv")
    return evaluate_model(
        model_name="distilbert",
        version=trained["version"],
        classifier=classifier,
        label_names=label_names,
        test_df=test_df,
        artifact_dir=trained["artifact_dir"],
    )


def test_evaluate_model_returns_full_contract(baseline_result: dict):
    m = baseline_result["metrics"]
    assert baseline_result["model_name"] == "tfidf_logreg"
    assert baseline_result["n_test_examples"] == N_CLASSES * EXAMPLES_PER_CLASS
    assert 0.0 <= m["accuracy"] <= 1.0
    assert {"macro_f1", "weighted_f1", "confusion_matrix", "confusion_matrix_labels"} <= m.keys()
    assert baseline_result["model_size_bytes"] > 0

    latency = baseline_result["latency_ms"]
    assert latency["n_samples"] < baseline_result["n_test_examples"]  # warmup samples excluded
    assert latency["mean_ms"] >= 0.0
    assert latency["min_ms"] <= latency["median_ms"] <= latency["max_ms"]


def test_evaluate_model_is_deterministic(
    tmp_path: Path, processed_dir: Path, label_names: list[str]
):
    """Re-scoring the same frozen artifact twice must reproduce identical metrics."""
    artifacts_dir = tmp_path / "baseline_artifacts"
    trained = baseline_train.run_training(
        processed_dir=processed_dir, artifacts_dir=artifacts_dir, seed=42
    )
    test_df = pd.read_csv(processed_dir / "test.csv")

    def _score() -> dict:
        classifier = BaselineClassifier(version=trained["version"], artifacts_dir=artifacts_dir)
        return evaluate_model(
            model_name="tfidf_logreg",
            version=trained["version"],
            classifier=classifier,
            label_names=label_names,
            test_df=test_df,
            artifact_dir=trained["artifact_dir"],
        )

    first = _score()
    second = _score()
    assert first["metrics"] == second["metrics"]


def test_artifact_size_bytes_matches_directory_contents(tmp_path: Path):
    artifact_dir = tmp_path / "artifact"
    artifact_dir.mkdir()
    (artifact_dir / "a.bin").write_bytes(b"1234567890")
    (artifact_dir / "b.bin").write_bytes(b"abcde")

    assert artifact_size_bytes(artifact_dir) == 15


def test_artifact_size_bytes_missing_directory_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        artifact_size_bytes(tmp_path / "does-not-exist")


def _fake_result(model_name: str, macro_f1: float, mean_latency_ms: float) -> dict:
    return {
        "model_name": model_name,
        "version": "v1",
        "n_test_examples": 10,
        "metrics": {"macro_f1": macro_f1, "weighted_f1": macro_f1, "accuracy": macro_f1},
        "model_size_bytes": 1000,
        "latency_ms": {"mean_ms": mean_latency_ms, "median_ms": mean_latency_ms},
    }


def test_select_production_model_picks_clear_primary_metric_winner():
    results = [
        _fake_result("slow_but_best", macro_f1=0.99, mean_latency_ms=500.0),
        _fake_result("fast_but_worse", macro_f1=0.80, mean_latency_ms=1.0),
    ]

    selection = select_production_model(results)

    assert selection["selected_model"] == "slow_but_best"
    assert "no tie-break" in selection["rationale"]


def test_select_production_model_breaks_near_tie_with_latency():
    results = [
        _fake_result("slightly_better_but_slow", macro_f1=0.9905, mean_latency_ms=500.0),
        _fake_result("slightly_worse_but_fast", macro_f1=0.9900, mean_latency_ms=1.0),
    ]

    selection = select_production_model(results, tie_epsilon=0.002)

    assert selection["selected_model"] == "slightly_worse_but_fast"
    assert "tied" in selection["rationale"]


def test_select_production_model_rejects_empty_results():
    with pytest.raises(ValueError):
        select_production_model([])


def test_build_comparison_and_report_cover_all_three_models(
    baseline_result: dict, bilstm_result: dict, distilbert_result: dict, processed_dir: Path
):
    results = [baseline_result, bilstm_result, distilbert_result]
    comparison = build_comparison(results, test_csv_path=processed_dir / "test.csv", seed=42)

    assert set(comparison["models"]) == {"tfidf_logreg", "embedding_bilstm", "distilbert"}
    assert comparison["reproducibility"]["same_split_used_by_all_models"] is True
    assert comparison["reproducibility"]["checkpoint_selection_used_only_validation_metrics"]

    # These tiny synthetic models can legitimately tie on macro F1 (e.g. both hit a
    # trivial 1.0 on toy data), in which case select_production_model breaks the tie
    # on latency -- so assert the selection contract's invariant rather than a naive
    # argmax, which the exact winner-selection logic already covers in isolation above.
    best_macro_f1 = max(r["metrics"]["macro_f1"] for r in results)
    selected = next(
        r for r in results if r["model_name"] == comparison["selection"]["selected_model"]
    )
    assert best_macro_f1 - selected["metrics"]["macro_f1"] <= comparison["selection"]["tie_epsilon"]

    report = render_report(comparison)
    assert "Phase 06" in report
    assert "tfidf_logreg" in report
    assert "embedding_bilstm" in report
    assert "distilbert" in report
    assert comparison["selection"]["selected_model"] in report


@pytest.mark.parametrize(
    "train_module_name",
    ["ml.bilstm.train", "ml.distilbert.train"],
)
def test_checkpoint_selection_never_reads_the_test_loader(train_module_name: str):
    """Regression guard: best-epoch/early-stopping selection must depend only on
    validation metrics. If a future edit starts comparing epochs on ``test_loader``
    inside the training loop, this test should fail before it ships.
    """
    import importlib

    module = importlib.import_module(train_module_name)
    source = inspect.getsource(module.run_training)

    loop_start = source.index("for epoch in range")
    loop_end = source.index("assert best_state is not None")
    loop_body = source[loop_start:loop_end]

    assert "test_loader" not in loop_body
    assert "test_subset" not in loop_body


def test_baseline_fits_the_model_exactly_once_on_training_data():
    """Regression guard: the baseline must never call ``.fit`` on validation/test data."""
    import ml.baseline.train as module

    source = inspect.getsource(module.run_training)
    assert source.count(".fit(") == 1
    fit_line = next(line for line in source.splitlines() if ".fit(" in line)
    assert "x_train" in fit_line and "y_train" in fit_line

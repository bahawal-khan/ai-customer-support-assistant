from pathlib import Path

import pandas as pd
import pytest

from ml.baseline import train as baseline_train
from ml.baseline.predict import IntentClassifier, InvalidComplaintTextError


def _write_split(path: Path, name: str, offset: int) -> None:
    rows = []
    n_classes = 3
    examples_per_class = 6
    for class_index in range(n_classes):
        intent = f"intent_{class_index}"
        for i in range(examples_per_class):
            rows.append(
                {
                    "instruction": f"topic{class_index} keyword{class_index} sample {offset}-{i}",
                    "category": "CATEGORY",
                    "intent": intent,
                    "response": "response",
                }
            )
    pd.DataFrame(rows).to_csv(path / f"{name}.csv", index=False)


@pytest.fixture
def trained_artifact(tmp_path: Path) -> tuple[Path, str]:
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    _write_split(processed_dir, "train", offset=0)
    _write_split(processed_dir, "validation", offset=1)
    _write_split(processed_dir, "test", offset=2)

    artifacts_dir = tmp_path / "artifacts"
    result = baseline_train.run_training(
        processed_dir=processed_dir, artifacts_dir=artifacts_dir, seed=42
    )
    return artifacts_dir, result["version"]


def test_predict_intent_returns_full_contract(trained_artifact):
    artifacts_dir, version = trained_artifact
    classifier = IntentClassifier(version=version, artifacts_dir=artifacts_dir)

    prediction = classifier.predict_intent("topic1 keyword1 sample")

    assert prediction.label == "intent_1"
    assert 0.0 <= prediction.confidence <= 1.0
    assert prediction.model_name == "tfidf_logreg"
    assert prediction.model_version == version
    assert len(prediction.top_k) == 3
    assert prediction.top_k[0]["label"] == "intent_1"
    # top_k must be ranked by descending confidence.
    confidences = [entry["confidence"] for entry in prediction.top_k]
    assert confidences == sorted(confidences, reverse=True)


def test_predict_intent_is_deterministic(trained_artifact):
    artifacts_dir, version = trained_artifact
    classifier = IntentClassifier(version=version, artifacts_dir=artifacts_dir)

    first = classifier.predict_intent("topic0 keyword0 sample")
    second = classifier.predict_intent("topic0 keyword0 sample")

    assert first == second


def test_predict_intent_rejects_empty_text(trained_artifact):
    artifacts_dir, version = trained_artifact
    classifier = IntentClassifier(version=version, artifacts_dir=artifacts_dir)

    with pytest.raises(InvalidComplaintTextError):
        classifier.predict_intent("   ")


def test_predict_intent_rejects_non_string_text(trained_artifact):
    artifacts_dir, version = trained_artifact
    classifier = IntentClassifier(version=version, artifacts_dir=artifacts_dir)

    with pytest.raises(InvalidComplaintTextError):
        classifier.predict_intent(None)  # type: ignore[arg-type]

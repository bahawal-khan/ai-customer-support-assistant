from pathlib import Path

import pandas as pd
import pytest

from ml.distilbert import train as distilbert_train
from ml.distilbert.predict import IntentClassifier, InvalidComplaintTextError
from ml.tests.distilbert_test_utils import build_tiny_model, build_tiny_tokenizer

N_CLASSES = 3
EXAMPLES_PER_CLASS = 10


def _vocab_words() -> list[str]:
    words = ["sample", "words"]
    for class_index in range(N_CLASSES):
        words += [f"topic{class_index}", f"keyword{class_index}"]
    return words


def _write_split(path: Path, name: str) -> None:
    rows = []
    for class_index in range(N_CLASSES):
        intent = f"intent_{class_index}"
        for i in range(EXAMPLES_PER_CLASS):
            rows.append(
                {
                    "instruction": f"topic{class_index} keyword{class_index} sample words",
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
    _write_split(processed_dir, "train")
    _write_split(processed_dir, "validation")
    _write_split(processed_dir, "test")

    tokenizer = build_tiny_tokenizer(_vocab_words())

    def builder(num_classes: int):
        return build_tiny_model(vocab_size=len(tokenizer), num_classes=num_classes)

    artifacts_dir = tmp_path / "artifacts"
    result = distilbert_train.run_training(
        processed_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        seed=42,
        mode="smoke",
        tokenizer=tokenizer,
        model_builder=builder,
    )
    return artifacts_dir, result["version"]


def test_predict_intent_returns_full_contract(trained_artifact):
    artifacts_dir, version = trained_artifact
    classifier = IntentClassifier(version=version, artifacts_dir=artifacts_dir)

    prediction = classifier.predict_intent("topic1 keyword1 sample words")

    assert prediction.label in {"intent_0", "intent_1", "intent_2"}
    assert 0.0 <= prediction.confidence <= 1.0
    assert prediction.model_name == "distilbert"
    assert prediction.model_version == version
    assert len(prediction.top_k) == 3
    assert prediction.top_k[0]["label"] == prediction.label
    confidences = [entry["confidence"] for entry in prediction.top_k]
    assert confidences == sorted(confidences, reverse=True)


def test_predict_intent_is_deterministic(trained_artifact):
    artifacts_dir, version = trained_artifact
    classifier = IntentClassifier(version=version, artifacts_dir=artifacts_dir)

    first = classifier.predict_intent("topic0 keyword0 sample words")
    second = classifier.predict_intent("topic0 keyword0 sample words")

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


def test_predict_intent_handles_out_of_vocabulary_text(trained_artifact):
    artifacts_dir, version = trained_artifact
    classifier = IntentClassifier(version=version, artifacts_dir=artifacts_dir)

    prediction = classifier.predict_intent("completely unseen gibberish phrase")

    assert prediction.label in {"intent_0", "intent_1", "intent_2"}

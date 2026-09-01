"""Phase 12 IntentService tests.

Uses the same offline, randomly-initialized tiny DistilBERT fixture as
ml/tests/test_distilbert_predict.py (no network, no download) to verify
IntentService correctly delegates to ml.distilbert.predict.IntentClassifier
and translates its errors into the app's controlled error types
(docs/ml/ML_INFERENCE_SPEC.md "inference errors must be controlled").
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.distilbert import train as distilbert_train  # noqa: E402
from ml.distilbert.predict import IntentClassifier  # noqa: E402
from ml.tests.distilbert_test_utils import build_tiny_model, build_tiny_tokenizer  # noqa: E402

import app.services.intent.service as intent_service_module  # noqa: E402
from app.core.errors import ModelUnavailableError, ValidationAppError  # noqa: E402
from app.services.intent.service import IntentService  # noqa: E402

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
        for _ in range(EXAMPLES_PER_CLASS):
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
def trained_classifier(tmp_path: Path) -> IntentClassifier:
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
    return IntentClassifier(version=result["version"], artifacts_dir=artifacts_dir)


def test_predict_intent_delegates_to_classifier(trained_classifier):
    service = IntentService(classifier=trained_classifier)

    prediction = service.predict_intent("topic1 keyword1 sample words")

    assert prediction.label in {"intent_0", "intent_1", "intent_2"}
    assert prediction.model_name == "distilbert"


def test_predict_intent_rejects_empty_text_as_validation_error(trained_classifier):
    service = IntentService(classifier=trained_classifier)

    with pytest.raises(ValidationAppError):
        service.predict_intent("   ")


def test_missing_artifact_raises_model_unavailable_error(monkeypatch):
    def _raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError("no artifact")

    monkeypatch.setattr(intent_service_module, "IntentClassifier", _raise_file_not_found)
    service = IntentService()

    with pytest.raises(ModelUnavailableError):
        service.predict_intent("Where is my refund?")


def test_unexpected_classifier_error_raises_model_unavailable_error(trained_classifier):
    class _BrokenClassifier:
        def predict_intent(self, text):
            raise RuntimeError("tensor shape mismatch")

    service = IntentService(classifier=_BrokenClassifier())

    with pytest.raises(ModelUnavailableError):
        service.predict_intent("Where is my refund?")


def test_classifier_loaded_once_and_reused(trained_classifier, monkeypatch):
    created = []
    monkeypatch.setattr(
        intent_service_module,
        "IntentClassifier",
        lambda *a, **k: created.append(1) or trained_classifier,
    )
    service = IntentService()

    service.predict_intent("topic0 keyword0 sample words")
    service.predict_intent("topic0 keyword0 sample words")

    assert len(created) == 1

"""Phase 12 sentiment tests.

Unit tests use a fake provider (no model download); the live test mirrors
test_embedding_provider.py's pattern -- it loads the real configured
SENTIMENT_MODEL and skips if unavailable in this environment
(docs/ml/ML_INFERENCE_SPEC.md "inference errors must be controlled",
docs/testing/TESTING_SPEC.md).
"""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.core.errors import ModelUnavailableError, ValidationAppError
from app.providers.sentiment_provider import (
    SentimentPrediction,
    SentimentProvider,
    _normalize_label,
)
from app.services.sentiment.service import SentimentService

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"


class _FakeProvider:
    def __init__(self, label: str = "negative", confidence: float = 0.9):
        self._label = label
        self._confidence = confidence
        self.calls: list[str] = []

    def predict(self, text: str) -> SentimentPrediction:
        self.calls.append(text)
        return SentimentPrediction(label=self._label, confidence=self._confidence)


def test_analyze_sentiment_delegates_to_provider():
    provider = _FakeProvider(label="positive", confidence=0.75)
    service = SentimentService(provider=provider)

    result = service.analyze_sentiment("Thanks, that solved it!")

    assert result.label == "positive"
    assert result.confidence == pytest.approx(0.75)
    assert provider.calls == ["Thanks, that solved it!"]


def test_analyze_sentiment_rejects_empty_text():
    service = SentimentService(provider=_FakeProvider())

    with pytest.raises(ValidationAppError):
        service.analyze_sentiment("   ")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("negative", "negative"),
        ("Neutral", "neutral"),
        ("POSITIVE", "positive"),
        ("LABEL_0", "negative"),
        ("LABEL_1", "neutral"),
        ("LABEL_2", "positive"),
    ],
)
def test_normalize_label(raw, expected):
    assert _normalize_label(raw) == expected


def test_missing_model_name_raises_model_unavailable_error():
    provider = SentimentProvider(Settings(_env_file=None, SENTIMENT_MODEL=""))

    with pytest.raises(ModelUnavailableError):
        provider.predict("hello")


# --- Live model test (mirrors test_embedding_provider.py) -------------------


@pytest.fixture(scope="module")
def live_provider() -> SentimentProvider:
    provider = SentimentProvider(Settings(_env_file=None, SENTIMENT_MODEL=MODEL_NAME))
    try:
        provider.predict("connectivity probe")
    except ModelUnavailableError as exc:
        pytest.skip(f"Sentiment model unavailable in this environment: {exc}")
    return provider


def test_live_predicts_negative_for_angry_complaint(live_provider):
    result = live_provider.predict(
        "This is the worst service ever, I am furious and want a refund."
    )

    assert result.label == "negative"
    assert 0.0 <= result.confidence <= 1.0


def test_live_predicts_positive_for_thankful_message(live_provider):
    result = live_provider.predict("Thank you so much, your team was amazing and fixed it fast!")

    assert result.label == "positive"


def test_live_label_is_always_canonical(live_provider):
    for text in ["Where is my order?", "This is unacceptable.", "Great, thanks!"]:
        result = live_provider.predict(text)
        assert result.label in {"positive", "neutral", "negative"}

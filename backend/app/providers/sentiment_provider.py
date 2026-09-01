"""Sentiment provider wrapping a configurable Hugging Face sentiment-analysis model.

docs/backend/BACKEND_SPEC.md: "SentimentService: Uses a clean provider
interface." Mirrors the EmbeddingProvider pattern
(app/providers/embedding_provider.py): lazy-loaded on first use,
configuration-driven via SENTIMENT_MODEL, never trains.

The dataset (docs/ml/DATASET_SPEC.md) only labels intent, so sentiment is not
one of the trained TF-IDF/BiLSTM/DistilBERT classifiers -- it is a separate,
off-the-shelf pretrained model, used purely for inference. No accuracy claim
is made about this model; it is not one of the project's evaluated/compared
classifiers (docs/ml/ML_TRAINING_SPEC.md, REQUIREMENTS.md "Never fabricate
metrics").
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.core.config import Settings, get_settings
from app.core.errors import ModelUnavailableError

CANONICAL_LABELS = frozenset({"positive", "neutral", "negative"})
MAX_SEQ_LEN = 128


@dataclass(frozen=True)
class SentimentPrediction:
    label: str
    confidence: float


def _normalize_label(raw_label: str) -> str:
    normalized = raw_label.strip().lower()
    if normalized in CANONICAL_LABELS:
        return normalized
    return {"label_0": "negative", "label_1": "neutral", "label_2": "positive"}.get(
        normalized, normalized
    )


class SentimentProvider:
    """Loads a Hugging Face sentiment-analysis model and scores text."""

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._model = None
        self._tokenizer = None

    @property
    def model_name(self) -> str:
        return self._settings.SENTIMENT_MODEL

    def _load(self):
        if self._model is not None:
            return self._model, self._tokenizer

        if not self.model_name:
            raise ModelUnavailableError("SENTIMENT_MODEL is not configured.")

        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            model.eval()
        except Exception as exc:
            raise ModelUnavailableError(
                f"Failed to load sentiment model '{self.model_name}': {exc}"
            ) from exc

        self._model, self._tokenizer = model, tokenizer
        return self._model, self._tokenizer

    @torch.no_grad()
    def predict(self, text: str) -> SentimentPrediction:
        model, tokenizer = self._load()

        encoded = tokenizer(text, truncation=True, max_length=MAX_SEQ_LEN, return_tensors="pt")
        logits = model(**encoded).logits[0]
        probabilities = torch.softmax(logits, dim=0)

        best_index = int(torch.argmax(probabilities))
        raw_label = model.config.id2label[best_index]
        return SentimentPrediction(
            label=_normalize_label(raw_label), confidence=float(probabilities[best_index])
        )


_provider: SentimentProvider | None = None


def get_sentiment_provider() -> SentimentProvider:
    global _provider
    if _provider is None:
        _provider = SentimentProvider()
    return _provider

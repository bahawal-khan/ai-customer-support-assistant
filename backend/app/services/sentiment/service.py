"""Phase 12 sentiment analysis service.

docs/backend/BACKEND_SPEC.md: "SentimentService: Uses a clean provider
interface." Thin orchestration wrapper around SentimentProvider, mirroring
LLMService's relationship to GroqProvider (app/services/llm/service.py):
this module owns no model-loading logic itself.
"""

from __future__ import annotations

from app.core.errors import ValidationAppError
from app.providers.sentiment_provider import (
    SentimentPrediction,
    SentimentProvider,
    get_sentiment_provider,
)

__all__ = ["SentimentService", "SentimentPrediction", "get_sentiment_service"]


class SentimentService:
    def __init__(self, provider: SentimentProvider | None = None):
        self._provider = provider or get_sentiment_provider()

    def analyze_sentiment(self, text: str) -> SentimentPrediction:
        if not text or not text.strip():
            raise ValidationAppError("Complaint text must be a non-empty string.")
        return self._provider.predict(text)


_service: SentimentService | None = None


def get_sentiment_service() -> SentimentService:
    global _service
    if _service is None:
        _service = SentimentService()
    return _service

"""Phase 12 intent classification service.

Wraps the Phase 05 production DistilBERT artifact (ml/distilbert/predict.py)
behind the IntentService boundary named in docs/backend/BACKEND_SPEC.md
("IntentService: Loads selected model artifact and predicts intent."). Does
not retrain or reimplement the classifier -- `IntentClassifier` already
loads the artifact selected by Phase 06 evaluation (LATEST_VERSION points at
"v2", ml/evaluation/artifacts/comparison.json) -- this module only adds the
FastAPI-facing error translation required by docs/ml/ML_INFERENCE_SPEC.md
("inference errors must be controlled").

`ml/` is a sibling of `backend/`, not an installed package, so it is added to
`sys.path` the same way backend/tests/conftest.py and backend/alembic/env.py
already add `backend/` to sys.path.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.distilbert.predict import (  # noqa: E402
    IntentClassifier,
    IntentPrediction,
    InvalidComplaintTextError,
)

from app.core.errors import ModelUnavailableError, ValidationAppError  # noqa: E402

__all__ = ["IntentService", "IntentPrediction", "get_intent_service"]


class IntentService:
    """Loads the production DistilBERT artifact once and classifies complaint intent."""

    def __init__(self, classifier: IntentClassifier | None = None):
        self._classifier = classifier

    def _get_classifier(self) -> IntentClassifier:
        if self._classifier is not None:
            return self._classifier
        try:
            self._classifier = IntentClassifier()
        except FileNotFoundError as exc:
            raise ModelUnavailableError(
                "No trained intent classification model is available."
            ) from exc
        return self._classifier

    def predict_intent(self, text: str) -> IntentPrediction:
        """Classify `text`. Raises ValidationAppError or ModelUnavailableError, never raw."""
        classifier = self._get_classifier()
        try:
            return classifier.predict_intent(text)
        except InvalidComplaintTextError as exc:
            raise ValidationAppError(str(exc)) from exc
        except Exception as exc:
            raise ModelUnavailableError("Intent classification failed.") from exc


_service: IntentService | None = None


def get_intent_service() -> IntentService:
    global _service
    if _service is None:
        _service = IntentService()
    return _service

"""DistilBERT inference.

Implements the ``predict_intent`` contract from ML_INFERENCE_SPEC.md: label,
confidence, top_k, model_name, model_version. Never trains; it only loads a
previously saved artifact and scores it. Model weights are set to eval mode
at load time, so dropout is disabled and predictions are deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from ml.distilbert.artifacts import load_artifact
from ml.distilbert.config import ARTIFACTS_DIR, MODEL_NAME, TOP_K


class InvalidComplaintTextError(ValueError):
    """Raised when input text fails validation for inference."""


@dataclass(frozen=True)
class IntentPrediction:
    label: str
    confidence: float
    top_k: list[dict[str, Any]]
    model_name: str
    model_version: str


class IntentClassifier:
    """Loads a versioned DistilBERT artifact once and serves deterministic predictions."""

    def __init__(self, version: str | None = None, artifacts_dir: Path = ARTIFACTS_DIR):
        artifact = load_artifact(version, artifacts_dir)
        self._version = artifact["version"]
        self._model = artifact["model"]
        self._model.eval()
        self._tokenizer = artifact["tokenizer"]
        label_mapping: dict[str, int] = artifact["label_mapping"]
        self._label_names = sorted(label_mapping, key=label_mapping.get)
        self._max_seq_len = artifact["config"]["max_seq_len"]

    @torch.no_grad()
    def predict_intent(self, text: str, top_k: int = TOP_K) -> IntentPrediction:
        """Classify ``text`` and return its top-1 label plus a ranked top_k list."""
        if not isinstance(text, str) or not text.strip():
            raise InvalidComplaintTextError("Complaint text must be a non-empty string.")

        encoded = self._tokenizer(
            text, truncation=True, max_length=self._max_seq_len, return_tensors="pt"
        )
        logits = self._model(**encoded).logits[0]
        probabilities = torch.softmax(logits, dim=0)

        ranked = torch.argsort(probabilities, descending=True)[:top_k]
        top_k_results = [
            {"label": self._label_names[i], "confidence": float(probabilities[i])} for i in ranked
        ]

        best_index = int(ranked[0])
        return IntentPrediction(
            label=self._label_names[best_index],
            confidence=float(probabilities[best_index]),
            top_k=top_k_results,
            model_name=MODEL_NAME,
            model_version=self._version,
        )


_default_classifier: IntentClassifier | None = None


def predict_intent(text: str, top_k: int = TOP_K) -> IntentPrediction:
    """Module-level convenience wrapper that loads the default classifier once per process."""
    global _default_classifier
    if _default_classifier is None:
        _default_classifier = IntentClassifier()
    return _default_classifier.predict_intent(text, top_k=top_k)

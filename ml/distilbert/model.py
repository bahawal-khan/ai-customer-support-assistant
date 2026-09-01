"""Pretrained DistilBERT loading for intent classification.

Pipeline (ML_TRAINING_SPEC.md): text -> Hugging Face tokenizer -> DistilBERT ->
classification head -> intent. The encoder starts from the pretrained
``distilbert-base-uncased`` checkpoint and is fine-tuned; it is never trained
from scratch.
"""

from __future__ import annotations

from typing import Any

from transformers import AutoModelForSequenceClassification, AutoTokenizer

from ml.distilbert.config import MODEL_CONFIG, PRETRAINED_CHECKPOINT


def load_tokenizer(checkpoint: str = PRETRAINED_CHECKPOINT) -> Any:
    """Load the Hugging Face tokenizer paired with ``checkpoint``."""
    return AutoTokenizer.from_pretrained(checkpoint)


def build_model(
    num_classes: int,
    checkpoint: str = PRETRAINED_CHECKPOINT,
    seq_classif_dropout: float = MODEL_CONFIG["seq_classif_dropout"],  # type: ignore[assignment]
) -> Any:
    """Load pretrained DistilBERT with a fresh ``num_classes``-way classification head."""
    return AutoModelForSequenceClassification.from_pretrained(
        checkpoint,
        num_labels=num_classes,
        seq_classif_dropout=seq_classif_dropout,
    )

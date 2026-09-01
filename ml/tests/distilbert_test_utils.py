"""Tiny, fully offline DistilBERT tokenizer/model builders used only by tests.

Downloading the real ``distilbert-base-uncased`` checkpoint for every unit test
run would be slow and require network access. These helpers build a randomly
initialized DistilBERT of the same architecture family from an in-memory
WordPiece vocabulary, so tests can exercise the real tokenizer/model API
surface without a network call.
"""

from __future__ import annotations

from transformers import DistilBertConfig, DistilBertForSequenceClassification, DistilBertTokenizer

_SPECIAL_TOKENS = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]


def build_tiny_tokenizer(vocab_words: list[str]) -> DistilBertTokenizer:
    """Build a ``DistilBertTokenizer`` from a small in-memory vocabulary.

    Passing ``vocab`` (a dict) directly is required here: this transformers
    version's tokenizer constructor only loads from a ``vocab_file`` path via
    the ``from_pretrained`` classmethod, not when instantiated directly.
    """
    words = list(dict.fromkeys(_SPECIAL_TOKENS + vocab_words))
    vocab = {token: index for index, token in enumerate(words)}
    return DistilBertTokenizer(vocab=vocab)


def build_tiny_model(vocab_size: int, num_classes: int) -> DistilBertForSequenceClassification:
    """Build a randomly initialized, architecturally valid tiny DistilBERT."""
    config = DistilBertConfig(
        vocab_size=vocab_size,
        dim=16,
        hidden_dim=32,
        n_layers=1,
        n_heads=2,
        max_position_embeddings=64,
        num_labels=num_classes,
    )
    return DistilBertForSequenceClassification(config)

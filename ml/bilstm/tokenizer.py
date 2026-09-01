"""Word-level tokenizer and vocabulary for the BiLSTM classifier.

The vocabulary must only ever be built from the training split; building it on
validation/test text would leak those vocabularies into the model, mirroring
the TF-IDF leakage protection in ``ml/baseline/features.py``.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Sequence

from ml.bilstm.config import MAX_SEQ_LEN, PAD_INDEX, PAD_TOKEN, UNK_INDEX, UNK_TOKEN, VOCAB_CONFIG

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def tokenize(text: str) -> list[str]:
    """Lowercase word tokenizer that keeps simple contractions (e.g. ``can't``) intact."""
    return _TOKEN_PATTERN.findall(text.lower())


class Vocabulary:
    """A reproducible token-to-id mapping with ``<pad>``/``<unk>`` reserved at indices 0/1."""

    def __init__(self, token_to_id: dict[str, int]):
        self._token_to_id = token_to_id

    @property
    def token_to_id(self) -> dict[str, int]:
        return dict(self._token_to_id)

    def __len__(self) -> int:
        return len(self._token_to_id)

    def encode(self, text: str, max_seq_len: int = MAX_SEQ_LEN) -> list[int]:
        """Tokenize ``text`` and map it to a truncated (not padded) list of token ids."""
        tokens = tokenize(text)[:max_seq_len]
        unk_id = self._token_to_id[UNK_TOKEN]
        ids = [self._token_to_id.get(token, unk_id) for token in tokens]
        # An empty token list (e.g. text with no alphanumeric characters) would produce a
        # zero-length sequence; encode it as a single <unk> so every example has length >= 1.
        return ids or [unk_id]

    def to_dict(self) -> dict[str, int]:
        return self.token_to_id

    @classmethod
    def from_dict(cls, token_to_id: dict[str, int]) -> "Vocabulary":
        return cls(dict(token_to_id))


def build_vocabulary(
    train_texts: Sequence[str],
    max_vocab_size: int = VOCAB_CONFIG["max_vocab_size"],  # type: ignore[assignment]
    min_token_freq: int = VOCAB_CONFIG["min_token_freq"],  # type: ignore[assignment]
) -> Vocabulary:
    """Fit a vocabulary on training text only, ranked by frequency then alphabetically."""
    counts = Counter()
    for text in train_texts:
        counts.update(tokenize(text))

    eligible = [token for token, freq in counts.items() if freq >= min_token_freq]
    eligible.sort(key=lambda token: (-counts[token], token))

    budget = max(max_vocab_size - 2, 0)  # reserve slots 0/1 for <pad>/<unk>
    kept = eligible[:budget]

    token_to_id = {PAD_TOKEN: PAD_INDEX, UNK_TOKEN: UNK_INDEX}
    for offset, token in enumerate(kept):
        token_to_id[token] = offset + 2

    return Vocabulary(token_to_id)

"""PyTorch dataset and batch collation for DistilBERT-tokenized intent text."""

from __future__ import annotations

from typing import Any, Sequence

import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset

from ml.distilbert.config import MAX_SEQ_LEN


class IntentTextDataset(Dataset):
    """Tokenizes (text, label) pairs into truncated, unpadded id/mask sequences.

    Padding happens per-batch in :func:`collate_batch` rather than up front, so
    each batch only pads to its own longest example.
    """

    def __init__(
        self,
        texts: Sequence[str],
        labels: Sequence[int],
        tokenizer: Any,
        max_seq_len: int = MAX_SEQ_LEN,
    ):
        if len(texts) != len(labels):
            raise ValueError("texts and labels must have the same length")
        encodings = tokenizer(list(texts), truncation=True, max_length=max_seq_len, padding=False)
        self._input_ids: list[list[int]] = encodings["input_ids"]
        self._attention_mask: list[list[int]] = encodings["attention_mask"]
        self._labels = list(labels)

    def __len__(self) -> int:
        return len(self._labels)

    def __getitem__(self, index: int) -> tuple[list[int], list[int], int]:
        return self._input_ids[index], self._attention_mask[index], self._labels[index]


def collate_batch(
    batch: Sequence[tuple[list[int], list[int], int]],
    pad_token_id: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Pad a batch of variable-length id/mask sequences.

    Returns ``(input_ids, attention_mask, labels)``.
    """
    ids, masks, labels = zip(*batch)
    id_tensors = [torch.tensor(seq, dtype=torch.int64) for seq in ids]
    mask_tensors = [torch.tensor(seq, dtype=torch.int64) for seq in masks]
    input_ids = pad_sequence(id_tensors, batch_first=True, padding_value=pad_token_id)
    attention_mask = pad_sequence(mask_tensors, batch_first=True, padding_value=0)
    label_tensor = torch.tensor(labels, dtype=torch.int64)
    return input_ids, attention_mask, label_tensor

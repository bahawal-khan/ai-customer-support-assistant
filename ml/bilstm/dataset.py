"""PyTorch dataset and batch collation for padded intent sequences."""

from __future__ import annotations

from typing import Sequence

import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset

from ml.bilstm.config import MAX_SEQ_LEN, PAD_INDEX
from ml.bilstm.tokenizer import Vocabulary


class IntentSequenceDataset(Dataset):
    """Encodes (text, label) pairs into truncated, unpadded token id sequences.

    Padding happens per-batch in :func:`collate_batch` rather than up front, so
    each batch only pads to its own longest example.
    """

    def __init__(
        self,
        texts: Sequence[str],
        labels: Sequence[int],
        vocabulary: Vocabulary,
        max_seq_len: int = MAX_SEQ_LEN,
    ):
        if len(texts) != len(labels):
            raise ValueError("texts and labels must have the same length")
        self._encoded = [vocabulary.encode(text, max_seq_len=max_seq_len) for text in texts]
        self._labels = list(labels)

    def __len__(self) -> int:
        return len(self._encoded)

    def __getitem__(self, index: int) -> tuple[list[int], int]:
        return self._encoded[index], self._labels[index]


def collate_batch(
    batch: Sequence[tuple[list[int], int]],
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Pad a batch of variable-length id sequences and return (input_ids, lengths, labels)."""
    sequences, labels = zip(*batch)
    lengths = torch.tensor([len(seq) for seq in sequences], dtype=torch.int64)
    tensors = [torch.tensor(seq, dtype=torch.int64) for seq in sequences]
    input_ids = pad_sequence(tensors, batch_first=True, padding_value=PAD_INDEX)
    label_tensor = torch.tensor(labels, dtype=torch.int64)
    return input_ids, lengths, label_tensor

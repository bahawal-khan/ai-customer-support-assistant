"""Embedding + bidirectional LSTM classifier for intent classification.

Pipeline (ML_TRAINING_SPEC.md): text -> tokenizer -> vocabulary -> padded
sequence -> embedding -> bidirectional LSTM -> dropout -> dense -> intent.
"""

from __future__ import annotations

import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence

from ml.bilstm.config import MODEL_CONFIG, PAD_INDEX


class BiLSTMClassifier(nn.Module):
    """Embeds token ids, encodes them with a BiLSTM, and classifies the final state."""

    def __init__(
        self,
        vocab_size: int,
        num_classes: int,
        embedding_dim: int = MODEL_CONFIG["embedding_dim"],  # type: ignore[assignment]
        hidden_dim: int = MODEL_CONFIG["hidden_dim"],  # type: ignore[assignment]
        num_lstm_layers: int = MODEL_CONFIG["num_lstm_layers"],  # type: ignore[assignment]
        dropout: float = MODEL_CONFIG["dropout"],  # type: ignore[assignment]
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=PAD_INDEX)
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_lstm_layers,
            batch_first=True,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, input_ids: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        """Return class logits of shape ``(batch_size, num_classes)``.

        ``lengths`` (true, unpadded sequence lengths) drive packing so the
        LSTM's final hidden state reflects each sequence's last real token
        rather than a padding position.
        """
        embedded = self.embedding(input_ids)
        packed = pack_padded_sequence(
            embedded, lengths.cpu(), batch_first=True, enforce_sorted=False
        )
        _, (h_n, _) = self.lstm(packed)

        # h_n: (num_layers * num_directions, batch, hidden_dim). The last layer's
        # forward/backward final states are the last two entries.
        forward_final = h_n[-2]
        backward_final = h_n[-1]
        sentence_repr = torch.cat([forward_final, backward_final], dim=1)

        return self.classifier(self.dropout(sentence_repr))


def build_model(vocab_size: int, num_classes: int) -> BiLSTMClassifier:
    """Construct an untrained BiLSTM classifier using the project's model configuration."""
    return BiLSTMClassifier(vocab_size=vocab_size, num_classes=num_classes, **MODEL_CONFIG)

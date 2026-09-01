"""Paths and hyperparameters for the Phase 04 Embedding + BiLSTM classifier."""

from __future__ import annotations

from pathlib import Path

from ml.data.config import SEED

REPO_ROOT = Path(__file__).resolve().parents[2]

BILSTM_DIR = REPO_ROOT / "ml" / "bilstm"
ARTIFACTS_DIR = BILSTM_DIR / "artifacts"
LATEST_VERSION_FILENAME = "LATEST_VERSION"

MODEL_NAME = "embedding_bilstm"

TOP_K = 3

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"
PAD_INDEX = 0
UNK_INDEX = 1

# Vocabulary: capped size, fit on the training split only.
VOCAB_CONFIG: dict[str, object] = {
    "max_vocab_size": 20000,
    "min_token_freq": 2,
}

MAX_SEQ_LEN = 32

# nn.Module constructor kwargs, persisted verbatim into each artifact's config.json.
MODEL_CONFIG: dict[str, object] = {
    "embedding_dim": 128,
    "hidden_dim": 128,
    "num_lstm_layers": 1,
    "dropout": 0.3,
}

TRAIN_CONFIG: dict[str, object] = {
    "batch_size": 64,
    "learning_rate": 1e-3,
    "weight_decay": 0.0,
    "max_epochs": 20,
    "early_stopping_patience": 3,
    "seed": SEED,
}

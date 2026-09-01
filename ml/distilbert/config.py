"""Paths and hyperparameters for the Phase 05 fine-tuned DistilBERT classifier."""

from __future__ import annotations

from pathlib import Path

from ml.data.config import SEED

REPO_ROOT = Path(__file__).resolve().parents[2]

DISTILBERT_DIR = REPO_ROOT / "ml" / "distilbert"
ARTIFACTS_DIR = DISTILBERT_DIR / "artifacts"
LATEST_VERSION_FILENAME = "LATEST_VERSION"

MODEL_NAME = "distilbert"
PRETRAINED_CHECKPOINT = "distilbert-base-uncased"

TOP_K = 3
MAX_SEQ_LEN = 64

# transformers constructor kwargs, persisted verbatim into each artifact's config.json.
MODEL_CONFIG: dict[str, object] = {
    "checkpoint": PRETRAINED_CHECKPOINT,
    "seq_classif_dropout": 0.1,
}

# Fast CPU sanity-check configuration: a small stratified subsample and a single
# epoch, used to verify the fine-tuning/evaluation pipeline end-to-end without
# paying for a full run.
SMOKE_TRAIN_CONFIG: dict[str, object] = {
    "batch_size": 16,
    "learning_rate": 5e-5,
    "weight_decay": 0.01,
    "max_epochs": 1,
    "early_stopping_patience": 1,
    "max_train_examples": 270,
    "max_eval_examples": 135,
    "seed": SEED,
}

# Full fine-tuning configuration, run over the complete Bitext split.
FULL_TRAIN_CONFIG: dict[str, object] = {
    "batch_size": 16,
    "learning_rate": 3e-5,
    "weight_decay": 0.01,
    "max_epochs": 5,
    "early_stopping_patience": 2,
    "max_train_examples": None,
    "max_eval_examples": None,
    "seed": SEED,
}

TRAIN_CONFIGS: dict[str, dict[str, object]] = {
    "smoke": SMOKE_TRAIN_CONFIG,
    "full": FULL_TRAIN_CONFIG,
}

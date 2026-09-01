"""Paths and hyperparameters for the Phase 03 TF-IDF + Logistic Regression baseline."""

from __future__ import annotations

from pathlib import Path

from ml.data.config import SEED

REPO_ROOT = Path(__file__).resolve().parents[2]

BASELINE_DIR = REPO_ROOT / "ml" / "baseline"
ARTIFACTS_DIR = BASELINE_DIR / "artifacts"
LATEST_VERSION_FILENAME = "LATEST_VERSION"

MODEL_NAME = "tfidf_logreg"

TOP_K = 3

# scikit-learn constructor kwargs, persisted verbatim into each artifact's config.json.
TFIDF_CONFIG: dict[str, object] = {
    "lowercase": True,
    "ngram_range": (1, 2),
    "min_df": 2,
    "max_df": 0.9,
    "sublinear_tf": True,
}

LOGREG_CONFIG: dict[str, object] = {
    "max_iter": 1000,
    "C": 1.0,
    "class_weight": "balanced",
    "random_state": SEED,
}

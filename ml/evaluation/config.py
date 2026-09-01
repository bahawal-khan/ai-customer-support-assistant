"""Paths and constants for the Phase 06 cross-model evaluation and selection."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

EVALUATION_DIR = REPO_ROOT / "ml" / "evaluation"
ARTIFACTS_DIR = EVALUATION_DIR / "artifacts"

COMPARISON_FILENAME = "comparison.json"
REPORT_FILENAME = "COMPARISON_REPORT.md"

# Registered candidates, in the order ML_TRAINING_SPEC.md introduces them.
CANDIDATE_MODEL_NAMES: list[str] = ["tfidf_logreg", "embedding_bilstm", "distilbert"]

# REQUIREMENTS.md: "Primary model-selection metrics: macro F1, weighted F1, accuracy,
# and inference latency/cost as secondary considerations."
PRIMARY_METRIC = "macro_f1"
SECONDARY_METRICS: list[str] = ["weighted_f1", "accuracy"]

# Two candidates are treated as tied on the primary metric (and therefore broken by
# latency) only if they land within this many macro-F1 points of each other. 0.002
# (0.2 points) is small enough that it never masks a real quality difference between
# these three architectures, while still tolerating noise from re-evaluation.
PRIMARY_METRIC_TIE_EPSILON = 0.002

# Number of leading predictions, per model, excluded from latency statistics to avoid
# counting one-time lazy-initialization cost (e.g. first-call framework warmup) as
# steady-state inference latency.
LATENCY_WARMUP_PREDICTIONS = 5

"""Logistic Regression classifier for the TF-IDF baseline."""

from __future__ import annotations

from sklearn.linear_model import LogisticRegression

from ml.baseline.config import LOGREG_CONFIG


def build_model() -> LogisticRegression:
    """Construct an unfit Logistic Regression classifier using the baseline configuration."""
    return LogisticRegression(**LOGREG_CONFIG)

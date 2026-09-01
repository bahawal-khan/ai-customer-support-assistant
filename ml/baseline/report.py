"""Human-readable evaluation report for a trained baseline artifact."""

from __future__ import annotations

from typing import Any


def render_report(
    *,
    version: str,
    config: dict[str, Any],
    metrics_by_split: dict[str, dict[str, Any]],
) -> str:
    """Render a Markdown summary of one baseline training run."""
    lines = [
        f"# TF-IDF + Logistic Regression Baseline — {version}",
        "",
        "## Configuration",
        f"- TF-IDF: {config['tfidf']}",
        f"- Logistic Regression: {config['logreg']}",
        "",
    ]
    for split_name, metrics in metrics_by_split.items():
        lines += [
            f"## {split_name.capitalize()} metrics",
            f"- Accuracy: {metrics['accuracy']:.4f}",
            f"- Macro precision: {metrics['macro_precision']:.4f}",
            f"- Macro recall: {metrics['macro_recall']:.4f}",
            f"- Macro F1: {metrics['macro_f1']:.4f}",
            f"- Weighted F1: {metrics['weighted_f1']:.4f}",
            "",
        ]
    return "\n".join(lines)

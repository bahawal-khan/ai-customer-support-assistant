"""Human-readable evaluation report for a trained DistilBERT artifact."""

from __future__ import annotations

from typing import Any


def render_report(
    *,
    version: str,
    config: dict[str, Any],
    manifest: dict[str, Any],
    metrics_by_split: dict[str, dict[str, Any]],
) -> str:
    """Render a Markdown summary of one DistilBERT fine-tuning run."""
    lines = [
        f"# Fine-tuned DistilBERT — {version}",
        "",
        "## Configuration",
        f"- Mode: {manifest['mode']}",
        f"- Checkpoint: {config['model']['checkpoint']}",
        f"- Max sequence length: {config['max_seq_len']}",
        f"- Model: {config['model']}",
        f"- Training: {config['train']}",
        "",
        "## Training summary",
        f"- Epochs run: {manifest['epochs_run']}",
        f"- Best epoch: {manifest['best_epoch']}",
        f"- Stopped early: {manifest['stopped_early']}",
        f"- Row counts used: {manifest['row_counts']}",
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

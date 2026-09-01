"""Human-readable Phase 06 model comparison and selection report."""

from __future__ import annotations

from typing import Any


def _confused_pairs(metrics: dict[str, Any], top_n: int = 5) -> list[tuple[str, str, int]]:
    """Return the top off-diagonal (true_label, predicted_label, count) confusions."""
    labels = metrics["confusion_matrix_labels"]
    matrix = metrics["confusion_matrix"]
    pairs = [
        (labels[i], labels[j], matrix[i][j])
        for i in range(len(labels))
        for j in range(len(labels))
        if i != j and matrix[i][j] > 0
    ]
    pairs.sort(key=lambda p: p[2], reverse=True)
    return pairs[:top_n]


def render_report(comparison: dict[str, Any]) -> str:
    """Render the Phase 06 Markdown comparison + selection report."""
    lines = [
        "# Phase 06 — Model Evaluation & Selection",
        "",
        f"Generated: {comparison['generated_at']}",
        f"Seed: {comparison['seed']}",
        f"Held-out test set: `{comparison['test_set']['path']}` "
        f"({comparison['test_set']['n_examples']} examples, used identically by every model)",
        "",
        "## Reproducibility & leakage check",
        f"- {comparison['reproducibility']['notes']}",
        "",
        "## Comparison",
        "",
        "| Model | Version | Accuracy | Macro P | Macro R | Macro F1 | Weighted F1 "
        "| Size | Latency (mean / p95) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for model_name, result in comparison["models"].items():
        m = result["metrics"]
        size_mb = result["model_size_bytes"] / (1024 * 1024)
        latency = result["latency_ms"]
        lines.append(
            f"| {model_name} | {result['version']} | {m['accuracy']:.4f} "
            f"| {m['macro_precision']:.4f} | {m['macro_recall']:.4f} | {m['macro_f1']:.4f} "
            f"| {m['weighted_f1']:.4f} | {size_mb:.2f} MB "
            f"| {latency['mean_ms']:.2f} ms / {latency['p95_ms']:.2f} ms |"
        )

    lines += ["", "## Per-model detail", ""]
    for model_name, result in comparison["models"].items():
        m = result["metrics"]
        latency = result["latency_ms"]
        lines += [
            f"### {model_name} ({result['version']})",
            f"- Test examples: {result['n_test_examples']}",
            f"- Accuracy: {m['accuracy']:.4f}",
            f"- Macro precision / recall / F1: {m['macro_precision']:.4f} / "
            f"{m['macro_recall']:.4f} / {m['macro_f1']:.4f}",
            f"- Weighted precision / recall / F1: {m['weighted_precision']:.4f} / "
            f"{m['weighted_recall']:.4f} / {m['weighted_f1']:.4f}",
            f"- Model size on disk: {result['model_size_bytes'] / (1024 * 1024):.2f} MB",
            f"- Inference latency (n={latency['n_samples']}, warmup excluded): "
            f"mean={latency['mean_ms']:.2f} ms, median={latency['median_ms']:.2f} ms, "
            f"p95={latency['p95_ms']:.2f} ms, min={latency['min_ms']:.2f} ms, "
            f"max={latency['max_ms']:.2f} ms",
        ]
        confused = _confused_pairs(m)
        if confused:
            lines.append("- Most confused label pairs (true → predicted: count):")
            lines += [f"  - {t} → {p}: {c}" for t, p, c in confused]
        else:
            lines.append("- No misclassifications on the test set.")
        lines.append("")

    selection = comparison["selection"]
    lines += [
        "## Production model selection",
        "",
        f"**Selected: `{selection['selected_model']}` "
        f"(version `{selection['selected_version']}`)**",
        "",
        f"- Primary metric: {selection['primary_metric']}",
        f"- Secondary metrics considered: {', '.join(selection['secondary_metrics'])}",
        f"- Tie epsilon on primary metric: {selection['tie_epsilon']}",
        f"- Rationale: {selection['rationale']}",
        f"- Full ranking: {selection['ranking']}",
        "",
    ]

    return "\n".join(lines)

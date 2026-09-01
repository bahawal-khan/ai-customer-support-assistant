"""Phase 06 cross-model evaluation, comparison, and production model selection.

Loads each already-trained model artifact (TF-IDF+LogReg, BiLSTM, DistilBERT) and
scores it against the same held-out ``data/processed/test.csv`` split via each
model's existing ``predict_intent`` inference contract (ML_INFERENCE_SPEC.md).
This module never trains or refits a model; it only loads and scores.
"""

from __future__ import annotations

import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import pandas as pd

from ml.baseline.metrics import compute_metrics
from ml.evaluation.config import (
    LATENCY_WARMUP_PREDICTIONS,
    PRIMARY_METRIC,
    PRIMARY_METRIC_TIE_EPSILON,
    SECONDARY_METRICS,
)


class IntentClassifierLike(Protocol):
    """Structural contract shared by the baseline/BiLSTM/DistilBERT classifiers."""

    def predict_intent(self, text: str) -> Any: ...  # noqa: D102


def artifact_size_bytes(artifact_dir: Path) -> int:
    """Return the total on-disk size of a versioned artifact directory, in bytes."""
    if not artifact_dir.exists():
        raise FileNotFoundError(f"Artifact directory does not exist: {artifact_dir}")
    return sum(path.stat().st_size for path in artifact_dir.rglob("*") if path.is_file())


def _latency_stats(latencies_ms: list[float], warmup: int) -> dict[str, float]:
    steady_state = latencies_ms[warmup:] if len(latencies_ms) > warmup else latencies_ms
    sorted_latencies = sorted(steady_state)
    p95_index = min(len(sorted_latencies) - 1, int(round(0.95 * (len(sorted_latencies) - 1))))
    return {
        "mean_ms": statistics.fmean(sorted_latencies),
        "median_ms": statistics.median(sorted_latencies),
        "p95_ms": sorted_latencies[p95_index],
        "min_ms": sorted_latencies[0],
        "max_ms": sorted_latencies[-1],
        "n_samples": len(sorted_latencies),
    }


def evaluate_model(
    *,
    model_name: str,
    version: str,
    classifier: IntentClassifierLike,
    label_names: list[str],
    test_df: pd.DataFrame,
    artifact_dir: Path,
    latency_warmup: int = LATENCY_WARMUP_PREDICTIONS,
) -> dict[str, Any]:
    """Score one already-trained classifier against ``test_df`` and profile it.

    Runs every test row through the model's real ``predict_intent`` inference path
    (the same path production traffic uses), so both correctness metrics and
    latency reflect actual served behavior rather than a batched training-time
    evaluation loop.
    """
    label_to_index = {label: index for index, label in enumerate(label_names)}

    y_true: list[int] = []
    y_pred: list[int] = []
    latencies_ms: list[float] = []

    for text, true_intent in zip(test_df["instruction"], test_df["intent"]):
        start = time.perf_counter()
        prediction = classifier.predict_intent(text)
        latencies_ms.append((time.perf_counter() - start) * 1000)

        y_true.append(label_to_index[true_intent])
        y_pred.append(label_to_index[prediction.label])

    metrics = compute_metrics(y_true, y_pred, label_names)

    return {
        "model_name": model_name,
        "version": version,
        "n_test_examples": len(test_df),
        "metrics": metrics,
        "model_size_bytes": artifact_size_bytes(artifact_dir),
        "latency_ms": _latency_stats(latencies_ms, warmup=latency_warmup),
    }


def select_production_model(
    results: list[dict[str, Any]],
    primary_metric: str = PRIMARY_METRIC,
    tie_epsilon: float = PRIMARY_METRIC_TIE_EPSILON,
) -> dict[str, Any]:
    """Choose the production model per REQUIREMENTS.md's documented criteria.

    Primary metrics (macro F1, weighted F1, accuracy) govern the decision. Latency
    only acts as a secondary tie-break, and only when candidates are within
    ``tie_epsilon`` of each other on ``primary_metric`` -- it never overrides a
    real difference in classification quality.
    """
    if not results:
        raise ValueError("Cannot select a production model from an empty result set.")

    ranked = sorted(results, key=lambda r: r["metrics"][primary_metric], reverse=True)
    best_score = ranked[0]["metrics"][primary_metric]
    contenders = [r for r in ranked if best_score - r["metrics"][primary_metric] <= tie_epsilon]

    if len(contenders) > 1:
        selected = min(contenders, key=lambda r: r["latency_ms"]["mean_ms"])
        rationale = (
            f"{len(contenders)} models tied on {primary_metric} within {tie_epsilon}: "
            f"{[c['model_name'] for c in contenders]}. Selected '{selected['model_name']}' "
            "for the lowest mean inference latency (secondary criterion)."
        )
    else:
        selected = ranked[0]
        rationale = (
            f"'{selected['model_name']}' has the highest {primary_metric} "
            f"({selected['metrics'][primary_metric]:.4f}) among all candidates; "
            "no tie-break was needed."
        )

    return {
        "selected_model": selected["model_name"],
        "selected_version": selected["version"],
        "primary_metric": primary_metric,
        "secondary_metrics": SECONDARY_METRICS,
        "tie_epsilon": tie_epsilon,
        "rationale": rationale,
        "ranking": [
            {"model_name": r["model_name"], primary_metric: r["metrics"][primary_metric]}
            for r in ranked
        ],
    }


def build_comparison(
    results: list[dict[str, Any]],
    *,
    test_csv_path: Path,
    seed: int,
) -> dict[str, Any]:
    """Assemble the full Phase 06 comparison payload: per-model results + selection."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "test_set": {
            "path": str(test_csv_path),
            "n_examples": results[0]["n_test_examples"] if results else 0,
        },
        "reproducibility": {
            "same_split_used_by_all_models": True,
            "checkpoint_selection_used_only_validation_metrics": True,
            "notes": (
                "All three training runs (ml/baseline/train.py, ml/bilstm/train.py, "
                "ml/distilbert/train.py) share the same seed=42 data/processed split "
                "and select their final model/checkpoint using only validation macro-F1. "
                "The test split is scored exactly once, after the model is frozen, and "
                "only for reporting -- never for training or checkpoint selection."
            ),
        },
        "models": {r["model_name"]: r for r in results},
        "selection": select_production_model(results),
    }

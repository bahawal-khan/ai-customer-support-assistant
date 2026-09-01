"""Evaluation metrics for intent classification.

Reports accuracy, macro/weighted precision-recall-F1, per-class metrics, and
a confusion matrix, per ML_TRAINING_SPEC.md's evaluation requirements.
"""

from __future__ import annotations

from typing import Any, Sequence

from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support


def compute_metrics(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    label_names: list[str],
) -> dict[str, Any]:
    """Compute the full Phase 03 evaluation report for one split's predictions."""
    labels = list(range(len(label_names)))

    accuracy = float(accuracy_score(y_true, y_pred))

    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="weighted", zero_division=0
    )
    class_p, class_r, class_f1, class_support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average=None, zero_division=0
    )

    per_class = {
        label_names[i]: {
            "precision": float(class_p[i]),
            "recall": float(class_r[i]),
            "f1": float(class_f1[i]),
            "support": int(class_support[i]),
        }
        for i in labels
    }

    matrix = confusion_matrix(y_true, y_pred, labels=labels)

    return {
        "accuracy": accuracy,
        "macro_precision": float(macro_p),
        "macro_recall": float(macro_r),
        "macro_f1": float(macro_f1),
        "weighted_precision": float(weighted_p),
        "weighted_recall": float(weighted_r),
        "weighted_f1": float(weighted_f1),
        "per_class": per_class,
        "confusion_matrix": matrix.tolist(),
        "confusion_matrix_labels": label_names,
    }

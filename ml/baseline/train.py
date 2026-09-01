"""Train and evaluate the TF-IDF + Logistic Regression intent classification baseline.

TF-IDF is fit strictly on the training split, then reused (never refit) to
transform validation and test text, preventing vocabulary leakage.

Run directly with: python -m ml.baseline.train
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ml.baseline.artifacts import next_version, save_artifact
from ml.baseline.config import ARTIFACTS_DIR, LOGREG_CONFIG, MODEL_NAME, TFIDF_CONFIG, TOP_K
from ml.baseline.features import fit_vectorizer
from ml.baseline.metrics import compute_metrics
from ml.baseline.model import build_model
from ml.baseline.report import render_report
from ml.data.config import PROCESSED_DIR, SEED
from ml.data.labels import build_label_mapping


def _load_split(processed_dir: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(processed_dir / f"{name}.csv")


def _encode_labels(df: pd.DataFrame, label_mapping: dict[str, int]) -> list[int]:
    unknown = set(df["intent"]) - set(label_mapping)
    if unknown:
        raise ValueError(f"Unknown intent label(s) not in label mapping: {sorted(unknown)}")
    return df["intent"].map(label_mapping).tolist()


def run_training(
    processed_dir: Path = PROCESSED_DIR,
    artifacts_dir: Path = ARTIFACTS_DIR,
    seed: int = SEED,
) -> dict[str, Any]:
    """Train the TF-IDF + Logistic Regression baseline and persist a versioned artifact.

    Returns the trained version id, its artifact directory, and validation/test metrics.
    """
    train_df = _load_split(processed_dir, "train")
    validation_df = _load_split(processed_dir, "validation")
    test_df = _load_split(processed_dir, "test")

    label_mapping = build_label_mapping(train_df)
    label_names = sorted(label_mapping, key=label_mapping.get)

    vectorizer = fit_vectorizer(train_df["instruction"])

    model = build_model()
    x_train = vectorizer.transform(train_df["instruction"])
    y_train = _encode_labels(train_df, label_mapping)
    model.fit(x_train, y_train)

    metrics_by_split: dict[str, dict[str, Any]] = {}
    for split_name, split_df in (("validation", validation_df), ("test", test_df)):
        x_split = vectorizer.transform(split_df["instruction"])
        y_true = _encode_labels(split_df, label_mapping)
        y_pred = model.predict(x_split)
        metrics_by_split[split_name] = compute_metrics(y_true, y_pred, label_names)

    config = {
        "model_name": MODEL_NAME,
        "seed": seed,
        "top_k": TOP_K,
        "tfidf": TFIDF_CONFIG,
        "logreg": LOGREG_CONFIG,
    }

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_name": MODEL_NAME,
        "seed": seed,
        "data_sources": {
            "train": str(processed_dir / "train.csv"),
            "validation": str(processed_dir / "validation.csv"),
            "test": str(processed_dir / "test.csv"),
        },
        "row_counts": {
            "train": len(train_df),
            "validation": len(validation_df),
            "test": len(test_df),
        },
        "num_classes": len(label_mapping),
    }

    version = next_version(artifacts_dir)
    version_dir = save_artifact(
        version=version,
        model=model,
        vectorizer=vectorizer,
        label_mapping=label_mapping,
        config=config,
        manifest=manifest,
        metrics=metrics_by_split,
        artifacts_dir=artifacts_dir,
    )

    report = render_report(version=version, config=config, metrics_by_split=metrics_by_split)
    (version_dir / "REPORT.md").write_text(report, encoding="utf-8")

    return {"version": version, "artifact_dir": version_dir, "metrics": metrics_by_split}


def _print_summary(result: dict[str, Any]) -> None:
    print(f"Trained baseline version: {result['version']}")
    print(f"Artifact directory: {result['artifact_dir']}")
    for split_name, metrics in result["metrics"].items():
        print(
            f"  {split_name}: accuracy={metrics['accuracy']:.4f} "
            f"macro_f1={metrics['macro_f1']:.4f} weighted_f1={metrics['weighted_f1']:.4f}"
        )


if __name__ == "__main__":
    _print_summary(run_training())

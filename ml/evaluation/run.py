"""Phase 06 orchestration: evaluate all trained models against the same held-out
test split and select the production model.

Loads each model's already-trained ``LATEST_VERSION`` artifact and scores it via
its real inference path (ML_INFERENCE_SPEC.md's ``predict_intent`` contract).
This script never trains, refits, or fine-tunes a model.

Run directly with: python -m ml.evaluation.run
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from ml.baseline.artifacts import load_artifact as load_baseline_artifact
from ml.baseline.config import ARTIFACTS_DIR as BASELINE_ARTIFACTS_DIR
from ml.baseline.predict import IntentClassifier as BaselineClassifier
from ml.bilstm.artifacts import load_artifact as load_bilstm_artifact
from ml.bilstm.config import ARTIFACTS_DIR as BILSTM_ARTIFACTS_DIR
from ml.bilstm.predict import IntentClassifier as BiLSTMClassifier
from ml.data.config import PROCESSED_DIR, SEED
from ml.distilbert.artifacts import load_artifact as load_distilbert_artifact
from ml.distilbert.config import ARTIFACTS_DIR as DISTILBERT_ARTIFACTS_DIR
from ml.distilbert.predict import IntentClassifier as DistilBertClassifier
from ml.evaluation.compare import build_comparison, evaluate_model
from ml.evaluation.config import ARTIFACTS_DIR, COMPARISON_FILENAME, REPORT_FILENAME
from ml.evaluation.report import render_report

_ModelSpec = tuple[str, Callable[..., Any], Path, Callable[..., dict[str, Any]]]

_MODEL_SPECS: list[_ModelSpec] = [
    ("tfidf_logreg", BaselineClassifier, BASELINE_ARTIFACTS_DIR, load_baseline_artifact),
    ("embedding_bilstm", BiLSTMClassifier, BILSTM_ARTIFACTS_DIR, load_bilstm_artifact),
    ("distilbert", DistilBertClassifier, DISTILBERT_ARTIFACTS_DIR, load_distilbert_artifact),
]


def run_evaluation(
    processed_dir: Path = PROCESSED_DIR,
    output_dir: Path = ARTIFACTS_DIR,
    seed: int = SEED,
    model_specs: list[_ModelSpec] = _MODEL_SPECS,
) -> dict[str, Any]:
    """Evaluate every model's latest trained artifact against the same test split."""
    test_csv_path = processed_dir / "test.csv"
    test_df = pd.read_csv(test_csv_path)

    results = []
    for model_name, classifier_cls, artifacts_dir, load_artifact_fn in model_specs:
        artifact = load_artifact_fn(None, artifacts_dir)
        version = artifact["version"]
        label_mapping: dict[str, int] = artifact["label_mapping"]
        label_names = sorted(label_mapping, key=label_mapping.get)
        classifier = classifier_cls(version=version, artifacts_dir=artifacts_dir)

        result = evaluate_model(
            model_name=model_name,
            version=version,
            classifier=classifier,
            label_names=label_names,
            test_df=test_df,
            artifact_dir=artifacts_dir / version,
        )
        print(
            f"[evaluation] {model_name} {version}: "
            f"macro_f1={result['metrics']['macro_f1']:.4f} "
            f"latency_mean_ms={result['latency_ms']['mean_ms']:.2f}",
            flush=True,
        )
        results.append(result)

    comparison = build_comparison(results, test_csv_path=test_csv_path, seed=seed)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / COMPARISON_FILENAME).write_text(
        json.dumps(comparison, indent=2), encoding="utf-8"
    )
    (output_dir / REPORT_FILENAME).write_text(render_report(comparison), encoding="utf-8")

    return comparison


if __name__ == "__main__":
    _comparison = run_evaluation()
    _selection = _comparison["selection"]
    print(
        f"Selected production model: {_selection['selected_model']} "
        f"({_selection['selected_version']})"
    )

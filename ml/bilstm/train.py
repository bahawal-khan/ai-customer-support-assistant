"""Train and evaluate the Embedding + BiLSTM intent classification model.

The vocabulary is built strictly from the training split, then reused (never
rebuilt) to encode validation/test text, preventing vocabulary leakage.

Run directly with: python -m ml.bilstm.train
"""

from __future__ import annotations

import copy
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader

from ml.baseline.metrics import compute_metrics
from ml.bilstm.artifacts import next_version, save_artifact
from ml.bilstm.config import (
    ARTIFACTS_DIR,
    MAX_SEQ_LEN,
    MODEL_CONFIG,
    MODEL_NAME,
    TOP_K,
    TRAIN_CONFIG,
    VOCAB_CONFIG,
)
from ml.bilstm.dataset import IntentSequenceDataset, collate_batch
from ml.bilstm.model import build_model
from ml.bilstm.report import render_report
from ml.bilstm.tokenizer import Vocabulary, build_vocabulary
from ml.data.config import PROCESSED_DIR, SEED
from ml.data.labels import build_label_mapping


def _load_split(processed_dir: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(processed_dir / f"{name}.csv")


def _encode_labels(df: pd.DataFrame, label_mapping: dict[str, int]) -> list[int]:
    unknown = set(df["intent"]) - set(label_mapping)
    if unknown:
        raise ValueError(f"Unknown intent label(s) not in label mapping: {sorted(unknown)}")
    return df["intent"].map(label_mapping).tolist()


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _make_loader(
    df: pd.DataFrame,
    label_mapping: dict[str, int],
    vocabulary: Vocabulary,
    batch_size: int,
    shuffle: bool,
    seed: int,
) -> DataLoader:
    dataset = IntentSequenceDataset(
        texts=df["instruction"].tolist(),
        labels=_encode_labels(df, label_mapping),
        vocabulary=vocabulary,
        max_seq_len=MAX_SEQ_LEN,
    )
    generator = None
    if shuffle:
        generator = torch.Generator()
        generator.manual_seed(seed)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=collate_batch,
        generator=generator,
    )


def _run_training_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
) -> None:
    model.train()
    for input_ids, lengths, labels in loader:
        optimizer.zero_grad()
        logits = model(input_ids, lengths)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()


@torch.no_grad()
def _evaluate(model: nn.Module, loader: DataLoader, label_names: list[str]) -> dict[str, Any]:
    model.eval()
    all_true: list[int] = []
    all_pred: list[int] = []
    for input_ids, lengths, labels in loader:
        logits = model(input_ids, lengths)
        predictions = torch.argmax(logits, dim=1)
        all_true.extend(labels.tolist())
        all_pred.extend(predictions.tolist())
    return compute_metrics(all_true, all_pred, label_names)


def run_training(
    processed_dir: Path = PROCESSED_DIR,
    artifacts_dir: Path = ARTIFACTS_DIR,
    seed: int = SEED,
) -> dict[str, Any]:
    """Train the Embedding + BiLSTM classifier and persist a versioned artifact.

    Returns the trained version id, its artifact directory, and validation/test metrics.
    """
    _set_seed(seed)

    train_df = _load_split(processed_dir, "train")
    validation_df = _load_split(processed_dir, "validation")
    test_df = _load_split(processed_dir, "test")

    label_mapping = build_label_mapping(train_df)
    label_names = sorted(label_mapping, key=label_mapping.get)

    vocabulary = build_vocabulary(train_df["instruction"], **VOCAB_CONFIG)

    train_config = {**TRAIN_CONFIG, "seed": seed}
    batch_size = train_config["batch_size"]
    train_loader = _make_loader(
        train_df, label_mapping, vocabulary, batch_size, shuffle=True, seed=seed
    )
    validation_loader = _make_loader(
        validation_df, label_mapping, vocabulary, batch_size, shuffle=False, seed=seed
    )
    test_loader = _make_loader(
        test_df, label_mapping, vocabulary, batch_size, shuffle=False, seed=seed
    )

    model = build_model(vocab_size=len(vocabulary), num_classes=len(label_mapping))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=train_config["learning_rate"],
        weight_decay=train_config["weight_decay"],
    )

    best_macro_f1 = -1.0
    best_epoch = 0
    best_state: dict[str, Any] | None = None
    epochs_without_improvement = 0
    stopped_early = False
    epochs_run = 0

    for epoch in range(1, train_config["max_epochs"] + 1):
        epochs_run = epoch
        _run_training_epoch(model, train_loader, criterion, optimizer)
        validation_metrics = _evaluate(model, validation_loader, label_names)
        macro_f1 = validation_metrics["macro_f1"]

        if macro_f1 > best_macro_f1:
            best_macro_f1 = macro_f1
            best_epoch = epoch
            best_state = copy.deepcopy(model.state_dict())
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= train_config["early_stopping_patience"]:
                stopped_early = True
                break

    assert best_state is not None
    model.load_state_dict(best_state)

    metrics_by_split = {
        "validation": _evaluate(model, validation_loader, label_names),
        "test": _evaluate(model, test_loader, label_names),
    }

    config = {
        "model_name": MODEL_NAME,
        "seed": seed,
        "top_k": TOP_K,
        "vocab_size": len(vocabulary),
        "num_classes": len(label_mapping),
        "max_seq_len": MAX_SEQ_LEN,
        "model": MODEL_CONFIG,
        "train": train_config,
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
        "epochs_run": epochs_run,
        "best_epoch": best_epoch,
        "stopped_early": stopped_early,
        "best_validation_macro_f1": best_macro_f1,
    }

    version = next_version(artifacts_dir)
    version_dir = save_artifact(
        version=version,
        model=model,
        vocabulary=vocabulary,
        label_mapping=label_mapping,
        config=config,
        manifest=manifest,
        metrics=metrics_by_split,
        artifacts_dir=artifacts_dir,
    )

    report = render_report(
        version=version, config=config, manifest=manifest, metrics_by_split=metrics_by_split
    )
    (version_dir / "REPORT.md").write_text(report, encoding="utf-8")

    return {"version": version, "artifact_dir": version_dir, "metrics": metrics_by_split}


def _print_summary(result: dict[str, Any]) -> None:
    print(f"Trained BiLSTM version: {result['version']}")
    print(f"Artifact directory: {result['artifact_dir']}")
    for split_name, metrics in result["metrics"].items():
        print(
            f"  {split_name}: accuracy={metrics['accuracy']:.4f} "
            f"macro_f1={metrics['macro_f1']:.4f} weighted_f1={metrics['weighted_f1']:.4f}"
        )


if __name__ == "__main__":
    _print_summary(run_training())

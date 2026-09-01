"""Fine-tune and evaluate the pretrained DistilBERT intent classifier.

Two named configurations are supported (ML_TRAINING_SPEC.md / IMPLEMENTATION_PHASES.md
Phase 05): a fast CPU ``"smoke"`` sanity check over a small stratified subsample, and
a ``"full"`` fine-tuning run over the complete Bitext split. Both reuse the same
train/validation/test files and seed as the earlier baseline/BiLSTM phases.

Run directly with: python -m ml.distilbert.train [smoke|full]
"""

from __future__ import annotations

import copy
import random
import sys
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from ml.baseline.metrics import compute_metrics
from ml.data.config import PROCESSED_DIR, SEED
from ml.data.labels import build_label_mapping
from ml.distilbert.artifacts import next_version, save_artifact
from ml.distilbert.config import (
    ARTIFACTS_DIR,
    MAX_SEQ_LEN,
    MODEL_CONFIG,
    MODEL_NAME,
    PRETRAINED_CHECKPOINT,
    TOP_K,
    TRAIN_CONFIGS,
)
from ml.distilbert.dataset import IntentTextDataset, collate_batch
from ml.distilbert.model import build_model, load_tokenizer
from ml.distilbert.report import render_report


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


def _stratified_subsample(
    df: pd.DataFrame, max_examples: int | None, seed: int
) -> pd.DataFrame:
    """Cap ``df`` at ``max_examples`` rows while keeping per-intent coverage.

    Used by the smoke configuration so a tiny run still exercises every class.
    """
    if max_examples is None or len(df) <= max_examples:
        return df

    n_classes = df["intent"].nunique()
    per_class = max(1, max_examples // n_classes)
    # Iterating groups (rather than groupby(...).apply(...)) sidesteps pandas 3.x's
    # include_groups behavior change, which would otherwise silently drop the
    # "intent" grouping column from the result.
    parts = [
        group.sample(n=min(per_class, len(group)), random_state=seed)
        for _, group in df.groupby("intent")
    ]
    sampled = pd.concat(parts)
    if len(sampled) > max_examples:
        sampled = sampled.sample(n=max_examples, random_state=seed)
    return sampled.reset_index(drop=True)


def _make_loader(
    df: pd.DataFrame,
    label_mapping: dict[str, int],
    tokenizer: Any,
    pad_token_id: int,
    batch_size: int,
    shuffle: bool,
    seed: int,
) -> DataLoader:
    dataset = IntentTextDataset(
        texts=df["instruction"].tolist(),
        labels=_encode_labels(df, label_mapping),
        tokenizer=tokenizer,
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
        collate_fn=partial(collate_batch, pad_token_id=pad_token_id),
        generator=generator,
    )


def _run_training_epoch(
    model: Any, loader: DataLoader, optimizer: torch.optim.Optimizer
) -> None:
    model.train()
    for input_ids, attention_mask, labels in loader:
        optimizer.zero_grad()
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        outputs.loss.backward()
        optimizer.step()


@torch.no_grad()
def _evaluate(model: Any, loader: DataLoader, label_names: list[str]) -> dict[str, Any]:
    model.eval()
    all_true: list[int] = []
    all_pred: list[int] = []
    for input_ids, attention_mask, labels in loader:
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        predictions = torch.argmax(outputs.logits, dim=1)
        all_true.extend(labels.tolist())
        all_pred.extend(predictions.tolist())
    return compute_metrics(all_true, all_pred, label_names)


def run_training(
    processed_dir: Path = PROCESSED_DIR,
    artifacts_dir: Path = ARTIFACTS_DIR,
    seed: int = SEED,
    mode: str = "smoke",
    checkpoint: str = PRETRAINED_CHECKPOINT,
    tokenizer: Any = None,
    model_builder: Callable[[int], Any] | None = None,
) -> dict[str, Any]:
    """Fine-tune DistilBERT and persist a versioned artifact.

    ``tokenizer``/``model_builder`` are injectable seams so tests can substitute a
    tiny offline tokenizer/model instead of downloading the full pretrained
    checkpoint; production callers should leave them unset.

    Returns the trained version id, its artifact directory, and validation/test metrics.
    """
    if mode not in TRAIN_CONFIGS:
        raise ValueError(f"Unknown mode '{mode}'; expected one of {sorted(TRAIN_CONFIGS)}")

    _set_seed(seed)

    train_df = _load_split(processed_dir, "train")
    validation_df = _load_split(processed_dir, "validation")
    test_df = _load_split(processed_dir, "test")

    label_mapping = build_label_mapping(train_df)
    label_names = sorted(label_mapping, key=label_mapping.get)

    train_config = {**TRAIN_CONFIGS[mode], "seed": seed}

    train_subset = _stratified_subsample(train_df, train_config["max_train_examples"], seed)
    validation_subset = _stratified_subsample(
        validation_df, train_config["max_eval_examples"], seed
    )
    test_subset = _stratified_subsample(test_df, train_config["max_eval_examples"], seed)

    tok = tokenizer if tokenizer is not None else load_tokenizer(checkpoint)
    model = (
        model_builder(len(label_mapping))
        if model_builder is not None
        else build_model(len(label_mapping), checkpoint=checkpoint)
    )

    batch_size = train_config["batch_size"]
    train_loader = _make_loader(
        train_subset, label_mapping, tok, tok.pad_token_id, batch_size, shuffle=True, seed=seed
    )
    validation_loader = _make_loader(
        validation_subset,
        label_mapping,
        tok,
        tok.pad_token_id,
        batch_size,
        shuffle=False,
        seed=seed,
    )
    test_loader = _make_loader(
        test_subset, label_mapping, tok, tok.pad_token_id, batch_size, shuffle=False, seed=seed
    )

    optimizer = torch.optim.AdamW(
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
        _run_training_epoch(model, train_loader, optimizer)
        validation_metrics = _evaluate(model, validation_loader, label_names)
        macro_f1 = validation_metrics["macro_f1"]
        print(f"[distilbert:{mode}] epoch {epoch} validation_macro_f1={macro_f1:.4f}", flush=True)

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
        "max_seq_len": MAX_SEQ_LEN,
        "num_classes": len(label_mapping),
        "model": {**MODEL_CONFIG, "checkpoint": checkpoint},
        "train": train_config,
    }

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_name": MODEL_NAME,
        "mode": mode,
        "seed": seed,
        "data_sources": {
            "train": str(processed_dir / "train.csv"),
            "validation": str(processed_dir / "validation.csv"),
            "test": str(processed_dir / "test.csv"),
        },
        "row_counts": {
            "train": len(train_subset),
            "validation": len(validation_subset),
            "test": len(test_subset),
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
        tokenizer=tok,
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
    print(f"Trained DistilBERT version: {result['version']}")
    print(f"Artifact directory: {result['artifact_dir']}")
    for split_name, metrics in result["metrics"].items():
        print(
            f"  {split_name}: accuracy={metrics['accuracy']:.4f} "
            f"macro_f1={metrics['macro_f1']:.4f} weighted_f1={metrics['weighted_f1']:.4f}"
        )


if __name__ == "__main__":
    _mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    _print_summary(run_training(mode=_mode))

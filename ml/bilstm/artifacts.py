"""Versioned artifact persistence for the Embedding + BiLSTM classifier.

Each trained run is written to ``artifacts_dir/<version>/`` and contains every
artifact required by ML_TRAINING_SPEC.md: model, vocabulary (tokenizer),
label mapping, configuration, training manifest, metrics, and version.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import torch

from ml.bilstm.config import ARTIFACTS_DIR, LATEST_VERSION_FILENAME
from ml.bilstm.model import BiLSTMClassifier
from ml.bilstm.tokenizer import Vocabulary

_VERSION_PATTERN = re.compile(r"^v(\d+)$")


def next_version(artifacts_dir: Path = ARTIFACTS_DIR) -> str:
    """Return the next sequential version id (``v1``, ``v2``, ...) for ``artifacts_dir``."""
    if not artifacts_dir.exists():
        return "v1"
    existing = [
        int(match.group(1))
        for path in artifacts_dir.iterdir()
        if path.is_dir() and (match := _VERSION_PATTERN.match(path.name))
    ]
    return f"v{max(existing, default=0) + 1}"


def save_artifact(
    *,
    version: str,
    model: BiLSTMClassifier,
    vocabulary: Vocabulary,
    label_mapping: dict[str, int],
    config: dict[str, Any],
    manifest: dict[str, Any],
    metrics: dict[str, Any],
    artifacts_dir: Path = ARTIFACTS_DIR,
) -> Path:
    """Persist one training run's artifacts and update the latest-version pointer."""
    version_dir = artifacts_dir / version
    version_dir.mkdir(parents=True, exist_ok=True)

    torch.save(model.state_dict(), version_dir / "model_state.pt")
    _write_json(version_dir / "vocabulary.json", vocabulary.to_dict())
    _write_json(version_dir / "label_mapping.json", label_mapping)
    _write_json(version_dir / "config.json", config)
    _write_json(version_dir / "manifest.json", manifest)
    _write_json(version_dir / "metrics.json", metrics)
    (version_dir / "VERSION").write_text(version, encoding="utf-8")

    _set_latest_version(version, artifacts_dir)
    return version_dir


def load_artifact(
    version: str | None = None, artifacts_dir: Path = ARTIFACTS_DIR
) -> dict[str, Any]:
    """Load a saved artifact bundle. Defaults to the most recently trained version."""
    resolved_version = version or load_latest_version(artifacts_dir)
    version_dir = artifacts_dir / resolved_version
    if not version_dir.exists():
        raise FileNotFoundError(f"No BiLSTM artifact found for version '{resolved_version}'")

    config = _read_json(version_dir / "config.json")
    label_mapping = _read_json(version_dir / "label_mapping.json")
    vocabulary = Vocabulary.from_dict(_read_json(version_dir / "vocabulary.json"))

    model = BiLSTMClassifier(
        vocab_size=config["vocab_size"],
        num_classes=config["num_classes"],
        **config["model"],
    )
    state_dict = torch.load(version_dir / "model_state.pt", map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    return {
        "version": resolved_version,
        "model": model,
        "vocabulary": vocabulary,
        "label_mapping": label_mapping,
        "config": config,
        "manifest": _read_json(version_dir / "manifest.json"),
        "metrics": _read_json(version_dir / "metrics.json"),
    }


def load_latest_version(artifacts_dir: Path = ARTIFACTS_DIR) -> str:
    """Read the version id most recently written by ``save_artifact``."""
    pointer = artifacts_dir / LATEST_VERSION_FILENAME
    if not pointer.exists():
        raise FileNotFoundError(
            f"No trained BiLSTM version recorded in {pointer}. Run training first."
        )
    return pointer.read_text(encoding="utf-8").strip()


def _set_latest_version(version: str, artifacts_dir: Path) -> None:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / LATEST_VERSION_FILENAME).write_text(version, encoding="utf-8")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

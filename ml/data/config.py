"""Paths and constants for the Phase 02 dataset pipeline."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
METADATA_DIR = REPO_ROOT / "data" / "metadata"

DATASET_REPO_ID = "bitext/Bitext-customer-support-llm-chatbot-training-dataset"
DATASET_FILENAME = "Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv"

# Required by DATASET_SPEC.md: instruction (input), intent (target), category (metadata),
# response (reference).
REQUIRED_COLUMNS: list[str] = ["instruction", "category", "intent", "response"]

SEED = 42
SPLIT_RATIOS: dict[str, float] = {"train": 0.8, "validation": 0.1, "test": 0.1}

MANIFEST_FILENAME = "dataset_manifest.json"

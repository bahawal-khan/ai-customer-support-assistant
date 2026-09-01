"""Reproducible download of the raw Bitext dataset file."""

from __future__ import annotations

from pathlib import Path

from huggingface_hub import hf_hub_download

from ml.data.config import DATASET_FILENAME, DATASET_REPO_ID, RAW_DIR


def download_raw_dataset(dest_dir: Path = RAW_DIR) -> Path:
    """Download the Bitext CSV from Hugging Face Hub into ``dest_dir``.

    Uses ``huggingface_hub.hf_hub_download`` directly (rather than
    ``datasets.load_dataset`` against the dataset repo) because the Arrow
    cache builder used by ``datasets`` for hub datasets can exceed Windows'
    MAX_PATH when the repo id is embedded into a long, space-containing
    project path. The downloaded CSV is later loaded through the Hugging
    Face ``datasets`` library in ``ml.data.load``.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = hf_hub_download(
        repo_id=DATASET_REPO_ID,
        repo_type="dataset",
        filename=DATASET_FILENAME,
        local_dir=str(dest_dir),
    )
    return Path(path)

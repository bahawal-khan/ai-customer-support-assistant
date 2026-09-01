"""Load the raw dataset file into a pandas DataFrame via Hugging Face `datasets`."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from datasets import load_dataset


def load_dataset_as_dataframe(csv_path: Path) -> pd.DataFrame:
    """Load ``csv_path`` through the Hugging Face `datasets` library and
    return it as a pandas DataFrame for validation/cleaning/splitting."""
    hf_dataset = load_dataset("csv", data_files=str(csv_path), split="train")
    return hf_dataset.to_pandas()

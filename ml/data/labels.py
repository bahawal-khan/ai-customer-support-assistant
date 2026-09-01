"""Reproducible intent label mapping."""

from __future__ import annotations

import pandas as pd


def build_label_mapping(df: pd.DataFrame) -> dict[str, int]:
    """Map each intent to a stable integer id, sorted alphabetically for reproducibility."""
    intents = sorted(df["intent"].unique())
    return {intent: index for index, intent in enumerate(intents)}

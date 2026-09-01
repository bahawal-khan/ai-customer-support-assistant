"""Reproducible 80/10/10 stratified split with instruction-level leakage protection."""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split

from ml.data.config import SEED, SPLIT_RATIOS


class LeakageError(ValueError):
    """Raised when the same instruction appears in more than one split."""


def stratified_group_split(
    df: pd.DataFrame,
    seed: int = SEED,
    ratios: dict[str, float] = SPLIT_RATIOS,
) -> dict[str, pd.DataFrame]:
    """Split ``df`` into train/validation/test.

    Splitting happens on unique ``instruction`` groups (not rows) so that no
    duplicate instruction can cross a split boundary, then stratifies on each
    group's intent to preserve class balance.
    """
    groups = df.groupby("instruction", as_index=False)["intent"].first()

    val_test_size = ratios["validation"] + ratios["test"]
    train_groups, holdout_groups = train_test_split(
        groups,
        test_size=val_test_size,
        random_state=seed,
        stratify=groups["intent"],
    )

    relative_test_size = ratios["test"] / val_test_size
    val_groups, test_groups = train_test_split(
        holdout_groups,
        test_size=relative_test_size,
        random_state=seed,
        stratify=holdout_groups["intent"],
    )

    splits: dict[str, pd.DataFrame] = {}
    for name, group_df in (
        ("train", train_groups),
        ("validation", val_groups),
        ("test", test_groups),
    ):
        instructions = set(group_df["instruction"])
        splits[name] = df[df["instruction"].isin(instructions)].reset_index(drop=True)

    assert_no_leakage(splits)
    return splits


def assert_no_leakage(splits: dict[str, pd.DataFrame]) -> None:
    """Raise ``LeakageError`` if any instruction appears in more than one split."""
    instruction_sets = {name: set(split_df["instruction"]) for name, split_df in splits.items()}
    names = list(instruction_sets)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            overlap = instruction_sets[left] & instruction_sets[right]
            if overlap:
                raise LeakageError(
                    f"{len(overlap)} instruction(s) leaked between '{left}' and '{right}' splits"
                )

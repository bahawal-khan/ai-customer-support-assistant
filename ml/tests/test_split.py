import pandas as pd
import pytest

from ml.data.split import LeakageError, assert_no_leakage, stratified_group_split


def _synthetic_dataset(n_classes: int = 5, unique_per_class: int = 30) -> pd.DataFrame:
    rows = []
    for class_index in range(n_classes):
        intent = f"intent_{class_index}"
        for i in range(unique_per_class):
            instruction = f"intent {class_index} example {i}"
            rows.append(
                {
                    "instruction": instruction,
                    "category": "CATEGORY",
                    "intent": intent,
                    "response": f"response {class_index}-{i}",
                }
            )
            if i == 0:
                # duplicate instruction (e.g. re-asked question) must stay together
                rows.append(
                    {
                        "instruction": instruction,
                        "category": "CATEGORY",
                        "intent": intent,
                        "response": f"alternate response {class_index}-{i}",
                    }
                )
    return pd.DataFrame(rows)


def test_stratified_group_split_has_no_instruction_leakage():
    df = _synthetic_dataset()

    splits = stratified_group_split(df, seed=42)

    assert_no_leakage(splits)  # should not raise
    total_rows = sum(len(split_df) for split_df in splits.values())
    assert total_rows == len(df)


def test_stratified_group_split_preserves_duplicate_instruction_grouping():
    df = _synthetic_dataset()
    splits = stratified_group_split(df, seed=42)

    duplicated_instruction = "intent 0 example 0"
    containing_splits = [
        name
        for name, split_df in splits.items()
        if duplicated_instruction in split_df["instruction"].values
    ]

    assert len(containing_splits) == 1
    only_split = splits[containing_splits[0]]
    assert (only_split["instruction"] == duplicated_instruction).sum() == 2


def test_stratified_group_split_approximates_80_10_10():
    df = _synthetic_dataset()
    splits = stratified_group_split(df, seed=42)
    total = sum(len(split_df) for split_df in splits.values())

    assert splits["train"].shape[0] / total == pytest.approx(0.8, abs=0.05)
    assert splits["validation"].shape[0] / total == pytest.approx(0.1, abs=0.05)
    assert splits["test"].shape[0] / total == pytest.approx(0.1, abs=0.05)


def test_stratified_group_split_is_reproducible_with_same_seed():
    df = _synthetic_dataset()

    splits_a = stratified_group_split(df, seed=42)
    splits_b = stratified_group_split(df, seed=42)

    for name in splits_a:
        assert set(splits_a[name]["instruction"]) == set(splits_b[name]["instruction"])


def test_assert_no_leakage_raises_on_overlap():
    splits = {
        "train": pd.DataFrame({"instruction": ["a", "b"]}),
        "validation": pd.DataFrame({"instruction": ["b", "c"]}),
    }

    with pytest.raises(LeakageError):
        assert_no_leakage(splits)

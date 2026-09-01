import pandas as pd
import pytest

from ml.data.schema import SchemaValidationError, find_empty_rows, validate_schema


def _valid_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "instruction": ["cancel my order", "where is my refund"],
            "category": ["ORDER", "REFUND"],
            "intent": ["cancel_order", "track_refund"],
            "response": ["Sure, I can help.", "Let me check."],
        }
    )


def test_validate_schema_passes_with_required_columns():
    validate_schema(_valid_df())


def test_validate_schema_raises_on_missing_column():
    df = _valid_df().drop(columns=["intent"])

    with pytest.raises(SchemaValidationError, match="intent"):
        validate_schema(df)


def test_find_empty_rows_detects_blank_and_nan_values():
    df = _valid_df()
    df.loc[0, "instruction"] = "   "
    df.loc[1, "response"] = None

    mask = find_empty_rows(df)

    assert mask.tolist() == [True, True]


def test_find_empty_rows_all_false_when_clean():
    mask = find_empty_rows(_valid_df())

    assert not mask.any()

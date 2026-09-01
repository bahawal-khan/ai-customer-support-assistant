import pandas as pd

from ml.data.clean import clean_dataframe, normalize_text


def test_normalize_text_collapses_whitespace_and_strips():
    assert normalize_text("  cancel   my    order \n") == "cancel my order"


def test_clean_dataframe_normalizes_and_drops_empty_rows():
    df = pd.DataFrame(
        {
            "instruction": ["  cancel my   order", "   ", "track refund please"],
            "category": ["ORDER", "ORDER", "REFUND"],
            "intent": ["cancel_order", "cancel_order", "track_refund"],
            "response": ["ok", "ok", "checking now"],
        }
    )

    cleaned, removed = clean_dataframe(df)

    assert removed == 1
    assert len(cleaned) == 2
    assert cleaned.loc[0, "instruction"] == "cancel my order"


def test_clean_dataframe_drops_rows_with_nan_in_required_column():
    df = pd.DataFrame(
        {
            "instruction": ["cancel my order", None],
            "category": ["ORDER", "ORDER"],
            "intent": ["cancel_order", "cancel_order"],
            "response": ["ok", "ok"],
        }
    )

    cleaned, removed = clean_dataframe(df)

    assert removed == 1
    assert len(cleaned) == 1

import pandas as pd

from ml.data.labels import build_label_mapping


def test_build_label_mapping_is_sorted_and_zero_indexed():
    df = pd.DataFrame({"intent": ["track_refund", "cancel_order", "cancel_order"]})

    mapping = build_label_mapping(df)

    assert mapping == {"cancel_order": 0, "track_refund": 1}


def test_build_label_mapping_is_reproducible_regardless_of_row_order():
    df_a = pd.DataFrame({"intent": ["b", "a", "c"]})
    df_b = pd.DataFrame({"intent": ["c", "c", "a", "b"]})

    assert build_label_mapping(df_a) == build_label_mapping(df_b)

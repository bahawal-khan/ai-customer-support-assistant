import pandas as pd

from ml.data.dedupe import deduplicate


def test_deduplicate_removes_exact_duplicate_rows():
    df = pd.DataFrame(
        {
            "instruction": ["cancel my order", "cancel my order", "track refund"],
            "category": ["ORDER", "ORDER", "REFUND"],
            "intent": ["cancel_order", "cancel_order", "track_refund"],
            "response": ["ok", "ok", "checking"],
        }
    )

    deduped, removed = deduplicate(df)

    assert removed == 1
    assert len(deduped) == 2


def test_deduplicate_keeps_rows_with_same_instruction_but_different_response():
    df = pd.DataFrame(
        {
            "instruction": ["cancel my order", "cancel my order"],
            "category": ["ORDER", "ORDER"],
            "intent": ["cancel_order", "cancel_order"],
            "response": ["response variant A", "response variant B"],
        }
    )

    deduped, removed = deduplicate(df)

    assert removed == 0
    assert len(deduped) == 2

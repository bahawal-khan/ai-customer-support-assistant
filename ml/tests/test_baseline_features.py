import pandas as pd

from ml.baseline.features import build_vectorizer, fit_vectorizer


def test_build_vectorizer_uses_configured_hyperparameters():
    vectorizer = build_vectorizer()

    assert vectorizer.lowercase is True
    assert vectorizer.ngram_range == (1, 2)
    assert vectorizer.min_df == 2


def test_fit_vectorizer_learns_vocabulary_only_from_training_text():
    train_texts = pd.Series(
        [
            "cancel my order please",
            "cancel my order today",
            "track my refund status",
            "track my refund now",
        ]
    )
    # Word that only ever appears in "validation" text, never passed to fit_vectorizer.
    validation_only_word = "zzzleakedword"

    vectorizer = fit_vectorizer(train_texts)

    assert validation_only_word not in vectorizer.vocabulary_
    assert "cancel" in vectorizer.vocabulary_
    assert "refund" in vectorizer.vocabulary_

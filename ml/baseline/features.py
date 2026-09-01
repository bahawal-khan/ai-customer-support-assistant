"""TF-IDF vectorization for the baseline model.

The vectorizer must only ever be fit on the training split; fitting it on
validation/test text would leak those vocabularies into the model.
"""

from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from ml.baseline.config import TFIDF_CONFIG


def build_vectorizer() -> TfidfVectorizer:
    """Construct an unfit TF-IDF vectorizer using the project's baseline configuration."""
    return TfidfVectorizer(**TFIDF_CONFIG)


def fit_vectorizer(train_texts: pd.Series) -> TfidfVectorizer:
    """Fit a new TF-IDF vectorizer on training text only."""
    vectorizer = build_vectorizer()
    vectorizer.fit(train_texts)
    return vectorizer

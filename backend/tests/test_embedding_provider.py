import pytest

from app.core.config import Settings
from app.core.errors import ModelUnavailableError
from app.providers.embedding_provider import EmbeddingProvider

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _make_settings(**overrides) -> Settings:
    base = Settings(EMBEDDING_MODEL=MODEL_NAME, EMBEDDING_DIMENSION=384)
    return base.model_copy(update=overrides)


@pytest.fixture(scope="module")
def provider() -> EmbeddingProvider:
    provider = EmbeddingProvider(_make_settings())
    try:
        provider.embed_query("connectivity probe")
    except ModelUnavailableError as exc:
        pytest.skip(f"Embedding model unavailable in this environment: {exc}")
    return provider


def test_embed_query_returns_configured_dimension(provider):
    vector = provider.embed_query("My package arrived damaged, I want a refund.")
    assert len(vector) == 384
    assert all(isinstance(value, float) for value in vector)


def test_embed_documents_returns_one_vector_per_text(provider):
    texts = [
        "How do I reset my password?",
        "My router keeps disconnecting from Wi-Fi.",
        "When will my refund be issued?",
    ]
    vectors = provider.embed_documents(texts)
    assert len(vectors) == len(texts)
    assert all(len(vector) == 384 for vector in vectors)


def test_embed_documents_empty_list_returns_empty_list(provider):
    assert provider.embed_documents([]) == []


def test_similar_texts_are_closer_than_unrelated_texts(provider):
    import math

    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        return dot / (norm_a * norm_b)

    refund_a = provider.embed_query("I want a refund for my order.")
    refund_b = provider.embed_query("How do I get my money back for a return?")
    router_c = provider.embed_query("My router's Wi-Fi light is blinking red.")

    assert cosine(refund_a, refund_b) > cosine(refund_a, router_c)


def test_missing_model_name_raises_model_unavailable_error():
    provider = EmbeddingProvider(_make_settings(EMBEDDING_MODEL=""))
    with pytest.raises(ModelUnavailableError):
        provider.embed_query("hello")


def test_dimension_mismatch_raises_model_unavailable_error():
    # The real model produces 384-dim vectors; configuring a mismatched
    # EMBEDDING_DIMENSION must be caught rather than silently persisted.
    provider = EmbeddingProvider(_make_settings(EMBEDDING_DIMENSION=999))
    with pytest.raises(ModelUnavailableError, match="384"):
        provider.embed_query("dimension mismatch check")

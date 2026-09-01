"""Embedding provider wrapping a configurable Hugging Face sentence-embedding model."""

from __future__ import annotations

from sentence_transformers import SentenceTransformer

from app.core.config import Settings, get_settings
from app.core.errors import ModelUnavailableError


class EmbeddingProvider:
    """Loads a Hugging Face embedding model and encodes text into vectors.

    The model is lazy-loaded on first use so importing this module never
    triggers a network call or model download.
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._model: SentenceTransformer | None = None

    @property
    def model_name(self) -> str:
        return self._settings.EMBEDDING_MODEL

    @property
    def dimension(self) -> int:
        return self._settings.EMBEDDING_DIMENSION

    def _load_model(self) -> SentenceTransformer:
        if self._model is not None:
            return self._model

        if not self.model_name:
            raise ModelUnavailableError("EMBEDDING_MODEL is not configured.")

        try:
            self._model = SentenceTransformer(self.model_name)
        except Exception as exc:
            raise ModelUnavailableError(
                f"Failed to load embedding model '{self.model_name}': {exc}"
            ) from exc

        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of chunk texts. Returns one vector per input text."""
        if not texts:
            return []

        model = self._load_model()
        vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        self._validate_dimension(vectors.shape[1])
        return [vector.tolist() for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        return self.embed_documents([text])[0]

    def _validate_dimension(self, actual: int) -> None:
        if actual != self.dimension:
            raise ModelUnavailableError(
                f"Embedding model '{self.model_name}' produced {actual}-dimensional "
                f"vectors, but EMBEDDING_DIMENSION is configured as {self.dimension}."
            )


_provider: EmbeddingProvider | None = None


def get_embedding_provider() -> EmbeddingProvider:
    global _provider
    if _provider is None:
        _provider = EmbeddingProvider()
    return _provider

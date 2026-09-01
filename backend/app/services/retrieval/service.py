"""Phase 09 RAG retrieval.

Pipeline: query -> embedding -> pgvector cosine similarity search -> top-k ->
similarity threshold filtering -> ranked results with source metadata
(docs/rag/RAG_SPEC.md).

Reuses the Phase 08 EmbeddingProvider and the Phase 07 DocumentChunkRepository.
Does not call Groq, LangChain, or expose an API route; those are later phases.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.errors import RetrievalError
from app.models.document_chunk import DocumentChunk
from app.providers.embedding_provider import EmbeddingProvider, get_embedding_provider
from app.repositories.document_chunk_repository import DocumentChunkRepository


@dataclass(frozen=True)
class RetrievedChunk:
    """A single ranked retrieval result with traceable source metadata."""

    chunk_id: uuid.UUID
    document_id: uuid.UUID
    source_id: str
    title: str
    category: str
    version: str
    chunk_index: int
    content: str
    content_hash: str
    score: float
    rank: int


class RAGService:
    """Coordinates query embedding, similarity search, and threshold filtering."""

    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider | None = None,
        settings: Settings | None = None,
        chunk_repository: DocumentChunkRepository | None = None,
    ):
        self._settings = settings or get_settings()
        self._embedding_provider = embedding_provider or get_embedding_provider()
        self._chunk_repo = chunk_repository or DocumentChunkRepository(db)

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
    ) -> list[RetrievedChunk]:
        """Return chunks relevant to `query`, ranked by cosine similarity.

        Returns an empty list (never raises) when nothing meets the similarity
        threshold, so callers can safely detect insufficient context.
        """
        query = query.strip()
        if not query:
            raise RetrievalError("Query text must not be empty.")

        top_k = self._settings.TOP_K if top_k is None else top_k
        threshold = (
            self._settings.SIMILARITY_THRESHOLD
            if similarity_threshold is None
            else similarity_threshold
        )
        if top_k <= 0:
            return []

        query_embedding = self._embedding_provider.embed_query(query)
        matches = self._chunk_repo.similarity_search_with_scores(query_embedding, top_k=top_k)

        results: list[RetrievedChunk] = []
        for chunk, score in matches:
            if score < threshold:
                continue
            results.append(_to_retrieved_chunk(chunk, score, rank=len(results) + 1))
        return results


def _to_retrieved_chunk(chunk: DocumentChunk, score: float, rank: int) -> RetrievedChunk:
    metadata = chunk.chunk_metadata or {}
    return RetrievedChunk(
        chunk_id=chunk.id,
        document_id=chunk.document_id,
        source_id=metadata.get("source_id", ""),
        title=metadata.get("title", ""),
        category=metadata.get("category", ""),
        version=metadata.get("version", ""),
        chunk_index=chunk.chunk_index,
        content=chunk.content,
        content_hash=metadata.get("content_hash", ""),
        score=score,
        rank=rank,
    )

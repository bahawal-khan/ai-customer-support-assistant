"""LangChain-compatible retriever adapter over the Phase 09 RAGService.

Implements the retriever contract from docs/langchain/LANGCHAIN_SPEC.md:

    retrieve(query, filters, k) -> normalized source objects

Retrieval logic (embedding, pgvector similarity search, threshold filtering)
stays in RAGService. This adapter only exposes that result to LangChain
orchestration, and applies optional metadata filtering.

pgvector/RAGService have no filter pushdown (docs/rag/RAG_SPEC.md's
retrieval stage is query -> embedding -> similarity search -> top-k ->
threshold only), so `filters` are applied to the already-ranked top-k
results here. Combining `filters` with a small `k` can therefore return
fewer than `k` sources; callers that need guaranteed counts should pass a
larger `k`.
"""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import PrivateAttr

from app.services.langchain_pipeline.documents import chunks_to_documents
from app.services.retrieval.service import RAGService, RetrievedChunk

FILTERABLE_FIELDS = frozenset({"category", "source_id", "version", "document_id"})


def _matches_filters(chunk: RetrievedChunk, filters: dict[str, Any]) -> bool:
    for field, value in filters.items():
        if field not in FILTERABLE_FIELDS:
            raise ValueError(
                f"Unsupported retrieval filter '{field}'. Supported filters: "
                f"{sorted(FILTERABLE_FIELDS)}."
            )
        chunk_value = getattr(chunk, field)
        if field == "document_id":
            chunk_value = str(chunk_value)
        if chunk_value != value:
            return False
    return True


class RAGRetriever(BaseRetriever):
    """Adapts `RAGService.retrieve` to the LangChain retriever interface."""

    _rag_service: RAGService = PrivateAttr()

    def __init__(self, rag_service: RAGService, **kwargs: Any):
        super().__init__(**kwargs)
        self._rag_service = rag_service

    def retrieve(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        k: int | None = None,
    ) -> list[RetrievedChunk]:
        """Return normalized, traceable source objects for `query`.

        `filters` matches on chunk metadata (see FILTERABLE_FIELDS); `k` caps
        the number of results, same as RAGService's `top_k`.
        """
        chunks = self._rag_service.retrieve(query, top_k=k)
        if not filters:
            return chunks
        return [chunk for chunk in chunks if _matches_filters(chunk, filters)]

    def retrieve_documents(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        k: int | None = None,
    ) -> list[Document]:
        """Same as `retrieve`, converted into LangChain Documents."""
        return chunks_to_documents(self.retrieve(query, filters=filters, k=k))

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        """Standard LangChain Runnable entry point (no filters, default k)."""
        return self.retrieve_documents(query)

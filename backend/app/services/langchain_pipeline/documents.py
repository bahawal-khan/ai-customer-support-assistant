"""Convert Phase 09 retrieval results into LangChain Documents.

Retrieval logic (embedding, pgvector similarity search, threshold filtering)
stays in `app.services.retrieval.service.RAGService`. This module only adapts
its output into `langchain_core.documents.Document`, preserving every
traceability field as metadata, so the LangChain orchestration layer never
depends on SQLAlchemy models or the database directly
(docs/langchain/LANGCHAIN_SPEC.md, docs/rag/RAG_SPEC.md "Chunk metadata").
"""

from __future__ import annotations

from langchain_core.documents import Document

from app.services.retrieval.service import RetrievedChunk


def chunk_to_document(chunk: RetrievedChunk) -> Document:
    """Convert a single normalized retrieval result into a LangChain Document."""
    return Document(
        page_content=chunk.content,
        metadata={
            "chunk_id": str(chunk.chunk_id),
            "document_id": str(chunk.document_id),
            "source_id": chunk.source_id,
            "title": chunk.title,
            "category": chunk.category,
            "version": chunk.version,
            "chunk_index": chunk.chunk_index,
            "content_hash": chunk.content_hash,
            "score": chunk.score,
            "rank": chunk.rank,
        },
    )


def chunks_to_documents(chunks: list[RetrievedChunk]) -> list[Document]:
    """Convert ranked retrieval results into LangChain Documents, preserving order."""
    return [chunk_to_document(chunk) for chunk in chunks]

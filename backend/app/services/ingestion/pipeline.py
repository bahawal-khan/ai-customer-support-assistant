"""Idempotent RAG knowledge-base ingestion pipeline.

Pipeline: Document -> Loader -> text extraction -> cleaning -> chunking ->
metadata -> embeddings -> PostgreSQL/pgvector (docs/rag/RAG_SPEC.md).

Run directly with: python -m app.services.ingestion.pipeline
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.providers.embedding_provider import EmbeddingProvider, get_embedding_provider
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.ingestion.config import (
    DOCUMENT_STATUS_INDEXED,
    DOCUMENT_STATUS_PENDING,
    KNOWLEDGE_BASE_DIR,
)
from app.services.ingestion.loader import LoadedDocument, load_knowledge_base
from app.services.ingestion.splitter import RecursiveCharacterTextSplitter


@dataclass(frozen=True)
class DocumentIngestionResult:
    source_id: str
    action: str  # "created", "updated", or "skipped"
    chunk_count: int


def _chunk_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _build_chunk_metadata(document: Document, chunk_index: int, chunk_text: str) -> dict:
    return {
        "source_id": document.source_id,
        "document_id": str(document.id),
        "title": document.title,
        "category": document.category,
        "version": document.version,
        "chunk_index": chunk_index,
        "content_hash": _chunk_content_hash(chunk_text),
    }


def ingest_document(
    db: Session,
    loaded: LoadedDocument,
    splitter: RecursiveCharacterTextSplitter,
    embedding_provider: EmbeddingProvider,
) -> DocumentIngestionResult:
    """Ingest a single loaded document. Idempotent: unchanged content_hash is skipped."""
    document_repo = DocumentRepository(db)
    chunk_repo = DocumentChunkRepository(db)

    existing = document_repo.get_by_source_id(loaded.source_id)

    if existing is not None and existing.content_hash == loaded.content_hash:
        return DocumentIngestionResult(loaded.source_id, "skipped", len(existing.chunks))

    chunk_texts = splitter.split_text(loaded.clean_text)
    embeddings = embedding_provider.embed_documents(chunk_texts)

    if existing is not None:
        for chunk in list(existing.chunks):
            chunk_repo.delete(chunk)
        existing.title = loaded.title
        existing.category = loaded.category
        existing.version = loaded.version
        existing.content_hash = loaded.content_hash
        existing.status = DOCUMENT_STATUS_PENDING
        db.flush()
        document = existing
        action = "updated"
    else:
        document = document_repo.add(
            Document(
                source_id=loaded.source_id,
                title=loaded.title,
                category=loaded.category,
                version=loaded.version,
                content_hash=loaded.content_hash,
                status=DOCUMENT_STATUS_PENDING,
            )
        )
        action = "created"

    for index, (chunk_text, embedding) in enumerate(zip(chunk_texts, embeddings, strict=True)):
        chunk_repo.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk_text,
                embedding=embedding,
                chunk_metadata=_build_chunk_metadata(document, index, chunk_text),
            )
        )

    document.status = DOCUMENT_STATUS_INDEXED
    db.flush()

    return DocumentIngestionResult(loaded.source_id, action, len(chunk_texts))


def ingest_knowledge_base(
    db: Session,
    directory: Path = KNOWLEDGE_BASE_DIR,
    splitter: RecursiveCharacterTextSplitter | None = None,
    embedding_provider: EmbeddingProvider | None = None,
) -> list[DocumentIngestionResult]:
    """Ingest every Markdown document in `directory`, committing once at the end."""
    splitter = splitter or RecursiveCharacterTextSplitter()
    embedding_provider = embedding_provider or get_embedding_provider()

    results = [
        ingest_document(db, loaded, splitter, embedding_provider)
        for loaded in load_knowledge_base(directory)
    ]
    db.commit()
    return results


def _print_summary(results: list[DocumentIngestionResult]) -> None:
    for result in results:
        print(f"{result.source_id}: {result.action} ({result.chunk_count} chunks)")
    total_chunks = sum(result.chunk_count for result in results)
    print(f"Documents: {len(results)}, total chunks: {total_chunks}")


if __name__ == "__main__":
    session = SessionLocal()
    try:
        summary = ingest_knowledge_base(session)
        _print_summary(summary)
    finally:
        session.close()

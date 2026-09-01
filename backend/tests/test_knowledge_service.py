"""Phase 12 KnowledgeService integration tests.

Exercises the real upload -> index -> delete lifecycle against Postgres (via
the shared `db_session` fixture, skips when unreachable) and an isolated
`tmp_path` knowledge-base directory, reusing the real Phase 08 ingestion
pipeline (app/services/ingestion/*) and a real EmbeddingProvider so chunking/
embedding is not reimplemented or mocked away.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.errors import ModelUnavailableError, NotFoundError, ValidationAppError
from app.providers.embedding_provider import EmbeddingProvider
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.knowledge.service import MAX_UPLOAD_BYTES, KnowledgeService

DOC_CONTENT = b"""---
title: Refund Policy
category: refund
version: v1
---

# Refund Policy

This is a fictional demo refund policy. Refunds are issued within 5
business days of an approved return.
"""


@pytest.fixture
def embedding_provider() -> EmbeddingProvider:
    provider = EmbeddingProvider()
    try:
        provider.embed_query("connectivity probe")
    except ModelUnavailableError as exc:
        pytest.skip(f"Embedding model unavailable in this environment: {exc}")
    return provider


def _service(
    db_session, tmp_path: Path, embedding_provider: EmbeddingProvider
) -> KnowledgeService:
    return KnowledgeService(
        db_session, knowledge_base_dir=tmp_path, embedding_provider=embedding_provider
    )


def test_upload_then_index_creates_document_and_chunks(db_session, tmp_path, embedding_provider):
    service = _service(db_session, tmp_path, embedding_provider)

    document = service.upload_document("refund_policy.md", "text/markdown", DOC_CONTENT)

    assert document.status == "pending"
    assert document.title == "Refund Policy"
    assert document.category == "refund"
    assert (tmp_path / "refund_policy.md").exists()

    outcome = service.index_document(document.id)

    # upload_document() always creates the Document row upfront with a blank
    # content_hash (see its docstring), so the first index_document() call
    # necessarily takes ingest_document()'s "existing row" branch -> "updated".
    assert outcome.action == "updated"
    assert outcome.chunk_count >= 1
    assert outcome.status == "indexed"

    chunks = DocumentChunkRepository(db_session).list_by_document(document.id)
    assert len(chunks) == outcome.chunk_count
    assert all(chunk.embedding is not None for chunk in chunks)


def test_reindex_unchanged_document_is_skipped(db_session, tmp_path, embedding_provider):
    service = _service(db_session, tmp_path, embedding_provider)
    document = service.upload_document("refund_policy.md", "text/markdown", DOC_CONTENT)
    service.index_document(document.id)

    outcome = service.index_document(document.id)

    assert outcome.action == "skipped"


def test_delete_document_removes_row_chunks_and_file(db_session, tmp_path, embedding_provider):
    service = _service(db_session, tmp_path, embedding_provider)
    document = service.upload_document("refund_policy.md", "text/markdown", DOC_CONTENT)
    service.index_document(document.id)
    document_id = document.id

    service.delete_document(document_id)

    assert DocumentRepository(db_session).get(document_id) is None
    assert DocumentChunkRepository(db_session).list_by_document(document_id) == []
    assert not (tmp_path / "refund_policy.md").exists()


def test_index_missing_document_raises_not_found(db_session, tmp_path, embedding_provider):
    import uuid

    service = _service(db_session, tmp_path, embedding_provider)

    with pytest.raises(NotFoundError):
        service.index_document(uuid.uuid4())


def test_delete_missing_document_raises_not_found(db_session, tmp_path, embedding_provider):
    import uuid

    service = _service(db_session, tmp_path, embedding_provider)

    with pytest.raises(NotFoundError):
        service.delete_document(uuid.uuid4())


def test_upload_rejects_non_markdown_extension(db_session, tmp_path, embedding_provider):
    service = _service(db_session, tmp_path, embedding_provider)

    with pytest.raises(ValidationAppError):
        service.upload_document("refund_policy.txt", "text/plain", DOC_CONTENT)


def test_upload_rejects_path_traversal_filename(db_session, tmp_path, embedding_provider):
    service = _service(db_session, tmp_path, embedding_provider)

    with pytest.raises(ValidationAppError):
        service.upload_document("../../etc/passwd.md", "text/markdown", DOC_CONTENT)


def test_upload_rejects_oversized_file(db_session, tmp_path, embedding_provider):
    service = _service(db_session, tmp_path, embedding_provider)
    oversized = DOC_CONTENT + b"x" * MAX_UPLOAD_BYTES

    with pytest.raises(ValidationAppError):
        service.upload_document("refund_policy.md", "text/markdown", oversized)


def test_upload_rejects_missing_frontmatter(db_session, tmp_path, embedding_provider):
    service = _service(db_session, tmp_path, embedding_provider)

    with pytest.raises(ValidationAppError):
        service.upload_document("bad.md", "text/markdown", b"# No frontmatter here")

    assert not (tmp_path / "bad.md").exists()


def test_upload_rejects_empty_file(db_session, tmp_path, embedding_provider):
    service = _service(db_session, tmp_path, embedding_provider)

    with pytest.raises(ValidationAppError):
        service.upload_document("empty.md", "text/markdown", b"")

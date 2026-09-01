import pytest
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories import DocumentChunkRepository, DocumentRepository
from app.services.ingestion.config import KNOWLEDGE_BASE_DIR
from app.services.ingestion.loader import load_document, load_knowledge_base
from app.services.ingestion.pipeline import ingest_document, ingest_knowledge_base
from app.services.ingestion.splitter import RecursiveCharacterTextSplitter

EMBED_DIM = get_settings().EMBEDDING_DIMENSION  # must match the DB's fixed-width vector(N) column


class FakeEmbeddingProvider:
    """Deterministic, network-free stand-in for the real embedding model.

    Real embedding-model behavior (correct dimension, semantic similarity)
    is covered separately in test_embedding_provider.py; these pipeline
    tests only need something that satisfies the same interface quickly.
    """

    def __init__(self, dimension: int = EMBED_DIM):
        self.dimension = dimension
        self.call_count = 0

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.call_count += 1
        return [[float((i + len(text)) % 7) / 7.0] * self.dimension for i, text in enumerate(texts)]


@pytest.fixture()
def splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


@pytest.fixture()
def embedder() -> FakeEmbeddingProvider:
    return FakeEmbeddingProvider()


def test_ingest_knowledge_base_creates_all_documents_and_chunks(db_session, splitter, embedder):
    results = ingest_knowledge_base(
        db_session, KNOWLEDGE_BASE_DIR, splitter=splitter, embedding_provider=embedder
    )

    assert len(results) == 9
    assert all(result.action == "created" for result in results)
    assert all(result.chunk_count > 0 for result in results)

    documents = DocumentRepository(db_session).list(limit=50)
    assert len(documents) == 9
    assert all(doc.status == "indexed" for doc in documents)

    total_expected_chunks = sum(
        len(splitter.split_text(doc.clean_text)) for doc in load_knowledge_base(KNOWLEDGE_BASE_DIR)
    )
    total_persisted_chunks = sum(result.chunk_count for result in results)
    assert total_persisted_chunks == total_expected_chunks


def test_ingested_chunks_have_embeddings_and_required_metadata(db_session, splitter, embedder):
    ingest_knowledge_base(
        db_session, KNOWLEDGE_BASE_DIR, splitter=splitter, embedding_provider=embedder
    )

    document = DocumentRepository(db_session).get_by_source_id("refund_policy.md")
    assert document is not None
    chunk_repo = DocumentChunkRepository(db_session)
    chunks = chunk_repo.list_by_document(document.id)

    assert len(chunks) > 0
    for index, chunk in enumerate(chunks):
        assert chunk.chunk_index == index
        assert chunk.embedding is not None
        assert len(chunk.embedding) == EMBED_DIM
        metadata = chunk.chunk_metadata
        assert metadata["source_id"] == "refund_policy.md"
        assert metadata["document_id"] == str(document.id)
        assert metadata["title"] == document.title
        assert metadata["category"] == document.category
        assert metadata["version"] == document.version
        assert metadata["chunk_index"] == index
        assert len(metadata["content_hash"]) == 64


def test_reingesting_unchanged_knowledge_base_is_idempotent(db_session, splitter, embedder):
    first = ingest_knowledge_base(
        db_session, KNOWLEDGE_BASE_DIR, splitter=splitter, embedding_provider=embedder
    )
    calls_after_first = embedder.call_count

    second = ingest_knowledge_base(
        db_session, KNOWLEDGE_BASE_DIR, splitter=splitter, embedding_provider=embedder
    )

    assert all(result.action == "skipped" for result in second)
    assert [r.chunk_count for r in second] == [r.chunk_count for r in first]
    # No new embedding calls should happen for unchanged documents.
    assert embedder.call_count == calls_after_first

    documents = DocumentRepository(db_session).list(limit=50)
    assert len(documents) == 9  # no duplicate Document rows created

    total_chunks = sum(
        len(DocumentChunkRepository(db_session).list_by_document(doc.id)) for doc in documents
    )
    assert total_chunks == sum(r.chunk_count for r in first)  # no duplicate chunk rows


def test_changed_document_content_replaces_its_chunks(db_session, splitter, embedder, tmp_path):
    kb_dir = tmp_path / "kb"
    kb_dir.mkdir()
    doc_path = kb_dir / "refund_policy.md"
    doc_path.write_text(
        '---\ntitle: "Refund Policy"\ncategory: refund\nversion: v1\n---\n\n'
        "# Refund Policy\n\nOriginal short body about refunds and returns.\n",
        encoding="utf-8",
    )

    first = ingest_document(db_session, load_document(doc_path), splitter, embedder)
    assert first.action == "created"

    doc_path.write_text(
        '---\ntitle: "Refund Policy"\ncategory: refund\nversion: v2\n---\n\n'
        "# Refund Policy\n\nCompletely different updated body about refund timing "
        "and eligibility, long enough to change the chunk boundaries meaningfully.\n",
        encoding="utf-8",
    )

    second = ingest_document(db_session, load_document(doc_path), splitter, embedder)
    db_session.commit()

    assert second.action == "updated"

    document = DocumentRepository(db_session).get_by_source_id("refund_policy.md")
    assert document.version == "v2"
    chunks = DocumentChunkRepository(db_session).list_by_document(document.id)
    assert len(chunks) == second.chunk_count
    contents = " ".join(chunk.content for chunk in chunks)
    assert "Completely different updated body" in contents
    assert "Original short body" not in contents


def test_duplicate_chunk_index_for_same_document_is_rejected(db_session):
    document = DocumentRepository(db_session).add(
        Document(
            source_id="duplicate_test.md",
            title="Duplicate Test",
            category="faq",
            version="v1",
            content_hash="deadbeef",
            status="pending",
        )
    )
    chunk_repo = DocumentChunkRepository(db_session)
    chunk_repo.add(
        DocumentChunk(document_id=document.id, chunk_index=0, content="first", chunk_metadata={})
    )

    with pytest.raises(IntegrityError):
        db_session.add(
            DocumentChunk(document_id=document.id, chunk_index=0, content="dup", chunk_metadata={})
        )
        db_session.flush()
    db_session.rollback()

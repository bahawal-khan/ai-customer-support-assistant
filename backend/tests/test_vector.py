import pytest

from app.core.config import get_settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories import DocumentChunkRepository, DocumentRepository

settings = get_settings()
DIM = settings.EMBEDDING_DIMENSION


def _embedding(seed: float) -> list[float]:
    vector = [0.0] * DIM
    vector[0] = seed
    vector[1] = 1.0 - seed
    return vector


def _make_document(db_session) -> Document:
    return DocumentRepository(db_session).add(
        Document(
            source_id="payment_faq.md",
            title="Payment FAQ",
            category="payment",
            version="v1",
            content_hash="def456",
            status="pending",
        )
    )


def test_embedding_round_trips_through_insert_and_read(db_session):
    doc = _make_document(db_session)
    embedding = _embedding(0.9)
    chunk_repo = DocumentChunkRepository(db_session)

    chunk = chunk_repo.add(
        DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="We accept credit card, debit card, and bank transfer payments.",
            embedding=embedding,
            chunk_metadata={"source_id": doc.source_id, "category": doc.category, "chunk_index": 0},
        )
    )

    fetched = chunk_repo.get(chunk.id)
    assert fetched.embedding is not None
    assert len(fetched.embedding) == DIM
    # pgvector stores components as single-precision floats (float4), so a
    # float64 round-trip is only guaranteed to survive at float32 precision.
    assert fetched.embedding[0] == pytest.approx(embedding[0])
    assert fetched.embedding[1] == pytest.approx(embedding[1])


def test_metadata_jsonb_round_trips(db_session):
    doc = _make_document(db_session)
    chunk_repo = DocumentChunkRepository(db_session)

    metadata = {
        "source_id": doc.source_id,
        "document_id": str(doc.id),
        "title": doc.title,
        "category": doc.category,
        "version": doc.version,
        "chunk_index": 2,
        "content_hash": "def456",
    }
    chunk = chunk_repo.add(
        DocumentChunk(
            document_id=doc.id,
            chunk_index=2,
            content="Bank transfers take 2-3 business days to clear.",
            chunk_metadata=metadata,
        )
    )

    fetched = chunk_repo.get(chunk.id)
    assert fetched.chunk_metadata == metadata


def test_similarity_search_returns_nearest_neighbor_first(db_session):
    doc = _make_document(db_session)
    chunk_repo = DocumentChunkRepository(db_session)

    near = chunk_repo.add(
        DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="Chunk close to the query vector.",
            embedding=_embedding(0.95),
            chunk_metadata={},
        )
    )
    far = chunk_repo.add(
        DocumentChunk(
            document_id=doc.id,
            chunk_index=1,
            content="Chunk far from the query vector.",
            embedding=_embedding(0.05),
            chunk_metadata={},
        )
    )

    results = chunk_repo.similarity_search(_embedding(0.94), top_k=2)

    assert [r.id for r in results][0] == near.id
    assert far.id in [r.id for r in results]


def test_similarity_search_ignores_chunks_without_embedding(db_session):
    doc = _make_document(db_session)
    chunk_repo = DocumentChunkRepository(db_session)

    chunk_repo.add(
        DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="No embedding yet.",
            embedding=None,
            chunk_metadata={},
        )
    )

    results = chunk_repo.similarity_search(_embedding(0.5), top_k=5)

    assert results == []

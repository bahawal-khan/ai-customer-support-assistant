"""Phase 09 RAG retrieval tests.

Unit tests exercise RAGService against in-memory DocumentChunk objects and a
fake embedding provider/repository, so they need no database or model
download. Integration tests exercise the real DocumentChunkRepository against
Postgres/pgvector (via the shared `db_session` fixture, which skips when no
live database is reachable) with a deterministic fake embedding provider, the
same pattern used in test_vector.py and test_ingestion_pipeline.py.
"""

import uuid

import pytest

from app.core.config import Settings, get_settings
from app.core.errors import RetrievalError
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.retrieval.service import RAGService


class FakeEmbeddingProvider:
    """Network-free stand-in satisfying RAGService's embedding interface."""

    def __init__(self, vector: list[float] | None = None):
        self._vector = vector or [1.0, 0.0]
        self.calls: list[str] = []

    def embed_query(self, text: str) -> list[float]:
        self.calls.append(text)
        return self._vector


class FakeChunkRepository:
    """Returns a canned (chunk, score) list, bypassing the database entirely."""

    def __init__(self, matches: list[tuple[DocumentChunk, float]]):
        self._matches = matches
        self.last_top_k: int | None = None

    def similarity_search_with_scores(
        self, query_embedding: list[float], top_k: int = 5
    ) -> list[tuple[DocumentChunk, float]]:
        self.last_top_k = top_k
        return self._matches[:top_k]


def _chunk(
    *,
    document_id: uuid.UUID | None = None,
    chunk_index: int = 0,
    content: str = "Refunds are issued within 5 business days.",
    source_id: str = "refund_policy.md",
    title: str = "Refund Policy",
    category: str = "refund",
    version: str = "v1",
    content_hash: str = "abc123",
) -> DocumentChunk:
    return DocumentChunk(
        id=uuid.uuid4(),
        document_id=document_id or uuid.uuid4(),
        chunk_index=chunk_index,
        content=content,
        chunk_metadata={
            "source_id": source_id,
            "document_id": str(document_id or uuid.uuid4()),
            "title": title,
            "category": category,
            "version": version,
            "chunk_index": chunk_index,
            "content_hash": content_hash,
        },
    )


def _service(matches: list[tuple[DocumentChunk, float]], **settings_overrides) -> tuple[
    RAGService, FakeEmbeddingProvider, FakeChunkRepository
]:
    embedder = FakeEmbeddingProvider()
    repo = FakeChunkRepository(matches)
    settings = Settings(_env_file=None, **settings_overrides)
    service = RAGService(
        db=None,
        embedding_provider=embedder,
        settings=settings,
        chunk_repository=repo,
    )
    return service, embedder, repo


# --- Unit tests (no database) -----------------------------------------------


def test_retrieve_ranks_results_starting_at_one():
    near = _chunk(content="near")
    far = _chunk(content="far")
    service, _, _ = _service([(near, 0.9), (far, 0.4)])

    results = service.retrieve("Where is my refund?")

    assert [r.rank for r in results] == [1, 2]
    assert results[0].chunk_id == near.id
    assert results[0].score == pytest.approx(0.9)
    assert results[1].chunk_id == far.id


def test_retrieve_respects_configured_top_k():
    matches = [(_chunk(chunk_index=i), 0.9 - i * 0.01) for i in range(5)]
    service, _, repo = _service(matches, TOP_K=2)

    results = service.retrieve("router troubleshooting")

    assert repo.last_top_k == 2
    assert len(results) == 2


def test_retrieve_top_k_argument_overrides_settings_default():
    matches = [(_chunk(chunk_index=i), 0.9 - i * 0.01) for i in range(5)]
    service, _, repo = _service(matches, TOP_K=5)

    results = service.retrieve("router troubleshooting", top_k=1)

    assert repo.last_top_k == 1
    assert len(results) == 1


def test_retrieve_filters_out_scores_below_similarity_threshold():
    strong = _chunk(content="strong match")
    weak = _chunk(content="weak match")
    service, _, _ = _service([(strong, 0.8), (weak, 0.2)], SIMILARITY_THRESHOLD=0.5)

    results = service.retrieve("payment question")

    assert len(results) == 1
    assert results[0].chunk_id == strong.id


def test_retrieve_threshold_argument_overrides_settings_default():
    chunk = _chunk()
    service, _, _ = _service([(chunk, 0.6)], SIMILARITY_THRESHOLD=0.0)

    assert service.retrieve("q", similarity_threshold=0.9) == []
    assert len(service.retrieve("q", similarity_threshold=0.5)) == 1


def test_retrieve_returns_empty_list_when_nothing_meets_threshold():
    chunk = _chunk()
    service, _, _ = _service([(chunk, 0.1)], SIMILARITY_THRESHOLD=0.5)

    results = service.retrieve("an unrelated query about spaceships")

    assert results == []


def test_retrieve_returns_empty_list_when_no_chunks_indexed():
    service, _, _ = _service([])

    assert service.retrieve("anything") == []


def test_retrieve_maps_required_source_and_chunk_metadata():
    document_id = uuid.uuid4()
    chunk = _chunk(
        document_id=document_id,
        chunk_index=3,
        content="Contact support to escalate an unresolved ticket.",
        source_id="escalation_policy.md",
        title="Escalation Policy",
        category="escalation",
        version="v2",
        content_hash="deadbeef",
    )
    service, _, _ = _service([(chunk, 0.77)])

    [result] = service.retrieve("how do I escalate my ticket")

    assert result.chunk_id == chunk.id
    assert result.document_id == document_id
    assert result.source_id == "escalation_policy.md"
    assert result.title == "Escalation Policy"
    assert result.category == "escalation"
    assert result.version == "v2"
    assert result.chunk_index == 3
    assert result.content_hash == "deadbeef"
    assert result.content == "Contact support to escalate an unresolved ticket."
    assert result.score == pytest.approx(0.77)


def test_retrieve_rejects_empty_query_without_embedding_it():
    service, embedder, _ = _service([])

    with pytest.raises(RetrievalError):
        service.retrieve("   ")

    assert embedder.calls == []


def test_retrieve_non_positive_top_k_returns_empty_without_embedding():
    service, embedder, _ = _service([(_chunk(), 0.9)])

    assert service.retrieve("q", top_k=0) == []
    assert embedder.calls == []


# --- Integration tests (live Postgres + pgvector) ---------------------------

DIM = get_settings().EMBEDDING_DIMENSION  # must match the DB's fixed-width vector(N) column


def _vector(seed: float) -> list[float]:
    vector = [0.0] * DIM
    vector[0] = seed
    vector[1] = 1.0 - seed
    return vector


class SeededEmbeddingProvider:
    """Embeds every query to the same fixed vector, for deterministic ranking."""

    def __init__(self, vector: list[float]):
        self._vector = vector

    def embed_query(self, text: str) -> list[float]:
        return self._vector


def _make_document(
    db_session,
    source_id: str = "refund_policy.md",
    title: str = "Refund Policy",
    category: str = "refund",
) -> Document:
    return DocumentRepository(db_session).add(
        Document(
            source_id=source_id,
            title=title,
            category=category,
            version="v1",
            content_hash="abc123",
            status="indexed",
        )
    )


def _add_chunk(db_session, document, *, chunk_index, content, embedding) -> DocumentChunk:
    return DocumentChunkRepository(db_session).add(
        DocumentChunk(
            document_id=document.id,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
            chunk_metadata={
                "source_id": document.source_id,
                "document_id": str(document.id),
                "title": document.title,
                "category": document.category,
                "version": document.version,
                "chunk_index": chunk_index,
                "content_hash": f"hash{chunk_index}",
            },
        )
    )


def test_live_retrieve_orders_by_cosine_similarity(db_session):
    document = _make_document(db_session)
    near = _add_chunk(
        db_session, document, chunk_index=0, content="near chunk", embedding=_vector(0.95)
    )
    far = _add_chunk(
        db_session, document, chunk_index=1, content="far chunk", embedding=_vector(0.05)
    )
    db_session.commit()

    settings = Settings(_env_file=None, TOP_K=5, SIMILARITY_THRESHOLD=-1.0)
    service = RAGService(
        db=db_session,
        embedding_provider=SeededEmbeddingProvider(_vector(0.94)),
        settings=settings,
    )

    results = service.retrieve("Where is my refund?")

    assert [r.chunk_id for r in results][0] == near.id
    assert far.id in [r.chunk_id for r in results]
    assert results[0].score > results[-1].score
    assert results[0].rank == 1


def test_live_retrieve_applies_similarity_threshold(db_session):
    document = _make_document(db_session, source_id="payment_faq.md")
    _add_chunk(db_session, document, chunk_index=0, content="close chunk", embedding=_vector(0.9))
    _add_chunk(db_session, document, chunk_index=1, content="distant chunk", embedding=_vector(0.1))
    db_session.commit()

    settings = Settings(_env_file=None, TOP_K=5, SIMILARITY_THRESHOLD=0.99)
    # Query vector deliberately distinct from both indexed chunks (0.9 and
    # 0.1): reusing either one outright would give it cosine similarity 1.0,
    # which trivially clears any threshold <= 1.0 and defeats the test.
    service = RAGService(
        db=db_session,
        embedding_provider=SeededEmbeddingProvider(_vector(0.5)),
        settings=settings,
    )

    results = service.retrieve("payment question unrelated to indexed content")

    assert results == []


def test_live_retrieve_returns_traceable_metadata(db_session):
    document = _make_document(
        db_session,
        source_id="escalation_policy.md",
        title="Escalation Policy",
        category="escalation",
    )
    chunk = _add_chunk(
        db_session,
        document,
        chunk_index=2,
        content="Escalate unresolved tickets to a supervisor.",
        embedding=_vector(0.5),
    )
    db_session.commit()

    settings = Settings(_env_file=None, TOP_K=5, SIMILARITY_THRESHOLD=-1.0)
    service = RAGService(
        db=db_session,
        embedding_provider=SeededEmbeddingProvider(_vector(0.5)),
        settings=settings,
    )

    [result] = service.retrieve("how do I escalate a ticket")

    assert result.chunk_id == chunk.id
    assert result.document_id == document.id
    assert result.source_id == "escalation_policy.md"
    assert result.title == document.title
    assert result.category == "escalation"
    assert result.version == document.version
    assert result.chunk_index == 2
    assert result.content_hash == "hash2"

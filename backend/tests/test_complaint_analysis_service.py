"""Phase 12 ComplaintAnalysisService integration tests.

Exercises the real persistence path (Complaint/Analysis/RetrievedSource/
GeneratedResponse) against Postgres via the shared `db_session` fixture
(skips when no live database is reachable, same pattern as
test_retrieval.py/test_repositories.py). Intent, sentiment, and the LLM are
faked (no model download, no Groq call -- docs/testing/TESTING_SPEC.md
"Integration: Mock Groq. Do not require external LLM credentials"); RAG
retrieval uses the real RAGService/pgvector against a seeded chunk with a
fake (but deterministic) embedding provider, the same pattern as
test_retrieval.py's live tests.
"""

from __future__ import annotations

from app.core.config import Settings, get_settings
from app.core.errors import LLMError
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.generated_response_repository import GeneratedResponseRepository
from app.repositories.retrieved_source_repository import RetrievedSourceRepository
from app.services.complaint_analysis.service import ComplaintAnalysisService
from app.services.intent.service import IntentPrediction
from app.services.llm.service import PROVIDER_NAME, GroundedResponse
from app.services.retrieval.service import RAGService

DIM = get_settings().EMBEDDING_DIMENSION  # must match the DB's fixed-width vector(N) column


def _vector(seed: float) -> list[float]:
    vector = [0.0] * DIM
    vector[0] = seed
    vector[1] = 1.0 - seed
    return vector


class SeededEmbeddingProvider:
    def __init__(self, vector: list[float]):
        self._vector = vector

    def embed_query(self, text: str) -> list[float]:
        return self._vector


class FakeIntentService:
    def __init__(self, label: str = "payment_issue", confidence: float = 0.97):
        self._label = label
        self._confidence = confidence

    def predict_intent(self, text: str) -> IntentPrediction:
        return IntentPrediction(
            label=self._label,
            confidence=self._confidence,
            top_k=[{"label": self._label, "confidence": self._confidence}],
            model_name="distilbert",
            model_version="v2",
        )


class FakeSentimentService:
    def __init__(self, label: str = "negative", confidence: float = 0.88):
        self._label = label
        self._confidence = confidence

    def analyze_sentiment(self, text: str):
        from app.providers.sentiment_provider import SentimentPrediction

        return SentimentPrediction(label=self._label, confidence=self._confidence)


class FakeLLMService:
    def __init__(self, response: str | None = None, error: Exception | None = None):
        self._response = response
        self._error = error

    def generate_response(self, grounded_prompt, request_id=None) -> GroundedResponse:
        if self._error is not None:
            raise self._error
        return GroundedResponse(
            response=self._response,
            provider=PROVIDER_NAME,
            model="openai/gpt-oss-20b",
            prompt_version=grounded_prompt.prompt_version,
            sources=grounded_prompt.sources,
            has_context=grounded_prompt.has_context,
        )


def _make_document(db_session, source_id: str = "refund_policy.md") -> Document:
    return DocumentRepository(db_session).add(
        Document(
            source_id=source_id,
            title="Refund Policy",
            category="refund",
            version="v1",
            content_hash="abc123",
            status="indexed",
        )
    )


def _add_chunk(
    db_session, document: Document, content: str, embedding: list[float]
) -> DocumentChunk:
    return DocumentChunkRepository(db_session).add(
        DocumentChunk(
            document_id=document.id,
            chunk_index=0,
            content=content,
            embedding=embedding,
            chunk_metadata={
                "source_id": document.source_id,
                "document_id": str(document.id),
                "title": document.title,
                "category": document.category,
                "version": document.version,
                "chunk_index": 0,
                "content_hash": "hash0",
            },
        )
    )


def test_analyze_persists_full_pipeline_with_sources_and_llm_success(db_session):
    document = _make_document(db_session)
    chunk = _add_chunk(
        db_session, document, "Refunds are issued within 5 business days.", _vector(0.9)
    )
    db_session.commit()

    settings = Settings(_env_file=None, TOP_K=5, SIMILARITY_THRESHOLD=-1.0)
    rag_service = RAGService(
        db=db_session, embedding_provider=SeededEmbeddingProvider(_vector(0.9)), settings=settings
    )

    service = ComplaintAnalysisService(
        db_session,
        settings=settings,
        intent_service=FakeIntentService(),
        sentiment_service=FakeSentimentService(),
        rag_service=rag_service,
        llm_service=FakeLLMService(response="Refunds take 5 business days."),
    )

    result = service.analyze(
        "My payment was charged but the refund never arrived.", request_id="req-1"
    )

    assert result.intent_label == "payment_issue"
    assert result.intent_model_version == "distilbert-v2"
    assert result.priority.level == "high"
    assert result.suggested_response == "Refunds take 5 business days."
    assert result.llm_available is True
    assert len(result.sources) == 1
    assert result.sources[0].chunk_id == chunk.id

    stored_complaint = ComplaintRepository(db_session).get(result.complaint_id)
    assert stored_complaint is not None
    assert "refund never arrived" in stored_complaint.text

    stored_analysis = AnalysisRepository(db_session).get_by_complaint_id(result.complaint_id)
    assert stored_analysis.intent == "payment_issue"
    assert stored_analysis.priority == "high"
    assert stored_analysis.intent_model_version == "distilbert-v2"

    stored_sources = RetrievedSourceRepository(db_session).list_by_analysis(stored_analysis.id)
    assert len(stored_sources) == 1
    assert stored_sources[0].chunk_id == chunk.id

    stored_response = GeneratedResponseRepository(db_session).get_by_analysis_id(stored_analysis.id)
    assert stored_response is not None
    assert stored_response.response == "Refunds take 5 business days."
    assert stored_response.provider == PROVIDER_NAME


def test_analyze_handles_llm_failure_without_losing_analysis(db_session):
    settings = Settings(_env_file=None, TOP_K=5, SIMILARITY_THRESHOLD=0.99)
    rag_service = RAGService(
        db=db_session, embedding_provider=SeededEmbeddingProvider(_vector(0.1)), settings=settings
    )

    service = ComplaintAnalysisService(
        db_session,
        settings=settings,
        intent_service=FakeIntentService(label="complaint"),
        sentiment_service=FakeSentimentService(label="negative"),
        rag_service=rag_service,
        llm_service=FakeLLMService(error=LLMError("Groq request failed.")),
    )

    result = service.analyze("This is unacceptable, please fix it now.")

    assert result.llm_available is False
    assert result.suggested_response is None
    assert result.sources == []

    stored_analysis = AnalysisRepository(db_session).get_by_complaint_id(result.complaint_id)
    assert stored_analysis is not None
    assert stored_analysis.intent == "complaint"
    assert GeneratedResponseRepository(db_session).get_by_analysis_id(stored_analysis.id) is None


def test_analyze_insufficient_context_is_not_an_error(db_session):
    """No indexed chunks meet the threshold: retrieval returns [], not a failure."""
    settings = Settings(_env_file=None, TOP_K=5, SIMILARITY_THRESHOLD=0.99)
    rag_service = RAGService(
        db=db_session, embedding_provider=SeededEmbeddingProvider(_vector(0.1)), settings=settings
    )

    service = ComplaintAnalysisService(
        db_session,
        settings=settings,
        intent_service=FakeIntentService(label="track_order"),
        sentiment_service=FakeSentimentService(label="neutral"),
        rag_service=rag_service,
        llm_service=FakeLLMService(
            response="The knowledge base does not have enough information to answer this."
        ),
    )

    result = service.analyze("Where is my order?")

    assert result.sources == []
    assert result.priority.level == "low"
    assert "does not have enough information" in result.suggested_response

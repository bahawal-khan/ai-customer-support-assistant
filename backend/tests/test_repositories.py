import pytest
from sqlalchemy.exc import IntegrityError

from app.models.analysis import Analysis
from app.models.complaint import Complaint
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.generated_response import GeneratedResponse
from app.models.retrieved_source import RetrievedSource
from app.repositories import (
    AnalysisRepository,
    ComplaintRepository,
    DocumentChunkRepository,
    DocumentRepository,
    GeneratedResponseRepository,
    RetrievedSourceRepository,
)


def _make_document(db_session) -> Document:
    doc = DocumentRepository(db_session).add(
        Document(
            source_id="refund_policy.md",
            title="Refund Policy",
            category="refund",
            version="v1",
            content_hash="abc123",
            status="pending",
        )
    )
    return doc


def test_document_crud_round_trip(db_session):
    repo = DocumentRepository(db_session)
    doc = _make_document(db_session)

    fetched = repo.get(doc.id)
    assert fetched is not None
    assert fetched.title == "Refund Policy"
    assert fetched.status == "pending"
    assert fetched.created_at is not None

    fetched.status = "indexed"
    db_session.flush()
    db_session.refresh(fetched)
    assert repo.get(doc.id).status == "indexed"

    by_source = repo.get_by_source_id("refund_policy.md")
    assert by_source is not None
    assert by_source.id == doc.id


def test_document_list_with_chunk_counts(db_session):
    doc_with_chunks = _make_document(db_session)
    doc_without_chunks = DocumentRepository(db_session).add(
        Document(
            source_id="delivery_faq.md",
            title="Delivery FAQ",
            category="delivery",
            version="v1",
            content_hash="def456",
            status="pending",
        )
    )
    chunk_repo = DocumentChunkRepository(db_session)
    chunk_repo.add(
        DocumentChunk(
            document_id=doc_with_chunks.id,
            chunk_index=0,
            content="Refunds are issued within 5 business days.",
            chunk_metadata={"source_id": doc_with_chunks.source_id},
        )
    )
    chunk_repo.add(
        DocumentChunk(
            document_id=doc_with_chunks.id,
            chunk_index=1,
            content="Approval starts a 1 business day issue window.",
            chunk_metadata={"source_id": doc_with_chunks.source_id},
        )
    )

    rows = DocumentRepository(db_session).list_with_chunk_counts()
    counts = {doc.id: count for doc, count in rows}

    assert counts[doc_with_chunks.id] == 2
    assert counts[doc_without_chunks.id] == 0


def test_document_chunk_cascade_delete_on_document_removal(db_session):
    doc = _make_document(db_session)
    chunk_repo = DocumentChunkRepository(db_session)
    chunk = chunk_repo.add(
        DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="Refunds are issued within 5 business days.",
            chunk_metadata={"source_id": doc.source_id, "title": doc.title},
        )
    )
    chunk_id = chunk.id

    DocumentRepository(db_session).delete(doc)

    assert chunk_repo.get(chunk_id) is None


def test_complaint_and_analysis_one_to_one(db_session):
    complaint = ComplaintRepository(db_session).add(
        Complaint(text="My payment was charged but the order was not processed.")
    )
    analysis = AnalysisRepository(db_session).add(
        Analysis(
            complaint_id=complaint.id,
            intent="payment_issue",
            intent_confidence=0.97,
            sentiment="negative",
            sentiment_confidence=0.88,
            priority="high",
            priority_reason="Payment failure affecting order fulfillment.",
            intent_model_version="distilbert-v2",
        )
    )

    assert AnalysisRepository(db_session).get_by_complaint_id(complaint.id).id == analysis.id

    duplicate = Analysis(
        complaint_id=complaint.id,
        intent="payment_issue",
        intent_confidence=0.5,
        sentiment="neutral",
        sentiment_confidence=0.5,
        priority="low",
        priority_reason="duplicate",
        intent_model_version="distilbert-v2",
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_analysis_cascade_delete_on_complaint_removal(db_session):
    complaint = ComplaintRepository(db_session).add(
        Complaint(text="Router keeps disconnecting every few minutes.")
    )
    analysis_repo = AnalysisRepository(db_session)
    analysis = analysis_repo.add(
        Analysis(
            complaint_id=complaint.id,
            intent="technical_support",
            intent_confidence=0.91,
            sentiment="negative",
            sentiment_confidence=0.7,
            priority="medium",
            priority_reason="Recurring connectivity issue.",
            intent_model_version="distilbert-v2",
        )
    )
    analysis_id = analysis.id

    ComplaintRepository(db_session).delete(complaint)

    assert analysis_repo.get(analysis_id) is None


def test_retrieved_source_chunk_set_null_on_chunk_delete(db_session):
    doc = _make_document(db_session)
    chunk = DocumentChunkRepository(db_session).add(
        DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="Router troubleshooting steps.",
            chunk_metadata={},
        )
    )
    complaint = ComplaintRepository(db_session).add(Complaint(text="Router is broken."))
    analysis = AnalysisRepository(db_session).add(
        Analysis(
            complaint_id=complaint.id,
            intent="technical_support",
            intent_confidence=0.9,
            sentiment="negative",
            sentiment_confidence=0.6,
            priority="medium",
            priority_reason="Connectivity issue.",
            intent_model_version="distilbert-v2",
        )
    )
    source_repo = RetrievedSourceRepository(db_session)
    source = source_repo.add(
        RetrievedSource(analysis_id=analysis.id, chunk_id=chunk.id, retrieval_score=0.82, rank=1)
    )

    DocumentChunkRepository(db_session).delete(chunk)
    db_session.refresh(source)

    assert source_repo.get(source.id).chunk_id is None


def test_generated_response_round_trip(db_session):
    complaint = ComplaintRepository(db_session).add(Complaint(text="Where is my refund?"))
    analysis = AnalysisRepository(db_session).add(
        Analysis(
            complaint_id=complaint.id,
            intent="refund_request",
            intent_confidence=0.95,
            sentiment="negative",
            sentiment_confidence=0.6,
            priority="medium",
            priority_reason="Refund delayed.",
            intent_model_version="distilbert-v2",
        )
    )
    response_repo = GeneratedResponseRepository(db_session)
    response = response_repo.add(
        GeneratedResponse(
            analysis_id=analysis.id,
            provider="groq",
            model="llama-3.1-8b-instant",
            prompt_version="v1",
            response="Your refund is being processed and should arrive within 5 business days.",
        )
    )

    fetched = response_repo.get_by_analysis_id(analysis.id)
    assert fetched is not None
    assert fetched.id == response.id
    assert fetched.response.startswith("Your refund")

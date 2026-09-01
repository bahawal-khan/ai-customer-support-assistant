"""Phase 12 GET /complaints and GET /complaints/{id} route tests.

These exercise the real repository/join logic against Postgres (via the
shared `db_session` fixture, skips when unreachable), with `get_db`
overridden to reuse that same session/transaction so seeded data is visible
to the request (docs/testing/TESTING_SPEC.md "API: history").
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.analysis import Analysis
from app.models.complaint import Complaint
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.generated_response import GeneratedResponse
from app.models.retrieved_source import RetrievedSource
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.generated_response_repository import GeneratedResponseRepository
from app.repositories.retrieved_source_repository import RetrievedSourceRepository


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app, raise_server_exceptions=False)
    finally:
        app.dependency_overrides.pop(get_db, None)


def _seed_complaint(
    db_session, *, text: str, intent: str, sentiment: str, priority: str
) -> Complaint:
    complaint = ComplaintRepository(db_session).add(Complaint(text=text))
    AnalysisRepository(db_session).add(
        Analysis(
            complaint_id=complaint.id,
            intent=intent,
            intent_confidence=0.9,
            sentiment=sentiment,
            sentiment_confidence=0.8,
            priority=priority,
            priority_reason="seeded for test",
            intent_model_version="distilbert-v2",
        )
    )
    db_session.commit()
    return complaint


def test_list_complaints_returns_seeded_items(db_session, client):
    _seed_complaint(
        db_session,
        text="Where is my refund?",
        intent="get_refund",
        sentiment="negative",
        priority="high",
    )
    _seed_complaint(
        db_session,
        text="How do I track my order?",
        intent="track_order",
        sentiment="neutral",
        priority="low",
    )

    response = client.get("/api/v1/complaints", params={"page": 1, "page_size": 50})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 2
    intents = {item["intent"] for item in body["items"]}
    assert "get_refund" in intents
    assert "track_order" in intents
    assert all(item["intent_confidence"] == 0.9 for item in body["items"])
    assert all(item["sentiment_confidence"] == 0.8 for item in body["items"])


def test_list_complaints_filters_by_priority(db_session, client):
    _seed_complaint(
        db_session,
        text="Urgent payment problem",
        intent="payment_issue",
        sentiment="negative",
        priority="high",
    )
    _seed_complaint(
        db_session,
        text="Just checking delivery options",
        intent="delivery_options",
        sentiment="neutral",
        priority="low",
    )

    response = client.get("/api/v1/complaints", params={"priority": "high", "page_size": 50})

    body = response.json()
    assert all(item["priority"] == "high" for item in body["items"])
    assert any("payment problem" in item["text"] for item in body["items"])


def test_list_complaints_filters_by_search(db_session, client):
    unique = str(uuid.uuid4())[:8]
    _seed_complaint(
        db_session,
        text=f"Special-{unique} refund request",
        intent="get_refund",
        sentiment="negative",
        priority="high",
    )

    response = client.get("/api/v1/complaints", params={"search": unique})

    body = response.json()
    assert body["total"] == 1
    assert unique in body["items"][0]["text"]


def test_get_complaint_returns_full_detail_with_sources_and_response(db_session, client):
    document = DocumentRepository(db_session).add(
        Document(
            source_id="refund_policy.md",
            title="Refund Policy",
            category="refund",
            version="v1",
            content_hash="abc123",
            status="indexed",
        )
    )
    chunk = DocumentChunkRepository(db_session).add(
        DocumentChunk(
            document_id=document.id,
            chunk_index=0,
            content="Refunds are issued within 5 business days.",
            chunk_metadata={
                "source_id": "refund_policy.md",
                "document_id": str(document.id),
                "title": "Refund Policy",
                "category": "refund",
                "version": "v1",
                "chunk_index": 0,
                "content_hash": "hash0",
            },
        )
    )
    complaint = ComplaintRepository(db_session).add(Complaint(text="Where is my refund?"))
    analysis = AnalysisRepository(db_session).add(
        Analysis(
            complaint_id=complaint.id,
            intent="get_refund",
            intent_confidence=0.95,
            sentiment="negative",
            sentiment_confidence=0.8,
            priority="high",
            priority_reason="Negative sentiment on a sensitive intent ('get_refund').",
            intent_model_version="distilbert-v2",
        )
    )
    RetrievedSourceRepository(db_session).add(
        RetrievedSource(analysis_id=analysis.id, chunk_id=chunk.id, retrieval_score=0.91, rank=1)
    )
    GeneratedResponseRepository(db_session).add(
        GeneratedResponse(
            analysis_id=analysis.id,
            provider="groq",
            model="openai/gpt-oss-20b",
            prompt_version="grounded-support-v1",
            response="Refunds take 5 business days.",
        )
    )
    db_session.commit()

    response = client.get(f"/api/v1/complaints/{complaint.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["complaint_id"] == str(complaint.id)
    assert body["intent"]["label"] == "get_refund"
    assert body["priority"]["level"] == "high"
    assert body["suggested_response"] == "Refunds take 5 business days."
    assert len(body["retrieved_sources"]) == 1
    assert body["retrieved_sources"][0]["source_id"] == "refund_policy.md"
    assert body["model_metadata"]["llm_available"] is True


def test_get_complaint_not_found_returns_404(db_session, client):
    response = client.get(f"/api/v1/complaints/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"

"""Phase 12 POST /complaints/analyze route tests.

Route-level tests only exercise request/response wiring and error mapping:
ComplaintAnalysisService is replaced with a fake, so no real DB connection,
ML model load, or Groq call happens here (docs/testing/TESTING_SPEC.md
"Integration: Mock Groq. Do not require external LLM credentials for normal
tests."). Full pipeline behavior (real persistence, real RAG) is covered by
test_complaint_analysis_service.py.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

import app.api.v1.complaints as complaints_module
from app.core.config import get_settings
from app.core.errors import ModelUnavailableError
from app.main import app
from app.services.complaint_analysis.service import ComplaintAnalysisResult
from app.services.priority.service import PriorityResult

client = TestClient(app, raise_server_exceptions=False)


def _result(**overrides) -> ComplaintAnalysisResult:
    defaults = dict(
        complaint_id=uuid.uuid4(),
        intent_label="payment_issue",
        intent_confidence=0.97,
        intent_model_version="distilbert-v2",
        sentiment_label="negative",
        sentiment_confidence=0.88,
        priority=PriorityResult(
            "high", "Negative sentiment on a sensitive intent ('payment_issue')."
        ),
        sources=[],
        suggested_response="Refunds take 5 business days.",
        llm_provider="groq",
        llm_model="openai/gpt-oss-20b",
        prompt_version="grounded-support-v1",
        llm_available=True,
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    )
    defaults.update(overrides)
    return ComplaintAnalysisResult(**defaults)


class _FakeService:
    """Stands in for ComplaintAnalysisService; class-level state set per-test."""

    result: ComplaintAnalysisResult | None = None
    error: Exception | None = None
    received_texts: list[str] = []

    def __init__(self, db, **kwargs):
        pass

    def analyze(self, text, request_id=None):
        _FakeService.received_texts.append(text)
        if _FakeService.error is not None:
            raise _FakeService.error
        return _FakeService.result


@pytest.fixture(autouse=True)
def _patch_service(monkeypatch):
    _FakeService.result = _result()
    _FakeService.error = None
    _FakeService.received_texts = []
    monkeypatch.setattr(complaints_module, "ComplaintAnalysisService", _FakeService)
    yield


def test_analyze_returns_structured_response():
    response = client.post(
        "/api/v1/complaints/analyze", json={"text": "My payment was charged twice."}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == {
        "label": "payment_issue",
        "confidence": pytest.approx(0.97),
        "model_version": "distilbert-v2",
    }
    assert body["sentiment"]["label"] == "negative"
    assert body["priority"]["level"] == "high"
    assert body["suggested_response"] == "Refunds take 5 business days."
    assert body["retrieved_sources"] == []
    assert body["model_metadata"]["llm_available"] is True
    assert body["model_metadata"]["intent_model_version"] == "distilbert-v2"
    assert "request_id" in body
    assert "complaint_id" in body


def test_analyze_passes_stripped_text_to_service():
    client.post("/api/v1/complaints/analyze", json={"text": "  Where is my refund?  "})

    assert _FakeService.received_texts == ["Where is my refund?"]


def test_analyze_rejects_empty_text():
    response = client.post("/api/v1/complaints/analyze", json={"text": "   "})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "request_id" in response.json()["error"]


def test_analyze_rejects_text_over_max_length():
    too_long = "x" * (get_settings().MAX_COMPLAINT_LENGTH + 1)

    response = client.post("/api/v1/complaints/analyze", json={"text": too_long})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_analyze_rejects_missing_text_field():
    response = client.post("/api/v1/complaints/analyze", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_analyze_maps_model_unavailable_error_to_503():
    _FakeService.error = ModelUnavailableError(
        "No trained intent classification model is available."
    )

    response = client.post("/api/v1/complaints/analyze", json={"text": "Where is my refund?"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "model_unavailable"


def test_analyze_reflects_llm_failure_as_partial_success():
    _FakeService.result = _result(
        suggested_response=None, llm_available=False, llm_provider=None, llm_model=None
    )

    response = client.post("/api/v1/complaints/analyze", json={"text": "Where is my refund?"})

    assert response.status_code == 200
    body = response.json()
    assert body["suggested_response"] is None
    assert body["model_metadata"]["llm_available"] is False
    assert body["model_metadata"]["llm_provider"] is None


def test_analyze_response_includes_request_id_header_matching_body():
    response = client.post("/api/v1/complaints/analyze", json={"text": "Where is my refund?"})

    assert "X-Request-ID" in response.headers
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_analyze_includes_retrieved_sources():
    from app.services.retrieval.service import RetrievedChunk

    source = RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        source_id="refund_policy.md",
        title="Refund Policy",
        category="refund",
        version="v1",
        chunk_index=0,
        content="Refunds are issued within 5 business days.",
        content_hash="abc123",
        score=0.91,
        rank=1,
    )
    _FakeService.result = _result(sources=[source])

    response = client.post("/api/v1/complaints/analyze", json={"text": "Where is my refund?"})

    body = response.json()
    assert len(body["retrieved_sources"]) == 1
    assert body["retrieved_sources"][0]["source_id"] == "refund_policy.md"
    assert body["retrieved_sources"][0]["score"] == pytest.approx(0.91)

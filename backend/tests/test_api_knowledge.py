"""Phase 12 knowledge document route tests.

Route-level tests replace KnowledgeService/DocumentRepository with fakes, so
no real DB connection or embedding model load happens here
(docs/testing/TESTING_SPEC.md). Full upload/index/delete behavior against a
real database and embedding model is covered by test_knowledge_service.py.
"""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

import app.api.v1.knowledge as knowledge_module
from app.core.errors import NotFoundError, ValidationAppError
from app.main import app
from app.models.document import Document
from app.services.knowledge.service import IndexOutcome

client = TestClient(app, raise_server_exceptions=False)


def _document(**overrides) -> Document:
    now = datetime.now(timezone.utc)
    doc = Document(
        source_id=overrides.get("source_id", "refund_policy.md"),
        title=overrides.get("title", "Refund Policy"),
        category=overrides.get("category", "refund"),
        version=overrides.get("version", "v1"),
        content_hash=overrides.get("content_hash", ""),
        status=overrides.get("status", "pending"),
    )
    doc.id = overrides.get("id", uuid.uuid4())
    doc.created_at = now
    doc.updated_at = now
    return doc


class _FakeKnowledgeService:
    upload_result: Document | None = None
    upload_error: Exception | None = None
    index_result: IndexOutcome | None = None
    index_error: Exception | None = None
    delete_error: Exception | None = None
    upload_calls: list[tuple] = []

    def __init__(self, db, **kwargs):
        pass

    def upload_document(self, filename, content_type, content):
        _FakeKnowledgeService.upload_calls.append((filename, content_type, content))
        if _FakeKnowledgeService.upload_error is not None:
            raise _FakeKnowledgeService.upload_error
        return _FakeKnowledgeService.upload_result

    def index_document(self, document_id):
        if _FakeKnowledgeService.index_error is not None:
            raise _FakeKnowledgeService.index_error
        return _FakeKnowledgeService.index_result

    def delete_document(self, document_id):
        if _FakeKnowledgeService.delete_error is not None:
            raise _FakeKnowledgeService.delete_error


class _FakeDocumentRepository:
    documents: list[Document] = []

    def __init__(self, db):
        pass

    def list(self, limit=200, offset=0):
        return _FakeDocumentRepository.documents[:limit]

    def list_with_chunk_counts(self, limit=200, offset=0):
        return [(doc, 2) for doc in _FakeDocumentRepository.documents[:limit]]


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    _FakeKnowledgeService.upload_result = _document()
    _FakeKnowledgeService.upload_error = None
    _FakeKnowledgeService.index_result = IndexOutcome(
        document_id=uuid.uuid4(),
        source_id="refund_policy.md",
        action="created",
        chunk_count=3,
        status="indexed",
    )
    _FakeKnowledgeService.index_error = None
    _FakeKnowledgeService.delete_error = None
    _FakeKnowledgeService.upload_calls = []
    _FakeDocumentRepository.documents = []

    monkeypatch.setattr(knowledge_module, "KnowledgeService", _FakeKnowledgeService)
    monkeypatch.setattr(knowledge_module, "DocumentRepository", _FakeDocumentRepository)
    yield


def test_upload_document_returns_created_document():
    response = client.post(
        "/api/v1/knowledge/documents",
        files={"file": ("refund_policy.md", io.BytesIO(b"content"), "text/markdown")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["source_id"] == "refund_policy.md"
    assert body["status"] == "pending"
    assert _FakeKnowledgeService.upload_calls[0][0] == "refund_policy.md"


def test_upload_document_maps_validation_error():
    _FakeKnowledgeService.upload_error = ValidationAppError(
        "Only Markdown (.md) knowledge documents are supported."
    )

    response = client.post(
        "/api/v1/knowledge/documents",
        files={"file": ("policy.txt", io.BytesIO(b"content"), "text/plain")},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_list_documents_returns_items():
    _FakeDocumentRepository.documents = [_document(source_id="a.md"), _document(source_id="b.md")]

    response = client.get("/api/v1/knowledge/documents")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["source_id"] for item in body["items"]} == {"a.md", "b.md"}
    assert all(item["chunk_count"] == 2 for item in body["items"])


def test_index_document_returns_outcome():
    document_id = uuid.uuid4()
    _FakeKnowledgeService.index_result = IndexOutcome(
        document_id=document_id,
        source_id="refund_policy.md",
        action="updated",
        chunk_count=4,
        status="indexed",
    )

    response = client.post(f"/api/v1/knowledge/documents/{document_id}/index")

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "updated"
    assert body["chunk_count"] == 4
    assert body["status"] == "indexed"


def test_index_document_maps_not_found_to_404():
    _FakeKnowledgeService.index_error = NotFoundError("Knowledge document was not found.")

    response = client.post(f"/api/v1/knowledge/documents/{uuid.uuid4()}/index")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_delete_document_returns_deleted_true():
    document_id = uuid.uuid4()

    response = client.delete(f"/api/v1/knowledge/documents/{document_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["deleted"] is True
    assert body["document_id"] == str(document_id)


def test_delete_document_maps_not_found_to_404():
    _FakeKnowledgeService.delete_error = NotFoundError("Knowledge document was not found.")

    response = client.delete(f"/api/v1/knowledge/documents/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_index_document_rejects_invalid_uuid():
    response = client.post("/api/v1/knowledge/documents/not-a-uuid/index")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"

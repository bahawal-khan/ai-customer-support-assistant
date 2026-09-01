"""DELETE /complaints route tests.

Route-level tests only exercise request/response wiring and error mapping:
ComplaintManagementService is replaced with a fake, so no real DB connection
happens here (docs/testing/TESTING_SPEC.md). Full cascade-delete behavior
against a real database is covered by test_complaint_management_service.py.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

import app.api.v1.complaints as complaints_module
from app.core.errors import NotFoundError
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


class _FakeService:
    """Stands in for ComplaintManagementService; class-level state set per-test."""

    result: list[str] | None = None
    error: Exception | None = None
    received_ids: list[list[str]] = []

    def __init__(self, db, **kwargs):
        pass

    def bulk_delete(self, complaint_ids):
        _FakeService.received_ids.append(complaint_ids)
        if _FakeService.error is not None:
            raise _FakeService.error
        return _FakeService.result if _FakeService.result is not None else complaint_ids


@pytest.fixture(autouse=True)
def _patch_service(monkeypatch):
    _FakeService.result = None
    _FakeService.error = None
    _FakeService.received_ids = []
    monkeypatch.setattr(complaints_module, "ComplaintManagementService", _FakeService)
    yield


def test_delete_complaints_returns_deleted_ids():
    ids = [str(uuid.uuid4()), str(uuid.uuid4())]

    response = client.request("DELETE", "/api/v1/complaints", json={"complaint_ids": ids})

    assert response.status_code == 200
    body = response.json()
    assert sorted(body["deleted_ids"]) == sorted(ids)


def test_delete_complaints_rejects_empty_list():
    response = client.request("DELETE", "/api/v1/complaints", json={"complaint_ids": []})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_delete_complaints_rejects_missing_field():
    response = client.request("DELETE", "/api/v1/complaints", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_delete_complaints_maps_not_found_to_404():
    _FakeService.error = NotFoundError("Complaint(s) not found: some-id")

    response = client.request(
        "DELETE", "/api/v1/complaints", json={"complaint_ids": [str(uuid.uuid4())]}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_delete_complaints_passes_parsed_ids_to_service():
    target_id = str(uuid.uuid4())

    client.request("DELETE", "/api/v1/complaints", json={"complaint_ids": [target_id]})

    assert str(_FakeService.received_ids[0][0]) == target_id

"""GET /health -- application status, database status, version (docs/api/API_SPEC.md,
docs/testing/TESTING_SPEC.md "API: health")."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app, raise_server_exceptions=False)
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_health_returns_ok_status_with_database_and_version(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["version"]


def test_health_reports_database_unavailable_when_query_fails():
    def _broken_get_db():
        class _BrokenSession:
            def execute(self, *args, **kwargs):
                raise RuntimeError("database connection lost")

        yield _BrokenSession()

    app.dependency_overrides[get_db] = _broken_get_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/health")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "unavailable"

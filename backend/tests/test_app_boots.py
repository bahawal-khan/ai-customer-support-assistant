from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.core.errors import REQUEST_ID_HEADER, ValidationAppError
from app.main import app


def test_app_instance_is_fastapi():
    assert isinstance(app, FastAPI)


def test_cors_middleware_configured():
    middleware_classes = [m.cls for m in app.user_middleware]
    assert CORSMiddleware in middleware_classes


def test_request_id_header_present_on_response():
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/does-not-exist")

    assert REQUEST_ID_HEADER in response.headers


def test_app_error_handler_returns_error_envelope():
    client = TestClient(app, raise_server_exceptions=False)

    @app.get("/__test-validation-error")
    def _raise_validation_error():
        raise ValidationAppError("bad input")

    response = client.get("/__test-validation-error")

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "bad input"
    assert "request_id" in body["error"]


def test_unhandled_exception_returns_safe_internal_error():
    client = TestClient(app, raise_server_exceptions=False)

    @app.get("/__test-unhandled-error")
    def _raise_unexpected_error():
        raise RuntimeError("something with a secret token=abc123")

    response = client.get("/__test-unhandled-error")

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert "token=abc123" not in response.text

"""Phase 11 Groq provider tests.

Unit tests only: the Groq client is always a fake/mocked object injected
into GroqProvider, so nothing here makes a real network call or requires a
GROQ_API_KEY (docs/llm/GROQ_SPEC.md "Testing", docs/testing/TESTING_SPEC.md
"Integration": "Mock Groq. Do not require external LLM credentials").
"""

from __future__ import annotations

import groq
import httpx
import pytest

from app.core.config import Settings
from app.core.errors import LLMError
from app.providers.groq_provider import GroqProvider

MODEL_NAME = "openai/gpt-oss-20b"


def _settings(**overrides) -> Settings:
    base = Settings(_env_file=None, GROQ_API_KEY="test-key", GROQ_MODEL=MODEL_NAME)
    return base.model_copy(update=overrides)


class _FakeMessage:
    def __init__(self, content: str | None):
        self.content = content


class _FakeChoice:
    def __init__(self, content: str | None):
        self.message = _FakeMessage(content)


class _FakeCompletion:
    def __init__(self, content: str | None):
        self.choices = [_FakeChoice(content)] if content is not None else []


class _FakeCompletions:
    def __init__(self, completion: _FakeCompletion | None = None, error: Exception | None = None):
        self._completion = completion
        self._error = error
        self.last_kwargs: dict | None = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        if self._error is not None:
            raise self._error
        return self._completion


class _FakeChat:
    def __init__(self, completions: _FakeCompletions):
        self.completions = completions


class _FakeClient:
    def __init__(self, completion: _FakeCompletion | None = None, error: Exception | None = None):
        self.chat = _FakeChat(_FakeCompletions(completion, error))


def _request() -> httpx.Request:
    return httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")


def _response(status_code: int) -> httpx.Response:
    return httpx.Response(status_code=status_code, request=_request())


# --- configuration validation -------------------------------------------------


def test_missing_api_key_raises_llm_error():
    provider = GroqProvider(_settings(GROQ_API_KEY=""))
    with pytest.raises(LLMError, match="GROQ_API_KEY"):
        provider.generate("system", "user")


def test_missing_model_raises_llm_error():
    provider = GroqProvider(_settings(GROQ_MODEL=""))
    with pytest.raises(LLMError, match="GROQ_MODEL"):
        provider.generate("system", "user")


def test_empty_prompt_raises_llm_error_without_calling_client():
    client = _FakeClient(completion=_FakeCompletion("should not be reached"))
    provider = GroqProvider(_settings(), client=client)

    with pytest.raises(LLMError, match="empty"):
        provider.generate("   ", "user")

    assert client.chat.completions.last_kwargs is None


# --- successful generation -----------------------------------------------------


def test_generate_returns_completion_text():
    client = _FakeClient(completion=_FakeCompletion("Here is your grounded answer."))
    provider = GroqProvider(_settings(), client=client)

    result = provider.generate("system prompt", "user prompt")

    assert result == "Here is your grounded answer."


def test_generate_passes_model_and_messages_to_client():
    client = _FakeClient(completion=_FakeCompletion("ok"))
    provider = GroqProvider(_settings(), client=client)

    provider.generate("system prompt", "user prompt")

    kwargs = client.chat.completions.last_kwargs
    assert kwargs["model"] == MODEL_NAME
    assert kwargs["messages"] == [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "user prompt"},
    ]


def test_generate_strips_whitespace_from_completion():
    client = _FakeClient(completion=_FakeCompletion("  padded response  \n"))
    provider = GroqProvider(_settings(), client=client)

    assert provider.generate("system", "user") == "padded response"


def test_client_is_created_once_and_reused(monkeypatch):
    created = []

    class _TrackedClient(_FakeClient):
        def __init__(self, *args, **kwargs):
            super().__init__(completion=_FakeCompletion("ok"))
            created.append(1)

    monkeypatch.setattr(groq, "Groq", _TrackedClient)
    provider = GroqProvider(_settings())

    provider.generate("system", "user")
    provider.generate("system", "user")

    assert len(created) == 1


# --- empty / missing response handling -----------------------------------------


def test_generate_raises_llm_error_on_no_choices():
    client = _FakeClient(completion=_FakeCompletion(None))
    provider = GroqProvider(_settings(), client=client)

    with pytest.raises(LLMError, match="empty response"):
        provider.generate("system", "user")


def test_generate_raises_llm_error_on_blank_content():
    client = _FakeClient(completion=_FakeCompletion("   "))
    provider = GroqProvider(_settings(), client=client)

    with pytest.raises(LLMError, match="empty response"):
        provider.generate("system", "user")


# --- Groq SDK error mapping -----------------------------------------------------


def test_generate_wraps_timeout_error():
    error = groq.APITimeoutError(request=_request())
    client = _FakeClient(error=error)
    provider = GroqProvider(_settings(), client=client)

    with pytest.raises(LLMError, match="timed out"):
        provider.generate("system", "user")


def test_generate_wraps_rate_limit_error():
    error = groq.RateLimitError("rate limited", response=_response(429), body=None)
    client = _FakeClient(error=error)
    provider = GroqProvider(_settings(), client=client)

    with pytest.raises(LLMError, match="rate limit"):
        provider.generate("system", "user")


def test_generate_wraps_authentication_error():
    error = groq.AuthenticationError("bad key", response=_response(401), body=None)
    client = _FakeClient(error=error)
    provider = GroqProvider(_settings(), client=client)

    with pytest.raises(LLMError, match="authentication failed"):
        provider.generate("system", "user")


def test_generate_wraps_connection_error():
    error = groq.APIConnectionError(request=_request())
    client = _FakeClient(error=error)
    provider = GroqProvider(_settings(), client=client)

    with pytest.raises(LLMError, match="unreachable"):
        provider.generate("system", "user")


def test_generate_error_message_never_contains_api_key():
    error = groq.AuthenticationError(
        "Invalid API Key: test-key", response=_response(401), body=None
    )
    client = _FakeClient(error=error)
    provider = GroqProvider(_settings(GROQ_API_KEY="test-key"), client=client)

    with pytest.raises(LLMError) as excinfo:
        provider.generate("system", "user")

    assert "test-key" not in str(excinfo.value)


def test_generate_wraps_generic_api_error():
    error = groq.APIError("boom", request=_request(), body=None)
    client = _FakeClient(error=error)
    provider = GroqProvider(_settings(), client=client)

    with pytest.raises(LLMError, match="Groq request failed"):
        provider.generate("system", "user")

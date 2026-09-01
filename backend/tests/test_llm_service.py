"""Phase 11 LLM service tests.

Unit tests only: the Groq provider is a fake object, so nothing here makes
a real network call or requires a GROQ_API_KEY (docs/llm/GROQ_SPEC.md
"Testing").
"""

from __future__ import annotations

import uuid

import pytest

from app.core.errors import LLMError
from app.services.langchain_pipeline.pipeline import GroundedPrompt
from app.services.llm.service import PROVIDER_NAME, GroundedResponse, LLMService
from app.services.retrieval.service import RetrievedChunk


class _FakeProvider:
    def __init__(
        self,
        response: str = "Here is your grounded answer.",
        error: Exception | None = None,
    ):
        self.model_name = "openai/gpt-oss-20b"
        self._response = response
        self._error = error
        self.calls: list[tuple[str, str, str | None]] = []

    def generate(self, system_prompt: str, user_prompt: str, *, request_id=None, **kwargs):
        self.calls.append((system_prompt, user_prompt, request_id))
        if self._error is not None:
            raise self._error
        return self._response


def _source() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        source_id="refund_policy.md",
        title="Refund Policy",
        category="refund",
        version="v1",
        chunk_index=0,
        content="Refunds are issued within 5 business days.",
        content_hash="abc123",
        score=0.9,
        rank=1,
    )


def _grounded_prompt(**overrides) -> GroundedPrompt:
    defaults = dict(
        system_prompt="system instructions",
        user_prompt="Customer complaint: Where is my refund?",
        prompt_version="grounded-support-v1",
        sources=[_source()],
        documents=[],
        has_context=True,
    )
    defaults.update(overrides)
    return GroundedPrompt(**defaults)


def test_generate_response_returns_clean_grounded_response():
    provider = _FakeProvider(response="Refunds take 5 business days.")
    service = LLMService(provider=provider)
    prompt = _grounded_prompt()

    result = service.generate_response(prompt)

    assert isinstance(result, GroundedResponse)
    assert result.response == "Refunds take 5 business days."
    assert result.provider == PROVIDER_NAME
    assert result.model == "openai/gpt-oss-20b"
    assert result.prompt_version == "grounded-support-v1"


def test_generate_response_preserves_sources_and_metadata():
    provider = _FakeProvider()
    service = LLMService(provider=provider)
    prompt = _grounded_prompt()

    result = service.generate_response(prompt)

    assert result.sources == prompt.sources
    assert result.has_context is True
    assert result.sources[0].source_id == "refund_policy.md"


def test_generate_response_no_context_case_still_generates():
    provider = _FakeProvider(
        response="The knowledge base does not have enough information to answer this."
    )
    service = LLMService(provider=provider)
    prompt = _grounded_prompt(sources=[], has_context=False)

    result = service.generate_response(prompt)

    assert result.has_context is False
    assert result.sources == []
    assert "does not have enough information" in result.response


def test_generate_response_passes_prompts_and_request_id_to_provider():
    provider = _FakeProvider()
    service = LLMService(provider=provider)
    prompt = _grounded_prompt(
        system_prompt="SYSTEM", user_prompt="USER", sources=[], has_context=False
    )

    service.generate_response(prompt, request_id="req-123")

    assert provider.calls == [("SYSTEM", "USER", "req-123")]


def test_generate_response_propagates_provider_errors():
    provider = _FakeProvider(error=LLMError("Groq request failed."))
    service = LLMService(provider=provider)

    with pytest.raises(LLMError):
        service.generate_response(_grounded_prompt())

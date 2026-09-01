"""Phase 11 LLM generation service.

Flow (docs/langchain/LANGCHAIN_PIPELINE_SPEC.md):

    Phase 10 GroundedPrompt -> GroqProvider.generate -> GroundedResponse

Connects the Phase 10 grounded prompt to the Groq provider abstraction
(docs/backend/BACKEND_SPEC.md "LLMService: Calls the configured Groq
adapter") and returns a clean response that still carries the retrieved
sources, so callers (a later persistence/API phase) can store
`generated_responses` and `retrieved_sources` without re-deriving them
(DATABASE.md). Does not call the Groq SDK directly -- that stays behind
GroqProvider -- and does not persist anything or expose a FastAPI route;
those are later phases.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.providers.groq_provider import GroqProvider, get_groq_provider
from app.services.langchain_pipeline.pipeline import GroundedPrompt
from app.services.retrieval.service import RetrievedChunk

PROVIDER_NAME = "groq"


@dataclass(frozen=True)
class GroundedResponse:
    """A generated response plus everything needed to persist/return it.

    Mirrors the `generated_responses` columns (provider, model,
    prompt_version, response) and keeps `sources`/`has_context` so callers
    can persist `retrieved_sources` and know whether the answer was grounded
    (DATABASE.md, docs/rag/RAG_SPEC.md "Grounding").
    """

    response: str
    provider: str
    model: str
    prompt_version: str
    sources: list[RetrievedChunk]
    has_context: bool


class LLMService:
    """Calls the configured Groq adapter with a grounded prompt."""

    def __init__(self, provider: GroqProvider | None = None):
        self._provider = provider or get_groq_provider()

    def generate_response(
        self, grounded_prompt: GroundedPrompt, request_id: str | None = None
    ) -> GroundedResponse:
        """Generate a grounded response for `grounded_prompt`.

        Raises `LLMError` (via GroqProvider) on missing configuration,
        timeout, rate limit, or any other provider failure -- this method
        adds no error handling of its own.
        """
        text = self._provider.generate(
            grounded_prompt.system_prompt,
            grounded_prompt.user_prompt,
            request_id=request_id,
        )
        return GroundedResponse(
            response=text,
            provider=PROVIDER_NAME,
            model=self._provider.model_name,
            prompt_version=grounded_prompt.prompt_version,
            sources=grounded_prompt.sources,
            has_context=grounded_prompt.has_context,
        )

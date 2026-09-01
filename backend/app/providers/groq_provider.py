"""Groq LLM provider (Phase 11).

Wraps the Groq chat completion API behind a minimal `generate()` interface
(docs/llm/GROQ_SPEC.md "Provider abstraction") so the rest of the
application never depends on Groq SDK objects directly. Consumes the
Phase 10 grounded prompt (system_prompt/user_prompt); does not build
prompts or run retrieval itself.

GROQ_API_KEY and GROQ_MODEL are read from Settings only, never
hard-coded (docs/llm/GROQ_SPEC.md, REQUIREMENTS.md "LLM").
"""

from __future__ import annotations

import logging

import groq

from app.core.config import Settings, get_settings
from app.core.errors import LLMError

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 1024


class GroqProvider:
    """Generates grounded chat completions through Groq.

    The Groq client is lazily created and validated on first use, so
    importing this module (or constructing this class) never requires
    GROQ_API_KEY to be set. Tests inject a fake `client` instead of calling
    the real Groq API (docs/llm/GROQ_SPEC.md "Testing").

    Transient failures (rate limits, connection errors, 5xx) are retried by
    the underlying Groq SDK via `max_retries`
    (docs/llm/GROQ_SPEC.md "Runtime": timeout, retry policy, rate-limit
    handling) rather than a hand-rolled retry loop here.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        client: groq.Groq | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self._settings = settings or get_settings()
        self._client = client
        self._timeout = timeout
        self._max_retries = max_retries

    @property
    def model_name(self) -> str:
        return self._settings.GROQ_MODEL

    def _get_client(self) -> groq.Groq:
        if self._client is not None:
            return self._client

        if not self._settings.GROQ_API_KEY:
            raise LLMError("GROQ_API_KEY is not configured.")
        if not self.model_name:
            raise LLMError("GROQ_MODEL is not configured.")

        self._client = groq.Groq(
            api_key=self._settings.GROQ_API_KEY,
            timeout=self._timeout,
            max_retries=self._max_retries,
        )
        return self._client

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        request_id: str | None = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> str:
        """Send a grounded system/user prompt pair to Groq and return the text.

        Raises `LLMError` (never a raw Groq SDK exception) for missing
        configuration, an empty prompt, a timeout, a rate limit, an
        authentication failure, a connection failure, any other API error,
        or an empty completion.
        """
        if not system_prompt.strip() or not user_prompt.strip():
            raise LLMError("Prompt must not be empty.")

        client = self._get_client()

        logger.info(
            "groq_generate_request",
            extra={"request_id": request_id, "model": self.model_name},
        )

        try:
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except groq.GroqError as exc:
            logger.error(
                "groq_generate_failed",
                extra={
                    "request_id": request_id,
                    "model": self.model_name,
                    "error_type": exc.__class__.__name__,
                    "error_detail": str(exc),
                },
            )
            raise LLMError(_safe_error_message(exc)) from exc

        text = _extract_text(completion)
        if not text:
            logger.error(
                "groq_generate_empty_response",
                extra={"request_id": request_id, "model": self.model_name},
            )
            raise LLMError("Groq returned an empty response.")

        logger.info(
            "groq_generate_success",
            extra={"request_id": request_id, "model": self.model_name},
        )
        return text


def _extract_text(completion: object) -> str:
    choices = getattr(completion, "choices", None) or []
    if not choices:
        return ""
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None) if message is not None else None
    return (content or "").strip()


def _safe_error_message(exc: groq.GroqError) -> str:
    """Map a Groq SDK exception to a safe, non-leaking user-facing message.

    Never includes the raw exception text: it may echo request details and
    must not reach the frontend (docs/backend/ERROR_HANDLING_SPEC.md "Do not
    expose ... API keys ... provider secrets"). Full detail is logged
    server-side above instead.
    """
    if isinstance(exc, groq.APITimeoutError):
        return "The Groq request timed out. Please try again."
    if isinstance(exc, groq.RateLimitError):
        return "Groq rate limit exceeded. Please try again shortly."
    if isinstance(exc, groq.AuthenticationError):
        return "Groq authentication failed."
    if isinstance(exc, groq.APIConnectionError):
        return "Groq API is unreachable."
    return "Groq request failed."


_provider: GroqProvider | None = None


def get_groq_provider() -> GroqProvider:
    global _provider
    if _provider is None:
        _provider = GroqProvider()
    return _provider

"""LangChain RAG orchestration pipeline (Phase 10).

Flow (docs/langchain/LANGCHAIN_PIPELINE_SPEC.md):

    User query -> RAGRetriever -> retrieved chunks -> LangChain Documents ->
    grounded prompt template -> GroundedPrompt (prompt + normalized sources)

Does not call Groq or any LLM provider; Phase 11 owns generation. Does not
implement a FastAPI route or persistence; those are later phases.
"""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.documents import Document

from app.services.langchain_pipeline.documents import chunks_to_documents
from app.services.langchain_pipeline.prompt import (
    GROUNDED_PROMPT_TEMPLATE,
    PROMPT_VERSION,
    format_context,
)
from app.services.langchain_pipeline.retriever import RAGRetriever
from app.services.retrieval.service import RetrievedChunk


@dataclass(frozen=True)
class GroundedPrompt:
    """A fully assembled, LLM-provider-agnostic grounded prompt plus its sources."""

    system_prompt: str
    user_prompt: str
    prompt_version: str
    sources: list[RetrievedChunk]
    documents: list[Document]
    has_context: bool


def build_grounded_prompt(
    retriever: RAGRetriever,
    complaint: str,
    intent: str,
    sentiment: str,
    priority: str,
    filters: dict[str, str] | None = None,
    k: int | None = None,
) -> GroundedPrompt:
    """Retrieve knowledge for `complaint` and render it into a grounded prompt.

    The complaint text is used verbatim as the retrieval query; query
    rewriting is an explicitly deferred post-MVP enhancement
    (docs/langchain/LANGCHAIN_PIPELINE_SPEC.md "Optional later").
    """
    sources = retriever.retrieve(complaint, filters=filters, k=k)
    documents = chunks_to_documents(sources)

    prompt_value = GROUNDED_PROMPT_TEMPLATE.invoke(
        {
            "prompt_version": PROMPT_VERSION,
            "intent": intent,
            "sentiment": sentiment,
            "priority": priority,
            "complaint": complaint,
            "context": format_context(documents),
        }
    )
    system_message, human_message = prompt_value.to_messages()

    return GroundedPrompt(
        system_prompt=system_message.content,
        user_prompt=human_message.content,
        prompt_version=PROMPT_VERSION,
        sources=sources,
        documents=documents,
        has_context=bool(sources),
    )

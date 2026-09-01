"""Phase 12 complaint analysis orchestrator.

docs/backend/BACKEND_SPEC.md: "ComplaintAnalysisService: Coordinates intent,
sentiment, priority, RAG, LLM, persistence."

Flow (docs/architecture/SYSTEM_ARCHITECTURE.md "Runtime complaint pipeline"):
complaint -> intent -> sentiment -> priority -> RAG retrieval -> grounded
prompt -> Groq -> persistence -> structured result. Reuses every Phase
06-11 building block (IntentService, SentimentService, PriorityService,
RAGRetriever/build_grounded_prompt, LLMService) rather than reimplementing
any of them.

Failure boundaries (same doc, "Failure boundaries"):
- intent/sentiment model failure -> propagate ModelUnavailableError (503);
  do not guess a result.
- retrieval failure (embedding model down, etc.) -> propagate
  RetrievalError/ModelUnavailableError; never hallucinate context. Note this
  is distinct from "insufficient context" (zero matches), which RAGService
  already returns as an empty list rather than raising, and which the
  grounded prompt already states explicitly to the LLM
  (docs/rag/RAG_SPEC.md "Grounding").
- Groq failure -> the complaint/analysis/retrieved_sources are still
  persisted and returned; only the generated response is omitted
  (`suggested_response = None`, `llm_available = False`).
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.errors import LLMError
from app.models.analysis import Analysis
from app.models.complaint import Complaint
from app.models.generated_response import GeneratedResponse
from app.models.retrieved_source import RetrievedSource
from app.providers.embedding_provider import get_embedding_provider
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.generated_response_repository import GeneratedResponseRepository
from app.repositories.retrieved_source_repository import RetrievedSourceRepository
from app.services.intent.service import IntentService, get_intent_service
from app.services.langchain_pipeline.pipeline import build_grounded_prompt
from app.services.langchain_pipeline.retriever import RAGRetriever
from app.services.llm.service import LLMService
from app.services.priority.service import PriorityResult, PriorityService
from app.services.retrieval.service import RAGService, RetrievedChunk
from app.services.sentiment.service import SentimentService, get_sentiment_service

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ComplaintAnalysisResult:
    complaint_id: uuid.UUID
    intent_label: str
    intent_confidence: float
    intent_model_version: str
    sentiment_label: str
    sentiment_confidence: float
    priority: PriorityResult
    sources: list[RetrievedChunk]
    suggested_response: str | None
    llm_provider: str | None
    llm_model: str | None
    prompt_version: str
    llm_available: bool
    embedding_model: str


class ComplaintAnalysisService:
    """Coordinates classification, retrieval, generation, and persistence for one complaint."""

    def __init__(
        self,
        db: Session,
        settings: Settings | None = None,
        intent_service: IntentService | None = None,
        sentiment_service: SentimentService | None = None,
        priority_service: PriorityService | None = None,
        rag_service: RAGService | None = None,
        llm_service: LLMService | None = None,
    ):
        self._db = db
        self._settings = settings or get_settings()
        self._intent_service = intent_service or get_intent_service()
        self._sentiment_service = sentiment_service or get_sentiment_service()
        self._priority_service = priority_service or PriorityService()
        self._rag_service = rag_service or RAGService(db, settings=self._settings)
        self._llm_service = llm_service or LLMService()

    def analyze(self, text: str, request_id: str | None = None) -> ComplaintAnalysisResult:
        text = text.strip()

        intent = self._intent_service.predict_intent(text)
        sentiment = self._sentiment_service.analyze_sentiment(text)
        priority = self._priority_service.determine_priority(intent.label, sentiment.label)
        intent_model_version = f"{intent.model_name}-{intent.model_version}"

        retriever = RAGRetriever(self._rag_service)
        grounded_prompt = build_grounded_prompt(
            retriever, text, intent.label, sentiment.label, priority.level
        )

        suggested_response: str | None = None
        llm_provider: str | None = None
        llm_model: str | None = None
        llm_available = True
        generated_response: str | None = None
        try:
            generated = self._llm_service.generate_response(
                grounded_prompt, request_id=request_id
            )
            suggested_response = generated.response
            llm_provider = generated.provider
            llm_model = generated.model
            generated_response = generated.response
        except LLMError as exc:
            llm_available = False
            logger.error(
                "complaint_analysis_llm_failed",
                extra={"request_id": request_id, "error": str(exc)},
            )

        complaint = ComplaintRepository(self._db).add(Complaint(text=text))

        analysis = AnalysisRepository(self._db).add(
            Analysis(
                complaint_id=complaint.id,
                intent=intent.label,
                intent_confidence=intent.confidence,
                sentiment=sentiment.label,
                sentiment_confidence=sentiment.confidence,
                priority=priority.level,
                priority_reason=priority.reason,
                intent_model_version=intent_model_version,
            )
        )

        source_repo = RetrievedSourceRepository(self._db)
        for source in grounded_prompt.sources:
            source_repo.add(
                RetrievedSource(
                    analysis_id=analysis.id,
                    chunk_id=source.chunk_id,
                    retrieval_score=source.score,
                    rank=source.rank,
                )
            )

        if generated_response is not None:
            GeneratedResponseRepository(self._db).add(
                GeneratedResponse(
                    analysis_id=analysis.id,
                    provider=llm_provider,
                    model=llm_model,
                    prompt_version=grounded_prompt.prompt_version,
                    response=generated_response,
                )
            )

        self._db.commit()

        return ComplaintAnalysisResult(
            complaint_id=complaint.id,
            intent_label=intent.label,
            intent_confidence=intent.confidence,
            intent_model_version=intent_model_version,
            sentiment_label=sentiment.label,
            sentiment_confidence=sentiment.confidence,
            priority=priority,
            sources=grounded_prompt.sources,
            suggested_response=suggested_response,
            llm_provider=llm_provider,
            llm_model=llm_model,
            prompt_version=grounded_prompt.prompt_version,
            llm_available=llm_available,
            embedding_model=get_embedding_provider().model_name,
        )

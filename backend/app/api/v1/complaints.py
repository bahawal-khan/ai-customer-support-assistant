"""docs/api/API_SPEC.md: POST /complaints/analyze, GET /complaints, GET /complaints/{id}.

Routes validate (via Pydantic schemas) and delegate; they contain no SQL and
no ML/RAG/LLM orchestration (docs/backend/BACKEND_SPEC.md "Rules": "API
layer must not contain ML code" / "must not contain SQL queries" / "Routes
call services").
"""

from __future__ import annotations

import math
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import NotFoundError, get_request_id
from app.models.retrieved_source import RetrievedSource
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.generated_response_repository import GeneratedResponseRepository
from app.repositories.retrieved_source_repository import RetrievedSourceRepository
from app.schemas.complaint import (
    ComplaintAnalyzeRequest,
    ComplaintAnalyzeResponse,
    ComplaintBulkDeleteRequest,
    ComplaintBulkDeleteResponse,
    ComplaintDetailResponse,
    ComplaintHistoryItem,
    IntentResult,
    ModelMetadata,
    PaginatedComplaints,
    PriorityResultOut,
    RetrievedSourceOut,
    SentimentResult,
)
from app.services.complaint_analysis.service import ComplaintAnalysisService
from app.services.complaint_management.service import ComplaintManagementService
from app.services.retrieval.service import RetrievedChunk

router = APIRouter()


def _sources_out(sources: list[RetrievedChunk]) -> list[RetrievedSourceOut]:
    return [
        RetrievedSourceOut(
            chunk_id=s.chunk_id,
            document_id=s.document_id,
            source_id=s.source_id,
            title=s.title,
            category=s.category,
            version=s.version,
            chunk_index=s.chunk_index,
            content=s.content,
            score=s.score,
            rank=s.rank,
        )
        for s in sources
    ]


@router.post("/complaints/analyze", response_model=ComplaintAnalyzeResponse)
def analyze_complaint(
    payload: ComplaintAnalyzeRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ComplaintAnalyzeResponse:
    request_id = get_request_id(request)
    result = ComplaintAnalysisService(db).analyze(payload.text, request_id=request_id)

    return ComplaintAnalyzeResponse(
        request_id=request_id,
        complaint_id=result.complaint_id,
        intent=IntentResult(
            label=result.intent_label,
            confidence=result.intent_confidence,
            model_version=result.intent_model_version,
        ),
        sentiment=SentimentResult(
            label=result.sentiment_label, confidence=result.sentiment_confidence
        ),
        priority=PriorityResultOut(level=result.priority.level, reason=result.priority.reason),
        retrieved_sources=_sources_out(result.sources),
        suggested_response=result.suggested_response,
        model_metadata=ModelMetadata(
            intent_model_version=result.intent_model_version,
            embedding_model=result.embedding_model,
            llm_provider=result.llm_provider,
            llm_model=result.llm_model,
            prompt_version=result.prompt_version,
            retrieved_source_count=len(result.sources),
            llm_available=result.llm_available,
        ),
    )


@router.get("/complaints", response_model=PaginatedComplaints)
def list_complaints(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    intent: str | None = Query(None),
    priority: str | None = Query(None),
    sentiment: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
) -> PaginatedComplaints:
    rows, total = AnalysisRepository(db).list_with_filters(
        page=page,
        page_size=page_size,
        search=search,
        intent=intent,
        priority=priority,
        sentiment=sentiment,
        date_from=date_from,
        date_to=date_to,
    )
    items = [
        ComplaintHistoryItem(
            complaint_id=complaint.id,
            text=complaint.text,
            intent=analysis.intent,
            intent_confidence=analysis.intent_confidence,
            sentiment=analysis.sentiment,
            sentiment_confidence=analysis.sentiment_confidence,
            priority=analysis.priority,
            created_at=complaint.created_at,
        )
        for analysis, complaint in rows
    ]
    total_pages = math.ceil(total / page_size) if total else 0
    return PaginatedComplaints(
        items=items, page=page, page_size=page_size, total=total, total_pages=total_pages
    )


@router.delete("/complaints", response_model=ComplaintBulkDeleteResponse)
def delete_complaints(
    payload: ComplaintBulkDeleteRequest, db: Session = Depends(get_db)
) -> ComplaintBulkDeleteResponse:
    deleted_ids = ComplaintManagementService(db).bulk_delete(payload.complaint_ids)
    return ComplaintBulkDeleteResponse(deleted_ids=deleted_ids)


def _retrieved_source_out(source: RetrievedSource) -> RetrievedSourceOut:
    """Reconstruct traceable source metadata by joining through the stored chunk.

    `retrieved_sources` only stores (chunk_id, retrieval_score, rank) per
    docs/database/DATABASE_SPEC.md; title/category/source_id etc. live on
    the chunk's `chunk_metadata` JSONB (docs/rag/RAG_SPEC.md "Chunk
    metadata"). `chunk` can be None if the chunk was later deleted
    (`ondelete="SET NULL"`, app/models/retrieved_source.py).
    """
    chunk = source.chunk
    metadata = (chunk.chunk_metadata or {}) if chunk else {}
    return RetrievedSourceOut(
        chunk_id=source.chunk_id,
        document_id=chunk.document_id if chunk else None,
        source_id=metadata.get("source_id", ""),
        title=metadata.get("title", ""),
        category=metadata.get("category", ""),
        version=metadata.get("version", ""),
        chunk_index=chunk.chunk_index if chunk else 0,
        content=chunk.content if chunk else "",
        score=source.retrieval_score,
        rank=source.rank,
    )


@router.get("/complaints/{complaint_id}", response_model=ComplaintDetailResponse)
def get_complaint(
    complaint_id: uuid.UUID, db: Session = Depends(get_db)
) -> ComplaintDetailResponse:
    complaint = ComplaintRepository(db).get(complaint_id)
    if complaint is None:
        raise NotFoundError(f"Complaint '{complaint_id}' was not found.")

    analysis = AnalysisRepository(db).get_by_complaint_id(complaint_id)
    if analysis is None:
        raise NotFoundError(f"No analysis found for complaint '{complaint_id}'.")

    sources = RetrievedSourceRepository(db).list_by_analysis(analysis.id)
    generated = GeneratedResponseRepository(db).get_by_analysis_id(analysis.id)

    retrieved_sources = [_retrieved_source_out(source) for source in sources]

    return ComplaintDetailResponse(
        complaint_id=complaint.id,
        text=complaint.text,
        created_at=complaint.created_at,
        intent=IntentResult(
            label=analysis.intent,
            confidence=analysis.intent_confidence,
            model_version=analysis.intent_model_version,
        ),
        sentiment=SentimentResult(
            label=analysis.sentiment, confidence=analysis.sentiment_confidence
        ),
        priority=PriorityResultOut(level=analysis.priority, reason=analysis.priority_reason),
        retrieved_sources=retrieved_sources,
        suggested_response=generated.response if generated else None,
        model_metadata=ModelMetadata(
            intent_model_version=analysis.intent_model_version,
            embedding_model=get_settings().EMBEDDING_MODEL,
            llm_provider=generated.provider if generated else None,
            llm_model=generated.model if generated else None,
            prompt_version=generated.prompt_version if generated else None,
            retrieved_source_count=len(retrieved_sources),
            llm_available=generated is not None,
        ),
    )

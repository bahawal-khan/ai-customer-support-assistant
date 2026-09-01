"""Phase 12 Pydantic schemas for docs/api/API_SPEC.md's complaint endpoints.

Kept separate from the SQLAlchemy models in app/models/ per
docs/database/DATABASE_SPEC.md ("SQLAlchemy models are separate from
Pydantic schemas.") and docs/api/API_SPEC.md ("no ORM objects directly in
responses.").
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.core.config import get_settings


class ComplaintAnalyzeRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def _validate_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Complaint text must not be empty.")
        max_length = get_settings().MAX_COMPLAINT_LENGTH
        if len(stripped) > max_length:
            raise ValueError(f"Complaint text must not exceed {max_length} characters.")
        return stripped


class IntentResult(BaseModel):
    label: str
    confidence: float
    model_version: str


class SentimentResult(BaseModel):
    label: str
    confidence: float


class PriorityResultOut(BaseModel):
    level: str
    reason: str


class RetrievedSourceOut(BaseModel):
    chunk_id: uuid.UUID | None
    document_id: uuid.UUID | None
    source_id: str
    title: str
    category: str
    version: str
    chunk_index: int
    content: str
    score: float
    rank: int


class ModelMetadata(BaseModel):
    intent_model_version: str
    embedding_model: str
    llm_provider: str | None
    llm_model: str | None
    prompt_version: str | None
    retrieved_source_count: int
    llm_available: bool


class ComplaintAnalyzeResponse(BaseModel):
    request_id: str
    complaint_id: uuid.UUID
    intent: IntentResult
    sentiment: SentimentResult
    priority: PriorityResultOut
    retrieved_sources: list[RetrievedSourceOut]
    suggested_response: str | None
    model_metadata: ModelMetadata


class ComplaintDetailResponse(BaseModel):
    complaint_id: uuid.UUID
    text: str
    created_at: datetime
    intent: IntentResult
    sentiment: SentimentResult
    priority: PriorityResultOut
    retrieved_sources: list[RetrievedSourceOut]
    suggested_response: str | None
    model_metadata: ModelMetadata


class ComplaintHistoryItem(BaseModel):
    complaint_id: uuid.UUID
    text: str
    intent: str
    intent_confidence: float
    sentiment: str
    sentiment_confidence: float
    priority: str
    created_at: datetime


class PaginatedComplaints(BaseModel):
    items: list[ComplaintHistoryItem]
    page: int
    page_size: int
    total: int
    total_pages: int


class ComplaintBulkDeleteRequest(BaseModel):
    complaint_ids: list[uuid.UUID]

    @field_validator("complaint_ids")
    @classmethod
    def _validate_complaint_ids(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if not value:
            raise ValueError("At least one complaint ID must be provided.")
        return value


class ComplaintBulkDeleteResponse(BaseModel):
    deleted_ids: list[uuid.UUID]

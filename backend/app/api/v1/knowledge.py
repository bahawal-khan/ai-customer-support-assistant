"""docs/api/API_SPEC.md: knowledge document management endpoints.

Routes validate and delegate to KnowledgeService; no SQL or ingestion logic
lives here (docs/backend/BACKEND_SPEC.md "Rules").
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.knowledge import (
    DocumentDeleteResponse,
    DocumentIndexResponse,
    DocumentListResponse,
    DocumentOut,
)
from app.services.knowledge.service import KnowledgeService

router = APIRouter()


def _document_out(document: Document, chunk_count: int = 0) -> DocumentOut:
    return DocumentOut(
        id=document.id,
        source_id=document.source_id,
        title=document.title,
        category=document.category,
        version=document.version,
        status=document.status,
        created_at=document.created_at,
        updated_at=document.updated_at,
        chunk_count=chunk_count,
    )


@router.post("/knowledge/documents", response_model=DocumentOut, status_code=201)
async def create_document(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> DocumentOut:
    content = await file.read()
    document = KnowledgeService(db).upload_document(file.filename, file.content_type, content)
    return _document_out(document)


@router.get("/knowledge/documents", response_model=DocumentListResponse)
def list_documents(db: Session = Depends(get_db)) -> DocumentListResponse:
    rows = DocumentRepository(db).list_with_chunk_counts(limit=200)
    return DocumentListResponse(
        items=[_document_out(d, chunk_count=c) for d, c in rows], total=len(rows)
    )


@router.post("/knowledge/documents/{document_id}/index", response_model=DocumentIndexResponse)
def index_document(
    document_id: uuid.UUID, db: Session = Depends(get_db)
) -> DocumentIndexResponse:
    outcome = KnowledgeService(db).index_document(document_id)
    return DocumentIndexResponse(
        document_id=outcome.document_id,
        source_id=outcome.source_id,
        action=outcome.action,
        chunk_count=outcome.chunk_count,
        status=outcome.status,
    )


@router.delete("/knowledge/documents/{document_id}", response_model=DocumentDeleteResponse)
def delete_document(
    document_id: uuid.UUID, db: Session = Depends(get_db)
) -> DocumentDeleteResponse:
    KnowledgeService(db).delete_document(document_id)
    return DocumentDeleteResponse(document_id=document_id, deleted=True)

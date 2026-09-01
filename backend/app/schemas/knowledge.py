from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: uuid.UUID
    source_id: str
    title: str
    category: str
    version: str
    status: str
    created_at: datetime
    updated_at: datetime
    chunk_count: int


class DocumentListResponse(BaseModel):
    items: list[DocumentOut]
    total: int


class DocumentIndexResponse(BaseModel):
    document_id: uuid.UUID
    source_id: str
    action: str
    chunk_count: int
    status: str


class DocumentDeleteResponse(BaseModel):
    document_id: uuid.UUID
    deleted: bool

"""docs/api/API_SPEC.md: GET /health -- application status, database status, version."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import check_connection, get_db
from app.schemas.health import HealthResponse

router = APIRouter()

APP_VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)) -> HealthResponse:
    database_status = "ok" if check_connection(db) else "unavailable"

    return HealthResponse(status="ok", database=database_status, version=APP_VERSION)

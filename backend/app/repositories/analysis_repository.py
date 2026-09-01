import uuid
from datetime import datetime

from sqlalchemy import func, select

from app.models.analysis import Analysis
from app.models.complaint import Complaint
from app.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository[Analysis]):
    model = Analysis

    def get_by_complaint_id(self, complaint_id: uuid.UUID) -> Analysis | None:
        stmt = select(Analysis).where(Analysis.complaint_id == complaint_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_with_filters(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        intent: str | None = None,
        priority: str | None = None,
        sentiment: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[tuple[Analysis, Complaint]], int]:
        """Paginated `complaints` history joined with its `analyses` row.

        Ordered newest first by complaint submission time. Returns
        `(rows, total_matching_count)`, where `rows` is one page of
        `(analysis, complaint)` pairs.
        """
        stmt = select(Analysis, Complaint).join(Complaint, Analysis.complaint_id == Complaint.id)
        if search:
            stmt = stmt.where(Complaint.text.ilike(f"%{search}%"))
        if intent:
            stmt = stmt.where(Analysis.intent == intent)
        if priority:
            stmt = stmt.where(Analysis.priority == priority)
        if sentiment:
            stmt = stmt.where(Analysis.sentiment == sentiment)
        if date_from:
            stmt = stmt.where(Complaint.created_at >= date_from)
        if date_to:
            stmt = stmt.where(Complaint.created_at <= date_to)

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

        stmt = (
            stmt.order_by(Complaint.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        rows = [(row[0], row[1]) for row in self.db.execute(stmt).all()]
        return rows, total

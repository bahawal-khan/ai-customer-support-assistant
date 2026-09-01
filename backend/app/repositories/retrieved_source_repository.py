import uuid

from sqlalchemy import select

from app.models.retrieved_source import RetrievedSource
from app.repositories.base import BaseRepository


class RetrievedSourceRepository(BaseRepository[RetrievedSource]):
    model = RetrievedSource

    def list_by_analysis(self, analysis_id: uuid.UUID) -> list[RetrievedSource]:
        stmt = (
            select(RetrievedSource)
            .where(RetrievedSource.analysis_id == analysis_id)
            .order_by(RetrievedSource.rank)
        )
        return list(self.db.execute(stmt).scalars().all())

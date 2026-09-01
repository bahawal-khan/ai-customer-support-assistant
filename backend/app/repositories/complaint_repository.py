import uuid

from sqlalchemy import select

from app.models.complaint import Complaint
from app.repositories.base import BaseRepository


class ComplaintRepository(BaseRepository[Complaint]):
    model = Complaint

    def list_by_ids(self, ids: list[uuid.UUID]) -> list[Complaint]:
        stmt = select(Complaint).where(Complaint.id.in_(ids))
        return list(self.db.execute(stmt).scalars().all())

import uuid

from sqlalchemy import select

from app.models.generated_response import GeneratedResponse
from app.repositories.base import BaseRepository


class GeneratedResponseRepository(BaseRepository[GeneratedResponse]):
    model = GeneratedResponse

    def get_by_analysis_id(self, analysis_id: uuid.UUID) -> GeneratedResponse | None:
        stmt = select(GeneratedResponse).where(GeneratedResponse.analysis_id == analysis_id)
        return self.db.execute(stmt).scalar_one_or_none()

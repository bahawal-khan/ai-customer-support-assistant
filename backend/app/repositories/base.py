import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, db: Session):
        self.db = db

    def add(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def get(self, id_: uuid.UUID) -> ModelType | None:
        return self.db.get(self.model, id_)

    def list(self, limit: int = 50, offset: int = 0) -> list[ModelType]:
        stmt = select(self.model).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def delete(self, instance: ModelType) -> None:
        self.db.delete(instance)
        self.db.flush()

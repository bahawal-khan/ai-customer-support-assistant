from sqlalchemy import func, select

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    model = Document

    def get_by_source_id(self, source_id: str) -> Document | None:
        stmt = select(Document).where(Document.source_id == source_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_category(self, category: str) -> list[Document]:
        stmt = select(Document).where(Document.category == category)
        return list(self.db.execute(stmt).scalars().all())

    def list_with_chunk_counts(
        self, limit: int = 50, offset: int = 0
    ) -> list[tuple[Document, int]]:
        """Like `list()`, but paired with each document's chunk count via a
        correlated subquery (one query, not N+1 lazy-loads of `.chunks`)."""
        chunk_count = (
            select(func.count(DocumentChunk.id))
            .where(DocumentChunk.document_id == Document.id)
            .correlate(Document)
            .scalar_subquery()
        )
        stmt = select(Document, chunk_count).limit(limit).offset(offset)
        return [(doc, count) for doc, count in self.db.execute(stmt).all()]

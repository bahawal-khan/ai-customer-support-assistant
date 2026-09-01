import uuid

from sqlalchemy import select

from app.models.document_chunk import DocumentChunk
from app.repositories.base import BaseRepository


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    model = DocumentChunk

    def list_by_document(self, document_id: uuid.UUID) -> list[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(self.db.execute(stmt).scalars().all())

    def similarity_search(
        self, query_embedding: list[float], top_k: int = 5
    ) -> list[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        return list(self.db.execute(stmt).scalars().all())

    def similarity_search_with_scores(
        self, query_embedding: list[float], top_k: int = 5
    ) -> list[tuple[DocumentChunk, float]]:
        """Return the top_k nearest chunks paired with their cosine similarity score.

        pgvector's `cosine_distance` is `1 - cosine_similarity`, so similarity is
        derived as `1 - distance` (higher is more similar).
        """
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(DocumentChunk, distance.label("distance"))
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance)
            .limit(top_k)
        )
        return [(chunk, 1.0 - dist) for chunk, dist in self.db.execute(stmt).all()]

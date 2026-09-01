"""Phase 12 knowledge document management service.

docs/api/API_SPEC.md: "POST /knowledge/documents: Create/upload a knowledge
document. Validate filename, content type, size, and parsing." and
docs/security/SECURITY_SPEC.md "Uploads: Validate file type, size, filename,
content parsing errors."

Orchestrates document upload/index/delete around the existing Phase 08
ingestion pipeline (app/services/ingestion/*) and Phase 07 repositories
without duplicating either: `ingest_document` still owns all chunking/
embedding/persistence logic. This module only adds the upload-time file
handling and validation that Phase 08 (which only ever read pre-existing
files from `data/knowledge_base/`) did not need.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationAppError
from app.models.document import Document
from app.providers.embedding_provider import EmbeddingProvider, get_embedding_provider
from app.repositories.document_repository import DocumentRepository
from app.services.ingestion.config import DOCUMENT_STATUS_PENDING, KNOWLEDGE_BASE_DIR
from app.services.ingestion.loader import load_document
from app.services.ingestion.pipeline import ingest_document
from app.services.ingestion.splitter import RecursiveCharacterTextSplitter

# Technical upload limits (not specified anywhere in the spec pack; chosen as
# a conservative default for Markdown knowledge articles and documented here
# rather than silently assumed).
MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB
ALLOWED_EXTENSION = ".md"
ALLOWED_CONTENT_TYPES = frozenset({"text/markdown", "text/plain", "application/octet-stream", ""})
_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(frozen=True)
class IndexOutcome:
    """Result of an index/re-index call, including the document's resulting status."""

    document_id: uuid.UUID
    source_id: str
    action: str
    chunk_count: int
    status: str


def _validate_filename(filename: str | None) -> str:
    if not filename:
        raise ValidationAppError("A filename is required.")
    name = Path(filename).name
    if name != filename or not _SAFE_FILENAME_RE.match(name):
        raise ValidationAppError("Filename contains unsupported characters.")
    if not name.lower().endswith(ALLOWED_EXTENSION):
        raise ValidationAppError("Only Markdown (.md) knowledge documents are supported.")
    return name


class KnowledgeService:
    def __init__(
        self,
        db: Session,
        knowledge_base_dir: Path = KNOWLEDGE_BASE_DIR,
        embedding_provider: EmbeddingProvider | None = None,
    ):
        self._db = db
        self._dir = knowledge_base_dir
        self._embedding_provider = embedding_provider or get_embedding_provider()
        self._document_repo = DocumentRepository(db)

    def upload_document(
        self, filename: str | None, content_type: str | None, content: bytes
    ) -> Document:
        """Validate, save to disk, and register (but do not index) a knowledge document."""
        name = _validate_filename(filename)

        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise ValidationAppError(f"Unsupported content type '{content_type}'.")
        if len(content) == 0:
            raise ValidationAppError("Uploaded file must not be empty.")
        if len(content) > MAX_UPLOAD_BYTES:
            raise ValidationAppError(
                f"Uploaded file exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)}MB size limit."
            )

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationAppError("Uploaded file must be UTF-8 encoded text.") from exc

        self._dir.mkdir(parents=True, exist_ok=True)
        path = self._dir / name

        try:
            path.write_text(text, encoding="utf-8")
            loaded = load_document(path)
        except ValueError as exc:
            path.unlink(missing_ok=True)
            raise ValidationAppError(f"Could not parse document '{name}': {exc}") from exc

        existing = self._document_repo.get_by_source_id(name)
        if existing is not None:
            existing.title = loaded.title
            existing.category = loaded.category
            existing.version = loaded.version
            existing.status = DOCUMENT_STATUS_PENDING
            self._db.flush()
            self._db.refresh(existing)
            document = existing
        else:
            # content_hash is intentionally left blank (not `loaded.content_hash`)
            # so the first /index call always detects a change and embeds it --
            # ingest_document() treats a matching content_hash as "already
            # indexed, skip" (app/services/ingestion/pipeline.py).
            document = self._document_repo.add(
                Document(
                    source_id=name,
                    title=loaded.title,
                    category=loaded.category,
                    version=loaded.version,
                    content_hash="",
                    status=DOCUMENT_STATUS_PENDING,
                )
            )
        self._db.commit()
        return document

    def index_document(self, document_id: uuid.UUID) -> IndexOutcome:
        """Chunk, embed, and persist a previously uploaded document (idempotent)."""
        document = self._document_repo.get(document_id)
        if document is None:
            raise NotFoundError(f"Knowledge document '{document_id}' was not found.")

        path = self._dir / document.source_id
        if not path.exists():
            raise NotFoundError(
                f"Source file for document '{document.source_id}' is missing on disk."
            )

        try:
            loaded = load_document(path)
        except ValueError as exc:
            raise ValidationAppError(
                f"Could not parse document '{document.source_id}': {exc}"
            ) from exc

        result = ingest_document(
            self._db, loaded, RecursiveCharacterTextSplitter(), self._embedding_provider
        )
        self._db.commit()
        # `document` and the row `ingest_document` mutated are the same
        # SQLAlchemy identity-mapped instance, so `.status` already reflects
        # the outcome without a second query.
        return IndexOutcome(
            document_id=document_id,
            source_id=result.source_id,
            action=result.action,
            chunk_count=result.chunk_count,
            status=document.status,
        )

    def delete_document(self, document_id: uuid.UUID) -> None:
        """Delete a document, its chunks (cascade), and its file on disk."""
        document = self._document_repo.get(document_id)
        if document is None:
            raise NotFoundError(f"Knowledge document '{document_id}' was not found.")

        # Captured before delete/commit: the ORM instance is expired/detached
        # once its row no longer exists, so its attributes can't be read after.
        source_id = document.source_id
        self._document_repo.delete(document)
        self._db.commit()

        (self._dir / source_id).unlink(missing_ok=True)

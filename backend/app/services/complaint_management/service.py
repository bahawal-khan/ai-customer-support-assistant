"""Bulk deletion of previously analyzed complaints (docs/api/API_SPEC.md "DELETE /complaints").

Deleting a `Complaint` cascades to its `Analysis`, `RetrievedSource` rows, and
`GeneratedResponse`: both the ORM relationship cascades (`cascade="all,
delete-orphan"` on `Complaint.analysis` and `Analysis.retrieved_sources` /
`Analysis.generated_response`, app/models/complaint.py and
app/models/analysis.py) and the matching DB-level `ON DELETE CASCADE`
foreign keys handle it, so no related-record cleanup is coded here.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.repositories.complaint_repository import ComplaintRepository


class ComplaintManagementService:
    def __init__(self, db: Session):
        self._db = db
        self._complaint_repo = ComplaintRepository(db)

    def bulk_delete(self, complaint_ids: list[uuid.UUID]) -> list[uuid.UUID]:
        """Delete all given complaints, or none of them if any ID doesn't exist."""
        found = self._complaint_repo.list_by_ids(complaint_ids)
        found_ids = {complaint.id for complaint in found}
        missing_ids = [cid for cid in complaint_ids if cid not in found_ids]
        if missing_ids:
            missing = ", ".join(str(cid) for cid in missing_ids)
            raise NotFoundError(f"Complaint(s) not found: {missing}")

        for complaint in found:
            self._complaint_repo.delete(complaint)
        self._db.commit()

        return complaint_ids

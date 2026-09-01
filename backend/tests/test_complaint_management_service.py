"""ComplaintManagementService.bulk_delete integration tests.

Exercises real cascade-delete behavior against Postgres (via the shared
`db_session` fixture, skips when unreachable): deleting a complaint must
also remove its analysis, retrieved sources, and generated response, with
no orphaned rows left behind.
"""

from __future__ import annotations

import uuid

import pytest

from app.core.errors import NotFoundError
from app.models.analysis import Analysis
from app.models.complaint import Complaint
from app.models.generated_response import GeneratedResponse
from app.models.retrieved_source import RetrievedSource
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.generated_response_repository import GeneratedResponseRepository
from app.repositories.retrieved_source_repository import RetrievedSourceRepository
from app.services.complaint_management.service import ComplaintManagementService


def _seed_full_complaint(db_session, *, text: str) -> tuple[Complaint, Analysis]:
    complaint = ComplaintRepository(db_session).add(Complaint(text=text))
    analysis = AnalysisRepository(db_session).add(
        Analysis(
            complaint_id=complaint.id,
            intent="get_refund",
            intent_confidence=0.9,
            sentiment="negative",
            sentiment_confidence=0.8,
            priority="high",
            priority_reason="seeded for test",
            intent_model_version="distilbert-v2",
        )
    )
    RetrievedSourceRepository(db_session).add(
        RetrievedSource(analysis_id=analysis.id, chunk_id=None, retrieval_score=0.9, rank=1)
    )
    GeneratedResponseRepository(db_session).add(
        GeneratedResponse(
            analysis_id=analysis.id,
            provider="groq",
            model="openai/gpt-oss-20b",
            prompt_version="grounded-support-v1",
            response="Refunds take 5 business days.",
        )
    )
    db_session.commit()
    return complaint, analysis


def test_bulk_delete_removes_complaint_and_cascades_related_rows(db_session):
    complaint, analysis = _seed_full_complaint(db_session, text="Where is my refund?")
    # Captured before delete/commit: the ORM instance is expired/detached
    # once its row no longer exists, so its attributes can't be read after
    # (same caveat as KnowledgeService.delete_document).
    complaint_id, analysis_id = complaint.id, analysis.id

    ComplaintManagementService(db_session).bulk_delete([complaint_id])

    assert ComplaintRepository(db_session).get(complaint_id) is None
    assert AnalysisRepository(db_session).get(analysis_id) is None
    assert RetrievedSourceRepository(db_session).list_by_analysis(analysis_id) == []
    assert GeneratedResponseRepository(db_session).get_by_analysis_id(analysis_id) is None


def test_bulk_delete_removes_multiple_complaints(db_session):
    complaint_a, _ = _seed_full_complaint(db_session, text="Complaint A")
    complaint_b, _ = _seed_full_complaint(db_session, text="Complaint B")
    id_a, id_b = complaint_a.id, complaint_b.id

    deleted_ids = ComplaintManagementService(db_session).bulk_delete([id_a, id_b])

    assert set(deleted_ids) == {id_a, id_b}
    assert ComplaintRepository(db_session).get(id_a) is None
    assert ComplaintRepository(db_session).get(id_b) is None


def test_bulk_delete_raises_not_found_and_deletes_nothing_if_any_id_missing(db_session):
    complaint, _ = _seed_full_complaint(db_session, text="Still here")
    missing_id = uuid.uuid4()

    with pytest.raises(NotFoundError):
        ComplaintManagementService(db_session).bulk_delete([complaint.id, missing_id])

    # All-or-nothing: the existing complaint must survive a batch that
    # included a nonexistent ID.
    assert ComplaintRepository(db_session).get(complaint.id) is not None

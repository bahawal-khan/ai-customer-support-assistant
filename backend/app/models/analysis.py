import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.generated_response import GeneratedResponse
    from app.models.retrieved_source import RetrievedSource


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (
        Index("ix_analyses_intent", "intent"),
        Index("ix_analyses_priority", "priority"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    intent: Mapped[str] = mapped_column(String(100), nullable=False)
    intent_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(50), nullable=False)
    sentiment_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    priority_reason: Mapped[str] = mapped_column(Text, nullable=False)
    intent_model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    complaint: Mapped["Complaint"] = relationship(back_populates="analysis")
    retrieved_sources: Mapped[list["RetrievedSource"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )
    generated_response: Mapped["GeneratedResponse"] = relationship(
        back_populates="analysis", cascade="all, delete-orphan", uselist=False
    )

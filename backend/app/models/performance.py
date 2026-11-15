import enum
import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import String, Date, Float, Enum, ForeignKey, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class CycleStatus(str, enum.Enum):
    UPCOMING = "UPCOMING"
    ACTIVE = "ACTIVE"
    EVALUATION = "EVALUATION"
    CLOSED = "CLOSED"

class GoalStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    ACHIEVED = "ACHIEVED"
    EXCEEDED = "EXCEEDED"
    MISSED = "MISSED"

class ReviewRelationship(str, enum.Enum):
    SELF = "SELF"
    MANAGER = "MANAGER"
    PEER = "PEER"
    DIRECT_REPORT = "DIRECT_REPORT"

class PerformanceCycle(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "performance_cycles"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False) # e.g. "Q4 2026 Engineering Review"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[CycleStatus] = mapped_column(
        Enum(CycleStatus), default=CycleStatus.UPCOMING, index=True, nullable=False
    )
    rubric_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    goals: Mapped[List["GoalOKR"]] = relationship("GoalOKR", back_populates="cycle", cascade="all, delete-orphan")
    reviews: Mapped[List["ReviewFeedback"]] = relationship(
        "ReviewFeedback", back_populates="cycle", cascade="all, delete-orphan"
    )

class GoalOKR(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "goal_okrs"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("performance_cycles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    key_results: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False) # targets and progress metrics
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus), default=GoalStatus.IN_PROGRESS, nullable=False
    )

    # Relationships
    cycle: Mapped["PerformanceCycle"] = relationship("PerformanceCycle", back_populates="goals")
    employee: Mapped["Employee"] = relationship("Employee")

class ReviewFeedback(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "review_feedbacks"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("performance_cycles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reviewee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    relationship: Mapped[ReviewRelationship] = mapped_column(
        Enum(ReviewRelationship), nullable=False
    )
    ratings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False) # category scores
    qualitative_feedback: Mapped[str] = mapped_column(Text, default="", nullable=False)
    ai_synthesized_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_submitted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    cycle: Mapped["PerformanceCycle"] = relationship("PerformanceCycle", back_populates="reviews")
    reviewee: Mapped["Employee"] = relationship("Employee", foreign_keys=[reviewee_id])
    reviewer: Mapped["Employee"] = relationship("Employee", foreign_keys=[reviewer_id])

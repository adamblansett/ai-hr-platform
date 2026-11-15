import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from backend.app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, utc_now

class PolicyDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "policy_documents"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # e.g. "Employee Handbook", "Code of Conduct", "Leave Policy"
    version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Chunking & Semantic Search support
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_chunks: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Dual vector embedding support for both local 768-dim and cloud/extended 1536-dim models
    embedding_768 = mapped_column(Vector(768), nullable=True)   # Local Ollama: nomic-embed-text / bge-base-en
    embedding_1536 = mapped_column(Vector(1536), nullable=True) # Cloud / High-dim: OpenAI text-embedding-3-small
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    active_dimension: Mapped[int] = mapped_column(Integer, default=768, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_acknowledgment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="policies")
    acknowledgments: Mapped[List["PolicyAcknowledgment"]] = relationship(
        "PolicyAcknowledgment", back_populates="policy", cascade="all, delete-orphan"
    )

class PolicyAcknowledgment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "policy_acknowledgments"

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("policy_documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), index=True, nullable=False
    )
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    signature_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Relationships
    policy: Mapped["PolicyDocument"] = relationship("PolicyDocument", back_populates="acknowledgments")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="policy_acknowledgments")

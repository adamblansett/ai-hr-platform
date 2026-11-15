import uuid
from typing import List, Optional
from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class Organization(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    employees: Mapped[List["Employee"]] = relationship(
        "Employee", back_populates="organization", cascade="all, delete-orphan"
    )
    policies: Mapped[List["PolicyDocument"]] = relationship(
        "PolicyDocument", back_populates="organization", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="organization", cascade="all, delete-orphan"
    )

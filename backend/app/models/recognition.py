from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


class CoreValue(str, Enum):
    CUSTOMER_OBSESSION = "CUSTOMER_OBSESSION"
    BIAS_FOR_ACTION = "BIAS_FOR_ACTION"
    INNOVATION_EXCELLENCE = "INNOVATION_EXCELLENCE"
    INCLUSION_AND_RESPECT = "INCLUSION_AND_RESPECT"
    DELIVER_RESULTS = "DELIVER_RESULTS"
    OWNERSHIP = "OWNERSHIP"


class MilestoneType(str, Enum):
    WORK_ANNIVERSARY = "WORK_ANNIVERSARY"
    BIRTHDAY = "BIRTHDAY"
    PROMOTION = "PROMOTION"
    PROJECT_ACHIEVEMENT = "PROJECT_ACHIEVEMENT"


class PeerRecognition(Base):
    __tablename__ = "peer_recognitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sender_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False)
    recipient_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=50)
    core_value: Mapped[str] = mapped_column(String(50), default=CoreValue.CUSTOMER_OBSESSION.value)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RewardCatalogItem(Base):
    __tablename__ = "reward_catalog_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="GIFT_CARD")
    points_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class EmployeeRecognitionWallet(Base):
    __tablename__ = "employee_recognition_wallets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), unique=True, nullable=False)
    points_balance: Mapped[int] = mapped_column(Integer, default=100)
    monthly_allowance_remaining: Mapped[int] = mapped_column(Integer, default=200)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

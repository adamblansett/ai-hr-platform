import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Integer, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    target_url = Column(String(500), nullable=False)
    secret_key = Column(String(128), nullable=False)
    event_types = Column(JSON, default=list)  # e.g. ["employee.hired", "leave.approved", "equity.vested"]
    is_active = Column(Boolean, default=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    deliveries = relationship("WebhookDeliveryLog", back_populates="subscription", cascade="all, delete-orphan")


class WebhookDeliveryLog(Base):
    __tablename__ = "webhook_delivery_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String(36), ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    status_code = Column(Integer, nullable=True)
    attempt_count = Column(Integer, default=1)
    delivered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    error_message = Column(Text, nullable=True)

    subscription = relationship("WebhookSubscription", back_populates="deliveries")

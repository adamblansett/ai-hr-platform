from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


class AssetCategory(str, Enum):
    LAPTOP = "LAPTOP"
    MONITOR = "MONITOR"
    MOBILE = "MOBILE"
    SECURITY_KEY = "SECURITY_KEY"
    ACCESSORY = "ACCESSORY"


class AssetStatus(str, Enum):
    IN_STOCK = "IN_STOCK"
    ASSIGNED = "ASSIGNED"
    UNDER_REPAIR = "UNDER_REPAIR"
    RETIRED = "RETIRED"
    LOST = "LOST"


class MDMProvider(str, Enum):
    JAMF_PRO = "JAMF_PRO"
    MICROSOFT_INTUNE = "MICROSOFT_INTUNE"
    KANDJI = "KANDJI"
    UNMANAGED = "UNMANAGED"


class RemoteWipeStatus(str, Enum):
    IDLE = "IDLE"
    PENDING = "PENDING"
    COMMAND_SENT = "COMMAND_SENT"
    WIPED = "WIPED"


class HardwareAsset(Base):
    __tablename__ = "hardware_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    asset_tag: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    serial_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    device_model: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(30), default=AssetCategory.LAPTOP.value)
    status: Mapped[str] = mapped_column(String(30), default=AssetStatus.IN_STOCK.value)
    assigned_to_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    purchase_date: Mapped[str] = mapped_column(String(10), nullable=False)
    warranty_expiry: Mapped[str] = mapped_column(String(10), nullable=False)
    device_condition: Mapped[str] = mapped_column(String(30), default="EXCELLENT")
    
    # MDM Integration (Jamf / Intune)
    mdm_enrolled: Mapped[bool] = mapped_column(Boolean, default=True)
    mdm_provider: Mapped[str] = mapped_column(String(30), default=MDMProvider.JAMF_PRO.value)
    mdm_device_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mdm_last_checkin: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    remote_wipe_status: Mapped[str] = mapped_column(String(30), default=RemoteWipeStatus.IDLE.value)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

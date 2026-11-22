from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class HardwareAssetCreate(BaseModel):
    asset_tag: str
    serial_number: str
    device_model: str
    category: str = Field("LAPTOP", description="LAPTOP, MONITOR, MOBILE, SECURITY_KEY, ACCESSORY")
    purchase_date: str = Field(..., description="YYYY-MM-DD")
    warranty_expiry: str = Field(..., description="YYYY-MM-DD")
    device_condition: str = "EXCELLENT"
    mdm_provider: str = "JAMF_PRO"
    notes: Optional[str] = None


class HardwareAssetResponse(BaseModel):
    id: str
    asset_tag: str
    serial_number: str
    device_model: str
    category: str
    status: str
    assigned_to_id: Optional[str] = None
    assigned_to_name: Optional[str] = None
    assigned_at: Optional[datetime] = None
    purchase_date: str
    warranty_expiry: str
    device_condition: str
    mdm_enrolled: bool
    mdm_provider: str
    mdm_device_id: Optional[str] = None
    mdm_last_checkin: Optional[datetime] = None
    remote_wipe_status: str
    notes: Optional[str] = None


class AssetAssignRequest(BaseModel):
    employee_id: str


class AssetRemoteWipeRequest(BaseModel):
    reason: str


class FleetSummary(BaseModel):
    total_assets: int
    assigned_assets: int
    in_stock_assets: int
    mdm_compliance_rate: float
    pending_wipe_count: int

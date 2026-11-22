from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.assets import (
    HardwareAssetCreate,
    HardwareAssetResponse,
    AssetAssignRequest,
    AssetRemoteWipeRequest,
    FleetSummary,
)
from backend.app.services.assets_service import assets_service

router = APIRouter()


@router.get("/", response_model=List[HardwareAssetResponse])
def list_hardware_assets(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    employee_id: Optional[str] = Query(None),
):
    """List hardware assets in the enterprise IT fleet."""
    return assets_service.list_assets(category=category, status=status, employee_id=employee_id)


@router.post("/", response_model=HardwareAssetResponse, status_code=status.HTTP_201_CREATED)
def create_hardware_asset(payload: HardwareAssetCreate):
    """Register a new hardware asset into the inventory system."""
    return assets_service.create_asset(payload)


@router.post("/{asset_id}/assign", response_model=HardwareAssetResponse)
def assign_hardware_asset(asset_id: str, payload: AssetAssignRequest):
    """Assign an asset to an employee."""
    try:
        return assets_service.assign_asset(asset_id, payload.employee_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{asset_id}/unassign", response_model=HardwareAssetResponse)
def unassign_hardware_asset(asset_id: str):
    """Return an assigned asset back to available in-stock inventory."""
    try:
        return assets_service.unassign_asset(asset_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{asset_id}/remote-wipe", response_model=HardwareAssetResponse)
def trigger_remote_wipe(asset_id: str, payload: AssetRemoteWipeRequest):
    """Dispatch remote device lock/wipe command via Jamf / Microsoft Intune MDM."""
    try:
        return assets_service.trigger_remote_wipe(asset_id, payload.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/summary/fleet", response_model=FleetSummary)
def get_fleet_summary():
    """Retrieve high-level hardware fleet and MDM enrollment metrics."""
    return assets_service.get_fleet_summary()

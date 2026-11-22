import uuid
from datetime import datetime
from typing import Dict, List, Optional
from backend.app.schemas.assets import (
    HardwareAssetCreate,
    HardwareAssetResponse,
    FleetSummary,
)


class AssetsService:
    def __init__(self):
        self._assets: Dict[str, dict] = {}
        self._seed_default_assets()

    def _seed_default_assets(self):
        a1 = {
            "id": "asset-001",
            "asset_tag": "TAG-MBP-8910",
            "serial_number": "C02G901KMD6T",
            "device_model": "Apple MacBook Pro 16\" (M3 Max, 64GB, 1TB)",
            "category": "LAPTOP",
            "status": "ASSIGNED",
            "assigned_to_id": "emp-001",
            "assigned_to_name": "Alex Chen",
            "assigned_at": datetime(2026, 1, 10, 10, 0, 0),
            "purchase_date": "2026-01-05",
            "warranty_expiry": "2029-01-05",
            "device_condition": "EXCELLENT",
            "mdm_enrolled": True,
            "mdm_provider": "JAMF_PRO",
            "mdm_device_id": "JAMF-DEV-99412",
            "mdm_last_checkin": datetime(2026, 11, 22, 12, 30, 0),
            "remote_wipe_status": "IDLE",
            "notes": "Primary development workstation with FileVault encryption enabled.",
        }
        a2 = {
            "id": "asset-002",
            "asset_tag": "TAG-MBP-8911",
            "serial_number": "C02GA22KMD6U",
            "device_model": "Apple MacBook Pro 14\" (M3 Pro, 36GB, 512GB)",
            "category": "LAPTOP",
            "status": "IN_STOCK",
            "assigned_to_id": None,
            "assigned_to_name": None,
            "assigned_at": None,
            "purchase_date": "2026-02-15",
            "warranty_expiry": "2029-02-15",
            "device_condition": "NEW_IN_BOX",
            "mdm_enrolled": True,
            "mdm_provider": "JAMF_PRO",
            "mdm_device_id": "JAMF-DEV-99413",
            "mdm_last_checkin": datetime(2026, 11, 20, 9, 0, 0),
            "remote_wipe_status": "IDLE",
            "notes": "Staged and ready for incoming engineering hires.",
        }
        a3 = {
            "id": "asset-003",
            "asset_tag": "TAG-MON-4401",
            "serial_number": "DL322409A88B",
            "device_model": "Dell UltraSharp 32\" 4K USB-C Hub Monitor (U3223QE)",
            "category": "MONITOR",
            "status": "ASSIGNED",
            "assigned_to_id": "emp-001",
            "assigned_to_name": "Alex Chen",
            "assigned_at": datetime(2026, 1, 10, 10, 0, 0),
            "purchase_date": "2026-01-05",
            "warranty_expiry": "2029-01-05",
            "device_condition": "EXCELLENT",
            "mdm_enrolled": False,
            "mdm_provider": "UNMANAGED",
            "mdm_device_id": None,
            "mdm_last_checkin": None,
            "remote_wipe_status": "IDLE",
            "notes": "Dual monitor desk mount setup.",
        }
        self._assets[a1["id"]] = a1
        self._assets[a2["id"]] = a2
        self._assets[a3["id"]] = a3

    def list_assets(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        employee_id: Optional[str] = None,
    ) -> List[HardwareAssetResponse]:
        results = list(self._assets.values())
        if category:
            results = [a for a in results if a["category"] == category]
        if status:
            results = [a for a in results if a["status"] == status]
        if employee_id:
            results = [a for a in results if a["assigned_to_id"] == employee_id]
        return [HardwareAssetResponse(**a) for a in results]

    def create_asset(self, payload: HardwareAssetCreate) -> HardwareAssetResponse:
        asset_id = f"asset-{uuid.uuid4().hex[:6]}"
        record = {
            "id": asset_id,
            "asset_tag": payload.asset_tag,
            "serial_number": payload.serial_number,
            "device_model": payload.device_model,
            "category": payload.category,
            "status": "IN_STOCK",
            "assigned_to_id": None,
            "assigned_to_name": None,
            "assigned_at": None,
            "purchase_date": payload.purchase_date,
            "warranty_expiry": payload.warranty_expiry,
            "device_condition": payload.device_condition,
            "mdm_enrolled": payload.mdm_provider != "UNMANAGED",
            "mdm_provider": payload.mdm_provider,
            "mdm_device_id": f"MDM-{uuid.uuid4().hex[:8].upper()}" if payload.mdm_provider != "UNMANAGED" else None,
            "mdm_last_checkin": datetime.utcnow() if payload.mdm_provider != "UNMANAGED" else None,
            "remote_wipe_status": "IDLE",
            "notes": payload.notes,
        }
        self._assets[asset_id] = record
        return HardwareAssetResponse(**record)

    def assign_asset(self, asset_id: str, employee_id: str, employee_name: str = "Assigned Employee") -> HardwareAssetResponse:
        asset = self._assets.get(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        asset["assigned_to_id"] = employee_id
        asset["assigned_to_name"] = employee_name
        asset["assigned_at"] = datetime.utcnow()
        asset["status"] = "ASSIGNED"
        return HardwareAssetResponse(**asset)

    def unassign_asset(self, asset_id: str) -> HardwareAssetResponse:
        asset = self._assets.get(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        asset["assigned_to_id"] = None
        asset["assigned_to_name"] = None
        asset["assigned_at"] = None
        asset["status"] = "IN_STOCK"
        return HardwareAssetResponse(**asset)

    def trigger_remote_wipe(self, asset_id: str, reason: str) -> HardwareAssetResponse:
        asset = self._assets.get(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        if not asset["mdm_enrolled"]:
            raise ValueError("Cannot remotely wipe unmanaged device without active MDM profile.")

        # Simulate Jamf/Intune remote command dispatch
        asset["remote_wipe_status"] = "COMMAND_SENT"
        asset["notes"] = f"Remote wipe command issued ({datetime.utcnow().isoformat()}): {reason}. Status: In-flight to client MDM agent."
        return HardwareAssetResponse(**asset)

    def get_fleet_summary(self) -> FleetSummary:
        total = len(self._assets)
        assigned = sum(1 for a in self._assets.values() if a["status"] == "ASSIGNED")
        in_stock = sum(1 for a in self._assets.values() if a["status"] == "IN_STOCK")
        managed = sum(1 for a in self._assets.values() if a["mdm_enrolled"])
        rate = round((managed / total) * 100, 1) if total > 0 else 100.0
        pending_wipes = sum(1 for a in self._assets.values() if a["remote_wipe_status"] in ("PENDING", "COMMAND_SENT"))

        return FleetSummary(
            total_assets=total,
            assigned_assets=assigned,
            in_stock_assets=in_stock,
            mdm_compliance_rate=rate,
            pending_wipe_count=pending_wipes,
        )


assets_service = AssetsService()

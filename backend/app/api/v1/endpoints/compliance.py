from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.api.v1.deps import get_current_user, require_roles
from backend.app.services.compliance_service import ComplianceService

router = APIRouter()


@router.get("/dsar/{employee_id}")
async def get_employee_dsar_export(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """Generate and export a complete GDPR / CCPA Data Subject Access Request bundle."""
    try:
        dsar_bundle = await ComplianceService.generate_dsar_export(
            db, employee_id, current_user.organization_id
        )
        return dsar_bundle
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/right-to-be-forgotten/{employee_id}")
async def execute_employee_erasure(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN"])),
):
    """Execute GDPR Article 17 Right to Erasure / Anonymization on employee record."""
    try:
        result = await ComplianceService.execute_right_to_be_forgotten(
            db, employee_id, current_user.organization_id, actor_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/soc2/evidence")
async def get_soc2_compliance_evidence(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"])),
):
    """Retrieve automated SOC 2 Trust Services Criteria evidence summary."""
    report = await ComplianceService.generate_soc2_evidence(db, current_user.organization_id)
    return report

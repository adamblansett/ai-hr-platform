import uuid
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.core.security import get_password_hash
from backend.app.models.employee import Employee, EmployeeRole, EmploymentStatus, EmploymentType
from backend.app.models.audit import AuditLog
from backend.app.schemas.scim import (
    SCIMUserResource,
    SCIMUserName,
    SCIMUserEmail,
    SCIMListResponse,
    SCIMCreateUserRequest,
    SCIMPatchRequest,
)

router = APIRouter()
DEFAULT_ORG_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

def employee_to_scim(emp: Employee) -> SCIMUserResource:
    return SCIMUserResource(
        id=str(emp.id),
        userName=emp.email,
        name=SCIMUserName(
            givenName=emp.first_name,
            familyName=emp.last_name,
            formatted=f"{emp.first_name} {emp.last_name}"
        ),
        emails=[SCIMUserEmail(value=emp.email, type="work", primary=True)],
        active=emp.status != EmploymentStatus.TERMINATED,
        title=emp.job_title,
        department=emp.department,
        meta={
            "resourceType": "User",
            "created": emp.created_at.isoformat(),
            "lastModified": emp.updated_at.isoformat(),
            "location": f"/scim/v2/Users/{emp.id}"
        }
    )

@router.get("/ServiceProviderConfig", summary="SCIM 2.0 Service Provider Configuration")
async def get_service_provider_config():
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "patch": {"supported": True},
        "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "filter": {"supported": True, "maxResults": 200},
        "changePassword": {"supported": False},
        "sort": {"supported": False},
        "etag": {"supported": False},
        "authenticationSchemes": [
            {
                "name": "OAuth Bearer Token",
                "description": "Authentication scheme using the OAuth Bearer Token Standard",
                "specUri": "http://www.rfc-editor.org/info/rfc6750",
                "type": "oauthbearertoken",
                "primary": True
            }
        ]
    }

@router.get("/Users", response_model=SCIMListResponse, summary="Query SCIM Users")
async def list_scim_users(
    startIndex: int = Query(1, ge=1),
    count: int = Query(50, ge=1, le=100),
    filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Employee).where(Employee.organization_id == DEFAULT_ORG_ID)

    if filter and "userName eq" in filter:
        target_email = filter.split("userName eq")[-1].strip().replace('"', '')
        query = query.where(Employee.email == target_email)

    total_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_stmt)).scalar() or 0

    offset = startIndex - 1
    paginated_stmt = query.offset(offset).limit(count)
    employees = (await db.execute(paginated_stmt)).scalars().all()

    resources = [employee_to_scim(e) for e in employees]
    return SCIMListResponse(
        totalResults=total,
        startIndex=startIndex,
        itemsPerPage=len(resources),
        Resources=resources
    )

@router.get("/Users/{user_id}", response_model=SCIMUserResource, summary="Get SCIM User by ID")
async def get_scim_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Employee).where(Employee.id == user_id, Employee.organization_id == DEFAULT_ORG_ID)
    emp = (await db.execute(stmt)).scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SCIM User not found")
    return employee_to_scim(emp)

@router.post("/Users", response_model=SCIMUserResource, status_code=status.HTTP_201_CREATED, summary="Inbound Provision User via SCIM")
async def create_scim_user(
    req: SCIMCreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    # Idempotency check
    stmt = select(Employee).where(Employee.email == req.userName)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {req.userName} already exists"
        )

    temp_pw = f"ScimWelcome!{uuid.uuid4().hex[:8]}"
    new_emp = Employee(
        organization_id=DEFAULT_ORG_ID,
        email=req.userName,
        hashed_password=get_password_hash(temp_pw),
        first_name=req.name.givenName,
        last_name=req.name.familyName,
        role=EmployeeRole.EMPLOYEE,
        status=EmploymentStatus.ACTIVE if req.active else EmploymentStatus.TERMINATED,
        employment_type=EmploymentType.FULL_TIME,
        department=req.department or "Engineering",
        job_title=req.title or "Team Member",
        hire_date=date.today(),
        custom_attributes={"provisioned_via": "inbound_scim_2.0"}
    )
    db.add(new_emp)
    await db.flush()

    audit = AuditLog(
        organization_id=DEFAULT_ORG_ID,
        actor_id=None,
        action="SCIM_USER_PROVISIONED",
        entity_type="Employee",
        entity_id=str(new_emp.id),
        details={"email": req.userName, "source": "inbound_scim_2.0"},
        pii_redacted=True
    )
    db.add(audit)
    await db.commit()
    await db.refresh(new_emp)

    return employee_to_scim(new_emp)

@router.patch("/Users/{user_id}", response_model=SCIMUserResource, summary="SCIM PATCH update user")
async def patch_scim_user(
    user_id: uuid.UUID,
    patch_req: SCIMPatchRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Employee).where(Employee.id == user_id, Employee.organization_id == DEFAULT_ORG_ID)
    emp = (await db.execute(stmt)).scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SCIM User not found")

    for op in patch_req.Operations:
        if op.path == "active" or (isinstance(op.value, dict) and "active" in op.value):
            active_val = op.value if op.path == "active" else op.value["active"]
            if not active_val:
                emp.status = EmploymentStatus.TERMINATED
            else:
                emp.status = EmploymentStatus.ACTIVE

    await db.commit()
    await db.refresh(emp)
    return employee_to_scim(emp)

@router.delete("/Users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="SCIM DELETE deprovision user")
async def delete_scim_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Employee).where(Employee.id == user_id, Employee.organization_id == DEFAULT_ORG_ID)
    emp = (await db.execute(stmt)).scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SCIM User not found")

    emp.status = EmploymentStatus.TERMINATED
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

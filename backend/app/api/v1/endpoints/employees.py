import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.employee import Employee, EmployeeRole, EmploymentStatus
from backend.app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeSelfUpdate,
    EmployeeResponse,
    PaginatedEmployeesResponse,
    OrgChartNode,
)
from backend.app.services.employee_service import employee_service

router = APIRouter()

@router.get("/", response_model=PaginatedEmployeesResponse, summary="List employees in the directory")
async def list_employees(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    department: Optional[str] = None,
    status_filter: Optional[EmploymentStatus] = None,
    role_filter: Optional[EmployeeRole] = None,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    items, total, total_pages = await employee_service.list_employees(
        db=db,
        org_id=current_user.organization_id,
        page=page,
        size=size,
        search=search,
        department=department,
        status_filter=status_filter,
        role_filter=role_filter
    )
    return PaginatedEmployeesResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, summary="Create a new employee")
async def create_employee(
    data: EmployeeCreate,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    return await employee_service.create_employee(
        db=db,
        org_id=current_user.organization_id,
        data=data
    )

@router.get("/org-chart", response_model=list[OrgChartNode], summary="Get hierarchical organizational chart")
async def get_org_chart(
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await employee_service.build_org_chart(
        db=db,
        org_id=current_user.organization_id
    )

@router.get("/me", response_model=EmployeeResponse, summary="Get own employee record")
async def get_own_profile(
    current_user: Employee = Depends(get_current_user)
):
    return current_user

@router.patch("/me", response_model=EmployeeResponse, summary="Update own employee profile")
async def update_own_profile(
    update_data: EmployeeSelfUpdate,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await employee_service.update_self_profile(
        db=db,
        current_user=current_user,
        update_data=update_data
    )

@router.get("/org-chart", response_model=list[OrgChartNode], summary="Get organizational hierarchy tree")
async def get_org_chart(
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await employee_service.build_org_chart(db=db, org_id=current_user.organization_id)

@router.get("/org-chart/stats", summary="Get organizational span of control and structure metrics")
async def get_org_chart_stats(
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chart = await employee_service.build_org_chart(db=db, org_id=current_user.organization_id)
    
    total_nodes = 0
    managers = 0
    direct_report_counts = []
    overloaded_managers = []

    def traverse(node: OrgChartNode):
        nonlocal total_nodes, managers
        total_nodes += 1
        reports = len(node.direct_reports)
        if reports > 0:
            managers += 1
            direct_report_counts.append(reports)
            if reports > 8:
                overloaded_managers.append({
                    "id": str(node.id),
                    "name": node.name,
                    "job_title": node.job_title,
                    "direct_reports": reports
                })
        for child in node.direct_reports:
            traverse(child)

    for root in chart:
        traverse(root)

    avg_span = round(sum(direct_report_counts) / len(direct_report_counts), 1) if direct_report_counts else 0.0

    return {
        "total_active_employees": total_nodes,
        "total_people_managers": managers,
        "average_span_of_control": avg_span,
        "overloaded_managers_count": len(overloaded_managers),
        "overloaded_managers": overloaded_managers
    }

@router.get("/{id}", response_model=EmployeeResponse, summary="Get employee details by ID")
async def get_employee(
    id: uuid.UUID,
    current_user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    employee = await employee_service.get_employee_by_id(
        db=db,
        org_id=current_user.organization_id,
        employee_id=id
    )
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee

@router.patch("/{id}", response_model=EmployeeResponse, summary="Update employee record")
async def update_employee(
    id: uuid.UUID,
    update_data: EmployeeUpdate,
    current_user: Employee = Depends(require_role([EmployeeRole.SUPER_ADMIN, EmployeeRole.HR_ADMIN, EmployeeRole.PEOPLE_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    # People managers can only edit their direct reports
    if current_user.role == EmployeeRole.PEOPLE_MANAGER:
        target = await employee_service.get_employee_by_id(db, current_user.organization_id, id)
        if not target or target.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can only update their direct reports"
            )

    return await employee_service.update_employee(
        db=db,
        org_id=current_user.organization_id,
        employee_id=id,
        update_data=update_data
    )

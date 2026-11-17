import math
import uuid
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.app.core.security import get_password_hash
from backend.app.models.employee import Employee, EmployeeRole, EmploymentStatus
from backend.app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeSelfUpdate,
    OrgChartNode,
)

class EmployeeService:
    @staticmethod
    async def create_employee(
        db: AsyncSession,
        org_id: uuid.UUID,
        data: EmployeeCreate
    ) -> Employee:
        # Check duplicate email
        stmt = select(Employee).where(Employee.email == data.email)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with email {data.email} already exists"
            )

        # Validate manager if provided
        if data.manager_id:
            m_stmt = select(Employee).where(
                Employee.id == data.manager_id,
                Employee.organization_id == org_id
            )
            manager = (await db.execute(m_stmt)).scalar_one_or_none()
            if not manager:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified manager not found in this organization"
                )

        hashed_password = get_password_hash(data.password or "TemporaryPass!2026")
        
        employee_dict = data.model_dump(exclude={"password"})
        employee = Employee(
            **employee_dict,
            organization_id=org_id,
            hashed_password=hashed_password
        )
        db.add(employee)
        await db.commit()
        await db.refresh(employee)
        return employee

    @staticmethod
    async def get_employee_by_id(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID
    ) -> Optional[Employee]:
        stmt = select(Employee).where(
            Employee.id == employee_id,
            Employee.organization_id == org_id
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def list_employees(
        db: AsyncSession,
        org_id: uuid.UUID,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        department: Optional[str] = None,
        status_filter: Optional[EmploymentStatus] = None,
        role_filter: Optional[EmployeeRole] = None,
    ) -> Tuple[List[Employee], int, int]:
        query = select(Employee).where(Employee.organization_id == org_id)

        if search:
            search_term = f"%{search.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(Employee.first_name).like(search_term),
                    func.lower(Employee.last_name).like(search_term),
                    func.lower(Employee.email).like(search_term),
                    func.lower(Employee.job_title).like(search_term),
                )
            )

        if department:
            query = query.where(Employee.department == department)

        if status_filter:
            query = query.where(Employee.status == status_filter)

        if role_filter:
            query = query.where(Employee.role == role_filter)

        # Count total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0
        total_pages = math.ceil(total / size) if size > 0 else 1

        # Pagination & ordering
        offset = (page - 1) * size
        paginated_stmt = query.order_by(Employee.last_name.asc()).offset(offset).limit(size)
        items = (await db.execute(paginated_stmt)).scalars().all()

        return list(items), total, total_pages

    @staticmethod
    async def update_employee(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID,
        update_data: EmployeeUpdate
    ) -> Employee:
        employee = await EmployeeService.get_employee_by_id(db, org_id, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        # Prevent circular reporting
        if update_data.manager_id and update_data.manager_id == employee.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee cannot be their own manager"
            )

        data = update_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(employee, key, value)

        await db.commit()
        await db.refresh(employee)
        return employee

    @staticmethod
    async def update_self_profile(
        db: AsyncSession,
        current_user: Employee,
        update_data: EmployeeSelfUpdate
    ) -> Employee:
        data = update_data.model_dump(exclude_unset=True)
        if "custom_attributes" in data and data["custom_attributes"] is not None:
            # Merge custom attributes
            merged = {**current_user.custom_attributes, **data["custom_attributes"]}
            current_user.custom_attributes = merged
            data.pop("custom_attributes")

        for key, value in data.items():
            setattr(current_user, key, value)

        await db.commit()
        await db.refresh(current_user)
        return current_user

    @staticmethod
    async def build_org_chart(
        db: AsyncSession,
        org_id: uuid.UUID
    ) -> List[OrgChartNode]:
        stmt = select(Employee).where(
            Employee.organization_id == org_id,
            Employee.status != EmploymentStatus.TERMINATED
        )
        employees = (await db.execute(stmt)).scalars().all()

        # Build lookup table
        node_map: Dict[uuid.UUID, OrgChartNode] = {}
        for emp in employees:
            display_name = f"{emp.first_name} {emp.last_name}"
            if emp.preferred_name:
                display_name = f"{emp.preferred_name} ({emp.first_name}) {emp.last_name}"

            node_map[emp.id] = OrgChartNode(
                id=emp.id,
                name=display_name,
                email=emp.email,
                job_title=emp.job_title,
                department=emp.department,
                manager_id=emp.manager_id,
                direct_reports=[]
            )

        root_nodes: List[OrgChartNode] = []
        for emp_id, node in node_map.items():
            if node.manager_id and node.manager_id in node_map:
                node_map[node.manager_id].direct_reports.append(node)
            else:
                root_nodes.append(node)

        return root_nodes

employee_service = EmployeeService()

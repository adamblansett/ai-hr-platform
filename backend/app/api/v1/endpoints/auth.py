from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.app.api.deps import get_db, get_current_user
from backend.app.core.config import settings
from backend.app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from backend.app.models.employee import Employee, EmploymentStatus
from backend.app.schemas.auth import LoginRequest, Token, RefreshTokenRequest, CurrentUserResponse

router = APIRouter()

@router.post("/login", response_model=Token, summary="Authenticate employee and obtain JWT tokens")
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Employee).where(Employee.email == login_data.email)
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if not employee or not verify_password(login_data.password, employee.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if employee.status == EmploymentStatus.TERMINATED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=employee.id,
        organization_id=employee.organization_id,
        role=employee.role.value,
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        subject=employee.id,
        organization_id=employee.organization_id,
        role=employee.role.value
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=Token, summary="Refresh access token using refresh token")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(refresh_data.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provided token is not a refresh token",
        )

    user_id_str = payload.get("sub")
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token subject",
        )

    stmt = select(Employee).where(Employee.id == user_id)
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if not employee or employee.status == EmploymentStatus.TERMINATED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer active",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        subject=employee.id,
        organization_id=employee.organization_id,
        role=employee.role.value,
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        subject=employee.id,
        organization_id=employee.organization_id,
        role=employee.role.value
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me", response_model=CurrentUserResponse, summary="Get current authenticated employee profile")
async def get_current_user_profile(
    current_user: Employee = Depends(get_current_user)
):
    return current_user

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.app.api.deps import get_db, get_current_user, security
from backend.app.core.config import settings
from backend.app.core.rate_limit import rate_limit
from backend.app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    revoke_token_jti,
    calculate_remaining_ttl,
)
from backend.app.models.employee import Employee, EmploymentStatus
from backend.app.schemas.auth import (
    LoginRequest,
    Token,
    RefreshTokenRequest,
    LogoutRequest,
    LogoutResponse,
    CurrentUserResponse,
)

router = APIRouter()

@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate employee and obtain JWT tokens",
    dependencies=[Depends(rate_limit("auth_login", settings.RATE_LIMIT_LOGIN_PER_MINUTE, 60))],
)
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

    # Refresh token rotation: revoke the used refresh token jti immediately to prevent replay
    old_jti = payload.get("jti")
    if old_jti:
        revoke_token_jti(old_jti, ttl_seconds=calculate_remaining_ttl(payload, default_ttl=7 * 86400))

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

@router.post("/logout", response_model=LogoutResponse, summary="Revoke active JWT access and optional refresh tokens")
async def logout(
    logout_data: LogoutRequest = LogoutRequest(),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: Employee = Depends(get_current_user),
):
    revoked_count = 0
    access_payload = decode_token(credentials.credentials)
    if access_payload and access_payload.get("jti"):
        revoke_token_jti(
            access_payload["jti"],
            ttl_seconds=calculate_remaining_ttl(access_payload, default_ttl=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        )
        revoked_count += 1

    if logout_data and logout_data.refresh_token:
        refresh_payload = decode_token(logout_data.refresh_token)
        if refresh_payload and refresh_payload.get("jti"):
            revoke_token_jti(
                refresh_payload["jti"],
                ttl_seconds=calculate_remaining_ttl(refresh_payload, default_ttl=7 * 86400),
            )
            revoked_count += 1

    return LogoutResponse(status="logged_out", revoked_tokens=revoked_count)

@router.get("/me", response_model=CurrentUserResponse, summary="Get current authenticated employee profile")
async def get_current_user_profile(
    current_user: Employee = Depends(get_current_user)
):
    return current_user

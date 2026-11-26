from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr
from backend.app.models.employee import EmployeeRole, EmploymentStatus

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    org_id: Optional[str] = None
    role: Optional[str] = None
    type: Optional[str] = None
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None

class LogoutResponse(BaseModel):
    status: str = "logged_out"
    revoked_tokens: int = 1

class CurrentUserResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    preferred_name: Optional[str] = None
    role: EmployeeRole
    status: EmploymentStatus
    department: str
    job_title: str

    class Config:
        from_attributes = True

import uuid
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class SCIMUserName(BaseModel):
    formatted: Optional[str] = None
    familyName: str
    givenName: str

class SCIMUserEmail(BaseModel):
    value: str
    type: str = "work"
    primary: bool = True

class SCIMUserResource(BaseModel):
    schemas: List[str] = Field(default_factory=lambda: ["urn:ietf:params:scim:schemas:core:2.0:User"])
    id: str
    userName: str
    name: SCIMUserName
    emails: List[SCIMUserEmail]
    active: bool = True
    title: Optional[str] = None
    department: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class SCIMListResponse(BaseModel):
    schemas: List[str] = Field(default_factory=lambda: ["urn:ietf:params:scim:api:messages:2.0:ListResponse"])
    totalResults: int
    startIndex: int = 1
    itemsPerPage: int
    Resources: List[SCIMUserResource]

class SCIMPatchOp(BaseModel):
    op: str # "add", "replace", "remove"
    path: Optional[str] = None
    value: Any

class SCIMPatchRequest(BaseModel):
    schemas: List[str] = Field(default_factory=lambda: ["urn:ietf:params:scim:api:messages:2.0:PatchOp"])
    Operations: List[SCIMPatchOp]

class SCIMCreateUserRequest(BaseModel):
    schemas: Optional[List[str]] = None
    userName: str
    name: SCIMUserName
    emails: List[SCIMUserEmail]
    active: bool = True
    title: Optional[str] = "Team Member"
    department: Optional[str] = "Engineering"

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class PolicyDocumentCreate(BaseModel):
    title: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100) # e.g. "Employee Handbook", "Code of Conduct", "PTO Policy"
    version: str = Field("1.0.0", max_length=50)
    content: str
    requires_acknowledgment: bool = False
    source_file_url: Optional[str] = None

class PolicyDocumentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    category: str
    version: str
    content: str
    chunk_index: int
    total_chunks: int
    is_active: bool
    requires_acknowledgment: bool
    source_file_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PolicyQuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    category_filter: Optional[str] = None

class PolicySourceCitation(BaseModel):
    policy_id: uuid.UUID
    title: str
    category: str
    chunk_index: int
    snippet: str
    relevance_score: float

class PolicyAnswerResponse(BaseModel):
    question: str
    answer: str
    citations: List[PolicySourceCitation]
    model_used: str
    pii_redacted: bool

class PolicyAcknowledgmentRequest(BaseModel):
    signature_name: str = Field(..., min_length=2, max_length=150)

class PolicyAcknowledgmentResponse(BaseModel):
    id: uuid.UUID
    policy_id: uuid.UUID
    employee_id: uuid.UUID
    acknowledged_at: datetime
    signature_hash: str
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True

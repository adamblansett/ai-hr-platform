import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Boolean, Float, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class BenefitPlan(Base):
    __tablename__ = "benefit_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    plan_name = Column(String(150), nullable=False) # e.g. "Acme Anthem PPO Platinum 500"
    plan_type = Column(String(50), nullable=False) # MEDICAL, DENTAL, VISION, RETIREMENT_401K, HSA_FSA
    provider = Column(String(100), nullable=False) # Anthem, Delta Dental, VSP, Fidelity
    tier_name = Column(String(50), default="PPO") # PPO, HDHP, HMO
    
    monthly_employee_premium = Column(Float, default=120.0)
    monthly_employer_contribution = Column(Float, default=480.0)
    annual_deductible = Column(Float, default=500.0)
    out_of_pocket_max = Column(Float, default=3000.0)
    summary_of_benefits = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    elections = relationship("EmployeeBenefitElection", back_populates="plan", cascade="all, delete-orphan")


class EmployeeBenefitElection(Base):
    __tablename__ = "employee_benefit_elections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("benefit_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    
    coverage_tier = Column(String(50), default="EMPLOYEE_ONLY") # EMPLOYEE_ONLY, EMPLOYEE_PLUS_SPOUSE, EMPLOYEE_PLUS_CHILDREN, FAMILY
    effective_date = Column(Date, nullable=False)
    employee_monthly_cost = Column(Float, nullable=False)
    employer_monthly_cost = Column(Float, nullable=False)
    status = Column(String(30), default="ACTIVE") # ACTIVE, PENDING_OPEN_ENROLLMENT, TERMINATED, WAIVED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    employee = relationship("Employee", foreign_keys=[employee_id])
    plan = relationship("BenefitPlan", back_populates="elections")

import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Boolean, Float, Integer, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class TimeSheetEntry(Base):
    __tablename__ = "timesheet_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    shift_date = Column(Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    clock_in = Column(DateTime(timezone=True), nullable=False)
    clock_out = Column(DateTime(timezone=True), nullable=True)
    
    total_hours = Column(Float, default=0.0)
    regular_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0) # 1.5x pay rate
    double_time_hours = Column(Float, default=0.0) # 2.0x pay rate
    
    meal_break_minutes = Column(Integer, default=0)
    meal_penalty_flag = Column(Boolean, default=False)
    
    ip_address = Column(String(45), nullable=True)
    status = Column(String(30), default="ACTIVE_SHIFT") # ACTIVE_SHIFT, COMPLETED, APPROVED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    employee = relationship("Employee", foreign_keys=[employee_id])

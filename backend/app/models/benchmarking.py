from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


class JobLevel(str, Enum):
    L3_ENTRY = "L3"
    L4_MID = "L4"
    L5_SENIOR = "L5"
    L6_STAFF = "L6"
    L7_PRINCIPAL = "L7"


class GeoZone(str, Enum):
    US_BAY_AREA = "US_BAY_AREA"      # 1.25x
    US_NYC = "US_NYC"                # 1.20x
    US_TIER_2 = "US_TIER_2"          # 1.05x (Austin/Seattle)
    US_REMOTE = "US_REMOTE"          # 1.00x baseline
    EMEA_LONDON = "EMEA_LONDON"      # 0.95x USD equiv
    EMEA_BERLIN = "EMEA_BERLIN"      # 0.85x USD equiv
    APAC_TOKYO = "APAC_TOKYO"        # 0.80x USD equiv


class SalaryBenchmark(Base):
    __tablename__ = "salary_benchmarks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    job_level: Mapped[str] = mapped_column(String(10), default=JobLevel.L5_SENIOR.value)
    geo_zone: Mapped[str] = mapped_column(String(30), default=GeoZone.US_BAY_AREA.value)
    
    # Radford / Option Impact percentiles
    base_salary_p25: Mapped[float] = mapped_column(Float, nullable=False)
    base_salary_p50: Mapped[float] = mapped_column(Float, nullable=False)
    base_salary_p75: Mapped[float] = mapped_column(Float, nullable=False)
    base_salary_p90: Mapped[float] = mapped_column(Float, nullable=False)
    equity_shares_p50: Mapped[float] = mapped_column(Float, default=15000.0)
    variable_bonus_target_pct: Mapped[float] = mapped_column(Float, default=15.0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

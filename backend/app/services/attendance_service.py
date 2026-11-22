from datetime import datetime, timezone, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from backend.app.models.attendance import TimeSheetEntry
from backend.app.schemas.attendance import ClockInRequest, ClockOutRequest, AttendanceSummaryOut


class AttendanceService:
    @staticmethod
    async def clock_in(
        db: AsyncSession,
        org_id: str,
        employee_id: str,
        ip_address: Optional[str] = None,
        notes: Optional[str] = None
    ) -> TimeSheetEntry:
        # Check if already clocked in
        active_res = await db.execute(
            select(TimeSheetEntry).where(
                TimeSheetEntry.employee_id == employee_id,
                TimeSheetEntry.status == "ACTIVE_SHIFT"
            )
        )
        if active_res.scalar_one_or_none():
            raise ValueError("Employee is already clocked in to an active shift.")

        now = datetime.now(timezone.utc)
        entry = TimeSheetEntry(
            organization_id=org_id,
            employee_id=employee_id,
            shift_date=now.date(),
            clock_in=now,
            status="ACTIVE_SHIFT",
            ip_address=ip_address,
            notes=notes,
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def clock_out(
        db: AsyncSession,
        employee_id: str,
        meal_break_minutes: int = 30,
        notes: Optional[str] = None
    ) -> TimeSheetEntry:
        active_res = await db.execute(
            select(TimeSheetEntry).where(
                TimeSheetEntry.employee_id == employee_id,
                TimeSheetEntry.status == "ACTIVE_SHIFT"
            )
        )
        entry = active_res.scalar_one_or_none()
        if not entry:
            raise ValueError("No active shift found. Please clock in first.")

        now = datetime.now(timezone.utc)
        entry.clock_out = now
        entry.meal_break_minutes = meal_break_minutes
        if notes:
            entry.notes = f"{entry.notes or ''} | Out: {notes}".strip(" |")

        # Duration math
        duration_seconds = (now - entry.clock_in).total_seconds()
        total_worked_seconds = max(duration_seconds - (meal_break_minutes * 60), 0)
        total_hours = round(total_worked_seconds / 3600.0, 2)
        entry.total_hours = total_hours

        # Statutory Overtime Calculation (FLSA / CA rules)
        # Up to 8 hours: regular
        # > 8 and <= 12 hours: 1.5x overtime
        # > 12 hours: 2.0x double time
        if total_hours <= 8.0:
            entry.regular_hours = total_hours
            entry.overtime_hours = 0.0
            entry.double_time_hours = 0.0
        elif total_hours <= 12.0:
            entry.regular_hours = 8.0
            entry.overtime_hours = round(total_hours - 8.0, 2)
            entry.double_time_hours = 0.0
        else:
            entry.regular_hours = 8.0
            entry.overtime_hours = 4.0
            entry.double_time_hours = round(total_hours - 12.0, 2)

        # Statutory Meal Break Audit: Shift > 6.0 hours requires at least 30 min meal break
        if total_hours >= 6.0 and meal_break_minutes < 30:
            entry.meal_penalty_flag = True
        else:
            entry.meal_penalty_flag = False

        entry.status = "COMPLETED"
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def get_summary(
        db: AsyncSession,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> AttendanceSummaryOut:
        today = date.today()
        start = start_date or (today - timedelta(days=14))
        end = end_date or today

        res = await db.execute(
            select(TimeSheetEntry).where(
                TimeSheetEntry.employee_id == employee_id,
                TimeSheetEntry.shift_date >= start,
                TimeSheetEntry.shift_date <= end,
                TimeSheetEntry.status == "COMPLETED"
            )
        )
        shifts = res.scalars().all()

        reg_h = round(sum(s.regular_hours for s in shifts), 2)
        ot_h = round(sum(s.overtime_hours for s in shifts), 2)
        dt_h = round(sum(s.double_time_hours for s in shifts), 2)
        penalties = sum(1 for s in shifts if s.meal_penalty_flag)
        payable_hours = round(reg_h + (ot_h * 1.5) + (dt_h * 2.0) + (penalties * 1.0), 2)

        return AttendanceSummaryOut(
            employee_id=employee_id,
            period_start=start,
            period_end=end,
            total_shifts=len(shifts),
            total_regular_hours=reg_h,
            total_overtime_hours=ot_h,
            total_double_time_hours=dt_h,
            meal_penalty_violations=penalties,
            estimated_payable_hours=payable_hours,
        )

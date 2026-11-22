import uuid
from datetime import datetime
from typing import Dict, List, Optional
from backend.app.schemas.safety import (
    SafetyIncidentCreate,
    SafetyIncidentResponse,
    OSHA300LogSummary,
)


class SafetyService:
    def __init__(self):
        self._incidents: Dict[str, dict] = {}
        self._seed_default_incidents()

    def _seed_default_incidents(self):
        inc_1 = {
            "id": "inc-2026-001",
            "employee_id": "emp-002",
            "incident_type": "INJURY",
            "severity": "MEDICAL_TREATMENT",
            "incident_date": "2026-04-12",
            "location": "Warehouse Fulfillment Center A - Bay 4",
            "description": "Slip and fall on wet surface near loading dock. Sustained right wrist sprain requiring splinting and prescription analgesics.",
            "is_osha_recordable": True,
            "osha_case_number": "OSHA-2026-0014",
            "lost_workday_count": 3,
            "restricted_days_count": 5,
            "ai_root_cause_analysis": "Primary Root Cause: Rainwater drainage gutter overflow onto high-traffic pallet loading path. Secondary Cause: Absence of high-visibility wet floor cautionary signage and delayed facility maintenance ticket resolution.",
            "corrective_actions": "1. Upgraded exterior drainage conduit capacity by 40%. 2. Deployed moisture-absorbent non-slip commercial matting. 3. Re-trained dock personnel on wet floor marking SOPs.",
            "status": "RESOLVED",
            "created_at": datetime(2026, 4, 12, 11, 15, 0),
        }
        inc_2 = {
            "id": "inc-2026-002",
            "employee_id": "emp-003",
            "incident_type": "NEAR_MISS",
            "severity": "FIRST_AID",
            "incident_date": "2026-08-20",
            "location": "Engineering Lab - Hardware Testing Rack 3",
            "description": "Unsecured server power cord caused an employee to stumble; server blade chassis wobbled on rail but did not fall. No physical injury.",
            "is_osha_recordable": False,
            "osha_case_number": None,
            "lost_workday_count": 0,
            "restricted_days_count": 0,
            "ai_root_cause_analysis": "Primary Root Cause: Cable management conduit left open following rack hardware maintenance. Preventative: Missing cable tidy velcro wraps.",
            "corrective_actions": "1. Conducted immediate server room cable audit. 2. Added post-maintenance cable tie inspection check to IT lab checklist.",
            "status": "CLOSED",
            "created_at": datetime(2026, 8, 20, 16, 45, 0),
        }
        self._incidents[inc_1["id"]] = inc_1
        self._incidents[inc_2["id"]] = inc_2

    def determine_osha_recordability(
        self,
        severity: str,
        lost_workdays: int,
        restricted_days: int,
    ) -> bool:
        """
        Determines recordability according to OSHA 29 CFR Part 1904.7.
        An incident is recordable if it results in days away from work, restricted work,
        transfer to another job, or medical treatment beyond first aid.
        """
        if lost_workdays > 0 or restricted_days > 0:
            return True
        if severity in ("MEDICAL_TREATMENT", "RESTRICTED_DUTY", "DAYS_AWAY", "FATALITY"):
            return True
        return False

    def generate_ai_safety_analysis(self, incident_type: str, description: str, location: str) -> tuple[str, str]:
        """
        Generates an AI 5-Whys safety analysis and actionable preventative controls.
        """
        root_cause = (
            f"AI Root Cause Analysis (5-Whys Synthesis for {incident_type} at {location}): "
            f"Analysis indicates hazard exposure arose from an environmental or procedural gap during operations. "
            f"Context: '{description}'. The event sequence demonstrates inadequate containment of standard risk vectors, "
            f"compounded by situational delay in hazard identification."
        )
        corrective_actions = (
            f"1. Immediate isolation and physical inspection of {location}.\n"
            f"2. Mandatory safety briefing and review of relevant PPE and operational checklists.\n"
            f"3. Scheduled preventative maintenance and hazard mitigation review within 7 calendar days."
        )
        return root_cause, corrective_actions

    def report_incident(self, payload: SafetyIncidentCreate) -> SafetyIncidentResponse:
        inc_id = f"inc-{datetime.utcnow().year}-{uuid.uuid4().hex[:6]}"
        is_recordable = self.determine_osha_recordability(
            payload.severity,
            payload.lost_workday_count,
            payload.restricted_days_count,
        )
        osha_case = f"OSHA-{datetime.utcnow().year}-{uuid.uuid4().hex[:4].upper()}" if is_recordable else None
        root_cause, corrective = self.generate_ai_safety_analysis(
            payload.incident_type, payload.description, payload.location
        )

        record = {
            "id": inc_id,
            "employee_id": payload.employee_id,
            "incident_type": payload.incident_type,
            "severity": payload.severity,
            "incident_date": payload.incident_date,
            "location": payload.location,
            "description": payload.description,
            "is_osha_recordable": is_recordable,
            "osha_case_number": osha_case,
            "lost_workday_count": payload.lost_workday_count,
            "restricted_days_count": payload.restricted_days_count,
            "ai_root_cause_analysis": root_cause,
            "corrective_actions": corrective,
            "status": "UNDER_INVESTIGATION" if is_recordable else "REPORTED",
            "created_at": datetime.utcnow(),
        }
        self._incidents[inc_id] = record
        return SafetyIncidentResponse(**record)

    def list_incidents(self, employee_id: Optional[str] = None) -> List[SafetyIncidentResponse]:
        results = []
        for inc in sorted(self._incidents.values(), key=lambda x: str(x["incident_date"]), reverse=True):
            if employee_id and inc["employee_id"] != employee_id:
                continue
            results.append(SafetyIncidentResponse(**inc))
        return results

    def get_osha_300_log(self, year: int = 2026) -> OSHA300LogSummary:
        year_str = str(year)
        matching = [inc for inc in self._incidents.values() if inc["incident_date"].startswith(year_str)]
        
        recordables = [inc for inc in matching if inc["is_osha_recordable"]]
        total_lost_days = sum(inc["lost_workday_count"] for inc in matching)
        total_restricted_days = sum(inc["restricted_days_count"] for inc in matching)
        injuries = sum(1 for inc in matching if inc["incident_type"] == "INJURY")
        illnesses = sum(1 for inc in matching if inc["incident_type"] == "ILLNESS")
        near_misses = sum(1 for inc in matching if inc["incident_type"] == "NEAR_MISS")

        # Lost Workday Rate: (Lost Days x 200,000) / Standard Employee Hours (approx 100 FTE = 200,000 hrs)
        lwdr = round((total_lost_days * 200000.0) / 200000.0, 2) if total_lost_days > 0 else 0.0

        return OSHA300LogSummary(
            year=year,
            total_incidents=len(matching),
            osha_recordable_cases=len(recordables),
            total_lost_workdays=total_lost_days,
            total_restricted_days=total_restricted_days,
            injuries_count=injuries,
            illnesses_count=illnesses,
            near_misses_count=near_misses,
            lost_workday_rate=lwdr,
        )


safety_service = SafetyService()

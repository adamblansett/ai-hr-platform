import uuid
from datetime import datetime
from typing import Dict, List, Optional
from backend.app.schemas.expenses import (
    ExpenseReportCreate,
    ExpenseReportResponse,
    ExpenseItemCreate,
    ExpenseItemResponse,
    ExpenseAuditResult,
)


class ExpensePolicyLimits:
    MAX_MEAL_PER_DIEM = 75.0
    MAX_LODGING_RATE = 300.0
    RECEIPT_MANDATORY_THRESHOLD = 25.0
    ALCOHOL_KEYWORDS = ["alcohol", "beer", "wine", "cocktail", "bar tab", "liquor"]


class ExpensesService:
    def __init__(self):
        # In-memory storage for reports and items
        self._reports: Dict[str, dict] = {}
        self._items: Dict[str, dict] = {}
        self._seed_default_reports()

    def _seed_default_reports(self):
        rep_id = "rep-eng-q4-01"
        self._reports[rep_id] = {
            "id": rep_id,
            "employee_id": "emp-001",
            "title": "AWS re:Invent 2026 Conference Travel",
            "status": "APPROVED",
            "total_amount": 1420.50,
            "currency": "USD",
            "audit_status": "COMPLIANT",
            "audit_notes": "All receipts verified. Within conference travel budget.",
            "reimbursement_reference": "REIMB-20261118-8841",
            "created_at": datetime(2026, 11, 15, 10, 0, 0),
            "submitted_at": datetime(2026, 11, 16, 14, 0, 0),
            "approved_at": datetime(2026, 11, 17, 9, 30, 0),
        }
        item_1 = {
            "id": "item-101",
            "report_id": rep_id,
            "category": "TRAVEL",
            "amount": 650.00,
            "currency": "USD",
            "expense_date": "2026-11-12",
            "merchant": "United Airlines",
            "description": "Roundtrip SFO to LAS flight",
            "receipt_url": "https://storage.enterprise-hr.local/receipts/ua-fl-992.pdf",
            "is_compliant": True,
            "policy_flags": None,
        }
        item_2 = {
            "id": "item-102",
            "report_id": rep_id,
            "category": "LODGING",
            "amount": 620.50,
            "currency": "USD",
            "expense_date": "2026-11-14",
            "merchant": "Venetian Resort Las Vegas",
            "description": "2 nights hotel room block",
            "receipt_url": "https://storage.enterprise-hr.local/receipts/venetian-folio.pdf",
            "is_compliant": True,
            "policy_flags": None,
        }
        item_3 = {
            "id": "item-103",
            "report_id": rep_id,
            "category": "MEALS",
            "amount": 150.00,
            "currency": "USD",
            "expense_date": "2026-11-14",
            "merchant": "Mesa Grill",
            "description": "Team dinner attendees (4 engineers)",
            "receipt_url": "https://storage.enterprise-hr.local/receipts/mesa-dinner.pdf",
            "is_compliant": True,
            "policy_flags": None,
        }
        self._items[item_1["id"]] = item_1
        self._items[item_2["id"]] = item_2
        self._items[item_3["id"]] = item_3

    def create_report(self, payload: ExpenseReportCreate) -> ExpenseReportResponse:
        report_id = str(uuid.uuid4())
        total = sum(item.amount for item in payload.items)
        now = datetime.utcnow()

        self._reports[report_id] = {
            "id": report_id,
            "employee_id": payload.employee_id,
            "title": payload.title,
            "status": "DRAFT",
            "total_amount": round(total, 2),
            "currency": "USD",
            "audit_status": "PENDING",
            "audit_notes": None,
            "reimbursement_reference": None,
            "created_at": now,
            "submitted_at": None,
            "approved_at": None,
        }

        created_items = []
        for it in payload.items:
            item_id = str(uuid.uuid4())
            item_record = {
                "id": item_id,
                "report_id": report_id,
                "category": it.category,
                "amount": round(it.amount, 2),
                "currency": it.currency,
                "expense_date": it.expense_date,
                "merchant": it.merchant,
                "description": it.description,
                "receipt_url": it.receipt_url,
                "is_compliant": True,
                "policy_flags": None,
            }
            self._items[item_id] = item_record
            created_items.append(ExpenseItemResponse(**item_record))

        return ExpenseReportResponse(**self._reports[report_id], items=created_items)

    def get_report(self, report_id: str) -> Optional[ExpenseReportResponse]:
        rep = self._reports.get(report_id)
        if not rep:
            return None
        items = [
            ExpenseItemResponse(**it)
            for it in self._items.values()
            if it["report_id"] == report_id
        ]
        return ExpenseReportResponse(**rep, items=items)

    def list_reports(self, employee_id: Optional[str] = None) -> List[ExpenseReportResponse]:
        results = []
        for rep in sorted(self._reports.values(), key=lambda x: str(x["created_at"]), reverse=True):
            if employee_id and rep["employee_id"] != employee_id:
                continue
            items = [
                ExpenseItemResponse(**it)
                for it in self._items.values()
                if it["report_id"] == rep["id"]
            ]
            results.append(ExpenseReportResponse(**rep, items=items))
        return results

    def audit_report(self, report_id: str) -> ExpenseAuditResult:
        rep = self._reports.get(report_id)
        if not rep:
            raise ValueError(f"Report {report_id} not found")

        items = [it for it in self._items.values() if it["report_id"] == report_id]
        flags: List[str] = []
        remediation_actions: List[str] = []
        flagged_count = 0

        for it in items:
            item_flags = []
            # Check 1: Mandatory receipt above threshold
            if it["amount"] > ExpensePolicyLimits.RECEIPT_MANDATORY_THRESHOLD and not it.get("receipt_url"):
                item_flags.append(f"Missing mandatory receipt for {it['merchant']} (${it['amount']:.2f})")
                remediation_actions.append(f"Upload itemized receipt for {it['merchant']}.")

            # Check 2: Meal Per Diem
            if it["category"] == "MEALS" and it["amount"] > ExpensePolicyLimits.MAX_MEAL_PER_DIEM:
                item_flags.append(f"Meal expense at {it['merchant']} (${it['amount']:.2f}) exceeds $75.00 single-meal limit")
                remediation_actions.append(f"Provide attendee list or VP exception approval for {it['merchant']}.")

            # Check 3: Lodging Cap
            if it["category"] == "LODGING" and it["amount"] > ExpensePolicyLimits.MAX_LODGING_RATE:
                item_flags.append(f"Lodging rate (${it['amount']:.2f}) exceeds standard city rate cap ($300.00)")
                remediation_actions.append("Attach travel agency booking confirmation justifying room rate.")

            # Check 4: Alcohol check
            desc = (it.get("description") or "").lower()
            merchant = it["merchant"].lower()
            if any(kw in desc or kw in merchant for kw in ExpensePolicyLimits.ALCOHOL_KEYWORDS):
                item_flags.append(f"Alcohol policy review required for {it['merchant']}")
                remediation_actions.append("Confirm compliance with client entertainment policy.")

            # Check 5: Weekend check
            try:
                dt = datetime.strptime(it["expense_date"], "%Y-%m-%d")
                if dt.weekday() in (5, 6):  # Saturday or Sunday
                    item_flags.append(f"Expense date {it['expense_date']} occurs on a weekend")
                    remediation_actions.append("Confirm business purpose for weekend expense.")
            except Exception:
                pass

            if item_flags:
                it["is_compliant"] = False
                it["policy_flags"] = "; ".join(item_flags)
                flags.extend(item_flags)
                flagged_count += 1
            else:
                it["is_compliant"] = True
                it["policy_flags"] = None

        if flagged_count > 0:
            rep["audit_status"] = "FLAGGED"
            rep["audit_notes"] = f"Automated audit identified {flagged_count} policy flags requiring review."
        else:
            rep["audit_status"] = "COMPLIANT"
            rep["audit_notes"] = "All expenses fully compliant with travel and entertainment policies."

        return ExpenseAuditResult(
            report_id=report_id,
            overall_status=rep["audit_status"],
            total_audited=rep["total_amount"],
            flagged_items_count=flagged_count,
            flags=flags,
            remediation_actions=list(set(remediation_actions)),
        )

    def submit_report(self, report_id: str) -> ExpenseReportResponse:
        rep = self._reports.get(report_id)
        if not rep:
            raise ValueError(f"Report {report_id} not found")
        rep["status"] = "SUBMITTED"
        rep["submitted_at"] = datetime.utcnow()
        self.audit_report(report_id)
        return self.get_report(report_id)

    def approve_report(self, report_id: str) -> ExpenseReportResponse:
        rep = self._reports.get(report_id)
        if not rep:
            raise ValueError(f"Report {report_id} not found")
        rep["status"] = "APPROVED"
        rep["approved_at"] = datetime.utcnow()
        rep["reimbursement_reference"] = f"REIMB-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        return self.get_report(report_id)


expenses_service = ExpensesService()

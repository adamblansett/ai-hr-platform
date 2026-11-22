import uuid
from datetime import datetime
from typing import Dict, List, Optional
from backend.app.schemas.immigration import (
    ImmigrationCaseCreate,
    ImmigrationCaseResponse,
    ImmigrationDocumentResponse,
    CaseStatusUpdateRequest,
    RelocationDisbursementResult,
    ImmigrationSummary,
)


class ImmigrationService:
    def __init__(self):
        self._cases: Dict[str, dict] = {}
        self._documents: Dict[str, dict] = {}
        self._seed_default_cases()

    def _seed_default_cases(self):
        c1 = {
            "id": "case-h1b-2026-01",
            "employee_id": "emp-004",
            "employee_name": "Elena Rostova",
            "visa_type": "H1B",
            "case_status": "USCIS_SUBMITTED",
            "uscis_receipt_number": "WAC-26-901-44120",
            "uscis_center": "California Service Center (WAC)",
            "filing_date": "2026-05-15",
            "expiry_date": "2029-09-30",
            "assigned_attorney": "Fragomen, Del Rey, Bernsen & Loewy, LLP",
            "relocation_stipend_amount": 12000.0,
            "stipend_disbursed": True,
            "tax_gross_up_amount": 3840.0,
            "created_at": datetime(2026, 3, 10, 10, 0, 0),
        }
        c2 = {
            "id": "case-o1-2026-02",
            "employee_id": "emp-001",
            "employee_name": "Alex Chen",
            "visa_type": "O1",
            "case_status": "APPROVED",
            "uscis_receipt_number": "LIN-26-881-19042",
            "uscis_center": "Nebraska Service Center (LIN)",
            "filing_date": "2026-01-20",
            "expiry_date": "2028-01-20",
            "assigned_attorney": "BAL Global Immigration",
            "relocation_stipend_amount": 10000.0,
            "stipend_disbursed": True,
            "tax_gross_up_amount": 3200.0,
            "created_at": datetime(2026, 1, 5, 14, 0, 0),
        }
        self._cases[c1["id"]] = c1
        self._cases[c2["id"]] = c2

        d1 = {
            "id": "doc-01",
            "case_id": c1["id"],
            "document_type": "PASSPORT",
            "document_name": "Elena_Rostova_Passport_Bio.pdf",
            "document_url": "https://storage.enterprise-hr.local/immigration/elena-passport.pdf",
            "is_verified": True,
            "uploaded_at": datetime(2026, 3, 12, 11, 0, 0),
        }
        d2 = {
            "id": "doc-02",
            "case_id": c1["id"],
            "document_type": "LCA",
            "document_name": "ETA-9035_Certified_LCA_2026.pdf",
            "document_url": "https://storage.enterprise-hr.local/immigration/lca-certified.pdf",
            "is_verified": True,
            "uploaded_at": datetime(2026, 4, 1, 9, 30, 0),
        }
        self._documents[d1["id"]] = d1
        self._documents[d2["id"]] = d2

    def list_cases(self, employee_id: Optional[str] = None) -> List[ImmigrationCaseResponse]:
        results = []
        for case in self._cases.values():
            if employee_id and case["employee_id"] != employee_id:
                continue
            docs = [
                ImmigrationDocumentResponse(**d)
                for d in self._documents.values()
                if d["case_id"] == case["id"]
            ]
            results.append(ImmigrationCaseResponse(**case, documents=docs))
        return results

    def create_case(self, payload: ImmigrationCaseCreate) -> ImmigrationCaseResponse:
        case_id = f"case-{payload.visa_type.lower()}-{uuid.uuid4().hex[:6]}"
        gross_up = round(payload.relocation_stipend_amount * 0.32, 2)
        record = {
            "id": case_id,
            "employee_id": payload.employee_id,
            "employee_name": "Enrolled Employee",
            "visa_type": payload.visa_type,
            "case_status": "INTAKE",
            "uscis_receipt_number": payload.uscis_receipt_number,
            "uscis_center": payload.uscis_center,
            "filing_date": payload.filing_date,
            "expiry_date": payload.expiry_date,
            "assigned_attorney": payload.assigned_attorney or "Fragomen, Del Rey, Bernsen & Loewy, LLP",
            "relocation_stipend_amount": payload.relocation_stipend_amount,
            "stipend_disbursed": False,
            "tax_gross_up_amount": gross_up,
            "created_at": datetime.utcnow(),
        }
        self._cases[case_id] = record
        return ImmigrationCaseResponse(**record, documents=[])

    def update_case_status(self, case_id: str, payload: CaseStatusUpdateRequest) -> ImmigrationCaseResponse:
        case = self._cases.get(case_id)
        if not case:
            raise ValueError(f"Immigration case {case_id} not found")

        case["case_status"] = payload.new_status
        if payload.uscis_receipt_number:
            case["uscis_receipt_number"] = payload.uscis_receipt_number

        docs = [
            ImmigrationDocumentResponse(**d)
            for d in self._documents.values()
            if d["case_id"] == case_id
        ]
        return ImmigrationCaseResponse(**case, documents=docs)

    def disburse_relocation_stipend(self, case_id: str) -> RelocationDisbursementResult:
        case = self._cases.get(case_id)
        if not case:
            raise ValueError(f"Immigration case {case_id} not found")

        case["stipend_disbursed"] = True
        total_payable = case["relocation_stipend_amount"] + case["tax_gross_up_amount"]
        ref = f"STIPEND-RELOC-{uuid.uuid4().hex[:8].upper()}"

        return RelocationDisbursementResult(
            case_id=case_id,
            stipend_amount=case["relocation_stipend_amount"],
            tax_gross_up_amount=case["tax_gross_up_amount"],
            total_payable=total_payable,
            disbursement_reference=ref,
            message=f"Relocation disbursement executed. Total net stipend ${case['relocation_stipend_amount']:,.2f} + ${case['tax_gross_up_amount']:,.2f} tax gross-up paid via payroll ACH reference {ref}.",
        )

    def get_immigration_summary(self) -> ImmigrationSummary:
        total = len(self._cases)
        pending = sum(1 for c in self._cases.values() if c["case_status"] in ("USCIS_SUBMITTED", "DRAFTING"))
        outlay = sum(c["relocation_stipend_amount"] for c in self._cases.values() if c["stipend_disbursed"])

        return ImmigrationSummary(
            active_cases=total,
            pending_uscis_receipts=pending,
            expiring_within_90_days_count=0,
            total_relocation_outlay=round(outlay, 2),
        )


immigration_service = ImmigrationService()

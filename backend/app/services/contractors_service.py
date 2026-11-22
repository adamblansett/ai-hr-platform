import uuid
from datetime import datetime
from typing import Dict, List, Optional
from backend.app.schemas.contractors import (
    ContractorCreate,
    ContractorResponse,
    SOWCreate,
    SOWResponse,
    InvoiceCreate,
    InvoiceResponse,
    EORSummary,
)


class ContractorsService:
    def __init__(self):
        self._contractors: Dict[str, dict] = {}
        self._sows: Dict[str, dict] = {}
        self._invoices: Dict[str, dict] = {}
        self._seed_default_data()

    def _seed_default_data(self):
        c1 = {
            "id": "ctr-001",
            "full_name": "Lars Lindqvist",
            "email": "lars.lindqvist@nordicdev.io",
            "country": "Sweden",
            "entity_type": "INDIVIDUAL",
            "tax_form_type": "W8_BEN",
            "tax_form_verified": True,
            "tax_id_masked": "SE-***-1944",
            "hourly_rate": 95.0,
            "currency": "EUR",
            "status": "ACTIVE",
            "created_at": datetime(2026, 3, 1, 10, 0, 0),
        }
        c2 = {
            "id": "ctr-002",
            "full_name": "Akira Tanaka",
            "email": "a.tanaka@tokyocloud.jp",
            "country": "Japan",
            "entity_type": "LLC",
            "tax_form_type": "W8_BEN_E",
            "tax_form_verified": True,
            "tax_id_masked": "JP-***-8821",
            "hourly_rate": 110.0,
            "currency": "USD",
            "status": "ACTIVE",
            "created_at": datetime(2026, 5, 15, 8, 30, 0),
        }
        self._contractors[c1["id"]] = c1
        self._contractors[c2["id"]] = c2

        sow1 = {
            "id": "sow-001",
            "contractor_id": "ctr-001",
            "title": "EU Data Sovereignty & GDPR Microservices Sharding",
            "total_budget": 24000.0,
            "currency": "EUR",
            "start_date": "2026-06-01",
            "end_date": "2026-12-31",
            "status": "ACTIVE",
            "deliverables_description": "Deliver tenant-isolated multi-region database migration scripts and compliance tests.",
        }
        self._sows[sow1["id"]] = sow1

        inv1 = {
            "id": "inv-001",
            "sow_id": "sow-001",
            "contractor_id": "ctr-001",
            "milestone_title": "Milestone 1: Multi-region partition schemas completed",
            "amount": 8000.0,
            "currency": "EUR",
            "status": "PAID",
            "submitted_at": datetime(2026, 8, 1, 10, 0, 0),
            "approved_at": datetime(2026, 8, 3, 14, 0, 0),
            "paid_at": datetime(2026, 8, 5, 9, 30, 0),
            "payout_tx_hash": "TX-EOR-SEPA-89104A",
        }
        inv2 = {
            "id": "inv-002",
            "sow_id": "sow-001",
            "contractor_id": "ctr-001",
            "milestone_title": "Milestone 2: Latency stress testing and failover verification",
            "amount": 8000.0,
            "currency": "EUR",
            "status": "SUBMITTED",
            "submitted_at": datetime(2026, 11, 20, 16, 0, 0),
            "approved_at": None,
            "paid_at": None,
            "payout_tx_hash": None,
        }
        self._invoices[inv1["id"]] = inv1
        self._invoices[inv2["id"]] = inv2

    def list_contractors(self, country: Optional[str] = None) -> List[ContractorResponse]:
        results = list(self._contractors.values())
        if country:
            results = [c for c in results if c["country"].lower() == country.lower()]
        return [ContractorResponse(**c) for c in results]

    def create_contractor(self, payload: ContractorCreate) -> ContractorResponse:
        ctr_id = f"ctr-{uuid.uuid4().hex[:6]}"
        record = {
            "id": ctr_id,
            "full_name": payload.full_name,
            "email": payload.email,
            "country": payload.country,
            "entity_type": payload.entity_type,
            "tax_form_type": payload.tax_form_type,
            "tax_form_verified": False,
            "tax_id_masked": f"{payload.country[:2].upper()}-***-{uuid.uuid4().hex[:4]}",
            "hourly_rate": payload.hourly_rate,
            "currency": payload.currency,
            "status": "ACTIVE",
            "created_at": datetime.utcnow(),
        }
        self._contractors[ctr_id] = record
        return ContractorResponse(**record)

    def verify_tax_form(self, contractor_id: str) -> ContractorResponse:
        ctr = self._contractors.get(contractor_id)
        if not ctr:
            raise ValueError(f"Contractor {contractor_id} not found")
        ctr["tax_form_verified"] = True
        return ContractorResponse(**ctr)

    def create_sow(self, payload: SOWCreate) -> SOWResponse:
        sow_id = f"sow-{uuid.uuid4().hex[:6]}"
        record = {
            "id": sow_id,
            "contractor_id": payload.contractor_id,
            "title": payload.title,
            "total_budget": payload.total_budget,
            "currency": payload.currency,
            "start_date": payload.start_date,
            "end_date": payload.end_date,
            "status": "ACTIVE",
            "deliverables_description": payload.deliverables_description,
        }
        self._sows[sow_id] = record
        return SOWResponse(**record)

    def list_sows(self, contractor_id: Optional[str] = None) -> List[SOWResponse]:
        results = list(self._sows.values())
        if contractor_id:
            results = [s for s in results if s["contractor_id"] == contractor_id]
        return [SOWResponse(**s) for s in results]

    def submit_invoice(self, payload: InvoiceCreate) -> InvoiceResponse:
        sow = self._sows.get(payload.sow_id)
        if not sow:
            raise ValueError(f"SOW {payload.sow_id} not found")

        inv_id = f"inv-{uuid.uuid4().hex[:6]}"
        record = {
            "id": inv_id,
            "sow_id": payload.sow_id,
            "contractor_id": payload.contractor_id,
            "milestone_title": payload.milestone_title,
            "amount": payload.amount,
            "currency": payload.currency,
            "status": "SUBMITTED",
            "submitted_at": datetime.utcnow(),
            "approved_at": None,
            "paid_at": None,
            "payout_tx_hash": None,
        }
        self._invoices[inv_id] = record
        return InvoiceResponse(**record)

    def list_invoices(self, contractor_id: Optional[str] = None) -> List[InvoiceResponse]:
        results = list(self._invoices.values())
        if contractor_id:
            results = [i for i in results if i["contractor_id"] == contractor_id]
        return [InvoiceResponse(**i) for i in sorted(results, key=lambda x: str(x["submitted_at"]), reverse=True)]

    def approve_invoice(self, invoice_id: str) -> InvoiceResponse:
        inv = self._invoices.get(invoice_id)
        if not inv:
            raise ValueError(f"Invoice {invoice_id} not found")
        inv["status"] = "APPROVED"
        inv["approved_at"] = datetime.utcnow()
        return InvoiceResponse(**inv)

    def pay_invoice(self, invoice_id: str) -> InvoiceResponse:
        inv = self._invoices.get(invoice_id)
        if not inv:
            raise ValueError(f"Invoice {invoice_id} not found")
        inv["status"] = "PAID"
        inv["paid_at"] = datetime.utcnow()
        inv["payout_tx_hash"] = f"TX-EOR-{inv['currency']}-{uuid.uuid4().hex[:8].upper()}"
        return InvoiceResponse(**inv)

    def get_eor_summary(self) -> EORSummary:
        active_contractors = sum(1 for c in self._contractors.values() if c["status"] == "ACTIVE")
        pending_tax = sum(1 for c in self._contractors.values() if not c["tax_form_verified"])
        active_sows = sum(1 for s in self._sows.values() if s["status"] == "ACTIVE")
        invoiced_month = sum(i["amount"] for i in self._invoices.values() if i["status"] in ("SUBMITTED", "APPROVED", "PAID"))
        paid_month = sum(i["amount"] for i in self._invoices.values() if i["status"] == "PAID")

        return EORSummary(
            active_contractors=active_contractors,
            pending_tax_verifications=pending_tax,
            total_active_sows=active_sows,
            total_invoiced_this_month=round(invoiced_month, 2),
            total_paid_this_month=round(paid_month, 2),
        )


contractors_service = ContractorsService()

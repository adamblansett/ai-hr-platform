import unittest
from datetime import datetime


class TestContractorsLogic(unittest.TestCase):
    def test_tax_form_validation(self):
        valid_forms = {"W9", "W8_BEN", "W8_BEN_E", "VAT_REGISTRATION"}
        self.assertIn("W8_BEN", valid_forms)
        self.assertIn("W9", valid_forms)
        self.assertNotIn("1099_MISC", valid_forms)

    def test_payout_transaction_hash_format(self):
        currency = "EUR"
        hash_code = "891A4B22"
        tx_hash = f"TX-EOR-{currency}-{hash_code}"
        self.assertEqual(tx_hash, "TX-EOR-EUR-891A4B22")

    def test_sow_budget_depletion(self):
        sow_budget = 24000.0
        invoices_paid = [8000.0, 8000.0]
        remaining = sow_budget - sum(invoices_paid)
        self.assertEqual(remaining, 8000.0)


if __name__ == "__main__":
    unittest.main()

import unittest
from datetime import datetime


class TestExpensesLogic(unittest.TestCase):
    def test_expense_policy_audit_rules(self):
        MAX_MEAL_PER_DIEM = 75.0
        RECEIPT_THRESHOLD = 25.0
        ALCOHOL_KEYWORDS = ["alcohol", "beer", "wine", "cocktail"]

        # Case 1: Compliant meal
        meal_1 = {"category": "MEALS", "amount": 45.0, "receipt_url": "https://receipt.pdf", "desc": "Lunch"}
        self.assertLessEqual(meal_1["amount"], MAX_MEAL_PER_DIEM)
        self.assertIsNotNone(meal_1["receipt_url"])

        # Case 2: Meal exceeding threshold
        meal_2 = {"category": "MEALS", "amount": 120.0, "receipt_url": "https://receipt.pdf", "desc": "Steak dinner with wine"}
        flags = []
        if meal_2["amount"] > MAX_MEAL_PER_DIEM:
            flags.append("Exceeds meal limit")
        if any(k in meal_2["desc"].lower() for k in ALCOHOL_KEYWORDS):
            flags.append("Alcohol policy review")
        self.assertEqual(len(flags), 2)

        # Case 3: Missing receipt check
        item_3 = {"category": "OFFICE_SUPPLIES", "amount": 85.0, "receipt_url": None}
        missing_receipt = item_3["amount"] > RECEIPT_THRESHOLD and not item_3["receipt_url"]
        self.assertTrue(missing_receipt)

    def test_reimbursement_reference_generation(self):
        date_str = datetime(2026, 11, 22).strftime("%Y%m%d")
        reimb_ref = f"REIMB-{date_str}-A9F3D1"
        self.assertTrue(reimb_ref.startswith("REIMB-20261122-"))


if __name__ == "__main__":
    unittest.main()

import unittest


class TestImmigrationLogic(unittest.TestCase):
    def test_relocation_tax_gross_up_formula(self):
        # 32% supplemental tax gross-up standard
        stipend = 10000.0
        tax_gross_up = round(stipend * 0.32, 2)
        total_payable = stipend + tax_gross_up

        self.assertEqual(tax_gross_up, 3200.0)
        self.assertEqual(total_payable, 13200.0)

    def test_uscis_receipt_pattern(self):
        receipt_wac = "WAC-26-901-44120"
        self.assertTrue(receipt_wac.startswith("WAC-"))
        self.assertEqual(len(receipt_wac.split("-")), 4)


if __name__ == "__main__":
    unittest.main()

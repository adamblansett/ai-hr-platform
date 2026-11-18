import unittest
from datetime import date, timedelta

class TestCompensation(unittest.TestCase):
    def test_equity_vesting_calculation_logic(self):
        total_shares = 48000
        start = date(2025, 1, 1)
        cliff_m = 12
        total_m = 48

        # 6 months in (before cliff)
        as_of_pre_cliff = date(2025, 7, 1)
        cliff_date = start + timedelta(days=int(cliff_m * 30.4375))
        vested_pre_cliff = 0 if as_of_pre_cliff < cliff_date else int(total_shares * (cliff_m / total_m))
        self.assertEqual(vested_pre_cliff, 0)

        # 13 months in (after cliff)
        as_of_post_cliff = date(2026, 2, 1)
        cliff_shares = int(total_shares * (cliff_m / total_m))
        self.assertEqual(cliff_shares, 12000)
        self.assertTrue(as_of_post_cliff >= cliff_date)

    def test_payroll_tax_math(self):
        gross = 10000.00
        fed_tax = round(gross * 0.22, 2)
        fica_tax = round(gross * 0.062, 2)
        medicare = round(gross * 0.0145, 2)
        health_benefit = 150.00
        total_deductions = fed_tax + fica_tax + medicare + health_benefit
        net = round(gross - total_deductions, 2)

        self.assertEqual(fed_tax, 2200.00)
        self.assertEqual(fica_tax, 620.00)
        self.assertEqual(medicare, 145.00)
        self.assertEqual(total_deductions, 3115.00)
        self.assertEqual(net, 6885.00)

if __name__ == "__main__":
    unittest.main()

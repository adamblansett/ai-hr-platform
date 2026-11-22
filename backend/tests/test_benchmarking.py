import unittest


class TestBenchmarkingLogic(unittest.TestCase):
    def test_compa_ratio_and_band_position(self):
        market_p50 = 185000.0

        # Case 1: Below range (< 0.85)
        salary_low = 150000.0
        ratio_low = round(salary_low / market_p50, 3)
        self.assertLess(ratio_low, 0.85)

        # Case 2: At market (0.95 - 1.05)
        salary_mid = 180000.0
        ratio_mid = round(salary_mid / market_p50, 3)
        self.assertTrue(0.95 <= ratio_mid <= 1.05)

        # Case 3: Suggested merit adjustment calculation
        adjustment = market_p50 - salary_low
        self.assertEqual(adjustment, 35000.0)

    def test_geographic_cost_of_labor_multiplier(self):
        base_rate = 150000.0
        geo_multipliers = {
            "US_BAY_AREA": 1.25,
            "US_NYC": 1.20,
            "US_TIER_2": 1.05,
            "US_REMOTE": 1.00,
        }
        self.assertEqual(base_rate * geo_multipliers["US_BAY_AREA"], 187500.0)
        self.assertEqual(base_rate * geo_multipliers["US_TIER_2"], 157500.0)


if __name__ == "__main__":
    unittest.main()

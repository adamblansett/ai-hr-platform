import unittest

class TestBenefits(unittest.TestCase):
    def test_coverage_tier_multipliers(self):
        base_employee_premium = 100.0
        multiplier_map = {
            "EMPLOYEE_ONLY": 1.0,
            "EMPLOYEE_PLUS_SPOUSE": 1.8,
            "EMPLOYEE_PLUS_CHILDREN": 1.7,
            "FAMILY": 2.5,
        }

        self.assertEqual(base_employee_premium * multiplier_map["EMPLOYEE_ONLY"], 100.0)
        self.assertEqual(base_employee_premium * multiplier_map["EMPLOYEE_PLUS_SPOUSE"], 180.0)
        self.assertEqual(base_employee_premium * multiplier_map["FAMILY"], 250.0)

    def test_advisor_recommendation_logic(self):
        def recommend_plan(has_hsa_preference: bool, family_size: int):
            if has_hsa_preference or family_size == 1:
                return "Acme Anthem HDHP with HSA Contribution"
            return "Acme Anthem Platinum PPO 500"

        self.assertEqual(recommend_plan(True, 1), "Acme Anthem HDHP with HSA Contribution")
        self.assertEqual(recommend_plan(False, 4), "Acme Anthem Platinum PPO 500")

if __name__ == "__main__":
    unittest.main()

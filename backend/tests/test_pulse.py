import unittest
import hashlib

class TestPulseService(unittest.TestCase):
    def test_respondent_hash_decoupling(self):
        salt = "test_salt"
        user_1 = "emp-101"
        survey_1 = "surv-A"

        h1 = hashlib.sha256(f"{user_1}:{survey_1}:{salt}".encode("utf-8")).hexdigest()
        h2 = hashlib.sha256(f"{user_1}:{survey_1}:{salt}".encode("utf-8")).hexdigest()
        h3 = hashlib.sha256(f"emp-102:{survey_1}:{salt}".encode("utf-8")).hexdigest()

        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)
        self.assertNotIn(user_1, h1)

    def test_enps_calculation_formula(self):
        ratings = [5, 5, 4, 4, 3, 3, 2, 1, 5, 4] # total 10
        # Promoters (4-5): 6, Detractors (1-2): 2, Passives (3): 2
        promoters = sum(1 for r in ratings if r >= 4)
        detractors = sum(1 for r in ratings if r <= 2)
        enps = round(((promoters - detractors) / len(ratings)) * 100, 1)

        self.assertEqual(promoters, 6)
        self.assertEqual(detractors, 2)
        self.assertEqual(enps, 40.0)

if __name__ == "__main__":
    unittest.main()

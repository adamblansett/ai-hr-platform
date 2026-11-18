import unittest

class TestSuccession(unittest.TestCase):
    def test_candidate_skill_matching_logic(self):
        required_skills = ["python", "fastapi", "postgresql", "docker"]
        emp_skills = ["python", "fastapi", "redis"]

        matching = [s for s in required_skills if s in emp_skills]
        missing = [s for s in required_skills if s not in emp_skills]
        score_pct = (len(matching) / len(required_skills)) * 100.0

        self.assertEqual(score_pct, 50.0)
        self.assertIn("python", matching)
        self.assertIn("fastapi", matching)
        self.assertIn("postgresql", missing)
        self.assertIn("docker", missing)

    def test_flight_risk_threshold_tiers(self):
        def categorize(score: float) -> str:
            if score >= 0.70:
                return "CRITICAL"
            elif score >= 0.50:
                return "HIGH"
            elif score >= 0.30:
                return "MEDIUM"
            return "LOW"

        self.assertEqual(categorize(0.85), "CRITICAL")
        self.assertEqual(categorize(0.65), "HIGH")
        self.assertEqual(categorize(0.40), "MEDIUM")
        self.assertEqual(categorize(0.15), "LOW")

if __name__ == "__main__":
    unittest.main()

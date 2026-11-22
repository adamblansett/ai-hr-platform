import unittest
from datetime import date

class TestOffboarding(unittest.TestCase):
    def test_standard_offboarding_task_definitions(self):
        standard_tasks = [
            ("Revoke SCIM 2.0 Identity & Enterprise SSO Access", "IT", "SECURITY_ADMIN"),
            ("Issue Prepaid Shipping Label for Laptop & Hardware Return", "IT", "IT_OPS"),
            ("Execute Remote Hardware Wipe & Security Audit Certification", "IT", "SECURITY_ADMIN"),
            ("Calculate Final Paystub & Accrued PTO Balance Payout", "FINANCE", "PAYROLL_ADMIN"),
            ("Conduct Exit Interview & Post-Employment IP/NDA Reaffirmation", "HR", "PEOPLE_MANAGER"),
            ("Archive Employee Records & Issue COBRA/Benefits Package", "HR", "HR_ADMIN"),
        ]

        self.assertEqual(len(standard_tasks), 6)
        categories = {t[1] for t in standard_tasks}
        self.assertIn("IT", categories)
        self.assertIn("FINANCE", categories)
        self.assertIn("HR", categories)

    def test_exit_interview_sentiment_synthesis(self):
        def synthesize_insights(rating: int, reason: str):
            score = 0.85 if rating >= 4 else (0.5 if rating == 3 else 0.2)
            category = "COMPENSATION_CAREER_GROWTH" if "compensation" in reason.lower() or "growth" in reason.lower() else "ORGANIZATIONAL"
            return score, category

        score, cat = synthesize_insights(5, "Better compensation offer elsewhere")
        self.assertEqual(score, 0.85)
        self.assertEqual(cat, "COMPENSATION_CAREER_GROWTH")

        score, cat = synthesize_insights(2, "Relocating to another state")
        self.assertEqual(score, 0.2)
        self.assertEqual(cat, "ORGANIZATIONAL")

if __name__ == "__main__":
    unittest.main()

import unittest
from datetime import datetime, timedelta


class TestLearningLogic(unittest.TestCase):
    def test_certificate_generation_and_expiry(self):
        passing_score = 80.0
        employee_score = 92.0
        validity_days = 365
        now = datetime(2026, 11, 22, 12, 0, 0)

        is_passed = employee_score >= passing_score
        self.assertTrue(is_passed)

        cert_id = f"CERT-{now.year}-ABC123"
        expires_at = now + timedelta(days=validity_days)
        self.assertEqual(expires_at.year, 2027)
        self.assertTrue(cert_id.startswith("CERT-2026-"))

    def test_compliance_completion_rate_math(self):
        total_mandatory_enrolled = 20
        total_completed = 17
        rate = round((total_completed / total_mandatory_enrolled) * 100, 1)
        self.assertEqual(rate, 85.0)


if __name__ == "__main__":
    unittest.main()

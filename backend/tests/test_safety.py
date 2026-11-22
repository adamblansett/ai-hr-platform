import unittest


class TestSafetyLogic(unittest.TestCase):
    def determine_osha_recordability(self, severity: str, lost_workdays: int, restricted_days: int) -> bool:
        if lost_workdays > 0 or restricted_days > 0:
            return True
        if severity in ("MEDICAL_TREATMENT", "RESTRICTED_DUTY", "DAYS_AWAY", "FATALITY"):
            return True
        return False

    def test_osha_recordability_criteria(self):
        # First aid with 0 days away is not OSHA recordable
        self.assertFalse(self.determine_osha_recordability("FIRST_AID", 0, 0))

        # Medical treatment beyond first aid is recordable
        self.assertTrue(self.determine_osha_recordability("MEDICAL_TREATMENT", 0, 0))

        # Any lost workdays make it recordable
        self.assertTrue(self.determine_osha_recordability("FIRST_AID", 1, 0))

    def test_osha_300_lwdr_formula(self):
        # Lost Workday Rate: (Lost Days x 200,000) / Standard Employee Hours (approx 100 FTE = 200,000 hrs)
        total_lost_days = 4
        total_hours = 200000.0
        lwdr = round((total_lost_days * 200000.0) / total_hours, 2)
        self.assertEqual(lwdr, 4.0)


if __name__ == "__main__":
    unittest.main()

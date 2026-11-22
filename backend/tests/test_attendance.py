import unittest

class TestAttendance(unittest.TestCase):
    def test_overtime_and_double_time_split(self):
        def calculate_split(total_hours: float):
            if total_hours <= 8.0:
                return total_hours, 0.0, 0.0
            elif total_hours <= 12.0:
                return 8.0, round(total_hours - 8.0, 2), 0.0
            else:
                return 8.0, 4.0, round(total_hours - 12.0, 2)

        # Standard 8-hr shift
        reg, ot, dt = calculate_split(8.0)
        self.assertEqual((reg, ot, dt), (8.0, 0.0, 0.0))

        # 10-hr shift (2 hrs overtime)
        reg, ot, dt = calculate_split(10.0)
        self.assertEqual((reg, ot, dt), (8.0, 2.0, 0.0))

        # 14-hr shift (4 hrs overtime, 2 hrs double-time)
        reg, ot, dt = calculate_split(14.0)
        self.assertEqual((reg, ot, dt), (8.0, 4.0, 2.0))

    def test_meal_break_audit_penalty_flag(self):
        def check_penalty(shift_hours: float, meal_minutes: int) -> bool:
            return shift_hours >= 6.0 and meal_minutes < 30

        self.assertTrue(check_penalty(8.0, 15)) # Violation
        self.assertFalse(check_penalty(8.0, 30)) # Compliant
        self.assertFalse(check_penalty(5.0, 0)) # Under 6 hours: compliant

if __name__ == "__main__":
    unittest.main()

import unittest


class TestRecognitionLogic(unittest.TestCase):
    def test_kudos_points_transfer_math(self):
        sender_allowance = 150
        recipient_balance = 180
        transfer_points = 50

        # Simulate points transfer
        self.assertGreaterEqual(sender_allowance, transfer_points)
        sender_allowance -= transfer_points
        recipient_balance += transfer_points

        self.assertEqual(sender_allowance, 100)
        self.assertEqual(recipient_balance, 230)

    def test_reward_catalog_redemption_validation(self):
        user_balance = 520
        item_cost = 250

        self.assertGreaterEqual(user_balance, item_cost)
        user_balance -= item_cost
        self.assertEqual(user_balance, 270)

        # Insufficient funds check
        expensive_item_cost = 1000
        has_sufficient = user_balance >= expensive_item_cost
        self.assertFalse(has_sufficient)

    def test_milestone_award_scale(self):
        # 1 yr: 100, 3 yr: 300, 5 yr: 500
        def get_anniversary_award(years: int) -> int:
            return years * 100

        self.assertEqual(get_anniversary_award(3), 300)
        self.assertEqual(get_anniversary_award(5), 500)


if __name__ == "__main__":
    unittest.main()

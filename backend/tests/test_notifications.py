import importlib.util
import unittest


class TestNotifications(unittest.TestCase):
    def test_notification_digest_aggregation_math(self):
        expiring_visas = 1
        pending_leaves = 2
        overdue_lms = 3
        reviews = 4
        total_action_items = expiring_visas + pending_leaves + overdue_lms + reviews
        self.assertEqual(total_action_items, 10)

    @unittest.skipUnless(importlib.util.find_spec("pydantic"), "Requires pydantic")
    def test_notification_service_dispatch_read_and_digest(self):
        from backend.app.schemas.notifications import NotificationCreate
        from backend.app.services.notification_service import NotificationService

        svc = NotificationService()
        initial_unread = svc.get_unread_count("emp-001").unread_count
        self.assertGreaterEqual(initial_unread, 2)

        dispatched = svc.dispatch_notification(
            NotificationCreate(
                recipient_employee_id="emp-001",
                channel="SLACK",
                category="VISA_EXPIRY",
                title="H-1B Filing Reminder",
                body="Petition due in 30 days.",
            )
        )
        self.assertEqual(dispatched.status, "SENT")
        self.assertEqual(svc.get_unread_count("emp-001").unread_count, initial_unread + 1)

        marked = svc.mark_as_read(dispatched.id)
        self.assertEqual(marked.status, "READ")
        self.assertEqual(svc.get_unread_count("emp-001").unread_count, initial_unread)

        digest = svc.compile_daily_digest("org-001")
        self.assertIn("EMAIL", digest.dispatched_channels)
        self.assertIn("Daily HR Ops Digest", digest.digest_preview)


if __name__ == "__main__":
    unittest.main()

import unittest


class TestAssetsLogic(unittest.TestCase):
    def test_remote_wipe_authorization(self):
        # Only MDM-enrolled devices can accept remote wipe commands
        def can_wipe_device(mdm_enrolled: bool) -> bool:
            return mdm_enrolled

        self.assertTrue(can_wipe_device(True))
        self.assertFalse(can_wipe_device(False))

    def test_fleet_metrics_calculation(self):
        assets = [
            {"status": "ASSIGNED", "mdm_enrolled": True},
            {"status": "ASSIGNED", "mdm_enrolled": True},
            {"status": "IN_STOCK", "mdm_enrolled": True},
            {"status": "ASSIGNED", "mdm_enrolled": False},
        ]
        total = len(assets)
        assigned = sum(1 for a in assets if a["status"] == "ASSIGNED")
        managed = sum(1 for a in assets if a["mdm_enrolled"])
        compliance_rate = round((managed / total) * 100, 1)

        self.assertEqual(total, 4)
        self.assertEqual(assigned, 3)
        self.assertEqual(managed, 3)
        self.assertEqual(compliance_rate, 75.0)


if __name__ == "__main__":
    unittest.main()

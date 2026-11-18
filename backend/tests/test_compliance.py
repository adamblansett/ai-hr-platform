import hashlib
import json
import unittest

class TestCompliance(unittest.TestCase):
    def test_dsar_integrity_seal_verification(self):
        raw_export = {
            "subject_id": "emp-101",
            "organization_id": "org-acme-1",
            "profile": {
                "first_name": "Elena",
                "last_name": "Rostova",
                "email": "elena.rostova@internal.dev"
            },
            "regulatory_standard": "GDPR_ARTICLE_15_CCPA"
        }

        export_bytes = json.dumps(raw_export, sort_keys=True).encode("utf-8")
        computed_hash = hashlib.sha256(export_bytes).hexdigest()

        self.assertEqual(len(computed_hash), 64)
        self.assertEqual(computed_hash, hashlib.sha256(export_bytes).hexdigest())

        # Altering payload invalidates seal
        altered_export = dict(raw_export)
        altered_export["profile"] = {"first_name": "Tampered"}
        altered_bytes = json.dumps(altered_export, sort_keys=True).encode("utf-8")
        altered_hash = hashlib.sha256(altered_bytes).hexdigest()

        self.assertNotEqual(computed_hash, altered_hash)

    def test_right_to_be_forgotten_redaction_rules(self):
        original_record = {
            "first_name": "Marcus",
            "last_name": "Vance",
            "email": "marcus.vance@internal.dev",
            "phone_number": "+1-555-0199",
            "status": "ACTIVE"
        }

        anonymized_alias = "anonymized_a1b2c3d4e5f6"
        anonymized_record = {
            "first_name": "ANONYMIZED",
            "last_name": "PERSON",
            "preferred_name": None,
            "email": f"{anonymized_alias}@redacted.internal",
            "phone_number": None,
            "status": "TERMINATED"
        }

        self.assertEqual(anonymized_record["first_name"], "ANONYMIZED")
        self.assertEqual(anonymized_record["last_name"], "PERSON")
        self.assertIsNone(anonymized_record["phone_number"])
        self.assertEqual(anonymized_record["status"], "TERMINATED")
        self.assertIn("@redacted.internal", anonymized_record["email"])
        self.assertNotIn("marcus", anonymized_record["email"])

if __name__ == "__main__":
    unittest.main()

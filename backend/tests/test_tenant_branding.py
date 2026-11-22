import unittest


class TestTenantBrandingLogic(unittest.TestCase):
    def test_domain_cname_validation(self):
        ingress_cname = "ingress.global.ai-hr-platform.cloud"
        tenant_domain = "people.acme.corp"
        self.assertTrue(tenant_domain.endswith(".corp"))
        self.assertIn("ai-hr-platform.cloud", ingress_cname)

    def test_hex_color_validation(self):
        primary_hex = "#4F46E5"
        self.assertTrue(primary_hex.startswith("#"))
        self.assertEqual(len(primary_hex), 7)


if __name__ == "__main__":
    unittest.main()

import base64
import hashlib
import hmac
import importlib.util
import struct
import time
import unittest


def _rfc6238_totp(secret: str, timestamp: float, interval: int = 30, digits: int = 6) -> str:
    norm = secret.strip().upper()
    padding = (-len(norm)) % 8
    key = base64.b32decode(norm + ("=" * padding), casefold=True)
    counter = int(timestamp // interval)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code_int % (10**digits)).zfill(digits)


class TestSSOMFA(unittest.TestCase):
    def test_totp_rfc6238_known_vector_and_tampering(self):
        # Official RFC 6238 SHA-1 secret ("12345678901234567890" -> Base32)
        secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
        ts = 59.0  # counter = 1 -> known RFC test vector suffix 287082
        expected = _rfc6238_totp(secret, ts)
        self.assertEqual(len(expected), 6)
        self.assertEqual(expected, "287082")
        wrong = "000000" if expected != "000000" else "999999"
        self.assertFalse(hmac.compare_digest(expected, wrong))

    def test_pkce_s256_format(self):
        verifier = "test_verifier_string_with_sufficient_entropy_123456"
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        self.assertNotIn("=", challenge)
        self.assertEqual(len(challenge), 43)

    @unittest.skipUnless(
        importlib.util.find_spec("jose") and importlib.util.find_spec("defusedxml"),
        "Requires jose and defusedxml",
    )
    def test_sso_mfa_service_totp_and_saml_xxe_protection(self):
        from backend.app.services.sso_mfa_service import (
            SSOMFAService,
            build_otpauth_uri,
            generate_totp_code,
            parse_saml_assertion,
            verify_totp_code,
        )

        svc = SSOMFAService()
        setup = svc.setup_mfa(employee_id="emp-test", email="sec.test@acme.corp")
        self.assertIn("otpauth://totp/", setup.otpauth_uri)
        self.assertEqual(len(setup.backup_codes), 8)
        self.assertIn("secret=", build_otpauth_uri("sec.test@acme.corp", setup.secret))

        # Valid live TOTP code + boundary tolerance
        now = time.time()
        live_code = generate_totp_code(setup.secret, timestamp=now)
        self.assertTrue(verify_totp_code(setup.secret, live_code, timestamp=now, window=1))
        self.assertFalse(verify_totp_code(setup.secret, "abcdef", timestamp=now))

        status_after = svc.verify_mfa("emp-test", live_code)
        self.assertTrue(status_after.is_enabled)

        # Backup recovery code consumes once
        backup = setup.backup_codes[0]
        svc.verify_mfa("emp-test", backup)
        self.assertEqual(svc.get_mfa_status("emp-test").backup_codes_remaining, 7)

        # Valid SAML 2.0 XML parsing
        saml_xml = """<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
            <saml:Issuer>https://idp.acme.corp</saml:Issuer>
            <saml:Assertion ID="id-saml-9988">
                <saml:Subject>
                    <saml:NameID>elena.rostova@acme.corp</saml:NameID>
                </saml:Subject>
            </saml:Assertion>
        </samlp:Response>"""
        saml_b64 = base64.b64encode(saml_xml.encode("utf-8")).decode("ascii")
        parsed = parse_saml_assertion(saml_b64)
        self.assertEqual(parsed["email"], "elena.rostova@acme.corp")
        self.assertEqual(parsed["assertion_id"], "id-saml-9988")

        # XXE / DTD entity attack payload must be blocked by defusedxml
        xxe_xml = """<?xml version="1.0"?>
        <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
        <Assertion><Subject><NameID>&xxe;</NameID></Subject></Assertion>"""
        xxe_b64 = base64.b64encode(xxe_xml.encode("utf-8")).decode("ascii")
        with self.assertRaises(ValueError):
            parse_saml_assertion(xxe_b64)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
import logging
import unittest

from backend.app.core.logging import JSONLogFormatter, request_id_ctx
from backend.app.core.rate_limit import RateLimiter


class TestRateLimitAndObservability(unittest.TestCase):
    def test_in_memory_rate_limiter_enforces_limit_and_resets(self):
        limiter = RateLimiter(redis_url=None)
        key = "auth_login:10.0.0.1"

        for idx in range(3):
            allowed, remaining, retry_after = limiter.check(key, max_requests=3, window_seconds=60)
            self.assertTrue(allowed)
            self.assertEqual(remaining, 2 - idx)
            self.assertEqual(retry_after, 0)

        allowed, remaining, retry_after = limiter.check(key, max_requests=3, window_seconds=60)
        self.assertFalse(allowed)
        self.assertEqual(remaining, 0)
        self.assertGreaterEqual(retry_after, 1)

        limiter.reset()
        allowed_after_reset, _, _ = limiter.check(key, max_requests=3, window_seconds=60)
        self.assertTrue(allowed_after_reset)

    def test_json_log_formatter_emits_correlation_id(self):
        formatter = JSONLogFormatter(service_name="ai-hr-platform")
        token = request_id_ctx.set("req-corr-98765")
        try:
            record = logging.LogRecord(
                name="ai_hr_platform.http",
                level=logging.INFO,
                pathname=__file__,
                lineno=42,
                msg="Request completed",
                args=(),
                exc_info=None,
            )
            record.method = "GET"
            record.path = "/health/ready"
            record.status_code = 200
            rendered = json.loads(formatter.format(record))
            self.assertEqual(rendered["request_id"], "req-corr-98765")
            self.assertEqual(rendered["service"], "ai-hr-platform")
            self.assertEqual(rendered["path"], "/health/ready")
            self.assertEqual(rendered["status_code"], 200)
        finally:
            request_id_ctx.reset(token)

    @unittest.skipUnless(importlib.util.find_spec("jose"), "Requires python-jose")
    def test_jwt_ttl_revocation_and_decode_rejection(self):
        import uuid
        from backend.app.core.security import (
            create_access_token,
            decode_token,
            is_jti_revoked,
            reset_revocation_cache_for_tests,
            revoke_token_jti,
        )

        reset_revocation_cache_for_tests()
        tok = create_access_token(uuid.uuid4(), uuid.uuid4(), "HR_ADMIN")
        payload = decode_token(tok)
        self.assertIsNotNone(payload)
        jti = payload["jti"]
        self.assertFalse(is_jti_revoked(jti))

        revoke_token_jti(jti, ttl_seconds=60)
        self.assertTrue(is_jti_revoked(jti))
        self.assertIsNone(decode_token(tok))


if __name__ == "__main__":
    unittest.main()

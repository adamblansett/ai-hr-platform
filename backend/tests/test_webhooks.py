import hashlib
import hmac
from backend.app.services.webhook_service import webhook_service

def test_webhook_hmac_verification_valid():
    secret = "test-webhook-secret-key"
    payload_body = b'{"event_id": "evt_123", "status": "offer_accepted"}'
    
    expected_digest = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
    
    # Test bare digest
    assert webhook_service.verify_signature(payload_body, expected_digest, secret) is True
    # Test 'sha256=' prefix
    assert webhook_service.verify_signature(payload_body, f"sha256={expected_digest}", secret) is True

def test_webhook_hmac_verification_tampered():
    secret = "test-webhook-secret-key"
    payload_body = b'{"event_id": "evt_123"}'
    tampered_body = b'{"event_id": "evt_123", "injected": true}'
    
    sig = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
    assert webhook_service.verify_signature(tampered_body, sig, secret) is False

def test_webhook_hmac_missing_header():
    assert webhook_service.verify_signature(b'{}', None) is False

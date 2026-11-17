from backend.app.services.pii_scrubber import PIIScrubber

def test_ssn_redaction():
    text = "Employee John Doe SSN is 123-45-6789 for tax processing."
    clean, found = PIIScrubber.redact(text)
    assert found is True
    assert "123-45-6789" not in clean
    assert "[SSN_REDACTED]" in clean

def test_credit_card_redaction():
    text = "Corporate card for expenses: 4111-2222-3333-4444"
    clean, found = PIIScrubber.redact(text)
    assert found is True
    assert "4111-2222-3333-4444" not in clean
    assert "[CREDIT_CARD_REDACTED]" in clean

def test_phone_and_email_redaction():
    text = "Reach out to candidate at alice.smith@gmail.com or 555-867-5309"
    clean, found = PIIScrubber.redact(text)
    assert found is True
    assert "alice.smith@gmail.com" not in clean
    assert "555-867-5309" not in clean

def test_clean_text_no_false_positive():
    text = "General corporate policy regarding quarterly performance and holidays."
    clean, found = PIIScrubber.redact(text)
    assert found is False
    assert clean == text

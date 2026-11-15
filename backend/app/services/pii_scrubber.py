import re
from typing import Dict, Tuple

class PIIScrubber:
    """
    Regex-based PII scrubber for masking sensitive employee identifiers
    before sending text to LLM inference or storing in audit logs.
    """
    PATTERNS: Dict[str, str] = {
        "SSN": r"\b(?!000|666|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "PHONE": r"\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b",
        "CREDIT_CARD": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
        "DOB": r"\b(0[1-9]|1[0-2])[\/\.-](0[1-9]|[12]\d|3[01])[\/\.-](19|20)\d{2}\b",
    }

    @classmethod
    def redact(cls, text: str) -> Tuple[str, bool]:
        """
        Returns redacted text and a boolean flag indicating if any PII was detected.
        """
        redacted = text
        pii_detected = False

        for pii_type, pattern in cls.PATTERNS.items():
            matches = list(re.finditer(pattern, redacted))
            if matches:
                pii_detected = True
                redacted = re.sub(pattern, f"[{pii_type}_REDACTED]", redacted)

        return redacted, pii_detected

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class JSONLogFormatter(logging.Formatter):
    """Structured JSON log formatter emitting correlation IDs for log aggregation."""

    def __init__(self, service_name: str = "ai-hr-platform"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx.get(),
            "service": self.service_name,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key in ("method", "path", "status_code", "duration_ms", "client_ip"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO", service_name: str = "ai-hr-platform") -> None:
    """Configure root logger with structured JSON output."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONLogFormatter(service_name=service_name))

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(numeric_level)

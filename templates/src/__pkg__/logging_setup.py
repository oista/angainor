# canon: LOG-1, LOG-2, LOG-3, LOG-4, LOG-5
"""Настройка логов — один раз в точке входа. Библиотеки только получают логгер.

    from __pkg__.logging_setup import configure_logging, run_id_var

    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format,
                      service="<project>", version=__version__)
    run_id_var.set(run.id)   # все записи этой операции получат run_id

В модулях:  logger = logging.getLogger(__name__)
Формат JSON-строки: angainor/schemas/log-event.schema.json
"""

from __future__ import annotations

import contextvars
import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

run_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("run_id", default=None)
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)

_STANDARD_ATTRS = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}
_SECRET_MARKERS = ("password", "secret", "token", "api_key", "apikey", "authorization", "cookie")


def _mask(key: str, value: Any) -> Any:
    return "***" if any(marker in key.lower() for marker in _SECRET_MARKERS) else value


class JsonFormatter(logging.Formatter):
    """Одна JSON-строка на событие (LOG-4); поля с «секретными» именами маскируются (LOG-5)."""

    def __init__(self, service: str, version: str) -> None:
        super().__init__()
        self.service = service
        self.version = version

    def format(self, record: logging.LogRecord) -> str:
        event: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "service": self.service,
            "version": self.version,
        }
        if run_id := run_id_var.get():
            event["run_id"] = run_id
        if request_id := request_id_var.get():
            event["request_id"] = request_id
        if error_code := getattr(record, "error_code", None):
            event["error_code"] = error_code
        extra = {
            key: _mask(key, value)
            for key, value in record.__dict__.items()
            if key not in _STANDARD_ATTRS and key != "error_code"
        }
        if extra:
            event["extra"] = extra
        if record.exc_info:
            event["exc"] = self.formatException(record.exc_info)
        return json.dumps(event, ensure_ascii=False, default=str)


def configure_logging(
    level: str = "INFO", fmt: str = "text", *, service: str = "<project>", version: str = "0.0.0"
) -> None:
    """Логи — в stdout (LOG-3): JSON в контейнерах, текст при локальной работе."""
    handler = logging.StreamHandler(sys.stdout)
    if fmt == "json":
        handler.setFormatter(JsonFormatter(service, version))
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())

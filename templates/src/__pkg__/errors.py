# canon: LOG-6, LOG-7, LOG-8, LOG-9, ARC-9
"""Базовая ошибка пакета и каталог ошибок модулей.

Источник каталога: ADR-0006 PRODATA. Формат: angainor/schemas/error-catalog.schema.json.

Правильно (LOG-6): перехватили — записали — передали дальше с кодом.

    try:
        client.fetch()
    except httpx.HTTPError as exc:
        logger.error("fetch failed", extra={"error_code": "example.fetch.UNAVAILABLE"})
        raise ExternalServiceError(str(exc), code="example.fetch.UNAVAILABLE") from exc
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

UNKNOWN_CODE = "platform.UNKNOWN"
_ASSETS = Path(__file__).resolve().parent / "assets"


class AppError(Exception):
    """Базовая ошибка пакета. Ловите её, а не Exception (LOG-7). Переименуйте под проект."""

    code: str = UNKNOWN_CODE

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code is not None:
            self.code = code


class ConfigError(AppError):
    """Неверная или неполная конфигурация."""


class ExternalServiceError(AppError):
    """Внешняя система недоступна или ответила ошибкой."""


class RuleViolation(AppError):
    """Данные прошли проверку формы, но нарушают предметное правило (ARC-9)."""


@dataclass(frozen=True)
class ErrorInfo:
    """То, что видит пользователь: код, заголовок, подсказка — без трассировки (LOG-8)."""

    code: str
    severity: str
    title: str
    hint: str
    http_status: int


_UNKNOWN = {
    "ru": ErrorInfo(
        UNKNOWN_CODE, "error", "Неизвестная ошибка", "Сообщите код и время разработчикам", 500
    ),
    "en": ErrorInfo(
        UNKNOWN_CODE, "error", "Unknown error", "Report the error code and time to developers", 500
    ),
}


@lru_cache(maxsize=1)
def _catalog() -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for path in sorted(_ASSETS.glob("*_errors.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        prefix = f"{data['module_id']}."
        for item in data["errors"]:
            if not item["code"].startswith(prefix):
                raise ValueError(f"{path.name}: код {item['code']} должен начинаться с {prefix}")
            entries[item["code"]] = item
    return entries


def describe(code: str, lang: str = "ru") -> ErrorInfo:
    """Описание ошибки по коду; неизвестный код — platform.UNKNOWN (LOG-9)."""
    item = _catalog().get(code)
    if item is None:
        return _UNKNOWN[lang]
    return ErrorInfo(
        code=item["code"],
        severity=item["severity"],
        title=item["title"][lang],
        hint=item["hint"][lang],
        http_status=int(item.get("http_status", 500)),
    )

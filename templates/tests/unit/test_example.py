# canon: TST-3, TST-6, TST-8, CFG-4, LAY-3
"""Пример: правило проверяется парой «проходит / падает».

Каждый тест читается как Подготовка → Действие → Проверка.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from __pkg__.errors import UNKNOWN_CODE, describe
from __pkg__.settings import Settings

VALID_ENV = {"APP_DB_URL": "postgresql://user@localhost:5432/db", "APP_WEB_SECRET_KEY": "s3cret"}


def _use_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, env: dict[str, str]) -> None:
    monkeypatch.chdir(tmp_path)  # не подхватывать локальный .env
    for key in VALID_ENV:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)


def test_settings_pass_with_valid_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Подготовка
    _use_env(monkeypatch, tmp_path, VALID_ENV)
    # Действие
    settings = Settings()  # type: ignore[call-arg]
    # Проверка
    assert settings.web_port == 8000


def test_settings_fail_with_empty_secret(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _use_env(monkeypatch, tmp_path, {**VALID_ENV, "APP_WEB_SECRET_KEY": ""})
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_unknown_error_code_falls_back_to_platform_unknown() -> None:
    info = describe("missing.area.NOPE")
    assert info.code == UNKNOWN_CODE

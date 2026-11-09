# canon: TST-1, LAY-3
"""Интеграционный тест: работает с настоящей базой (в CI — Postgres как сервис)."""

from __future__ import annotations

import os

import pytest


@pytest.mark.integration
def test_database_url_is_provided() -> None:
    # Замените на реальную проверку: подключение, миграции, запрос.
    assert os.environ.get("APP_DB_URL"), "APP_DB_URL не задан — интеграционные тесты требуют базу"

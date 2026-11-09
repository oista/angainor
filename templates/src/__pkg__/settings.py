# canon: CFG-1, CFG-3, CFG-4, CFG-5, CFG-6, ARC-9
"""Настройки приложения: один типизированный объект, проверка при запуске.

APP — заменить на префикс проекта из config-contract Norma.

    python -m __pkg__.settings --check              # загрузить и проверить настройки
    python -m __pkg__.settings --check-env-example  # сверить схему, .env.example и Settings
"""

from __future__ import annotations

import argparse
import sys
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs" / "architecture" / "config-schema.yaml"
ENV_EXAMPLE_PATH = ROOT / ".env.example"


class Settings(BaseSettings):
    """Все переменные окружения проекта. Создаётся один раз в точке входа (CFG-5)."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", frozen=True
    )

    env: Literal["dev", "stage", "prod"] = Field(default="dev", alias="PD_ENV")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", alias="PD_LOG_LEVEL"
    )
    log_format: Literal["text", "json"] = Field(default="text", alias="PD_LOG_FORMAT")

    db_url: str = Field(alias="APP_DB_URL")  # обязательна: значения по умолчанию нет
    web_host: str = Field(default="127.0.0.1", alias="APP_WEB_HOST")
    web_port: int = Field(default=8000, alias="APP_WEB_PORT")
    web_secret_key: SecretStr = Field(alias="APP_WEB_SECRET_KEY")  # секрет без умолчания (CFG-6)

    @field_validator("web_secret_key")
    @classmethod
    def _secret_not_empty(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("секрет не задан")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # значения приходят из окружения


def _env_example_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            keys.add(line.split("=", 1)[0].strip())
    return keys


def _schema_keys(path: Path) -> set[str]:
    import yaml  # только для проверки, в рантайме не нужен

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {str(item["name"]) for item in data.get("variables", [])}


def _settings_keys() -> set[str]:
    return {field.alias for field in Settings.model_fields.values() if field.alias}


def check_env_example() -> list[str]:
    """Схема — источник правды; .env.example и Settings должны с ней совпадать (CFG-3)."""
    schema = _schema_keys(SCHEMA_PATH)
    problems: list[str] = []
    sources = (
        (".env.example", _env_example_keys(ENV_EXAMPLE_PATH)),
        ("Settings", _settings_keys()),
    )
    for where, keys in sources:
        problems += [f"{k}: есть в схеме, нет в {where}" for k in sorted(schema - keys)]
        problems += [f"{k}: есть в {where}, нет в схеме" for k in sorted(keys - schema)]
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--check", action="store_true", help="загрузить и проверить настройки")
    parser.add_argument(
        "--check-env-example", action="store_true", help="сверить схему, .env.example и Settings"
    )
    args = parser.parse_args(argv)

    if args.check_env_example:
        problems = check_env_example()
        if problems:
            print("Схема конфигурации расходится:\n  " + "\n  ".join(problems), file=sys.stderr)
            return 1
        print("Схема, .env.example и Settings совпадают")

    if args.check or not args.check_env_example:
        try:
            Settings()  # type: ignore[call-arg]
        except ValidationError as exc:
            print("Конфигурация неверна:", file=sys.stderr)
            for err in exc.errors():
                where = ".".join(str(part) for part in err["loc"])
                print(f"  {where}: {err['msg']}", file=sys.stderr)
            return 1
        print("Конфигурация в порядке")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

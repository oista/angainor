# 01. Структура репозитория

Где что лежит, чтобы человек и агент находили нужное без поиска.

**Опора:** [src-раскладка Python-пакетов](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) (PyPA); [12-factor, I. Codebase](https://12factor.net/codebase) — одна кодовая база в одном репозитории; воспроизводимая установка зависимостей по lock-файлу.

## Правила

**LAY-1.** В корне репозитория лежат только: `README.md`, `AGENTS.md`, `pyproject.toml`, `uv.lock`, `.env.example`, `.gitignore`, `.gitattributes`, файлы Docker и точка запуска проверок (`scripts/check_all.py`, при желании `Makefile`). Временные и отладочные файлы (`cookies*.txt`, `*.html`, отчёты, выгрузки) в корне не хранятся. *(частично)*

↳ Шаблон: [`README.md`](../../templates/README.md), [`.gitignore`](../../templates/.gitignore)

**LAY-2.** Код живёт только в пакетах с src-раскладкой. Если проект поставляется одним приложением — `src/<пакет>/`. Если частей несколько — `apps/<приложение>/` для точек входа (CLI, API, веб) и `packages/<библиотека>/` для библиотек; у каждой части свой `pyproject.toml` и свои тесты. *(частично)*

↳ Шаблон: [`pyproject.toml`](../../templates/pyproject.toml), [`src/__pkg__/__init__.py`](../../templates/src/__pkg__/__init__.py)

**LAY-3.** Тесты лежат в `tests/` и разложены по видам: `unit/`, `integration/`, `architecture/`; общие тестовые данные — в `tests/fixtures/`. *(частично)*

↳ Шаблон: [`tests/unit/test_example.py`](../../templates/tests/unit/test_example.py), [`tests/integration/test_example_integration.py`](../../templates/tests/integration/test_example_integration.py), [`tests/architecture/test_no_print.py`](../../templates/tests/architecture/test_no_print.py)

**LAY-4.** В `scripts/` лежат проверки (`check_*.py`) и служебные операции. Одна проверка — один файл, имя говорит, что проверяется. Логика проверок пишется на Python, чтобы один и тот же файл работал на Windows и в CI на Linux; `.ps1` — только тонкие обёртки. *(есть)*

↳ Шаблон: [`scripts/check_all.py`](../../templates/scripts/check_all.py)

**LAY-5.** Настройки поведения, которые версионируются вместе с кодом (реестры модулей, профили, справочники), лежат в `config/` в формате TOML или YAML. Секретов и адресов окружения там нет — они задаются по правилам [02-config](02-config.md). *(частично)*

**LAY-6.** Сгенерированные файлы лежат в отдельных папках (`generated/`, `projections/`, `static/dist/`) и руками не правятся. Рядом или в README указана команда, которой они пересобираются. *(частично)*

**LAY-7.** Файлы развёртывания — в `deploy/` и `docker/`, документация — в `docs/` (см. [07-docs-adr](07-docs-adr.md)).

**LAY-8.** Зависимости управляются через uv: `pyproject.toml` и `uv.lock` хранятся в git, в CI зависимости ставятся только из lock-файла (`uv sync --frozen`). *(частично)*

↳ Шаблон: [`pyproject.toml`](../../templates/pyproject.toml)

## Зачем

Одинаковая раскладка убирает вопрос «где это лежит» при переходе между проектами и сокращает объём, который агенту нужно прочитать, чтобы сориентироваться. src-раскладка не даёт тестам случайно взять код из рабочей папки вместо установленного пакета. Lock-файл гарантирует, что CI, локальная машина и закрытый контур ставят одни и те же версии.

## Как сейчас

| Проект | Раскладка |
| --- | --- |
| PRODATA | одно приложение, 9 пакетов в `src/`, реестры модулей в `src/platform_web/config/*.toml`, тесты `tests/unit`, `tests/integration`, `tests/fixtures`, uv + lock |
| moex-data-model | `apps/` (api, cli, web, viewer, drawdb) и `packages/` (13 библиотек), у каждой свой `pyproject.toml` и `tests/`; общие `tests/architecture`; `generated/` |
| Clavis | пакет `ontology_core/` в корне и `src/clavis_*`; тесты плоским списком в `tests/`; `projections/` — производные файлы |
| Norma | `packages/norma-*`, у каждого свой `pyproject.toml` |

Расхождения: в Clavis пакет `ontology_core` лежит в корне, а не в `src/`. PRODATA держит реестры модулей внутри пакета (`src/platform_web/config/`), а файлы настроек — в корневом `config/`. В рабочих папках PRODATA (`cookies.txt`, `login_out.html`, `eval_live_*`) и moex-data-model (`tmp/`) в корне копятся временные файлы; git их игнорирует, но они мешают ориентироваться.

## Как проверяется

- `scripts/check_repo_hygiene.py` (PRODATA) — нет мусора в корне.
- `scripts/check_architecture_sync.py` (PRODATA) — пакеты в `src/` совпадают с `pyproject.toml`, README и `architecture.md`.
- `uv lock --check` в CI (PRODATA) — lock-файл соответствует `pyproject.toml`.

## Открытые вопросы

- Сделать `scripts/check_all.py` обязательной точкой запуска всех проверок во всех проектах (см. CI-1).
- Переносить ли `ontology_core` в Clavis в `src/` или оставить как исключение по ADR.

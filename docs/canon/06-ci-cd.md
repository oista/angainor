# 06. CI/CD, версии и выпуск

Как изменение проходит путь от коммита до работающей системы.

**Опора:** [Continuous Delivery](https://continuousdelivery.com/) (J. Humble, D. Farley) — конвейер развёртывания, «собрать один раз — развернуть много раз»; [Semantic Versioning](https://semver.org/lang/ru/); [Keep a Changelog](https://keepachangelog.com/ru/); [Conventional Commits](https://www.conventionalcommits.org/ru/); защита основной ветки.

## Правила

**CI-1.** Одна команда запускает все проверки локально — ровно те же, что и CI: `python scripts/check_all.py`. В CI нет логики, которой нет в этой команде; workflow только вызывает её по шагам. *(частично)*

↳ Шаблон: [`scripts/check_all.py`](../../templates/scripts/check_all.py)

**CI-2.** Стадии идут от быстрых к медленным: проверки архитектуры и документации → линтер и unit-тесты → интеграционные тесты с настоящей базой → сборка фронтенда и образов. Падение любой стадии блокирует слияние. *(частично)*

↳ Шаблон: [`.github/workflows/quality.yml`](../../templates/.github/workflows/quality.yml)

**CI-3.** Зависимости в CI ставятся только из lock-файла: `uv lock --check`, затем `uv sync --frozen`. *(частично)*

↳ Шаблон: [`.github/workflows/quality.yml`](../../templates/.github/workflows/quality.yml)

**CI-4.** Сканер секретов (gitleaks) — обязательная стадия. *(частично)*

↳ Шаблон: [`.github/workflows/quality.yml`](../../templates/.github/workflows/quality.yml)

**CI-5.** В `main` попадают только PR с зелёным CI (защита ветки). PR маленькие и про одно; изменение схемы данных и миграция самих данных идут разными PR. *(частично)*

**CI-6.** Развёртывание — отдельный workflow от `main`: одновременно идёт только одно развёртывание, каждый запуск оставляет журнал. Образ собирается один раз и переносится в закрытый контур без пересборки (air-gap-пакет образов). *(частично)*

**CI-7.** Версия хранится в одном месте — в `pyproject.toml`, остальной код читает её оттуда. Формат SemVer: MAJOR — несовместимые изменения, MINOR — новые возможности, PATCH — исправления. Выпуск — это git-тег `vX.Y.Z` и запись в `docs/changelog/CHANGELOG.md`. *(частично)*

↳ Шаблон: [`pyproject.toml`](../../templates/pyproject.toml), [`docs/changelog/CHANGELOG.md`](../../templates/docs/changelog/CHANGELOG.md)

**CI-8.** Сообщения коммитов пишутся по Conventional Commits: `feat(web): …`, `fix(api): …`, `docs(adr): …`, `chore: …`. *(частично)*

**CI-9.** Результаты CI (отчёты, базы вердиктов проверок) выгружаются как артефакты запуска и в репозиторий не коммитятся. *(частично)*

↳ Шаблон: [`.github/workflows/quality.yml`](../../templates/.github/workflows/quality.yml), [`.gitignore`](../../templates/.gitignore)

## Зачем

Если локальные проверки и CI различаются, разработчик и агент узнают о проблеме только после push. Порядок «от быстрого к медленному» даёт ответ за минуты. Lock-файл и однократная сборка образа гарантируют, что в закрытом контуре работает ровно то, что прошло проверки. Единая версия и теги нужны, чтобы проекты могли зависеть друг от друга по точной версии.

## Как сейчас

| Проект | Как сделано |
| --- | --- |
| PRODATA | `quality.yml` из 4 джобов (около 25 архитектурных проверок, unit, фронтенд, integration с Postgres 16); `deploy.yml` на собственном Windows-раннере; gitleaks; шаблон PR |
| moex-data-model | `check.yml` + `scripts/check_all.py` (15 шагов, повторяет цели Makefile); Conventional Commits; тег `v1.0.0`; PR сериями |
| Clavis | `ci.yml`: проверки онтологии, SHACL, ruff, mypy |
| Norma | `norma.yml` сохранён в UTF-16 — вероятно, не запускается |

Расхождения: в PRODATA версия хранится в двух местах (`pyproject.toml` — 2.3.2, `version.py` — 2.3.0); тегов нет в PRODATA, Clavis и Norma, хотя README Norma предлагает ставить пакеты по тегу `v0.1.0`; в PRODATA в git лежит `.archpolicy/ci-verdicts.sqlite`; сообщения коммитов в PRODATA и Clavis — свободной формы.

## Как проверяется

- CI сам по себе — стадии и защита ветки.
- `uv lock --check` (PRODATA).
- Формат сообщений коммитов (CI-8): [`scripts/check_commit_msg.py`](../../scripts/check_commit_msg.py) — хук `commit-msg` и проверка диапазона коммитов PR в CI; подключение проверок к git и CI описано в ADR-0005 (поле `enforce` правила реестра).
- Совпадение версии в одном месте пока не проверяется.

## Открытые вопросы

- Обёртка для GitLab CI в корпоративном контуре должна вызывать ту же команду CI-1.
- Добавить проверку «версия только в `pyproject.toml`».
- Добавить нормы работы с git: имена веток, размер PR, CODEOWNERS, шаблон PR; сверку настроек платформы (защита `main`) — см. ADR-0005, п. 6.

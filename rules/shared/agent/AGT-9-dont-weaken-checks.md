---
id: AGT-9
title: Не ослабляй проверки ради зелёного статуса
status: Accepted
scope: shared
activation: globs
globs:
- .github/workflows/**
- .pre-commit-config.yaml
- .githooks/**
- pyproject.toml
- tests/**
- '**/conftest.py'
- ruff.toml
- mypy.ini
- .coveragerc
- pytest.ini
- setup.cfg
- sonar-project.properties
norm:
- QLT-6
- TST-2
check: angainor:tools/check_change_guard.py
enforce:
- event: ci
  stage: guard
  when: pull_request
  tool: tools/check_change_guard.py
  args: [--range, '{pr_range}']
since: 0.1.0
---

# AGT-9: Не ослабляй проверки ради зелёного статуса

## Для агента

Ты меняешь файл, от которого зависят проверки. Не делай проверки мягче, чтобы получить зелёный статус: не удаляй и не пропускай тесты (`skip`, `xfail`), не добавляй `noqa`, `type: ignore`, `pragma: no cover`, `nosec`, `continue-on-error`, `|| true`, не снижай пороги покрытия и не расширяй исключения. Чини причину.
Если проверку действительно нужно изменить, скажи об этом пользователю прямо и добавь в коммит строку `Checks-Change: <причина>`. Без неё CI отклонит PR, а причина попадёт в сводку, которую читает человек.

## Зачем

Код пишут агенты, человек смотрит тесты и результат. Если агент может ослабить проверку, зелёный CI перестаёт что-либо значить. Правило делает такое изменение видимым и требует причины.

## Как проверяется

`tools/check_change_guard.py --range origin/main..HEAD` в CI (стадия `guard`, ADR-0005): смотрит diff PR, ищет правки конфигов проверок, добавленные маркеры обхода, удалённые тесты и ослабленные пороги. Находки блокируют PR, пока в одном из коммитов нет `Checks-Change:`.

## Исключения и особенности проектов

Агент сам может написать `Checks-Change:`; это не защита от злого умысла, а способ сделать изменение видимым. Настоящий барьер — CODEOWNERS и обязательное одобрение человеком для защищённых путей в настройках платформы (ADR-0005, п. 6).

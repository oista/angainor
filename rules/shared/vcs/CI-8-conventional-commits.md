---
id: CI-8
title: Сообщения коммитов — Conventional Commits
status: Accepted
scope: shared
activation: always
norm:
- CI-8
check: angainor:scripts/check_commit_msg.py
since: 0.1.0
---

# CI-8: Сообщения коммитов — Conventional Commits

## Для агента

Сообщения коммитов пиши по Conventional Commits: `тип(область): описание`, например `feat(web): добавить экран метрик`, `fix(api): …`, `docs(adr): …`, `chore: …`.
Типы: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. Несовместимое изменение — `!` после типа или `BREAKING CHANGE:` в теле.
Первая строка до 100 символов. Один коммит — одна тема; схема и миграция данных — разными коммитами.

## Зачем

Из шести проектов формат соблюдает только moex-data-model; в остальных коммиты свободным текстом, и тип изменения не читается.

## Как проверяется

`python scripts/check_commit_msg.py <файл>` (хук `commit-msg`) и `--range origin/main..HEAD` (CI).

## Исключения и особенности проектов

Слияния (`Merge …`), `Revert "…"` и `fixup!`/`squash!` не проверяются.

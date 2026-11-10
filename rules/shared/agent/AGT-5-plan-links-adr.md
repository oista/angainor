---
id: AGT-5
title: План ссылается на ADR
status: Accepted
scope: shared
activation: globs
globs:
- .cursor/plans/*.plan.md
norm:
- DOC-8
check: null
since: 0.1.0
---

# AGT-5: План ссылается на ADR

## Для агента

В YAML-шапке плана укажи `adr: ADR-NNNN`.
Новая фича начинается с ADR со статусом Proposed и рассмотренными вариантами, затем план со ссылкой `adr:`.
Модуль включают, только когда его ADR принят.

## Зачем

Связывает решение, план и код; без ссылки решение не прослеживается.

## Как проверяется

`scripts/check_adr_integrity.py` в PRODATA и Clavis (включённые модули ссылаются на Accepted ADR).

## Исключения и особенности проектов

В PRODATA у прежнего правила был пустой `globs`, поэтому оно не срабатывало; здесь исправлено.

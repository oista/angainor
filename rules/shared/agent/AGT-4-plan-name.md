---
id: AGT-4
title: 'Имя плана — «Проект: тема»'
status: Accepted
scope: shared
activation: globs
globs:
- .cursor/plans/*.plan.md
norm: []
check: null
params:
  project_name: последний сегмент пути корня рабочей области
since: 0.1.0
---

# AGT-4: Имя плана — «Проект: тема»

## Для агента

Перед созданием плана задай `name: {Project}: короткая тема`, где Project — {{project_name}}.
Верно: `Isthmus: Control Hub hardening`. Неверно: `Control Hub hardening`.
Имя файла плана начинается с того же префикса в нижнем регистре; если в проекте нет хука, который это нормализует, следи за этим сам.

## Зачем

Планы из разных проектов лежат в общей папке `~/.cursor/plans`; префикс показывает, чьи они.

## Как проверяется

Хук `normalize-plan-name` (сейчас `.ps1`) есть в ENTAN, Clavis и Isthmus; заменяется на `tools/plan_name_hook.py`.

## Исключения и особенности проектов

Параметр `project_name`: по умолчанию последний сегмент пути корня рабочей области; в Clavis — `clavis`.

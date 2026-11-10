---
id: AGT-4
title: 'Имя плана — «Проект: тема»'
status: Accepted
scope: shared
activation: globs
globs:
- .cursor/plans/*.plan.md
norm: []
check: angainor:tools/plan_name_hook.py
enforce:
- event: afterFileEdit
  tool: tools/plan_name_hook.py
  args: [--project, '{plan_prefix}']
- event: postToolUse
  matcher: Write|EditNotebook
  tool: tools/plan_name_hook.py
  args: [--project, '{plan_prefix}']
params:
  project_name: последний сегмент пути корня рабочей области
since: 0.1.0
---

# AGT-4: Имя плана — «Проект: тема»

## Для агента

Перед созданием плана задай `name: {Project}: короткая тема`, где Project — {{project_name}}.
Верно: `Isthmus: Control Hub hardening`. Неверно: `Control Hub hardening`.
Имя файла плана начинается с того же префикса в нижнем регистре. Хук Angainor исправляет имя после сохранения, но задавай его верно сразу.

## Зачем

Планы из разных проектов лежат в общей папке `~/.cursor/plans`; префикс показывает, чьи они.

## Как проверяется

Хук `tools/plan_name_hook.py` (ADR-0004) приводит имя и файл плана к виду «Проект: тема» после сохранения. Он заменяет `normalize-plan-name.ps1` в ENTAN, Clavis и Isthmus.

## Исключения и особенности проектов

Параметр `project_name`: по умолчанию последний сегмент пути корня рабочей области; в Clavis — `clavis`.

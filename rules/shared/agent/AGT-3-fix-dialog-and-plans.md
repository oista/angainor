---
id: AGT-3
title: Фиксация диалога и планов
status: Accepted
scope: shared
activation: on_request
triggers:
- зафиксируй
- зафиксируй диалог
- зафиксируй планы
- wrap
- export dialog
- сохрани диалог
norm: []
check: null
params:
  export_command: .\scripts\export-cursor-dialog.ps1
since: 0.1.0
---

# AGT-3: Фиксация диалога и планов

## Для агента

По фразам «зафиксируй», «зафиксируй диалог», «зафиксируй планы», «wrap», «export dialog», «сохрани диалог»:
1. Не пересказывай и не переписывай диалог, не создавай markdown-заметку.
2. Если открытые планы лежат только в `~/.cursor/plans`, напомни: в редакторе плана «Save to Workspace» → `.cursor/plans/` репозитория.
3. Запусти из корня репозитория `{{export_command}}`: диалоги → `docs/dialogs/raw/`, планы из `.cursor/plans/` → `docs/plans/`.
4. Ответь только путями созданных файлов.
Если скрипта нет — скажи об этом и остановись.

## Зачем

Объединяет `dialog-fixation`, `plan-fixation`, `session-notes` (PRODATA и Clavis) и раздел о фиксации в `workflows.md`.

## Как проверяется

Пожелание: агент должен запустить скрипт, а не писать пересказ. Скрипт переедет в `tools/export_dialog.py`.

## Исключения и особенности проектов

Параметр `export_command` — пока `.ps1` проекта. Сырые диалоги попадают в git: проверьте `.gitignore` и сканер секретов.

---
id: DOC-7
title: Принятый ADR не правят по месту
status: Accepted
scope: shared
activation: always
norm:
- DOC-7
check: null
since: 0.1.0
---

# DOC-7: Принятый ADR не правят по месту

## Для агента

Не переписывай и не правь Accepted ADR по месту. Решение меняется новым ADR со статусом, который заменяет прежний (`supersedes`, ссылка на старый).
Возврат к ранее отклонённому варианту — тоже только новым ADR.

## Зачем

Правило повторялось в трёх `workflows.md`, в Norma `docs-conventions` и в CONTRIBUTING moex-data-model.

## Как проверяется

`scripts/check_adr_integrity.py` в проектах проверяет номера и индекс; запрет правки принятого ADR проверяется только на ревью.

## Исключения и особенности проектов

Нет.

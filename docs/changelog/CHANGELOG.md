<!-- canon: CI-7 -->
# История изменений

Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), версии — [SemVer](https://semver.org/lang/ru/). Каждому выпуску соответствует git-тег `vX.Y.Z`.

## [Unreleased]

## [0.1.0] — 2026-11-10

Первый выпуск реестра правил для агентов.

### Добавлено

- Реестр правил `rules/` (ADR-0003): схемы `rule.schema.json` и `project-profile.schema.json`, профили проектов, генерируемые страницы `RULE-INDEX.md`, `RULE-MATRIX.md`, `projects/<проект>/RULES.md`.
- 14 общих правил: AGT-1…8, DOC-4/5/7/11, LAY-1, CI-8.
- `scripts/check_rules.py` и `scripts/build_rules.py`: проверка реестра и проекции в `.cursor/rules/*.mdc`, `AGENTS.md`.
- Хуки Cursor через поле `enforce` (ADR-0004): `tools/plan_name_hook.py`, генерация `.cursor/hooks.json`.
- Проверки git и CI через `enforce` (ADR-0005): `.githooks` или блок в `.pre-commit-config.yaml`, workflow `angainor-<stage>.yml`, `tools/check_commit_msg.py` (CI-8).
- Карантин старых правил проекта (`.cursor/_quarantine/<дата>/` с `MANIFEST.md`) и его проверка.
- Профили Clavis и Isthmus.

### Изменено

### Исправлено

### Удалено

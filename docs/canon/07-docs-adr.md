# 07. Документация и архитектурные решения (ADR)

Где описано, как устроена система и почему она устроена именно так.

**Опора:** docs-as-code — документация живёт в git рядом с кодом и проходит ревью; [arc42](https://arc42.org/overview) — структура описания архитектуры; ADR в формате [M. Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) и [MADR](https://adr.github.io/madr/); единый словарь терминов (ubiquitous language из DDD); [Keep a Changelog](https://keepachangelog.com/ru/).

## Правила

**DOC-1.** Вся документация — Markdown в `docs/` того же репозитория, она меняется в том же PR, что и код. Word и PDF — только производные копии, не источник. *(частично)*

**DOC-2.** Обязательный набор в каждом проекте:
- `README.md` в корне — что это, как запустить, как проверить;
- `AGENTS.md` в корне — что агенту читать первым и какой источник прав при расхождении;
- `docs/README.md` — карта документации;
- `docs/architecture.md` — описание архитектуры по разделам arc42; неприменимый раздел остаётся с пометкой «не применимо»;
- `docs/configuration.md`, `docs/glossary.md`, `docs/changelog/CHANGELOG.md`, `docs/adr/`.

*(частично)*

↳ Шаблон: [`AGENTS.md`](../../templates/AGENTS.md), [`README.md`](../../templates/README.md), [`docs/README.md`](../../templates/docs/README.md), [`docs/architecture.md`](../../templates/docs/architecture.md), [`docs/configuration.md`](../../templates/docs/configuration.md)

**DOC-3.** При расхождении текстов прав, по порядку: Accepted ADR → нормативные документы архитектуры и схемы → код. Черновики, планы и записи диалогов не описывают текущее состояние. *(частично)*

↳ Шаблон: [`AGENTS.md`](../../templates/AGENTS.md)

**DOC-4.** Термин предметной области — это определение элемента модели данных (DM-4), глоссарий собирается из модели (DM-5). Технический термин, которого нет в модели, описывается в `docs/glossary.md` в том же изменении, где он появился. *(частично)*

↳ Шаблон: [`docs/glossary.md`](../../templates/docs/glossary.md)

**DOC-5.** В папке с серией однотипных документов (ADR, design notes) обязательны `template.md` и индекс (`ADR-INDEX.md`). Новую серию без шаблона и индекса не заводят. *(есть)*

↳ Шаблон: [`docs/adr/ADR-INDEX.md`](../../templates/docs/adr/ADR-INDEX.md)

**DOC-6.** ADR пишется для каждого решения, которое дорого отменить: выбор технологии, граница модуля, формат данных, отказ от варианта. Обязательные разделы: Контекст, Решение, Последствия (плюсы и минусы), Рассмотренные варианты с причиной отказа — не меньше двух, на одном уровне абстракции с выбранным. *(есть)*

↳ Шаблон: [`docs/adr/template.md`](../../templates/docs/adr/template.md), [`docs/adr/ADR-0001-project-charter.md`](../../templates/docs/adr/ADR-0001-project-charter.md) · Схема: [`adr-frontmatter.schema.json`](../../schemas/adr-frontmatter.schema.json)

**DOC-7.** Номер ADR не используется повторно. Статусы: Proposed, Accepted, Deprecated, Superseded. Accepted ADR не переписывают: решение меняется новым ADR, который заменяет старый. Возврат к отклонённому варианту — тоже только новым ADR. *(есть)*

↳ Шаблон: [`docs/adr/template.md`](../../templates/docs/adr/template.md) · Схема: [`adr-frontmatter.schema.json`](../../schemas/adr-frontmatter.schema.json)

**DOC-8.** Решение связано с кодом. План работы ссылается на ADR (`adr: ADR-NNNN` в шапке плана); модуль включается, только когда его ADR принят; автоматическая проверка ссылается на ADR, из которого выросла. *(частично)*

↳ Шаблон: [`docs/plans/template.md`](../../templates/docs/plans/template.md)

**DOC-9.** Документ, собранный из реестра или схемы, помечен «не редактировать вручную» и содержит команду пересборки. *(частично)*

**DOC-10.** Диаграммы пишутся как код (Mermaid, PlantUML, Structurizr DSL) и лежат рядом с документом; картинки — только производные. *(частично)*

## Зачем

Документ вне репозитория отстаёт от кода с первого дня. ADR хранит не только решение, но и отвергнутые варианты, поэтому через полгода не приходится заново обсуждать уже закрытый вопрос, и агент не «изобретает» отклонённое решение повторно. Порядок правоты источников нужен агенту, чтобы при противоречии он не выбирал случайно. Связь ADR с планом и кодом делает решение проверяемым, а не декларацией.

## Как сейчас

| Проект | Как сделано |
| --- | --- |
| PRODATA | 47 ADR, номер из 4 цифр, метаданные в тексте; `_docs.meta.yaml` в каждой папке `docs/`; планы `.cursor/plans` со ссылкой `adr:`; модуль включается только при Accepted ADR |
| moex-data-model | 59 ADR, номер из 3 цифр, YAML-шапка со статусом и связями; `AGENTS.md` с порядком правоты источников; пользовательская документация проверяется автоматически |
| Clavis | 20 ADR в формате PRODATA; концепт, архитектура, глоссарий |
| Norma | 2 ADR; `docs-conventions.md` — общие правила документации |
| angainor | концепция в `.docx` — нарушает DOC-1 |

Расхождения: два формата ADR (метаданные в тексте с 4-значным номером и YAML-шапка с 3-значным). `AGENTS.md` есть только в moex-data-model.

## Как проверяется

- `scripts/check_adr_integrity.py` (PRODATA, Clavis, Norma — три разные копии) — уникальность номеров, соответствие индексу, включённые модули ссылаются на Accepted ADR.
- `tests/architecture/test_adr_numbers_unique.py`, `test_adr_readme_matches_frontmatter.py` (moex-data-model).
- `scripts/check_docs_config.py`, `check_architecture_sync.py` (PRODATA); проверка пользовательской документации (moex-data-model).

## Открытые вопросы

- Единый формат ADR. Предложение: YAML-шапка (status, date, supersedes, rules) и 4-значный номер; проверка на переходный период читает оба формата. Решение — meta-ADR.
- Одна общая реализация проверки ADR вместо трёх копий.

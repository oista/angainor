# 08. Архитектурные приёмы

Приёмы, которые повторяются в нескольких проектах и доказали пользу. Применяются в новом проекте по умолчанию.

**Опора:** [фитнес-функции эволюционной архитектуры](https://www.oreilly.com/library/view/building-evolutionary-architectures/9781492097532/) (N. Ford, R. Parsons, P. Kua) — архитектурные свойства проверяются автоматически; [гексагональная архитектура](https://alistair.cockburn.us/hexagonal-architecture/) (A. Cockburn) и правило зависимостей Clean Architecture; модульный монолит; объекты передачи данных (DTO, M. Fowler, «Patterns of Enterprise Application Architecture»); [«Parse, don't validate»](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/); единый источник правды (single source of truth); контракт у производителя (published language из DDD); [OWASP Fail securely](https://owasp.org/www-community/Fail_securely).

## Правила

**ARC-1. Решение → правило → проверка.** Архитектурное решение без автоматической проверки — пожелание. Каждый инвариант из ADR получает исполняемую проверку с проходящим и падающим примером (TST-3) и ссылкой на ADR. Проверки быстрые, работают без сети и без LLM; оценка с помощью LLM допустима только как совет и никогда не блокирует слияние. *(частично)*

↳ Шаблон: [`docs/architecture/invariants.yaml`](../../templates/docs/architecture/invariants.yaml) · Схема: [`invariant.schema.json`](../../schemas/invariant.schema.json)

**ARC-2. Зависимости направлены внутрь.** Ядро (предметная логика, общие библиотеки) ничего не знает о продуктах, интерфейсах и внешних системах. Внешние системы подключаются через порты и адаптеры. Внутри пакета: `domain` ← `application` ← `infrastructure`, `interfaces`; стрелки только к ядру. Направления закреплены import-linter или архитектурными тестами (QLT-3). *(частично)*

↳ Шаблон: [`.importlinter`](../../templates/.importlinter)

**ARC-3. Модульный монолит по умолчанию.** Один развёртываемый контур, жёсткие границы между пакетами. Отдельный сервис выделяется только через ADR и только когда у модуля другой ритм выпуска или другая нагрузка. *(есть)*

**ARC-4. Один источник правды — много производных.** У каждого вида знания есть один канонический файл: онтология в TTL, модель в LinkML, переменные в `config-schema.yaml`, инварианты в YAML-матрице. Всё остальное (таблицы, `.env.example`, YAML-проекции, контракты) генерируется, помечено как производное и проверяется на устаревание. *(частично)*

**ARC-5. Типизированные границы доверия.** Данные снаружи (HTTP, инструменты MCP, файлы, ответы LLM) сразу превращаются в типизированную модель (Pydantic) и дальше живут только в ней. `dict[str, Any]` на границе запрещён. Чем описывать модели внутри и снаружи — см. ARC-9. *(частично)*

**ARC-6. Закрыто по умолчанию.** Каждый вход требует авторизации, если он не внесён в явный список исключений со ссылкой на ADR. Если ключа или настройки нет, сервис отказывает, а не открывается. У паролей нет значений по умолчанию. *(частично)*

**ARC-7. Явные швы между проектами.** Любая зависимость между репозиториями (пакет, файл, API) записывается в реестр швов: кто производит, кто потребляет, где лежит контракт (у производителя), как версионируется, чем проверяется. Продукты зависят от общего слоя, общий слой не знает о продуктах. Продукты общаются только через HTTP-контракт, без импорта кода друг друга. *(частично)*

**ARC-8. Модуль объявляет себя сам.** У модуля есть паспорт (`module.toml` или запись в `module_registry.toml`): идентификатор, версия, что производит и потребляет, каким ADR разрешён. Модуль включается только при Accepted ADR. *(частично)*

↳ Шаблон: [`module.toml`](../../templates/module.toml) · Схема: [`module-passport.schema.json`](../../schemas/module-passport.schema.json)

**ARC-9. Система типов.** Данные на границах и в интеграциях — запросы и ответы API, аргументы и результаты MCP-инструментов, конверты, контракты между модулями и проектами, настройки — описываются моделями Pydantic. Внутренние значения предметной логики — неизменяемые dataclass (`frozen=True`). Порты (интерфейсы к внешним системам) — `typing.Protocol`, адаптеры их реализуют. `dict[str, Any]` и «сырые» словари между модулями не передаются. Pydantic проверяет форму данных, но не заменяет предметные правила: они живут отдельным слоем проверок. Общие библиотеки Norma от Pydantic не зависят. *(частично)*

↳ Шаблон: [`src/__pkg__/settings.py`](../../templates/src/__pkg__/settings.py), [`src/__pkg__/errors.py`](../../templates/src/__pkg__/errors.py)

## Зачем

ИИ-агент пишет код быстро и уверенно нарушает договорённости, которые записаны только словами: обратная связь от CI приходит постфактум, а текст ADR в момент генерации он не помнит. Исполняемые проверки и направленные зависимости удерживают архитектуру, даже когда код пишет не человек. Единый источник правды убирает целый класс ошибок «поправили в одном месте, забыли в другом». Явные швы позволяют менять один проект, не ломая три других.

## Как сейчас

| Приём | Где уже работает |
| --- | --- |
| ARC-1 | PRODATA — archpolicy-engine (ADR-0043), 18 скриптов `check_*.py`; moex-data-model — матрица из 67 инвариантов (ADR-045) |
| ARC-2 | PRODATA — `gitlab_lineage` (domain / application / infrastructure / interfaces), 7 контрактов import-linter; Norma — `check_norma_purity.py`; moex-data-model — порты в `modeling-kernel`, `test_import_boundaries.py` |
| ARC-3 | moex-data-model — ADR-004; PRODATA — одно приложение из 9 пакетов |
| ARC-4 | Clavis — TTL-канон и производные проекции с проверкой устаревания (ADR-0002); moex-data-model — `generated/**` только через перегенерацию; PRODATA — `config-schema.yaml` |
| ARC-5 | PRODATA — ADR-0041, правило R-001 строго на 10 файлах |
| ARC-6 | PRODATA — ADR-0010 и тест списка открытых маршрутов, lineage-api отказывает без `ADMIN_API_KEY`; Clavis — пароль Fuseki без значения по умолчанию |
| ARC-7 | Norma — ADR-0001 и `seam-registry.md`; PRODATA — `docs/architecture/boundary-contract.md` |
| ARC-8 | PRODATA — ADR-0013, `src/platform_web/config/module_registry.toml`; Clavis — `module.toml` |
| ARC-9 | Pydantic на границах: PRODATA (31 файл, ADR-0041), `modeling-kernel` moex-data-model (11 файлов, frozen-конверты), `ontology_core` Clavis; frozen dataclass внутри: PRODATA (65 файлов с `frozen=True`), Norma canalis; `Protocol` для портов: Norma canalis (`Connector`, `RowSource`, `SecretResolver`), `modeling-kernel`, PRODATA (17 файлов); Pydantic не единственный проверяющий — ADR-007 moex-data-model |

Расхождения: ARC-1 реализован дважды и независимо — archpolicy в PRODATA и матрица инвариантов в moex-data-model, с пересекающимися идентификаторами (`INV-001` в обоих проектах с разным смыслом).

## Как проверяется

- ARC-1: `python -m platform_archpolicy --mode ci_gate` (PRODATA), `check_constraint_matrix.py --gate-strict` (moex-data-model).
- ARC-2: import-linter (PRODATA), `check_norma_purity.py` (Norma), `test_import_boundaries.py` (moex-data-model).
- ARC-4: `check_projection_staleness.py` (Clavis), `validate_config --check-env-example` (PRODATA).
- ARC-5: правило R-001 (PRODATA).
- ARC-6: `test_route_auth_allowlist.py`, `test_lineage_api_auth.py` (PRODATA).
- ARC-7: `check_seam_registry.py` (Norma).
- ARC-8: `check_adr_integrity.py`, `check_ontology_bindings.py` (PRODATA).
- ARC-9: правило R-001 (PRODATA) — только для `dict[str, Any]` на границах доверия; выбор между Pydantic, dataclass и `Protocol` внутри кода не проверяется.

## Открытые вопросы

- Объединить две реализации ARC-1 в ядро Angainor; идентификаторы правил — с префиксом проекта (`prodata.INV-001`, `dams.INV-001`).
- Расширять R-001 (ARC-5) на новые файлы по принципу храповика.
- ARC-9: проверка «модели в контрактах между модулями — Pydantic, а не dict» и проверка, что Norma не импортирует `pydantic`.

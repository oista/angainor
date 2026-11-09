# 09.002 Логическая модель решения

Как конкретное приложение видит данные: сущности, атрибуты и связи в его контексте, без привязки к способу хранения.

**Правила:** [DM-1](../09-data-model.md), [DM-2](../09-data-model.md), [DM-3](../09-data-model.md), [DM-4](../09-data-model.md), [DM-7](../09-data-model.md), [DM-8](../09-data-model.md)  
**Опора:** логическая модель данных (DAMA-DMBOK); ограниченный контекст (bounded context, DDD); ADR-021, ADR-022, ADR-029, ADR-034–ADR-037, ADR-047 moex-data-model.

## Назначение

Логическая модель — главная часть пакета решения. Она фиксирует, какие данные приложение производит и потребляет, как они идентифицируются и какие понятия общего слоя реализуют. Код приложения строится по ней: таблицы, контракты API и сообщения ссылаются на её сущности и атрибуты.

## Состав

| Элемент DAMS | Что это | Главные поля |
| --- | --- | --- |
| `ModelPackage` (solution) | пакет модели решения | `solution_ref`, `conceptual_implementation_ref`, `domain_refs`, `imports_refs`, `model_version` |
| `DomainContext` | ограниченный контекст со своей терминологией | `domain_ref`, `solution_ref`, `namespace` |
| `LogicalEntity` | сущность решения | `context_ref`, `conceptual_entity_refs`, `solution_data_role` (`producer` / `consumer` / `intermediary`), `key_attribute_refs`, `identity_rule`, `conceptual_alignment_status` (`aligned` / `pending` / `local-only` / `not-applicable`), `isolation_rationale` |
| `LogicalAttribute` | атрибут сущности | `owner_entity_ref`, `data_type_ref` или `value_domain_ref`, `required`, `multivalued`, кардинальности, `concept_ref` (на значимое свойство), `critical_data_element`, `derived_expression` |
| `Relationship` | связь сущностей | роли, кардинальности, `identifying`, `relation_term_ref` |
| `ValueDomain` | допустимые значения атрибута | `value_domain_kind`, `data_type_ref`, `permissible_values`, `format_pattern` |
| `DataType` | тип данных — только из корпоративного реестра типов | `type_family`, `precision`, `scale`, `max_length` |
| `RealizesMapping` | сущность реализует понятие | источник — логическая сущность, цель — понятие |

## Связи

- **Вверх:** каждая сущность реализует одно или несколько понятий общего слоя ([001](001-conceptual-model.md)). Сущность без понятия допустима только со статусом `local-only` и обоснованием `isolation_rationale`.
- **Вниз:** сущность связана с носителем данных, атрибут — с полем структуры ([003](003-physical-model.md)).
- **В код:** классы приложения помечены `element_id` элементов логической модели (DM-7).

## Как оформлять

1. **Где лежит.** В репозитории моделей: `model-assets/implementations/solutions/<app>/`: конверт `implementation.yaml`, тело `<app>-solution-model.yaml`, публикация `publish.yaml`. В описи `manifest.yaml` — запись с `owner` и `depends_on` на концептуальные пакеты.
2. **В приложении** — только фиксация в YAML-файле `docs/architecture/data-model.yaml`: репозиторий моделей, версия спецификации и пакеты (решение и концептуальные пакеты) с версией и ревизией, с которыми совместим код. Шаблон — [`templates/docs/architecture/data-model.yaml`](../../../templates/docs/architecture/data-model.yaml), схема — [`schemas/data-model-pin.schema.json`](../../../schemas/data-model-pin.schema.json).
3. **Идентификаторы:** `dams:context/<app>`, `dams:logical/<app>/<ENTITY>`, `dams:logical/<app>/<ENTITY>/<ATTRIBUTE>`.
4. **Сущность реализует понятие.** Одна сущность может реализовать несколько понятий, зерно может отличаться: клиент решения ≠ юрлицо ≠ участник торгов (ADR-029). Взаимоисключающие роли («клиент — физлицо или юрлицо») — необязательные связи основной сущности, а не обязательные зависимости.
5. **Типы** — ссылки на корпоративные `DataType` или на `ValueDomain`; своих типов решение не заводит.
6. **Определения** — у каждой сущности и атрибута, по [004-glossary-terms](004-glossary-terms.md). Если смысл в контексте решения уже общего, используйте `scoped_definitions`, а не новое понятие.
7. **Импорт из xlsx** (`moex-model import-solution`, ADR-022) даёт только черновик. После импорта определения переписываются, ссылки на понятия проставляются.

Пример — сущность из пакета MDM. Определение переписано по DM-4 как учебный вариант, не утверждённый текст:

```yaml
- element_id: dams:logical/mdm/ENTERPRISE
  name: ENTERPRISE
  title: Юридические лица (ЮЛ)
  # было: description: Юридические лица (ЮЛ)  — повтор названия
  description: >
    Золотая запись юридического лица в MDM: сведения об организации,
    собранные из систем-источников и сведённые к одной записи на одно ЮЛ.
  context_ref: dams:context/mdm
  conceptual_entity_refs: [dams:concept/LegalEntity]
  solution_data_role: producer
```

## Как проверяется

- `moex-model validate`, `moex-model lint`, `moex-model check-manifest`, `moex-model lock verify`.
- Требования каталога DAMS к ИТ-решениям: 17 требований (`LDM-01`…`LDM-13`, `LDM-101`, `REF-002`, `PDM-01`, `PDM-02`), обязательные и рекомендуемые.
- LDM-008 — полнота реализации зависимых понятий (пока предупреждение).
- Пока не проверяется: определение не повторяет название; метки `element_id` в коде приложения существуют в модели.

## Как сейчас

- Четыре пакета решений: crm, esed, mdm, ucd — 26 логических сущностей, 208 атрибутов, 31 связь, 16 связей «реализует».
- У 10 из 26 сущностей нет ссылки на понятие.
- У 232 из 234 сущностей и атрибутов определение совпадает с названием.
- Пакетов для PRODATA, ENTAN и Clavis нет.

## Открытые вопросы

- Проверка, что файл фиксации соответствует описи репозитория моделей (пакеты и ревизии существуют).
- Порядок создания пакетов PRODATA, ENTAN, Clavis: какой первым и из чего (DDL, Pydantic-модели, ER-набросок).

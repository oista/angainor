# 09.003 Физическая модель решения

Где и в каком виде данные реально лежат и передаются: базы, таблицы, файлы, топики, API, сообщения.

**Правила:** [DM-3](../09-data-model.md), [DM-6](../09-data-model.md)  
**Опора:** физическая модель данных (DAMA-DMBOK); описание структур по образцу ODCS и JSON Schema; ADR-031–ADR-033, ADR-038–ADR-041, ADR-046, ADR-055 moex-data-model.

## Назначение

Физическая модель связывает логическую модель с тем, что видно в системах. По ней строится линия происхождения данных, сверяются миграции и контракты, и по ней понятно, какое поле какой таблицы хранит какой атрибут.

## Состав

| Элемент DAMS | Что это | Главные поля |
| --- | --- | --- |
| `TechnicalAsset` (абстрактный) | «квант данных» — адресуемый технический объект | `asset_namespace` + `qualified_name` (идентичность), `system_ref`, `technology`, `asset_kind`, `lineage_role` (`source` / `sink` / `intermediate` / `none`), `parent_ref` |
| `DataContainer` | контейнер, данных не несёт | `asset_kind`: `database`, `schema`, `bucket`, `broker`, `directory`, `cluster` |
| `DataCarrier` | носитель данных | `asset_kind`: `relational_table`, `relational_view`, `file`, `dataset`, `stream_topic`, `stream_queue`, `in_memory`, `api_resource`, `other`; ссылка на структуру |
| `AccessPoint` | точка доступа: интерфейс, операция, канал | `serves_refs`, `operation_name`, `http_method`, `path_template`, `message_refs` |
| `ExecutionAsset` | исполняемый актив: конвейер или задание | `produces_refs`, `consumes_refs` |
| `DataStructure` | версия структуры данных — дерево узлов | `schema_format`, `schema_dialect` (семейство JSON Schema), `structure_version`, `root_local_key`, `nodes`, `content_digest` |
| `SchemaNode` | узел структуры: колонка, поле, элемент | `local_key`, `node_kind`, `data_type_ref`, `native_type`, `nullable`, `is_primary_key`, `foreign_key_target`, `realizes_attribute_ref` |
| `Message` | сообщение интеграции | `payload_structure_ref`, `headers_structure_ref`, `content_type` |
| `EntityPhysicalMapping` | носитель ↔ логическая сущность, строго один к одному | — |
| `FieldMapping` | атрибут → узел структуры (`structure_id#local_key`) | — |

## Связи

- **Вверх:** носитель связан с логической сущностью (`EntityPhysicalMapping`), поле — с атрибутом (`FieldMapping`). Поле без атрибута помечается `mapping_coverage_status` (`technical-only`, `planned`, `not-applicable` …) с обоснованием.
- **Топология** — системы, решения, интерфейсы, каналы — принадлежит каталогу Clinkr / EAM (ADR-055). Физическая модель ссылается на неё (`system_ref`, `integration_ref`), но не описывает заново.
- **В код:** миграции базы и схемы сообщений приложения соответствуют физической модели (DM-6).

## Как оформлять

1. Поле или колонка — не квант: адресуется как узел структуры своего носителя, а не отдельным активом (ADR-033).
2. Идентичность актива — пара `asset_namespace` + `qualified_name` (ADR-032).
3. У каждого носителя с данными модели — `EntityPhysicalMapping`; у каждого поля — `FieldMapping` или статус покрытия с причиной.
4. Структуры описываются плоским списком узлов; рёбра `children` и `item_node` — по `local_key` (ADR-038, ADR-039).
5. DBML и ER-диаграммы — производные публикации (`publications/physical.dbml`, `physical.erd.svg`); руками не правятся.
6. Миграции пишутся как обычно (Alembic). Проверка в CI применяет миграции к чистой базе и сверяет получившиеся таблицы и колонки — имена, типы, обязательность, первичные и внешние ключи — с носителями и узлами физической модели из зафиксированной версии. Таблица без носителя в модели или колонка без узла — ошибка. Генерация миграций из модели не используется.

## Как проверяется

- `moex-model validate` и `moex-model lint`; требования `PDM-01`, `PDM-02`.
- Матрица инвариантов: правила для структур, узлов, носителей и точек доступа (например, узел-массив имеет `item_node` и не имеет `children`; поля сообщений только у операций и каналов).
- Пока не проверяется: соответствие миграций и контрактов приложения физической модели.

## Как сейчас

- В четырёх пакетах решений: 26 носителей, 26 структур, 26 связей «носитель ↔ сущность», 208 связей «атрибут ↔ поле»; публикации DBML и ER есть.
- В PRODATA схема базы задаётся миграциями Alembic и в модели не описана.

## Открытые вопросы

- Кто описывает физику PRODATA, ENTAN и Clavis первым и из какого источника: снимок схемы базы, модели Pydantic.

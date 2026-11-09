<!-- canon: DOC-2, CFG-3 -->
# Конфигурация <project>

Общие правила имён — [config-contract Norma](https://github.com/oista/norma/blob/main/docs/config-contract.md). Здесь — только особенности проекта.

Источник правды — [architecture/config-schema.yaml](architecture/config-schema.yaml). `.env.example` и класс `Settings` сверяются с ним командой:

```bash
python -m <pkg>.settings --check-env-example
```

Проверка конфигурации текущего окружения:

```bash
python -m <pkg>.settings --check
```

## Особенности проекта

<Переменные, требующие пояснений: несовместимые сочетания, порядок настройки, примеры для закрытого контура.>

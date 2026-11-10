# Angainor: контуры, поставка, развитие canon и контроль декомпозиции

Исследовательский срез: 9 ноября 2026 года. Документ объединяет проверенные материалы репозиториев, сведения из прежних диалогов и предложения по развитию Angainor; предложения не являются принятыми ADR или уже реализованными проверками.

## Главный вывод

Angainor целесообразно развивать не в сторону ещё одной платформы, а как компактное локальное ядро проверок и версионируемый канон для существующих проектов. Именно такую границу задаёт текущая концепция: сервер и интерфейс относятся к PRODATA, онтология к Clavis, метамодель данных к moex-data-model, runtime-контроль продуктовых агентов к ENTAN. ([Текущая концепция Angainor](https://github.com/oista/angainor/blob/main/docs/concept.md))

Самый полезный следующий шаг: замкнуть цепочку «норма → применимость → исполняемая проверка → обязательный шлюз → свидетельство исполнения». Сейчас в Angainor уже есть содержательный канон, но его парсер не распознаёт табличные ENV-правила, а в PRODATA quality и deploy запускаются независимо; это воспроизведённые пробелы контроля, а не предположение о плохом качестве всей системы. ([Проверка связей Angainor](https://github.com/oista/angainor/blob/main/scripts/check_canon_links.py), [workflow deploy](https://github.com/oista/prodata-platform/blob/main/.github/workflows/deploy.yml), [workflow quality](https://github.com/oista/prodata-platform/blob/main/.github/workflows/quality.yml))

Для борьбы со сложностью недостаточно лимита строк. Нужны одновременно граф разрешённых зависимостей, публичные интерфейсы модулей, локальные метрики функций, контроль роста существующего долга и проверка того, насколько типичное изменение локализовано в одном модуле.

## Основания и границы исследования

### Проверенные срезы

| Репозиторий | Исследованная ревизия | Роль в исследовании |
|---|---|---|
| Angainor | `72b7e9a310bf6718bc79b65dfacc4edead4a6bc1` | Концепция, весь canon 01–10, схемы, шаблоны, ADR, проверка связей. ([Репозиторий](https://github.com/oista/angainor)) |
| moex-data-model | `241662891cd9e307a82e8788bfaa26c048143fae` | CI, архитектурные тесты, поставка, GitLab моделей, размеры функций. ([Репозиторий](https://github.com/oista/moex-data-model)) |
| PRODATA | `a83702d9918cc70ef3aa75ee51c5b57ad311a4a9` | CI/CD, archpolicy, типизированные границы, контуры, размеры функций. ([Репозиторий с авторизованным доступом](https://github.com/oista/prodata-platform)) |
| Isthmus | `bdf58b2b777697bb3d60a6cb9b7717dddca9793a` | Дополнительная проверка инфраструктурных сведений, на которые ссылается PRODATA. ([Описание Pharos](https://github.com/oista/isthmus/blob/main/pharos-vps/README.md), [сетевая политика](https://github.com/oista/isthmus/blob/main/docs/adr/0021-network-physical-layer-and-transport-policy.md)) |
| infra | `8986e07a278641758c1cbde70672d1ac1d4b3384` | Дополнительный просмотр стека мониторинга; не источник назначения кодов контуров. ([Репозиторий с авторизованным доступом](https://github.com/oista/infra)) |

Приватные репозитории читались через авторизованные `gh` и `git`; публичный веб-загрузчик их не открывает. Ссылки на них в документе предназначены владельцу доступа, а не означают публичную доступность.

Дополнительно прочитаны приложенный `10-contours.md`, вики проекта и исходные диалоги: об Angainor от 11 сентября, об archpolicy от 29 августа, о реестре архитектурных правил от 14 октября и о домашнем `app-srv` от 23–24 октября 2026 года. Сведения из диалогов ниже явно отделены от текущего состояния репозиториев; предложения ассистента в старых диалогах не считаются решениями пользователя.

### Что действительно проверялось

- **Структура и содержание:** файлы canon, схемы, workflow, скрипты поставки, архитектурные тесты и реализация archpolicy.
- **Исполнение:** `check_canon_links.py`; валидация реестра контуров через JSON Schema Draft 2020-12; отдельная проверка поведения при отсутствии скрипта правила.
- **Метрики:** AST-разбор Python-кода и cyclomatic complexity выбранных функций через Radon 6.0.1.
- **Настройки GitHub:** API-проверка `main`, rulesets и последних Actions runs на момент исследования.
- **Не проверялось:** доступность серверов по сети, фактический SSH-вход, текущая RAM и ОС живых машин, настройки локального GitLab через его API, восстановление из бэкапа и полный прогон продуктовых тестовых наборов.

Ни успешный CI, ни актуальная документация сами по себе не доказывают состояние работающего сервера. В инвентаре используются статусы «по текущему документу», «исторически подтверждено», «противоречие» и «не установлено».

## Контуры: что удалось восстановить

### Инвентарь

| Контур | Адреса и доступ | ОС и ресурсы | Особенности и уверенность |
|---|---|---|---|
| `cnt`, Centurion | WireGuard `10.20.20.4`; актуальная LAN-резервация `192.168.10.64`; профиль туннеля `wireg-homepc`. ([Заметки PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/dev/wangate-infra.md), [cutover Isthmus](https://github.com/oista/isthmus/blob/main/wangate/host/choke-point-cutover.md)) | Windows подтверждается Windows-раннером и эксплуатационными инструкциями; редакция, версия ОС, CPU и RAM не установлены. ([Workflow deploy](https://github.com/oista/prodata-platform/blob/main/.github/workflows/deploy.yml), [заметки PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/dev/wangate-infra.md)) | Основная разработка и существующий Windows-путь деплоя PRODATA; это не доказательство назначения только стадии `dev`. ([Workflow deploy](https://github.com/oista/prodata-platform/blob/main/.github/workflows/deploy.yml), [реестр Angainor](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contours.yaml)) |
| `lgn`, Legioner | WireGuard `10.20.20.3`; профиль `wireg`, только на ноутбуке; при фильтрации сети путь через Nekoray/Throne и wstunnel к Pharos. ([Заметки PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/dev/wangate-infra.md)) | Windows следует из инструкций helper для ноутбука; точная версия, CPU и RAM не установлены. ([Заметки PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/dev/wangate-infra.md)) | Helper `:9099` не следует считать SSH-доступом; одинаковый WG-адрес нельзя одновременно активировать на ноутбуке и Centurion. ([Заметки PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/dev/wangate-infra.md)) |
| `wgn`, Wangate | LAN `192.168.10.1`; WireGuard `10.20.20.2`; документирован SSH как `oista`, ключевая аутентификация. Старый LAN `192.168.1.203` исторический. ([Cutover](https://github.com/oista/isthmus/blob/main/wangate/host/choke-point-cutover.md), [SSH и overlay](https://github.com/oista/prodata-platform/blob/main/docs/dev/wangate-infra.md)) | Debian 13 указан как проверенный вариант; CPU и RAM в просмотренных эксплуатационных материалах не установлены. ([Сетевая инструкция Isthmus](https://github.com/oista/isthmus/blob/main/wangate/docs/network-and-vps-setup.md)) | Шлюз домашней сети, маршрутизация, DNS и TLS edge; изменение сети способно одновременно нарушить доступ к прикладным сервисам. ([Сетевая политика Isthmus](https://github.com/oista/isthmus/blob/main/docs/adr/0021-network-physical-layer-and-transport-policy.md)) |
| `prs`, Pharos | Публичный IP `45.134.218.129`; overlay `10.20.20.1`; SSH `vpsops`, ключ `~/.ssh/vps/vps_eu`. ([Реестр Angainor](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contours.yaml), [доступ к Pharos](https://github.com/oista/isthmus/blob/main/pharos-vps/README.md)) | В записи о создании VPS от 05.07.2026: Ubuntu 26.04, 1 vCPU, 2 GB RAM, диск 40 GB; текущая конфигурация живого VPS не проверялась. ([Исходная карточка VPS, приватная](https://github.com/oista/isthmus/blob/main/pharos-vps/vps_init.md)) | Публичный transport hub, wstunnel/WG и overlay DNS; административные Portainer/Kuma должны быть доступны по WG, не WAN. ([Описание Pharos](https://github.com/oista/isthmus/blob/main/pharos-vps/README.md), [сетевая инструкция](https://github.com/oista/isthmus/blob/main/wangate/docs/network-and-vps-setup.md)) |
| `cst`, Castrum, код и имя предложены | В черновике Angainor `192.168.10.140`; это нужно привязать к конкретному узлу, а не автоматически к физическому серверу. ([Реестр Angainor](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contours.yaml)) | По исходному домашнему диалогу `app-srv` является Debian VM на Proxmox; пользовательский вывод подтверждает диски 150G и 300G. RAM не подтверждена; ранее предложенные 8 vCPU и примерно 16 GB нельзя выдавать за измеренный факт. | На том же адресе документация moex-data-model описывает GitLab `:8929`, проект `root/moex-models`, runner и `MOEX_AUTH_MODE=dev`; это документированная установка, не выполненная в этом исследовании runtime-проверка. ([Инструкция GitLab](https://github.com/oista/moex-data-model/blob/main/docs/user/30-howto/gitlab-models.md)) |
| `mxl`, Moexlab, код предложен | Адрес, SSH-пользователь и топология не установлены; доставка образов по почте указана в черновике. ([Реестр Angainor](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contours.yaml)) | ОС, CPU, RAM и диски не установлены. Не следует приписывать этому контуру Debian домашнего `app-srv` или РЕД ОС из troubleshooting другого документа. | Рабочий изолированный контур; в черновике запрещены инструменты агентов и указан ручной перенос человеком. Это проект политики, а не доказанная техническая блокировка. ([Реестр Angainor](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contours.yaml)) |

Из домашнего диалога также восстановлен отдельный физический узел Proxmox: Ryzen 9 5950X, ASRock Rack B550D4U-2T и отдельные VM для Home Assistant OS и приложений. Эти сведения полезны как историческая карточка хоста; автоматически отождествлять физический Proxmox, VM `app-srv` и имя Castrum нельзя.

### Подключение: что можно перенести в runbook

Для Wangate и Pharos в существующих инструкциях указаны следующие способы SSH-подключения; наличие ключей и доступность портов здесь не проверялись. Для Centurion, Legioner и Moexlab единого подтверждённого SSH-runbook не найдено. ([Инструкции доступа PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/dev/wangate-infra.md), [доступ Pharos](https://github.com/oista/isthmus/blob/main/pharos-vps/README.md))

```powershell
# Wangate через overlay. Выполнять на своей машине с соответствующим ключом.
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" -o IdentitiesOnly=yes oista@10.20.20.2

# Pharos. Не отключать проверку ключа сервера.
ssh -i "$env:USERPROFILE\.ssh\vps\vps_eu" -o IdentitiesOnly=yes vpsops@45.134.218.129
```

Для `app-srv` в домашнем диалоге использовался `ssh oista@192.168.10.140`; вывод пользователя подтверждал слушающий SSH на порту 22. Это историческое свидетельство, не гарантия текущей сетевой доступности.

Предлагаю хранить в утверждённой карточке `ssh_alias`, `user`, `port`, `via/bastion`, ссылку на ключ и проверенный fingerprint сервера. Пароль, приватный ключ и токен не должны попадать ни в карточку, ни в bundle.

### Противоречия, которые нельзя замести под общий адрес

- **Домашний сервер и рабочий контур:** домашний диалог явно относится к `app-srv` дома, а некоторые страницы moex-data-model называют сервер на `192.168.10.140` «рабочим». IP сам по себе не позволяет назначить ему зону доверия работодателя. ([Инструкция GitLab с адресом](https://github.com/oista/moex-data-model/blob/main/docs/user/30-howto/gitlab-models.md))
- **Адрес `.30`:** README Wangate говорит, что app containers находятся на `192.168.10.30`; это не совпадает с `.140` в черновике Angainor. Нужно установить, другой ли это узел, старое имя или новая адресация, а не выбирать один адрес наугад. ([README Wangate](https://github.com/oista/isthmus/blob/main/wangate/README.md), [реестр Angainor](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contours.yaml))
- **Старая сеть:** PRODATA сохраняет `192.168.1.203` и `192.168.1.64`, тогда как cutover Isthmus от 02.11.2026 фиксирует новую домашнюю сеть и Centurion `.10.64`. Для инвентаря нужен timestamp и признак `current/historical`, а не просто строка `address`. ([Заметки PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/dev/wangate-infra.md), [cutover](https://github.com/oista/isthmus/blob/main/wangate/host/choke-point-cutover.md))
- **DNS:** в материалах встречаются рекомендации о приоритете Pharos и Wangate; устойчивое общее основание состоит в использовании обоих overlay DNS, а не публичного resolver для внутренних имён. Приоритет нужно фиксировать по профилю клиента и проверять отдельно. ([Сетевая инструкция Isthmus](https://github.com/oista/isthmus/blob/main/wangate/docs/network-and-vps-setup.md), [заметки PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/dev/wangate-infra.md))

Публичный IP не является паролем, а приватный IP не становится безопасным только из-за RFC1918. Предлагаю разделять публичный шаблон реестра и закрытый эксплуатационный inventory по классификации информации, а не просто исключать все публичные IP.

### Как улучшить модель contours

Предлагаемая модель: `contour → node → environment → workload`. Контур задаёт границу доверия и допустимость операций, узел описывает физическую/виртуальную машину, среда задаёт стадию и изоляцию, workload описывает конкретный продукт.

| Объект | Что хранить |
|---|---|
| Contour | Стабильный код, владелец, зона доверия, статус, политика данных и действий агентов |
| Node | Имя/идентификатор, `physical/vm/workstation`, `parent_node`, ОС, архитектура, vCPU, RAM, диски, адреса и сеть |
| Environment | `cnt.dev`, выбранные узлы, изоляция, хранилище секретов, цели выкладки, проверки и бэкап |
| Workload | Проект, сервис, image digest, config revision, model revision, порты, volumes, ресурсы |
| Evidence | `observed_at`, `source_ref`, `verified_by`, `verification_method`, статус достоверности |

Политики предлагаю вычислять пересечением ограничений контура, среды и workload, а не объединением разрешений. Например, разрешение на собственные данные в домашнем контуре не должно автоматически разрешать их в каждом публичном workload.

CPU, RAM и лимиты контейнеров следует разделить: `node.ram_total_mib` не равен `workload.memory_limit_mib`. Для ОС стоит хранить семейство, версию, архитектуру и дату наблюдения; для дисков отдельно назначение, ёмкость и место хранения данных.

В этом реестре `unknown` должен оставаться явно неизвестным значением с задачей на заполнение. Он не должен означать разрешение выкладки; production-pin обязан ссылаться на проверенную и полную карточку.

## CI/CD, Git и раскатка

### Текущее состояние

| Проект | Реализовано в исследованном срезе | Что не следует объявлять уже обеспеченным |
|---|---|---|
| Angainor | Проверка `python scripts/check_canon_links.py`; в корне нет собственного Actions workflow, хотя workflow есть в шаблоне. Последние Actions runs отсутствовали. ([Репозиторий](https://github.com/oista/angainor), [скрипт проверки](https://github.com/oista/angainor/blob/main/scripts/check_canon_links.py)) | Нельзя приравнивать наличие шаблона CI к CI самого Angainor. |
| PRODATA quality | Четыре jobs: fitness, unit, frontend, integration; `uv lock --check`, frozen sync, archpolicy, import-linter, Gitleaks, Postgres 16, Alembic. Mypy имеет `continue-on-error: true`. ([Workflow quality](https://github.com/oista/prodata-platform/blob/main/.github/workflows/quality.yml)) | Mypy не является блокирующим шлюзом; четыре jobs не выстроены в последовательную цепочку через `needs`. ([Workflow quality](https://github.com/oista/prodata-platform/blob/main/.github/workflows/quality.yml)) |
| PRODATA deploy | Отдельный workflow по push в `main` и вручную; self-hosted Windows X64; группа concurrency `deploy-prod`. Скрипт обновляет checkout через `fetch`, `checkout`, `pull --ff-only`, затем build/up и health checks. ([Workflow deploy](https://github.com/oista/prodata-platform/blob/main/.github/workflows/deploy.yml), [скрипт выкладки](https://github.com/oista/prodata-platform/blob/main/scripts/gha-deploy.ps1)) | Deploy не зависит от завершения quality и ориентируется на текущее состояние ветки; это не продвижение неизменяемого ранее проверенного образа. ([Workflow deploy](https://github.com/oista/prodata-platform/blob/main/.github/workflows/deploy.yml), [скрипт выкладки](https://github.com/oista/prodata-platform/blob/main/scripts/gha-deploy.ps1)) |
| moex-data-model GitHub | Три jobs: Stage 0 через `check_all.py`, viewer/packages, workbench; Ubuntu 24.04, отдельный frontend/e2e. ([Workflow check](https://github.com/oista/moex-data-model/blob/main/.github/workflows/check.yml)) | `check_all.py` соответствует Stage 0, а не всему workflow с viewer и workbench. ([Workflow check](https://github.com/oista/moex-data-model/blob/main/.github/workflows/check.yml)) |
| Локальный GitLab моделей | Есть opt-in шаблон `MOEX_MODELS_CI=1`, manifest/lock, validate с baseline, semantic diff и breaking gate, publications freshness, matrix-check. ([Шаблон GitLab CI](https://github.com/oista/moex-data-model/blob/main/deploy/models-repo/.gitlab-ci.yml)) | Gitleaks и fmt пока `allow_failure`; фактическое включение runner и защиты ветки описано документацией, но не проверено через GitLab API в этом исследовании. ([Шаблон CI](https://github.com/oista/moex-data-model/blob/main/deploy/models-repo/.gitlab-ci.yml), [эксплуатационная инструкция](https://github.com/oista/moex-data-model/blob/main/docs/user/30-howto/gitlab-models.md)) |

На одном и том же SHA `a83702d…` workflow PRODATA `deploy` и `quality` стартовали 09.11.2026 в 16:18:04 UTC; deploy был завершён к 16:20:07, quality к 16:21:34. Оба успешны, но последовательность наглядно подтверждает, что deploy не ждёт весь quality; это не пример доказанного деплоя неработающего кода. ([Запуск deploy](https://github.com/oista/prodata-platform/actions/runs/42653354922), [запуск quality](https://github.com/oista/prodata-platform/actions/runs/42653355023))

API GitHub на исследованном срезе вернул `protected:false` для `main` всех трёх основных репозиториев; списки rulesets Angainor и moex-data-model были пусты. Для приватного PRODATA запрос rulesets вернул 403 с ограничением тарифа, поэтому отсутствие rulesets там не установлено; делать репозиторий публичным ради этой функции не предлагается. ([Angainor](https://github.com/oista/angainor), [moex-data-model](https://github.com/oista/moex-data-model), [PRODATA](https://github.com/oista/prodata-platform))

### Что переносить из существующей практики

- **Малые тематические PR:** разделять изменение схемы и миграцию экземпляров; generated-файлы менять только перегенерацией. Это уже явный порядок moex-data-model и хорошая основа общего канона. ([CONTRIBUTING](https://github.com/oista/moex-data-model/blob/main/CONTRIBUTING.md))
- **Отдельный поток моделей:** приложения поставляются образами, модели обновляются через отдельный GitLab-репозиторий; приложение не должно везти случайный снимок моделей с build-машины. ([ADR-058](https://github.com/oista/moex-data-model/blob/main/docs/adr/ADR-058-airgap-image-deploy.md))
- **Full и Overlay:** поставка кода поверх последнего Full является полным снимком кода, а не цепочкой патчей; изменение зависимостей требует нового Full. ([ADR PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/adr/ADR-0044-airgap-image-deploy.md), [ADR-058](https://github.com/oista/moex-data-model/blob/main/docs/adr/ADR-058-airgap-image-deploy.md))
- **Один drop:** образы/overlay, checksum, manifest, compose/config bundle, инструкция и apply-скрипт доставляются согласованным комплектом, без секретов. ([ADR-058](https://github.com/oista/moex-data-model/blob/main/docs/adr/ADR-058-airgap-image-deploy.md))
- **Проверка границ владения:** GitLab владеет прикладными моделями, upstream владеет спецификациями и generated, spec-sync имеет явный allowlist путей. ([ADR-058, D7](https://github.com/oista/moex-data-model/blob/main/docs/adr/ADR-058-airgap-image-deploy.md))

### Предлагаемый обязательный путь изменения

```text
Чистая рабочая копия и зафиксированная база
  → тематическая ветка
  → точечные проверки во время работы
  → полная локальная команда выбранного CI-профиля
  → PR с ADR при изменении архитектурного решения
  → обязательные CI-checks для конкретного SHA
  → merge
  → сборка и тестирование release-кандидата с точным source SHA
  → manifest + immutable digest + evidence
  → разрешённый переход между средами
  → preflight → миграции → deploy → readiness → smoke
  → deploy receipt; при неудаче контролируемый rollback
```

Ветку нельзя считать релизным идентификатором. Выкладка должна принимать точный SHA и digest, а повторная сборка из плавающего `main` не должна называться продвижением того же артефакта.

Для Git предлагаю: Conventional Commits, без принудительного требования rebase/squash для каждого проекта; merge strategy фиксируется в проектном профиле. Автоматическому агенту запрещаются force-push основной ветки, обход required checks, несанкционированный `--no-verify` и незаметное изменение baseline; локальный hook сам по себе не является границей безопасности.

CI-1 стоит переформулировать как «единый каталог проверок и единая реализация каждой проверки», а не «любой локальный запуск обязан поднимать всё». Нужны профили `fast`, `full`, `integration`, `frontend`, `release`; workflow вызывает эти же профили и декларирует полный набор обязательных jobs.

Деплой лучше связать с quality через явный `needs` в одном workflow либо через защищённый release-процесс. Если использовать отдельный `workflow_run`, дополнительно проверять успешный результат, тип события, исходный репозиторий, ветку и точный `head_sha`; ручной запуск тоже не должен обходить проверку evidence.

GitHub environments и concurrency можно использовать для approvals, секретов и ограничения параллельных выкладок; наличие environment не включает concurrency автоматически. Доступность соответствующих protection rules зависит от конфигурации аккаунта, поэтому профиль обязан явно описывать технически доступный механизм, а не имитировать его чек-листом. ([GitHub: управление deployment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments))

### Как уточнить air-gap-поставку

В текущем CI-6 одновременно написаны «без пересборки» и перенос практики Overlay; в ADR-058 Overlay на закрытом сервере делает `docker build` поверх локального Full с `--network=none`. Эти режимы нужно назвать по-разному, иначе канон запрещает собственный прецедент. ([CI-6](https://github.com/oista/angainor/blob/main/docs/canon/06-ci-cd.md), [ADR-058](https://github.com/oista/moex-data-model/blob/main/docs/adr/ADR-058-airgap-image-deploy.md))

Предлагается два режима:

| Режим | Гарантия | Требование |
|---|---|---|
| `immutable-image` | На целевой среде запускается тот же image digest, который прошёл release-проверки | Только load/pull и запуск; сборка на целевой стороне запрещена |
| `offline-overlay` | На целевой стороне воспроизводится образ из проверенного снимка без скачивания зависимостей | Full parent по digest, проверенный deps fingerprint, сеть запрещена, результат идентифицирован новым digest и прошёл smoke |

Хеш рядом с архивом обнаруживает повреждение, но не подтверждает автора поставки, если злоумышленник может заменить и архив, и хеш. Для Moexlab предлагаю подпись manifest с заранее доверенным публичным ключом либо иной утверждённый независимый канал проверки подлинности.

В release manifest предлагаю фиксировать `release_id`, source SHA, версии инструментов, image digests, Full-parent digest, deps fingerprint, config schema revision, модели и их ревизии, поддерживаемую архитектуру, результаты проверок, подпись и минимальную совместимую версию схемы БД. На приёмке проверять manifest до распаковки и запуска, отсутствие путей за пределами каталога и отсутствие секретов.

Нынешний порядок contour-pack поднимает patch локально, а коммит версии делается после упаковки. Для однозначной provenance предлагаю сначала зафиксировать release-версию коммитом, затем собирать из чистого SHA; при сохранении старого механизма manifest обязан отдельно фиксировать реальный build-tree digest, а не представлять до-bump SHA как полное описание дерева. ([Порядок версии в ADR-058](https://github.com/oista/moex-data-model/blob/main/docs/adr/ADR-058-airgap-image-deploy.md), [порядок PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/adr/ADR-0044-airgap-image-deploy.md))

Откат образа не равен откату данных. Для каждой миграции нужно указывать совместимость предыдущей версии приложения, возможность повторного запуска и отдельный план восстановления; автоматический destructive downgrade БД по неудачному smoke запрещать.

## Пробелы самого Angainor, подтверждённые проверками

| Наблюдение | Как проверено | Предложение |
|---|---|---|
| Два текста `10-contours.md` расходятся: корневой ещё говорит о неизвестных трёх контурах, вложенный и приложенный файл описывают шесть | Сравнение файлов; канон ссылается на ещё другой целевой путь реестра. ([Корневой раздел](https://github.com/oista/angainor/blob/main/docs/canon/10-contours.md), [фактический YAML](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contours.yaml)) | Один краткий нормативный файл; подробности не дублируют нормы; один канонический путь registry |
| `ENV-1…12` не входят в результат `canon_rules()` | Прямой вызов парсера: 78 распознанных правил, 0 ENV; regex ожидает строку `**CODE-N.`. ([Реализация парсера](https://github.com/oista/angainor/blob/main/scripts/check_canon_links.py)) | Либо унифицировать формат правил, либо вынести реестр норм в структурированные данные; добавить negative fixture с ENV |
| `check_canon_links.py` падает в отдельном клоне | Ошибка ссылки `../../../norma/docs/config-contract.md`; успешный запуск зависит от наличия соседнего checkout. ([Парсер](https://github.com/oista/angainor/blob/main/scripts/check_canon_links.py), [CFG-2](https://github.com/oista/angainor/blob/main/docs/canon/02-config.md)) | Версионируемая ссылка/пакет контракта и явный cross-project reference вместо неявной зависимости от расположения папок |
| `contours.yaml` пока не проходит собственную JSON Schema | 17 диагностик Draft 2020-12, в основном ожидаемые для TODO в enum/boolean; это черновик, не 17 независимых архитектурных дефектов. ([YAML](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contours.yaml), [схема](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contour-registry.schema.json)) | Разделить draft-inventory и approved registry; production-pin не может ссылаться на draft |
| Ряд полей TODO проходит строковые `minLength:1`; production-условия не выражены | Схема допускает произвольные непустые `owner/access/store`; backup и post_deploy_check не являются безусловно обязательными для prod. ([Схема](https://github.com/oista/angainor/blob/main/docs/canon/10-contours/contour-registry.schema.json)) | Запрет sentinel-значений в approved-режиме, условные требования prod, проверка ссылок, исполняемые probes |
| Пока нет `check_contours.py`, лишь его проект | Просмотр `scripts/` и ссылок в разделе 10. ([Скрипт, реально имеющийся в репозитории](https://github.com/oista/angainor/blob/main/scripts/check_canon_links.py), [раздел 10](https://github.com/oista/angainor/blob/main/docs/canon/10-contours.md)) | Добавить проверку схемы, ссылок, unique codes, retired codes, pin и generated projections |
| Устав ADR-0001 имеет статус Proposed | Статус frontmatter и текста ADR. ([ADR-0001](https://github.com/oista/angainor/blob/main/docs/adr/ADR-0001-angainor-charter.md)) | Не называть его Accepted в производных текстах; оформить принятие отдельно после согласования |
| Один и тот же механизм может принять отсутствие скрипта за skip | В PRODATA `run_script()` на отсутствующем файле вернул `status=skip`; это воспроизведено отдельным вызовом, без утверждения, что так пропущена реальная текущая проверка. ([Адаптер скриптов](https://github.com/oista/prodata-platform/blob/main/src/platform_archpolicy/script_runner.py)) | Для обязательного применимого правила отсутствие checker или evidence является error и блокирует gate |

В черновом pin указан `registry_version: v0.1.0`, но на исследованном срезе Angainor тегов нет. Такой пример допустим как шаблон, но не как рабочая зафиксированная зависимость. ([Репозиторий Angainor](https://github.com/oista/angainor), [реестр и раздел контуров](https://github.com/oista/angainor/blob/main/docs/canon/10-contours.md))

## Что дополнить в каждом разделе canon

Все идентификаторы новых норм ниже являются предложениями. Их номера следует назначать после согласования, не создавая впечатления уже принятого стандарта.

| Раздел | Что оставить основой | Конкретные дополнения |
|---|---|---|
| `01-repo-layout` | Src-layout, отделение apps/packages и generated. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/01-repo-layout.md)) | Полный allowlist корня через профиль, включая README/AGENTS, конфиги инструментов, лицензии и lock-файлы; правила временных отчётов; язык-независимая структура; тесты пакетов не обязаны переезжать в один общий tests |
| `02-config` | Схема переменных, типизированный Settings, запрет secret defaults. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/02-config.md)) | Порядок наложения конфигурации; provenance эффективной настройки; допустимость dev auth только в dev; secret references; scope и ротация; compatibility aliases с датой удаления; разделение `<PROJECT>_ENV` и продуктового режима |
| `03-logging-errors` | Структурированные события, operation ID, каталог ошибок. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/03-logging-errors.md)) | Поля project/env/release/trace, redaction-тесты, cardinality budget, причинная цепочка ошибок; неизвестный внешний код сохранять во внутренних диагностических данных с origin, но пользователю выдавать безопасное сообщение |
| `04-testing` | Пирамида, regression-тесты, пары pass/fail для правил. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/04-testing.md)) | Контрактные тесты, CLI/subprocess и air-gap e2e, property-based tests для валидаторов, fixtures совместимости, TTL карантина; тест признаётся проверяющим также через `pytest.raises`, snapshot и ожидаемый exit code, не только буквальный `assert` |
| `05-linters-quality` | Ruff, типы, import-linter и храповик. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/05-linters-quality.md)) | CC и вложенность для изменённых функций, контроль размера, новые/устранённые нарушения по stable ID, запрет незаметного rebasing baseline, frontend-профиль, отчёт hotspots |
| `06-ci-cd` | PR, lock, артефакты, Full/Overlay. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/06-ci-cd.md)) | SHA-gated deploy, release provenance, явные профили checks, signed manifest, receipt, безопасные миграции и rollback, защита workflow/baseline; исправить противоречие «без пересборки» vs Overlay |
| `07-docs-adr` | Иерархия источников, ADR для дорогих решений, docs-as-code. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/07-docs-adr.md)) | Жизненный цикл правила отдельно от статуса ADR; owner и expiry исключений; разделение fact/proposal/target; применимость через профиль; короткий generated AGENTS-index с ссылками на explain |
| `08-architecture` | Модульный монолит, направленные зависимости, typed boundaries и швы. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/08-architecture.md)) | Политика зависимостей как DAG, public API модулей, владение данными, отсутствие скрытого I/O в domain, транзакционные границы, правила композиции и контроля декомпозиции |
| `09-data-model` | Pin модели, концептуальный/логический/физический уровни, сверка контрактов. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/09-data-model.md)) | Версии совместимости, семантический diff, authority per path, canonicalization/digests, explicit unknowns, динамические поля и расширения, staged migration; зависимость от корпоративной модели включать профилем, не делать универсальной |
| `10-contours` | Контур отдельно от стадии, explicit promotion, default deny. ([Текущий раздел](https://github.com/oista/angainor/blob/main/docs/canon/10-contours.md)) | Node inventory, trust boundary, политику на environment/workload, независимые build/deploy/runtime механизмы, executable health/backup/restore, evidence свежести, offline-доставку с подписью |

### Исправления формулировок, а не наращивание количества правил

- **LOG-9:** общий `platform.UNKNOWN` не должен уничтожать исходный внешний error code и его origin во внутренней диагностике. Иначе канон возвращает класс проблемы, ради которого PRODATA уже вводила типизированную границу и passthrough ошибки. ([LOG-9](https://github.com/oista/angainor/blob/main/docs/canon/03-logging-errors.md), [ADR archpolicy с отсылкой к инциденту](https://github.com/oista/prodata-platform/blob/main/docs/adr/ADR-0043-archpolicy-engine.md))
- **TST-1:** e2e не стоит ограничивать веб-интерфейсом. Сквозная проверка CLI, GitLab-публикации, pack/load и миграции не менее полезна, чем браузерный сценарий.
- **TST-8:** буквальный поиск `assert` даёт ложные нарушения для `pytest.raises` и других корректных oracle. Формулировать нужно наличие проверяемого результата.
- **ARC-2:** hexagonal-правило надо показать графом: application зависит от domain и портов; infrastructure реализует порты; composition root связывает реализации. Фраза о движении «только внутрь» не должна разрешать domain импортировать infrastructure через промежуточный application.
- **ARC-7:** HTTP не должен быть единственным разрешённым межпродуктовым транспортом. Допустимы событийный контракт и версионируемый файл/bundle с одним владельцем; импорт внутренних классов другого продукта остаётся запрещён.
- **ARC-9:** лучше требовать типизированный и валидируемый контракт, а выбор Pydantic закрепить Python-профилем. Библиотечный `Protocol` и внутренний dataclass не нужно заменять тяжёлой runtime-валидацией ради формального единообразия.
- **DM-1/DM-2:** MOEX DAMS и корпоративная концептуальная модель должны быть обязательны для соответствующего data-profile. Минимальная CLI-утилита не должна получать корпоративный модельный стек только из-за подключения Angainor.
- **ENV-4:** environment ID, release ID и image digest являются разными осями. Один digest должен продвигаться в несколько сред без переименования его идентичности.
- **ENV-8:** запрещать перенос секретов в Git и поставке, а не любое использование секрета между контурами. Общий внешний сервис может требовать отдельные ограниченные credentials в нескольких средах, выданные через управляемый процесс.
- **ENV-11:** `backup.required: true` не доказывает возможность восстановления. Нужны объект бэкапа, расписание, retention, RPO/RTO, дата последнего восстановления и проверяемый результат.

## Какие блоки отсутствуют в целом

Предлагаю сначала добавить несколько сквозных механизмов, а не немедленно заводить десятки новых каталогов. Часть требований логичнее расширяет существующие разделы 02/05/06/08/10.

| Блок | Минимальное содержимое | Когда нужен |
|---|---|---|
| Управление правилами и исключениями | Applicability, lifecycle, severity, gate mode, owner, waiver, expiry, baseline, evidence contract | Сразу, до выделения ядра archpolicy |
| Декомпозиция и модульные контракты | Dependency policy, public API, data owner, budget сложности, change-locality | Сразу для PRODATA и moex-data-model |
| Безопасность и supply chain | Threat boundary, secrets, auth modes, dependencies/SBOM, provenance, approvals, workflow permissions | Сразу для удалённой выкладки и air-gap |
| Надёжность и эксплуатационная готовность | Liveness/readiness, SLO, timeout/retry, backup/restore, migration/rollback, incident runbook | До признания среды production |
| Наблюдаемость и метрики качества | События приложения, результат правил, длительность checks, false-positive feedback, изменения baseline | После унификации минимального result schema |
| Версионирование и обновление самого Angainor | Pin checker/schema/template, changelog, migration guide, проверка совместимости consumers | До первого общего релиза |
| Работа dev-time агентов | Scope чтения/записи, разрешённые цели, подтверждения, план/дифф, лимиты действий, запрет обхода проверок | После минимального детерминированного gate |
| Контракты интеграций | Producer-owned schema, versioning, backward compatibility, idempotency и delivery semantics | Для границ, где это действительно используется |

Отдельный Hub, собственный graph database и LLM-судья не нужны для первого внедрения этих блоков. Такое ограничение соответствует текущей концепции Angainor и уже принятому направлению локального L1 в PRODATA. ([Концепция Angainor](https://github.com/oista/angainor/blob/main/docs/concept.md), [ADR-0043](https://github.com/oista/prodata-platform/blob/main/docs/adr/ADR-0043-archpolicy-engine.md))

### Отдельное замечание о секретах

В приватной исходной карточке Pharos обнаружены открытые значения учётных данных; значения намеренно не перенесены в этот документ. Нельзя установить, действуют ли они сейчас, поэтому их следует считать потенциально скомпрометированными до проверки и ротации владельцем. ([Приватная исходная карточка](https://github.com/oista/isthmus/blob/main/pharos-vps/vps_init.md))

Рекомендованный порядок: установить scope, отозвать/заменить потенциально действующие credentials, перенести инструкции на secret references, затем отдельно согласовать очистку истории и перевыпуск зависимых конфигураций. Удаление строки только из последнего коммита не заменяет ротацию; деструктивная перепись истории в этом исследовании не выполнялась.

## Как проверять декомпозицию

### Проблема измерима уже сейчас

Для оценки использованы AST-диапазоны `lineno…end_lineno`, включая комментарии, пустые строки и вложенные определения; это не SLOC. Cyclomatic complexity измерена отдельно через Radon 6.0.1 и не называется Cognitive Complexity. ([Определения метрик Radon](https://radon.readthedocs.io/en/latest/intro.html))

| Репозиторий и функция | Диапазон строк AST | Вложенных функций | Cyclomatic complexity | Интерпретация |
|---|---:|---:|---:|---|
| moex-data-model `apps/api/…/app.py::create_app` | 1572 | 43 | 3 | Большая фабрика-контейнер обработчиков: собственный control flow прост, но границы API и композиции сконцентрированы в одном месте. ([Код API](https://github.com/oista/moex-data-model/blob/main/apps/api/src/moex_model_api/app.py)) |
| moex-data-model `ingest/mapper.py::map_er_dictionary` | 625 | 0 | 118 | Сильный кандидат на декомпозицию преобразования по этапам и семантическим объектам. ([Код mapper](https://github.com/oista/moex-data-model/blob/main/packages/standard-linkml/src/moex_standard_linkml/ingest/mapper.py)) |
| moex-data-model `formal_checks.py::_run_conditional` | 452 | 0 | 82 | Кандидат на таблицу обработчиков видов ограничений и выделение чистых функций проверки; не основание удалять проверки. ([Код валидатора](https://github.com/oista/moex-data-model/blob/main/packages/specification-dams/src/moex_dams/rules/formal_checks.py)) |
| PRODATA `platform_web/main.py::create_app` | 553 | 23 | 2 | Аналогично: большая composition factory, не эквивалент функции с CC 80. ([Код фабрики](https://github.com/oista/prodata-platform/blob/main/src/platform_web/main.py)) |
| PRODATA `platform_metrics/ingest/eval.py::ingest_eval_scorecard_dict` | 363 | 1 | 83 | Приоритетный hotspot на границе ingest: стоит отделить parse/normalize, domain mapping, persistence и итоговый результат. ([Код ingest](https://github.com/oista/prodata-platform/blob/main/src/platform_metrics/ingest/eval.py)) |
| PRODATA `eval_sessions.py::run_eval_session` | 251 | 0 | 48 | Проверить раздельность планирования, исполнения, классификации исходов и фиксации результата. ([Код оркестратора](https://github.com/oista/prodata-platform/blob/main/src/platform_web/core/platform_ai/eval/eval_sessions.py)) |

В сканируемом Python-коде PRODATA найдено 542 файла и 3023 определения функций, у 78 диапазон больше 80 строк, у 16 больше 150; в moex-data-model соответственно 370, 1645, 104 и 33. ([Исходный код PRODATA](https://github.com/oista/prodata-platform), [исходный код moex-data-model](https://github.com/oista/moex-data-model)) Скан охватывал `src` PRODATA и `apps/packages/tools` moex-data-model, исключал пути `tests` и `generated`; это локальные вычисления по указанным срезам, не опубликованные показатели проектов.

Самое важное наблюдение: `create_app` на 1572 строки имеет CC 3, а mapper на 625 строк имеет CC 118. Поэтому правило «резать каждую функцию после 80 строк» не различает инфраструктурную сборку и сложную предметную логику; низкая CC фабрики также не доказывает хорошую модульность её 43 обработчиков. ([Код API](https://github.com/oista/moex-data-model/blob/main/apps/api/src/moex_model_api/app.py), [код mapper](https://github.com/oista/moex-data-model/blob/main/packages/standard-linkml/src/moex_standard_linkml/ingest/mapper.py))

### Пять уровней контроля

| Уровень | Вопрос | Проверка |
|---|---|---|
| Функция | Можно ли понять одну операцию без удержания десятков ветвей? | CC, когнитивная сложность при наличии согласованного анализатора, вложенность, число аргументов, объём собственной логики |
| Файл/модуль | Есть ли одна ответственность и понятный публичный вход? | Паспорт, exports, запрет private imports, размер, число независимых групп обработчиков |
| Подсистема | Есть ли архитектурная граница, а не просто папка? | Dependency DAG, отсутствие циклов, allowed edges, ownership таблиц, контрактные тесты |
| Изменение | Локализуется ли типичная доработка? | Количество затронутых модулей, co-change, fan-out диффа, отдельность schema/data migrations |
| Продукт | Выделение сервиса действительно необходимо? | ADR с нагрузкой, release cadence, данными, отказами и операционной стоимостью; не количество файлов |

Cyclomatic complexity показывает ветвление потока управления; Cognitive Complexity отдельно учитывает трудность понимания и вложенность. Их нельзя суммировать или подменять друг другом; предлагаемые ниже пороги являются настройкой пилота, а не универсальным отраслевым стандартом. ([Ruff C901](https://docs.astral.sh/ruff/rules/complex-structure/), [методика Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf))

### Предлагаемые проверяемые правила

Обозначения `DEC-*` ниже являются рабочими именами предложений. Детерминированные структурные нарушения можно блокировать сразу на новом коде; численные эвристики сначала следует включить в report-only.

| Код | Норма | Реализация проверки | Начальный режим |
|---|---|---|---|
| `DEC-1` | Межмодульный граф ацикличен | SCC-анализ импортов; новый SCC больше одного узла запрещён | Block новых циклов |
| `DEC-2` | Все межмодульные зависимости входят в allowlist | Реестр модулей и граф imports; новый модуль без классификации считается ошибкой | Block |
| `DEC-3` | Domain не импортирует framework, transport, ORM, filesystem/network adapters | Import contracts, включая косвенные пути и external packages | Block нового |
| `DEC-4` | Чужой модуль доступен только через объявленный public API | AST imports → public surface, исключения в manifest | Block нового |
| `DEC-5` | Модуль не пишет в таблицы другого владельца | Allowlist repository/SQL access, миграций; интеграционные permissions для сильной границы | Block очевидных нарушений; SQL-эвристики advisory |
| `DEC-6` | На trust boundary есть конкретная схема входа/выхода и runtime parsing | Реестр границ + AST + runtime negative tests | Block нового |
| `DEC-7` | В domain нет скрытого I/O и чтения env | AST/import checks, monkeypatch guards в тестах; allowlist composition/adapters | Block нового |
| `DEC-8` | Новая функция не получает чрезмерную CC | Ruff C901 либо единообразно выбранный Radon; предупреждение `>10`, кандидат в блокировку `>20` после пилота | Report → ratchet |
| `DEC-9` | Чрезмерная вложенность явно рассмотрена | AST nesting; предупреждение глубже 4, без учёта декларативных уровней class/function | Report |
| `DEC-10` | Большой размер функции/файла является сигналом ревью | Предупреждение функция `>80` строк собственной логики, файл `>500` SLOC; generated исключён | Report, не глобальный block |
| `DEC-11` | Крупный composition root не содержит доменных алгоритмов | Наличие nested handlers, calls к persistence и бизнес-ветвлению → отчёт; тонкие routers/services | Advisory + архитектурный review |
| `DEC-12` | У модуля есть владелец, назначение, public API и data ownership | Схема паспорта + сверка с фактическими модулями | Block отсутствующей карточки нового модуля |
| `DEC-13` | Рефакторинг не создаёт новый долг под видом переноса | Stable symbol mapping, baseline из base SHA, unmatched violations считаются новыми | Block роста после пилота |
| `DEC-14` | Правило имеет выполняемые pass/fail fixtures | Запуск обеих fixtures, проверка ожидаемого rule ID и результата | Block |
| `DEC-15` | Новый большой cross-module change объяснён | Дифф затрагивает более 3 бизнес-модулей → review notice; generated и formatting классифицируются отдельно | Report |
| `DEC-16` | Зависимость и публичный контракт имеют совместимость | Consumer/provider contract tests; schema diff для API/events/files | Block breaking без разрешённой миграции |
| `DEC-17` | Число аргументов не маскирует отсутствующую модель | Предупреждение `>6` бизнес-параметров; исключения DI/framework отдельно | Report |
| `DEC-18` | Дублируется не предметное решение, а максимум механика | Duplicate-code detector и сравнение co-change → список review; общий helper только после установления одинаковой семантики | Advisory |

Import-linter уже умеет forbidden, independence и layers contracts, в том числе косвенные зависимости; это позволяет не писать собственный общий анализатор импортов с нуля. При использовании проверки внешних пакетов нужно включить соответствующую опцию, а поддержка exhaustive-классификации имеет ограничения для layers/containers. ([Документация import-linter](https://import-linter.readthedocs.io/en/stable/contract_types.html))

Статический граф импортов не следует считать доказательством отсутствия любых runtime-зависимостей. Для проектов с dynamic imports, plugin discovery, raw SQL и рефлексией предлагаю отдельно декларировать динамические связи, проверять их контрактными тестами и явно показывать непокрытые механизмы в evidence проверки.

Пример предлагаемой декларации границы, а не существующий контракт репозитория:

```yaml
module: moex.ingest
responsibility: "Преобразование разобранного входного словаря в модель-кандидат"
public_api:
  - moex_standard_linkml.ingest.public
allowed_dependencies:
  - moex.contracts
  - moex.modeling
forbidden_dependencies:
  - moex_model_api
  - moex_publication_viewer
owns_data: []
quality:
  cyclomatic_warning: 10
  cyclomatic_candidate_limit: 20
  enforcement: report
```

### Правильный храповик

Не следует хранить только число нарушений. При таком подходе можно убрать одно простое нарушение и добавить одно опасное, сохранив тот же счётчик.

Предлагаемый baseline хранит `rule_id`, путь, символ/модуль, fingerprint диагностического места, значение метрики, основание, владельца и срок исключения. Сравнение идёт с base SHA PR; изменившийся в этом же PR baseline не может сам себе разрешить новые нарушения.

Уже сложная изменяемая функция не обязана немедленно достичь CC 10, но не должна ухудшаться; новый код не должен наследовать её численное исключение автоматически. Для сплита функции нужно сохранять traceability нарушений, а изменения `.importlinter`, policy, baseline и waiver проверять как отдельные изменения правил.

Исключение composition root допустимо только для метрики размера. Оно не должно отключать циклы, auth, secret scanning, бизнес-ветвление во вложенных handlers и проверки контрактов.

### Что конкретно декомпозировать первым

- **`map_er_dictionary`:** сначала regression/golden fixtures на текущий результат, затем выделение построения сущностей, атрибутов, связей и диагностик в чистые функции; orchestration оставляет порядок этапов. Цель не «625 строк превратить в 20 файлов», а получить отдельно тестируемые предметные операции.
- **`ingest_eval_scorecard_dict`:** typed raw input → нормализованный результат → domain mapping → одна контролируемая транзакция сохранения → ingest report. Нужны негативные кейсы неизвестных кодов, частичных результатов и повторного ingest.
- **`run_eval_session`:** отделить подготовку execution plan, запуск shard/job, классификацию outcome, сохранение scorecard и завершение session. Каждый переход состояния должен проверяться без реального LLM и subprocess.
- **Обе `create_app`:** вынести routers по capability, DI providers и lifecycle wiring, не создавать отдельный сервис на каждый router. Критерий завершения: handler тестируется без поднятия всего приложения, а factory не выполняет предметных преобразований.
- **`_run_conditional`:** рассмотреть dispatch по видам ограничений, единый typed context и небольшие валидаторы. Обязательны сохранение состава диагностик и pass/fail fixtures, иначе уменьшение CC может означать потерю проверок.

Это последовательность предложений, а не автоматический вердикт о дефектности перечисленных функций. До изменения нужны владельцы поведения, тесты и отдельное согласование каждого крупного шага.

### Проверка качества самого разбиения

После рефакторинга предлагаю проверять: прежние contract/golden tests проходят, новых SCC нет, публичная поверхность не расширилась без необходимости, данные имеют прежнего владельца, а новая функция не требует импорта всего приложения. Изменение одной типичной бизнес-возможности должно затрагивать меньше независимых модулей и допускать локальный тест.

Разбиение нельзя считать успешным, если ветвления просто перенесены в «универсальный» helper, увеличилось число взаимных вызовов или возникли proxy/facade без собственной ответственности. Строки и CC помогают отобрать кандидатов, но смысловую границу подтверждают сценарии изменений и review.

## Единое ядро правил: что извлечь из PRODATA и moex-data-model

В PRODATA уже есть разделение Invariant/Rule/Policy, локальное L1-ядро, режимы advisory/inline/ci_gate и принцип, что LLM Judge не блокирует merge. В moex-data-model уже работает подход с явной матрицей ограничений и обязательными положительными/отрицательными примерами; эти механизмы стоит унифицировать, не импортируя предметную DAMS-семантику в общее ядро. ([ADR-0043 PRODATA](https://github.com/oista/prodata-platform/blob/main/docs/adr/ADR-0043-archpolicy-engine.md), [канон архитектуры](https://github.com/oista/angainor/blob/main/docs/canon/08-architecture.md), [канон тестов](https://github.com/oista/angainor/blob/main/docs/canon/04-testing.md))

Предлагаемый минимальный набор сущностей:

| Сущность | Смысл |
|---|---|
| Norm | Утверждение канона с устойчивым кодом и основанием |
| Invariant | Проверяемое свойство архитектуры или данных |
| Rule | Конкретный алгоритм, его версия, scope и fixtures |
| Policy/Profile | Какие rules обязательны для данного проекта и почему |
| Waiver | Ограниченное отклонение: правило, scope, owner, основание, expiry |
| Evidence | Что проверяли: commit, files/model/environment, toolchain, inputs |
| Result | Pass/fail/error/skip, violations, время, coverage scope |
| Gate | Политика преобразования Result в block/warn, отдельно от алгоритма |

Ключевой контракт: `skip` допустим только при доказанной неприменимости, а не при отсутствии файла, анализатора или runtime-зависимости проверки. Для обязательного применимого правила `error`, неизвестный rule ID, пустой scope из-за поломки discovery и неполный evidence должны блокировать gate.

Минимальный результат предлагается сохранять в JSON с полями `rule_id`, `rule_version`, `policy_version`, `source_commit`, `scope`, `status`, `violations`, `evidence_refs`, `duration_ms`, `checker_exit_code`. JSON является первичным результатом, Markdown/CI annotations/SARIF или JUnit выступают проекциями по необходимости.

Общее ядро должно работать локально без сети, PRODATA, MCP и LLM. Адаптер MCP вызывает тот же Python API, UI PRODATA читает результаты, а специфические checks DAMS, PRODATA и Isthmus остаются в своих пакетах с namespaced identifiers.

## Что полезного переносится из других диалогов

| Обсуждение | Что действительно полезно | Что не переносить как принятое решение |
|---|---|---|
| Angainor, 11.09.2026 | Каркас документации, ADR, fitness checks, связь решений с метриками, разделение статических правил и runtime | Старую polyrepo-схему из восьми репозиториев, собственный сервер Angainor и ArchiMate/Linked.Archi как обязательный фундамент: текущая концепция уже иная |
| Archpolicy, 29.08.2026 | Лёгкие проверки до CI, `validate_plan/lint_diff/explain`, компактный контекст агента, метрики качества правил | Утверждение, что prompt или hook невозможно обойти; «точные токены соблюдения» без полного наблюдаемого trace |
| Реестр правил, 14.10.2026 | Правило становится обязательным через конкретную норму/профиль; применимость и отклонения отделены от каталога | Автоматическое превращение всех описанных правил в обязательные для каждого проекта; корпоративный шестимесячный срок не нужно без решения переносить в личные проекты |
| HomeLab, 23–24.10.2026 | Фактические Debian VM, адрес `.140`, SSH, раздельные диски и мониторинг | Изначальные рекомендации 8 GB или 8 vCPU/16 GB как якобы измеренную конфигурацию |

Из августовского обсуждения особенно полезна идея измерять качество самих правил: долю срабатываний, подтверждённые false positives, время проверки, частоту waiver, escape rate после merge и затраты на исправление. При этом «mute rate» не равен false-positive rate, а размер MCP-ответа не равен полной стоимости рассуждений и повторных действий агента.

План и подсказка агента не являются enforcement. Границу создаёт неизбежная для выпуска проверка с независимыми правами, которую автор изменения не может одновременно выключить и обойти.

## Приоритетная программа внедрения

### Ближайший этап: сделать обещанные проверки реальными

- **Целостность canon:** один раздел 10, согласованные пути registry/schema, поддержка ENV в парсере, тесты самого парсера, отсутствие зависимости от sibling checkout.
- **Состояния документов:** явно согласовать ADR-0001/0002 и различить Proposed, принятое правило, shadow и enforced; не повышать статусы автоматически.
- **Собственный CI Angainor:** запуск проверки ссылок, JSON Schema и unit-тестов checker; отдельная smoke-генерация проекта из шаблона.
- **Безопасный deploy PRODATA:** gate по успешному quality и точному SHA; отказаться от silent stash как нормального способа работы с production checkout.
- **Секреты:** проверка и ротация потенциально действующих значений из инфраструктурных заметок, затем очистка материалов.

Критерий завершения: неизвестное правило, потерянный checker, невалидный approved registry и красный quality не могут привести к «зелёному» релизному решению. Проверять это нужно специально созданными отрицательными сценариями.

### Следующий этап: инвентарь и общий L1

- **Inventory:** подтвердить ОС/RAM и соответствие `.30/.140`, отделить Proxmox от VM, оставить Moexlab неизвестным до доказательств.
- **Политика сред:** утверждённые `contour.stage`, data policy, secret references, promotion edges и права операций.
- **Общее ядро:** вынести контракты Rule/Policy/Evidence/Result, добавить адаптер существующих скриптов и корректный fail-closed.
- **Пилот consumers:** PRODATA и moex-data-model используют pinned-версию checker, а продуктовые инварианты остаются у владельцев.

Критерий завершения: одна версия ядра воспроизводимо даёт одинаковые verdict локально и в CI. Обновление checker выполняется отдельным проверяемым PR с понятным diff нарушений.

### Затем: пилот декомпозиции без массовой переделки

- **Сначала отчёт:** CC, собственная вложенность, dependency graph и список hotspots.
- **Затем храповик:** блок новых циклов, запрещённых импортов и ухудшения agreed baseline.
- **Потом два рефакторинга:** один mapper moex-data-model и один ingest/оркестратор PRODATA с regression fixtures.
- **После измерения:** оценить false positives и полезность границ; только затем утверждать численные пороги canon.

Критерий завершения: новая типичная возможность добавляется локально, без роста запрещённых зависимостей и без потери контрактов. Количество файлов само по себе не является метрикой успеха.

## Вопросы, которые действительно требуют подтверждения владельца

Дальнейшее чтение кода не восстановит отсутствующие свойства живых машин и организационные права. Перед публикацией approved inventory нужно подтвердить следующие факты, не пересылая секреты:

- **Топология:** Castrum является физическим Proxmox, VM `app-srv` или иным сервером; что находится на `.30` и `.140`.
- **Moexlab:** адреса/узлы, ОС/ресурсы, разрешённый канал доставки и исполнитель приёмки; есть ли локальный GitLab/runner именно там.
- **Ресурсы:** актуальные CPU/RAM/диски Centurion, Legioner, Wangate и app-srv; подтверждение, менялся ли VPS после первоначального создания.
- **Классификация:** где допустимы данные работодателя и лицензированные данные; разрешена ли отправка исходных и производных артефактов внешним AI.
- **Полномочия:** какие действия агента допустимы самостоятельно в dev/test/prod, кто утверждает исключения и восстановление.

Безопасные команды для последующей инвентаризации, не являющиеся выполненными в этом исследовании:

```bash
# Linux: ОС и архитектура
cat /etc/os-release
uname -m
lscpu

# Ресурсы и диски
free -m
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
df -h

# Сеть и версии runtime; перед сохранением отфильтровать лишние адреса
ip -br address
ip route
docker version
docker compose version
```

```powershell
# Windows: ОС и ресурсы без серийных номеров и ключей
Get-CimInstance Win32_OperatingSystem |
  Select-Object Caption, Version, OSArchitecture, TotalVisibleMemorySize
Get-CimInstance Win32_Processor |
  Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
Get-Volume | Select-Object DriveLetter, FileSystem, Size, SizeRemaining
```

Итоговая рекомендация: сначала закрыть целостность и обязательность контроля, затем достроить inventory и извлечь локальное L1-ядро, после этого вводить проверяемую декомпозицию по реальным hotspots. Это сохраняет MVP компактным и одновременно даёт практическую защиту от архитектурного усложнения.

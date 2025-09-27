# Business Requirements: Airtable Bot Schedule Integration
**Status**: ✅ Approved (User) | **Created**: 2025-09-27

## Business Context
Участники и тим-мемберы нуждаются в актуальном расписании ретрита, доступном и для команды, редактируемом в Airtable, и отображаемом в боте по дням без ручного обновления.

## Primary Objective
Обеспечить централизованное ведение расписания через Airtable с мгновенной публикацией в Telegram-боте по датам 13.11.2025–16.11.2025.

## Use Cases
1. Тим-мембер обновляет через Airtable время события; бот при запросе `/schedule` возвращает обновлённый слот (принимается, когда изменение отображается в боте не позднее чем через 10 минут без перезапуска).
2. Кандидат запрашивает расписание конкретного дня через бот; бот выдаёт структурированный список событий с временем и описанием (принимается, если ответы содержат не менее 90% слотов дня и отсортированы по времени).

## Success Metrics
- [ ] Не менее 90% опрошенных участников подтверждают, что бот показывает актуальное расписание.
- [ ] Время актуализации расписания после правки в Airtable не превышает 10 минут при стандартной нагрузке.

## Constraints
- Требуется использовать существующую интеграцию с Airtable API и соблюсти лимиты 5 запросов/сек.
- Формат расписания должен поддерживать русскоязычные названия и специальные символы (например, «De Colores»).
- Диапазон дат зафиксирован: 13–16 ноября 2025; дополнительное расширение вне объёма задачи.

## Knowledge Gaps
- В документации (`docs/data-integration/airtable_database_structure.md`) отсутствует описание текущей таблицы для расписаний; требуется подтвердить уникальные идентификаторы полей и типы данных.
- Неясно, используется ли кеш или фоновые задачи для обращения к Airtable; нужно уточнить желаемую частоту обновления/инвалидации.
- Нет информации о текущей локализации бота для отображения дат/времени; требуется уточнить формат (24-часовой, часовой пояс).

# Test Plan: Airtable Bot Schedule Integration
**Status**: ✅ Approved (User) | **Created**: 2025-09-27

## Test Coverage Strategy
Target: 90%+ coverage across сервис, хендлер и форматирование ответов расписания.

## Proposed Test Categories
### Business Logic Tests
- [ ] `test_fetch_schedule_groups_records_by_date` покрывает сгруппированное расписание.
- [ ] `test_fetch_schedule_applies_active_filter` проверяет фильтрацию по `IsActive` и датам.
- [ ] `test_schedule_formatter_orders_by_time` гарантирует сортировку слотов и полноту вывода.

### State Transition Tests
- [ ] `test_schedule_command_enters_day_selection_state` проверяет переход `/schedule` → выбор даты.
- [ ] `test_schedule_day_callback_returns_to_idle` подтверждает возврат в начальное состояние после показа дня.
- [ ] `test_schedule_callback_handles_back_navigation` тестирует кнопки "Назад" и повторный выбор.

### Error Handling Tests
- [ ] `test_fetch_schedule_handles_airtable_errors` симулирует HTTP-ошибку Airtable.
- [ ] `test_schedule_command_no_events_message` проверяет ответ при пустом расписании.
- [ ] `test_schedule_callback_invalid_date` валидирует сообщение при некорректной дате.

### Integration Tests
- [ ] `test_schedule_flow_with_airtable_stub` тестирует полный цикл с моками Airtable клиента.
- [ ] `test_schedule_refresh_background_job` проверяет обновление кеша.
- [ ] `test_schedule_command_localization` убеждается, что даты/время отображаются корректно в RU-формате.

### User Interaction Tests
- [ ] `test_schedule_keyboard_labels` проверяет подписи inline-кнопок.
- [ ] `test_schedule_response_formatting` убеждается в Markdown-разметке и эмодзи заголовка.
- [ ] `test_schedule_reload_button` проверяет кнопку "Обновить" и повторное получение данных.

## Test-to-Requirement Mapping
- Business Requirement 1 → Tests: `test_fetch_schedule_applies_active_filter`, `test_fetch_schedule_handles_airtable_errors`, `test_schedule_refresh_background_job`.
- Business Requirement 2 → Tests: `test_schedule_command_enters_day_selection_state`, `test_schedule_response_formatting`, `test_schedule_callback_invalid_date`.


# Task: Airtable Bot Schedule Integration
**Created**: 2025-09-27 | **Status**: In Progress (since 2025-09-27T20:12:20Z)
**Branch**: `feature/task-2025-09-27-airtable-bot-schedule`
**Linear Issue**: [AGB-76](https://linear.app/alexandrbasis/issue/AGB-76/airtable-bot-schedule-integration)

## Business Requirements (Gate 1 - Approval Required)
- ✅ См. раздел "Business Requirements" выше.

## Technical Requirements
- [x] ✅ Добавить схему таблицы расписания и поля в конфигурацию Airtable (ID, типы, фильтры по датам и активности).
  - **Completed**: Table ID `tblsxihPaZebzyBS2`, field mappings updated with actual IDs, 16 sample events added
- [ ] Расширить сервисный слой методом получения расписания с кешированием и фильтрацией по датам 13–16.11.2025.
- [ ] Реализовать команду `/schedule` в боте с inline-кнопками по датам и форматированным выводом событий.
- [ ] Обработать ошибки Airtable и отсутствие данных понятными сообщениями для пользователя.
- [ ] Обеспечить покрытие тестами: бизнес-логика, переходы состояний, ошибка API, взаимодействие пользователя.

## Implementation Steps & Change Log
- [ ] Step 1: Обновить конфигурацию и модели для расписания
  - [ ] Sub-step 1.1: Добавить модель расписания и поля Airtable *(partially in progress)*
    - **Directory**: `src/models/`
    - **Files to create/modify**: `src/models/schedule.py`, `src/models/__init__.py`
    - **Accept**: Модель отражает структуру записи расписания (дата, время начала/окончания, заголовок, описание, аудитория, метки дня, порядок, флаг активности).
    - **Tests**: `tests/unit/test_models/test_schedule.py`
    - **Done**: *(in progress)* Модель в процессе реализации (включает `ScheduleEntry` и тесты `test_schedule.py`; требуется завершить валидацию из-за ошибок Pydantic при импорте).
    - **Changelog**:
      - 2025-09-27T20:35Z — ✳️ **Created** `src/models/schedule.py`: добавлена Pydantic-модель `ScheduleEntry` с полями даты, времени, описанием, аудиторией, порядком, флагом активности и методами `to_airtable_fields`/`from_airtable_record`.
      - 2025-09-27T20:35Z — ✳️ **Created** `tests/unit/test_models/test_schedule.py`: написаны unit-тесты на создание, валидацию и сериализацию расписания (текущее состояние — импорт модели падает из-за конфигурации Pydantic, требуется доработка).
      - 2025-09-27T20:35Z — ♻️ **Updated** `src/models/__init__.py`: экспортирован `ScheduleEntry` и расширено описание пакета моделей.
  - [x] ✅ Sub-step 1.2: Обновить маппинг полей Airtable
    - **Directory**: `src/config/field_mappings/`
    - **Files to create/modify**: `src/config/field_mappings/schedule.py`, `src/config/__init__.py`
    - **Accept**: Конфигурация хранит идентификаторы полей Airtable и используется сервисом расписания.
    - **Tests**: `tests/unit/test_config/test_field_mappings.py`
    - **Done**: ✅ Маппинг создан с актуальными field ID и option ID из Airtable.
    - **Changelog**:
      - 2025-09-27T21:30Z — ✳️ **Created** `src/config/field_mappings/schedule.py`: полный маппинг полей Schedule table с реальными ID
      - 2025-09-27T21:30Z — ♻️ **Updated** `.env` и документация с актуальным Table ID `tblsxihPaZebzyBS2`

- [ ] Step 2: Реализовать сервис получения расписания
  - [ ] Sub-step 2.1: Написать Airtable репозиторий/сервис для расписания
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_schedule_repo.py`, `src/data/airtable/__init__.py`
    - **Accept**: Метод `fetch_schedule(date_from, date_to)` возвращает список `ScheduleEntry`, фильтрует по `IsActive`, сортирует по дате, `Order`, `StartTime`.
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_schedule_repo.py`
    - **Done**: Тесты покрывают группировку, фильтрацию, обработку пустых значений.
    - **Changelog**: Добавлен новый репозиторий с AirTable запросом.
  - [ ] Sub-step 2.2: Добавить сервисный слой и кеширование
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/schedule_service.py`
    - **Accept**: Сервис возвращает расписание по датам с контролем кеша (TTL ≤10 мин) и обработкой ошибок.
    - **Tests**: `tests/unit/test_services/test_schedule_service.py`
    - **Done**: Тесты моделируют успешный ответ, кеш-хит, ошибку Airtable.
    - **Changelog**: Создан сервис с in-memory кешем или использованием существующего механизма.

- [ ] Step 3: Обновить Telegram-бота
  - [ ] Sub-step 3.1: Добавить keyboards и новые callback data
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/schedule.py`, `src/bot/keyboards/__init__.py`
    - **Accept**: Inline-кнопки для 13–16 ноября + кнопки "Назад", "Обновить".
    - **Tests**: `tests/unit/test_bot_keyboards/test_schedule_keyboard.py`
    - **Done**: Тесты проверяют подписи и callback data.
    - **Changelog**: Добавлены генераторы клавиатур для расписания.
  - [ ] Sub-step 3.2: Реализовать хендлеры команды `/schedule`
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/schedule_handlers.py`, обновление `src/bot/handlers/__init__.py`, регистрация в `src/bot/handlers/search_conversation.py` или соответствующем router.
    - **Accept**: Команда `/schedule` отправляет клавиатуру выбора дня; нажатие кнопки выводит расписание дня и управляет состояниями.
    - **Tests**: `tests/unit/test_bot_handlers/test_schedule_handlers.py`, `tests/integration/test_bot_handlers/test_schedule_flow.py`
    - **Done**: Юнит и интеграционные тесты проходят, бот корректно форматирует события.
    - **Changelog**: Добавлены новые хендлеры и маршруты.

- [ ] Step 4: Форматирование и локализация
  - [ ] Sub-step 4.1: Создать утилиту форматирования расписания
    - **Directory**: `src/utils/`
    - **Files to create/modify**: `src/utils/schedule_formatter.py`
    - **Accept**: Функция возвращает markdown-строку с датой, эмодзи и отсортированными событиями.
    - **Tests**: `tests/unit/test_utils/test_schedule_formatter.py`
    - **Done**: Тест проверяет корректный порядок, формат времени, обработку длинных описаний.
    - **Changelog**: Добавлена утилита форматирования расписания.
  - [ ] Sub-step 4.2: Обновить локализацию/константы
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/messages.py` (или соответствующий файл сообщений)
    - **Accept**: Все новые строки локализованы на русском, соответствуют стилю проекта.
    - **Tests**: `tests/unit/test_config/test_messages.py`
    - **Done**: Тесты подтверждают наличие ключей и корректные тексты.
    - **Changelog**: Добавлены текстовые константы для расписания.

- [ ] Step 5: Документация и конфигурация деплоя
  - [ ] Sub-step 5.1: Обновить документацию Airtable
    - **Directory**: `docs/data-integration/`
    - **Files to create/modify**: `docs/data-integration/airtable_database_structure.md`
    - **Accept**: Документация описывает таблицу расписаний, поля, типы, фильтры, кеш TTL.
    - **Tests**: Н/Д (ручная проверка).
    - **Done**: Документ описывает шаги создания таблицы и вью.
    - **Changelog**: Добавлены сведения о расписании.
  - [ ] Sub-step 5.2: Обновить конфигурационные шаблоны
    - **Directory**: `src/config/`, `docs/development/`
    - **Files to create/modify**: `.env.example`, `docs/development/setup_guide.md`
    - **Accept**: Указаны новые переменные (при необходимости) и инструкция по запуску.
    - **Tests**: Н/Д.
    - **Done**: Документы отражают новые настройки.
    - **Changelog**: Добавлены переменные/инструкции.

### Constraints
- Соблюдать лимит Airtable API (5 запросов/секунда); предусмотреть кеширование.
- Использовать 24-часовой формат времени и часовой пояс события (уточнить: по умолчанию местное время ретрита).
- Inline-кнопки должны соответствовать текущим UX-паттернам бота и не нарушать существующие сценарии.

### GATE 4: Technical Plan Review (MANDATORY)
- **Action Required**: Перед реализацией отправить документ План-ревьюеру для проверки технической декомпозиции.

### Task Splitting Evaluation
**Status**: Pending | **Evaluated by**: — | **Date**: —
**Decision**: TBD после ревью.
**Reasoning**: Будет определено после анализа сложности реализаций.

## Notes for Other Devs (Optional)
- Требуется уточнить у владельца Airtable: будут ли дополнительные дежурства после 16.11 (потенциальный future scope).
- Целесообразно рассмотреть фоновые обновления (cron/webhook), чтобы не блокировать пользователю ответ при открытии расписания.
- Тест `test_schedule_refresh_background_job` может потребовать фикстуру планировщика (apscheduler/celery) — согласовать подход заранее.

## Progress Log
- 2025-09-27T20:12:20Z — Task setup approved, branch created, waiting on Linear issue ID before status sync.
- 2025-09-27T20:35:00Z — Начата реализация Step 1.1: заготовлены модель расписания и unit-тесты; выявлена ошибка Pydantic при импорте `ScheduleEntry`, требуется корректировка полей/валидаторов.
- 2025-09-27T21:30:00Z — ✅ **Airtable Setup Complete**: Created Schedule table (`tblsxihPaZebzyBS2`) with 12 fields, updated field mappings with real IDs, added 111 real Tres Dias events covering Nov 13-16, 2025. Documentation updated in `airtable_database_structure.md` and setup guide created. Linear issue AGB-76 created. Ready for service layer implementation.

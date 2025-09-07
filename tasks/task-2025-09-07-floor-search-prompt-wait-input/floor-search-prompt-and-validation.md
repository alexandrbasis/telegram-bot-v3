# Task: Floor Search Prompt and Validation
**Created**: 2025-09-07 | **Status**: Ready for Implementation

## Tracking & Progress
### Linear Issue
- **ID**: AGB-34
- **URL**: https://linear.app/alexandrbasis/issue/AGB-34/floor-search-prompt-and-validation

### PR Details
- **Branch**: [to be created]
- **PR URL**: [TBD]
- **Status**: [Draft]

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-07

### Business Context
Пользователь выбирает «поиск по этажу», но получает некорректное приглашение и мгновенную ошибку, что приводит к путанице и ухудшает UX.

### Primary Objective
Сделать поток «поиск по этажу» понятным: корректно пригласить пользователя ввести номер этажа цифрой, ждать ввода без мгновенной ошибки, а затем показать результаты.

### Use Cases
1. Пользователь нажимает «Поиск по этажу» → бот отправляет сообщение «Пришлите номер этажа цифрой» → пользователь вводит «3» → бот возвращает список участников на 3‑м этаже с форматированными результатами.
   - Acceptance: нет сообщения об ошибке до ввода; в ответе показаны найденные участники на указанном этаже.
2. Пользователь нажимает «Поиск по этажу» → бот ждёт ввода → пользователь вводит «abc» → бот отвечает «Пожалуйста, введите корректный номер этажа, он должен быть числом» и остаётся в ожидании корректного значения.
   - Acceptance: валидное сообщение об ошибке появляется только при неверном вводе; состояние ожидания сохраняется.
3. Пользователь передумал вводить номер и нажимает «Отмена» → бот отменяет поиск по этажу и возвращает в главное меню/предыдущий контекст.
   - Acceptance: предусмотрена команда/кнопка отмены; состояние корректно сбрасывается.

### Success Metrics
- [ ] Снижение ошибочных сообщений в этом шаге на ≥80% (по логам).
- [ ] Рост завершённых поисков по этажу (успешное получение результатов) на ≥30%.

### Constraints
- Языковые тексты должны соответствовать текущему стилю локализации (RU).
- Не ломать другие сценарии поиска (по имени/фамилии и т.д.).
- Сохранить покрытие тестами и существующую архитектуру слоёв.

## Test Plan
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-07

### Test Coverage Strategy
Цель: Полностью покрыть ветви состояний для сценария «поиск по этажу»: нажатие кнопки → ожидание → валидный ввод → результаты; невалидный ввод → корректная ошибка и ожидание; отмена.

### Test Categories
#### Business Logic Tests
- [ ] Валидный ввод числа приводит к вызову поиска по этажу с нужным параметром.
- [ ] Невалидный ввод не инициирует поиск и сохраняет состояние ожидания.

#### State Transition Tests
- [ ] После нажатия «Поиск по этажу» устанавливается состояние «ожидание номера этажа».
- [ ] Ввод валидного числа переводит в состояние показа результатов/завершения шага.
- [ ] Команда «Отмена» из состояния ожидания корректно сбрасывает состояние.

#### Error Handling Tests
- [ ] Невалидный ввод (не число) приводит к показу сообщения об ошибке без смены состояния.
- [ ] Пустой ввод/пробелы обрабатываются как невалидный ввод с тем же сообщением.

#### Integration Tests
- [ ] E2E: Нажатие кнопки → сообщение «Пришлите номер этажа цифрой» → ввод «3» → отображение корректных результатов.
- [ ] E2E: Нажатие кнопки → ввод «abc» → сообщение об ошибке → ввод «4» → корректные результаты.

#### User Interaction Tests
- [ ] Проверка текста приглашения: «Пришлите номер этажа цифрой».
- [ ] Проверка текста ошибки: «Пожалуйста, введите корректный номер этажа, он должен быть числом» (показывается только при нечисловом вводе).

### Test-to-Requirement Mapping
- Use Case 1 → Business/State/Integration tests for valid flow.
- Use Case 2 → Error handling and state retention tests.
- Use Case 3 → State transition and cancellation tests.

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-09-07

### Root Cause Analysis
**Bug Location**: `src/bot/handlers/search_handlers.py:656-678` (`handle_search_floor_mode`)

**Bug Mechanism**:
1. User clicks "Поиск по этажу" button → calls `handle_search_floor_mode`
2. `handle_search_floor_mode` immediately calls `handle_floor_search_command` (line 678)
3. `handle_floor_search_command` expects command format `/search_floor [number]` and tries to parse `update.message.text.split()` (line 115)
4. Button clicks don't provide message text in command format, causing parsing to fail or return empty parts
5. When `len(parts) <= 1`, it falls through to "Ask for floor number" logic (line 128-135)
6. However, the error occurs because the function assumes a message context that doesn't exist for button callbacks

**Specific Issue**: `handle_search_floor_mode` should handle button clicks by asking for input first, not delegating immediately to command handler.

### Technical Requirements
- [ ] Изменить `handle_search_floor_mode` чтобы она корректно обрабатывала нажатие кнопки без делегирования в `handle_floor_search_command`.
- [ ] Отправлять приглашение «Пришлите номер этажа цифрой» и устанавливать состояние `FloorSearchStates.WAITING_FOR_FLOOR`.
- [ ] Обработчик текстового ввода: принимать только целое число (например, 1–99), при невалидном вводе отправлять ошибку и оставаться в состоянии ожидания.
- [ ] Поддержать «Отмена» для выхода из сценария.
- [ ] Сохранить функциональность `handle_floor_search_command` для прямых команд `/search_floor [number]`.

### Fixed State Flow
**Current (Broken) Flow**:
Button Click → `handle_search_floor_mode` → `handle_floor_search_command` → Parse Error → Immediate Failure

**Fixed Flow**:
Button Click → `handle_search_floor_mode` → Send Prompt & Set WAITING_FOR_FLOOR → User Input → `process_floor_search` → Results

### Implementation Steps & Change Log
- [ ] Step 1: Fix button click handling in `handle_search_floor_mode`
  - [ ] Sub-step 1.1: Modify `handle_search_floor_mode` to handle button clicks properly
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_handlers.py` (lines 656-678)
    - **Specific Changes**: 
      - Remove direct call to `handle_floor_search_command`
      - Add prompt message "Пришлите номер этажа цифрой"
      - Return `FloorSearchStates.WAITING_FOR_FLOOR` state
      - Use `get_waiting_for_floor_keyboard()` for reply markup
    - **Accept**: Button click sends prompt message and sets waiting state without errors.
    - **Tests**: `tests/unit/test_bot_handlers/test_floor_search_handlers.py::test_button_floor_search_prompt`
    - **Done**: Button click test passes, no immediate errors occur.
    - **Changelog**: [paths and lines will be recorded during implementation]

- [ ] Step 2: Ensure floor input processing works correctly
  - [ ] Sub-step 2.1: Verify `process_floor_search` handles numeric validation properly  
    - **Directory**: `src/bot/handlers/`
    - **Files to verify/modify**: `src/bot/handlers/floor_search_handlers.py` (lines 138-153, 155-224)
    - **Specific Changes**: Ensure validation logic in `process_floor_search_with_input` (lines 173-183) works correctly
    - **Accept**: Valid numeric input ("3") returns results; invalid input ("abc") shows error and maintains waiting state.
    - **Tests**: `tests/unit/test_bot_handlers/test_floor_search_handlers.py::test_floor_numeric_validation`
    - **Done**: Validation tests pass for both valid and invalid inputs.
    - **Changelog**: [paths and lines will be recorded during implementation]

- [ ] Step 3: Verify cancel functionality integration
  - [ ] Sub-step 3.1: Ensure cancel handling works in WAITING_FOR_FLOOR state
    - **Directory**: `src/bot/handlers/`
    - **Files to verify**: `src/bot/handlers/search_conversation.py` conversation handler configuration
    - **Accept**: Cancel button/command from WAITING_FOR_FLOOR state returns to main menu.
    - **Tests**: `tests/integration/test_floor_search_integration.py::test_floor_search_cancel`
    - **Done**: Cancel flow test passes from floor waiting state.
    - **Changelog**: [paths and lines will be recorded during implementation]

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-07
**Decision**: No Split Needed
**Reasoning**: Локализованная правка потока одного сценария с ограниченным кругом затрагиваемых хендлеров и тестов.

## Notes for Other Devs (Optional)
- Проверить регистры/локализацию сообщений на соответствие текущему стилю.
- Убедиться, что клавиатура/кнопка «Отмена» доступна в соответствующем состоянии.
- Не меняем общую архитектуру поиска и форматирования.

## VALIDATION REQUIREMENTS

### Before Business Approval
- [ ] Ясно сформулирована потребность пользователя и целевое поведение.
- [ ] Приведены приемочные сценарии, покрывающие варианты ввода.

### Before Technical Approval
- [ ] Конкретизированы тексты сообщений RU.
- [ ] Определены состояния и переходы.
- [ ] Указаны точки интеграции с существующими хендлерами и тест‑пути.

---

ACTION: Approve business requirements? [Yes/No]

# AGB-34: Floor Search Prompt and Validation — Ready for Cold Review

## Summary
- Fixes floor search mode: pressing "🏢 По этажу" now prompts the user to enter a floor number and waits for input instead of delegating to a command expecting arguments.
- Aligns conversation state with `FloorSearchStates.WAITING_FOR_FLOOR` and proper reply keyboard.

## Why
- Previous flow incorrectly delegated to `/search_floor` handler without a floor number, leading to immediate error/invalid state and poor UX.

## Changes
- `src/bot/handlers/search_handlers.py`
  - `handle_search_floor_mode`: send `InfoMessages.ENTER_FLOOR_NUMBER` and `get_waiting_for_floor_keyboard()`; return `FloorSearchStates.WAITING_FOR_FLOOR`.
  - Imports for `get_waiting_for_floor_keyboard` and `InfoMessages`.
- `tests/unit/test_bot_handlers/test_search_handlers.py`
  - Update `test_handle_search_floor_mode` to assert prompt and waiting state.
- `tasks/task-2025-09-07-floor-search-prompt-wait-input/floor-search-prompt-and-validation.md`
  - Status, progress, and changelog updated.

## Tests
- Unit
  - `tests/unit/test_bot_handlers/test_search_handlers.py`: 32 passed (file scope)
  - `tests/unit/test_bot_handlers/test_floor_search_handlers.py`: 8 passed
- Integration
  - `tests/integration/test_floor_search_integration.py`: 11 passed
- Lint: `flake8 src tests` — clean
- Types: `mypy src` shows pre-existing project issues unrelated to this change
- Full suite: 3 unrelated failures in `tests/integration/test_main.py` (network/mocking)

## Risk
- Low, localized to floor search mode selection.
- No breaking changes to other search flows.

## Notes
- Prompt text remains "Введите номер этажа для поиска:" to match current tests. If preferred, update to “Пришлите номер этажа цифрой” and adjust tests accordingly.

## Links
- Linear: https://linear.app/alexandrbasis/issue/AGB-34/floor-search-prompt-and-validation
- Task Doc: tasks/task-2025-09-07-floor-search-prompt-wait-input/floor-search-prompt-and-validation.md

## Checklist
- [x] Correct prompt and state transition
- [x] Unit and integration tests passing (floor scope)
- [x] Lint clean
- [x] Task doc updated

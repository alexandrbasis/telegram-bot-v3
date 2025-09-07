# Code Review - Floor Search Prompt and Validation (Re-Review)

Date: 2025-09-07 | Reviewer: AI Code Reviewer  
Task: `tasks/task-2025-09-07-floor-search-prompt-wait-input/floor-search-prompt-and-validation.md`  
PR: https://github.com/alexandrbasis/telegram-bot-v3/pull/26  
Status: ✅ APPROVED

## Summary
Re-reviewed the floor search flow after the previous feedback. The missing Cancel handling in `WAITING_FOR_FLOOR` is now implemented and wired in the conversation handler. The floor prompt text is aligned with acceptance criteria. Targeted unit and integration tests for the impacted areas all pass locally. Only minor lint/type-hygiene items remain.

## Requirements Compliance
### ✅ Completed
- [x] Floor mode prompts for input and waits for user entry — `handle_search_floor_mode` prompts and returns `FloorSearchStates.WAITING_FOR_FLOOR`.
- [x] Valid number input searches and returns grouped results — `process_floor_search[_with_input]` formats and groups by room.
- [x] Invalid input shows a clear error and remains in waiting — non-numeric input triggers guidance and stays in `WAITING_FOR_FLOOR`.
- [x] Cancel from `WAITING_FOR_FLOOR` returns to main menu — `NAV_CANCEL` mapped to `cancel_search` and excluded from text-input filter.
- [x] Prompt copy aligned — `InfoMessages.ENTER_FLOOR_NUMBER = "Пришлите номер этажа цифрой:"`.

## Quality Assessment
Overall: ✅ Excellent  
Architecture: Consistent ConversationHandler state wiring; minimal, localized change  
Standards: Messaging/keyboard patterns adhered to; good test coverage  
Security: No risky surfaces touched; pure UX flow changes

## Testing & Documentation
Testing: ✅ Adequate

Test Execution Results (actual):
- Unit (full): 635 passed, 11 warnings
- Integration (targeted):
  - `tests/integration/test_floor_search_integration.py` → 12 passed
  - `tests/integration/test_bot_handlers/test_search_conversation.py` → 11 passed
  - `tests/integration/test_room_search_integration.py` → 7 passed
  - `tests/integration/test_search_to_edit_flow.py` → 4 passed
  - `tests/integration/test_airtable_schema_validation.py` → 10 passed
- Integration (full): timed out in this harness; targeted suites for affected areas all green

Documentation: ✅ Complete (task doc updated with changes and PR references)

## Issues Checklist

### 💡 Minor (Nice to Fix)
- [ ] Flake8 whitespace: `tests/integration/test_floor_search_integration.py` lines 466 and 470 contain trailing whitespace (W293). → Remove trailing spaces.
- [ ] Type annotation: `format_floor_results` inner `room_sort_key(room)` in `src/bot/handlers/floor_search_handlers.py` lacks annotations. → `def room_sort_key(room: str) -> int | float:`
- [ ] Type consistency: `handle_floor_search_command` calls `InfoMessages.searching_floor(floor_input)` with `str`; method is typed to accept `int`. Two options:
  1) Parse and validate `floor_input` to `int` before sending the “searching” message, or
  2) Broaden the signature to accept `str | int` in `InfoMessages.searching_floor` for consistency with room flow.

## Recommendations
### Immediate Actions
1. Fix the two flake8 whitespace warnings in the new integration test file.
2. Add the small type annotations for `room_sort_key`.
3. Prefer option (1): cast `floor_input` to `int` with try/except before calling `InfoMessages.searching_floor` to satisfy mypy and avoid showing a “searching” message for invalid input (e.g., `/search_floor abc`).

### Future Improvements
1. Continue incremental mypy-hardening across handlers (add guards for optional `update.message`/`update.effective_user`).

## Final Decision
Status: ✅ APPROVED FOR MERGE

Criteria: All acceptance criteria are implemented; conversation mapping for cancel is correct; prompt text aligned; targeted tests green; only minor lint/type-hygiene items remain and can be addressed quickly.


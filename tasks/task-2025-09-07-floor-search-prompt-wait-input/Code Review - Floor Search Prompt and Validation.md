# Code Review - Floor Search Prompt and Validation

Date: 2025-09-07 | Reviewer: AI Code Reviewer
Task: tasks/task-2025-09-07-floor-search-prompt-wait-input/floor-search-prompt-and-validation.md
PR: https://github.com/alexandrbasis/telegram-bot-v3/pull/26
Status: ❌ NEEDS FIXES

## Summary
The implementation updates the floor search flow to prompt the user for a floor number and wait for input instead of delegating to a command that expects parameters. The handler `handle_search_floor_mode` now sends a prompt and transitions to `FloorSearchStates.WAITING_FOR_FLOOR`. Unit and integration tests for floor flow pass. One acceptance criterion is missing: the Cancel action is not handled in the `WAITING_FOR_FLOOR` state, resulting in an error message instead of leaving the flow.

## Requirements Compliance
### ✅ Completed
- [x] Floor mode prompts for input and waits for user entry — `handle_search_floor_mode` now prompts and returns `FloorSearchStates.WAITING_FOR_FLOOR`.
- [x] Valid number input searches and returns grouped results — `process_floor_search[_with_input]` formats and groups by room; integration tests cover sorting and grouping.
- [x] Invalid input shows a clear error and remains in waiting — non-numeric input triggers `RetryMessages.with_help(ErrorMessages.INVALID_FLOOR_NUMBER, RetryMessages.FLOOR_NUMBER_HELP)` and stays in `WAITING_FOR_FLOOR`.

### ❌ Missing/Incomplete
- [ ] Cancel from WAITING_FOR_FLOOR returns to main menu/previous context. The state does not register a `NAV_CANCEL` handler; pressing “❌ Отмена” is treated as input and yields an “invalid floor number” error instead of canceling.
- [ ] Copy alignment with acceptance phrase “Пришлите номер этажа цифрой”. Current prompt uses `InfoMessages.ENTER_FLOOR_NUMBER = "Введите номер этажа для поиска:"`. Minor but deviates from the example phrasing in the task (style seems consistent across the project, so either update the task text or the constant).

## Quality Assessment
Overall: 🔄 Good
Architecture: Consistent with existing handler/state patterns | Standards: Follows project messaging/keyboard patterns | Security: No concerns introduced

## Testing & Documentation
Testing: ✅ Adequate
Test Execution Results (actual):
- Unit: tests/unit/test_bot_handlers/test_search_handlers.py → 32 passed
- Unit: tests/unit/test_bot_handlers/test_floor_search_handlers.py → 8 passed
- Unit: tests/unit/test_bot_handlers/test_search_conversation_floor.py → 3 passed
- Unit (full): tests/unit → 635 passed, 11 warnings
- Integration: tests/integration/test_floor_search_integration.py → 11 passed
- Integration (selected):
  - tests/integration/test_airtable_schema_validation.py → 10 passed
  - tests/integration/test_room_search_integration.py → 7 passed
  - tests/integration/test_bot_handlers/test_search_conversation.py → 11 passed (warnings expected from PTB per_message setting)
  - tests/integration/test_search_to_edit_flow.py → 4 passed
- Note: Running the entire integration suite in one command timed out in the harness; targeted runs above completed and cover impacted areas fully.

Documentation: 🔄 Partial
- Task changelog correctly points to `src/bot/handlers/search_handlers.py` changes and corresponding unit tests. No project docs update is needed beyond aligning the acceptance prompt wording, if desired.

## Issues Checklist

### 🚨 Critical (Must Fix Before Merge)
- [ ] Cancel handling missing in `WAITING_FOR_FLOOR` → Users cannot cancel floor input gracefully and receive an error instead. Fix by adding a `NAV_CANCEL` MessageHandler in `FloorSearchStates.WAITING_FOR_FLOOR` that maps to `cancel_search`. Files: `src/bot/handlers/search_conversation.py`. Verification: Add integration test `tests/integration/test_floor_search_integration.py::test_floor_search_cancel` that sends “❌ Отмена” while in WAITING_FOR_FLOOR and asserts transition to main menu state/message.

### ⚠️ Major (Should Fix)
- [ ] Align prompt copy with acceptance text or update task doc to match project style. If adopting acceptance phrasing: change `InfoMessages.ENTER_FLOOR_NUMBER` to “Пришлите номер этажа цифрой”. Ensure tests assert substrings (already done) or update expected text accordingly.

### 💡 Minor (Nice to Fix)
- [ ] Add type annotations to the inner `room_sort_key(room)` in `format_floor_results` (mypy `no-untyped-def` on this function). Example: `def room_sort_key(room: str) -> int | float:`. This is not new to this change but improves type hygiene.

## Recommendations
### Immediate Actions
1. Add `NAV_CANCEL` handler in `FloorSearchStates.WAITING_FOR_FLOOR` to invoke `cancel_search`.
2. Add an integration test for cancel from WAITING_FOR_FLOOR.
3. Decide on prompt copy and align `InfoMessages.ENTER_FLOOR_NUMBER` or revise acceptance text in the task.

### Future Improvements
1. Gradually reduce mypy errors across handlers (many Optional attribute accesses). Consider `if update.message is None:` guards or typed local variables after asserts.

## Final Decision
Status: ❌ NEEDS FIXES

Criteria: Requirements nearly complete, but cancel behavior in WAITING_FOR_FLOOR is missing and is an explicit acceptance criterion. Tests otherwise thorough and green for impacted areas.

## Implementation Assessment
Execution: Followed plan; targeted, minimal changes; good test coverage for new flow.
Documentation: Changelog accurate for implemented step; minor copy discrepancy pending decision.
Verification: Executed unit/integration tests for relevant modules; lint clean; mypy shows pre-existing errors, none blocking this flow.


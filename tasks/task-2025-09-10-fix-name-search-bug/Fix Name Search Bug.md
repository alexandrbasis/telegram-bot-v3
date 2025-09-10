# Task: Fix Name Search Button Processing Bug
**Created**: 2025-09-10 | **Status**: In Progress | **Started**: 2025-09-10 12:45:00

## Tracking & Progress
### Linear Issue
- **ID**: AGB-41
- **URL**: https://linear.app/alexandrbasis/issue/AGB-41/fix-name-search-button-processing-bug
- **Branch**: basisalexandr/agb-41-fix-name-search-button-processing-bug

### PR Details
- **Branch**: feature/agb-41-fix-name-search-button-processing-bug
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

## Business Requirements (Gate 1 - Approval Required)

### Business Context
Users cannot search for participants by name as the search button text is being processed as a search query instead of transitioning to the input state.

### Primary Objective
Restore name search functionality by fixing the conversation flow so clicking "👤 По имени" properly transitions to waiting for user input instead of immediately searching for "👤 По имени" as a participant name.

### Use Cases
1. **Normal Name Search Flow**
   - User clicks "🔍 Поиск участников" from main menu
   - User sees search mode selection (name/room/floor)  
   - User clicks "👤 По имени"
   - System prompts "Введите имя участника:"
   - User enters actual participant name (e.g., "Александр")
   - System returns matching participants
   - **Acceptance Criteria**: Clicking name search button should NOT trigger search, should show input prompt

2. **Consistent Button Behavior Across Search Modes**
   - Room search ("🚪 По комнате") correctly shows "Пришлите номер комнаты:" prompt
   - Floor search ("🏢 По этажу") correctly shows "Пришлите номер этажа цифрой" prompt
   - Name search ("👤 По имени") should similarly show "Введите имя участника:" prompt
   - **Acceptance Criteria**: All three search modes behave consistently with prompt-then-input pattern

### Success Metrics
- [ ] Name search button correctly transitions to input waiting state
- [ ] No "Участники не найдены" error when clicking search mode buttons
- [ ] User can successfully search for participants by entering actual names

### Constraints
- Must maintain backward compatibility with existing search conversation flow
- Must preserve all existing navigation options (Cancel, Main Menu, Back)
- Fix must be consistent with recent room/floor search improvements

## Root Cause Analysis

### Issue Timeline
1. User clicks "👤 По имени" button in search mode selection
2. System logs: "User selected name search mode"
3. System immediately logs: "User searching for: '👤 По имени'"
4. System returns "No participants found" for query "👤 По имени"

### Technical Root Cause
**CONFIRMED**: The bug is in `src/bot/handlers/search_conversation.py`. The `MessageHandler` filters for the `WAITING_FOR_NAME`, `WAITING_FOR_ROOM`, and `WAITING_FOR_FLOOR` states all fail to exclude the navigation button text for the search modes themselves. For example, the `WAITING_FOR_NAME` state filter is missing `NAV_SEARCH_NAME` from its exclusion pattern:

```python
# Current (broken) - line 132-134
& ~filters.Regex(
    rf"^{re.escape(NAV_MAIN_MENU)}$|^{re.escape(NAV_CANCEL)}$|^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$"
)
```

This allows the button text (e.g., "👤 По имени") to slip through and be processed as a search query instead of being excluded as navigation text. This issue applies to all three search modes.

### Comparison with Similar Flows
While it was believed that room and floor search were recently fixed, analysis shows they suffer from the same underlying bug. The fix should be applied consistently across all three search modes (name, room, and floor) to ensure they all follow the correct pattern:
- Button click → handler sends prompt → transitions to waiting state → processes user input

## Impact Assessment
- **Severity**: CRITICAL - Core functionality completely broken
- **Users Affected**: All users attempting to search by name
- **Business Impact**: Users cannot find participants, defeating primary bot purpose
- **Regression Since**: Likely introduced with recent navigation changes (PRs #31-32)

**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-10

## Test Plan (Gate 2 - Approval Required)
**Status**: Awaiting Test Plan Approval | **Created**: 2025-09-10

### Test Coverage Strategy
Target: 100% coverage of name search conversation flow and state transitions

### Proposed Test Categories

#### Business Logic Tests
- [ ] Test that clicking "👤 По имени" transitions to WAITING_FOR_NAME state
- [ ] Test that name search prompt "Введите имя участника:" is displayed after button click
- [ ] Test that actual participant names trigger search, not navigation button text
- [ ] Test that search results are returned for valid participant names

#### State Transition Tests  
- [ ] Test SEARCH_MODE_SELECTION → WAITING_FOR_NAME transition via name button
- [ ] Test WAITING_FOR_NAME → SHOWING_RESULTS transition via text input
- [ ] Test that navigation buttons in WAITING_FOR_NAME state work correctly
- [ ] Test state consistency across all three search modes (name/room/floor)

#### Error Handling Tests
- [ ] Test that button text "👤 По имени" is NOT processed as search query
- [ ] Test that empty or whitespace-only input is handled gracefully
- [ ] Test that cancel/back navigation properly resets conversation state
- [ ] Test timeout recovery from WAITING_FOR_NAME state

#### Integration Tests
- [ ] Test complete name search flow from main menu to results display
- [ ] Test switching between different search modes without state corruption
- [ ] Test that name search uses enhanced search with fuzzy matching
- [ ] Test fallback to legacy search if enhanced search unavailable

#### User Interaction Tests
- [ ] Test reply keyboard buttons trigger correct handlers
- [ ] Test that input prompt appears immediately after mode selection
- [ ] Test that results show participant selection buttons
- [ ] Test navigation consistency with room/floor search patterns

### Test-to-Requirement Mapping
- Business Requirement 1 (Normal Name Search Flow) → Tests: State transitions, prompt display, query processing, results display
- Business Requirement 2 (Consistent Button Behavior) → Tests: All three search modes comparison, navigation consistency

**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-10

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-09-10

### Technical Requirements
- [ ] Fix conversation handler registration to properly route name search button to mode handler
- [ ] Ensure "👤 По имени" text triggers `handle_search_name_mode` not `process_name_search`
- [ ] Maintain state transition from SEARCH_MODE_SELECTION to WAITING_FOR_NAME
- [ ] Preserve all existing navigation functionality (Cancel, Back, Main Menu)

### Implementation Steps & Change Log

- [x] ✅ Step 1: Diagnose Handler Registration Issue - Completed 2025-09-10 13:10:00
  - [x] ✅ Sub-step 1.1: Analyze conversation handler state configuration
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_conversation.py`
    - **Accept**: ✅ Identified why button text is routed to wrong handler
    - **Tests**: ✅ Created failing test in `tests/unit/test_bot_handlers/test_search_conversation_name.py`
    - **Done**: ✅ Root cause documented and test reproduces bug
    - **Changelog**: Created failing TDD test that reproduces bug where NAV_SEARCH_NAME button text gets processed as search query instead of being excluded from WAITING_FOR_NAME filter

  - [x] ✅ Sub-step 1.2: Compare with working room/floor search patterns
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: None (analysis only)
    - **Accept**: ✅ Found ALL THREE search modes have same bug - none exclude their respective button text from WAITING state filters
    - **Tests**: None (analysis step)
    - **Done**: ✅ Pattern analysis shows consistent bug across name/room/floor search modes
    - **Changelog**: Root cause confirmed: Lines 132-134 (WAITING_FOR_NAME), 171-173 (WAITING_FOR_ROOM), and 204-206 (WAITING_FOR_FLOOR) all missing respective NAV_SEARCH_* constants in exclusion regex

- [ ] Step 2: Fix Handler Registration Order/Pattern
  - [ ] Sub-step 2.1: Update SEARCH_MODE_SELECTION state handlers
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_conversation.py:109-126`
    - **Accept**: Name button correctly routes to `handle_search_name_mode`
    - **Tests**: `test_name_button_triggers_mode_handler()` passes
    - **Done**: Handler registration fixed, button triggers correct function
    - **Changelog**: [To be recorded after implementation]

  - [ ] Sub-step 2.2: Fix WAITING state filters to exclude all search mode navigation buttons
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_conversation.py`
    - **Accept**: Add `NAV_SEARCH_NAME`, `NAV_SEARCH_ROOM`, and `NAV_SEARCH_FLOOR` to the exclusion regex pattern for the `MessageHandler` in the `WAITING_FOR_NAME`, `WAITING_FOR_ROOM`, and `WAITING_FOR_FLOOR` states.
    - **Tests**: `test_search_buttons_excluded_from_processing()` passes
    - **Done**: Navigation button text is no longer processed as a search query in any search mode.
    - **Changelog**: [To be recorded after implementation]

- [ ] Step 3: Test State Transitions
  - [ ] Sub-step 3.1: Write comprehensive state transition tests
    - **Directory**: `tests/unit/test_bot_handlers/`
    - **Files to create/modify**: `test_search_conversation_name.py`
    - **Accept**: All state transitions tested with proper assertions
    - **Tests**: 15+ unit tests covering all scenarios
    - **Done**: Test suite complete with 100% pass rate
    - **Changelog**: [To be recorded after implementation]

  - [ ] Sub-step 3.2: Write integration test for complete flow
    - **Directory**: `tests/integration/test_bot_handlers/`
    - **Files to create/modify**: `test_name_search_flow_integration.py`
    - **Accept**: End-to-end flow works from main menu to results
    - **Tests**: Integration test simulates real user interaction
    - **Done**: Integration test passes
    - **Changelog**: [To be recorded after implementation]

- [ ] Step 4: Verify Consistency with Room/Floor Search
  - [ ] Sub-step 4.1: Ensure all three search modes behave identically
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: None (verification only)
    - **Accept**: Name/Room/Floor all follow button→prompt→input pattern
    - **Tests**: `test_search_mode_consistency()` passes
    - **Done**: All modes verified consistent
    - **Changelog**: [To be recorded after implementation]

- [ ] Step 5: Run Full Test Suite and Quality Checks
  - [ ] Sub-step 5.1: Execute all tests and fix any regressions
    - **Directory**: Project root
    - **Files to create/modify**: Any files needing fixes
    - **Accept**: All existing tests still pass
    - **Tests**: `./venv/bin/pytest tests/ -v` shows 100% pass
    - **Done**: No regressions introduced
    - **Changelog**: [To be recorded after implementation]

  - [ ] Sub-step 5.2: Run linting and type checking
    - **Directory**: Project root
    - **Files to create/modify**: Any files needing fixes
    - **Accept**: No linting or type errors
    - **Tests**: `./venv/bin/flake8 src tests` and `./venv/bin/mypy src --no-error-summary`
    - **Done**: All quality checks pass
    - **Changelog**: [To be recorded after implementation]

### Constraints
- Must not break existing room/floor search functionality
- Must maintain backward compatibility with inline buttons
- Fix must be minimal and focused on the specific issue
- Should follow patterns established in recent room/floor search fixes

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-10
**Decision**: No Split Needed
**Reasoning**: This is a surgical single-line fix with atomic business value and appropriate PR size (~50-100 lines mostly tests). All implementation steps serve the same business objective and cannot be delivered independently. Splitting would add unnecessary overhead without benefits.
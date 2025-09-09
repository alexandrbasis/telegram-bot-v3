# Task: Main Menu Start Command Equivalence
**Created**: 2025-09-09 | **Status**: Ready for Review | **Started**: 2025-09-09 | **Completed**: 2025-09-09

## Tracking & Progress
### Linear Issue
- **ID**: AGB-40
- **URL**: https://linear.app/alexandrbasis/issue/AGB-40/main-menu-start-command-equivalence

### PR Details
- **Branch**: basisalexandr/agb-40-main-menu-start-command-equivalence ✅ Created
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-09

### Business Context
Users experience frustration when the "Main Menu" button becomes unresponsive after periods of bot inactivity, forcing them to manually type /start command to reactivate the bot functionality.

### Primary Objective
Ensure the "Main Menu" button consistently reactivates the bot and provides the same functionality as the /start command, eliminating user friction after periods of inactivity.

### Use Cases
1. **Inactive Bot Recovery**: When a user returns after extended inactivity and presses "Main Menu", the bot should respond immediately with the main interface
   - **Acceptance Criteria**: Main Menu button triggers the same initialization as /start command
   - **Acceptance Criteria**: No need to manually type /start after bot inactivity

2. **Consistent Navigation**: Throughout all bot conversations, the "Main Menu" button should reliably return users to the main interface
   - **Acceptance Criteria**: Main Menu button works from any conversation state
   - **Acceptance Criteria**: Button behavior is identical to /start command functionality

3. **Session Recovery**: Users can restore bot functionality using the Main Menu button regardless of conversation state or timeout
   - **Acceptance Criteria**: Main Menu button works even after conversation timeouts
   - **Acceptance Criteria**: Button provides same initialization as fresh /start

### Success Metrics
- [ ] Zero instances of unresponsive Main Menu button after bot inactivity
- [ ] User reports show improved bot responsiveness and reduced need for manual /start commands
- [ ] All keyboard instances with Main Menu button consistently trigger start command behavior
- [ ] Text-based Main Menu/Search buttons re-enter conversation after timeout without requiring /start
- [ ] Unified welcome message and identical session init from both Main Menu and /start

### Constraints
- Must maintain existing /start command functionality
- Changes should not break existing conversation flows
- Should work across all bot handler states and keyboards

## Test Plan
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-09

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

### Proposed Test Categories

#### Business Logic Tests
- [ ] Main menu button triggers identical functionality as /start command
- [ ] Start command handler is properly invoked when main menu button is pressed
- [ ] Bot state initialization occurs correctly for both /start and main menu button
- [ ] User session is properly reset/initialized for both entry points

#### State Transition Tests
- [ ] Main menu button works from search conversation state
- [ ] Main menu button works from edit participant state  
- [ ] Main menu button works from any active conversation handler state
- [ ] Main menu button works after conversation timeout states
- [ ] Bot transitions to main menu state from any current state when button is pressed

#### Error Handling Tests
- [ ] Main menu button handles conversation handler cleanup properly
- [ ] Main menu button works when bot is in error/invalid state
- [ ] Main menu button handles concurrent state transitions gracefully
- [ ] Fallback behavior when start command handler fails

#### Integration Tests
- [ ] Main menu button integration with ConversationHandler states
- [ ] Main menu button works with timeout handlers
- [ ] Main menu keyboard rendering after main menu button press
- [ ] Integration with existing start command workflow

#### User Interaction Tests
- [ ] Main menu button responds immediately after bot inactivity periods
- [ ] Main menu button provides identical user experience as /start command
- [ ] Main menu button works from all keyboards that contain it
- [ ] End-to-end user journey: inactivity → main menu button → bot reactivation

### Test-to-Requirement Mapping
- **Inactive Bot Recovery** → Tests: Main menu button after inactivity, session initialization, state reset
- **Consistent Navigation** → Tests: Main menu from any conversation state, ConversationHandler integration
- **Session Recovery** → Tests: Timeout handling, error state recovery, concurrent state management

## TECHNICAL TASK 
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-09-09

### Technical Requirements
- [ ] Create shared initialization helper for common state between `start_command` and `main_menu_button`:
  - `initialize_main_menu_session(context)`: sets `user_data["search_results"] = []` and `user_data["force_direct_name_input"] = True`
  - `get_welcome_message()`: unified Russian welcome text used by both entry points
- [ ] Update `start_command` to use shared helpers (no behavior change besides centralizing the message)
- [ ] Update `main_menu_button` to use shared helpers while maintaining callback-query UX (edit previous message + send reply keyboard)
- [ ] Ensure `main_menu_button` provides equivalent functionality to `start_command` without direct delegation (use shared helpers)
- [ ] Maintain proper handling of both event types: `update.message` (start) and `update.callback_query` (main menu button)
- [ ] Add conversation entry points for text buttons to allow re-entry after timeout:
  - `MessageHandler(Regex("^🔍 Поиск участников$"), search_button)` as an entry point
  - `MessageHandler(Regex(rf"^{NAV_MAIN_MENU}$"), start_command)` as an entry point
  - Keep `CallbackQueryHandler(search_button, pattern="^search$")` as an entry point for stale inline buttons
- [ ] Preserve existing ConversationHandler state management and transitions  
- [ ] Preserve all existing keyboard layouts and navigation patterns
- [ ] Ensure proper cleanup of conversation state when main menu button is pressed
- [ ] Maintain compatibility with timeout recovery handlers that rely on main menu functionality
- [ ] Test integration with all conversation states (search, edit, floor search, room search)
- [ ] Handle `force_direct_name_input` flag appropriately in both contexts

### Implementation Steps & Change Log

- [ ] Step 1: Create shared initialization function for both handlers
  - [ ] Sub-step 1.1: Extract common initialization logic into shared function
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_handlers.py` — add `initialize_main_menu_session` and `get_welcome_message`
    - **Accept**: Helpers handle user_data initialization and provide a unified welcome message
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py` — test_initialize_main_menu_session_and_welcome
    - **Done**: Helpers created and tested
    - **Changelog**: [Record new function creation and location]

- [ ] Step 2: Update start_command to use shared initialization
  - [ ] Sub-step 2.1: Refactor start_command to use shared initialization function
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_handlers.py` — function `start_command`
    - **Accept**: start_command uses shared helpers and unified welcome message; preserves existing message vs callback context handling
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py` - test_start_command_uses_shared_initialization
    - **Done**: start_command refactored to use shared initialization function
    - **Changelog**: [Record changes to start_command function]

- [ ] Step 3: Update main_menu_button to use shared initialization  
  - [ ] Sub-step 3.1: Refactor main_menu_button to use shared initialization function
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_handlers.py` — function `main_menu_button`
    - **Accept**: main_menu_button uses shared initialization while maintaining callback query handling
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py` - test_main_menu_button_uses_shared_initialization
    - **Done**: main_menu_button refactored to use shared initialization function
    - **Changelog**: [Record changes to main_menu_button function]

  - [ ] Sub-step 3.2: Ensure main_menu_button provides equivalent welcome message to start_command
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_handlers.py` — use `get_welcome_message()` in main_menu_button
    - **Accept**: main_menu_button shows equivalent welcome message as start_command
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py` - test_main_menu_button_equivalent_welcome_message
    - **Done**: Welcome message updated to match start_command behavior
    - **Changelog**: [Record welcome message changes]

  - [ ] Sub-step 3.3: Add entry points for text buttons to re-enter after timeout
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_conversation.py` — extend `entry_points` to handle:
      - `MessageHandler(Regex("^🔍 Поиск участников$"), search_button)`
      - `MessageHandler(Regex(rf"^{re.escape(NAV_MAIN_MENU)}$"), start_command)`
      - Keep `CallbackQueryHandler(search_button, pattern="^search$")`
    - **Accept**: After ConversationHandler.TIMEOUT (END), pressing Main Menu or Search text buttons reactivates the conversation without typing /start
    - **Tests**: Integration tests simulate timeout then pressing Main Menu/Search to verify re-entry
    - **Done**: Entry points modified and verified by tests
    - **Changelog**: [Record conversation entry point updates]

- [ ] Step 4: Test integration with ConversationHandler states
  - [ ] Sub-step 4.1: Verify main menu button works from all conversation states
    - **Directory**: `tests/integration/test_bot_handlers/`
    - **Files to create/modify**: `test_search_conversation_integration.py`
    - **Accept**: Main menu button successfully transitions to MAIN_MENU state from any conversation state
    - **Tests**: Integration tests for each conversation state (SearchStates, EditStates, RoomSearchStates, FloorSearchStates)
    - **Done**: All integration tests pass verifying state transitions
    - **Changelog**: [Record test file creation and test results]

  - [ ] Sub-step 4.2: Verify timeout recovery integration (including text button re-entry)
    - **Directory**: `tests/integration/test_bot_handlers/`
    - **Files to create/modify**: `test_timeout_recovery_integration.py`
    - **Accept**: Main Menu and Search text buttons re-enter conversation after timeout (no need to type /start)
    - **Tests**: Test Main Menu and Search after timeout in each conversation state; verify equivalent initialization
    - **Done**: Timeout recovery tests pass with main menu button functionality
    - **Changelog**: [Record timeout recovery test implementation]

- [ ] Step 5: Update existing tests to reflect new behavior
  - [ ] Sub-step 5.1: Update unit tests for main_menu_button behavior
    - **Directory**: `tests/unit/test_bot_handlers/`
    - **Files to create/modify**: `test_search_handlers.py` - update existing main_menu_button tests
    - **Accept**: All existing tests pass with updated main_menu_button behavior
    - **Tests**: Update test_main_menu_button, test_main_menu_button_callback_query, test_main_menu_button_clears_context
    - **Done**: Unit tests updated and passing
    - **Changelog**: [Record specific test updates and assertions changed]

  - [ ] Sub-step 5.2: Add new tests for start_command equivalence
    - **Directory**: `tests/unit/test_bot_handlers/`
    - **Files to create/modify**: `test_search_handlers.py` - add equivalence tests
    - **Accept**: Tests verify main_menu_button produces identical results to start_command (same welcome message and user_data keys/values)
    - **Tests**: `test_main_menu_button_equivalent_to_start_command`, `test_main_menu_button_initializes_user_data`, `test_start_and_main_menu_set_force_direct_name_input`
    - **Done**: Equivalence tests implemented and passing
    - **Changelog**: [Record new test implementations]

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-09
**Decision**: No Split Needed
**Reasoning**: Task is appropriately sized for single PR with tightly coupled changes serving single business objective

### Constraints
- Must maintain existing /start command functionality unchanged
- Cannot break existing conversation flows or keyboard layouts
- Must preserve existing user interaction logging behavior
- Should maintain backward compatibility with existing callback query patterns
- Must work across all ConversationHandler states without side effects
 - Do not delegate `main_menu_button` to `start_command` directly (use shared helpers)

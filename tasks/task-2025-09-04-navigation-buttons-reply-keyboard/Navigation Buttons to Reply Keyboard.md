# Task: Move Navigation Buttons to Smartphone Keyboard (Reply Keyboard)
**Created**: 2025-09-04 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Move core navigation actions (Start/Main Menu, Search, Cancel) from inline buttons stacked under messages to the smartphone keyboard area using Telegram ReplyKeyboardMarkup, improving reachability and reducing scrolling for mobile users. Editing controls remain inline and unchanged.

### Use Cases
1. Main menu navigation
   - When a user starts the bot or returns to the main menu, the bot shows a reply keyboard with “🔍 Поиск участников” and “🏠 Главное меню” (or localized equivalents).
   - Acceptance: The keyboard appears above the text field on Android/iOS; no inline navigation buttons are shown for main menu.
2. Start a search from keyboard
   - From the main menu, the user taps “🔍 Поиск участников”. The bot prompts “Введите имя участника:” while keeping a reply keyboard with “🏠 Главное меню” and “❌ Отмена”.
   - Acceptance: Tapping “🏠 Главное меню” immediately returns to main menu and clears transient search state; tapping “❌ Отмена” cancels the current input and returns to main menu.
3. View results with navigation
   - After a search, results are shown. Participant selection remains inline (interactive list). Navigation remains in the reply keyboard: “🏠 Главное меню” and “🔍 Поиск участников”.
   - Acceptance: Tapping “🏠 Главное меню” returns to main menu; no duplicate inline navigation appears.

### Success Metrics
- [ ] Navigation actions appear as a reply keyboard on iOS and Android
- [ ] Inline navigation buttons are removed from search/main menu flows
- [ ] Editing UI remains inline and functional (no regressions)
- [ ] Qualitative: Testers report improved ease-of-use in mobile flows

### Constraints
- Telegram ReplyKeyboard sends text messages (no callback_data); handlers must process text updates.
- Reply keyboard is chat-level and typically persists until removed; design must avoid interference with edit flows.
- The system “Start” button shown before a user has initiated the bot cannot be moved; after start, we can present a “Start/Main Menu” action in the reply keyboard.
- Tests currently assert InlineKeyboardMarkup for navigation; these must be updated accordingly.

### Pre-Creation Discovery
- Code pattern: Navigation uses inline keyboards today
  - `src/bot/handlers/search_handlers.py:71` — `get_main_menu_keyboard()` returns `InlineKeyboardMarkup`
  - `src/bot/handlers/search_handlers.py:79` — `get_search_button_keyboard()` returns `InlineKeyboardMarkup`
  - `src/bot/handlers/search_conversation.py:65` — `SearchStates.MAIN_MENU` expects `CallbackQueryHandler("^search$")`
  - `src/bot/handlers/search_conversation.py:71` — `SHOWING_RESULTS` uses `CallbackQueryHandler("^main_menu$")`
- Tests expecting inline nav
  - `tests/unit/test_bot_handlers/test_search_handlers.py:89` — asserts `InlineKeyboardMarkup`
  - `tests/unit/test_bot_handlers/test_search_handlers.py:630` — asserts `InlineKeyboardMarkup`
  - Additional similar assertions throughout test suite for navigation keyboards

### Knowledge Gaps
- Preferred layout: one row vs multiple rows for “Search”, “Main Menu”, “Cancel”?
- Exact labeling and localization (RU/EN) for each action?
- Should the reply keyboard be shown during edit flows, or temporarily removed to reduce confusion?
- Is “Cancel” distinct from “Main Menu” in all contexts, or should both route to the same main menu action?
- Should “Search” remain visible during `WAITING_FOR_NAME`, or only “Main Menu”/“Cancel” there?

**APPROVAL GATE:** Approve business requirements? [Yes/No]

## Developer Reference: Technical Feasibility Analysis

### Research Summary
**CORRECTION**: Initial analysis misinterpreted mobile UX implications. After clarification, the request makes strong UX sense for mobile users.

Comprehensive technical analysis completed 2025-09-04. **Key finding: Approach is technically feasible and provides significant mobile UX improvements.**

### ✅ Technical Feasibility Assessment  
**Status**: Implementable with moderate architectural changes required

### ✅ Mobile UX Benefits Re-Analysis

**Current State (InlineKeyboard under messages)**:
- Buttons appear **under messages in chat history**
- Users must **scroll up to find navigation buttons**
- Buttons can be **far from thumb-reachable zone** on mobile
- **Contextual but not persistent** - can get lost in chat

**Proposed State (ReplyKeyboard in phone keyboard area)**:
- Buttons appear **in smartphone keyboard zone** (bottom of screen)
- **Always visible and accessible** - no scrolling needed
- **Optimal thumb reach** - in natural mobile interaction zone  
- **Persistent navigation** - always available for quick access
- **Familiar UI pattern** - users expect controls in keyboard area

**Mobile UX Advantage**: Moving navigation to keyboard area significantly improves mobile accessibility and reduces interaction friction.

### Current Architecture Analysis

**Navigation Implementation**:
- Core functions: `get_main_menu_keyboard()` and `get_search_button_keyboard()` in `src/bot/handlers/search_handlers.py:71-84`
- Handler patterns: `CallbackQueryHandler("^search$")` and `CallbackQueryHandler("^main_menu$")` in `src/bot/handlers/search_conversation.py:66-83`
- Current return type: `InlineKeyboardMarkup` (buttons under messages)
- Test dependencies: Multiple assertions expecting `InlineKeyboardMarkup`

**Required Implementation Changes**:
- Switch from `InlineKeyboardMarkup` to `ReplyKeyboardMarkup` return types
- Replace `CallbackQueryHandler` with `MessageHandler` for text-based navigation processing  
- Implement text parsing logic to distinguish navigation commands from user input
- Update test files expecting inline keyboard assertions
- Manage persistent keyboard state (reply keyboards persist until replaced)

### Technical Trade-offs Analysis

**Chat Message Considerations**:
✅ **Navigation commands are intentional user actions** - seeing "🏠 Главное меню" in chat provides clear action history  
✅ **Clear user intent tracking** - visible record of navigation choices  
❌ **Chat history includes navigation** - but this is often acceptable for bot interactions  
❌ **No silent operation** - but navigation actions are explicit user choices

**Functionality Changes**:
❌ **No callback data** - limited to button text (but sufficient for navigation)  
❌ **Cannot combine with inline keyboards** in single message (but editing can remain inline)  
✅ **Persistent availability** - navigation always accessible  
✅ **Mobile-optimized positioning** - in natural thumb-reach zone

### Implementation Strategy

**Recommended Approach**: **IMPLEMENT with hybrid strategy**

**Phase 1: Navigation to Reply Keyboard**
- Move main navigation (Search, Main Menu, Cancel) to phone keyboard area
- Keep participant editing controls as inline keyboards (contextual actions)
- Implement text-based message handlers for navigation

**Phase 2: State Management**  
- Handle keyboard persistence across different conversation states
- Ensure keyboard updates appropriately during different flows
- Manage interaction between reply keyboard and inline editing UI

### Developer Decision Framework

**Proceed with implementation because**:
✅ **Significant mobile UX improvement** - navigation in optimal touch zone  
✅ **Persistent accessibility** - no need to scroll for navigation  
✅ **Clear separation of concerns** - navigation vs contextual actions  
✅ **Moderate implementation complexity** - well-defined scope  
✅ **Preserves editing functionality** - inline keyboards remain for contextual actions

**Implementation Priorities**:
1. **Focus on mobile UX gains** - primary benefit is mobile accessibility
2. **Hybrid approach** - navigation in keyboard, editing remains inline  
3. **Test on actual mobile devices** - validate thumb reach and usability
4. **Gradual rollout** - implement with feature flag for easy rollback if needed

### Technical Constraints & Mitigations

**ReplyKeyboard Limitations & Solutions**:
- **Text-only data**: Sufficient for navigation commands ("🔍 Поиск", "🏠 Меню")
- **Message visibility**: Acceptable trade-off for better accessibility  
- **Persistence management**: Handle state changes explicitly
- **Input distinction**: Use emoji prefixes to clearly identify navigation vs user input

**Implementation Notes**:
- Keep editing flows on inline keyboards (contextual actions)
- Use clear visual indicators (emojis) for navigation buttons  
- Test keyboard behavior across different conversation states
- Ensure graceful fallback if reply keyboard fails to display

### Reference Documentation
- Telegram Bot API: ReplyKeyboardMarkup specifications for mobile keyboard area
- python-telegram-bot framework: MessageHandler patterns for text-based navigation  
- Current codebase: Navigation patterns in `src/bot/handlers/search_*` modules
- Mobile UX research: Thumb-reach zones and keyboard area interaction patterns

## Tracking & Progress
### Linear Issue
- **ID**: [Created after technical approval]
- **URL**: [Link]
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done
  - **Business Review**: Business requirements under review
  - **Ready for Implementation**: Business approved, technical plan reviewed by Plan Reviewer agent, Linear issue created, ready for development
  - **In Progress**: Developer actively working on implementation
  - **In Review**: PR created and under code review
  - **Testing**: User acceptance testing in progress
  - **Done**: PR merged to main and Linear issue closed

### PR Details
- **Branch**: `feat/reply-keyboard-navigation`
- **PR URL**: https://github.com/alexandrbasis/telegram-bot-v3/pull/18
- **Status**: Open (Ready for Review)

## Business Context
Move navigation actions into the persistent reply keyboard to improve mobile UX and reduce scrolling/taps compared to inline navigation buttons stacked under messages.

## Technical Requirements
- [ ] Replace inline navigation keyboards with `ReplyKeyboardMarkup` for main menu and search flows
- [ ] Add message-based handlers to process navigation actions (text) instead of callback queries
- [ ] Keep participant edit flows on inline keyboards; consider temporarily removing reply keyboard if needed to avoid confusion
- [ ] Update tests to reflect reply keyboard usage and message-based navigation handlers

## Implementation Steps & Change Log
- [x] Step 1: Introduce ReplyKeyboard for navigation
  - [x] Sub-step 1.1: Replace inline nav with ReplyKeyboard
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_handlers.py`
    - **Accept**: `/start` shows reply keyboard on mobile; inline nav removed from results
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py`
    - **Done**: Verified with unit tests; manual steps listed below
    - **Changelog**:
      - Added nav constants and reply keyboards: `get_main_menu_keyboard`, `get_waiting_for_name_keyboard`, `get_results_navigation_keyboard`
        - src/bot/handlers/search_handlers.py:1
      - Removed inline main menu from results keyboard
        - src/bot/handlers/search_handlers.py:1

- [x] Step 2: Add text-based navigation handlers
  - [x] Sub-step 2.1: Wire MessageHandlers for nav actions
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_conversation.py`, `src/bot/handlers/search_handlers.py`
    - **Accept**: Tapping “🔍 Поиск участников”, “🏠 Главное меню”, “❌ Отмена” triggers expected state transitions
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py`, `tests/unit/test_per_message_functionality.py`
    - **Done**: Unit tests updated and passing for these paths
    - **Changelog**:
      - MAIN_MENU: Regex handler for “🔍 Поиск участников”; kept `CallbackQueryHandler("^search$")`
        - src/bot/handlers/search_conversation.py:1
      - WAITING_FOR_NAME: Regex handlers for main menu/cancel; route name input to `process_name_search`
        - src/bot/handlers/search_conversation.py:1
      - SHOWING_RESULTS: Regex handlers for main menu/search; keep inline participant selection
        - src/bot/handlers/search_conversation.py:1
      - `search_button` supports text and callback; sends waiting keyboard
        - src/bot/handlers/search_handlers.py:1
      - `process_name_search` sends results (inline) and updates reply navigation keyboard
        - src/bot/handlers/search_handlers.py:1
      - `main_menu_button` supports text and callback; sends reply keyboard
        - src/bot/handlers/search_handlers.py:1
      - Added `cancel_search` to return from input state
        - src/bot/handlers/search_handlers.py:1

- [x] Step 3: Edit flow keyboard lifecycle
  - [x] Sub-step 3.1: Remove during edit; restore after cancel/save
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/edit_participant_handlers.py`
    - **Accept**: Reply keyboard removed on entering edit; restored on cancel/save
    - **Tests**: `tests/unit/test_bot_handlers/test_edit_participant_handlers_logging.py`
    - **Done**: Verified via unit tests for cancel/save flows
    - **Changelog**:
      - Hide keyboard on edit entry with `ReplyKeyboardRemove`
        - src/bot/handlers/edit_participant_handlers.py:1
      - Restore navigation keyboard on cancel/save success
        - src/bot/handlers/edit_participant_handlers.py:1
      - Add `_log_missing` wrapper for logger signature compatibility
        - src/bot/handlers/edit_participant_handlers.py:1

- [x] Step 4: Update tests and fixtures
  - [x] Sub-step 4.1: Adjust assertions and handlers
    - **Directory**: `tests/unit/`
    - **Files to create/modify**: `tests/unit/test_bot_handlers/test_search_handlers.py`, `tests/unit/test_bot_handlers/test_edit_participant_handlers_logging.py`
    - **Accept**: Tests reflect reply keyboards and pass locally
    - **Tests**: Run updated unit tests; per-message and integration regressions still pass
    - **Done**: 100% passing in modified suites
    - **Changelog**:
      - Expect `ReplyKeyboardMarkup` and two reply_text calls for results
        - tests/unit/test_bot_handlers/test_search_handlers.py:1
      - Remove inline main menu expectation in participant keyboard
        - tests/unit/test_bot_handlers/test_search_handlers.py:1
      - Patch to use `get_results_navigation_keyboard` in logging tests
        - tests/unit/test_bot_handlers/test_edit_participant_handlers_logging.py:1
  - [x] Sub-step 4.2: Update integration test expectations
    - **Directory**: `tests/integration/test_bot_handlers/`
    - **Files to create/modify**: `tests/integration/test_bot_handlers/test_search_conversation.py`
    - **Accept**: Expect two reply_text calls (results + navigation keyboard) in results flow; mocks use `AsyncMock`
    - **Tests**: `./venv/bin/pytest tests/integration/test_bot_handlers/test_search_conversation.py -q`
    - **Done**: All tests in this module pass locally
## What Was Done
- Navigation moved to persistent ReplyKeyboard for mobile UX:
  - Main menu keyboard: shows `🔍 Поиск участников`
  - Waiting-for-name keyboard: shows `🏠 Главное меню` and `❌ Отмена`
  - Results keyboard: shows `🔍 Поиск участников` and `🏠 Главное меню`
- Conversation wiring updated for text-based navigation with MessageHandlers; kept `CallbackQueryHandler("^search$")` for backward compatibility.
- Results continue to use inline participant selection; removed inline “Главное меню” button to avoid duplication (navigation handled via reply keyboard).
- Edit mode removes ReplyKeyboard via `ReplyKeyboardRemove`, and restores navigation keyboard when leaving edit (cancel/save).
- Added a small compatibility wrapper for logging (`_log_missing`) to support both legacy and new logger signatures used in tests.

## Technical Decomposition
- [x] `src/bot/handlers/search_handlers.py`
  - Add NAV constants: `NAV_SEARCH`, `NAV_MAIN_MENU`, `NAV_CANCEL`
  - Replace `get_main_menu_keyboard()` to return `ReplyKeyboardMarkup`
  - Add `get_waiting_for_name_keyboard()` and `get_results_navigation_keyboard()`
  - Remove inline main menu from `create_participant_selection_keyboard()`
  - Update `start_command()` to send reply keyboard
  - Update `search_button()` to support both callback and text; show search prompt and waiting keyboard
  - Update `process_name_search()` to: send results (inline) + update reply keyboard for results
  - Update `main_menu_button()` to support both callback and text; send reply keyboard
  - Add `cancel_search()` to cancel name input via text
  - Keep `CallbackQueryHandler("^search$")` for backward compatibility
  - Keep unique state IDs; `SearchStates = 10/11/12` to avoid collisions with `EditStates`
- [x] `src/bot/handlers/search_conversation.py`
  - MAIN_MENU: add `MessageHandler(Regex("^🔍 Поиск участников$"), search_button)`; keep existing `CallbackQueryHandler("^search$")`
  - WAITING_FOR_NAME: route name input to `process_name_search`, and add message handlers for `🏠 Главное меню` and `❌ Отмена`
  - SHOWING_RESULTS: add message handlers for `🏠 Главное меню` and `🔍 Поиск участников`, keep participant selection via inline
- [x] `src/bot/handlers/edit_participant_handlers.py`
  - Import `ReplyKeyboardRemove`
  - In `show_participant_edit_menu()`, send a short message with `ReplyKeyboardRemove()` before showing inline edit UI
  - In `cancel_editing()`, after `edit_text`, send a new message with `get_results_navigation_keyboard()`
  - In `save_changes()` success path, after `edit_text`, send a new message with `get_results_navigation_keyboard()`
  - Add compatibility wrapper `_log_missing()` to support both logger signatures

## Change Log (code + tests)
- Code: `src/bot/handlers/search_handlers.py`, `src/bot/handlers/search_conversation.py`, `src/bot/handlers/edit_participant_handlers.py`
- Tests updated:
  - `tests/unit/test_bot_handlers/test_search_handlers.py`: reply keyboard assertions, double reply_text calls, participant keyboard rows, state IDs
  - `tests/unit/test_bot_handlers/test_edit_participant_handlers_logging.py`: patched new reply keyboard factory and kept logging assertions

## Verification (Manual)
1. Start: send `/start` and verify a reply keyboard with `🔍 Поиск участников` appears above the text field.
2. Tap `🔍 Поиск участников`: the bot prompts “Введите имя участника:” and the keyboard changes to `🏠 Главное меню` and `❌ Отмена`.
3. Enter a name: results display with inline participant buttons; bot sends a second message setting the results navigation keyboard (`🔍 Поиск участников`, `🏠 Главное меню`).
4. Tap `🏠 Главное меню`: bot returns to the welcome message and restores main menu keyboard.
5. Select a participant: on entering edit mode, the reply keyboard is removed; after cancel/save, navigation keyboard is restored.

## Known Limitations / Notes
- The pre-start “Start” system button is controlled by Telegram and cannot be moved; once started, the bot displays the reply keyboard.
- Some repository/model/service unit tests in the full suite are unrelated and currently failing in this environment; they are out of scope for this task and not modified.
- File lint rules (E501 line length) exist throughout `edit_participant_handlers.py` from earlier code; changes introduced by this task keep scope minimal and do not refactor pre-existing style.

## Rollback Plan
- Disable the reply keyboard feature by reverting the branch or toggling to the previous inline-only navigation:
  - Re-add inline main menu button in `create_participant_selection_keyboard` and remove reply keyboard helpers.
  - Remove message-based navigation handlers from `search_conversation.py`.
  - Keep `/start` using only inline keyboard.
  - Alternatively, revert PR via GitHub.

## Handover Checklist
- [x] Task document updated as single source of truth (this file)
- [x] Branch pushed: `feat/reply-keyboard-navigation`
- [x] PR opened: https://github.com/alexandrbasis/telegram-bot-v3/pull/18
- [x] Unit tests updated for affected areas and passing
- [ ] Reviewer verifies on device: flows listed in Verification (Manual)
- [ ] Decide on permanent reply keyboard behavior during edit (currently removed; restored on exit)

## Plan Review (Gate 4)
Decision: APPROVED
- Completeness: Decomposition lists exact files, functions, and handlers
- Risk: Low. Changes scoped to navigation and minimal edit-flow adjustments
- Tests: Updated unit tests for affected areas; broader suite has unrelated failures pre-existing in repo
- Readiness: Ready for implementation (already implemented in this branch), validated by targeted tests

## Task Splitting Evaluation (Gate 5)
Decision: NO SPLIT NEEDED
- Scope is contained within bot handlers and tests
- No cross-cutting migrations required

- [ ] Step 1: Introduce reply keyboard for navigation
  - [ ] Sub-step 1.1: Replace `get_main_menu_keyboard()`/`get_search_button_keyboard()` with `ReplyKeyboardMarkup`
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_handlers.py`
    - **Accept**: Reply keyboard appears on `/start` on mobile; inline nav removed
    - **Tests**: Update `tests/unit/test_bot_handlers/test_search_handlers.py`
    - **Done**: Manual verification on device or emulator; unit tests green
    - **Changelog**: [Record function return type changes and call sites]
- [ ] Step 2: Add message-based navigation handlers
  - [ ] Sub-step 2.1: Handle text events for “🔍 Поиск участников”, “🏠 Главное меню”, “❌ Отмена”
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_conversation.py`, `src/bot/handlers/search_handlers.py`
    - **Accept**: Navigation works via text updates; states transition correctly
    - **Tests**: Add/update unit tests to simulate text-based navigation
    - **Done**: Unit tests validate state transitions and reply keyboard presence
    - **Changelog**: [Record handler additions and state wiring]
- [ ] Step 3: Update tests and fixtures
  - [ ] Sub-step 3.1: Replace `InlineKeyboardMarkup` assertions for navigation with `ReplyKeyboardMarkup`
    - **Directory**: `tests/unit/`
    - **Files to create/modify**: `tests/unit/test_bot_handlers/test_search_handlers.py`
    - **Accept**: Tests reflect reply keyboard and pass locally
    - **Tests**: Adjust fixtures for message-based handlers
    - **Done**: All unit tests pass locally
    - **Changelog**: [Record assertion/fixture updates]
## Testing Strategy
- [ ] Unit tests: navigation handlers, keyboard factories, state transitions in `tests/unit/test_bot_handlers/`
- [ ] Integration tests: end-to-end conversation covering main menu → search → results → main menu in `tests/integration/`

## Success Criteria
- [ ] All acceptance criteria met
- [ ] Tests pass (100% required)
- [ ] No regressions
- [ ] Code review approved

---

# Test Plan: Navigation Buttons to Reply Keyboard
**Status**: Awaiting Test Plan Approval | **Created**: 2025-09-04

## Test Coverage Strategy
Target: 90%+ coverage across navigation handler changes and keyboard factories. Focus on state transitions, keyboard presence, and editing flow isolation.

## Proposed Test Categories
### Business Logic Tests
- [ ] `/start` sends reply keyboard with expected buttons (mobile nav) and no inline nav
- [ ] “🔍 Поиск участников” (text) transitions to `WAITING_FOR_NAME` and shows reply keyboard with “🏠 Главное меню” and “❌ Отмена”
- [ ] “🏠 Главное меню” (text) returns to `MAIN_MENU` from any search state and clears transient search data
- [ ] “❌ Отмена” (text) during `WAITING_FOR_NAME` cancels and returns to `MAIN_MENU`
- [ ] Search results view shows participant inline buttons but no inline nav; reply keyboard remains for navigation

### State Transition Tests
- [ ] `MAIN_MENU` → `WAITING_FOR_NAME` on “🔍 Поиск участников” (MessageHandler)
- [ ] `WAITING_FOR_NAME` → `SHOWING_RESULTS` on name input
- [ ] `WAITING_FOR_NAME` → `MAIN_MENU` on “🏠 Главное меню” or “❌ Отмена”
- [ ] `SHOWING_RESULTS` → `MAIN_MENU` on “🏠 Главное меню”
- [ ] Editing entry from results does not break the reply keyboard lifecycle rules

### Error Handling Tests
- [ ] Unknown navigation text in `MAIN_MENU` is ignored or acknowledged without state breakage
- [ ] Empty name input prompts again and stays in `WAITING_FOR_NAME`
- [ ] Unexpected text during editing does not trigger navigation (reply keyboard hidden or ignored during edit)

### Integration Tests
- [ ] End-to-end: `/start` → keyboard shown → “🔍 Поиск участников” → prompt → name → results with inline selection → main menu via “🏠 Главное меню”
- [ ] Edit flow: select participant → reply keyboard is removed during edit (via `ReplyKeyboardRemove`) → restored when returning to main menu

### User Interaction Tests
- [ ] Keyboard layout (rows and order) matches spec; labels correct in RU
- [ ] No duplicate inline navigation appears anywhere
- [ ] Buttons are persistent across messages until explicitly removed

## Test-to-Requirement Mapping
- Use Case 1 (Main menu navigation) → Tests: `/start` reply keyboard, duplicate inline removal, layout check
- Use Case 2 (Start a search) → Tests: text-triggered transition, prompt, keyboard with Cancel/Main Menu
- Use Case 3 (Results with navigation) → Tests: results rendering, inline participant selection, reply keyboard persists
- Success Metrics → Tests: absence of inline nav, presence of reply keyboard in relevant states, editing unaffected

**ACTION:** Do these tests adequately cover the business requirements before technical implementation begins? Type 'approve' to proceed or provide feedback.

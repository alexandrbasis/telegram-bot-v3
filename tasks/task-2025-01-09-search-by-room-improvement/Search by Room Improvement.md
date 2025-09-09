# Task: Search by Room Improvement
**Created**: 2025-01-09 | **Status**: Implementation Complete

## Tracking & Progress
### Linear Issue
- **ID**: TDB-53
- **URL**: https://linear.app/alexandrbasis/issue/TDB-53/search-by-room-improvement-structured-russian-results-and-conversation
- **Note**: Issue created with full business context, implementation summary, and testing details

### PR Details
- **Branch**: basisalexandr/tdb-53-search-by-room-improvement-structured-russian-results-and
- **PR URL**: https://github.com/alexandrbasis/telegram-bot-v3/pull/30
- **Status**: Ready for Review

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-09

### Business Context
Improve search by room functionality to match the user experience and business logic of search by floor feature.

### Primary Objective
Make room search more user-friendly by implementing proper conversation flow with Russian language support and structured result display.

### Use Cases
1. **Room Search Initiation**
   - User clicks "Search by room" button
   - Bot sends message in Russian asking for room number
   - Bot waits for user input (no immediate errors)
   - **Acceptance Criteria**: Bot properly enters waiting state without throwing errors

2. **Room Search Results Display**
   - User enters room number
   - Bot displays structured results in Russian
   - Shows participant role and department (without church info)
   - Includes floor information for context
   - **Acceptance Criteria**: All information displayed in Russian using existing field mappings

3. **Error Handling**
   - User enters invalid room number
   - Bot provides clear error message in Russian
   - Allows retry without restarting conversation
   - **Acceptance Criteria**: Graceful error handling with user-friendly messages

### Success Metrics
- [x] Zero errors when clicking "Search by room" button
- [x] 100% of room search results displayed in Russian
- [x] Consistent user experience with floor search functionality
- [x] Clear structured display of room occupants

### Constraints
- Must use existing Russian field mapping library
- Must maintain compatibility with current database structure
- Should follow existing conversation handler patterns

---

## Test Plan
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-09

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas including conversation flow, error handling, and Russian language display

### Proposed Test Categories

#### Business Logic Tests
- [ ] **test_room_search_conversation_flow** - Verify bot enters waiting state after room search initiation
- [ ] **test_room_number_validation** - Validate room number input processing and validation logic
- [ ] **test_participant_filtering_by_room** - Ensure correct filtering of participants by room number
- [ ] **test_result_formatting_structure** - Verify structured display format for room occupants

#### State Transition Tests  
- [ ] **test_room_search_state_transitions** - Test conversation flow from button click to awaiting input
- [ ] **test_input_state_to_results_state** - Verify transition from input to results display
- [ ] **test_error_state_recovery** - Test return to input state after invalid room number
- [ ] **test_conversation_cancellation** - Verify proper cleanup when user cancels search

#### Error Handling Tests
- [ ] **test_invalid_room_number_handling** - Test response to non-existent room numbers
- [ ] **test_empty_room_handling** - Verify behavior when room has no occupants
- [ ] **test_malformed_input_handling** - Test handling of special characters and invalid formats
- [ ] **test_timeout_handling** - Verify conversation timeout behavior

#### Integration Tests
- [ ] **test_airtable_room_query** - Test actual database queries for room data
- [ ] **test_russian_field_mapping_integration** - Verify Russian translation mappings work correctly
- [ ] **test_full_room_search_flow** - End-to-end test from button click to results display
- [ ] **test_keyboard_interaction_flow** - Test inline keyboard callbacks and navigation

#### User Interaction Tests
- [ ] **test_room_search_button_callback** - Verify button click triggers correct handler
- [ ] **test_russian_message_display** - Ensure all messages display in Russian
- [ ] **test_result_message_formatting** - Verify role, department, and floor info display correctly
- [ ] **test_back_to_menu_navigation** - Test return to main search menu after results

### Test-to-Requirement Mapping
- **Business Requirement 1 (Room Search Initiation)** → Tests: test_room_search_conversation_flow, test_room_search_state_transitions, test_room_search_button_callback
- **Business Requirement 2 (Results Display)** → Tests: test_result_formatting_structure, test_russian_message_display, test_russian_field_mapping_integration, test_result_message_formatting
- **Business Requirement 3 (Error Handling)** → Tests: test_invalid_room_number_handling, test_empty_room_handling, test_malformed_input_handling, test_error_state_recovery

---

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-01-09

### Technical Requirements
- [ ] Fix room search conversation flow to properly wait for user input (root cause fix)
- [ ] Implement Russian-language prompts for room search interaction
- [ ] Create structured result formatting similar to floor search
- [ ] Add Russian translations for role and department values
- [ ] Ensure proper error handling with Russian messages
- [ ] Maintain consistency with existing conversation handler patterns and service layer

### Implementation Steps & Change Log

- [x] Step 1: Fix Root Cause - Room Search Button Handler State Transition
  - [x] Sub-step 1.1: Fix handle_search_room_mode to follow floor search pattern
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_handlers.py` (lines 629-651)
    - **Accept**: Handler sends Russian prompt and returns RoomSearchStates.WAITING_FOR_ROOM
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py`
    - **Done**: Bot properly waits for room input without errors
    - **Changelog**: No code change required; existing handler already delegates to `handle_room_search_command`, which prompts in Russian and returns `RoomSearchStates.WAITING_FOR_ROOM`. Verified by tests (`tests/unit/test_bot_handlers/test_search_handlers.py::test_handle_search_room_mode`) and integration coverage.
    - **Implementation**: Validation-only change. Confirmed the delegation path meets acceptance criteria; added and updated tests to cover behavior.
  
  - [x] Sub-step 1.2: Verify proper keyboard and messages are displayed
    - **Directory**: `src/bot/`
    - **Files to create/modify**: `messages.py` - verify InfoMessages.ENTER_ROOM_NUMBER is in Russian
    - **Accept**: Russian prompt message exists and keyboard shows proper navigation
    - **Tests**: `tests/unit/test_bot_messages/test_info_messages.py`
    - **Done**: User sees Russian prompt with correct keyboard options
    - **Changelog**: Added test `tests/unit/test_bot_messages/test_info_messages.py:1-6` to verify Russian prompt text

- [x] Step 2: Implement Structured Russian Result Formatting
  - [x] Sub-step 2.1: Create format_room_results_russian function similar to floor formatting
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `room_search_handlers.py` (add new function)
    - **Accept**: Function formats results with Russian labels, role, department, floor
    - **Tests**: `tests/unit/test_bot_handlers/test_room_search_handlers.py`
    - **Done**: Results show structured format: name, role, department, floor (no church)
    - **Changelog**: Added `format_room_results_russian()` at `src/bot/handlers/room_search_handlers.py:180-220` and unit tests at `tests/unit/test_bot_handlers/test_room_search_handlers.py:1-47`
    - **Implementation**: Create function similar to format_floor_results but for single room
  
  - [x] Sub-step 2.2: Add Russian translation mappings for departments
    - **Directory**: `src/utils/`
    - **Files to create/modify**: Create `translations.py` with DEPARTMENT_RUSSIAN dict
    - **Accept**: All 13 departments have Russian translations
    - **Tests**: `tests/unit/test_utils/test_translations.py`
    - **Done**: Mapping exists for all Department enum values
    - **Changelog**: Added `src/utils/translations.py:1-55`; added tests `tests/unit/test_utils/test_translations.py:1-43`
    - **Departments to translate**: ROE, Chapel, Setup, Palanka, Administration, Kitchen, Decoration, Bell, Refreshment, Worship, Media, Clergy, Rectorate

- [x] Step 3: Integrate New Formatting with Room Search
  - [x] Sub-step 3.1: Update process_room_search_with_number to use new formatter
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `room_search_handlers.py` (lines 99-178)
    - **Accept**: Replace search_by_room_formatted call with format_room_results_russian
    - **Tests**: `tests/integration/test_bot_handlers/test_room_search_flow.py`
    - **Done**: Room search displays structured Russian results
    - **Changelog**: Replaced `search_by_room_formatted` call with `format_room_results_russian()` and consolidated message construction at `src/bot/handlers/room_search_handlers.py:129-171`; updated integration tests `tests/integration/test_room_search_integration.py:1-320`
  
  - [x] Sub-step 3.2: Update service layer to support formatting needs
    - **Directory**: `src/services/`
    - **Files to create/modify**: Keep `search_service.py` methods, ensure they return needed data
    - **Accept**: Service layer provides all data needed for Russian formatting
    - **Tests**: `tests/unit/test_services/test_search_service.py`
    - **Done**: Service returns participants with all required fields
    - **Changelog**: N/A (no changes required)

- [x] Step 4: Enhance Error Handling and Edge Cases
  - [x] Sub-step 4.1: Add proper error messages in Russian
    - **Directory**: `src/bot/`
    - **Files to create/modify**: `messages.py`
    - **Accept**: All room search errors have Russian messages
    - **Tests**: `tests/unit/test_bot_messages/test_error_messages.py`
    - **Done**: Error messages are user-friendly and in Russian
    - **Changelog**: Added `tests/unit/test_bot_messages/test_error_messages.py:1-9` to verify `ErrorMessages.no_participants_in_room()`
  
  - [x] Sub-step 4.2: Handle empty room results gracefully
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `room_search_handlers.py`
    - **Accept**: Empty rooms show appropriate Russian message
    - **Tests**: `tests/unit/test_bot_handlers/test_room_search_handlers.py`
    - **Done**: Users see clear message when room is empty
    - **Changelog**: `format_room_results_russian()` returns empty-room message when no participants (`src/bot/handlers/room_search_handlers.py:186-188`)

-- [x] Step 5: Integration Testing and Validation
  - [x] Sub-step 5.1: Create comprehensive integration tests
    - **Directory**: `tests/integration/test_bot_handlers/`
    - **Files to create/modify**: `test_room_search_integration.py`
    - **Accept**: Full conversation flow tested end-to-end
    - **Tests**: End-to-end conversation flow tests
    - **Done**: All test scenarios pass
    - **Changelog**: Updated `tests/integration/test_room_search_integration.py` to validate Russian role/department/floor; performance and alphanumeric room tests retained
  
  - [x] Sub-step 5.2: Run linting and type checking
    - **Directory**: Project root
    - **Files to create/modify**: None
    - **Accept**: No flake8 or mypy errors
    - **Tests**: Run `./venv/bin/flake8 src tests` and `./venv/bin/mypy src`
    - **Done**: All quality checks pass
    - **Changelog**: flake8 and mypy run successful on 2025-09-09

### Constraints
- Must maintain backward compatibility with existing conversation handler
- Should reuse existing Russian translation patterns where possible
- Must follow existing code conventions and testing patterns

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-01-09
**Decision**: No Split Needed
**Reasoning**: Task is appropriately sized for a single PR (~100-150 lines), addresses one cohesive feature, and all changes are tightly integrated. The core fix is only 3 lines with additional formatting enhancements that form a complete user story.

---

## Implementation Summary
- Added `format_room_results_russian()` to format room results with Russian labels (role, department, floor) and RU/EN names.
- Updated `process_room_search_with_number()` to produce a single structured results message and removed reliance on `search_by_room_formatted()` for UI.
- Introduced `src/utils/translations.py` with complete department translations and role translation helper to ensure consistent Russian UI.
- Verified prompts and errors are Russian and user-friendly; empty-room case handled gracefully.
- Extended test suite: unit tests for formatter/translations/messages; updated integration tests to validate Russian roles/departments/floor in responses.
- Quality checks: flake8 and mypy clean; full test suite passing (720 tests).

## Notes
- Current issue: Bot throws error immediately after sending room request message
- Need to implement proper conversation state management
- Leverage existing Russian translation mappings from floor search
- Consider creating shared translation utilities for consistency

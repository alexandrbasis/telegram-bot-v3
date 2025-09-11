# Task: Interactive Floor Search UI Components
**Created**: 2025-01-20 | **Status**: Ready for Review (2025-01-21 08:26)

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Create interactive UI components for floor discovery, including inline keyboards, messages, and callback handlers for enhanced user experience.

### Use Cases
1. **Interactive Floor Discovery Button**: User sees discovery button in chat area to reveal available floors
   - **Acceptance Criteria**: Inline keyboard button displays "Показать доступные этажи" with proper callback data
2. **Enhanced User Guidance Messages**: Clear instructions show both discovery button and manual input options
   - **Acceptance Criteria**: Messages include both button interaction and "Send floor number" instructions in Russian
3. **Floor Selection Interface**: Users can click on discovered floors to trigger search
   - **Acceptance Criteria**: Available floors display as clickable buttons with format "Этаж 1", "Этаж 2", etc.

### Success Metrics
- [ ] Users can discover floors through interactive button without guessing numbers
- [ ] Clear guidance reduces confusion about available input methods
- [ ] Floor selection buttons provide intuitive floor search experience
- [ ] All UI text maintains Russian language consistency

### Constraints
- Floor discovery button must appear as inline keyboard in chat area (not reply keyboard)
- All UI text and messages must be in Russian with proper formatting
- Must integrate with existing conversation flow without breaking current functionality
- UI components must handle empty results and error states gracefully

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-55
- **URL**: https://linear.app/alexandrbasis/issue/TDB-55/subtask-2-interactive-floor-search-ui-components
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: feature/TDB-55-interactive-floor-ui
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
Users can discover available floors through an interactive button interface, eliminating guesswork while maintaining manual input flexibility.

## Technical Requirements
- [ ] Create inline keyboard functions for floor discovery button
- [ ] Add floor discovery messages to InfoMessages class in Russian
- [ ] Implement callback handlers for floor discovery and floor selection
- [ ] Update floor input prompt to include inline keyboard
- [ ] Ensure all UI components handle error states and empty results
 - [ ] Acknowledge callback queries and use strict callback patterns
 - [ ] Prefer editing the discovery message to show floors list with buttons

## Implementation Steps & Change Log
- [x] ✅ Step 1: Create inline keyboard for floor discovery - Completed 2025-01-21 08:12
  - [x] Sub-step 1.1: Add floor discovery inline keyboard functions
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `search_keyboards.py`
    - **Accept**: Inline keyboard with "Показать доступные этажи" button, callback data `floor_discovery` (pattern `^floor_discovery$`)
    - **Tests**: Add test cases to existing `tests/unit/test_bot_keyboards/test_search_keyboards.py`
    - **Done**: Keyboard renders properly with callback data, integrated with waiting_for_floor message
    - **Callback Patterns**: `floor_discovery` for discovery button, `floor_select_{number}` for individual floor selection (pattern `^floor_select_(\d+)$`)
    - **Changelog**: 
      - `src/bot/keyboards/search_keyboards.py:85-139` - Added get_floor_discovery_keyboard() and get_floor_selection_keyboard() functions
      - `tests/unit/test_bot_keyboards/test_search_keyboards.py:137-231` - Added TestFloorDiscoveryKeyboard and TestFloorSelectionKeyboard test classes

- [x] ✅ Step 2: Update floor search messages - Completed 2025-01-21 08:15
  - [x] Sub-step 2.1: Add floor discovery messages to InfoMessages class
    - **Directory**: `src/bot/`
    - **Files to create/modify**: `messages.py`
    - **Accept**: Russian messages following InfoMessages pattern: `ENTER_FLOOR_WITH_DISCOVERY`, optional display header for available floors
    - **Tests**: Add test cases to existing message tests
    - **Done**: All required Russian messages added with consistent formatting and emoji usage
    - **Message Patterns**: `ENTER_FLOOR_WITH_DISCOVERY = "Выберите этаж из списка или пришлите номер этажа цифрой:"`
    - **Changelog**: 
      - `src/bot/messages.py:96-103` - Added floor discovery messages (ENTER_FLOOR_WITH_DISCOVERY, AVAILABLE_FLOORS_HEADER, NO_FLOORS_AVAILABLE, FLOOR_DISCOVERY_ERROR)
      - `tests/unit/test_bot_messages/test_info_messages.py:20-41` - Added tests for new floor discovery messages

- [x] ✅ Step 3: Create floor discovery callback handlers - Completed 2025-01-21 08:20
  - [x] Sub-step 3.1: Create handle_floor_discovery_callback function
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `floor_search_handlers.py`
    - **Accept**: Processes `floor_discovery` callback, acknowledges callback, displays available floors with selection buttons (3 per row), edits original message if present
    - **Tests**: Add test cases to existing `tests/unit/test_bot_handlers/test_floor_search_handlers.py`
    - **Done**: Callback handles floor discovery, formats results, shows selection options
    - **Error Handling**: API failures show "Произошла ошибка. Пришлите номер этажа цифрой.", empty floors show helpful message
    - **Changelog**: 
      - `src/bot/handlers/floor_search_handlers.py:228-293` - Added handle_floor_discovery_callback() function

  - [x] Sub-step 3.2: Create handle_floor_selection_callback function
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `floor_search_handlers.py`
    - **Accept**: Processes `floor_select_{number}` callback, parses number via regex `^floor_select_(\d+)$`, triggers floor search with selected number
    - **Tests**: Add test cases to existing `tests/unit/test_bot_handlers/test_floor_search_handlers.py`
    - **Done**: Floor selection triggers existing process_floor_search_with_input function
    - **Callback Pattern**: Extracts floor number from "floor_select_{number}" pattern
    - **Changelog**: 
      - `src/bot/handlers/floor_search_handlers.py:295-342` - Added handle_floor_selection_callback() function
      - `tests/unit/test_bot_handlers/test_floor_search_handlers.py:365-566` - Added test classes for callback handlers

- [x] ✅ Step 4: Update floor input prompt with enhanced UI - Completed 2025-01-21 08:24
  - [x] Sub-step 4.1: Update floor input prompt with inline keyboard
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `floor_search_handlers.py`
    - **Accept**: `handle_floor_search_command` uses enhanced message with inline discovery keyboard from Step 1.1 (`ENTER_FLOOR_WITH_DISCOVERY`)
    - **Tests**: Update existing `tests/unit/test_bot_handlers/test_floor_search_handlers.py`
    - **Done**: Message combines inline keyboard with text instructions, maintains backward compatibility
    - **Changelog**: 
      - `src/bot/handlers/floor_search_handlers.py:130-142` - Updated floor input prompt to use enhanced UI with discovery button
      - `tests/unit/test_bot_handlers/test_floor_search_handlers.py:134-149` - Updated test to verify two-message approach

## Testing Strategy
- [x] Unit tests: Keyboard generation and callback data validation in `tests/unit/test_bot_keyboards/`
- [x] Unit tests: Message formatting and Russian text validation
- [x] Unit tests: Callback handler logic and error scenarios in `tests/unit/test_bot_handlers/`
- [x] UI component tests: Empty results handling and error state displays
- [x] Integration tests: Callback workflow from discovery to floor selection
 - [x] Ensure tests acknowledge callback queries (`answer()` called) and handle edited messages

## Success Criteria
- [x] All acceptance criteria met for interactive UI components
- [x] Unit tests pass with coverage on new keyboard and handler code
- [x] Russian language consistency maintained across all UI elements
- [x] Error states handled gracefully with user-friendly messages
- [x] Callback handlers integrate properly with existing conversation flow

## Implementation Notes (Concrete Guidance)

- Keyboard builders:
  - Discovery: single inline button `"Показать доступные этажи"` → callback `floor_discovery`.
  - Floors list: build inline keyboard with rows of up to 3 buttons, text `"Этаж {n}"`, callback `floor_select_{n}`.

- Messages:
  - Use `InfoMessages.ENTER_FLOOR_WITH_DISCOVERY` in the prompt shown when waiting for floor.
  - When no floors available, send: `"В данный момент участники не размещены ни на одном этаже. Пришлите номер этажа цифрой."`.

- Handlers:
  - `handle_floor_discovery_callback`: `await query.answer()`, get floors from `SearchService.get_available_floors()`, render keyboard; if `update.callback_query.message` is present, prefer `edit_text` to swap button/message in place.
  - `handle_floor_selection_callback`: parse floor from data via regex; call `process_floor_search_with_input(update, context, str(floor))` for reuse.

- Error Handling:
  - On repo/service error or timeout, show manual input fallback: `"Произошла ошибка. Пришлите номер этажа цифрой."`.

## Implementation Summary

### Completed Components
1. **Inline Keyboards** (`src/bot/keyboards/search_keyboards.py`)
   - `get_floor_discovery_keyboard()`: Single button for floor discovery
   - `get_floor_selection_keyboard()`: Dynamic buttons for available floors (3 per row)

2. **Russian Messages** (`src/bot/messages.py`)
   - Added 4 new messages to InfoMessages class
   - All messages maintain Russian language consistency

3. **Callback Handlers** (`src/bot/handlers/floor_search_handlers.py`)
   - `handle_floor_discovery_callback()`: Fetches and displays available floors
   - `handle_floor_selection_callback()`: Processes floor selection
   - Both handlers acknowledge callbacks and edit messages in place

4. **Enhanced UI Integration**
   - Updated `handle_floor_search_command()` to use discovery UI
   - Maintains backward compatibility with manual input

5. **Callback Handler Registration** (`src/bot/handlers/search_conversation.py`)
   - Registered `floor_discovery` callback handler in WAITING_FOR_FLOOR state
   - Registered `floor_select_{number}` callback handler with regex pattern
   - Added integration test to verify handlers are properly wired

### Test Coverage
- 8 new keyboard tests (discovery and selection)
- 4 new message tests (Russian text validation)
- 5 new callback handler tests (including error scenarios)
- 1 updated integration test for enhanced UI flow
- 1 new callback registration test (critical integration verification)
- **Total: 19 new/updated tests, all passing**

### Key Features Delivered
- ✅ Interactive floor discovery without guessing
- ✅ Clear dual-input guidance (button + manual)
- ✅ Intuitive floor selection with numbered buttons
- ✅ Graceful error handling with fallback options
- ✅ Full Russian language consistency
- ✅ Seamless integration with existing conversation flow

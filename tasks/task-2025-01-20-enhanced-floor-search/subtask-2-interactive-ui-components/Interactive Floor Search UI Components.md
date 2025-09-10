# Task: Interactive Floor Search UI Components
**Created**: 2025-01-20 | **Status**: Business Review

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
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Create inline keyboard functions for floor discovery button
- [ ] Add floor discovery messages to InfoMessages class in Russian
- [ ] Implement callback handlers for floor discovery and floor selection
- [ ] Update floor input prompt to include inline keyboard
- [ ] Ensure all UI components handle error states and empty results

## Implementation Steps & Change Log
- [ ] Step 1: Create inline keyboard for floor discovery
  - [ ] Sub-step 1.1: Add floor discovery inline keyboard functions
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `search_keyboards.py`
    - **Accept**: Inline keyboard with "Показать доступные этажи" button, callback data "floor_discovery"
    - **Tests**: Add test cases to existing `tests/unit/test_bot_keyboards/test_search_keyboards.py`
    - **Done**: Keyboard renders properly with callback data, integrated with waiting_for_floor message
    - **Callback Patterns**: "floor_discovery" for discovery button, "floor_select_{number}" for individual floor selection
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Update floor search messages
  - [ ] Sub-step 2.1: Add floor discovery messages to InfoMessages class
    - **Directory**: `src/bot/`
    - **Files to create/modify**: `messages.py`
    - **Accept**: Russian messages following InfoMessages pattern: ENTER_FLOOR_WITH_DISCOVERY, AVAILABLE_FLOORS_DISPLAY
    - **Tests**: Add test cases to existing message tests
    - **Done**: All required Russian messages added with consistent formatting and emoji usage
    - **Message Patterns**: ENTER_FLOOR_WITH_DISCOVERY = "Выберите этаж из списка или пришлите номер этажа цифрой:"
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Create floor discovery callback handlers
  - [ ] Sub-step 3.1: Create handle_floor_discovery_callback function
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `floor_search_handlers.py`
    - **Accept**: Processes "floor_discovery" callback, displays available floors with selection buttons
    - **Tests**: Add test cases to existing `tests/unit/test_bot_handlers/test_floor_search_handlers.py`
    - **Done**: Callback handles floor discovery, formats results, shows selection options
    - **Error Handling**: API failures show "Произошла ошибка. Пришлите номер этажа цифрой.", empty floors show helpful message
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 3.2: Create handle_floor_selection_callback function
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `floor_search_handlers.py`
    - **Accept**: Processes "floor_select_{number}" callback, triggers floor search with selected number
    - **Tests**: Add test cases to existing `tests/unit/test_bot_handlers/test_floor_search_handlers.py`
    - **Done**: Floor selection triggers existing process_floor_search_with_input function
    - **Callback Pattern**: Extracts floor number from "floor_select_{number}" pattern
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Update floor input prompt with enhanced UI
  - [ ] Sub-step 4.1: Update floor input prompt with inline keyboard
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `floor_search_handlers.py`
    - **Accept**: handle_floor_search_command uses enhanced message with inline keyboard from Step 1.1
    - **Tests**: Update existing `tests/unit/test_bot_handlers/test_floor_search_handlers.py`
    - **Done**: Message combines inline keyboard with text instructions, maintains backward compatibility
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Keyboard generation and callback data validation in `tests/unit/test_bot_keyboards/`
- [ ] Unit tests: Message formatting and Russian text validation
- [ ] Unit tests: Callback handler logic and error scenarios in `tests/unit/test_bot_handlers/`
- [ ] UI component tests: Empty results handling and error state displays
- [ ] Integration tests: Callback workflow from discovery to floor selection

## Success Criteria
- [ ] All acceptance criteria met for interactive UI components
- [ ] Unit tests pass with coverage on new keyboard and handler code
- [ ] Russian language consistency maintained across all UI elements
- [ ] Error states handled gracefully with user-friendly messages
- [ ] Callback handlers integrate properly with existing conversation flow
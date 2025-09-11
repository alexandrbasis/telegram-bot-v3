# Task: Enhanced Floor Search with Interactive Options  
**Created**: 2025-01-20 | **Status**: Ready for Implementation

## Tracking & Progress
### Linear Issues
- **Main Issue**: [AGB-43](https://linear.app/alexandrbasis/issue/AGB-43/enhanced-floor-search-with-interactive-options) - Enhanced Floor Search with Interactive Options
- **Subtask 1**: [TDB-54](https://linear.app/alexandrbasis/issue/TDB-54/subtask-1-floor-discovery-backend-implementation) - Floor Discovery Backend Implementation
- **Subtask 2**: [TDB-55](https://linear.app/alexandrbasis/issue/TDB-55/subtask-2-interactive-floor-search-ui-components) - Interactive Floor Search UI Components  
- **Subtask 3**: [TDB-56](https://linear.app/alexandrbasis/issue/TDB-56/subtask-3-conversation-flow-integration-and-testing) - Conversation Flow Integration and Testing

### Implementation Status
- **Status**: Task Split Completed - Ready for Development
- **Split Decision**: Task split into 3 manageable subtasks for optimal development and review process
- **Dependencies**: TDB-54 → TDB-55 → TDB-56 (sequential implementation recommended)

## Business Requirements (Gate 1 - Approval Required)
**Status**: Awaiting Business Approval | **Created**: 2025-01-20

### Business Context
Improve user experience in floor-based participant searches by providing both automated floor discovery and traditional manual input options.

### Primary Objective
Enhance the floor search functionality to show users all available floors with participants while maintaining the ability to manually input floor numbers.

### Use Cases
1. **Interactive Floor Discovery**: User selects floor search and clicks a discovery button to see all available floors with participants
   - **Acceptance Criteria**: Button displays in chat area (not keyboard), shows only floors with participants, formatted as clickable options

2. **Traditional Floor Input**: User can still manually type a floor number for direct search
   - **Acceptance Criteria**: System continues to accept and process numeric floor input as before

3. **Enhanced User Guidance**: Clear instructions guide users on available input methods
   - **Acceptance Criteria**: Message includes both options: "Choose a floor" button and "Send floor number" instruction

### Success Metrics
- [ ] Users can discover available floors without guessing numbers
- [ ] Reduced invalid floor searches (searching floors with no participants)
- [ ] Maintained backward compatibility with numeric input
- [ ] Improved user engagement with floor search functionality

### Constraints
- Must maintain existing numeric floor input functionality
- Button must appear in chat area, not as keyboard markup
- Only show floors that contain participants (non-empty floors)
- Russian language interface consistency

**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-20

## Test Plan (Gate 2 - Approval Required)
**Status**: Awaiting Test Plan Approval | **Created**: 2025-01-20

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas including business logic, state transitions, error handling, integration, and user interactions.

### Proposed Test Categories

#### Business Logic Tests
- [ ] **Floor discovery with participants test**: Verify system correctly identifies and returns only floors that contain participants
- [ ] **Empty floor filtering test**: Ensure floors with no participants are excluded from discovery results
- [ ] **Floor number validation test**: Validate numeric floor input processing maintains existing functionality
- [ ] **Available floors formatting test**: Test proper formatting of discovered floors for user display

#### State Transition Tests  
- [ ] **Floor search mode activation test**: Verify transition from main menu to floor search mode
- [ ] **Discovery button interaction test**: Test state change when user clicks floor discovery option
- [ ] **Manual input processing test**: Verify state handling when user sends numeric floor input
- [ ] **Search results to main menu transition test**: Test return flow after floor search completion

#### Error Handling Tests
- [ ] **Invalid floor number handling test**: Test response to non-existent or invalid floor numbers
- [ ] **Empty discovery results test**: Handle scenario when no floors contain participants
- [ ] **Airtable API failure during floor discovery test**: Test graceful error handling for API failures
- [ ] **Malformed floor input test**: Validate handling of non-numeric floor input

#### Integration Tests
- [ ] **Airtable floor data retrieval test**: Test integration with Airtable to fetch floor information
- [ ] **Participant count per floor calculation test**: Verify accurate counting of participants by floor
- [ ] **Floor search repository integration test**: Test repository layer floor filtering functionality
- [ ] **Cache integration for floor discovery test**: Verify caching behavior for repeated floor queries

#### User Interaction Tests
- [ ] **Floor discovery button rendering test**: Verify button appears in chat area with correct text
- [ ] **Dual input method guidance test**: Test message shows both discovery button and manual input instructions
- [ ] **Floor selection from discovery results test**: Test user can select from discovered floors
- [ ] **Russian language consistency test**: Verify all floor search messages maintain Russian language interface
- [ ] **Response formatting for floor options test**: Test proper formatting of available floors display

### Test-to-Requirement Mapping
- **Interactive Floor Discovery** → Tests: Floor discovery with participants, Available floors formatting, Floor discovery button rendering, Floor selection from discovery results
- **Traditional Floor Input** → Tests: Floor number validation, Manual input processing, Invalid floor number handling, Malformed floor input  
- **Enhanced User Guidance** → Tests: Dual input method guidance, Russian language consistency, Response formatting for floor options

**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-20

## TECHNICAL TASK
**Status**: Plan Review Required | **Created**: 2025-01-20

### Technical Requirements
- [ ] Add repository method to discover all floors with participants
- [ ] Create inline keyboard functionality for floor discovery button
- [ ] Enhance floor search message to include both button and manual input options
- [ ] Implement floor selection handling for inline button responses
- [ ] Maintain backward compatibility with existing numeric floor input processing
- [ ] Ensure Russian language consistency across all new messages
- [ ] Add strict callback patterns and acknowledge callback queries
- [ ] Add 5-minute in-memory caching for discovery results (module/class-level)
- [ ] Apply 10s timeout around discovery to fail fast and fallback to manual input

### Implementation Steps & Change Log

- [ ] Step 1: Backend Floor Discovery Implementation → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-1-floor-discovery-backend/Floor Discovery Backend Implementation.md`
  - **Description**: Implement repository and service layer floor discovery with caching and error handling
  - **Linear Issue**: TDB-54 - https://linear.app/alexandrbasis/issue/TDB-54/subtask-1-floor-discovery-backend-implementation
  - **Dependencies**: None - can be implemented independently

- [ ] Step 2: Interactive UI Components → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-2-interactive-ui-components/Interactive Floor Search UI Components.md`
  - **Description**: Create inline keyboards, messages, and callback handlers for floor discovery interface
  - **Linear Issue**: TDB-55 - https://linear.app/alexandrbasis/issue/TDB-55/subtask-2-interactive-floor-search-ui-components
  - **Dependencies**: Requires Subtask 1 (backend floor discovery) for callback handler implementation

- [ ] Step 3: Conversation Integration and Testing → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-3-conversation-integration/Conversation Flow Integration and Testing.md`
  - **Description**: Register callback handlers in conversation flow and implement comprehensive integration testing
  - **Linear Issue**: TDB-56 - https://linear.app/alexandrbasis/issue/TDB-56/subtask-3-conversation-flow-integration-and-testing
  - **Dependencies**: Requires Subtask 2 (UI components) for callback handler registration and testing

### Constraints
- Must maintain existing numeric floor input functionality unchanged
- Floor discovery button must appear as inline keyboard in chat area  
- Only show floors that contain participants (non-empty floors)
- All messages and interface elements must be in Russian
- Error handling must gracefully fall back to manual input on API failures
- Cache floor discovery results for 5 minutes using simple in-memory dict with timestamp cleanup
- Acknowledge callback queries (answer) and prefer editing the original discovery message when listing floors
- Prefer retrieving only the `Floor` field from Airtable for discovery to minimize payload

### Error Handling Strategy
- **API Failures**: Return empty list, log warning, show manual input fallback message
- **Timeout Scenarios**: 10-second timeout on floor discovery (wrap discovery in `asyncio.wait_for`), fallback to manual input
- **Empty Results**: Show helpful message "В данный момент участники не размещены ни на одном этаже. Пришлите номер этажа цифрой."
- **Callback Errors**: Invalid callback data gracefully ignored with log entry

### Callback Data Specification
- **Floor Discovery Button**: `"floor_discovery"` (pattern: `^floor_discovery$`)
- **Floor Selection Buttons**: `"floor_select_1"`, `"floor_select_2"`, etc. (pattern: `^floor_select_(\d+)$`)
- **Button Text Format**: Floor numbers displayed as "Этаж 1", "Этаж 2", etc.

### Design Decisions
- **Floor type**: Treat floors as integers (per Airtable schema `Floor` is numeric). Reject non-numeric in selection callback; manual input keeps existing numeric validation.
- **Sorting**: Sort floors ascending numerically; deduplicate.
- **Caching placement**: Implement cache at repository module/class level (singleton-style) keyed by `(base_id, table_identifier)` to persist across service/repo factory calls.
- **UI/UX**: Acknowledge callback queries (`CallbackQuery.answer()`), layout floor buttons in rows of 3; prefer editing the discovery message to show available floors with selection keyboard.
- **Minimal retrieval**: Fetch only the `Floor` field when discovering floors.

### Message Updates
- Add `InfoMessages.ENTER_FLOOR_WITH_DISCOVERY = "Выберите этаж из списка или пришлите номер этажа цифрой:"`.
- When listing floors: prepend header like `"Доступные этажи:"` and render buttons; also keep guidance for manual input.

### Test Notes
- Update tests that assert the simple `ENTER_FLOOR_NUMBER` prompt to account for the enhanced prompt when discovery is enabled.
- Add tests for discovery callback, selection callback, timeout fallback, and callback acknowledgement.

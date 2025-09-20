# Task: Conversation UI Integration
**Created**: 2025-01-19 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Convert the existing `/export` command into an interactive conversation flow with a selection menu that provides 6 export options, enabling administrators to choose specific data exports rather than downloading everything.

### Use Cases
1. **Interactive Export Selection**: Admin uses `/export` command and sees menu with 6 clear options
   - **Acceptance Criteria**: Command shows selection menu with options: Export All, Export Team, Export Candidates, Export by Department, Export Bible Readers, Export ROE
2. **Department Selection Workflow**: Admin selects "Export by Department" and sees list of all 13 departments
   - **Acceptance Criteria**: Secondary menu shows all departments (ROE, Chapel, Setup, Palanka, Administration, Kitchen, Decoration, Bell, Refreshment, Worship, Media, Clergy, Rectorate)
3. **Export Processing Feedback**: Admin sees progress updates during export generation
   - **Acceptance Criteria**: User receives progress messages and completion notifications with file statistics
4. **Cancel and Error Handling**: Admin can cancel export process or recover from errors
   - **Acceptance Criteria**: Cancel option returns to main menu, errors show helpful messages with retry options

### Success Metrics
- [ ] Conversion from direct export to interactive selection improves user experience
- [ ] Clear progress feedback reduces user uncertainty during processing
- [ ] Admin can easily access all export types through intuitive menu navigation

### Constraints
- Must maintain admin-only access control throughout workflow
- Conversation flow must integrate with existing bot architecture
- Must preserve backwards compatibility for admin users
- UI must support Russian language for user-facing elements

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-69
- **URL**: https://linear.app/alexandrbasis/issue/TDB-69/subtask-4-conversation-ui-integration
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Ensure conversation flow reuses export progress tracking and interaction logging utilities
- [ ] Create conversation states for export selection workflow
- [ ] Build interactive keyboards for export options and department selection
- [ ] Implement conversation handlers with state management
- [ ] Update main export handler to use conversation flow
- [ ] Integrate with all export services through service factory
- [ ] Register conversation handlers in main application

## Implementation Steps & Change Log
- [ ] Step 1: Create conversation infrastructure
  - [ ] Sub-step 1.1: Define conversation states and callback data structure
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/export_states.py`
    - **Accept**: Enum-based states (SELECTING_EXPORT_TYPE, SELECTING_DEPARTMENT, PROCESSING_EXPORT) and callback data patterns
    - **Tests**: `tests/unit/test_bot_handlers/test_export_states.py`
    - **Done**: State definitions provide clear conversation flow management
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Create export selection keyboards
  - [ ] Sub-step 2.1: Build main export selection keyboard
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/export_keyboards.py`
    - **Accept**: Keyboard displays 6 export options with proper Russian labels and callback data
    - **Tests**: `tests/unit/test_bot_keyboards/test_export_keyboards.py`
    - **Done**: Main selection keyboard renders correctly with state-based callbacks
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 2.2: Build department selection keyboard
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/export_keyboards.py`
    - **Accept**: Keyboard displays all 13 departments with proper navigation and cancel options
    - **Tests**: `tests/unit/test_bot_keyboards/test_export_keyboards.py`
    - **Done**: Department selection keyboard provides complete department list
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Implement conversation handlers
  - [ ] Sub-step 3.1: Create export selection conversation handler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/export_conversation_handlers.py`
    - **Accept**: ConversationHandler with states, entry points, and callback processing for all export types
    - **Tests**: `tests/unit/test_bot_handlers/test_export_conversation_handlers.py`
    - **Done**: Conversation flow tests pass with proper state transitions and admin validation
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 3.2: Implement export processing handlers
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/export_conversation_handlers.py`
    - **Accept**: Handlers process each export type using appropriate service from factory
    - **Tests**: `tests/unit/test_bot_handlers/test_export_conversation_handlers.py`
    - **Done**: All export types properly integrated with service factory
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 3.3: Integrate progress updates and logging
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/export_conversation_handlers.py`, `src/bot/handlers/export_handlers.py`
    - **Accept**: Conversation invokes `ExportProgressTracker` and `UserInteractionLogger` consistently across all export paths
    - **Tests**: `tests/unit/test_bot_handlers/test_export_conversation_handlers.py` (update)
    - **Done**: Progress throttling and interaction logging verified in conversation tests
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Update main export handler integration
  - [ ] Sub-step 4.1: Modify main export handler to start conversation
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/export_handlers.py`
    - **Accept**: Modified handler shows selection menu instead of immediate export, integrates with conversation handler
    - **Tests**: `tests/unit/test_bot_handlers/test_export_handlers.py`
    - **Done**: Handler integration tests pass with new conversation flow
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 5: Register conversation handlers in application
  - [ ] Sub-step 5.1: Update main application handler registration
    - **Directory**: `src/main.py`
    - **Files to create/modify**: `src/main.py`
    - **Accept**: New export conversation handlers registered in application with proper priority and fallbacks
    - **Tests**: `tests/integration/test_main.py`
    - **Done**: Application starts with export selection functionality enabled
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 6: Integration testing
  - [ ] Sub-step 6.1: Create end-to-end workflow tests
    - **Directory**: `tests/integration/`
    - **Files to create/modify**: `tests/integration/test_export_selection_workflow.py`
    - **Accept**: End-to-end tests cover all export types, department selection, and error scenarios
    - **Tests**: Integration test suite with full conversation flow coverage
    - **Done**: All integration tests pass with realistic user interaction scenarios
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Conversation states and handlers in tests/unit/test_bot_handlers/
- [ ] Unit tests: Keyboard components in tests/unit/test_bot_keyboards/
- [ ] Integration tests: Complete workflow testing in tests/integration/

## Success Criteria
- [ ] Conversation flow reuses telemetry (progress + logging) without regressions
- [ ] Export command shows interactive selection menu instead of immediate export
- [ ] All 6 export options work correctly with proper service integration
- [ ] Department selection provides access to all 13 departments
- [ ] Conversation flow handles errors and cancellation gracefully
- [ ] All tests pass (100% required)
- [ ] Code review approved
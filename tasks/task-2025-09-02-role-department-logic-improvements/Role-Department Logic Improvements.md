# Task: Role-Department Logic Improvements
**Created**: 2025-09-02 | **Status**: In Progress

Implementation Branch: feature/task-2025-09-02-role-department-logic-improvements

Started: 2025-09-02

## Business Requirements (Gate 1 - Approval Required)

### Primary Objective
Implement automatic department management logic when participant roles are changed during editing to ensure data consistency and improve user experience by eliminating invalid role-department combinations.

### Use Cases
1. **Auto-cleanup on Role Downgrade During Editing Process**: When a user changes a participant's role from "team member" to "candidate" during the interactive editing workflow, the system should automatically clear the department field because candidates cannot have department assignments.
   - **Acceptance Criteria**: Department field is automatically set to null/empty when role changes from team member to candidate during editing
   - **User Feedback**: System shows confirmation that department was cleared due to role change within the editing interface
   - **Context**: This occurs within the existing participant editing conversation flow

2. **Prompt for Department on Role Upgrade During Editing Process**: When a user changes a participant's role from "candidate" to "team member" during the interactive editing workflow, the system should prompt the user to select a department since team members require department assignments.
   - **Acceptance Criteria**: Department selection interface appears immediately after role change from candidate to team member during editing
   - **User Feedback**: Clear indication that department selection is required for team members within the editing flow
   - **Validation**: Cannot proceed with editing workflow without selecting a valid department
   - **Context**: This integrates with the existing editing conversation state management

### Success Metrics
- [ ] Zero invalid role-department combinations in the database after implementation
- [ ] Improved user experience with guided department selection workflow
- [ ] Reduced data entry errors related to role-department mismatches

### Constraints
- Must maintain backward compatibility with existing participant data
- Changes should integrate seamlessly with current editing workflow
- Should not disrupt existing save/cancel functionality
- Must work within Telegram bot interface limitations

**APPROVAL GATE:** ✅ **APPROVED** - Ready for Test Plan

## Test Plan (Gate 2 - Approval Required)

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

### Proposed Test Categories

#### Business Logic Tests
- [ ] **Role Change Auto-cleanup Test**: Verify department field is automatically cleared when role changes from team member to candidate during editing
  - Test data: Participant with role="team member" and department="Operations"
  - Action: Change role to "candidate" during editing flow
  - Expected: Department field becomes null/empty, confirmation message shown
  
- [ ] **Role Change Department Prompt Test**: Verify department selection prompt appears when role changes from candidate to team member during editing  
  - Test data: Participant with role="candidate" and department=null
  - Action: Change role to "team member" during editing flow
  - Expected: Department selection interface appears, cannot proceed without selection

- [ ] **Department Validation Test**: Verify only valid departments can be selected for team members
  - Test data: Available departments list from configuration
  - Action: Attempt to select valid and invalid departments
  - Expected: Only valid departments accepted, appropriate error messages for invalid selections

#### State Transition Tests
- [ ] **Editing Flow State Management Test**: Verify conversation state is properly maintained through role-department logic changes
  - Test transitions: editing → role change → department prompt → selection → save confirmation
  - Expected: All state transitions work correctly, user can navigate back/cancel at any point

- [ ] **Save/Cancel Workflow Integration Test**: Verify role-department changes integrate with existing save/cancel workflow
  - Test scenarios: Save changes with auto-cleanup, cancel after department prompt, retry after failed save
  - Expected: All workflows maintain data consistency and user experience

#### Error Handling Tests
- [ ] **Department API Failure Test**: Handle failures when fetching available departments for selection
  - Simulate: Airtable API failure during department list retrieval
  - Expected: Graceful error handling, option to retry or continue without department change

- [ ] **Invalid Role Transition Test**: Handle edge cases in role transitions
  - Test data: Participants with invalid initial states, corrupted role data
  - Expected: System handles gracefully, provides clear error messages

- [ ] **Concurrent Edit Prevention Test**: Prevent data corruption from simultaneous edits
  - Simulate: Multiple edit sessions on same participant
  - Expected: Appropriate locking or conflict resolution

#### Integration Tests
- [ ] **Airtable Department Field Update Test**: Verify department field updates are properly saved to Airtable
  - Test both auto-cleanup (null) and user-selected department values
  - Expected: Airtable records reflect correct department values after save

- [ ] **Field Mapping Integration Test**: Verify role and department field mappings work correctly
  - Test with actual Airtable field IDs from field_mappings.py
  - Expected: Correct fields updated in Airtable with proper data types

#### User Interaction Tests
- [ ] **Role Selection Interface Test**: Verify role change interface in editing workflow
  - Test UI elements: role selection buttons, confirmation dialogs, progress indicators
  - Expected: Intuitive interface, clear feedback, proper navigation

- [ ] **Department Selection Interface Test**: Verify department selection interface appears and functions correctly
  - Test UI elements: department list, selection buttons, required field indicators
  - Expected: All departments displayed, selection works, validation messages clear

- [ ] **Confirmation Message Test**: Verify appropriate feedback messages are shown
  - Test messages for: auto-cleanup confirmation, department selection requirement, validation errors
  - Expected: Messages are clear, informative, and contextually appropriate

### Test-to-Requirement Mapping
- **Business Requirement 1** (Auto-cleanup on Role Downgrade) → Tests: Role Change Auto-cleanup Test, Airtable Department Field Update Test, Confirmation Message Test
- **Business Requirement 2** (Prompt for Department on Role Upgrade) → Tests: Role Change Department Prompt Test, Department Validation Test, Department Selection Interface Test, Save/Cancel Workflow Integration Test

**APPROVAL GATE:** ✅ **APPROVED** - Ready for Technical Implementation

## Tracking & Progress
### Linear Issue
- **ID**: AGB-24
- **URL**: https://linear.app/alexandrbasis/issue/AGB-24/role-department-logic-improvements
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done
  - **Business Review**: Business requirements under review
  - **Ready for Implementation**: Business approved, technical plan reviewed by Plan Reviewer agent, Linear issue created, ready for development
  - **In Progress**: Developer actively working on implementation
  - **In Review**: PR created and under code review
  - **Testing**: User acceptance testing in progress
  - **Done**: PR merged to main and Linear issue closed

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
Implement role-based department logic to automatically manage department field consistency during participant editing, preventing invalid role-department combinations and guiding users through required selections.

## Technical Requirements
- [ ] Implement role change detection logic in button field selection handlers
- [ ] Add automatic department clearing when role changes from TEAM to CANDIDATE
- [ ] Add department selection prompt when role changes from CANDIDATE to TEAM
- [ ] Integrate role-department logic with existing editing workflow state management
- [ ] Maintain backward compatibility with current save/cancel functionality
- [ ] Add appropriate user feedback messages for automatic actions
- [ ] Ensure validation prevents proceeding without department selection for team members

## Implementation Steps & Change Log
- [x] ✅ Step 1: Enhance ParticipantUpdateService with role-department logic
  - [x] Sub-step 1.1: Add role change detection method
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_update_service.py`
    - **Accept**: Method detects role changes and returns appropriate actions
    - **Tests**: `tests/unit/test_services/test_participant_update_service.py`
    - **Done**: Role change detection working with TEAM→CANDIDATE and CANDIDATE→TEAM scenarios
    - **Changelog**:
      - `src/services/participant_update_service.py` - added `detect_role_transition`, `requires_department`, `get_role_department_actions`, `build_auto_action_message`
      - `tests/unit/test_services/test_participant_update_service.py` - added `TestRoleDepartmentLogic`

  - [x] Sub-step 1.2: Add automatic department management methods
    - **Directory**: `src/services/`  
    - **Files to create/modify**: `src/services/participant_update_service.py`
    - **Accept**: Methods handle auto-cleanup and prompt requirements based on role change
    - **Tests**: `tests/unit/test_services/test_participant_update_service.py`
    - **Done**: Auto-cleanup and prompt logic implemented and tested
    - **Changelog**:
      - `src/services/participant_update_service.py` - implemented actions and messages
      - `tests/unit/test_services/test_participant_update_service.py` - tests for actions/messages

- [x] ✅ Step 2: Integrate logic into edit participant handlers
  - [x] Sub-step 2.1: Modify role button selection handler with role-department logic
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/edit_participant_handlers.py`
    - **Accept**: Role changes trigger appropriate department actions during editing
    - **Tests**: `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - **Done**: Role selection integrated with department logic
    - **Changelog**:
      - `src/bot/handlers/edit_participant_handlers.py` - role selection now clears department on downgrade and prompts selection on upgrade with user messages
      - `tests/unit/test_bot_handlers/test_edit_participant_handlers.py` - tests for role-change flows added

  - [x] Sub-step 2.2: Add department selection workflow integration
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/edit_participant_handlers.py`
    - **Accept**: Department selection appears after role upgrade, blocks save until selected
    - **Tests**: `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - **Done**: Department selection workflow working seamlessly
    - **Changelog**:
      - `src/bot/handlers/edit_participant_handlers.py` - immediate prompt after CANDIDATE→TEAM, save guard for TEAM without department
      - `tests/unit/test_bot_handlers/test_edit_participant_handlers.py` - test for save enforcement

- [ ] Step 3: Update keyboard and UI components
  - [ ] Sub-step 3.1: Enhance edit keyboards for conditional department prompts
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/edit_keyboards.py`
    - **Accept**: Keyboards adapt to role changes, show department selection when needed
    - **Tests**: `tests/unit/test_bot_keyboards/test_edit_keyboards.py`
    - **Done**: Dynamic keyboard behavior implemented
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 3.2: Add user feedback messages for automatic actions
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/edit_participant_handlers.py`
    - **Accept**: Clear messages inform user of auto-cleanup and prompt requirements
    - **Tests**: `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - **Done**: User feedback messages working correctly
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Service logic tests in `tests/unit/test_services/test_participant_update_service.py`
- [ ] Integration tests: Handler workflow tests in `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
- [ ] End-to-end tests: Complete editing workflow in `tests/integration/test_participant_editing_workflow.py`

## Success Criteria
- [ ] Role change from TEAM to CANDIDATE automatically clears department field
- [ ] Role change from CANDIDATE to TEAM prompts for department selection
- [ ] Cannot save team member without department assignment
- [ ] All existing editing workflow functionality remains intact  
- [ ] Users receive clear feedback about automatic actions
- [ ] Tests pass (100% required)
- [ ] No regressions in existing participant editing features

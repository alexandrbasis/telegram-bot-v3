# Task: Handler Integration and Complete User Workflow
**Created**: 2025-01-19 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Complete the department filtering feature by integrating UI components with data services and implementing the full user workflow from team selection to filtered list display.

### Use Cases
1. **Department selection workflow**: Users navigate from team selection to department filtering to filtered results
   - **Acceptance Criteria**:
     - User selects "Team members" and sees department selection keyboard
     - Department selection leads to filtered participant list
     - Navigation preserves filter context through pagination
     - Back navigation returns to department selection, not role selection
     - Clear visual indication of active filter in list header

2. **Complete filtering experience**: All filter options work correctly with proper list display
   - **Acceptance Criteria**:
     - "All participants" shows complete team member list with chief-first sorting
     - Individual department filters show only relevant members
     - "No department" shows only unassigned participants
     - Department chiefs marked with crown emoji in all lists
     - List headers show current filter and member counts
     - Pagination works correctly with filtered results

3. **Error handling and edge cases**: System handles exceptional scenarios gracefully
   - **Acceptance Criteria**:
     - Empty departments show appropriate "no members" message
     - Invalid department callbacks handled without crashes
     - Airtable API failures show user-friendly error messages
     - Navigation state preserved during error recovery
     - Timeout handling maintains conversation context

### Success Metrics
- [ ] Complete user workflow from selection to filtered results works smoothly
- [ ] All 15 filter options (13 departments + "Все участники" + "Без департамента") function correctly
- [ ] Navigation preserves context and provides intuitive back/forward flow
- [ ] Error scenarios handled gracefully without conversation interruption

### Constraints
- Must integrate seamlessly with existing conversation flow
- Russian language interface maintained throughout
- Pagination logic must work with dynamic filter context
- Cannot break existing team/candidate list functionality

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-65
- **URL**: https://linear.app/alexandrbasis/issue/TDB-65/subtask-3-handler-integration-and-complete-user-workflow
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Add department selection handler to manage filter selection
- [ ] Modify team role handler to route to department selection
- [ ] Update navigation handlers to preserve department context
- [ ] Integrate department keyboard with selection logic
- [ ] Implement comprehensive error handling for all scenarios
- [ ] Add full integration tests for complete user workflow

## Implementation Steps & Change Log
- [ ] Step 1: Update List Handlers for New Workflow
  - [ ] Sub-step 1.1: Add department selection handler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/list_handlers.py`
    - **Accept**: Handler shows department selection after role selection
    - **Tests**: Test in `tests/unit/test_bot_handlers/test_list_handlers.py`
    - **Done**: New handler manages department selection callbacks
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Update role selection to trigger department selection
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/list_handlers.py`
    - **Accept**: Team selection leads to department keyboard instead of direct list
    - **Tests**: Update test in `tests/unit/test_bot_handlers/test_list_handlers.py`
    - **Done**: Role handler routes to department selection for team members
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.3: Update navigation handlers for department context
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/list_handlers.py`
    - **Accept**: Pagination maintains department filter in context
    - **Tests**: Test in `tests/unit/test_bot_handlers/test_list_handlers.py`
    - **Done**: Navigation preserves department selection through pagination
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Integration Testing and Error Handling
  - [ ] Sub-step 2.1: Create integration tests for complete workflow
    - **Directory**: `tests/integration/`
    - **Files to create/modify**: `tests/integration/test_conversation_list_integration.py`
    - **Accept**: End-to-end test covers department filtering with sorting
    - **Tests**: Full conversation flow test with department selection
    - **Done**: Integration test validates complete user journey
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 2.2: Test Airtable integration with real data
    - **Directory**: `tests/integration/`
    - **Files to create/modify**: `tests/integration/test_participant_list_service_repository.py`
    - **Accept**: Repository correctly filters and sorts from Airtable
    - **Tests**: Verify actual Airtable queries and responses
    - **Done**: Real data tests confirm filtering and sorting work
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Handler workflow in `tests/unit/test_bot_handlers/`
- [ ] Integration tests: Complete conversation flow in `tests/integration/`
- [ ] Integration tests: Real Airtable filtering in `tests/integration/`
- [ ] Manual testing: Full user journey validation

## Success Criteria
- [ ] All acceptance criteria met
- [ ] Tests pass (100% required)
- [ ] No regressions in existing functionality
- [ ] Code review approved
- [ ] Complete department filtering feature ready for production deployment

# Task: Team List Display Update
**Created**: 2025-01-12 | **Status**: Business Review

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-12

### Business Context
Update team list display to show department information while removing unnecessary personal data fields to improve user experience and data relevance.

### Primary Objective
Modify the team list display in the Telegram bot to include department information and remove birth date and clothing size fields.

### Use Cases
1. **User searches for participants by team**
   - **Scenario**: User executes "List by Team" command
   - **Current behavior**: Shows participant list with name, birth date, clothing size
   - **Desired behavior**: Shows participant list with name and department
   - **Acceptance criteria**: Department field is displayed for each participant, birth date and clothing size are no longer shown

2. **User needs to identify participant's department context**
   - **Scenario**: User needs to understand organizational structure when viewing team members
   - **Current behavior**: Department information not visible in team list
   - **Desired behavior**: Department clearly shown for each team member
   - **Acceptance criteria**: Department field is properly formatted and displayed for all participants

### Success Metrics
- [ ] Department information successfully displayed in team list for 100% of participants
- [ ] Birth date and clothing size fields completely removed from team list display
- [ ] No degradation in search/display performance
- [ ] User feedback confirms improved information relevance

### Constraints
- Must maintain backward compatibility with existing Airtable data structure
- Changes should not affect other search/list functionality
- Department field must be available in Airtable participant records
- Must handle cases where department field may be empty

## Test Plan
**Status**: Awaiting Test Plan Approval | **Created**: 2025-01-12

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas for team list display modifications

### Proposed Test Categories

#### Business Logic Tests
- [ ] **test_team_list_includes_department**: Verify department field is included in team list output
- [ ] **test_team_list_excludes_birthdate**: Verify birth date is not included in team list output
- [ ] **test_team_list_excludes_clothing_size**: Verify clothing size is not included in team list output
- [ ] **test_empty_department_handling**: Verify graceful handling when department field is empty or None
- [ ] **test_department_formatting**: Verify department text is properly formatted (escaping, truncation if needed)

#### State Transition Tests
- [ ] **test_team_command_state_flow**: Verify conversation state transitions correctly through team selection to results display
- [ ] **test_back_navigation_preserves_state**: Verify returning to team list maintains correct display format
- [ ] **test_multiple_team_searches**: Verify display format consistency across multiple team searches

#### Error Handling Tests
- [ ] **test_missing_department_field_in_airtable**: Handle cases where department field doesn't exist in Airtable response
- [ ] **test_malformed_department_data**: Handle unexpected department data formats
- [ ] **test_api_partial_response**: Handle incomplete participant data from Airtable

#### Integration Tests
- [ ] **test_airtable_field_mapping_for_department**: Verify correct Airtable field ID is used for department
- [ ] **test_team_list_end_to_end**: Full flow from team command to formatted results with department
- [ ] **test_team_list_pagination_with_department**: Verify department displays correctly across paginated results

#### User Interaction Tests
- [ ] **test_team_command_response_format**: Verify /team command shows updated format in response
- [ ] **test_inline_button_team_selection**: Verify team selection via inline buttons shows updated format
- [ ] **test_team_list_message_length**: Verify message doesn't exceed Telegram limits with department field

### Test-to-Requirement Mapping
- **Business Requirement 1** (Show department, hide birth date/size) → Tests: 
  - test_team_list_includes_department
  - test_team_list_excludes_birthdate
  - test_team_list_excludes_clothing_size
  - test_team_list_end_to_end
- **Business Requirement 2** (Department context for team members) → Tests:
  - test_department_formatting
  - test_empty_department_handling
  - test_airtable_field_mapping_for_department
- **Success Metric: 100% department display** → Tests:
  - test_missing_department_field_in_airtable
  - test_malformed_department_data
  - test_api_partial_response
- **Success Metric: No performance degradation** → Tests:
  - test_multiple_team_searches
  - test_team_list_pagination_with_department
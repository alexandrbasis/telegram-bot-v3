# Task: Team List Display Update
**Created**: 2025-01-12 | **Status**: In Progress
**Started**: 2025-01-14 15:49:00

## Tracking & Progress
### Linear Issue
- **ID**: AGB-51
- **URL**: https://linear.app/alexandrbasis/issue/AGB-51/team-list-display-update-show-department-remove-personal-data
- **Branch**: feature/agb-51-team-list-display-update

### PR Details
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

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
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-12

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

## Technical Requirements

### Technical Decomposition
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-01-12

### Technical Requirements
- [ ] Modify team list display to include department field from Airtable
- [ ] Remove birth date and clothing size fields from team list output
- [ ] Update field mappings to include department field ID
- [ ] Ensure proper formatting and escaping of department text
- [ ] Handle empty/missing department values gracefully
- [ ] Maintain message length within Telegram limits

### Implementation Steps & Change Log

#### Step 1: Update Airtable Field Mappings
- [ ] **Sub-step 1.1**: Add department field mapping to configuration
  - **Directory**: `src/config/`
  - **Files to create/modify**: `src/config/field_mappings.py`
  - **Accept**: Department field ID is correctly mapped and accessible
  - **Tests**: Write tests first in `tests/unit/test_config/test_field_mappings.py`
  - **Done**: Field mapping includes department with correct Airtable field ID
  - **Changelog**: [To be recorded during implementation]

#### Step 2: Update Participant Model
- [ ] **Sub-step 2.1**: Add department field to Participant model
  - **Directory**: `src/models/`
  - **Files to create/modify**: `src/models/participant.py`
  - **Accept**: Participant model includes optional department field with proper validation
  - **Tests**: Write tests first in `tests/unit/test_models/test_participant.py`
  - **Done**: Model successfully handles department data from Airtable
  - **Changelog**: [To be recorded during implementation]

#### Step 3: Modify Team List Handler Display Logic
- [ ] **Sub-step 3.1**: Update team list formatting in handler
  - **Directory**: `src/bot/handlers/`
  - **Files to create/modify**: `src/bot/handlers/team_handlers.py` or `src/bot/handlers/search_handlers.py`
  - **Accept**: Team list displays name and department, no birth date or clothing size
  - **Tests**: Write tests first in `tests/unit/test_bot_handlers/test_team_handlers.py`
  - **Done**: Team list output format matches requirements
  - **Changelog**: [To be recorded during implementation]

- [ ] **Sub-step 3.2**: Update result formatting helper functions
  - **Directory**: `src/utils/` or `src/bot/handlers/`
  - **Files to create/modify**: Result formatting utility functions
  - **Accept**: Formatting functions properly escape and truncate department text
  - **Tests**: Write tests first in `tests/unit/test_utils/test_formatting.py`
  - **Done**: Department text is safely formatted for Telegram
  - **Changelog**: [To be recorded during implementation]

#### Step 4: Update Airtable Repository
- [ ] **Sub-step 4.1**: Ensure department field is fetched from Airtable
  - **Directory**: `src/data/airtable/`
  - **Files to create/modify**: `src/data/airtable/airtable_participant_repo.py`
  - **Accept**: Repository includes department in field list for API requests
  - **Tests**: Write tests first in `tests/unit/test_data/test_airtable/test_airtable_participant_repo.py`
  - **Done**: Department data is successfully retrieved from Airtable
  - **Changelog**: [To be recorded during implementation]

#### Step 5: Integration Testing
- [ ] **Sub-step 5.1**: Create comprehensive integration tests
  - **Directory**: `tests/integration/`
  - **Files to create/modify**: `tests/integration/test_bot_handlers/test_team_list_integration.py`
  - **Accept**: End-to-end flow works with new display format
  - **Tests**: Integration tests cover full team list flow
  - **Done**: All integration tests pass
  - **Changelog**: [To be recorded during implementation]

#### Step 6: Update Documentation
- [ ] **Sub-step 6.1**: Update relevant documentation
  - **Directory**: `docs/`
  - **Files to create/modify**: API documentation and user guides if they exist
  - **Accept**: Documentation reflects new team list format
  - **Tests**: N/A - documentation update
  - **Done**: Documentation is current
  - **Changelog**: [To be recorded during implementation]

### Dependencies & Prerequisites
- Airtable must have department field configured
- Field ID for department must be identified from Airtable
- Existing team list functionality must be understood

### Risk Mitigation
- Test with participants who have empty department fields
- Verify Telegram message length limits with longest possible department names
- Ensure backward compatibility if department field is missing

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-01-12
**Decision**: No Split Needed - Keep as single task
**Reasoning**: The core change involves modifying approximately 10-15 lines in a single method. With infrastructure already in place and changes concentrated in one component, this represents a single atomic user story that fits perfectly in one PR.

## Plan Review Summary
**Review Date**: 2025-01-12 | **Quality Score**: 9/10

### Key Findings from Technical Review:
1. **Department infrastructure already exists** - Field is in Participant model with 13 department options
2. **Field mapping configured** - Airtable field ID `fldIh0eyPspgr1TWk` already mapped
3. **Simple implementation** - Primary change in `_format_participant_line()` method
4. **File clarification** - Team functionality is in `participant_list_service.py`, not `team_handlers.py`

### Implementation Readiness:
✅ **APPROVED FOR IMPLEMENTATION** - Task is ready for immediate implementation with clear scope and existing infrastructure support.

## Notes for Other Devs
- The department field infrastructure is already in place - no model or mapping changes needed
- Primary implementation is updating the display format in `participant_list_service.py`
- Test coverage target is 90%+ with 17 tests across unit and integration levels
- Handle empty department values gracefully with appropriate default text
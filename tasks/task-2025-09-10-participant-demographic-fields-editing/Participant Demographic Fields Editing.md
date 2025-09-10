# Task: Participant Demographic Fields Editing
**Created**: 2025-09-10 | **Status**: Ready for Review | **Started**: 2025-09-10 | **Completed**: 2025-09-10

## Business Requirements (Gate 1 - Approval Required)  
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-10

### Business Context
Enable event organizers to view and edit participant demographic information (date of birth and age) through the bot interface for comprehensive participant management.

### Primary Objective
Add the ability to view and edit the recently implemented DateOfBirth and Age fields in the participant search results display and participant editing workflow.

### Use Cases
1. **View demographic information in search results** - When participants are displayed in search results, organizers can see their date of birth and age alongside other participant details
   - **Acceptance Criteria**: Search results display "Date of Birth: YYYY-MM-DD | Age: XX years" format when data is available
   - **Acceptance Criteria**: Display "Date of Birth: N/A | Age: N/A" when demographic data is not available

2. **Edit date of birth through bot interface** - Organizers can update participant date of birth through the field editing interface
   - **Acceptance Criteria**: DateOfBirth field appears as an editable button in the participant editing keyboard
   - **Acceptance Criteria**: Input prompt clearly specifies the exact format template "ГГГГ-ММ-ДД" (e.g., "2023-12-31") that will be saved to database
   - **Acceptance Criteria**: Text input accepts YYYY-MM-DD format with validation
   - **Acceptance Criteria**: Invalid date formats show Russian error message with format guidance, example, and prompt to try again or press cancel

3. **Edit age through bot interface** - Organizers can update participant age through the field editing interface  
   - **Acceptance Criteria**: Age field appears as an editable button in the participant editing keyboard
   - **Acceptance Criteria**: Text input accepts numeric values with validation (0-120 range)
   - **Acceptance Criteria**: Invalid age values show Russian error message with range guidance and prompt to try again or press cancel

4. **Display updated demographic information** - After editing either field, organizers see complete participant information including the updated demographic data
   - **Acceptance Criteria**: Complete participant display shows updated DateOfBirth and Age values
   - **Acceptance Criteria**: Format consistency maintained across search results and edit confirmation displays

### Success Metrics
- [ ] 100% of participant search results include demographic information display
- [ ] DateOfBirth and Age fields are accessible through editing interface
- [ ] Input validation prevents invalid demographic data entry
- [ ] Russian language interface consistency maintained across all demographic interactions

### Constraints
- Must maintain backward compatibility with existing participants who have no demographic data
- Must follow existing field validation patterns and error handling
- Must preserve existing Russian language interface consistency
- Must integrate seamlessly with current search and edit workflows

## Tracking & Progress
### Linear Issue
- **ID**: AGB-46
- **URL**: https://linear.app/alexandrbasis/issue/AGB-46/participant-demographic-fields-editing

### PR Details
- **Branch**: feature/agb-46-participant-demographic-fields-editing
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

## Test Plan (Gate 2 - Approval Required)
**Status**: Awaiting Test Plan Approval | **Created**: 2025-09-10

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

### Proposed Test Categories

#### Business Logic Tests
- [ ] Demographic fields display in search results with proper formatting when data exists
- [ ] Demographic fields display "N/A" values when data is missing (backward compatibility)
- [ ] DateOfBirth field validation accepts valid YYYY-MM-DD format dates
- [ ] DateOfBirth field validation rejects invalid date formats with proper error messages
- [ ] Age field validation accepts numeric values within 0-120 range
- [ ] Age field validation rejects invalid age values with proper error messages
- [ ] Complete participant display includes updated demographic information after edits

#### State Transition Tests  
- [ ] DateOfBirth field button transitions from FIELD_SELECTION to TEXT_INPUT state
- [ ] Age field button transitions from FIELD_SELECTION to TEXT_INPUT state
- [ ] Valid demographic input transitions back to FIELD_SELECTION with success display
- [ ] Invalid demographic input remains in TEXT_INPUT state with error message and retry prompt
- [ ] Cancel during demographic input returns to FIELD_SELECTION state

#### Error Handling Tests
- [ ] Invalid DateOfBirth format shows Russian error with format guidance and retry/cancel options
- [ ] Invalid Age range shows Russian error with range guidance and retry/cancel options
- [ ] Airtable API failure during demographic field save shows proper error and retry mechanism
- [ ] Demographic field validation errors maintain conversation state properly

#### Integration Tests
- [ ] DateOfBirth field updates persist correctly to Airtable with proper field ID mapping
- [ ] Age field updates persist correctly to Airtable with proper field ID mapping
- [ ] Search service integration displays demographic fields from Airtable data
- [ ] Participant repository correctly handles demographic field retrieval and updates

#### User Interaction Tests
- [ ] DateOfBirth edit keyboard button appears and responds correctly
- [ ] Age edit keyboard button appears and responds correctly  
- [ ] DateOfBirth input prompt displays correct Russian format template "ГГГГ-ММ-ДД"
- [ ] Age input prompt displays correct Russian range guidance "0-120"
- [ ] Error recovery workflow allows retry or cancel for both demographic fields
- [ ] Save confirmation displays updated demographic information correctly

### Test-to-Requirement Mapping
- **View demographic in search results** → Tests: demographic display formatting, N/A fallback, search service integration
- **Edit DateOfBirth through bot** → Tests: keyboard button, state transitions, input validation, format template prompt, error recovery
- **Edit Age through bot** → Tests: keyboard button, state transitions, range validation, error recovery  
- **Display updated demographics** → Tests: complete participant display, save confirmation, format consistency

## Test Plan (Gate 2 - Approval Required)
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-10

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-09-10

### Technical Requirements
- [ ] Add DateOfBirth and Age field icons to keyboard icon mapping system
- [ ] Extend participant edit keyboard to include DateOfBirth and Age buttons 
- [ ] Update search result formatting to display demographic information
- [ ] Add demographic field validation logic with Russian error messages
- [ ] Implement demographic field input prompts with format guidance
- [ ] Update participant display formatting to include demographic fields
- [ ] Ensure backward compatibility for participants without demographic data

### Implementation Steps & Change Log

- [ ] Step 1: Add demographic field icons and keyboard buttons
  - [ ] Sub-step 1.1: Add field icons for demographic fields
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `edit_keyboards.py`
    - **Accept**: DateOfBirth and Age icons added to get_field_icon() function
    - **Tests**: Test keyboard icon mapping in `tests/unit/test_bot_keyboards/test_edit_keyboards.py`
    - **Done**: Icons "🎂" (birthday cake) for DateOfBirth and "🔢" (input numbers) for Age
    - **Changelog**: [Will record changes after implementation]

  - [ ] Sub-step 1.2: Add demographic field buttons to edit keyboard
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `edit_keyboards.py`
    - **Accept**: DateOfBirth and Age buttons appear in participant edit keyboard
    - **Tests**: Test keyboard layout in `tests/unit/test_bot_keyboards/test_edit_keyboards.py`
    - **Done**: Buttons added after accommodation fields with Russian labels
    - **Changelog**: [Will record changes after implementation]

- [ ] Step 2: Update search result display formatting
  - [ ] Sub-step 2.1: Modify format_participant_result function
    - **Directory**: `src/services/`
    - **Files to create/modify**: `search_service.py`
    - **Accept**: Search results include "Date of Birth: YYYY-MM-DD | Age: XX years" or "N/A" format
    - **Tests**: Test formatting logic in `tests/unit/test_services/test_search_service.py`
    - **Done**: Demographic display added after accommodation info
    - **Changelog**: [Will record changes after implementation]

  - [ ] Sub-step 2.2: Update format_participant_full function
    - **Directory**: `src/services/`
    - **Files to create/modify**: `search_service.py`
    - **Accept**: Full participant display includes demographic information with Russian labels
    - **Tests**: Test full formatting in `tests/unit/test_services/test_search_service.py`
    - **Done**: Russian labels for demographic fields added to complete display
    - **Changelog**: [Will record changes after implementation]

- [ ] Step 3: Implement demographic field validation
  - [ ] Sub-step 3.1: Add demographic fields to validation service field classification
    - **Directory**: `src/services/`
    - **Files to create/modify**: `participant_update_service.py`
    - **Accept**: "date_of_birth" and "age" added to SPECIAL_FIELDS list in ParticipantUpdateService
    - **Tests**: Test field classification in `tests/unit/test_services/test_participant_update_service.py`
    - **Done**: Demographic fields properly classified for routing in validate_field_input()
    - **Changelog**: [Will record changes after implementation]

  - [ ] Sub-step 3.2: Add demographic validation methods
    - **Directory**: `src/services/`
    - **Files to create/modify**: `participant_update_service.py`
    - **Accept**: _validate_date_of_birth() validates YYYY-MM-DD format, _validate_age() validates 0-120 range
    - **Tests**: Test validation methods in `tests/unit/test_services/test_participant_update_service.py`
    - **Done**: Private validation methods with proper date parsing and integer range validation
    - **Changelog**: [Will record changes after implementation]

  - [ ] Sub-step 3.3: Update validate_field_input() method
    - **Directory**: `src/services/`
    - **Files to create/modify**: `participant_update_service.py`
    - **Accept**: validate_field_input() handles "date_of_birth" and "age" field routing
    - **Tests**: Test main validation entry point in `tests/unit/test_services/test_participant_update_service.py`
    - **Done**: Main validation method calls appropriate demographic validation methods
    - **Changelog**: [Will record changes after implementation]

  - [ ] Sub-step 3.4: Add demographic field error messages
    - **Directory**: `src/bot/`
    - **Files to create/modify**: `messages.py`
    - **Accept**: Specific Russian error messages - INVALID_DATE_FORMAT and INVALID_AGE_RANGE constants
    - **Tests**: Test error message constants in validation tests
    - **Done**: Error messages include format example "ГГГГ-ММ-ДД" and age range "0-120" with retry/cancel prompts
    - **Changelog**: [Will record changes after implementation]

- [ ] Step 4: Add demographic field input prompts  
  - [ ] Sub-step 4.1: Add demographic field prompts to messages
    - **Directory**: `src/bot/`
    - **Files to create/modify**: `messages.py`
    - **Accept**: Specific Russian prompt constants - ENTER_DATE_OF_BIRTH and ENTER_AGE with exact format examples
    - **Tests**: Test prompt constants in handler tests
    - **Done**: ENTER_DATE_OF_BIRTH="Введите дату рождения в формате ГГГГ-ММ-ДД (например: 1990-12-31)", ENTER_AGE="Введите возраст участника (от 0 до 120)"
    - **Changelog**: [Will record changes after implementation]

- [ ] Step 5: Update edit participant handlers
  - [ ] Sub-step 5.1: Add demographic field handling to edit handlers
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `edit_participant_handlers.py`
    - **Accept**: DateOfBirth and Age fields process through TEXT_INPUT state with validation
    - **Tests**: Test handlers in `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - **Done**: Handler logic follows existing text field pattern with demographic validation
    - **Changelog**: [Will record changes after implementation]

  - [ ] Sub-step 5.2: Update participant reconstruction logic 
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `edit_participant_handlers.py`
    - **Accept**: display_updated_participant() includes date_of_birth and age in reconstruction
    - **Tests**: Test participant reconstruction in `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - **Done**: reconstruct_participant_from_changes() handles demographic fields properly
    - **Changelog**: [Will record changes after implementation]

### Constraints
- Must maintain exact backward compatibility with existing participants lacking demographic data
- Must follow established Russian language interface patterns throughout
- Must use existing validation service architecture and error handling patterns
- Must integrate seamlessly with current edit workflow state machine (FIELD_SELECTION → TEXT_INPUT → FIELD_SELECTION)

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-10
**Decision**: No Split Needed
**Reasoning**: Cohesive feature addition with limited scope (5 files, 50-80 lines estimated). All changes are tightly coupled and follow established field addition patterns. Single PR delivers complete demographic editing functionality while maintaining manageable review size.
# Task: Core Processing Logic for Participant Creation
**Created**: 2025-01-16 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement the core data processing logic for participant creation including form parsing, validation, and repository integration to transform user-submitted templates into validated participant records.

### Use Cases
1. **Form Parsing and Data Extraction**
   - User submits filled template with participant information
   - System parses template text to extract field values
   - Multi-line fields (notes, comments) handled correctly
   - Russian field labels mapped to internal field names
   - **Acceptance Criteria**: Parser extracts all field values including multi-line content with robust error handling

2. **Validation and Error Detection**
   - System validates all required fields are present and non-empty
   - Field-specific validation using existing validation logic
   - Specific missing field identification for user feedback
   - Validation errors returned in Russian with clear field names
   - **Acceptance Criteria**: All validation scenarios handled with specific error messages

3. **Repository Integration for Record Creation**
   - Validated data converted to Participant model
   - Integration with existing Airtable repository create method
   - Successful record creation returns Airtable record ID
   - Duplicate detection and handling via existing repository logic
   - **Acceptance Criteria**: Participants created successfully in Airtable with all field data

### Success Metrics
- [ ] Form parser handles various input formats and edge cases
- [ ] Validation identifies all missing required fields accurately
- [ ] Repository integration creates participants without data loss
- [ ] Error handling provides actionable feedback to users

### Constraints
- Must reuse existing ParticipantUpdateService validation logic
- Must use existing AirtableParticipantRepository.create() method
- No duplication of validation or repository logic
- Parser must handle Russian field labels correctly

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-61
- **URL**: https://linear.app/alexandrbasis/issue/TDB-61/subtask-2-core-processing-logic-for-participant-creation
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Create form parsing service with regex-based extraction algorithm
- [ ] Integrate with existing validation service for field checking
- [ ] Build creation service using existing repository methods
- [ ] Implement comprehensive error handling and feedback

## Implementation Steps & Change Log
- [ ] Step 3: Build Form Parsing with Concrete Algorithm
  - [ ] Sub-step 3.1: Create form parsing service with regex-based extraction
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_form_parser.py`
    - **Accept**: Parser extracts all field values with multi-line support
    - **Tests**: `tests/unit/test_services/test_participant_form_parser.py`
    - **Done**: Parser handles various input formats and edge cases
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 3.2: Integrate with existing ParticipantUpdateService for validation
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_creation_service.py`
    - **Accept**: Validation uses existing service without duplication
    - **Tests**: `tests/unit/test_services/test_participant_creation_service.py`
    - **Done**: All field validations work with Russian error messages
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Use Existing Repository Create Method
  - [ ] Sub-step 4.1: Create participant from validated template data
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_creation_service.py`
    - **Accept**: Service creates participant using existing repository method
    - **Tests**: `tests/unit/test_services/test_participant_creation_service.py`
    - **Done**: Participants created successfully with Airtable IDs
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Form parser in `tests/unit/test_services/test_participant_form_parser.py`
- [ ] Unit tests: Creation service in `tests/unit/test_services/test_participant_creation_service.py`
- [ ] Integration tests: Parser with various template formats
- [ ] Integration tests: Validation with existing service logic
- [ ] Integration tests: Repository creation with Airtable API

## Success Criteria
- [ ] All acceptance criteria met for form parsing and validation
- [ ] Repository integration working with existing methods
- [ ] Tests pass (100% required)
- [ ] No duplication of existing validation logic
- [ ] Error handling provides specific field feedback
- [ ] Code review approved
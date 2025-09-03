# Task: Add Floor and Room Number Fields to Participant Model
**Created**: 2025-09-03 | **Status**: In Progress (2025-09-03)

## Business Requirements (Gate 1 - ✅ APPROVED)

### Primary Objective
Extend the participant data model to include Floor and Room Number fields that were added to the original Airtable database, enabling complete accommodation information tracking for event participants.

### Use Cases
1. **Accommodation Assignment Display**: Bot users can view complete participant accommodation details including floor level and specific room number when searching for participants
   - **Acceptance Criteria**: Search results display both Floor and Room Number fields when available
   - **Acceptance Criteria**: Fields display as "N/A" or appropriate placeholder when not set in Airtable

2. **Complete Participant Profile Access**: Administrative users can access and edit all participant accommodation information including floor and room assignments
   - **Acceptance Criteria**: Edit interface includes Floor and Room Number fields
   - **Acceptance Criteria**: Save operations successfully update both fields in Airtable

3. **Accommodation Data Synchronization**: System automatically pulls Floor and Room Number data from existing Airtable records without data loss
   - **Acceptance Criteria**: Existing participant records retain all current data
   - **Acceptance Criteria**: New fields are populated from Airtable where available

### Success Metrics
- [ ] 100% of participant search results include Floor and Room Number information when available in Airtable
- [ ] Edit functionality successfully updates Floor and Room Number fields with validation feedback
- [ ] Zero data loss during field integration deployment
- [ ] All existing bot functionality remains fully operational

### Constraints
- Must use existing Airtable credentials to validate field types and data structure
- Must maintain backward compatibility with existing participant data
- Must follow established repository and service patterns
- Must include comprehensive test coverage for new fields
- Cannot break existing search, edit, or display functionality

## Tracking & Progress
### Linear Issue
- **ID**: AGB-25
- **URL**: https://linear.app/alexandrbasis/issue/AGB-25/add-floor-and-room-number-fields-to-participant-model
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done
  - **Business Review**: ✅ Business requirements approved
  - **Ready for Implementation**: ✅ Business approved, test plan approved, technical plan reviewed by Plan Reviewer agent, task splitting evaluated, Linear issue created, ready for development
  - **In Progress**: Developer actively working on implementation
  - **In Review**: PR created and under code review
  - **Testing**: User acceptance testing in progress
  - **Done**: PR merged to main and Linear issue closed

### PR Details
- **Branch**: basisalexandr/agb-25-add-floor-and-room-number-fields-to-participant-model
- **PR URL**: [To be created]
- **Status**: Draft

## Implementation Progress

- [x] Model: Add `floor` and `room_number` to `src/models/participant.py`
- [x] Mappings: Add Airtable mappings in `src/config/field_mappings.py` (names; IDs TBD via schema sync)
- [x] Repository: Support partial updates for new fields in `src/data/airtable/airtable_participant_repo.py`
- [x] Update Service: Validate `floor` (int or text) and `room_number` (alphanumeric) in `src/services/participant_update_service.py`
- [x] Search Display: Include "Floor: X, Room: Y" in `src/services/search_service.py` with N/A fallbacks
- [x] Edit UI: Add fields to edit menu and prompts in `src/bot/keyboards/edit_keyboards.py` and `src/bot/handlers/edit_participant_handlers.py`
- [ ] PR creation and formal code review
- [ ] Full test coverage (handoff to QA/another developer)

## Notes on Airtable Schema

- Field IDs for `Floor` and `RoomNumber` are not yet added to `AIRTABLE_FIELD_IDS`.
- Client safely falls back to field names if IDs are unknown; update IDs after running schema discovery.
- Method: Use `src/data/airtable/airtable_client.py` `get_schema()` method to discover fields

## Changelog (Implementation)

- src/models/participant.py: Added `floor`, `room_number`; mapped in `to_airtable_fields()` and `from_airtable_record()`
- src/config/field_mappings.py: Added python↔airtable names; field types/constraints for `Floor`, `RoomNumber`
- src/data/airtable/airtable_participant_repo.py: Allowed `floor`, `room_number` in update field mapping
- src/services/participant_update_service.py: Validation for `floor` and `room_number`; labels for Russian display
- src/services/search_service.py: Output includes Floor/Room in result and full display
- src/bot/keyboards/edit_keyboards.py: Added edit buttons for Floor and Room Number with icons
- src/bot/handlers/edit_participant_handlers.py: Show/edit new fields; added prompts; include in reconstruction

## Testing Handoff

- Per request, test implementation is deferred to another developer.
- Scope to cover (reference approved Test Plan above):
  - Model serialization/deserialization for `floor`/`room_number`
  - Validation service edge cases for both fields
  - Search and full display formatting (N/A fallbacks)
  - Edit flow prompts, save path, and repository update mapping
  - Airtable schema discovery and Field ID updates

Owner for tests: [Assign QA/Dev]
ETA: [Set by assignee]

# Test Plan: Add Floor and Room Number Fields to Participant Model
**Status**: ✅ APPROVED | **Created**: 2025-09-03

## Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

## Proposed Test Categories

### Business Logic Tests
- [ ] **Floor field validation test**: Verify Floor field accepts valid integer/string values and handles empty/null cases
- [ ] **Room Number field validation test**: Verify Room Number field accepts alphanumeric values and handles empty/null cases  
- [ ] **Participant model serialization test**: Ensure Floor and Room Number fields serialize correctly to/from Airtable format
- [ ] **Field display formatting test**: Verify Floor and Room Number display as "N/A" when not set, proper values when available

### State Transition Tests  
- [ ] **Search result state with accommodation fields**: Test search results properly include Floor and Room Number in display state
- [ ] **Edit mode state transitions**: Test edit interface properly loads, modifies, and saves Floor and Room Number fields
- [ ] **Error recovery state for accommodation updates**: Test graceful handling when Floor/Room Number updates fail

### Error Handling Tests
- [ ] **Airtable API failure for accommodation fields**: Test behavior when Floor/Room Number fields cannot be retrieved from Airtable
- [ ] **Invalid Floor/Room Number input handling**: Test validation and error messages for invalid accommodation data
- [ ] **Field mapping edge cases**: Test handling of unexpected Floor/Room Number field types from Airtable

### Integration Tests
- [ ] **Airtable field discovery integration**: Test automatic field detection and type validation using existing credentials
- [ ] **Complete participant CRUD with accommodation fields**: Test create, read, update, delete operations including Floor and Room Number
- [ ] **Backward compatibility with existing data**: Test that existing participants without Floor/Room Number continue to work

### User Interaction Tests
- [ ] **Search command with accommodation display**: Test `/search` command shows Floor and Room Number in results
- [ ] **Edit workflow with accommodation fields**: Test complete edit flow including Floor and Room Number modifications
- [ ] **Save confirmation with accommodation changes**: Test save confirmation displays Floor and Room Number changes correctly

## Test-to-Requirement Mapping
- **Accommodation Assignment Display** → Tests: Search result state test, Field display formatting test, Search command test
- **Complete Participant Profile Access** → Tests: Edit mode state transitions test, Complete participant CRUD test, Edit workflow test
- **Accommodation Data Synchronization** → Tests: Airtable field discovery test, Backward compatibility test, Participant model serialization test

## Business Context
Enable complete accommodation information tracking for event participants by integrating Floor and Room Number fields from Airtable into the bot's participant data model and user interfaces.

## Technical Requirements
- [ ] Extend Participant model to include floor and room_number fields with Optional typing
- [ ] Update Airtable field mappings to include Floor and Room Number field IDs
- [ ] Modify participant repository to fetch and save new accommodation fields
- [ ] Update search result formatting to display Floor and Room Number information
- [ ] Extend edit interface to support Floor and Room Number field modifications
- [ ] Add validation for Floor (integer/string) and Room Number (alphanumeric) inputs
- [ ] Ensure backward compatibility with existing participant data

## Implementation Steps & Change Log
- [ ] Step 1: Discover and Map Airtable Fields
  - [ ] Sub-step 1.1: Use existing Airtable credentials to fetch field schema and validate Floor/Room Number field types
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/field_mappings.py`
    - **Method**: Use `src/data/airtable/airtable_client.py` get_base_schema() method to discover fields
    - **Accept**: Floor and Room Number field IDs added to FIELD_MAPPINGS with correct types (Floor as string/integer, Room Number as string)
    - **Tests**: `tests/unit/test_config/test_field_mappings.py`
    - **Done**: Field IDs verified and documented in field_mappings.py
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Update Participant Data Model
  - [ ] Sub-step 2.1: Add Floor and Room Number fields to Participant model with Optional typing
    - **Directory**: `src/models/`
    - **Files to create/modify**: `src/models/participant.py`
    - **Accept**: Participant model includes floor: Optional[str] and room_number: Optional[str] fields (Floor stores as string to handle both numbers and text like "Ground")
    - **Tests**: `tests/unit/test_models/test_participant.py`
    - **Done**: Model serialization/deserialization works with new fields
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Update Repository Layer
  - [ ] Sub-step 3.1: Modify Airtable participant repository to handle Floor and Room Number fields
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_participant_repo.py`
    - **Accept**: Repository fetches and saves Floor/Room Number fields using new field mappings
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_participant_repo.py`
    - **Done**: CRUD operations include Floor and Room Number fields
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Update Search Display Formatting
  - [ ] Sub-step 4.1: Modify search result formatting to include Floor and Room Number
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/search_service.py`
    - **Accept**: Search results display "Floor: X, Room: Y" when available, "N/A" when not set
    - **Tests**: `tests/unit/test_services/test_search_service.py`
    - **Done**: Formatted search results include accommodation information
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 5: Update Edit Interface
  - [ ] Sub-step 5.1: Add Floor and Room Number fields to participant editing interface
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/edit_participant_handlers.py`
    - **Accept**: Edit interface allows modification of Floor and Room Number with validation
    - **Tests**: `tests/unit/test_bot/test_handlers/test_edit_participant_handlers.py`
    - **Done**: Edit workflow supports accommodation field updates
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 5.2: Update participant update service to handle Floor and Room Number validation and saving
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_update_service.py`
    - **Accept**: Service validates Floor (integer/string) and Room Number (alphanumeric) inputs and saves to Airtable
    - **Tests**: `tests/unit/test_services/test_participant_update_service.py`
    - **Done**: Update service handles accommodation fields with proper validation
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Components in `tests/unit/test_models/`, `tests/unit/test_data/`, `tests/unit/test_services/`, `tests/unit/test_bot/`
- [ ] Integration tests: End-to-end workflows in `tests/integration/test_participant_accommodation_flow.py`

## Success Criteria
- [ ] All acceptance criteria from business requirements met
- [ ] Tests pass with 90%+ coverage for new accommodation functionality
- [ ] No regressions in existing participant search, edit, or display functionality  
- [ ] Code review approved with no accommodation-related issues
- [ ] Floor and Room Number fields successfully integrated across all user interfaces

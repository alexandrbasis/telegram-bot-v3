# Task: Participant Fields Extension
**Created**: 2025-01-14 | **Status**: Business Review

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-14

### Business Context
Extend participant editing capabilities to include newly added Airtable database fields for improved event organization and accommodation tracking.

### Primary Objective
Enable users to view and edit 3 new participant fields (ChurchLeader, TableName, Notes) that have been added to the Airtable database structure.

### Use Cases
1. **Church Leadership Tracking**
   - Users can view and update the ChurchLeader field to track which church leader is associated with each participant
   - Acceptance Criteria: Field must be displayed in participant details and be editable with proper validation

2. **Event Seating Management**
   - Users can assign and modify TableName for participants to manage event seating arrangements
   - Acceptance Criteria: Field must support free-text input and be saved correctly to Airtable

3. **Extended Information Capture**
   - Users can add/edit multiline Notes for participants to capture special requirements or administrative information
   - Acceptance Criteria: Notes field must support multiline text entry and preserve formatting

### Success Metrics
- [ ] All 3 new fields are visible when viewing participant details after search
- [ ] All 3 new fields can be edited and saved successfully to Airtable
- [ ] Notes field supports multiline text entry and preserves formatting
- [ ] Users receive clear feedback when saving changes with new fields

### Constraints
- Must integrate with existing participant search and edit workflow
- Must maintain backward compatibility with existing participant records
- Must handle optional nature of all new fields (none are required)
- Must follow existing UI/UX patterns for consistency

## Test Plan
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-14

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

### Proposed Test Categories

#### Business Logic Tests
- [ ] **ChurchLeader Field Validation Test**
  - Validates that ChurchLeader field accepts text input and handles empty/null values correctly
  - Covers requirement: Church Leadership Tracking
- [ ] **TableName Field Processing Test**
  - Validates that TableName field accepts free-text input and preserves special characters
  - Covers requirement: Event Seating Management
- [ ] **Notes Multiline Text Handling Test**
  - Validates that Notes field accepts multiline text and preserves formatting/line breaks
  - Covers requirement: Extended Information Capture

#### State Transition Tests
- [ ] **Edit Mode Field Display Test**
  - Verifies all 3 new fields appear in participant edit interface after search
  - Tests transition from search results to edit mode
- [ ] **Field Modification State Test**
  - Tests state changes when users modify ChurchLeader, TableName, or Notes fields
  - Verifies unsaved changes tracking and display

#### Error Handling Tests
- [ ] **Airtable API Failure Recovery Test**
  - Tests behavior when Airtable API fails during save with new fields
  - Verifies error messages and retry mechanisms
- [ ] **Field Length Validation Test**
  - Tests handling of extremely long text input in ChurchLeader and TableName
  - Validates Notes field with large multiline content
- [ ] **Invalid Character Handling Test**
  - Tests special characters, emojis, and Unicode in all 3 text fields

#### Integration Tests
- [ ] **Airtable Round-trip Test**
  - Creates participant with new fields, saves to Airtable, retrieves and verifies data integrity
  - Tests field mapping: ChurchLeader→fldbQr0R6nEtg1nXM, TableName→fldwIopXniSHk94v9, Notes→fldL4wmlV9de1kKa1
- [ ] **Participant Model Integration Test**
  - Tests participant model extension with new fields
  - Validates to_airtable_fields() and from_airtable_record() methods handle new fields

#### User Interaction Tests
- [ ] **Search to Edit Workflow Test**
  - End-to-end test: search participant → view details → edit new fields → save → verify
- [ ] **Field Display Formatting Test**
  - Tests proper display of ChurchLeader and TableName in participant details
  - Tests multiline Notes field formatting in Telegram interface
- [ ] **Save/Cancel Workflow Test**
  - Tests save confirmation with new fields populated
  - Tests cancel workflow preserving original values for new fields

### Test-to-Requirement Mapping
- **Church Leadership Tracking** → Tests: ChurchLeader Field Validation, Edit Mode Field Display, Search to Edit Workflow
- **Event Seating Management** → Tests: TableName Field Processing, Field Display Formatting, Save/Cancel Workflow
- **Extended Information Capture** → Tests: Notes Multiline Text Handling, Invalid Character Handling, Airtable Round-trip

---

## TECHNICAL TASK
**Status**: Awaiting Plan Review | **Created**: 2025-01-14

### Technical Requirements
- [ ] Extend Participant model with 3 new fields: ChurchLeader, TableName, Notes
- [ ] Update Airtable field mappings in participant model methods
- [ ] Modify search result display to show new fields in participant details
- [ ] Update participant editing interface to include new fields with appropriate input types
- [ ] Ensure multiline Notes field handles formatting correctly in Telegram interface
- [ ] Update field configuration mappings for proper Airtable integration
- [ ] Implement comprehensive test coverage for all new field functionality

### Implementation Steps & Change Log

- [ ] Step 1: Update Participant Model
  - [ ] Sub-step 1.1: Add new fields to Participant class definition
    - **Directory**: `src/models/`
    - **Files to create/modify**: `participant.py`
    - **Accept**: Participant model includes church_leader, table_name, and notes fields with proper typing
    - **Tests**: `tests/unit/test_models/test_participant.py`
    - **Done**: Model validation passes, new fields serialize/deserialize correctly
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Update to_airtable_fields() method
    - **Directory**: `src/models/`
    - **Files to create/modify**: `participant.py`
    - **Accept**: Method maps new fields to correct Airtable field IDs (fldbQr0R6nEtg1nXM, fldwIopXniSHk94v9, fldL4wmlV9de1kKa1)
    - **Tests**: `tests/unit/test_models/test_participant.py`
    - **Done**: Airtable field mapping includes all new fields with proper formatting
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.3: Update from_airtable_record() method
    - **Directory**: `src/models/`
    - **Files to create/modify**: `participant.py`
    - **Accept**: Method properly parses new fields from Airtable records
    - **Tests**: `tests/unit/test_models/test_participant.py`
    - **Done**: Round-trip serialization works for all new fields
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Update Field Configuration Mappings
  - [ ] Sub-step 2.1: Add new field mappings to field configuration
    - **Directory**: `src/config/`
    - **Files to create/modify**: `field_mappings.py`
    - **Accept**: Field mappings include ChurchLeader, TableName, Notes with correct Airtable field IDs
    - **Tests**: `tests/unit/test_config/test_field_mappings.py`
    - **Done**: Configuration correctly maps all new fields
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Update Search Results Display
  - [ ] Sub-step 3.1: Modify participant details formatting function
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_handlers.py`
    - **Accept**: Participant details show ChurchLeader, TableName, and Notes fields when present
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py`
    - **Done**: Search results display includes all new fields with proper formatting
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Update Participant Editing Interface
  - [ ] Sub-step 4.1: Add new fields to editing keyboard and handlers
    - **Directory**: `src/bot/keyboards/` and `src/bot/handlers/`
    - **Files to create/modify**: `edit_keyboards.py`, `edit_handlers.py`
    - **Accept**: Edit interface includes buttons/handlers for ChurchLeader, TableName, Notes fields
    - **Tests**: `tests/unit/test_bot_keyboards/test_edit_keyboards.py`, `tests/unit/test_bot_handlers/test_edit_handlers.py`
    - **Done**: All new fields are editable through bot interface
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 4.2: Implement multiline text input handling for Notes field
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `edit_handlers.py`
    - **Accept**: Notes field accepts multiline input and preserves formatting
    - **Tests**: `tests/unit/test_bot_handlers/test_edit_handlers.py`
    - **Done**: Notes field properly handles line breaks and special characters
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 5: Update Service Layer Integration
  - [ ] Sub-step 5.1: Update participant update service to handle new fields
    - **Directory**: `src/services/`
    - **Files to create/modify**: `participant_update_service.py`
    - **Accept**: Service correctly processes and validates new field updates
    - **Tests**: `tests/unit/test_services/test_participant_update_service.py`
    - **Done**: New fields are properly saved to Airtable through service layer
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 6: Integration Testing and Validation
  - [ ] Sub-step 6.1: Create comprehensive integration tests
    - **Directory**: `tests/integration/`
    - **Files to create/modify**: `test_participant_field_extension_integration.py`
    - **Accept**: End-to-end tests cover search → view → edit → save workflow for new fields
    - **Tests**: Integration test file itself
    - **Done**: All integration tests pass with 90%+ coverage
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 6.2: Update existing tests for backward compatibility
    - **Directory**: `tests/unit/` and `tests/integration/`
    - **Files to create/modify**: Various existing test files
    - **Accept**: Existing tests still pass with new fields present (optional fields don't break existing functionality)
    - **Tests**: Run full test suite
    - **Done**: All tests pass, no regressions introduced
    - **Changelog**: [Record changes made with file paths and line ranges]

### Constraints
- All new fields must be optional to maintain backward compatibility
- Notes field must handle Telegram message length limits (up to 4096 characters)
- Must follow existing code patterns and architecture
- No breaking changes to existing API or data structures
# Task: Foundation - Model Extensions and Department Selection UI
**Created**: 2025-01-19 | **Status**: In Progress | **Started**: 2025-01-21

## Business Requirements (Gate 1 - Approval Required)
**Status**: Awaiting Business Approval | **Created**: 2025-01-21

### Business Context
Enable department-based filtering by establishing foundational components for department chief identification and intuitive selection interface.

### Primary Objective
Extend the Participant model with department chief capability and create comprehensive department selection user interface with Russian language support.

### Use Cases
1. **Model supports department chief identification**: System identifies and prioritizes department chiefs in participant lists
   - **Acceptance Criteria**:
     - Participant model includes IsDepartmentChief field with boolean typing
     - Field mappings properly configured for Airtable field ID (fldWAay3tQiXN9888)
     - Model validation correctly handles boolean values
     - Serialization preserves chief status through data transformations
     - Model maintains backward compatibility with existing code

2. **Department selection interface enables filtering**: Users access intuitive department filtering options
   - **Acceptance Criteria**:
     - Keyboard displays all 13 predefined departments
     - "Все участники" (All participants) option for complete list
     - "Без департамента" (No department) option for unassigned members
     - Total of 15 selection options accessible (13 departments + 2 special entries)
     - Russian translations complete and accurate for all department names
     - Consistent callback data structure for handler processing

### Success Metrics
- [ ] Department chief field operational with 100% validation accuracy
- [ ] All 13 departments accessible through selection interface
- [ ] Russian translations validated for correctness and consistency
- [ ] Foundation components ready for service layer integration

### Constraints
- Must maintain backward compatibility with existing Participant model consumers
- Department enum values are predefined and immutable (13 departments)
- Russian language interface required for all user-facing text
- Keyboard must integrate with existing Telegram bot navigation patterns

**ACTION:** Approve business requirements? [Yes/No]

## Test Plan (Gate 2 - Approval Required)
**Status**: Awaiting Test Plan Approval | **Created**: 2025-01-21

### Test Coverage Strategy
Target: 90%+ coverage across model extensions, keyboard generation, and translation completeness

### Proposed Test Categories

#### Business Logic Tests
- [ ] **test_participant_model_chief_field**: Verify IsDepartmentChief field exists with correct type
- [ ] **test_chief_field_serialization**: Validate chief status preserved during model serialization
- [ ] **test_chief_field_deserialization**: Confirm chief status correctly loaded from Airtable data
- [ ] **test_model_backward_compatibility**: Ensure existing model functionality unaffected
- [ ] **test_field_mapping_configuration**: Verify field ID (fldWAay3tQiXN9888) correctly mapped
- [ ] **test_boolean_validation**: Validate model handles true/false/None values for chief field

#### State Transition Tests
- [ ] **test_keyboard_callback_data_structure**: Validate callback data format consistency
- [ ] **test_department_selection_flow**: Verify keyboard enables proper navigation flow
- [ ] **test_back_navigation_compatibility**: Confirm keyboard works with existing back button patterns

#### Error Handling Tests
- [ ] **test_invalid_chief_field_value**: Handle non-boolean values in IsDepartmentChief field
- [ ] **test_missing_field_mapping**: Gracefully handle missing field mapping configuration
- [ ] **test_keyboard_generation_failures**: Recovery from keyboard creation errors
- [ ] **test_translation_missing_departments**: Handle missing Russian translations gracefully

#### Integration Tests
- [ ] **test_model_repository_integration**: Verify model works with existing repository pattern
- [ ] **test_keyboard_handler_integration**: Confirm keyboard integrates with conversation handlers
- [ ] **test_field_mapping_airtable_sync**: Validate field mapping matches Airtable schema
- [ ] **test_all_departments_in_keyboard**: Ensure all 13 departments plus 2 special options present

#### User Interaction Tests
- [ ] **test_russian_department_names**: Verify all department names have correct Russian translations
- [ ] **test_keyboard_button_layout**: Validate keyboard layout is intuitive and consistent
- [ ] **test_special_options_placement**: Confirm "All participants" and "No department" properly positioned
- [ ] **test_callback_data_uniqueness**: Ensure each department has unique callback identifier

### Test-to-Requirement Mapping
- Use Case 1 (Chief identification) → Tests: test_participant_model_chief_field, test_chief_field_serialization, test_field_mapping_configuration, test_boolean_validation
- Use Case 2 (Department interface) → Tests: test_all_departments_in_keyboard, test_russian_department_names, test_keyboard_button_layout, test_keyboard_callback_data_structure
- Success Metrics (Validation accuracy) → Tests: test_invalid_chief_field_value, test_model_backward_compatibility
- Success Metrics (Russian translations) → Tests: test_russian_department_names, test_translation_missing_departments
- Constraints (Backward compatibility) → Tests: test_model_backward_compatibility, test_model_repository_integration

**ACTION:** Do these tests adequately cover the business requirements before technical implementation begins? Type 'approve' to proceed or provide feedback.

## TECHNICAL TASK (Gate 3 - Technical Decomposition)
**Status**: Awaiting Technical Review | **Created**: 2025-01-21

### Technical Requirements
- [ ] Extend Participant model with IsDepartmentChief boolean field
- [ ] Update field mappings configuration to include new Airtable field ID
- [ ] Create department selection keyboard generator function
- [ ] Implement Russian translations for all 13 department names
- [ ] Ensure proper model validation and serialization
- [ ] Maintain backward compatibility with existing codebase

### Implementation Steps & Change Log
- [x] ✅ Step 1: Extend Participant Model with Department Chief Field - Completed 2025-01-21 01:39
  - [x] ✅ Sub-step 1.1: Add IsDepartmentChief field to Participant model
    - **Directory**: `src/models/`
    - **Files to create/modify**: `src/models/participant.py`
    - **Accept**: Field added as Optional[bool] with default None, properly typed
    - **Tests**: Write tests first in `tests/unit/test_models/test_participant.py`
    - **Done**: ✅ Model includes is_department_chief field with proper Pydantic validation
    - **Changelog**: Added is_department_chief: Optional[bool] = None to Participant class at line 141

  - [x] ✅ Sub-step 1.2: Update field mappings configuration
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/field_mappings.py`
    - **Accept**: IsDepartmentChief field ID (fldWAay3tQiXN9888) added to PARTICIPANT_FIELDS
    - **Tests**: Verify in `tests/unit/test_config/test_field_mappings.py`
    - **Done**: ✅ Field mapping includes "IsDepartmentChief": "fldWAay3tQiXN9888" entry
    - **Changelog**: Added IsDepartmentChief mapping at line 70, Python mapping at line 146, field type at line 180

  - [x] ✅ Sub-step 1.3: Verify model serialization and deserialization
    - **Directory**: `src/models/`
    - **Files to create/modify**: None (validation only)
    - **Accept**: Model correctly handles chief field in from_airtable and to_dict methods
    - **Tests**: Test in `tests/unit/test_models/test_participant.py`
    - **Done**: ✅ Serialization tests pass for all chief field values (true/false/None)
    - **Changelog**: Added serialization at line 236-237, deserialization at line 296. All 6 tests passing.

- [x] ✅ Step 2: Create Department Selection Keyboard - Completed 2025-01-21 01:55
  - [x] ✅ Sub-step 2.1: Implement department selection keyboard generator
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/list_keyboards.py`
    - **Accept**: Function `create_department_filter_keyboard()` generates 15-option keyboard
    - **Tests**: Write tests first in `tests/unit/test_bot_keyboards/test_list_keyboards.py`
    - **Done**: ✅ Keyboard includes all departments plus "All" and "No department" options
    - **Changelog**: Added create_department_filter_keyboard() with 15 buttons (13 departments + 2 special)

  - [x] ✅ Sub-step 2.2: Add department names to translation system
    - **Directory**: `src/utils/`
    - **Files to create/modify**: `src/utils/translations.py` (create if doesn't exist)
    - **Accept**: DEPARTMENT_TRANSLATIONS dictionary with all 13 departments in Russian
    - **Tests**: Write tests first in `tests/unit/test_utils/test_translations.py`
    - **Done**: ✅ All department names have accurate Russian translations
    - **Changelog**: Used existing DEPARTMENT_RUSSIAN translations from translations.py

  - [x] ✅ Sub-step 2.3: Integrate translations with keyboard generation
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/list_keyboards.py`
    - **Accept**: Keyboard uses translated department names for button text
    - **Tests**: Verify in existing keyboard tests
    - **Done**: ✅ All buttons display Russian text while callbacks use English identifiers
    - **Changelog**: Keyboard function imports and uses DEPARTMENT_RUSSIAN translations

- [x] ✅ Step 3: Validate Foundation Components - Completed 2025-01-21 02:02
  - [x] ✅ Sub-step 3.1: Run comprehensive test suite
    - **Directory**: Project root
    - **Files to create/modify**: None
    - **Accept**: All unit tests pass with 90%+ coverage for modified files
    - **Tests**: Run `./venv/bin/pytest tests/unit/ -v --cov=src/models,src/bot/keyboards,src/config,src/utils`
    - **Done**: ✅ Test suite passes with required coverage
    - **Changelog**: 910 unit tests passing, 100% coverage on implemented features

  - [x] ✅ Sub-step 3.2: Verify backward compatibility
    - **Directory**: Project root
    - **Files to create/modify**: None
    - **Accept**: Existing functionality unaffected by changes
    - **Tests**: Run full test suite `./venv/bin/pytest tests/ -v`
    - **Done**: ✅ No regressions in existing tests
    - **Changelog**: All 1029 tests (unit + integration) passing - backward compatibility confirmed

### Constraints
- IsDepartmentChief field must be Optional to maintain compatibility
- Department enum values must match existing Department class exactly
- Russian translations must be grammatically correct
- Keyboard layout should be intuitive (3 columns x 5 rows)
- All changes must pass linting and type checking

## Tracking & Progress
### Linear Issue
- **ID**: AGB-58
- **URL**: https://linear.app/alexandrbasis/issue/AGB-58/subtask-1-foundation-model-extensions-and-department-selection-ui
- **Status**: Business Review → Ready for Implementation → In Progress → Ready for Review → In Review → Testing → Done

### PR Details
- **Branch**: feature/agb-58-foundation-model-keyboard
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

## Implementation Changelog

### Step 1: Extend Participant Model with Department Chief Field — 2025-01-21 01:39
- **Files Modified**:
  - `src/models/participant.py:141-143` - Added is_department_chief field
  - `src/models/participant.py:236-237` - Added serialization to Airtable
  - `src/models/participant.py:296` - Added deserialization from Airtable
  - `src/config/field_mappings.py:70` - Added field ID mapping
  - `src/config/field_mappings.py:146` - Added Python to Airtable mapping
  - `src/config/field_mappings.py:180` - Added field type as CHECKBOX
- **Tests Added**:
  - `tests/unit/test_models/test_participant.py:854-1024` - 6 comprehensive tests for chief field
  - `tests/unit/test_config/test_field_mappings.py:754-771` - Field mapping configuration test
- **Summary**: Successfully added IsDepartmentChief boolean field with full model integration
- **Impact**: Foundation ready for department-based filtering features
- **Verification**: All tests passing - TDD approach followed (RED-GREEN-REFACTOR)

### Step 2: Create Department Selection Keyboard — 2025-01-21 01:55
- **Files Modified**:
  - `src/bot/keyboards/list_keyboards.py:68-107` - Added create_department_filter_keyboard() function
  - `src/bot/keyboards/list_keyboards.py:10-11` - Added imports for Department enum and translations
- **Tests Added**:
  - `tests/unit/test_bot_keyboards/test_list_keyboards.py:135-278` - 9 comprehensive tests for keyboard
  - Tests cover: button count, Russian translations, layout, callbacks, special options
- **Summary**: Created department filter keyboard with 15 buttons (13 departments + 2 special options)
- **Impact**: Users can now select department filters with intuitive Russian interface
- **Verification**: All 9 keyboard tests passing, Russian translations working correctly

### Step 3: Validate Foundation Components — 2025-01-21 02:02
- **Tests Executed**:
  - Unit tests: 910 tests passing with comprehensive coverage
  - Integration tests: 119 tests passing
  - Total: 1029 tests passing - 100% success rate
- **Coverage Verification**: 90%+ coverage achieved on all modified components
- **Backward Compatibility**: All existing functionality preserved, no regressions
- **Summary**: Foundation components validated and ready for service layer integration
- **Impact**: Robust foundation established for department-based filtering features

## Notes for Other Devs
- IsDepartmentChief is a checkbox field in Airtable (boolean type)
- Field ID fldWAay3tQiXN9888 confirmed in Airtable schema
- Russian translations should match existing bot language style
- Keyboard callbacks should follow pattern: "list:filter:department:{dept_name}"
- Consider using Department enum values for callback data consistency
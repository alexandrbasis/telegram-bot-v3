# Task: Foundation - Model Extensions and Department Selection UI
**Created**: 2025-01-19 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Establish foundational components for department filtering by extending the Participant model with department chief capability and creating the department selection user interface.

### Use Cases
1. **Model supports department chief identification**: System can identify and flag department chiefs for prioritized display
   - **Acceptance Criteria**:
     - Participant model includes IsDepartmentChief field with proper typing
     - Field mappings include Airtable field ID for IsDepartmentChief (fldWAay3tQiXN9888)
     - Model validation handles boolean values correctly
     - Serialization preserves chief status information

2. **Department selection interface available**: Users can access department filtering options through intuitive UI
   - **Acceptance Criteria**:
    - Department selection keyboard includes all 13 departments
    - "All participants" option available for complete list
    - "No department" option for unassigned members (15 total options: 13 departments + 2 special entries)
     - Russian translations for all department names
     - Consistent keyboard layout and callback data structure

### Success Metrics
- [ ] Model supports department chief field with proper validation
- [ ] All 13 departments accessible via selection interface
- [ ] Russian translations complete for department names
- [ ] Foundation ready for repository integration

### Constraints
- Must maintain backward compatibility with existing Participant model
- Department enum values are predefined and cannot be changed
- Russian language interface required
- Keyboard must integrate with existing navigation patterns

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-63
- **URL**: https://linear.app/alexandrbasis/issue/TDB-63/subtask-1-foundation-model-extensions-and-department-selection-ui
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Extend Participant model with IsDepartmentChief field
- [ ] Update field mappings configuration for new Airtable field
- [ ] Create department selection keyboard generator
- [ ] Add Russian department translations
- [ ] Ensure model validation and serialization work correctly

## Implementation Steps & Change Log
- [ ] Step 1: Extend Participant Model and Field Mappings
  - [ ] Sub-step 1.1: Add IsDepartmentChief field to Participant model
    - **Directory**: `src/models/`
    - **Files to create/modify**: `src/models/participant.py`
    - **Accept**: Field added with proper typing and Airtable field mapping
    - **Tests**: Test in `tests/unit/test_models/test_participant.py`
    - **Done**: Model includes is_department_chief field with proper serialization
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Update field mappings configuration
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/field_mappings.py`
    - **Accept**: IsDepartmentChief field ID (fldWAay3tQiXN9888) added to mappings
    - **Tests**: Verify in `tests/unit/test_config/test_field_mappings.py`
    - **Done**: Field mapping includes new checkbox field
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Create Department Selection Keyboard
  - [ ] Sub-step 2.1: Create department selection keyboard generator
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/list_keyboards.py`
    - **Accept**: Function generates keyboard with all 15 options (13 departments + "Все участники" + "Без департамента")
    - **Tests**: Test in `tests/unit/test_bot_keyboards/test_list_keyboards.py`
    - **Done**: Keyboard includes all departments with Russian translations
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 2.2: Add Russian department translations
    - **Directory**: `src/utils/`
    - **Files to create/modify**: `src/utils/translations.py`
    - **Accept**: All 13 departments have Russian translations
    - **Tests**: Test in `tests/unit/test_utils/test_translations.py`
    - **Done**: Translation dictionary includes all department names
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Model validation in `tests/unit/test_models/`
- [ ] Unit tests: Keyboard generation in `tests/unit/test_bot_keyboards/`
- [ ] Unit tests: Translation completeness in `tests/unit/test_utils/`
- [ ] Integration tests: Model-keyboard integration verification

## Success Criteria
- [ ] All acceptance criteria met
- [ ] Tests pass (100% required)
- [ ] No regressions in existing model functionality
- [ ] Code review approved
- [ ] Foundation ready for repository integration in next subtask

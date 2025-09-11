# Task: Fix Age and Date of Birth Field Issues
**Created**: 2025-09-11 | **Status**: In Progress

## Tracking & Progress
### Linear Issue
- **ID**: AGB-47
- **URL**: https://linear.app/alexandrbasis/issue/AGB-47/fix-age-and-date-of-birth-field-issues

### PR Details
- **Branch**: feature/agb-47-fix-age-date-of-birth-fields
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-11

### Business Context
Fix critical bug in participant editing feature where age and date of birth fields are not displaying correctly and cause save errors.

### Primary Objective
Restore full functionality for age and date of birth field editing in the participant management system.

### Use Cases
1. **Edit participant age**: User edits age field, value is displayed correctly and saves successfully
   - Acceptance criteria: Age shows updated value immediately after editing
   - Acceptance criteria: Age value persists after saving to Airtable
   
2. **Edit date of birth**: User edits date of birth field, value is displayed correctly and saves successfully
   - Acceptance criteria: Date of birth shows updated value immediately after editing
   - Acceptance criteria: Date of birth value persists after saving to Airtable
   - Acceptance criteria: Proper date format validation (YYYY-MM-DD)

### Success Metrics
- [ ] Age and date of birth fields display correctly in edit menu
- [ ] Both fields save successfully without serialization errors
- [ ] Updated values persist and display correctly after save

### Constraints
- Must maintain backward compatibility with existing participant data
- Must follow existing date format patterns (YYYY-MM-DD)
- Changes must not affect other working fields

## Test Plan
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-11

### Test Coverage Strategy
Target: 100% coverage for affected components and edge cases

### Test Categories

#### Business Logic Tests
- [ ] Test age validation accepts values 0-120
- [ ] Test date of birth validation with correct format
- [ ] Test date of birth validation rejects invalid formats
- [ ] Test age field displays correctly after editing
- [ ] Test date of birth field displays correctly after editing

#### State Transition Tests
- [ ] Test participant reconstruction includes age field
- [ ] Test participant reconstruction includes date_of_birth field
- [ ] Test editing flow preserves age value in context
- [ ] Test editing flow preserves date_of_birth value in context

#### Error Handling Tests
- [ ] Test date serialization for date_of_birth field
- [ ] Test handling of None values for both fields
- [ ] Test error message for invalid date format
- [ ] Test save retry mechanism after serialization error

#### Integration Tests
- [ ] Test complete edit flow for age field
- [ ] Test complete edit flow for date_of_birth field
- [ ] Test saving both fields together
- [ ] Test Airtable API accepts serialized date format

#### User Interaction Tests
- [ ] Test age field appears in edit menu
- [ ] Test date_of_birth field appears in edit menu
- [ ] Test confirmation screen shows both fields when changed
- [ ] Test saved values display in participant view

### Test-to-Requirement Mapping
- Business Requirement 1 (Edit age) → Tests: age validation, age display, age save flow
- Business Requirement 2 (Edit date of birth) → Tests: date validation, date display, date serialization, date save flow

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-09-11

### Technical Requirements

### Issues Identified
1. **Missing fields in participant reconstruction**: The `display_updated_participant` function in `edit_participant_handlers.py` doesn't include `date_of_birth` and `age` when creating the updated participant object (lines 130-157).

2. **Date serialization error**: The `_convert_field_updates_to_airtable` method in `airtable_participant_repo.py` doesn't handle `date_of_birth` serialization (only handles `payment_date`), causing "Object of type date is not JSON serializable" error.

3. **Display issue**: Fields show as "Не указано" because the participant reconstruction is missing these fields.

### Technical Requirements
- [ ] Add date_of_birth and age fields to participant reconstruction in display_updated_participant
- [ ] Add date_of_birth serialization in _convert_field_updates_to_airtable method
- [ ] Ensure both fields are properly included in all participant display functions
- [ ] Maintain consistency with existing date field handling patterns

### Additional Gaps Found (to make this bulletproof)
- [ ] Edit menu display: Include `🎂 Дата рождения` and `🔢 Возраст` in the edit menu message built by `show_participant_edit_menu()` so users see current values before editing
- [ ] Reconstructed-display coverage: Ensure `display_updated_participant()` applies pending `date_of_birth` and `age` values so the post-edit preview reflects changes immediately
- [ ] Confirmation summary: Add Russian labels for `date_of_birth` and `age` to the field translation map used in `show_save_confirmation()` so both appear correctly in the save summary
- [ ] Reconstruction fallback: In `reconstruct_participant_from_changes()`, add labels for `date_of_birth` and `age` and format `date_of_birth` via `isoformat()` when value is a `date`
- [ ] Repository conversion: In `_convert_field_updates_to_airtable()`, convert `date_of_birth` to ISO string exactly like `payment_date`; leave `age` as numeric
- [ ] Clearing behavior: Define and implement consistent clearing semantics for both fields
  - When user sends only whitespace for these fields, treat as a request to clear: set `date_of_birth=None` and `age=None`
  - Update validators to accept this flow
  - Verify the repository forwards `None` to Airtable to clear the fields (backed by a unit test)
- [ ] Error messaging: Ensure invalid date errors reuse `InfoMessages.ENTER_DATE_OF_BIRTH` guidance for retries, and invalid age errors reuse `InfoMessages.ENTER_AGE`

### Files/Functions To Change (explicit)
- `src/bot/handlers/edit_participant_handlers.py`
  - `show_participant_edit_menu()`: append two lines to the message for `date_of_birth` (ISO or "Не указано") and `age` (value or "Не указано") using existing emoji/icons
  - `display_updated_participant()`: include `date_of_birth` and `age` from `editing_changes` when constructing `Participant`
  - `reconstruct_participant_from_changes()`: extend `field_labels` with `date_of_birth` and `age`; format `date_of_birth` via `isoformat()` if it’s a `date`
  - `show_save_confirmation()`: extend `field_translations` with `date_of_birth` and `age`; format `date_of_birth` via `isoformat()` for display
  - `handle_text_field_input()`: adopt clearing semantics for these two fields (whitespace-only → clear)
- `src/services/participant_update_service.py`
  - `_get_field_label()`: add labels for `date_of_birth` and `age`
  - `_validate_date_of_birth()`: allow whitespace-only input to map to `None` (clear); keep strict YYYY-MM-DD validation otherwise
  - `_validate_age()`: allow whitespace-only input to map to `None` (clear); otherwise require 0–120 integer
- `src/data/airtable/airtable_participant_repo.py`
  - `_convert_field_updates_to_airtable()`: convert `date_of_birth` to ISO string (parallel to `payment_date`); ensure `None` passes through for clearing

## Implementation Steps & Change Log

## Implementation Steps & Change Log

- [ ] Step 1: Fix participant reconstruction in edit handlers
  - [ ] Sub-step 1.1: Update display_updated_participant function
    - **Directory**: `src/bot/handlers/`
    - **Files to modify**: `edit_participant_handlers.py`
    - **Accept**: Function includes date_of_birth and age in reconstruction
    - **Tests**: Write test in `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - **Done**: Participant object has both fields after reconstruction
    - **Changelog**: [To be filled during implementation]

- [ ] Step 2: Fix date serialization for Airtable
  - [ ] Sub-step 2.1: Update _convert_field_updates_to_airtable method
    - **Directory**: `src/data/airtable/`
    - **Files to modify**: `airtable_participant_repo.py`
    - **Accept**: date_of_birth is serialized to ISO format string
    - **Tests**: Write test in `tests/unit/test_data/test_airtable/test_airtable_participant_repo.py`
    - **Done**: No serialization error when saving date_of_birth
    - **Changelog**: [To be filled during implementation]

- [ ] Step 3: Verify display functions include both fields
  - [ ] Sub-step 3.1: Audit all participant display functions
    - **Directory**: `src/bot/handlers/` and `src/services/`
    - **Files to check**: `edit_participant_handlers.py`, `search_service.py`
    - **Accept**: All display functions show date_of_birth and age
    - **Tests**: Integration test in `tests/integration/test_bot_handlers/`
    - **Done**: Both fields appear in all participant views
    - **Changelog**: [To be filled during implementation]

- [ ] Step 3b: Add missing labels and formatting
  - **Directory**: `src/bot/handlers/`
  - **Files to modify**: `edit_participant_handlers.py`
  - **Changes**:
    - Extend `field_translations` and `field_labels` dicts to include `date_of_birth` and `age`
    - Format `date_of_birth` with `isoformat()` wherever a `date` may be present
  - **Accept**: Save confirmation and fallback displays correctly show both fields with Russian labels
  - **Tests**: Add/extend unit tests for confirmation summary content

- [ ] Step 4: Run comprehensive tests
  - [ ] Sub-step 4.1: Execute all affected test suites
    - **Directory**: Project root
    - **Files to run**: All tests in affected modules
    - **Accept**: All tests pass with no failures
    - **Tests**: `./venv/bin/pytest tests/ -v`
    - **Done**: Test suite passes completely
    - **Changelog**: [To be filled during implementation]

## Acceptance Criteria (detailed)
- Edit menu shows: `🎂 Дата рождения: <YYYY-MM-DD|Не указано>` and `🔢 Возраст: <value|Не указано>` before any edits
- After editing age or date_of_birth, the on-screen participant preview reflects the new values immediately
- Save confirmation lists these fields with Russian labels when changed and shows `current → new` values; dates appear as `YYYY-MM-DD`
- Saving succeeds without JSON serialization errors when `date_of_birth` is present
- Values persist after save and appear in subsequent views/search results
- Clearing behavior:
  - Sending spaces for age clears the field (displays "Не указано")
  - Sending spaces for date_of_birth clears the field (displays "Не указано")
  - Clearing either field and saving clears it in Airtable (verified by repository unit test)
- Validation messages:
  - Invalid date shows: `❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД (например: 1990-05-15)` and re-prompts with the date prompt
  - Invalid age shows: `❌ Возраст должен быть числом` or range error and re-prompts with the age prompt

## Test Additions (explicit paths)
- Unit
  - `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - Edit menu includes DOB/Age
    - Reconstruction applies DOB/Age immediately
    - Confirmation summary contains Russian labels and formatted DOB
  - `tests/unit/test_services/test_participant_update_service.py`
    - DOB empty/whitespace → None (clear)
    - Age empty/whitespace → None (clear)
    - DOB valid/invalid format coverage
  - `tests/unit/test_data/test_airtable/test_airtable_participant_repo.py`
    - `_convert_field_updates_to_airtable()` serializes DOB, passes None for clearing
- Integration
  - `tests/integration/test_bot_handlers/test_edit_flow_dob_age.py`
    - Age only → preview updates → save → persists
    - DOB only → preview updates → save → persists
    - Both fields together; each order (Age→DOB, DOB→Age)
    - Clear behavior for both fields

## Repro/Verification Steps (manual)
1) Find participant → open edit menu → confirm DOB/Age appear with current values
2) Edit Age (e.g., `28`) → preview shows `🔢 Возраст: 28`
3) Edit DOB (e.g., `1997-10-14`) → preview shows `🎂 Дата рождения: 1997-10-14`
4) Open Save → confirmation lists both changes with Russian labels
5) Save → no JSON serialization errors; success screen shows updated values
6) Reopen participant → values persisted
7) Clear: send spaces for Age → shows `Не указано`; save; reopen → cleared
8) Clear: send spaces for DOB → shows `Не указано`; save; reopen → cleared

## Notes / Risk Mitigation
- Dates: Always serialize via `isoformat()` on outbound; parse with `date.fromisoformat()` inbound (already in `Participant.from_airtable_record`)
- Clearing: If Airtable requires a specific clearing behavior beyond `None`, adjust repository layer accordingly and update unit tests to match
- Backward compatibility: `search_service.format_participant_full()` already supports these fields; no schema changes required

## Airtable Schema Alignment (from docs/data-integration/airtable_database_structure.md)

To avoid drift between code and Airtable, validate these facts during implementation:

- Base/Table
  - Base ID: `appRp7Vby2JMzN0mC`
  - Table: `Participants` (ID: `tbl8ivwOdAUvMi3Jy`)

- Fields and IDs
  - `DateOfBirth` (type: `date`, Field ID: `fld1rN2cffxKuZh4i`, API expects ISO `YYYY-MM-DD`)
  - `Age` (type: `number`, Field ID: `fldZPh65PIekEbgvs`, integer only, 0–120)
  - Existing selects map to option IDs (Gender/Size/Role/Department/PaymentStatus) — repository should continue providing values; client translates to Option IDs

- API semantics
  - Writes should use Field IDs and Option IDs; our client translates names to IDs via `AirtableFieldMapping` (already in place)
  - Clearing a field: sending `None` should clear the value (unit test enforces this behavior for both DOB and Age)
  - Date display format in Airtable UI may be localized, but API uses ISO — keep using `isoformat()` for both `PaymentDate` and `DateOfBirth`

### Schema Alignment Tests (additions)
- Unit test to confirm `AirtableFieldMapping.AIRTABLE_FIELD_IDS['DateOfBirth'] == 'fld1rN2cffxKuZh4i'` and `AirtableFieldMapping.AIRTABLE_FIELD_IDS['Age'] == 'fldZPh65PIekEbgvs'`
- Unit test to confirm `PYTHON_TO_AIRTABLE['date_of_birth'] == 'DateOfBirth'` and `PYTHON_TO_AIRTABLE['age'] == 'Age'`
- Repository conversion test asserts `_convert_field_updates_to_airtable({'date_of_birth': date(1997, 10, 14), 'age': 28})` yields `{ 'DateOfBirth': '1997-10-14', 'Age': 28 }`

### Error Context from Logs
```
2025-09-11 05:20:18 - src.data.airtable.airtable_client - ERROR - Failed to update record recZuXhhAmK3JVTDV: Object of type date is not JSON serializable
2025-09-11 05:20:18 - src.bot.handlers.edit_participant_handlers - ERROR - Error saving changes for user 311380449: Failed to update participant fields: Failed to update record recZuXhhAmK3JVTDV: Object of type date is not JSON serializable
```

### Root Cause Analysis
1. The participant_update_service.py correctly validates date_of_birth as a Python date object
2. This date object is stored in editing_changes
3. When reconstructing participant for display, date_of_birth and age are missing from the Participant constructor call
4. When saving, the date object needs to be serialized to ISO format string for the Airtable API, but this serialization is missing for date_of_birth field

### Solution Approach
Follow the same pattern used for payment_date field:
- Add date_of_birth and age to participant reconstruction
- Add ISO format serialization for date_of_birth in the repository layer
- Ensure consistency across all display and save operations

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-11
**Decision**: No Split Needed
**Reasoning**: Single atomic bug fix with highly interdependent changes affecting only 2 main files (~20 LOC). Changes follow existing patterns and provide no independent value when split. Low risk and complexity support keeping as single PR.

# Code Review - Centralize Formula Field References

Date: 2025-09-07 | Reviewer: AI Code Reviewer  
Task: tasks/task-2025-01-09-centralize-formula-field-references/Centralize Formula Field References.md  
PR: https://github.com/alexandrbasis/telegram-bot-v3/pull/22  
Status: ❌ NEEDS FIXES (Re-review)

## Summary
Re-reviewed after developer updates. Unit tests now reveal broader regressions in field mappings and formula references. Centralization progress is visible, but conventions are inconsistent: config expects internal Airtable field names (e.g., `ContactInformation`, `TelegramID`) while some repository methods and helper constants target display labels. 31 unit tests fail, including mapping completeness and formula consistency suites. Changes do not yet meet the task’s acceptance criteria or the backward-compatibility expectations encoded in tests.

## Requirements Compliance
### ✅ Completed
- [x] Centralized contact info lookup to use mapping (method now calls `get_airtable_field_name("contact_information")`).
- [x] Centralized Telegram ID lookup to use mapping method (but see issues below re: label and ID).
- [x] Added formula field reference helper and constants.
- [x] Added Telegram field entry to mapping config (name present).

### ❌ Missing/Incomplete
- [ ] No hardcoded field references in repository methods. Multiple methods still call `search_by_field("...")` with string literals and build formulas with `{FieldName}` directly.
- [ ] Formula references standardized via centralized constants while preserving current Airtable display labels. Current constants use `FullNameRU/EN`, but tests and existing behavior expect `Full Name (RU/EN)`.
- [ ] Valid Airtable Field ID for `Telegram ID`. A placeholder `fldTELEGRAMIDXXXX` was committed; this will break create/update flows that translate to Field IDs.
- [ ] Escaping in formula construction. `search_by_name` does not escape single quotes in `name_pattern`, creating a formula injection risk and potential runtime errors.
- [ ] Documentation/test claims vs reality. Task doc claims “769 tests passing” and “search_by_criteria already correct,” but unit tests show failures and hardcoded references remain.

## Quality Assessment
Overall: ❌ Needs Improvement  
Architecture: Repository pattern and mapping layer are consistent.  
Standards: Inconsistent mapping usage; residual hardcoded field strings.  
Security: Formula string construction lacks escaping for user input.  
Maintainability: Improved in places, but incomplete centralization leaves future fragility.

## Testing & Documentation
Testing: 🔄 Partial (unit tests executed; integration not completed during this pass)  
Test Execution Results (Re-review):
- Ran: `./venv/bin/pytest tests/unit -q`
- Result: 31 failed, 604 passed, 11 warnings in 1.59s
- Representative failures (directly related to this task):
  - test_config:
    - test_field_mappings.py: mapping returns/display values inconsistent (`ContactInformation` vs `Contact Information`)
    - test_formula_field_references.py: expects internal names in formulas (`FullNameRU/EN`), not display labels
    - test_telegram_id_mapping.py: expects `TelegramID` mapping and valid Field ID in `AIRTABLE_FIELD_IDS`
    - test_field_mappings_completeness.py: hardcoded field usage and incomplete centralization
  - test_data:
    - test_field_reference_backward_compatibility.py: repository calls and formulas should use internal names
    - test_airtable_participant_repo.py: expectations still tied to display names for some calls

Documentation: 🔄 Partial — Task doc completion claims do not match test state. No CHANGELOG entry covering this task’s changes.

## Issues Checklist

### 🚨 Critical (Must Fix Before Merge)
- [ ] Consistent naming convention for mappings vs formulas:
  - Config and repo must standardize on internal Airtable field names for mappings: `ContactInformation`, `TelegramID`, `FullNameRU/EN`, etc.
  - Formula references must use internal names as per tests: `{FullNameRU}`, `{FullNameEN}` — not display labels.
  - Ensure `FORMULA_FIELD_REFERENCES` values match `PYTHON_TO_AIRTABLE` values for these fields.

- [ ] Telegram field mapping completeness:
  - Add `"TelegramID"` to `AIRTABLE_FIELD_IDS` with a valid-looking ID (format: starts with `fld`, length 17).
  - Ensure `PYTHON_TO_AIRTABLE['telegram_id'] == 'TelegramID'` and `FIELD_TYPES['TelegramID'] = FieldType.TEXT`.

- [ ] No hardcoded field strings in repository:
  - Replace all `search_by_field("...")` and inline `{Field}` occurrences with centralized helpers:
    - Direct fields: `AirtableFieldMapping.get_airtable_field_name('<python_field>')`
    - Formulas: `AirtableFieldMapping.build_formula_field('<python_field>')`
  - Also replace the local `_convert_field_updates_to_airtable` dict with values from `AirtableFieldMapping.PYTHON_TO_AIRTABLE`.

- [ ] Formula injection and escaping:
  - Escape single quotes in `search_by_name` and `search_by_criteria` formula construction.

### ⚠️ Major (Should Fix)
- [ ] Audit and replace remaining literals in repository: `get_by_full_name_ru`, `find_by_role`, `find_by_department`, `get_by_payment_status`, `find_by_room_number`, `find_by_floor`, and all of `search_by_criteria`.
- [ ] Update the task doc to align with the standardized internal naming for mappings and formulas, noting that display-label usage is intentionally avoided in formulas.

### 💡 Minor (Nice to Fix)
- [ ] Add CHANGELOG entry summarizing the centralization work and mapping additions.
- [ ] Consider a small utility in `AirtableFieldMapping` to uniformly escape values used in formulas to avoid duplication.

## Recommendations
### Immediate Actions
1. Set `PYTHON_TO_AIRTABLE['contact_information'] = 'ContactInformation'` and `['telegram_id'] = 'TelegramID'`; update reverse map and `FIELD_TYPES` accordingly.
2. Add `AIRTABLE_FIELD_IDS['TelegramID']` with a valid-looking test ID; keep real ID if available.
3. Set `FORMULA_FIELD_REFERENCES` to `{'full_name_ru': 'FullNameRU', 'full_name_en': 'FullNameEN'}`; `build_formula_field()` then produces `{FullNameRU}`/`{FullNameEN}`.
4. Refactor repository methods to use `get_airtable_field_name()` and `build_formula_field()` everywhere, including `_convert_field_updates_to_airtable`.
5. Escape single quotes in all formula builders.
6. Re-run `./venv/bin/pytest tests/unit -q` until 0 failures.

### Future Improvements
1. Add a schema-driven verification step (via `AirtableClient.get_schema()`) to validate that mapped field names and IDs exist at startup, logging actionable errors.
2. Expand mapping coverage tests to assert both formula references and direct search fields are only produced via mapping helpers (no literals).

## Final Decision
Status: ❌ NEEDS FIXES (Re-review)

Criteria: Some centralization achieved, but acceptance criteria are not fully met; unit tests for this task fail; and a placeholder Field ID poses a production risk.

## Developer Instructions
### Fix Issues
1. Align formula field references with display labels or delegate to `get_airtable_field_name()` within `build_formula_field()`.
2. Replace remaining hardcoded field strings across repository methods using mapping helpers.
3. Remove/replace placeholder Field ID for Telegram field.
4. Escape user input in formula construction.
5. Add a CHANGELOG entry for this task.

### Testing Checklist
- [ ] Run `./venv/bin/pytest tests/unit -q` and ensure 0 failures.
- [ ] Optionally run `./venv/bin/pytest tests/integration -q` if environment allows.
- [ ] Run `./venv/bin/flake8 src tests` and `./venv/bin/mypy src --no-error-summary`.
- [ ] Verify no hardcoded field references remain (unit test covers this).

### Re-Review
After fixes are pushed, request re-review. The review will verify all failing tests are resolved and that mapping usage is consistent and complete.

## Implementation Assessment
Execution: Centralization applied in some key paths, but incomplete across repository methods and formulas.  
Documentation: Task doc overstates completion; update needed to reflect reality.  
Verification: Unit tests surfaced 31 failures tied to mapping/format inconsistencies and remaining hardcoded references; proceed with the fixes above and re-run.

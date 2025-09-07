# Code Review - Centralize Formula Field References

Date: 2025-09-07 | Reviewer: AI Code Reviewer  
Task: tasks/task-2025-01-09-centralize-formula-field-references/Centralize Formula Field References.md  
PR: https://github.com/alexandrbasis/telegram-bot-v3/pull/22  
Status: ❌ NEEDS FIXES

## Summary
The implementation partially centralizes Airtable field references and introduces formula field reference helpers. However, several repository methods still use hardcoded field names, the formula references were switched to non‑existent “internal” names (e.g., `{FullNameRU}`) instead of Airtable display labels used throughout the codebase and tests (e.g., `{Full Name (RU)}`), and a placeholder Field ID was committed for the Telegram field. Unit tests surface these gaps: 5 failures tied directly to this task’s changes and acceptance criteria.

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
Test Execution Results:
- Ran: `./venv/bin/pytest tests/unit -q`
- Result: 5 failed, 630 passed, 11 warnings in 1.39s
- Failures directly related to this task:
  - tests/unit/test_config/test_field_mappings_completeness.py::TestFieldMappingsCompleteness::test_no_hardcoded_field_references_in_repository
  - tests/unit/test_config/test_field_mappings_completeness.py::TestFieldMappingsCompleteness::test_field_id_mapping_completeness
  - tests/unit/test_data/test_airtable/test_airtable_participant_repo.py::TestAirtableParticipantRepositorySearch::test_find_by_contact_information_success
  - tests/unit/test_data/test_airtable/test_airtable_participant_repo.py::TestAirtableParticipantRepositorySearch::test_find_by_telegram_id_success
  - tests/unit/test_data/test_airtable/test_airtable_participant_repo.py::TestAirtableParticipantRepositorySearch::test_search_by_name_success

Documentation: 🔄 Partial — Task doc completion claims do not match test state. No CHANGELOG entry covering this task’s changes.

## Issues Checklist

### 🚨 Critical (Must Fix Before Merge)
- [ ] Hardcoded field references remain in repository methods → Violates acceptance criteria and failing completeness tests.  
  Solution: Replace all `search_by_field("...")` string literals with `AirtableFieldMapping.get_airtable_field_name(<python_field>)` and replace in‑formula `{Field}` usages with `AirtableFieldMapping.build_formula_field(<python_field>)`.  
  Files/lines (examples from unit test output):
  - src/data/airtable/airtable_participant_repo.py:329 (`FullNameRU`), 547-549 (`PaymentStatus`), 728-731 (`Role`), 771-774 (`Department`), 1101-1105 (`RoomNumber`), 1146-1149 (`Floor`).

- [ ] Formula field references use non‑existent names (`{FullNameRU}`, `{FullNameEN}`) instead of current display labels (`{Full Name (RU)}`, `{Full Name (EN)}`) → Breaks tests and likely Airtable formulas if labels differ.  
  Solution: Align `FORMULA_FIELD_REFERENCES` to the Airtable display labels currently in use (e.g., `"full_name_ru": "Full Name (RU)"`). Alternatively, have `build_formula_field()` resolve via `get_airtable_field_name()` so there’s a single source of truth.

- [ ] Placeholder Field ID for Telegram field (`fldTELEGRAMIDXXXX`) committed → Will cause create/update translation to use an invalid Field ID.  
  Solution: Replace with the real Airtable Field ID from the base schema. Until known, remove the placeholder to force name fallback in `translate_fields_to_ids()`.

- [ ] Unescaped user input in `search_by_name` formula → Risk of formula breakage with names containing single quotes (e.g., O'Connor).  
  Solution: Escape single quotes in `name_pattern` (replace `'` with `''`) before interpolating into the formula.

### ⚠️ Major (Should Fix)
- [ ] Ensure all search helpers consistently use centralized mapping, including: `get_by_full_name_ru`, `find_by_role`, `find_by_department`, `get_by_payment_status`, `find_by_room_number`, `find_by_floor`, and `search_by_criteria` formula construction.
- [ ] Reconcile tests and task doc: Either update code to keep current display label format or adjust test expectations if the Airtable schema has actually changed. Given the “backward compatibility” constraint, prefer fixing the code to keep existing labels and centralize via mappings.

### 💡 Minor (Nice to Fix)
- [ ] Add CHANGELOG entry summarizing the centralization work and mapping additions.
- [ ] Consider a small utility in `AirtableFieldMapping` to uniformly escape values used in formulas to avoid duplication.

## Recommendations
### Immediate Actions
1. Update `AirtableFieldMapping.FORMULA_FIELD_REFERENCES` to use display labels matching the current Airtable schema, or delegate to `get_airtable_field_name()` inside `build_formula_field()`.
2. Replace all hardcoded field strings in repository methods with centralized mapping calls (both direct field searches and in-formula references).
3. Remove the Telegram placeholder Field ID or replace with the real one from the base. Verify `translate_fields_to_ids()` falls back gracefully when ID is absent.
4. Escape `name_pattern` in `search_by_name` to handle single quotes safely.
5. Re-run unit tests to confirm fixes (target: 0 failures). Optionally run integration tests afterward.

### Future Improvements
1. Add a schema-driven verification step (via `AirtableClient.get_schema()`) to validate that mapped field names and IDs exist at startup, logging actionable errors.
2. Expand mapping coverage tests to assert both formula references and direct search fields are only produced via mapping helpers (no literals).

## Final Decision
Status: ❌ NEEDS FIXES

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
Verification: Unit tests run surfaced 5 failures directly tied to this task; proceed with the fixes above.


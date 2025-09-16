# Create Airtable Formula Escaping Helper

## Summary
Formula-building logic manually escapes quotes across multiple methods. Consolidate escaping and quoting into a dedicated helper to reduce duplication and prevent inconsistent behavior.

## References
- `src/data/airtable/airtable_participant_repo.py`
- `src/config/field_mappings.py`

## Goals
- Implement a reusable utility for quoting/escaping Airtable formula values.
- Replace ad-hoc escaping in repository methods with the helper.
- Add tests covering edge cases (quotes, special characters, enums).

## Acceptance Criteria
- All formula-building code paths use the centralized helper.
- Tests cover string inputs with quotes and other special characters.
- No regressions in existing search behavior.

## Change Log
- Added `formula_utils` module with `escape_formula_value` and `prepare_formula_value` helpers and wired repository formula builders to use them.
- Added dedicated tests for the new helpers and updated name/criteria searches to rely on centralized escaping.

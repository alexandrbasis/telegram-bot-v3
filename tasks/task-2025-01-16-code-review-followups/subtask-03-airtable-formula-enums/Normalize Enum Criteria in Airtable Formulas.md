# Normalize Enum Criteria in Airtable Formulas

## Summary
`search_by_criteria` constructs Airtable formulas without quoting enum values, yielding expressions such as `{Role} = Role.CANDIDATE`. Convert enum inputs to their string values and ensure proper escaping before injecting into formulas.

## References
- `src/data/airtable/airtable_participant_repo.py:440-467`
- `tests/unit/test_data/test_airtable/test_formula_consistency.py`

## Goals
- Coerce enums to strings and quote them consistently when building formulas.
- Centralize value escaping to guard against injection or syntax errors.
- Extend tests to cover enum inputs for all supported fields (role, department, gender, payment status).

## Acceptance Criteria
- Airtable search succeeds when criteria contain enum members.
- Tests fail if formulas render raw enum representations.
- Formula generation logic remains backward compatible for string inputs.

## Change Log
- Normalized formula comparisons to coerce Enum inputs into their string values before quoting, preventing raw `EnumName.MEMBER` leakage into Airtable filters.
- Added parameterized tests covering role, department, gender, and payment status criteria to lock the quoting behaviour.

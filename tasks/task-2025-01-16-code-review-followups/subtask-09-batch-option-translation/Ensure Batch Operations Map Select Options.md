# Ensure Batch Operations Map Select Options

## Summary
Bulk create/update helpers bypass `_translate_fields_for_api`, risking incorrect option IDs for select fields if Airtable display names change. Align batch payload preparation with the single-record path.

## References
- `src/data/airtable/airtable_client.py:341-386`
- `src/data/airtable/airtable_participant_repo.py:820-876`

## Goals
- Share the same field/option translation logic between single and batch operations.
- Confirm select fields resolve to the correct option IDs when using batch APIs.
- Enhance tests to cover select-field updates in bulk scenarios.

## Acceptance Criteria
- Batch operations translate select fields identically to single-record operations.
- Tests fail if select options are sent with display values instead of option IDs.
- No regressions in existing bulk behavior (still respects Airtable limits).

## Change Log
- Updated Airtable client bulk create/update to reuse `_translate_fields_for_api` so select options map to IDs consistently.
- Extended bulk operation tests to assert translated payloads are sent to Airtable.

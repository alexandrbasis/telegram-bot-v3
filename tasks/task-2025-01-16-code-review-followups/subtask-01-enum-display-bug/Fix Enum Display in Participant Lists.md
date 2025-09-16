# Fix Enum Display in Participant Lists

## Summary
Participant list responses currently render enum objects with their full Python representation (e.g., `Department.CHAPEL`). Update the formatting logic so Telegram messages show localized, human-readable values.

## References
- `src/services/participant_list_service.py:136-170`

## Goals
- Use the enum value (or a localized label) instead of `str(enum)` when building list entries.
- Ensure Markdown escaping still applies correctly after the change.
- Add coverage to confirm enums render as expected for departments and other fields.

## Acceptance Criteria
- Team/candidate list outputs show values like `Chapel` (and localized Russian label if desired) with no `EnumName.VALUE` artifacts.
- Tests fail if enum rendering regresses.
- No Markdown formatting regressions in bot messages.


# Tres Dias Telegram Bot v3 – Code Review

## Summary
The codebase is well-structured with clear layering (bot/services/data) and solid test coverage. Most modules are readable and provide defensive logging. I focused on correctness, maintainability, and UX polish. Below are the key issues and suggested improvements.

## Critical / High Priority Findings
- **Enum values leak into UI lists** (`src/services/participant_list_service.py:160`): department names are rendered with `str(participant.department)` producing strings like `Department.CHAPEL`. Use the enum value (`participant.department.value`) and localize where needed. This is user-facing and confuses admins viewing team lists.
- **Blocking call on active event loop** (`src/services/participant_export_service.py:124-134`): `export_to_csv` calls `loop.run_until_complete(...)` when a loop is already running, which raises `RuntimeError` under PTB async contexts. Prefer `asyncio.run` only when no loop, otherwise expose/await the coroutine or use `asyncio.create_task`.
- **Airtable formula building fails for enums** (`src/data/airtable/airtable_participant_repo.py:440-467`): when callers pass enums (Role/Department/Gender/PaymentStatus), the else-branch emits `{Field} = Role.CANDIDATE` without quotes, yielding invalid formulas. Normalize to strings and quote them before building the formula.

## Medium Priority / UX & Reliability
- **Search result formatting mixes English fallbacks** (`src/services/search_service.py:135-159`): labels like `Floor`, `Room`, `Date of Birth`, `Age`, and `N/A`/`years` appear in English inside otherwise Russian messages. Localizing these strings will improve user trust and polish.
- **Heavy `list_all()` usage per search** (`src/data/airtable/airtable_participant_repo.py:1093-1112`): enhanced name search pulls the entire participant set from Airtable for every query. Consider caching or delegating filtering to Airtable to avoid hitting API limits as the roster grows.
- **Repeated settings reloads** (e.g., `src/bot/handlers/search_handlers.py:58-66`, `src/bot/handlers/edit_participant_handlers.py:34-52`): `get_user_interaction_logger()` resets global settings on each invocation to pick up env changes. This re-reads `.env` and rebuilds configs frequently. Capture the setting once per process or watch for env changes another way to avoid unnecessary I/O.

## Backend Improvement Ideas
- **Reuse Airtable client instances** (`src/services/service_factory.py:18-45`): every factory call builds a new `AirtableClient` and rate limiter. Singleton or cached instances would cut session churn and help with rate limit tracking across handlers.
- **Tighten formula builders**: `search_by_criteria` and related helpers manually escape quotes. A small utility to quote/escape values in one place would reduce risk of formula injection and bugs.
- **Batch operations translation**: bulk create/update currently bypass `_translate_fields_for_api`. Ensure option ID translation happens for batch payloads as well so select fields remain stable if Airtable display names change.

## UI / Conversation Flow Suggestions
- **Consistent localization**: mirror the Russian tone used elsewhere for fields like floor/room, ages, and error hints in `format_participant_result` and similar helpers.
- **Pagination UX**: when offsets overshoot the dataset, the current clamp drops users to a single-item page. Consider snapping to the previous full page to keep context.
- **Admin logging toggles**: exposing `/logging` admin commands to toggle user interaction logging at runtime (instead of env reloads) would be more controllable and avoids `reset_settings()` churn.

## Testing & Tooling Notes
- Add regression tests for the enum-handling path in `search_by_criteria` to guard the quoting bug.
- Consider an async test covering `ParticipantExportService.export_to_csv` to confirm it works under running event loops.
- Running `mypy` shows a few opportunities to tighten type hints around optional logger returns (e.g., `_log_missing`).

## Next Steps
1. Patch the three high-priority issues above and add targeted tests.
2. Sweep localization for mixed-language strings in search results.
3. Evaluate caching/reuse strategy for Airtable client and settings, aligning with expected load.

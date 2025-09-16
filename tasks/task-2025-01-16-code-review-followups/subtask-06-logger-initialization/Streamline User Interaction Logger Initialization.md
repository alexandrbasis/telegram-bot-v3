# Streamline User Interaction Logger Initialization

## Summary
`get_user_interaction_logger()` resets global settings on every call to pick up environment changes, triggering repeated `.env` parsing and config rebuilding. Refine the initialization flow to avoid unnecessary churn.

## References
- `src/bot/handlers/search_handlers.py:46-68`
- `src/bot/handlers/edit_participant_handlers.py:24-56`
- `src/config/settings.py`

## Goals
- Eliminate repeated `reset_settings()` calls during normal operation.
- Provide a predictable way to refresh logging configuration when needed.
- Add targeted tests to ensure logger initialization respects configuration flags.

## Acceptance Criteria
- Logger helper initializes once per process (or per explicit refresh) without redundant `.env` loads.
- Behavior around `ENABLE_USER_INTERACTION_LOGGING` remains correct.
- Tests cover both enabled/disabled scenarios.

## Change Log
- Added a cached logger provider in `user_interaction_logger` that consults settings without calling `reset_settings()` on every request and exposes an explicit refresh hook.
- Updated search and edit handlers to use the provider instead of reloading settings per call, and extended service/handler tests to cover caching and disabled scenarios.

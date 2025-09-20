# Add Admin Logging Toggle Command

## Summary
Provide administrators with a bot command to enable/disable user interaction logging at runtime, avoiding the need to edit environment variables and restart the bot.

## References
- `src/bot/handlers/search_handlers.py`
- `src/bot/handlers/edit_participant_handlers.py`
- `src/services/user_interaction_logger.py`

## Goals
- Add a protected admin command (e.g., `/logging on|off`) that updates logging configuration safely.
- Persist the new state for the running process and surface confirmation to the admin.
- Ensure the setting integrates with the streamlined logger initialization.

## Acceptance Criteria
- Admins can toggle logging without restarts; non-admins are denied.
- Logging state reflects the toggle immediately across handlers.
- Tests cover toggling behavior and permission checks.

## Change Log
- Added `/logging` admin command with runtime overrides in `user_interaction_logger`, allowing logging to be toggled without restarts.
- Registered command in the application and conversation fallback, including tests for permission checks and state changes.

# Changelog - 2025-09-30

All notable changes made on 2025-09-30 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Changes Made

### Added
- Admin Commands for Notification Configuration with runtime reconfiguration support (`src/bot/handlers/notification_admin_handlers.py`, `src/main.py:26-30,172-244`)
  - `/notifications` command for viewing status and toggling notifications on/off with immediate scheduling/unscheduling
  - `/set_notification_time HH:MM [timezone]` command for configuring delivery time and timezone with live rescheduling
  - `/test_stats` command for immediate test notification delivery to verify configuration
  - All commands protected by admin-only access using `auth_utils.is_admin_user()` permission validation
  - Russian-localized messages with emoji indicators for consistency with bot UI patterns
  - Comprehensive input validation for time format (HH:MM) and timezone (pytz validation) with helpful error messages
- Post_init Scheduler Integration for improved lifecycle management (`src/main.py:188-244`)
  - Refactored notification scheduler to use `Application.post_init` pattern instead of inline initialization
  - Scheduler instance stored in `bot_data` for runtime access by admin command handlers
  - Conditional scheduling based on feature flag (`settings.notification.daily_stats_enabled`)
  - Cleaner separation of concerns with proper initialization timing after bot startup
  - Graceful error handling ensuring bot continues operation even if notification initialization fails
- Runtime Notification Reconfiguration with immediate effect (`src/services/notification_scheduler.py:155-174`, `src/bot/handlers/notification_admin_handlers.py:83-266`)
  - `reschedule_notification()` method in NotificationScheduler enabling dynamic job rescheduling
  - Enable/disable commands immediately schedule or remove jobs without requiring bot restart
  - Time configuration changes instantly reschedule the notification job with updated settings
  - Administrators can test and adjust notification settings in real-time for operational flexibility

### Fixed
- Test isolation issues in main application tests (`tests/unit/test_main.py:18,283,383,420`)
  - Added `reset_settings()` calls in test setup to prevent test dependencies from cached settings
  - Updated test expectations to match new scheduler behavior (created but conditionally scheduled)
  - Fixed flaky tests caused by global settings state persisting across test runs

## Merge Details

### Admin Commands Integration (AGB-80)
- **PR**: [#76](https://github.com/alexandrbasis/telegram-bot-v3/pull/76)
- **Branch**: feature/AGB-80-admin-commands-integration
- **Status**: In Review
- **Test Results**: 33 notification tests passing (100% pass rate)
  - 16 unit tests for admin command handlers
  - 4 unit tests for post_init integration
  - 4 integration tests for command registration
  - 9 additional tests for runtime reconfiguration and test isolation fixes
- **Code Quality**: All checks passing (black, isort, flake8, mypy)
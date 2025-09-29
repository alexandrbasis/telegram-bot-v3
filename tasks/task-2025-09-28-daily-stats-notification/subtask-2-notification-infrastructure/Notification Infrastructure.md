# Task: Notification Infrastructure
**Created**: 2025-09-28 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement core notification infrastructure including configuration, scheduling, and delivery services to enable automated daily statistics reporting with proper timezone support and admin permissions.

### Use Cases
1. **Configurable Notification Settings**: Administrators can configure:
   - Enable/disable daily statistics notifications
   - Set notification delivery time with timezone support
   - Specify admin user for notification delivery
   - All settings validated and persisted through bot lifecycle

2. **Reliable Scheduling Infrastructure**: System provides robust scheduling:
   - JobQueue-based scheduling integrated with Telegram bot lifecycle
   - Timezone-aware scheduling with proper conversion handling
   - Job persistence across bot restarts for reliability
   - Error handling with exponential backoff retry mechanisms

3. **Professional Notification Delivery**: Service delivers formatted notifications:
   - Russian-localized message formatting for statistics
   - Clean, readable presentation of participant and team counts
   - Delivery to configured admin users with error handling
   - Integration with existing admin permission system

### Success Metrics
- [ ] Notifications are delivered at configured times with timezone accuracy
- [ ] Configuration changes persist across bot restarts
- [ ] Failed notifications are retried with exponential backoff
- [ ] Admin permissions are properly validated for configuration access

### Constraints
- Must integrate with existing bot configuration system and patterns
- Should use telegram.ext.JobQueue for proper bot integration
- Must respect existing admin permission patterns (auth_utils)
- Configuration must be timezone-aware with validation
- Feature must be optional (can be disabled)

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: AGB-79
- **URL**: https://linear.app/alexandrbasis/issue/AGB-79/subtask-2-notification-infrastructure
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Extend configuration system with NotificationSettings dataclass
- [ ] Implement NotificationScheduler using telegram.ext.JobQueue
- [ ] Create DailyNotificationService for formatting and delivery
- [ ] Add timezone support with pytz validation
- [ ] Implement job persistence and error handling

## Implementation Steps & Change Log
- [ ] Step 1: Extend Configuration System
  - [ ] Sub-step 1.1: Add NotificationSettings dataclass with timezone support
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/settings.py`
    - **Accept**: NotificationSettings dataclass with daily_stats_enabled, notification_time, timezone, admin_user_id fields and proper validation
    - **Tests**: `tests/unit/test_config/test_settings.py` - Test time parsing, timezone validation, admin ID validation
    - **Done**: Configuration validates time format (HH:MM), timezone (pytz), admin ID as integer, and feature flag
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Create JobQueue-based Scheduling Infrastructure
  - [ ] Sub-step 2.1: Implement NotificationScheduler using telegram.ext.JobQueue
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/notification_scheduler.py`
    - **Accept**: Scheduler uses Application.job_queue.run_daily(), handles timezone conversion, implements job persistence, includes exponential backoff retry
    - **Tests**: `tests/unit/test_services/test_notification_scheduler.py` - Test JobQueue integration, timezone handling, persistence, retry logic
    - **Done**: Scheduler properly integrates with bot lifecycle, handles errors gracefully, persists across restarts
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Create Notification Service
  - [ ] Sub-step 3.1: Implement notification formatting and delivery
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/daily_notification_service.py`
    - **Accept**: Service formats statistics into Russian message and sends to configured admin
    - **Tests**: `tests/unit/test_services/test_daily_notification_service.py` - Test message formatting, delivery, error handling
    - **Done**: Service formats and delivers notifications with proper error handling
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Configuration validation in tests/unit/test_config/
- [ ] Service tests: Scheduler and notification logic in tests/unit/test_services/
- [ ] Integration tests: JobQueue integration in tests/integration/
- [ ] Timezone tests: Comprehensive timezone handling validation

## Success Criteria
- [ ] All acceptance criteria met
- [ ] Tests pass (100% required)
- [ ] No regressions in existing configuration system
- [ ] JobQueue integration works with bot lifecycle
- [ ] Timezone handling is accurate
- [ ] Code review approved

# Task: Daily Statistics Notification
**Status**: Ready for Implementation

## Tracking & Progress
### Main Linear Issue
- **ID**: AGB-81
- **URL**: https://linear.app/alexandrbasis/issue/AGB-81/daily-statistics-notification-feature-implementation
- **Priority**: High
- **Git Branch**: basisalexandr/agb-81-daily-statistics-notification-feature-implementation

### Sub-tasks
- **AGB-78**: Statistics Collection Service (No dependencies)
- **AGB-79**: Notification Infrastructure (Depends on AGB-78)
- **AGB-80**: Admin Commands Integration (Depends on AGB-78 & AGB-79)

## Primary Objective
Add automated daily statistics notification functionality to provide administrators with a comprehensive overview of participant and team counts by departments, enabling better event management and resource planning.

## Use Cases
1. **Daily Morning Statistics Report**: Bot sends daily notification at a configured morning time with:
   - Total number of candidates/participants
   - Number of teams per department
   - Total number of teams across all departments
   - Clear formatting for easy readability

2. **Configurable Notification Control**: Administrators can enable/disable the daily notifications through bot settings:
   - Setting to enable/disable daily stats notifications
   - Configurable time for notification delivery (default: morning)
   - Option to change notification format or content scope

3. **Automated Reporting**: System automatically generates and sends reports without manual intervention:
   - Runs via scheduled cron job
   - Pulls current data from Airtable
   - Formats data consistently
   - Handles errors gracefully (e.g., API failures, network issues)

## Constraints
- Must integrate with existing bot configuration system
- Should use existing Airtable data access patterns
- Notification timing must be configurable
- Feature must be optional (can be disabled)
- Should follow existing error handling and logging patterns
- Must work with current deployment environment

## Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

## Proposed Test Categories

### Business Logic Tests
- [ ] Statistics calculation service test covering accurate participant count aggregation
- [ ] Department team counting logic test with various team distributions
- [ ] Notification message formatting test with multiple departments and counts
- [ ] Configuration validation test for notification settings (enabled/disabled, timing)

### State Transition Tests
- [ ] Cron job scheduling state management test
- [ ] Configuration update flow test (enable/disable notifications)
- [ ] Error recovery state transitions for failed notifications
- [ ] Notification delivery confirmation state handling

### Error Handling Tests
- [ ] Airtable API failure scenario test during statistics collection
- [ ] Network timeout handling test for data retrieval
- [ ] Invalid configuration values handling test
- [ ] Telegram API failure during notification sending test
- [ ] Cron job failure and retry mechanism test

### Integration Tests
- [ ] End-to-end statistics collection from Airtable integration test
- [ ] Telegram notification delivery integration test
- [ ] Configuration persistence and retrieval integration test
- [ ] Cron job execution with real scheduler integration test

### User Interaction Tests
- [ ] Configuration command processing test for enabling/disabling notifications
- [ ] Notification message formatting and readability test
- [ ] Admin permission validation test for configuration changes
- [ ] Help command integration test for new notification settings

## Test-to-Requirement Mapping
- Daily Morning Statistics Report → Tests: Statistics calculation service, Message formatting, End-to-end Airtable integration, Telegram notification delivery
- Configurable Notification Control → Tests: Configuration validation, Configuration update flow, Configuration persistence, Admin permission validation
- Automated Reporting → Tests: Cron job scheduling, Error recovery states, API failure scenarios, Retry mechanism

## TECHNICAL TASK

### Technical Requirements
- [ ] Create configurable scheduling infrastructure using telegram.ext.JobQueue for proper bot integration
- [ ] Add daily statistics notification settings to configuration system with timezone support
- [ ] Implement efficient statistics collection service with batched Airtable queries and aggregation
- [ ] Create notification formatting service for Russian text with proper department names
- [ ] Add administrative commands for enabling/disabling and configuring notifications
- [ ] Integrate notification delivery with existing admin user permissions using auth_utils
- [ ] Implement comprehensive error handling with exponential backoff and retry mechanisms
- [ ] Add job persistence strategy for reliable operation across bot restarts

### Implementation Steps & Change Log

- [ ] Step 1: Extend Configuration System → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-2-notification-infrastructure/Notification Infrastructure.md`
  - **Description**: Configuration system extension with NotificationSettings, timezone validation, and settings integration
  - **Linear Issue**: AGB-79 - https://linear.app/alexandrbasis/issue/AGB-79/subtask-2-notification-infrastructure
  - **Dependencies**: None - can be started immediately

- [ ] Step 2: Create Statistics Collection Service → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-1-statistics-collection/Statistics Collection Service.md`
  - **Description**: Efficient statistics collection service with Airtable integration and service factory setup
  - **Linear Issue**: AGB-78 - https://linear.app/alexandrbasis/issue/AGB-78/subtask-1-statistics-collection-service
  - **Dependencies**: None - can be developed in parallel with other subtasks

- [ ] Step 3: Create JobQueue-based Scheduling Infrastructure → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-2-notification-infrastructure/Notification Infrastructure.md`
  - **Description**: JobQueue-based scheduler with timezone support and job persistence
  - **Linear Issue**: AGB-79 - https://linear.app/alexandrbasis/issue/AGB-79/subtask-2-notification-infrastructure
  - **Dependencies**: Requires subtask-1 (Statistics Collection) to be completed for integration

- [ ] Step 4: Create Notification Service → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-2-notification-infrastructure/Notification Infrastructure.md`
  - **Description**: Notification formatting and delivery service with Russian localization
  - **Linear Issue**: AGB-79 - https://linear.app/alexandrbasis/issue/AGB-79/subtask-2-notification-infrastructure
  - **Dependencies**: Requires subtask-1 (Statistics Collection) for data integration

- [ ] Step 5: Add Administrative Commands with Permission Integration → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-3-admin-commands-integration/Admin Commands Integration.md`
  - **Description**: Admin commands for notification configuration with auth_utils integration
  - **Linear Issue**: AGB-80 - https://linear.app/alexandrbasis/issue/AGB-80/subtask-3-admin-commands-integration
  - **Dependencies**: Requires subtask-2 (Notification Infrastructure) for configuration and scheduler access

- [ ] Step 6: Integrate Scheduler with Main Application using post_init → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-3-admin-commands-integration/Admin Commands Integration.md`
  - **Description**: Main application integration with post_init scheduler initialization and command registration
  - **Linear Issue**: AGB-80 - https://linear.app/alexandrbasis/issue/AGB-80/subtask-3-admin-commands-integration
  - **Dependencies**: Requires both subtask-1 and subtask-2 to be completed for full integration

### Constraints
- Must integrate with existing bot configuration system
- Should use existing Airtable data access patterns
- Notification timing must be configurable
- Feature must be optional (can be disabled)
- Should follow existing error handling and logging patterns
- Must work with current deployment environment
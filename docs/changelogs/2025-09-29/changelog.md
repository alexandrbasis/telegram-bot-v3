# Changelog - 2025-09-29

All notable changes made on 2025-09-29 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Changes Made

### Added
- Statistics Collection Service with efficient Airtable integration for automated daily reporting (`src/services/statistics_service.py`)
  - Single batched query design minimizing API calls and respecting rate limits (5 requests/second)
  - In-memory aggregation providing <5s execution time for optimal performance
  - Comprehensive error handling with custom StatisticsError for secure data collection
  - Thread-safe, stateless service design following established repository patterns
- DepartmentStatistics Pydantic model with validation and serialization (`src/models/department_statistics.py`)
  - Structured data representation with participants_by_department mapping and total counts
  - Built-in validation for non-negative values and collection timestamp tracking
  - Pydantic-based serialization methods (model_dump, model_dump_json) for data exchange
- Service factory integration with proper dependency injection (`src/services/service_factory.py:get_statistics_service()`)
  - Reuses existing participant repository infrastructure for consistency
  - Follows established factory patterns for service creation and caching
- Notification Infrastructure for automated daily statistics reporting with timezone support (`src/services/notification_scheduler.py`, `src/services/daily_notification_service.py`)
  - NotificationSettings configuration with feature flag, scheduled time (HH:MM), timezone validation (pytz), and admin user ID (`src/config/settings.py:565-661`)
  - NotificationScheduler using telegram.ext.JobQueue for reliable timezone-aware scheduling with job persistence (`src/services/notification_scheduler.py:1-190`)
  - DailyNotificationService with Russian-localized message formatting using centralized department translations (`src/services/daily_notification_service.py:1-133`)
  - Main application integration with feature flag check and graceful error handling (`src/main.py:29-340`)
  - Comprehensive error handling with NotificationError custom exception and graceful degradation
  - 22 new tests covering configuration validation, scheduler integration, and notification delivery (1652 total tests passing)

### Changed
- Enhanced model exports to include DepartmentStatistics in package interface (`src/models/__init__.py`)
- Updated base dependencies to include timezone support library (`requirements/base.txt:7`)
  - Added pytz>=2025.1 for timezone-aware notification scheduling
  - Added types-pytz>=2024.1.0 for mypy type checking support

### Fixed
- Critical performance optimization resolving Airtable API pagination limitations (`src/services/statistics_service.py:45-67`)
  - Replaced faulty offset-based pagination with single-fetch approach preventing memory accumulation
  - Eliminated exponential performance degradation with large datasets
- Security improvements preventing information disclosure in error handling (`src/services/statistics_service.py:89-102`)
  - Masked sensitive error details with debug-level logging for production safety
  - Implemented robust isinstance() type checking replacing fragile hasattr() calls
- Code quality fixes addressing all PR review feedback (`src/services/statistics_service.py`, `src/models/department_statistics.py`)
  - Applied Black formatting and resolved all linting violations (line length, unused imports)
  - Enhanced error handling using try/except NameError instead of locals() inspection
  - Updated field documentation to accurately reflect data content and behavior
- Notification service department name corrections (`src/services/daily_notification_service.py`)
  - Replaced hardcoded incorrect department names with centralized department_to_russian() utility
  - Fixed DailyNotificationService to use proper Department enum values (ROE, Chapel, Kitchen, Decoration)
  - Ensured consistent Russian translations across all notification messages
- Type safety improvements for notification infrastructure (`src/services/notification_scheduler.py`, `src/services/daily_notification_service.py`)
  - Added types-pytz type stubs for mypy compliance
  - Implemented null-safety checks for optional configuration values
  - Resolved all mypy type checking errors (zero type errors)
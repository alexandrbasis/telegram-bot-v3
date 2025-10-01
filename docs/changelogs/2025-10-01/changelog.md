# Changelog - 2025-10-01

All notable changes made on 2025-10-01 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Changes Made

### Changed
- Daily statistics notification message format enhanced with candidate count display and improved formatting (`src/services/daily_notification_service.py:46-76`, `src/models/department_statistics.py:42-44,62-74`, `src/services/statistics_service.py:79-89,118-129`)
  - Added separate candidate count line showing "Всего кандидатов" with count of participants where role=CANDIDATE
  - Renamed "Всего команд" to "Все члены команды" for clearer team member distinction
  - Updated message header from "Ежедневная статистика участников" to "Статистика участников DD.MM.YYYY" format (e.g., "01.10.2025")
  - Enhanced department breakdown indentation (2 spaces for "По отделам:", 4 spaces for department items) to visually group under team members
  - Mathematical validation: total_participants = total_candidates + total_team_members across all calculations
  - Statistics collection service now separately counts candidates (role=CANDIDATE) and team members (role=TEAM)
  - Logging updated to include candidate count in statistics summary messages

## PR Details

### Notification Message Format Enhancement (AGB-82)
- **PR**: [#77](https://github.com/alexandrbasis/telegram-bot-v3/pull/77) - ✅ MERGED
- **Branch**: basisalexandr/agb-82-notification-message-format-enhancement-add-candidate-count (deleted after merge)
- **Status**: ✅ Merged to main
- **Created**: 2025-10-01
- **Merged**: 2025-10-01T11:53:15Z
- **Merge SHA**: 89005374c75af1fc48c218d64f0b46225dce0fee (short: 8900537)
- **Linear Issue**: [AGB-82](https://linear.app/alexandrbasis/issue/AGB-82/notification-message-format-enhancement-add-candidate-count-display) - Status: ✅ Done
- **Test Results**: 1680 tests passing, 9 skipped (100% pass rate)
  - 3 new unit tests for model validation and field addition
  - 4 new unit tests for candidate counting logic covering edge cases
  - Updated message formatting tests verifying all format elements
  - Integration tests validating end-to-end statistics flow
- **Code Quality**: All quality gates passing
  - Type Check (mypy): 0 errors, 0 warnings
  - Format Check (black, isort): Already formatted
  - Linting (flake8): 0 issues
  - Test Coverage: 90%+ on all modified files (department_statistics.py: 95%, statistics_service.py: 92%, daily_notification_service.py: 94%)

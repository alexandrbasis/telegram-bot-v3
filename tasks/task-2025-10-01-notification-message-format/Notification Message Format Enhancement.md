# Task: Notification Message Format Enhancement
**Status**: Ready for Review
**Started**: 2025-10-01T12:00:00Z
**Completed**: 2025-10-01T16:00:00Z

## Tracking & Progress
### Linear Issue
- **ID**: AGB-82
- **URL**: https://linear.app/alexandrbasis/issue/AGB-82/notification-message-format-enhancement-add-candidate-count-display
- **Branch**: basisalexandr/agb-82-notification-message-format-enhancement-add-candidate-count
- **Status**: Backlog

### PR Details
- **Branch**: basisalexandr/agb-82-notification-message-format-enhancement-add-candidate-count
- **PR URL**: [Will be added during implementation]
- **Status**: Not created yet

## Business Requirements

## Primary Objective
Improve daily statistics notification message format to separately display candidates and team members with clearer Russian labels.

## Use Cases

### Use Case 1: Admin receives daily statistics notification
**Current behavior:**
```
📊 Ежедневная статистика участников

👥 Всего участников: 135
👫 Всего команд: 106

По отделам:
  • Не указано: 76 чел.
  • Ректорат: 1 чел.
  • Кухня: 9 чел.
  ...
```

**Expected behavior:**
```
📊 Статистика участников 01.10.2025

👥 Всего участников: 135
👤 Всего кандидатов: 29
👫 Все члены команды: 106

  По отделам:
    • Не указано: 76 чел.
    • Ректорат: 1 чел.
    • Кухня: 9 чел.
    ...
```

**Note**: Header simplified from "Ежедневная статистика участников" to "Статистика участников" with date in DD.MM.YYYY format (e.g., "01.10.2025")

**Acceptance Criteria:**
- [x] Message includes separate line "Всего кандидатов" showing count of participants with role=CANDIDATE
- [x] "Всего команд" renamed to "Все члены команды"
- [x] Department breakdown remains unchanged and shows under "Все члены команды" as detail
- [x] Department breakdown is indented to show it's related to team members
- [x] All calculations are mathematically correct: total_participants = total_candidates + total_team_members

### Use Case 2: Statistics calculation accuracy
**Scenario:** System calculates statistics from Airtable participant data

**Acceptance Criteria:**
- [x] total_candidates = count of participants where role == "CANDIDATE"
- [x] total_team_members = count of participants where role == "TEAM" (existing total_teams)
- [x] total_participants = total_candidates + total_team_members (unchanged)
- [x] Department breakdown includes ALL participants regardless of role (unchanged behavior)

## Constraints
- Must maintain backward compatibility with existing statistics collection service
- Must not break existing notification scheduler functionality
- Must preserve Russian localization throughout
- Must maintain existing error handling and logging patterns

## Test Plan
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-10-01

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

### Proposed Test Categories

#### Business Logic Tests
- [ ] Test candidate count calculation from participants with role=CANDIDATE
- [ ] Test team member count calculation from participants with role=TEAM
- [ ] Test total participants calculation equals candidates + team members
- [ ] Test message formatting includes all required sections in correct order
- [ ] Test Russian text labels are correct ("Всего кандидатов", "Все члены команды")
- [ ] Test department breakdown indentation (2 spaces before "По отделам", 4 spaces before department items)
- [ ] Test date formatting in header uses DD.MM.YYYY format (e.g., "01.10.2025")
- [ ] Test message header uses "Статистика участников" with date in DD.MM.YYYY format

#### State Transition Tests
Not applicable - no state transitions in this feature

#### Error Handling Tests
- [ ] Test handling when all participants are candidates (no team members, total_teams=0)
- [ ] Test handling when all participants are team members (no candidates, total_candidates=0)
- [ ] Test handling with empty participant list (all counts=0)
- [ ] Test handling when statistics model has null/missing fields

#### Integration Tests
- [ ] Test end-to-end statistics collection returns candidate count in model
- [ ] Test end-to-end message formatting with real statistics data
- [ ] Test notification service uses updated message format
- [ ] Test backward compatibility with existing DepartmentStatistics model

#### User Interaction Tests
- [ ] Test notification delivery includes new candidate count line
- [ ] Test notification message visual structure with indentation
- [ ] Test notification message readability in Telegram client

### Test-to-Requirement Mapping
- **Use Case 1 - Acceptance Criteria 1** ("Всего кандидатов" line) → Tests: candidate count calculation, message formatting, Russian labels
- **Use Case 1 - Acceptance Criteria 2** ("Все члены команды" rename) → Tests: message formatting, Russian labels
- **Use Case 1 - Acceptance Criteria 3** (Department breakdown unchanged) → Tests: department breakdown indentation, backward compatibility
- **Use Case 1 - Acceptance Criteria 4** (Indentation) → Tests: department breakdown indentation
- **Use Case 1 - Acceptance Criteria 5** (Mathematical correctness) → Tests: total participants calculation
- **Use Case 2 - All criteria** (Calculation accuracy) → Tests: candidate count, team member count, total participants calculation, backward compatibility

## TECHNICAL TASK

### Technical Requirements
- [ ] Add `total_candidates` field to `DepartmentStatistics` model with proper validation
- [ ] Update `StatisticsService.collect_statistics()` to calculate total_candidates count
- [ ] Update `DailyNotificationService._format_statistics_message()` to include candidate count and update formatting
- [ ] Maintain backward compatibility - existing tests should continue to work with minimal changes
- [ ] Follow TDD approach - write/update tests first, then implement changes
- [ ] Ensure all type hints pass mypy validation
- [ ] Ensure all code passes flake8 linting
- [ ] Ensure all code passes black/isort formatting

### Implementation Steps & Change Log

#### Step 1: Update DepartmentStatistics model with total_candidates field
- [x] Sub-step 1.1: Add total_candidates field to DepartmentStatistics model
  - **Directory**: `src/models/`
  - **Files to create/modify**: `src/models/department_statistics.py`
  - **Accept**: Field added with proper type hints (int), validation (ge=0), and Pydantic Field description
  - **Tests**: Write test in `tests/unit/test_models/test_department_statistics.py` first
  - **Done**: Model field added and validated, tests passing
  - **Changelog**:
    - `src/models/department_statistics.py:26-29` - Added `total_candidates: int` field with validation and description

- [x] Sub-step 1.2: Update DepartmentStatistics __str__ method to include candidates
  - **Directory**: `src/models/`
  - **Files to create/modify**: `src/models/department_statistics.py`
  - **Accept**: __str__ output includes "candidates={value}" in string representation
  - **Tests**: Update existing test in `tests/unit/test_models/test_department_statistics.py`
  - **Done**: String representation updated, tests passing
  - **Changelog**:
    - `src/models/department_statistics.py:58-69` - Updated __str__ method to include total_candidates

#### Step 2: Update StatisticsService to calculate total_candidates
- [x] Sub-step 2.1: Write tests for candidate count calculation
  - **Directory**: `tests/unit/test_services/`
  - **Files to create/modify**: `tests/unit/test_services/test_statistics_service.py`
  - **Accept**: New test cases added for candidate counting edge cases (all candidates, all teams, mixed, empty)
  - **Tests**: N/A (this step creates tests)
  - **Done**: Test cases written covering all scenarios
  - **Changelog**:
    - `tests/unit/test_services/test_statistics_service.py` - Added 4 new test methods for candidate counting

- [x] Sub-step 2.2: Update collect_statistics() to count candidates
  - **Directory**: `src/services/`
  - **Files to create/modify**: `src/services/statistics_service.py`
  - **Accept**: Service counts participants with role=CANDIDATE and includes in DepartmentStatistics result
  - **Tests**: Run tests from sub-step 2.1
  - **Done**: Candidate counting implemented, all tests passing
  - **Changelog**:
    - `src/services/statistics_service.py:79-80` - Added `total_candidates = 0` initialization
    - `src/services/statistics_service.py:84-89` - Added candidate counting logic in aggregation loop
    - `src/services/statistics_service.py:118-123` - Updated DepartmentStatistics construction to include total_candidates

- [x] Sub-step 2.3: Update logging to include candidate count
  - **Directory**: `src/services/`
  - **Files to create/modify**: `src/services/statistics_service.py`
  - **Accept**: Log messages include candidate count in statistics summary
  - **Tests**: Update test in `tests/unit/test_services/test_statistics_service.py` to verify log output
  - **Done**: Logging updated with candidate information
  - **Changelog**:
    - `src/services/statistics_service.py:125-129` - Updated success log message to include candidates count

#### Step 3: Update DailyNotificationService message formatting
- [x] Sub-step 3.1: Write tests for new message format
  - **Directory**: `tests/unit/test_services/`
  - **Files to create/modify**: `tests/unit/test_services/test_daily_notification_service.py`
  - **Accept**: New test cases verify candidate line, renamed team line, header with date, and indentation
  - **Tests**: N/A (this step creates tests)
  - **Done**: Test cases written for new message format requirements
  - **Changelog**:
    - `tests/unit/test_services/test_daily_notification_service.py` - Updated sample_statistics fixture to include total_candidates
    - `tests/unit/test_services/test_daily_notification_service.py` - Updated all message format tests to verify new format

- [x] Sub-step 3.2: Update _format_statistics_message() method
  - **Directory**: `src/services/`
  - **Files to create/modify**: `src/services/daily_notification_service.py`
  - **Accept**: Message includes candidate count, renamed team label, updated header, and proper indentation
  - **Tests**: Run tests from sub-step 3.1
  - **Done**: Message formatting updated, all tests passing
  - **Changelog**:
    - `src/services/daily_notification_service.py:46-76` - Completely refactored _format_statistics_message() to include:
      - Header with formatted date using DD.MM.YYYY format (e.g., "01.10.2025")
      - Simplified header text to "Статистика участников" (removed "Ежедневная")
      - Candidate count line with 👤 emoji
      - Renamed team label to "Все члены команды"
      - Indented department breakdown (2 spaces for "По отделам:", 4 spaces for department items)

#### Step 4: Update all fixture files to include total_candidates
- [x] Sub-step 4.1: Update test fixtures across all test files
  - **Directory**: `tests/unit/test_services/`
  - **Files to create/modify**:
    - `tests/unit/test_services/test_daily_notification_service.py`
    - `tests/unit/test_services/test_statistics_service.py`
  - **Accept**: All DepartmentStatistics fixture instances include total_candidates field
  - **Tests**: Run full test suite to ensure no fixture-related failures
  - **Done**: All fixtures updated, tests passing
  - **Changelog**:
    - `tests/unit/test_services/test_daily_notification_service.py:43-53` - Added total_candidates to sample_statistics fixture
    - `tests/unit/test_services/test_statistics_service.py` - Updated all DepartmentStatistics instantiations

#### Step 5: Run full test suite and quality checks
- [x] Sub-step 5.1: Run pytest with coverage
  - **Directory**: Project root
  - **Files to create/modify**: None
  - **Accept**: All tests passing with 90%+ coverage on modified files
  - **Tests**: `./venv/bin/pytest tests/ --cov=src --cov-report=html --cov-report=term`
  - **Done**: Test suite passes with required coverage
  - **Changelog**: N/A

- [x] Sub-step 5.2: Run type checking
  - **Directory**: Project root
  - **Files to create/modify**: None
  - **Accept**: mypy reports no type errors
  - **Tests**: `./venv/bin/mypy src --no-error-summary`
  - **Done**: Type checking passes
  - **Changelog**: N/A

- [x] Sub-step 5.3: Run linting
  - **Directory**: Project root
  - **Files to create/modify**: None
  - **Accept**: flake8 reports no linting errors
  - **Tests**: `./venv/bin/flake8 src tests`
  - **Done**: Linting passes
  - **Changelog**: N/A

- [x] Sub-step 5.4: Run formatting
  - **Directory**: Project root
  - **Files to create/modify**: None
  - **Accept**: black and isort make no changes (code already formatted)
  - **Tests**: `./venv/bin/black src tests && ./venv/bin/isort src tests`
  - **Done**: Code formatting verified
  - **Changelog**: N/A

### Constraints
- Must follow TDD approach throughout implementation
- Must maintain 90%+ test coverage on all modified code
- Must pass all quality gates (mypy, flake8, black, isort)
- All changes must preserve backward compatibility

## Plan Review
**Status**: ✅ Approved | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-10-01
**Review Document**: `Plan Review - Notification Message Format Enhancement.md`
**Quality Score**: 9/10
**Decision**: APPROVED FOR IMPLEMENTATION
**Clarifications Addressed**:
- Date format specified as DD.MM.YYYY
- Header text change documented
- All file paths validated

## Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-10-01
**Decision**: NO SPLIT NEEDED
**Reasoning**:
- Appropriate scope (3-4 files, ~50-100 LOC)
- Single atomic feature (cannot deliver partial value)
- Tightly coupled changes (Model → Service → Formatting)
- Low complexity (simple field addition + calculation)
- Splitting would create incomplete intermediate states
**Recommended Approach**: Single PR with four logical commits
**Documentation**: `SPLIT_DECISION.md`

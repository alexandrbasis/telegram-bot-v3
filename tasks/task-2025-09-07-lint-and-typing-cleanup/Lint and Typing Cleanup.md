# Task: Lint and Typing Cleanup
**Created**: 2025-09-07 | **Status**: Ready for Implementation

## Tracking & Progress
### Linear Issue
- **ID**: AGB-35
- **URL**: https://linear.app/alexandrbasis/issue/AGB-35/lint-and-typing-cleanup

### PR Details
- **Branch**: basisalexandr/agb-35-lint-and-typing-cleanup
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-07

### Business Context
Improve code health and developer velocity by eliminating outstanding lint (flake8) and typing (mypy) errors without changing runtime behavior. This reduces CI noise, prevents future regressions, and speeds up reviews.

### Primary Objective
Resolve identified flake8 and mypy issues in targeted modules and tests while preserving current functionality and test outcomes.

### Use Cases
1. Developer runs `flake8` and sees zero violations for targeted files.
   - Acceptance: No W29x/W292/W293 or similar whitespace violations in listed test files; no new violations introduced.
2. Developer runs `mypy` and sees zero errors in targeted modules.
   - Acceptance: mypy returns 0 errors for the modules in scope; no new typing errors introduced.

### Success Metrics
- [ ] 0 flake8 violations in targeted files
- [ ] 0 mypy errors in targeted modules
- [ ] All unit tests remain green (no regressions)

### Constraints
- No functional/behavioral changes
- Minimal, localized edits (annotations/guards/formatting only)
- Avoid refactors or API changes; keep changes surgical

## Test Plan
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-07

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas (Primary verification relies on static analysis (flake8, mypy) and regression safety through the existing unit test suite. No functional changes are introduced; no new tests required.)

### Test Categories
#### Business Logic Tests
- [ ] Verify zero diff in behavior via existing unit tests (no logic changes)

#### State Transition Tests
- [ ] Not applicable (no dialog/state changes)

#### Error Handling Tests
- [ ] Ensure unit tests still pass (no runtime error path changes)

#### Integration Tests
- [ ] Ensure existing integration tests remain green if run locally (no IO/API changes)

#### User Interaction Tests
- [ ] Not applicable (no UI/UX or bot conversation changes)

### Test-to-Requirement Mapping
- Business Requirement 1 (Zero flake8 violations) → Lint command returns no output/errors
- Business Requirement 2 (Zero mypy errors) → mypy returns 0 errors for scoped modules
- Regression safety (No behavior change) → All unit tests remain green

### Verification Commands
- Lint: `./venv/bin/flake8 src tests`
- Typing: `./venv/bin/mypy src --no-error-summary`
- Unit tests: `./venv/bin/pytest tests/unit -q`

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: AI Plan Reviewer | **Date**: 2025-09-07
**Review Document**: [Plan Review - Lint and Typing Cleanup.md](./Plan%20Review%20-%20Lint%20and%20Typing%20Cleanup.md)

### Technical Requirements
- [ ] Fix flake8 whitespace issues in listed test files only
- [ ] Add missing return type annotations in `src/utils/test_helper.py`
- [ ] Add type annotations and None-guards in `src/utils/single_instance.py`
- [ ] Ensure all branches return in `src/services/participant_update_service.py`
- [ ] Add return types in `src/services/service_factory.py`, `src/config/settings.py`
- [ ] Add dict type annotations in `src/data/data_validator.py`
- [ ] Resolve minor assignment types in `src/models/participant.py` without behavior change

### Implementation Steps & Change Log
- [ ] Step 1: Fix whitespace in tests (no behavior changes)
  - [ ] Sub-step 1.1: Fix flake8 whitespace violations in test files
    - **Directory**: `tests/`
    - **Files to create/modify**: 
      - `tests/integration/test_centralized_field_references.py`
      - `tests/unit/test_config/test_field_mappings_completeness.py`
      - `tests/unit/test_config/test_formula_field_references.py`
      - `tests/unit/test_config/test_telegram_id_mapping.py`
      - `tests/unit/test_data/test_airtable/test_contact_info_mapping_verification.py`
      - `tests/unit/test_data/test_airtable/test_field_reference_backward_compatibility.py`
      - `tests/unit/test_data/test_airtable/test_formula_consistency.py`
      - `tests/unit/test_data/test_airtable/test_telegram_id_search_centralized.py`
    - **Accept**: 0 flake8 violations for these files
    - **Tests**: Use existing test suite to verify no behavioral changes
    - **Done**: `./venv/bin/flake8` returns no violations for listed files
    - **Changelog**: [Record formatting-only changes with file paths and line ranges]

- [ ] Step 2: Add annotations to utils/test_helper.py
  - [ ] Sub-step 2.1: Add missing return type annotations
    - **Directory**: `src/utils/`
    - **Files to create/modify**: `src/utils/test_helper.py`
    - **Accept**: 0 mypy errors in file; tests unaffected
    - **Tests**: Run existing unit tests to verify no regression
    - **Done**: `./venv/bin/mypy src/utils/test_helper.py` returns no errors
    - **Changelog**: [Record annotation additions with line ranges]

- [ ] Step 3: Harden single_instance.py types and guards
  - [ ] Sub-step 3.1: Add type annotations and None-guards for file handle
    - **Directory**: `src/utils/`
    - **Files to create/modify**: `src/utils/single_instance.py`
    - **Accept**: 0 mypy errors; no behavior changes
    - **Tests**: Run existing unit tests to verify functionality preserved
    - **Done**: `./venv/bin/mypy src/utils/single_instance.py` returns no errors
    - **Changelog**: [Record type annotations and guard additions with line ranges]

- [ ] Step 4: Ensure participant_update_service.py functions return correctly
  - [ ] Sub-step 4.1: Fix missing return paths in functions
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_update_service.py`
    - **Accept**: 0 mypy errors; business logic unchanged
    - **Tests**: Run participant update service tests to verify behavior preserved
    - **Done**: `./venv/bin/mypy src/services/participant_update_service.py` returns no errors
    - **Changelog**: [Record return statement additions with line ranges]

- [ ] Step 5: Annotate service_factory.py and settings.py select functions
  - [ ] Sub-step 5.1: Add return types to targeted functions
    - **Directory**: `src/services/` and `src/config/`
    - **Files to create/modify**: `src/services/service_factory.py`, `src/config/settings.py`
    - **Accept**: 0 mypy errors in targeted functions
    - **Tests**: Run existing unit tests to verify no regressions
    - **Done**: `./venv/bin/mypy` returns no errors for these files
    - **Changelog**: [Record return type annotations with line ranges]

- [ ] Step 6: Add dict type annotations in data_validator.py
  - [ ] Sub-step 6.1: Add types for field_error_counts, error_frequency
    - **Directory**: `src/data/`
    - **Files to create/modify**: `src/data/data_validator.py`
    - **Accept**: 0 mypy errors in file
    - **Tests**: Run data validation tests to verify functionality preserved
    - **Done**: `./venv/bin/mypy src/data/data_validator.py` returns no errors
    - **Changelog**: [Record dictionary type annotations with line ranges]

- [ ] Step 7: Address minor type issues in models/participant.py
  - [ ] Sub-step 7.1: Add explicit types in validators and assignments
    - **Directory**: `src/models/`
    - **Files to create/modify**: `src/models/participant.py`
    - **Accept**: 0 mypy errors; preserve pydantic validations and behavior
    - **Tests**: Run participant model tests to verify validation logic unchanged
    - **Done**: `./venv/bin/mypy src/models/participant.py` returns no errors
    - **Changelog**: [Record type annotations with line ranges]

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-07
**Decision**: No Split Needed - Keep as Single Task
**Reasoning**: Task should proceed as single PR. Scope is well-contained (15 files, <300 lines of mechanical changes), low risk (formatting/typing only, no behavioral changes), efficient review time (25-30 minutes), and cohesive single objective (code health improvement). All changes are easily verifiable against linting/typing tool output with no complex logic to understand. Splitting would add coordination overhead without benefit - both sets of changes serve complementary aspects of the same goal and should land together for complete static analysis compliance.

## Notes for Other Devs
- All changes are formatting and typing-only with explicit constraint to avoid behavior changes
- Commit in small steps by file/module for easy review
- Keep commit messages explicit (lint-only vs type-only) for clear review process
- Verification relies on static analysis and existing unit tests
- No new dependencies or external changes required
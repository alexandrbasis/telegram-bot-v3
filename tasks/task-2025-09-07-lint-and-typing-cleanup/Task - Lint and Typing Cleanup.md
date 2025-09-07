# Task: Lint and Typing Cleanup
**Created**: 2025-09-07 | **Status**: Ready for Implementation

## Tracking & Progress
### Linear Issue
- **ID**: AGB-35
- **URL**: https://linear.app/alexandrbasis/issue/AGB-35/lint-and-typing-cleanup

### PR Details
- **Branch**: basisalexandr/agb-35-lint-and-typing-cleanup (proposed)
- **PR URL**: (TBD)
- **Status**: Draft

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-07

### Business Context
Improve code health and developer velocity by eliminating outstanding lint (flake8) and typing (mypy) errors without changing runtime behavior. This reduces CI noise, prevents future regressions, and speeds up reviews.

### Primary Objective
Resolve identified flake8 and mypy issues in targeted modules and tests while preserving current functionality and test outcomes.

### Use Cases
1. Developer runs `flake8` and sees zero violations for targeted files.
2. Developer runs `mypy` and sees zero errors in targeted modules.

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
Verification via static analysis and existing unit tests; no new tests required.

### Test Categories
- Lint: `./venv/bin/flake8 src tests`
- Typing: `./venv/bin/mypy src --no-error-summary`
- Unit: `./venv/bin/pytest tests/unit -q`

### Test-to-Requirement Mapping
- Business Requirement 1 → flake8 returns no violations
- Business Requirement 2 → mypy returns 0 errors
- Regression safety → all unit tests pass

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-09-07

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
  - **Files**: See Flake8 scope list below
  - **Accept**: 0 flake8 violations for these files
  - **Tests**: Use existing test suite
  - **Changelog**: Formatting only; no logic changes

- [ ] Step 2: Add annotations to `src/utils/test_helper.py`
  - **Accept**: 0 mypy errors in file; tests unaffected

- [ ] Step 3: Harden `src/utils/single_instance.py` types and guards
  - **Accept**: 0 mypy errors; no behavior changes

- [ ] Step 4: Ensure `participant_update_service.py` functions return correctly
  - **Accept**: 0 mypy errors; business logic unchanged

- [ ] Step 5: Annotate `service_factory.py`, `settings.py` select functions
  - **Accept**: 0 mypy errors in targeted functions

- [ ] Step 6: Add dict type annotations in `data_validator.py`
  - **Accept**: 0 mypy errors in file

- [ ] Step 7: Address minor type issues in `models/participant.py`
  - **Accept**: 0 mypy errors; preserve pydantic validations and behavior

### Flake8 Scope (tests)
- `tests/integration/test_centralized_field_references.py`
- `tests/unit/test_config/test_field_mappings_completeness.py`
- `tests/unit/test_config/test_formula_field_references.py`
- `tests/unit/test_config/test_telegram_id_mapping.py`
- `tests/unit/test_data/test_airtable/test_contact_info_mapping_verification.py`
- `tests/unit/test_data/test_airtable/test_field_reference_backward_compatibility.py`
- `tests/unit/test_data/test_airtable/test_formula_consistency.py`
- `tests/unit/test_data/test_airtable/test_telegram_id_search_centralized.py`

### Task Splitting Evaluation
Decision: ✅ No Split Needed — scope is localized and low-risk.

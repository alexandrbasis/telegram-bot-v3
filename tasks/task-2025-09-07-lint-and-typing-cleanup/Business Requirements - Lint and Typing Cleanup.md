# Business Requirements: Lint and Typing Cleanup
**Status**: ✅ Approved | **Created**: 2025-09-07 | **Approved by**: User | **Date**: 2025-09-07

## Business Context
Improve code health and developer velocity by eliminating outstanding lint (flake8) and typing (mypy) errors without changing runtime behavior. This reduces CI noise, prevents future regressions, and speeds up reviews.

## Primary Objective
Resolve identified flake8 and mypy issues in targeted modules and tests while preserving current functionality and test outcomes.

## Use Cases
1. Developer runs `flake8` and sees zero violations for targeted files.
   - Acceptance: No W29x/W292/W293 or similar whitespace violations in listed test files; no new violations introduced.
2. Developer runs `mypy` and sees zero errors in targeted modules.
   - Acceptance: mypy returns 0 errors for the modules in scope; no new typing errors introduced.

## Success Metrics
- [ ] 0 flake8 violations in targeted files
- [ ] 0 mypy errors in targeted modules
- [ ] All unit tests remain green (no regressions)

## Constraints
- No functional/behavioral changes
- Minimal, localized edits (annotations/guards/formatting only)
- Avoid refactors or API changes; keep changes surgical

## Initial Scope (from current diagnostics)

### Flake8 whitespace fixes (tests)
- `tests/integration/test_centralized_field_references.py` (trailing whitespace, blank-line whitespace, missing newline)
- `tests/unit/test_config/test_field_mappings_completeness.py` (trailing/blank-line whitespace)
- `tests/unit/test_config/test_formula_field_references.py` (blank-line whitespace, newline)
- `tests/unit/test_config/test_telegram_id_mapping.py` (blank-line whitespace, newline)
- `tests/unit/test_data/test_airtable/test_contact_info_mapping_verification.py` (trailing/blank-line whitespace, newline)
- `tests/unit/test_data/test_airtable/test_field_reference_backward_compatibility.py` (trailing/blank-line whitespace, newline)
- `tests/unit/test_data/test_airtable/test_formula_consistency.py` (trailing/blank-line whitespace, newline)
- `tests/unit/test_data/test_airtable/test_telegram_id_search_centralized.py` (blank-line whitespace, newline)

### mypy errors (src)
- `src/utils/test_helper.py` — add return type annotations (-> None where appropriate)
- `src/utils/single_instance.py` — annotate fields; add None-guards for file handle; clean unreachable branches
- `src/services/participant_update_service.py` — ensure all code paths return as declared
- `src/services/service_factory.py` — add return types
- `src/config/settings.py` — add return type on specific function(s)
- `src/data/data_validator.py` — add types for `field_error_counts`, `error_frequency`
- `src/models/participant.py` — add explicit types in validators; minor assignment types

Note: Handlers have numerous Optional/None diagnostics. Excluded in this pass to avoid behavioral changes; to be handled in a separate task if needed.

---

Approve business requirements? [Yes/No]

# Code Review - Airtable Bot Schedule Integration

**Date**: 2025-09-27 | **Reviewer**: AI Code Reviewer  
**Task**: `tasks/task-2025-09-27-airtable-bot-schedule/Airtable Bot Schedule Integration.md` | **PR**: https://github.com/alexandrbasis/telegram-bot-v3/pull/71 | **Status**: 🔄 READY FOR RE-REVIEW

## Summary
Implementation adds schedule models, repository, service with caching, Telegram handlers, formatting utilities, and Airtable scripting assets. Following fixes were applied: inclusive Airtable date filtering, documented feature flag with deterministic enablement in `main.py`, DI via service factory for handlers, and keyboard export. CI is green.

## Requirements Compliance
### ✅ Completed
- [x] Airtable schedule field mappings documented and scripted — good metadata coverage.
- [x] Schedule model and formatter validated by unit tests.

### 🔄 Addressed / Remaining
- [x] `/schedule` command reachable in production; feature flag documented in `.env.example` and `docs/technical/configuration.md`; gating via `settings.application.enable_schedule_feature` in `main.py`.
- [x] Airtable query includes boundary dates; formula fixed and covered by tests.
- [x] Service layer honors dependency injection/caching via `service_factory.get_schedule_service()`.
- [~] Test plan coverage: repository unit tests added; service/handler/integration tests remain TODO.

## Quality Assessment
**Overall**: ❌ Needs Improvement  
**Architecture**: Handler directly instantiates service, bypassing factory; schedule module not registered with router  
**Standards**: Tests missing for new flows; Airtable formula incorrect; env-flag workflow undocumented  
**Security**: Auth utils change OK; no new security findings, but feature enablement relies on undocumented env var

## Testing & Documentation
**Testing**: 🔄 Improved — added repository tests for inclusive date boundaries and sorting; service/handler/integration tests pending.  
**Test Execution Results**: `./venv/bin/pytest tests -v` → 1566 passed, 9 skipped.  
**Documentation**: ✅ Updated — Feature flag `ENABLE_SCHEDULE_FEATURE` added to `.env.example` and documented; task doc updated; PR description to reflect changes.

## Issues Checklist

### 🚨 Critical (Must Fix Before Merge)
- [x] **Airtable formula excludes boundary dates** → Fixed with inclusive `OR(IS_AFTER, IS_SAME)` / `OR(IS_BEFORE, IS_SAME)` logic; added regression tests → `src/data/airtable/airtable_schedule_repo.py`, `tests/unit/test_data/test_airtable/test_airtable_schedule_repo.py`.
- [x] **Schedule feature never enabled in production** → Documented flag; `.env.example` updated; deterministic gating via `settings.application.enable_schedule_feature` in `src/main.py`.
- [x] **Handlers bypass DI & caching** → Refactored to use `service_factory.get_schedule_service()`; respects caching/testing strategy → `src/bot/handlers/schedule_handlers.py`, `src/services/service_factory.py`.
- [x] **Handlers not registered / keyboard export missing** → Keyboard exported; handlers registered behind feature flag in `main.py` → `src/bot/keyboards/__init__.py`, `src/main.py`.

### ⚠️ Major (Should Fix)
- [x] **Formula string malformed** → Corrected per inclusive boundary logic in repo; validated by tests.
- [ ] **Missing negative-path tests** → Add tests for empty schedules, Airtable errors, handler states → `tests/unit/test_services/test_schedule_service.py`, `tests/unit/test_bot_handlers/test_schedule_handlers.py`.
- [ ] **Caching TTL upper bound** → Document/verify TTL adherence to ≤10m; add tests if applicable.

### 💡 Minor (Nice to Fix)
- [ ] **Schedule formatter sorting** → When `order` missing, fallback 9999 but still sorts by start_time only; consider sorting by start_time first to avoid inter-day mixing; add docstring.
- [ ] **Scripts bundle** → Many helper scripts added to repo (create/add/verify). Consider consolidating or moving to `docs/scripts` with usage notes.

## Recommendations
### Immediate Actions
1. Add remaining tests per plan (service caching, handler states, error messages).  
2. Document/verify cache TTL (≤10m) behavior and add tests.  
3. Optional: formatter/unit tests and integration flow tests.

### Future Improvements
1. Consider background refresh job instead of per-request fetch to meet freshness SLA.  
2. Evaluate central config for schedule date range to avoid magic constants.

## Final Decision
**Status**: 🔄 READY FOR RE-REVIEW

**Criteria**: All Critical issues addressed; CI green; repository-level tests added. Major items remaining are test coverage for negative paths and TTL documentation.

## Developer Instructions
### Fix Issues:
1. Address each Critical/Major item, update review checklist with `[x]` once done.  
2. Extend test suite to cover schedule repo/service/handlers per task plan.  
3. Update documentation and `.env.example` for feature enablement.  
4. Update changelog and task checklist with accurate completion status.

### Testing Checklist:
- [ ] Schedule repository tests verify inclusive filtering and sorting  
- [ ] Service caching tests cover TTL, error propagation, cache hits  
- [ ] Handler tests cover command entry, day callbacks, back/refresh, errors  
- [ ] Formatter tests cover empty day, location/audience formatting  
- [ ] Full test suite passes: `./venv/bin/pytest tests -v`

### Re-Review:
1. After fixes, update this review doc with resolutions.  
2. Notify reviewer for re-evaluation.

## Implementation Assessment
**Execution**: Partial; significant missing registrations and tests  
**Documentation**: Incomplete for feature toggles  
**Verification**: Suite passes but lacks targeted schedule coverage

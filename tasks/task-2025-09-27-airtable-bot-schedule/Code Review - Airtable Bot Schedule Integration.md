# Code Review - Airtable Bot Schedule Integration

**Date**: 2025-09-27 | **Reviewer**: AI Code Reviewer  
**Task**: `tasks/task-2025-09-27-airtable-bot-schedule/Airtable Bot Schedule Integration.md` | **PR**: https://github.com/alexandrbasis/telegram-bot-v3/pull/71 | **Status**: ❌ NEEDS FIXES

## Summary
Implementation adds schedule models, repository, service with caching, Telegram handlers, formatting utilities, and extensive Airtable scripting assets. Core functionality meets high-level requirements, but several critical issues block safe go-live: incorrect Airtable formula filtering causes missing events; schedule feature always disabled in production due to missing env flag docs; service instantiation in handler breaks DI/testing strategy; missing keyboard export/registration prevents handler wiring. Documentation claims full completion without covering enablement steps.

## Requirements Compliance
### ✅ Completed
- [x] Airtable schedule field mappings documented and scripted — good metadata coverage.
- [x] Schedule model and formatter validated by unit tests.

### ❌ Missing/Incomplete
- [ ] `/schedule` command reachable in production; feature flag absent in docs/env templates.
- [ ] Airtable query must include boundary dates; current formula excludes same-day events.
- [ ] Service layer should honor existing dependency injection/testing patterns.
- [ ] Task/test plan coverage claims (state transitions, error handling, integration) not backed by tests.

## Quality Assessment
**Overall**: ❌ Needs Improvement  
**Architecture**: Handler directly instantiates service, bypassing factory; schedule module not registered with router  
**Standards**: Tests missing for new flows; Airtable formula incorrect; env-flag workflow undocumented  
**Security**: Auth utils change OK; no new security findings, but feature enablement relies on undocumented env var

## Testing & Documentation
**Testing**: ❌ Insufficient — only model tests added; missing service, repo, handler, formatter behavior tests promised in plan.  
**Test Execution Results**: `./venv/bin/pytest tests -v` → 1564 passed, 9 skipped (existing suite). No schedule-specific tests observed.  
**Documentation**: 🔄 Partial — Airtable setup docs added, but enabling instructions (`ENABLE_SCHEDULE_FEATURE`) missing from `.env.example`, setup guides, and PR description; task changelog marks steps done despite gaps.

## Issues Checklist

### 🚨 Critical (Must Fix Before Merge)
- [ ] **Airtable formula excludes boundary dates** → Events on `date_from`/`date_to` dropped; users miss same-day slots → Use `IS_AFTER({Date}, '2025-11-13')` formula is incorrect; replace with `IS_AFTER({Date}, DATEADD('2025-11-13', -1, 'days'))` or use `IS_SAME` / `AND({Date} >= ...)` style to include boundaries → `src/data/airtable/airtable_schedule_repo.py` → Add regression test in `tests/unit/test_data/test_airtable/test_airtable_schedule_repo.py`.
- [ ] **Schedule feature never enabled in production** → `main.py` guards handlers behind `ENABLE_SCHEDULE_FEATURE`, but `.env.example`, docs, task instructions omit flag → Adds requirement violation: command unreachable → Document and default behavior (consider enabling by default) → `.env.example`, `docs/development/setup_guide.md`, task doc.
- [ ] **Handlers bypass DI & caching** → `handle_schedule_callback` constructs `ScheduleService()` per call; bypasses shared factory, complicates testing and caching TTL guarantee → Inject via application context or use existing service factory (e.g., `get_service_factory().get_schedule_service()`) → `src/bot/handlers/schedule_handlers.py`.
- [ ] **Handlers not registered / keyboard export missing** → New handler module not added to routers; keyboard not exported → `/schedule` unusable even if flag set → Update `src/bot/handlers/__init__.py`, integrate with conversation/router, ensure tests cover registration → same for `src/bot/keyboards/__init__.py`.

### ⚠️ Major (Should Fix)
- [ ] **Formula string malformed** → Current formula uses `IS_AFTER` with addition `+ 1`; Airtable formula will error → Replace with valid AND clause using `DATETIME_PARSE` or direct comparison → `src/data/airtable/airtable_schedule_repo.py`.
- [ ] **Missing negative-path tests** → Test plan promised coverage for empty schedules, Airtable errors, handler states; absent tests reduce confidence → Add tests in `tests/unit/test_services/test_schedule_service.py`, `tests/unit/test_bot_handlers/test_schedule_handlers.py`, etc.
- [ ] **Caching TTL upper bound** → Service enforces TTL ≤1h; requirement states ≤10m; consider default 600 but allow config? Document rationale/test for TTL behavior.

### 💡 Minor (Nice to Fix)
- [ ] **Schedule formatter sorting** → When `order` missing, fallback 9999 but still sorts by start_time only; consider sorting by start_time first to avoid inter-day mixing; add docstring.
- [ ] **Scripts bundle** → Many helper scripts added to repo (create/add/verify). Consider consolidating or moving to `docs/scripts` with usage notes.

## Recommendations
### Immediate Actions
1. Fix Airtable formula to include inclusive range; add unit tests covering boundary dates and invalid formula detection.  
2. Register schedule handlers/keyboards with bot factory and ensure feature flag documented/enabled.  
3. Refactor handler to use injected service (similar to other handlers).  
4. Add missing tests per plan (service caching, handler states, error messages).  
5. Update docs/env templates/task checklist to reflect enablement.

### Future Improvements
1. Consider background refresh job instead of per-request fetch to meet freshness SLA.  
2. Evaluate central config for schedule date range to avoid magic constants.

## Final Decision
**Status**: ❌ NEEDS FIXES

**Criteria**: Critical functionality gaps (unreachable command, incorrect Airtable filtering) and missing test coverage prevent approval. Resolve Critical/Major issues and resubmit.

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

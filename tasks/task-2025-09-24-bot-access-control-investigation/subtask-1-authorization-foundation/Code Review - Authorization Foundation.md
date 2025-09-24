# Code Review - Authorization Foundation

**Date**: 2025-09-24 | **Reviewer**: AI Code Reviewer  
**Task**: `tasks/task-2025-09-24-bot-access-control-investigation/subtask-1-authorization-foundation/Authorization Foundation.md` | **PR**: https://github.com/alexandrbasis/telegram-bot-v3/pull/63 | **Status**: ❌ NEEDS FIXES

## Summary
Implementation introduces viewer/coordinator role support in configuration and utilities, but current changes leave authorization gaps and logging issues that can leak information. Core Airtable queries still expose coordinator data to viewers and schema mapping is out of sync, blocking safe rollout.

## Requirements Compliance
### ✅ Completed
- [x] Configuration loads viewer/coordinator IDs from environment variables with parsing tests
- [x] Role utilities enforce hierarchy (admin > coordinator > viewer) with unit coverage

### ❌ Missing/Incomplete
- [ ] Airtable integration honors role-based restrictions (legacy filters bypass role gating)
- [ ] Documentation/telemetry fully updated for new role counts and fields
- [ ] Operational logging meets privacy guidance for authorization events

## Quality Assessment
**Overall**: ❌ Needs Improvement  
**Architecture**: Role hierarchy utilities align with design, but data-layer integration remains unsecured  
**Standards**: Logging and telemetry updates incomplete; caching strategy regressed performance guarantees  
**Security**: Authorization bypass and PII logging at INFO level require fixes

## Testing & Documentation
**Testing**: 🔄 Partial  
**Test Execution Results**: `./venv/bin/pytest tests -v` → 1318 passed, 9 skipped; coverage 86.39% (meets threshold). Targeted suites also run clean. Functional security tests missing.  
**Documentation**: 🔄 Partial – `.env.example` updated, but field mapping docs and telemetry references not yet aligned with new roles.

## Issues Checklist

### 🚨 Critical (Must Fix Before Merge)
- [ ] **Role bypass in Airtable filters**: `AirtableParticipantRepository.search_by_name` still filters on legacy participant fields, so viewers receive coordinator-only data. Update filters to respect `AccessLevel`/role gating and add regression tests covering viewer/coordinator segmentation.

### ⚠️ Major (Should Fix)
- [ ] **AuthorizedUsers mapping drift**: `src/config/field_mappings/__init__.py` lacks constants for `AccessLevel`/`Status`, blocking future sync jobs. Define mappings and document schema alignment.
- [ ] **Authorization logging leaks PII**: `_has_role_access` logs raw user IDs at INFO. Switch to hashed IDs or downgrade logging to DEBUG to meet privacy guidance.
- [ ] **Missing guard for unknown roles**: `_has_role_access` raises when passed an unsupported role. Add graceful handling (warn + deny) for unexpected inputs from decorators.
- [ ] **Role resolution not cached**: `get_user_role` scans full lists each call; under load this violates <50 ms requirement. Introduce memoized lookup refreshed on cache invalidation.
- [ ] **Telemetry/docs lag role counts**: `Settings.to_dict` now reports coordinator/viewer counts but downstream docs/telemetry references still assume admin-only. Update success metrics and documentation to reflect new keys.

### 💡 Minor (Nice to Fix)
- [ ] None identified.

## Recommendations
### Immediate Actions
1. Patch Airtable repository queries and add coverage to verify viewers cannot access coordinator/admin-only data.
2. Extend field mappings and documentation for `AuthorizedUsers` schema.
3. Harden logging and role helper functions; add caching layer for role lookups.
4. Update telemetry/documentation consumers to consume new role count metrics.

### Future Improvements
1. Define `/auth_refresh` manual invalidation flow and seed strategy for `AuthorizedUsers` table in deployment notes.

## Final Decision
**Status**: ❌ NEEDS FIXES

**Criteria**: Critical authorization bypass and multiple major gaps prevent safe merge.

## Developer Instructions
### Fix Issues:
1. Address each checklist item above; mark with `[x]` when complete.
2. Update changelog/task document with fixes and add regression tests.
3. Rerun full test suite (`./venv/bin/pytest tests -v`) and attach results.

### Testing Checklist:
- [ ] Complete test suite executed
- [ ] Manual verification of role-restricted features (viewer vs coordinator) performed
- [ ] Performance baseline for role lookup (<50 ms) confirmed
- [ ] Regression tests for Airtable filters added
- [ ] Test results documented in task file

### Re-Review:
1. Push fixes, update review doc, notify reviewer for follow-up assessment.

## Implementation Assessment
**Execution**: Initial configuration/utilities solid; data-layer integration incomplete.  
**Documentation**: Partial; schema and telemetry references need updates.  
**Verification**: Automated tests run, but security/performance validations outstanding.

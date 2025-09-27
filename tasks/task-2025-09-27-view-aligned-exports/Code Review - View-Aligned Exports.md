# Code Review - View-Aligned Exports

**Date**: 2025-09-27 | **Reviewer**: AI Code Reviewer  
**Task**: `tasks/task-2025-09-27-view-aligned-exports/View-Aligned Exports.md` | **PR**: https://github.com/alexandrbasis/telegram-bot-v3/pull/69 | **Status**: ❌ NEEDS FIXES

## Summary
Implementation introduces view-driven exports and associated utilities. The approach generally aligns with the documented plan, but the header extraction logic misses columns whenever the first Airtable record lacks values, causing exports to drop required fields, so corrections are needed before merge.

## Requirements Compliance
### ✅ Completed
- [x] Fetch exports through repository `list_view_records()` with graceful legacy fallback
- [x] Preserve sequential `#` column and progress callbacks across export flows
- [x] Add configuration entries for view names with validation and tests

### ❌ Missing/Incomplete
- [ ] Ensure CSV headers always match Airtable view column order and contents, even when early records omit field values

## Quality Assessment
**Overall**: ❌ Needs Improvement  
**Architecture**: Service layering respected; new settings usage bypasses existing factory caching but not breaking  
**Standards**: Tests thorough; primary gap in header extraction logic  
**Security**: No new risks observed

## Testing & Documentation
**Testing**: ✅ Adequate  
**Test Execution Results**: `./venv/bin/pytest tests/unit/test_utils/test_export_utils.py tests/unit/test_services/test_participant_export_service.py tests/unit/test_services/test_roe_export_service.py tests/unit/test_services/test_bible_readers_export_service.py -q` → 135 passed  
**Documentation**: ✅ Complete (CHANGELOG and task doc updated)

## Issues Checklist

### 🚨 Critical (Must Fix Before Merge)
- [ ] **Headers omit view columns without data**: `extract_headers_from_view_records()` only inspects the first record, and `order_rows_by_view_headers()` drops fields not listed there. If the leading record lacks values for some columns, the export removes those columns entirely, violating the requirement that exports mirror Airtable views. → Update header extraction to accumulate the ordered union of fields across view records (or query view metadata) while keeping consistent ordering, then ensure row reordering retains empty columns. → `src/utils/export_utils.py`, `src/services/participant_export_service.py`, `src/services/roe_export_service.py`, `src/services/bible_readers_export_service.py`, `tests/unit/test_utils/test_export_utils.py`

### ⚠️ Major (Should Fix)
- [ ] *None*

### 💡 Minor (Nice to Fix)
- [ ] *None*

## Recommendations
### Immediate Actions
1. Rework header extraction to preserve all view columns even when early records omit values, and extend tests to cover sparse-record scenarios.

### Future Improvements
1. Consider injecting `Settings` via `service_factory` to reuse cached configuration rather than instantiating `Settings()` within services.

## Final Decision
**Status**: ❌ NEEDS FIXES

**Criteria**: Critical requirement failure—exports can drop view columns when initial records have empty fields, so corrections and additional tests are required before approval.

## Developer Instructions
### Fix Issues:
1. **Follow solution guidance** and mark fixes with `[x]`
2. **Update task document** with fix details
3. **Test thoroughly** and request re-review

### Testing Checklist:
- [ ] Complete test suite executed and passes
- [ ] Manual testing of implemented features completed
- [ ] Performance impact assessed (if applicable)
- [ ] No regressions introduced
- [ ] Test results documented with actual output

### Re-Review:
1. Complete fixes, update changelog, ensure tests pass
2. Notify reviewer when ready

## Implementation Assessment
**Execution**: Solid structure, but header logic needs correction  
**Documentation**: Detailed and up to date  
**Verification**: Automated tests strong, need additional sparse-field coverage


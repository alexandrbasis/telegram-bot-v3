# View-Aligned Exports

## Tracking & Progress
### Linear Issue
- **ID**: AGB-74
- **URL**: https://linear.app/alexandrbasis/issue/AGB-74/view-aligned-exports-align-bot-exports-with-airtable-views-for

### PR Details
- **Branch**: feature/agb-74-view-aligned-exports
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

## Business Requirements
**Status**: ✅ Approved | **Approved by**: Alexandr Basis | **Date**: 2025-09-27

### Business Context
New Airtable views have been curated to reflect the exact ordering and fields needed for candidate, ROE, and Bible Readers exports. Aligning bot exports with those views prevents schema drift and ensures consistent structure with the operational dashboards.

### Primary Objective
Leverage Airtable API credentials to fetch view-specific records for Candidates (`Кандидаты`), ROE (`РОЕ: Расписание`), and Bible Readers (`Чтецы: Расписание`), producing Telegram exports that mirror those view structures and retain the leading line-number column.

### Use Cases
1. **Candidate view export** – Admin triggers candidate export and receives CSV with columns ordered exactly as in Airtable view `Кандидаты`, including `#` as first column.
2. **ROE view export** – Admin exports ROE data; CSV matches Airtable `РОЕ: Расписание` view (fields, order, formatting) with `#` column first.
3. **Bible Readers view export** – Admin exports Bible Readers data; CSV matches Airtable `Чтецы: Расписание` view structure while preserving first-column line numbers.

### Success Metrics
- [ ] Bot CSV exports for candidates, ROE, and Bible Readers match Airtable view column order and naming 1:1
- [ ] Every exported row for the three flows includes a sequential `#` column starting at 1

### Constraints
- Must use existing Airtable API credentials; no manual CSV restructuring after fetch
- Avoid regressions in existing export flows (progress callbacks, captions, file delivery)
- Keep solution resilient to minor view additions (ignore unknown fields gracefully)

---

## Test Plan
**Status**: ✅ Approved | **Approved by**: Alexandr Basis | **Date**: 2025-09-27

### Test Coverage Strategy
Target: 90%+ coverage across view-aligned export logic

### Proposed Test Categories
#### Business Logic Tests
- [ ] Candidate export uses view header ordering and includes `#` column
- [ ] ROE export uses view header ordering and includes `#` column
- [ ] Bible Readers export uses view header ordering and includes `#` column

#### State Transition Tests
- [ ] Export conversation flows remain unchanged when switching to view-driven exports
- [ ] Progress callbacks still fire during exports across all three flows

#### Error Handling Tests
- [ ] Export falls back gracefully if a view temporarily disappears (returns consistent error messaging)
- [ ] Unknown fields in view are ignored without crashing CSV generation

#### Integration Tests
- [ ] Candidate export end-to-end using mocked Airtable view response
- [ ] ROE export end-to-end using mocked Airtable view response
- [ ] Bible Readers export end-to-end using mocked Airtable view response

#### User Interaction Tests
- [ ] Captions show correct participant counts with line numbers unaffected
- [ ] Telegram document upload still works with updated CSV content

### Test-to-Requirement Mapping
- Business Requirement 1 → Tests: Candidate view business logic, candidate integration, caption checks
- Business Requirement 2 → Tests: ROE view business logic, ROE integration, caption checks
- Business Requirement 3 → Tests: Bible Readers view business logic, Bible Readers integration, caption checks

---

## Technical Task
**Created**: 2025-09-27 | **Status**: Partially Complete (Foundation Done) | **Started**: 2025-09-27 | **Foundation Complete**: 2025-09-27 | **Plan Reviewed by**: Plan Reviewer Agent | **Task Evaluated by**: Task Splitter Agent | **Date**: 2025-09-26

### ✅ COMPLETED: Foundation Infrastructure (Steps 1-3)
**Repository Layer**: All three repositories (Participant, ROE, Bible Readers) now have consistent `list_view_records()` support
**Configuration Layer**: View names configurable via environment variables with proper validation
**Test Coverage**: 111/111 tests passing across all modified components (9 repository + 53 airtable + 49 settings tests)

### ⚠️ REMAINING: Export Service Integration (Steps 4-8)
**Next Steps**: Update export utilities and services to use view-based data retrieval with configured view names
**Key Files**: `src/utils/export_utils.py`, `src/services/*_export_service.py`
**Critical**: Preserve `#` line numbers while respecting view column order

**For Next Developer**:
1. **Step 4**: Extend `src/utils/export_utils.py` to handle view-based column ordering
2. **Steps 5-7**: Update export services to use `list_view_records(settings.{type}_export_view)`
3. **Step 8**: Add enhanced logging and documentation
4. **Pattern**: Follow TDD approach established in foundation - see existing tests for examples
5. **Repository Access**: Use `settings.database.{type}_export_view` for configured view names

### Knowledge Gaps - Addressed in Implementation
- ✅ **Field ordering from Airtable views**: Addressed in Steps 2.1-2.2 by implementing concrete view support in ROE and Bible Readers repositories with proper field mapping and ordering.
- ✅ **Repository view-specific helpers**: Addressed in Steps 1.1 by standardizing `list_view_records()` interface across all repositories, and Steps 2.1-2.2 by implementing concrete view support.
- ✅ **Downstream consumer dependencies**: Addressed in Step 3.1 by creating configurable view names with fallback handling, and comprehensive testing in Steps 5-7 to validate no regressions in export workflows.

### Technical Requirements
- [ ] **REMAINING**: Candidate export must retrieve records using Airtable view `Кандидаты`, preserving view-defined column order and prepending `#` line numbers.
- [ ] **REMAINING**: ROE export must retrieve records using Airtable view `РОЕ: Расписание`, preserving column order and prepending `#` line numbers.
- [ ] **REMAINING**: Bible Readers export must retrieve records using Airtable view `Чтецы: Расписание`, preserving column order and prepending `#` line numbers.
- [x] ✅ **FOUNDATION**: Repository layer supports view-based data retrieval with consistent interface across all three types
- [x] ✅ **FOUNDATION**: View names are configurable via environment variables with validation and fallback handling
- [x] ✅ **FOUNDATION**: Repository tests validate view functionality with mocked Airtable responses
- [ ] **REMAINING**: View-driven exports must degrade gracefully: if a view is unavailable, log a clear warning and optionally fall back to existing behavior (without breaking the bot).
- [ ] **REMAINING**: Export service tests must validate column ordering, line numbers, and integration workflow for all three exports with mocked Airtable responses.

### Implementation Steps & Change Log
- [x] ✅ Step 1: Establish repository interface consistency for view support
  - [x] ✅ Sub-step 1.1: Add abstract view method to repository interfaces - Completed 2025-09-27
    - **Directory**: `src/data/repositories/`
    - **Files to create/modify**: `src/data/repositories/roe_repository.py`, `src/data/repositories/bible_readers_repository.py`
    - **Accept**: Both repository interfaces include abstract `list_view_records(view_name: str)` method matching ParticipantRepository interface.
    - **Tests**: `tests/unit/test_data/test_repositories/test_roe_repository.py`, `tests/unit/test_data/test_repositories/test_bible_readers_repository.py` (interface validation).
    - **Done**: Repository interfaces are consistent; abstract method exists in all three interfaces.
    - **Changelog**: Document repository interface standardization.
    - **Notes**: Added list_view_records() to ROE and BibleReaders repository interfaces, updated tests with TDD approach, all 9 interface tests passing

- [x] ✅ Step 2: Implement concrete view support in Airtable repositories
  - [x] ✅ Sub-step 2.1: Implement ROE repository view support - Completed 2025-09-27
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_roe_repo.py`
    - **Accept**: `list_view_records("РОЕ: Расписание")` returns records in view-defined order with proper field mapping.
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_roe_repo.py` (view method functionality).
    - **Done**: ROE repository supports view-based record retrieval with mocked Airtable responses.
    - **Changelog**: Document ROE view support implementation.
    - **Notes**: Added list_view_records() method with TDD approach, all 26 ROE repository tests passing including 2 new view tests
  - [x] ✅ Sub-step 2.2: Implement Bible Readers repository view support - Completed 2025-09-27
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_bible_readers_repo.py`
    - **Accept**: `list_view_records("Чтецы: Расписание")` returns records in view-defined order with proper field mapping.
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_bible_readers_repo.py` (view method functionality).
    - **Done**: Bible Readers repository supports view-based record retrieval with mocked Airtable responses.
    - **Changelog**: Document Bible Readers view support implementation.
    - **Notes**: Added list_view_records() method with TDD approach, all 27 Bible Readers repository tests passing including 2 new view tests

- [x] ✅ Step 3: Create view configuration management
  - [x] ✅ Sub-step 3.1: Add view name configuration - Completed 2025-09-27
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/settings.py`
    - **Accept**: Configuration class includes validated view names for candidates, ROE, and Bible Readers exports with fallback handling.
    - **Tests**: `tests/unit/test_config/test_settings.py` (view configuration validation).
    - **Done**: View names are configurable and validated at startup.
    - **Changelog**: Document view configuration management.
    - **Notes**: Added 3 configurable view fields with environment variable support, validation, and TDD tests (49/49 settings tests passing)

- [x] ✅ Step 4: Enhance export utilities for view-based ordering (clarify existing vs new functionality) - Completed 2025-09-27
  - [x] ✅ Sub-step 4.1: Extend existing export utilities for view header ordering - Completed 2025-09-27
    - **Directory**: `src/utils/`
    - **Files to create/modify**: `src/utils/export_utils.py`
    - **Accept**: Existing utilities extended to derive column order from Airtable view records while preserving `#` line numbers as first column.
    - **Tests**: `tests/unit/test_utils/test_export_utils.py` (new test cases for view-based ordering using existing function signatures).
    - **Done**: Unit tests pass with view-based header extraction using standardized mock data structure.
    - **Changelog**: Document utility enhancement for view ordering.
    - **Notes**: Implemented extract_headers_from_view_records() and order_rows_by_view_headers() with TDD approach, all 48 export utility tests passing including 13 new view-ordering tests

- [ ] Step 5: Update participant export to use view `Кандидаты`
  - [ ] Sub-step 5.1: Modify candidate export path
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: Candidate export uses configured view name via `list_view_records()`, builds CSV using view-based headers, includes `#` column.
    - **Tests**: `tests/unit/test_services/test_participant_export_service.py` (view-order test with standardized mocks), `tests/integration/test_export_selection_workflow.py` (candidate path).
    - **Done**: Relevant unit and integration tests pass with consistent mock data structure, manual verification confirms column ordering.
    - **Changelog**: Record participant view alignment.

- [ ] Step 6: Update ROE export to use view `РОЕ: Расписание`
  - [ ] Sub-step 6.1: Modify ROE export service
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/roe_export_service.py`
    - **Accept**: `export_to_csv_async()` fetches via `list_view_records()` using configured view name, respects view column order, ensures `#` column.
    - **Tests**: `tests/unit/test_services/test_roe_export_service.py` (view-order test with standardized mocks), `tests/integration/test_export_selection_workflow.py` (ROE path).
    - **Done**: Tests pass with consistent mock data structure, manual verification confirms column ordering and numbering.
    - **Changelog**: Record ROE view alignment.

- [ ] Step 7: Update Bible Readers export to use view `Чтецы: Расписание`
  - [ ] Sub-step 7.1: Modify Bible Readers export service
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/bible_readers_export_service.py`
    - **Accept**: `export_to_csv_async()` fetches via `list_view_records()` using configured view name, respects view column order, ensures `#` column.
    - **Tests**: `tests/unit/test_services/test_bible_readers_export_service.py` (view-order test with standardized mocks), `tests/integration/test_export_selection_workflow.py` (Bible Readers path).
    - **Done**: Tests pass with consistent mock data structure, manual verification confirms column ordering and numbering.
    - **Changelog**: Record Bible Readers view alignment.

- [ ] Step 8: Update handler logging and documentation
  - [ ] Sub-step 8.1: Enhance logging for view usage and fallback
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/export_conversation_handlers.py`
    - **Accept**: Handler logs which configured view is used or whether fallback triggered with structured error context; no behavior regression.
    - **Tests**: Extend integration tests to capture logging via mocks if necessary.
    - **Done**: Integration tests pass with enhanced logging verification.
    - **Changelog**: Document logging improvements with view context.
  - [ ] Sub-step 8.2: Update documentation
    - **Directory**: project root/docs
    - **Files to create/modify**: `CHANGELOG.md`, optionally `docs/data-integration/`
    - **Accept**: CHANGELOG entry describes view alignment implementation; documentation references new view configuration requirements and fallback behavior.
    - **Tests**: N/A
    - **Done**: Docs reviewed and updated with view configuration details.
    - **Changelog**: Mention documentation update with view management details.

### Implementation Changelog

#### Step 1: Repository Interface Standardization — 2025-09-27
- **Files**: `src/data/repositories/roe_repository.py:151-165`, `src/data/repositories/bible_readers_repository.py:137-151` - Added list_view_records() abstract method
- **Files**: `tests/unit/test_data/test_repositories/test_roe_repository.py:38,84-85`, `tests/unit/test_data/test_repositories/test_bible_readers_repository.py:37,69,99-100` - Updated tests and mocks
- **Summary**: Standardized repository interfaces to include view-based record retrieval method across all three repository types
- **Impact**: All repository implementations must now support list_view_records() method, enabling consistent view-driven exports
- **Tests**: Added list_view_records to required methods validation and mock implementations (9/9 tests passing)
- **Verification**: Repository interface tests validate abstract method presence and mock implementation works correctly

#### Step 2: Concrete View Support Implementation — 2025-09-27
- **Files**: `src/data/airtable/airtable_roe_repo.py:349-371`, `src/data/airtable/airtable_bible_readers_repo.py:317-339` - Added list_view_records() concrete implementations
- **Files**: `tests/unit/test_data/test_airtable/test_airtable_roe_repo.py:343-360`, `tests/unit/test_data/test_airtable/test_airtable_bible_readers_repo.py:336-353` - Added comprehensive TDD tests
- **Summary**: Implemented view-based record retrieval in both ROE and Bible Readers Airtable repositories following participant repository pattern
- **Impact**: All three repository types now support consistent view-driven data access with proper error handling and logging
- **Tests**: Added view functionality tests for both repositories (26/26 ROE, 27/27 Bible Readers tests passing)
- **Verification**: TDD Red-Green-Refactor cycles validated functionality; view names РОЕ: Расписание and Чтецы: Расписание properly supported

#### Step 3: View Configuration Management — 2025-09-27
- **Files**: `src/config/settings.py:134-143,187-195` - Added configurable view names with environment variable support and validation
- **Files**: `tests/unit/test_config/test_settings.py:818-863` - Added comprehensive TDD tests for view configuration
- **Summary**: Implemented configurable view names for all three export types with proper validation and fallback handling
- **Impact**: View names now configurable via environment variables with sensible defaults aligned to business requirements
- **Tests**: Added view configuration test class with 3 test cases (49/49 settings tests passing)
- **Verification**: Environment variables AIRTABLE_PARTICIPANT_EXPORT_VIEW, AIRTABLE_ROE_EXPORT_VIEW, AIRTABLE_BIBLE_READERS_EXPORT_VIEW properly supported

#### Step 4: Export Utilities Enhancement — 2025-09-27
- **Files**: `src/utils/export_utils.py:217-281` - Added view-based ordering functions
- **Files**: `tests/unit/test_utils/test_export_utils.py:453-652` - Added comprehensive TDD tests
- **Summary**: Implemented utility functions to extract headers from view records and reorder rows to match view column order
- **Impact**: Export services can now preserve Airtable view column ordering while maintaining line numbers
- **Tests**: Added 13 new test cases covering header extraction and row reordering (48/48 total tests passing)
- **Verification**: TDD Red-Green cycle completed; functions handle edge cases including missing fields and line number preservation

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-26
**Decision**: No Split Needed
**Reasoning**: Task represents cohesive business objective with tightly coupled implementation across 8 steps spanning 10 files (~300-450 lines). Sequential dependencies (repository → configuration → services → handlers) and shared utilities make splitting counterproductive. All three export types must be view-aligned together for consistent user experience. Single PR provides better coordination, testing, and rollback path than multiple dependent PRs.

### Constraints
- Maintain compatibility with existing line-number utilities.
- Ensure Airtable API usage respects rate limits; consider caching view headers when appropriate.
- Keep fallback behavior documented in case views are renamed or deleted.

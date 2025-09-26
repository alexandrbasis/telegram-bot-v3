# View-Aligned Exports

## Tracking & Progress
### Linear Issue
- **ID**: AGB-74
- **URL**: https://linear.app/alexandrbasis/issue/AGB-74/view-aligned-exports-align-bot-exports-with-airtable-views-for

### PR Details
- **Branch**: basisalexandr/agb-74-view-aligned-exports-align-bot-exports-with-airtable-views
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
**Created**: 2025-09-27 | **Status**: In Progress | **Started**: 2025-09-27 | **Plan Reviewed by**: Plan Reviewer Agent | **Task Evaluated by**: Task Splitter Agent | **Date**: 2025-09-26

### Knowledge Gaps - Addressed in Implementation
- ✅ **Field ordering from Airtable views**: Addressed in Steps 2.1-2.2 by implementing concrete view support in ROE and Bible Readers repositories with proper field mapping and ordering.
- ✅ **Repository view-specific helpers**: Addressed in Steps 1.1 by standardizing `list_view_records()` interface across all repositories, and Steps 2.1-2.2 by implementing concrete view support.
- ✅ **Downstream consumer dependencies**: Addressed in Step 3.1 by creating configurable view names with fallback handling, and comprehensive testing in Steps 5-7 to validate no regressions in export workflows.

### Technical Requirements
- [ ] Candidate export must retrieve records using Airtable view `Кандидаты`, preserving view-defined column order and prepending `#` line numbers.
- [ ] ROE export must retrieve records using Airtable view `РОЕ: Расписание`, preserving column order and prepending `#` line numbers.
- [ ] Bible Readers export must retrieve records using Airtable view `Чтецы: Расписание`, preserving column order and prepending `#` line numbers.
- [ ] View-driven exports must degrade gracefully: if a view is unavailable, log a clear warning and optionally fall back to existing behavior (without breaking the bot).
- [ ] Tests must validate column ordering, line numbers, and integration workflow for all three exports with mocked Airtable responses.

### Implementation Steps & Change Log
- [ ] Step 1: Establish repository interface consistency for view support
  - [ ] Sub-step 1.1: Add abstract view method to repository interfaces
    - **Directory**: `src/data/repositories/`
    - **Files to create/modify**: `src/data/repositories/roe_repository.py`, `src/data/repositories/bible_readers_repository.py`
    - **Accept**: Both repository interfaces include abstract `list_view_records(view_name: str)` method matching ParticipantRepository interface.
    - **Tests**: `tests/unit/test_data/test_repositories/test_roe_repository.py`, `tests/unit/test_data/test_repositories/test_bible_readers_repository.py` (interface validation).
    - **Done**: Repository interfaces are consistent; abstract method exists in all three interfaces.
    - **Changelog**: Document repository interface standardization.

- [ ] Step 2: Implement concrete view support in Airtable repositories
  - [ ] Sub-step 2.1: Implement ROE repository view support
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_roe_repo.py`
    - **Accept**: `list_view_records("РОЕ: Расписание")` returns records in view-defined order with proper field mapping.
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_roe_repo.py` (view method functionality).
    - **Done**: ROE repository supports view-based record retrieval with mocked Airtable responses.
    - **Changelog**: Document ROE view support implementation.
  - [ ] Sub-step 2.2: Implement Bible Readers repository view support
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_bible_readers_repo.py`
    - **Accept**: `list_view_records("Чтецы: Расписание")` returns records in view-defined order with proper field mapping.
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_bible_readers_repo.py` (view method functionality).
    - **Done**: Bible Readers repository supports view-based record retrieval with mocked Airtable responses.
    - **Changelog**: Document Bible Readers view support implementation.

- [ ] Step 3: Create view configuration management
  - [ ] Sub-step 3.1: Add view name configuration
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/settings.py`
    - **Accept**: Configuration class includes validated view names for candidates, ROE, and Bible Readers exports with fallback handling.
    - **Tests**: `tests/unit/test_config/test_settings.py` (view configuration validation).
    - **Done**: View names are configurable and validated at startup.
    - **Changelog**: Document view configuration management.

- [ ] Step 4: Enhance export utilities for view-based ordering (clarify existing vs new functionality)
  - [ ] Sub-step 4.1: Extend existing export utilities for view header ordering
    - **Directory**: `src/utils/`
    - **Files to create/modify**: `src/utils/export_utils.py`
    - **Accept**: Existing utilities extended to derive column order from Airtable view records while preserving `#` line numbers as first column.
    - **Tests**: `tests/unit/test_utils/test_export_utils.py` (new test cases for view-based ordering using existing function signatures).
    - **Done**: Unit tests pass with view-based header extraction using standardized mock data structure.
    - **Changelog**: Document utility enhancement for view ordering.

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

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-26
**Decision**: No Split Needed
**Reasoning**: Task represents cohesive business objective with tightly coupled implementation across 8 steps spanning 10 files (~300-450 lines). Sequential dependencies (repository → configuration → services → handlers) and shared utilities make splitting counterproductive. All three export types must be view-aligned together for consistent user experience. Single PR provides better coordination, testing, and rollback path than multiple dependent PRs.

### Constraints
- Maintain compatibility with existing line-number utilities.
- Ensure Airtable API usage respects rate limits; consider caching view headers when appropriate.
- Keep fallback behavior documented in case views are renamed or deleted.

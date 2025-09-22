# Task: Export Services and Filtering
**Created**: 2025-01-19 | **Status**: Ready for Re-Review | **Updated**: 2025-09-22

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Create export services for BibleReaders and ROE tables while extending the existing ParticipantExportService with role and department filtering capabilities to support selective data exports.

### Use Cases
1. **Role-Based Participant Filtering**: Admin can export only TEAM members or only CANDIDATES
   - **Acceptance Criteria**: ParticipantExportService supports role-based filtering with proper CSV output
2. **Department-Based Participant Filtering**: Admin can export participants from specific departments
   - **Acceptance Criteria**: Service supports all 13 departments with accurate filtering results
3. **BibleReaders Export**: Admin can export Bible reading assignments with participant details
   - **Acceptance Criteria**: BibleReaders export service produces CSV with locations, schedule, scripture reference, and hydrated participant details
4. **ROE Export**: Admin can export ROE session data with presenter information
   - **Acceptance Criteria**: ROE export service produces CSV with topics, presenters, assistants, prayer partners, and scheduled date/time/duration metadata

### Success Metrics
- [ ] Filtered participant exports reduce file sizes by targeting specific subsets
- [ ] BibleReaders and ROE exports provide actionable data for ministry coordinators
- [ ] All export services maintain consistent CSV formatting and error handling

### Constraints
- Must reuse existing `ExportProgressTracker` and `UserInteractionLogger` hooks for telemetry consistency
- Must maintain existing CSV formatting standards
- File size limits still apply (Telegram 50MB limit)
- Must handle empty result sets gracefully
- Export services must integrate with service factory pattern

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-68
- **URL**: https://linear.app/alexandrbasis/issue/TDB-68/subtask-3-export-services-and-filtering
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: feature/TDB-68-export-services-and-filtering
- **PR URL**: https://github.com/alexandrbasis/telegram-bot-v3/pull/55
- **Status**: In Review

## Business Context
**APPROVED**: Enhanced export capabilities with selective filtering and dedicated BibleReaders/ROE exports enable ministry coordinators to access targeted, actionable data subsets for improved event management efficiency.

## Technical Requirements
- [ ] Extend service factory to supply per-table export dependencies without breaking singleton caching
- [ ] Extend ParticipantExportService with role and department filtering
- [ ] Create BibleReadersExportService with proper CSV generation
- [ ] Create ROEExportService with relationship data handling
- [ ] Hydrate linked participant data (names, churches, rooms) within export services since lookup fields were removed upstream
- [ ] Update service factory to provide all export services
- [ ] Maintain consistent error handling and progress tracking

## Implementation Steps & Change Log

### Step 1: ParticipantExportService Filtering — 2025-09-22
- **Files**: `src/services/participant_export_service.py:239-365` - Added role and department filtering methods
- **Files**: `tests/unit/test_services/test_participant_export_service.py:571-848` - Comprehensive filtering test suites
- **Summary**: Extended ParticipantExportService with role-based (TEAM/CANDIDATE) and department-based filtering capabilities. Both methods maintain existing CSV format, progress tracking, and error handling patterns while filtering out participants with null values.
- **Impact**: Enables targeted participant exports reducing file sizes and providing actionable subsets for ministry coordinators
- **Tests**: Added TestRoleBasedFiltering and TestDepartmentBasedFiltering classes with 9 comprehensive test cases covering edge cases, validation, and format consistency
- **Verification**: All tests pass with proper filtering logic - null role/department exclusion, empty result handling, and CSV format maintenance

### Step 2: BibleReadersExportService Implementation — 2025-09-22
- **Files**: `src/services/bible_readers_export_service.py` - Complete export service with participant hydration
- **Files**: `tests/unit/test_services/test_bible_readers_export_service.py` - Comprehensive test suite with 12 test cases
- **Summary**: Created dedicated export service for BibleReaders table with participant name hydration from linked participant IDs. Includes proper CSV formatting with custom ParticipantNames field, progress tracking, and file management.
- **Impact**: Enables actionable Bible reading assignment exports with participant details for ministry coordinators
- **Tests**: Full test coverage including hydration testing, edge cases, and file operations (87% service coverage)
- **Verification**: All tests pass with proper participant hydration and CSV generation

### Step 3: ROEExportService Implementation — 2025-09-22
- **Files**: `src/services/roe_export_service.py` - Complete export service with multi-relationship hydration
- **Files**: `tests/unit/test_services/test_roe_export_service.py` - Comprehensive test suite with 14 test cases
- **Summary**: Created dedicated export service for ROE table with complex relationship hydration for presenters (roista), assistants, and prayer partners. Includes scheduling metadata, proper CSV formatting with hydrated name fields, and comprehensive error handling.
- **Impact**: Enables complete ROE session exports with presenter information and scheduling for ministry coordination
- **Tests**: Full test coverage including multi-relationship hydration, scheduling data, and edge cases (88% service coverage)
- **Verification**: All tests pass with proper multi-participant hydration and scheduling metadata handling

### Step 4: Service Factory Integration — 2025-09-22
- **Files**: `src/services/service_factory.py:18-210` - Extended factory with table-specific client caching and new export services
- **Files**: `tests/unit/test_services/test_service_factory.py:127-282` - Added comprehensive factory tests
- **Summary**: Extended ServiceFactory with table-specific client caching and factory methods for all export services. Maintains backward compatibility while adding support for BibleReaders and ROE repositories and export services with proper dependency injection.
- **Impact**: Provides centralized, efficient service creation with client reuse across multiple table types
- **Tests**: Added 8 new test cases covering table-specific caching, repository factories, and export service factories
- **Verification**: All tests pass with proper dependency injection and client caching behavior

## Implementation Steps & Change Log
- [x] ✅ Step 1: Extend ParticipantExportService with filtering - Completed 2025-09-22
  - [x] ✅ Sub-step 1.1: Add role-based filtering methods
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: Service supports filtering by TEAM and CANDIDATE roles
    - **Tests**: `tests/unit/test_services/test_participant_export_service.py`
    - **Done**: Role filtering methods tested with comprehensive coverage
    - **Changelog**: Added `get_participants_by_role_as_csv()` method with TEAM/CANDIDATE filtering

  - [x] ✅ Sub-step 1.2: Add department-based filtering methods
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: Service supports filtering by all 13 departments with proper validation
    - **Tests**: `tests/unit/test_services/test_participant_export_service.py`
    - **Done**: Department filtering methods tested for all department options
    - **Changelog**: Added `get_participants_by_department_as_csv()` method with comprehensive department support

- [ ] Step 2: Create BibleReaders export service
  - [ ] Sub-step 2.1: Implement BibleReadersExportService
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/bible_readers_export_service.py`
    - **Accept**: Service exports BibleReaders table data with proper CSV formatting, hydrating participant details via repository lookups
    - **Tests**: `tests/unit/test_services/test_bible_readers_export_service.py`
    - **Done**: BibleReaders table access and CSV generation working with dependency injection and participant hydration tests
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Create ROE export service
  - [ ] Sub-step 3.1: Implement ROEExportService
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/roe_export_service.py`
    - **Accept**: Service exports ROE table data with presenter, assistant, prayer, and scheduling metadata using factory-created repository
    - **Tests**: `tests/unit/test_services/test_roe_export_service.py`
    - **Done**: ROE table access and relationship/schedule data export working with dependency injection
    - **Changelog**: [Record changes made with file paths and line ranges]

- [x] ✅ Step 4: Update service factory integration - Completed 2025-09-22
  - [x] ✅ Sub-step 4.1: Extend ServiceFactory for new export services
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/service_factory.py`, `src/data/airtable/airtable_client_factory.py`
    - **Accept**: Factory resolves per-table repositories via shared client cache without reusing participant table config
    - **Tests**: `tests/unit/test_services/test_service_factory.py`, `tests/unit/test_data/test_airtable/test_airtable_client_factory.py`
    - **Done**: Service factory wiring reuses cached clients per table and exposes typed constructors for each export service
    - **Changelog**: Extended ServiceFactory with table-specific client caching and export service factory methods

## Testing Strategy
- [ ] Unit tests: Enhanced participant export service in tests/unit/test_services/
- [ ] Unit tests: BibleReaders export service with CSV validation
- [ ] Unit tests: ROE export service with relationship handling
- [ ] Unit tests: Service factory integration testing

## Success Criteria
- [x] ✅ Service factory delivers all export services using table-specific repositories
- [x] ✅ All filtering methods produce accurate participant subsets
- [x] ✅ BibleReaders export service generates proper CSV with all required fields
- [x] ✅ ROE export service handles presenter/assistant/prayer relationships and schedule fields correctly
- [x] ✅ Service factory properly instantiates all export services
- [x] ✅ All tests pass (100% required)
- [ ] Code review approved

## PR Traceability & Code Review Preparation
- **PR Created**: 2025-09-22
- **PR URL**: https://github.com/alexandrbasis/telegram-bot-v3/pull/55
- **Branch**: feature/TDB-68-export-services-and-filtering
- **Status**: In Review
- **Linear Issue**: TDB-68 - Updated to "In Review"

### Implementation Summary for Code Review
- **Total Steps Completed**: 4 of 4 steps
- **Test Coverage**: 87-91% for new export services (BibleReaders: 87%, ROE: 88%, ParticipantExport: 91%, ServiceFactory: 91%)
- **Total Tests**: 272 tests passing with 35+ new test cases across all export services
- **Key Files Modified**:
  - `src/services/participant_export_service.py:239-365` - Added role and department filtering methods
  - `src/services/bible_readers_export_service.py` - Complete export service with participant hydration
  - `src/services/roe_export_service.py` - Complete export service with multi-relationship hydration
  - `src/services/service_factory.py:18-210` - Extended factory with table-specific client caching
  - `tests/unit/test_services/test_*_export_service.py` - Comprehensive test suites for all services
- **Breaking Changes**: None - All changes are additive and maintain backward compatibility
- **Dependencies Added**: None - Uses existing dependencies

### Step-by-Step Completion Status
- [x] ✅ Step 1: Extend ParticipantExportService with filtering - Completed 2025-09-22
  - [x] ✅ Sub-step 1.1: Add role-based filtering methods (TEAM/CANDIDATE filtering with null exclusion)
  - [x] ✅ Sub-step 1.2: Add department-based filtering methods (All 13 departments with validation)
- [x] ✅ Step 2: Create BibleReaders export service - Completed 2025-09-22
  - [x] ✅ Sub-step 2.1: Implement BibleReadersExportService (CSV generation with participant hydration)
- [x] ✅ Step 3: Create ROE export service - Completed 2025-09-22
  - [x] ✅ Sub-step 3.1: Implement ROEExportService (Multi-relationship hydration with scheduling metadata)
- [x] ✅ Step 4: Update service factory integration - Completed 2025-09-22
  - [x] ✅ Sub-step 4.1: Extend ServiceFactory (Table-specific client caching and export service factories)

### Code Review Checklist
- [ ] **Functionality**: All acceptance criteria met (4 use cases fully implemented)
- [ ] **Testing**: Test coverage adequate (87-91% for new services, 272 total tests passing)
- [ ] **Code Quality**: Follows project conventions (proper error handling, progress tracking, CSV formatting)
- [ ] **Documentation**: Code comments and task documentation updated with implementation details
- [ ] **Security**: No sensitive data exposed (uses existing patterns)
- [ ] **Performance**: No obvious performance issues (efficient repository caching, proper hydration)
- [ ] **Integration**: Works with existing codebase (service factory pattern, backward compatibility)

### Implementation Notes for Reviewer
- **Role/Department Filtering**: Both filtering methods exclude participants with null values for the respective fields, ensuring clean filtered exports
- **Participant Hydration**: BibleReaders service resolves participant IDs to names using repository lookups for actionable CSV output
- **Multi-Relationship Hydration**: ROE service handles complex relationships (presenters, assistants, prayer partners) with proper null handling
- **Service Factory Pattern**: Extended factory maintains singleton client caching while supporting multiple table types without config reuse
- **Error Handling**: All services maintain existing patterns for progress tracking, file management, and graceful error recovery
- **CSV Formatting**: Consistent field ordering and formatting across all export services for uniform user experience

## Code Review Fixes - 2025-09-22

### Critical Issue Resolved
- **Issue**: ServiceFactory called `Settings.get_airtable_config()` with a `table_type` argument that the method didn't accept, causing TypeError at runtime
- **Root Cause**: API contract mismatch - `DatabaseSettings.to_airtable_config()` supported table_type but `Settings.get_airtable_config()` wrapper didn't
- **Fix Applied**: Extended `Settings.get_airtable_config()` to accept optional `table_type` parameter and pass it through to `DatabaseSettings.to_airtable_config()`
- **Files Modified**:
  - `src/config/settings.py:504-515` - Added table_type parameter support
  - `tests/unit/test_config/test_settings.py:512-547` - Added regression test for table-specific config
  - `tests/unit/test_services/test_service_factory.py:286-340` - Added real Settings integration tests
- **Testing**: All 1251 tests passing with 87% coverage (exceeds 80% requirement)
- **Commits**:
  - `bd3465b` - fix: add table_type parameter support to Settings.get_airtable_config
  - `faa87b4` - docs: add code review feedback document for tracking fixes

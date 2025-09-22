# Task: Export Services and Filtering
**Created**: 2025-01-19 | **Status**: Business Review

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
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Extend service factory to supply per-table export dependencies without breaking singleton caching
- [ ] Extend ParticipantExportService with role and department filtering
- [ ] Create BibleReadersExportService with proper CSV generation
- [ ] Create ROEExportService with relationship data handling
- [ ] Hydrate linked participant data (names, churches, rooms) within export services since lookup fields were removed upstream
- [ ] Update service factory to provide all export services
- [ ] Maintain consistent error handling and progress tracking

## Implementation Steps & Change Log
- [ ] Step 1: Extend ParticipantExportService with filtering
  - [ ] Sub-step 1.1: Add role-based filtering methods
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: Service supports filtering by TEAM and CANDIDATE roles
    - **Tests**: `tests/unit/test_services/test_participant_export_service.py`
    - **Done**: Role filtering methods tested with comprehensive coverage
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Add department-based filtering methods
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: Service supports filtering by all 13 departments with proper validation
    - **Tests**: `tests/unit/test_services/test_participant_export_service.py`
    - **Done**: Department filtering methods tested for all department options
    - **Changelog**: [Record changes made with file paths and line ranges]

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

- [ ] Step 4: Update service factory integration
  - [ ] Sub-step 4.1: Extend ServiceFactory for new export services
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/service_factory.py`, `src/data/airtable/airtable_client_factory.py`
    - **Accept**: Factory resolves per-table repositories via shared client cache without reusing participant table config
    - **Tests**: `tests/unit/test_services/test_service_factory.py`, `tests/unit/test_data/test_airtable/test_airtable_client_factory.py`
    - **Done**: Service factory wiring reuses cached clients per table and exposes typed constructors for each export service
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Enhanced participant export service in tests/unit/test_services/
- [ ] Unit tests: BibleReaders export service with CSV validation
- [ ] Unit tests: ROE export service with relationship handling
- [ ] Unit tests: Service factory integration testing

## Success Criteria
- [ ] Service factory delivers all export services using table-specific repositories
- [ ] All filtering methods produce accurate participant subsets
- [ ] BibleReaders export service generates proper CSV with all required fields
- [ ] ROE export service handles presenter/assistant/prayer relationships and schedule fields correctly
- [ ] Service factory properly instantiates all export services
- [ ] All tests pass (100% required)
- [ ] Code review approved

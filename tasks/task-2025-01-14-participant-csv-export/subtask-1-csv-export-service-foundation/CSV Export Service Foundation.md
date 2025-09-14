# Task: CSV Export Service Foundation
**Created**: 2025-01-14 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Create the foundational CSV export service that retrieves ALL participant data from Airtable and formats it into proper CSV structure with exact field name matching.

### Use Cases
1. **Administrative Data Export**: Service retrieves all participant records from repository and converts to CSV format identical to Airtable structure
   - **Acceptance Criteria**: Service class successfully calls repository.list_all() and returns well-formatted CSV string with all participant data

2. **Field Mapping Accuracy**: CSV headers and data match exact Airtable field names for seamless external usage
   - **Acceptance Criteria**: Exported CSV headers verified to match AirtableFieldMapping configuration exactly

3. **File Management Foundation**: Secure file generation with proper cleanup and size estimation for large datasets
   - **Acceptance Criteria**: CSV files created in secure temporary directory with automatic cleanup and size validation

### Success Metrics
- [ ] CSV export service successfully retrieves 100% of participant data from repository
- [ ] Field mapping integration ensures CSV headers match Airtable structure exactly
- [ ] File generation handles large datasets without memory issues
- [ ] Admin authentication utility properly validates authorized users
- [ ] Comprehensive test coverage (90%+) for all service methods

### Constraints
- Must handle large datasets (1000+ records) efficiently without memory exhaustion
- File size estimation must account for Telegram's 50MB upload limit
- Admin access control must be properly enforced using existing settings configuration
- Generated files must be automatically cleaned up to prevent disk space issues
- Use try-finally blocks for file cleanup to ensure execution even on errors
- Implement UTF-8 encoding explicitly for CSV output to support Russian text
- Use streaming for CSV generation to optimize memory for large datasets

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-57
- **URL**: https://linear.app/alexandrbasis/issue/TDB-57/subtask-1-csv-export-service-foundation
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Create ParticipantExportService class with repository dependency injection
- [ ] Implement get_all_participants_as_csv method using repository.list_all()
- [ ] Integrate AirtableFieldMapping for accurate column headers
- [ ] Add secure file generation with temporary directory management
- [ ] Implement file size estimation and Telegram limit validation
- [ ] Create admin authorization utility using existing settings configuration
- [ ] Add progress tracking capability for large dataset exports

## Implementation Steps & Change Log
- [ ] Step 1: Create CSV Export Service
  - [ ] Sub-step 1.1: Create participant export service class
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: Service class created with constructor accepting ParticipantRepository
    - **Tests**: `tests/unit/test_services/test_participant_export_service.py`
    - **Done**: `pytest tests/unit/test_services/test_participant_export_service.py -v` passes
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Implement get_all_participants_as_csv method using repository.list_all()
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: Method calls `repository.list_all()` to retrieve ALL participants and returns CSV string
    - **Tests**: Add test cases to `tests/unit/test_services/test_participant_export_service.py`
    - **Done**: Method successfully exports all participants from repository to valid CSV format
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.3: Add field mapping integration for Airtable column headers
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: CSV headers match exact Airtable field names from AirtableFieldMapping
    - **Tests**: Add field mapping test cases
    - **Done**: Exported CSV headers verified to match Airtable structure
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Add File Management Capabilities
  - [ ] Sub-step 2.1: Implement secure file generation and storage
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: CSV files saved to secure temporary directory with unique filenames
    - **Tests**: Add file creation and cleanup test cases
    - **Done**: Files created with proper permissions and automatic cleanup
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 2.2: Add file size estimation and Telegram limit handling
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: Service estimates CSV size before generation and handles Telegram's 50MB limit
    - **Tests**: Add file size estimation and limit handling test cases
    - **Done**: File size checked before upload with appropriate user warnings for large files
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 2.3: Add progress tracking for large datasets
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_export_service.py`
    - **Accept**: Service provides progress callbacks for UI updates during export
    - **Tests**: Add progress tracking mock verification tests
    - **Done**: Progress callbacks fire correctly during export process
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Create Authentication Utilities
  - [ ] Sub-step 3.1: Create admin authorization utility
    - **Directory**: `src/utils/`
    - **Files to create/modify**: `src/utils/auth_utils.py`
    - **Accept**: Function `is_admin_user(user_id: int, settings: Settings) -> bool` created
    - **Tests**: `tests/unit/test_utils/test_auth_utils.py`
    - **Done**: Admin check utility tested with various user IDs and settings configurations
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Service methods in `tests/unit/test_services/test_participant_export_service.py`
- [ ] Unit tests: Auth utilities in `tests/unit/test_utils/test_auth_utils.py`
- [ ] Integration tests: Repository integration in `tests/integration/test_csv_export_repository.py`

## Success Criteria
- [ ] All acceptance criteria met
- [ ] Tests pass (100% required)
- [ ] No regressions
- [ ] Code review approved
- [ ] Service successfully exports all participant data to properly formatted CSV
- [ ] Admin authentication utility properly validates authorized users
- [ ] File management handles large datasets with proper cleanup
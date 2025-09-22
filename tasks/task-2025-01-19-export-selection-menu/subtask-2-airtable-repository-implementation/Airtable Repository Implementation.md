# Task: Airtable Repository Implementation
**Created**: 2025-01-19 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement concrete Airtable repository classes for BibleReaders and ROE tables that provide reliable data access functionality using the established repository interfaces.

### Use Cases
1. **BibleReaders Data Access**: System can retrieve reading assignments, locations, and participant details
   - **Acceptance Criteria**: Repository correctly accesses BibleReaders table (ID: tblGEnSfpPOuPLXcm) and maps the current fields (Where, Participants, When, Bible)
2. **ROE Data Access**: System can retrieve ROE topics along with presenters, assistants, prayer partners, and schedule metadata
   - **Acceptance Criteria**: Repository correctly accesses ROE table (ID: tbl0j8bcgkV3lVAdc) and handles presenter/assistant/prayer relationships plus the new date/time/duration fields
3. **Multi-Table Client Management**: System efficiently manages connections to multiple Airtable tables
   - **Acceptance Criteria**: Repository implementations use factory-created clients without connection conflicts

### Success Metrics
- [ ] BibleReaders repository correctly maps all table fields and relationships
- [ ] ROE repository handles presenter/assistant/prayer relationships and scheduling fields accurately
- [ ] Repository implementations follow existing Airtable client patterns

### Constraints
- Must use specific table IDs: BibleReaders (tblGEnSfpPOuPLXcm), ROE (tbl0j8bcgkV3lVAdc)
- Must maintain existing rate limiting and error handling patterns
- Must use factory-created clients for proper dependency injection

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-67
- **URL**: https://linear.app/alexandrbasis/issue/TDB-67/subtask-2-airtable-repository-implementation
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Provide BibleReaders/ROE field ID and option mapping utilities
- [ ] Implement BibleReaders Airtable repository with proper field mapping
- [ ] Implement ROE Airtable repository with relationship handling
- [ ] Integrate with client factory for dependency injection
- [ ] Maintain consistency with existing AirtableParticipantRepo patterns

## Implementation Steps & Change Log
- [ ] Step 0: Add multi-table field mappings
  - [ ] Sub-step 0.1: Define BibleReaders mapping helper
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/field_mappings/bible_readers.py`
    - **Accept**: Mapping exposes Airtable field IDs and python↔Airtable translations for the active BibleReaders fields (Where, Participants, When, Bible)
    - **Tests**: `tests/unit/test_config/test_field_mappings_bible_readers.py`
    - **Done**: Helper converts to/from Airtable schema without relying on participant mapping and enforces localized date formatting (`format = l`)
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 0.2: Define ROE mapping helper
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/field_mappings/roe.py`
    - **Accept**: Mapping exposes Airtable field IDs and python↔Airtable translations for ROE exports including schedule fields and prayer links
    - **Tests**: `tests/unit/test_config/test_field_mappings_roe.py`
    - **Done**: Helper handles presenter/assistant/prayer relationship validation plus date/duration conversions
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 1: Implement BibleReaders repository
  - [ ] Sub-step 1.1: Create AirtableBibleReadersRepo class
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_bible_readers_repo.py`
    - **Accept**: Repository implements BibleReadersRepository interface using table ID tblGEnSfpPOuPLXcm
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_bible_readers_repo.py`
    - **Done**: Repository correctly maps BibleReaders fields and participant relationships
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Implement ROE repository
  - [ ] Sub-step 2.1: Create AirtableROERepo class
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_roe_repo.py`
    - **Accept**: Repository implements ROERepository interface using table ID tbl0j8bcgkV3lVAdc
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_roe_repo.py`
    - **Done**: Repository correctly handles ROE presenter, assistant, and prayer relationships plus schedule fields
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Integration testing
  - [ ] Sub-step 3.1: Test multi-table repository coordination
    - **Directory**: `tests/integration/`
    - **Files to create/modify**: `tests/integration/test_multi_table_repositories.py`
    - **Accept**: Repositories work together without connection conflicts using factory pattern
    - **Tests**: Integration tests for concurrent table access
    - **Done**: Multi-table access tests pass with proper client isolation
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Field mapping helpers in tests/unit/test_config/field_mappings/
- [ ] Unit tests: Repository implementations in tests/unit/test_data/test_airtable/
- [ ] Integration tests: Multi-table coordination in tests/integration/

## Success Criteria
- [ ] Field mapping helpers translate BibleReaders/ROE schemas accurately
- [ ] BibleReaders repository accesses correct table with proper field mapping
- [ ] ROE repository handles presenter/assistant/prayer relationships and schedule fields correctly
- [ ] All repository operations follow existing error handling patterns
- [ ] All tests pass (100% required)
- [ ] Code review approved

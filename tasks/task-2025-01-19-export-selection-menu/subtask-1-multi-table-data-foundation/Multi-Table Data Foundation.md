# Task: Multi-Table Data Foundation
**Created**: 2025-01-19 | **Status**: In Progress (2025-01-21)

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Establish the foundational data layer infrastructure to support multi-table export functionality by creating data models and repository interfaces for BibleReaders and ROE tables.

### Use Cases
1. **Data Model Validation**: System can validate BibleReaders data with fields (Where, Participants, Church, RoomNumber, When, Bible)
   - **Acceptance Criteria**: Pydantic model correctly validates all BibleReaders table fields and relationships
2. **ROE Data Structure**: System can validate ROE data with fields (RoeTopic, Roista, Assistant, lookup fields)
   - **Acceptance Criteria**: Pydantic model correctly validates ROE table structure and presenter relationships
3. **Repository Interface Consistency**: Data access follows consistent patterns across all table types
   - **Acceptance Criteria**: Repository interfaces provide standardized CRUD operations following existing ParticipantRepository pattern

### Success Metrics
- [ ] All data models pass validation tests with proper type checking
- [ ] Repository interfaces maintain consistency with existing patterns
- [ ] Foundation supports future export service implementation

### Constraints
- Must follow existing ParticipantRepository interface patterns
- Data models must match exact Airtable table structures
- Repository interfaces must support dependency injection

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-66
- **URL**: https://linear.app/alexandrbasis/issue/TDB-66/subtask-1-multi-table-data-foundation
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: feature/TDB-66-multi-table-data-foundation
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
Enabling multi-table data export capabilities by establishing consistent data models and repository patterns for BibleReaders and ROE tables.

## Technical Requirements
- [ ] Extend Airtable configuration to expose BibleReaders/ROE table identifiers and reusable client settings
- [ ] Document new environment variables in `.env.example` and Airtable database docs
- [ ] Create BibleReaders Pydantic model with complete field definitions
- [ ] Create ROE Pydantic model with presenter relationship handling
- [ ] Create abstract repository interfaces for BibleReaders and ROE
- [ ] Implement repository factory pattern for multi-table client creation
- [ ] Establish foundation for dependency injection

## Implementation Steps & Change Log
- [ ] Step 0: Extend multi-table settings and documentation
  - [ ] Sub-step 0.1: Update Airtable settings for additional tables
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/settings.py`, `.env.example`
    - **Accept**: `DatabaseSettings`/`AirtableConfig` expose participants, BibleReaders, and ROE table metadata with defaults
    - **Tests**: `tests/unit/test_config/test_settings.py`
    - **Done**: New environment variables validated with defaults and error cases
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 0.2: Update Airtable structure documentation
    - **Directory**: `docs/data-integration/`
    - **Files to create/modify**: `docs/data-integration/airtable_database_structure.md`
    - **Accept**: Documentation lists table IDs/field references for BibleReaders and ROE exports
    - **Tests**: Documentation review checklist
    - **Done**: Docs reflect new configuration variables and schemas
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 1: Create BibleReaders data model
  - [ ] Sub-step 1.1: Create BibleReaders Pydantic model
    - **Directory**: `src/models/`
    - **Files to create/modify**: `src/models/bible_readers.py`
    - **Accept**: Pydantic model with all fields from BibleReaders table (Where, Participants, Church, RoomNumber, When, Bible)
    - **Tests**: `tests/unit/test_models/test_bible_readers.py`
    - **Done**: Model validates all field types and relationships correctly
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Create ROE data model
  - [ ] Sub-step 2.1: Create ROE Pydantic model
    - **Directory**: `src/models/`
    - **Files to create/modify**: `src/models/roe.py`
    - **Accept**: Pydantic model with all fields from ROE table (RoeTopic, Roista, Assistant, lookup fields)
    - **Tests**: `tests/unit/test_models/test_roe.py`
    - **Done**: Model validates ROE structure and presenter relationships correctly
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Create repository interfaces
  - [ ] Sub-step 3.1: Create BibleReaders repository interface
    - **Directory**: `src/data/repositories/`
    - **Files to create/modify**: `src/data/repositories/bible_readers_repository.py`
    - **Accept**: Abstract base class following existing ParticipantRepository pattern
    - **Tests**: `tests/unit/test_data/test_repositories/test_bible_readers_repository.py`
    - **Done**: Repository interface provides consistent CRUD operations
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 3.2: Create ROE repository interface
    - **Directory**: `src/data/repositories/`
    - **Files to create/modify**: `src/data/repositories/roe_repository.py`
    - **Accept**: Abstract base class following existing ParticipantRepository pattern
    - **Tests**: `tests/unit/test_data/test_repositories/test_roe_repository.py`
    - **Done**: Repository interface provides consistent CRUD operations
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Create Airtable client factory
  - [ ] Sub-step 4.1: Implement table-specific client factory
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_client_factory.py`
    - **Accept**: Factory creates clients for different table IDs maintaining single-table client pattern
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_client_factory.py`
    - **Done**: Factory provides clients for Participants, BibleReaders, ROE tables
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Settings validation in tests/unit/test_config/
- [ ] Unit tests: Data models in tests/unit/test_models/
- [ ] Unit tests: Repository interfaces in tests/unit/test_data/test_repositories/
- [ ] Unit tests: Client factory in tests/unit/test_data/test_airtable/

## Success Criteria
- [ ] Configuration exposes all table metadata with passing settings tests
- [ ] All data models validate correctly with type safety
- [ ] Repository interfaces provide consistent API
- [ ] Client factory creates table-specific clients
- [ ] All tests pass (100% required)
- [ ] Code review approved
# Task: Export Selection Menu
**Created**: 2025-01-19 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)

### Business Context
Enable administrators to selectively export specific participant subsets instead of downloading the entire database every time.

### Primary Objective
Provide an interactive selection menu when using the `/export` command that allows administrators to choose exactly which participant data they want to export, reducing file sizes and improving data relevance.

### Use Cases
1. **Export by Role**: An admin preparing for a team meeting needs to export only TEAM member data without candidate information
   - **Acceptance Criteria**: User can select "Export Team Members" and receive CSV containing only participants with Role=TEAM

2. **Department-Specific Export**: Event coordinator needs to export participants from a specific department (e.g., Kitchen) to share with department leaders
   - **Acceptance Criteria**: User can select department from a list and receive CSV containing only participants from that department

3. **Export All Candidates**: Registration team needs candidate-only list for processing applications
   - **Acceptance Criteria**: User can select "Export Candidates" and receive CSV containing only participants with Role=CANDIDATE

4. **Export Bible Readers**: Ministry coordinator needs to export data from the BibleReaders table (ID: `tblGEnSfpPOuPLXcm`)
   - **Acceptance Criteria**: User can select "Export Bible Readers" and receive CSV with reading assignments, locations, and participant details

5. **Export ROE Sessions**: Ministry coordinator needs to export data from the ROE table (ID: `tbl0j8bcgkV3lVAdc`)
   - **Acceptance Criteria**: User can select "Export ROE Sessions" and receive CSV with ROE topics, presenters, and assistant assignments

6. **Quick Full Export**: Admin still needs ability to export all participants when needed
   - **Acceptance Criteria**: User can select "Export All Participants" to maintain current functionality

### Success Metrics
- [ ] Reduced average export file size by allowing targeted data selection
- [ ] Improved admin workflow efficiency with fewer manual filtering steps needed post-export
- [ ] Maintained backwards compatibility with option for full export

### Constraints
- Must maintain current security model (admin-only access)
- File size limits still apply (Telegram 50MB limit)
- Must handle empty result sets gracefully with appropriate user messaging
- Bible Readers and ROE are separate tables in Airtable (see `/docs/data-integration/airtable_database_structure.md` for complete table specifications)

**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-19

## Test Plan
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-19

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

### Proposed Test Categories

#### Business Logic Tests
- [ ] Export menu keyboard generation with correct export options
- [ ] Role-based filtering logic for TEAM vs CANDIDATE exports
- [ ] Department-based filtering with all 13 departments (ROE, Chapel, Setup, Palanka, Administration, Kitchen, Decoration, Bell, Refreshment, Worship, Media, Clergy, Rectorate)
- [ ] Multi-table export service for BibleReaders and ROE tables
- [ ] CSV field mapping for different export types (participants vs Bible readers vs ROE)
- [ ] Export selection validation and user input processing

#### State Transition Tests
- [ ] Export command flow: /export → selection menu → export processing → file delivery
- [ ] Selection menu state management with proper keyboard updates
- [ ] Cancel export workflow returning to main menu state
- [ ] Progress tracking state during export processing for large datasets
- [ ] Error recovery state transitions from failed exports

#### Error Handling Tests
- [ ] Empty result set handling for each export type with descriptive user messages
- [ ] File size limit validation and warning messages for large exports
- [ ] Airtable API failure handling during multi-table access
- [ ] Invalid department selection handling with error recovery
- [ ] Network failure during BibleReaders/ROE table access

#### Integration Tests
- [ ] BibleReaders table API access using table ID `tblGEnSfpPOuPLXcm`
- [ ] ROE table API access using table ID `tbl0j8bcgkV3lVAdc`
- [ ] Multi-table relationship data export (participants linked to Bible readings)
- [ ] Airtable client configuration for accessing multiple tables
- [ ] Service factory integration for new export types

#### User Interaction Tests
- [ ] Export selection keyboard presentation and option selection
- [ ] Progress notification display during large department exports
- [ ] File delivery confirmation messages with export type identification
- [ ] Admin permission validation before showing export options
- [ ] Export completion messages with file statistics

### Test-to-Requirement Mapping
- **Export Team Members** → Role-based filtering tests, TEAM role validation tests
- **Export Candidates** → Role-based filtering tests, CANDIDATE role validation tests
- **Department Export** → Department filtering tests, all 13 department validation tests
- **Bible Readers Export** → BibleReaders table access tests, multi-table API tests
- **ROE Sessions Export** → ROE table access tests, relationship data export tests
- **Full Export** → Backwards compatibility tests, existing functionality preservation tests

## Tracking & Progress
### Linear Issue
- **ID**: AGB-65
- **URL**: https://linear.app/alexandrbasis/issue/AGB-65/export-selection-menu-interactive-export-options

### Task Splitting Evaluation
**Status**: ✅ Split into 4 Sub-tasks | **Evaluated by**: Task Splitter Agent | **Date**: 2025-01-19
**Decision**: Task split due to complexity (16 sub-steps, multi-table architecture, conversation state management)

### Sub-task Dependencies
1. **TDB-66**: Multi-Table Data Foundation → **TDB-67**: Airtable Repository Implementation
2. **TDB-67**: Airtable Repository Implementation → **TDB-68**: Export Services and Filtering
3. **TDB-68**: Export Services and Filtering → **TDB-69**: Conversation UI Integration

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-01-19

### Plan Review Feedback Addressed
**Critical Issues Resolved:**
- ✅ **Data Models Created**: Added BibleReaders and ROE Pydantic models with complete field definitions
- ✅ **Multi-Table Architecture**: Implemented table-specific client factory pattern maintaining single-table clients
- ✅ **Repository Pattern**: Created abstract interfaces following existing ParticipantRepository pattern
- ✅ **Conversation State Management**: Defined ConversationHandler states, transitions, and callback data structure
- ✅ **Service Factory Integration**: Planned proper dependency injection avoiding circular dependencies

### Technical Requirements
- [ ] Convert `/export` command from direct export to interactive conversation flow
- [ ] Implement export selection menu with 6 predefined options
- [ ] Create multi-table export services for BibleReaders and ROE tables
- [ ] Extend existing ParticipantExportService with filtering capabilities
- [ ] Implement conversation state management for export selection workflow
- [ ] Add progress tracking support for filtered exports
- [ ] Maintain backwards compatibility with existing export functionality

### Implementation Steps & Change Log

- [ ] Step 0: Extend configuration for multi-table exports → **NEW**
  - **Description**: Update settings, environment templates, and documentation to expose BibleReaders/ROE table metadata
  - **Details**: Extend `DatabaseSettings`/`AirtableConfig` for multiple table IDs, add `.env.example` variables, document defaults in `/docs/data-integration/airtable_database_structure.md`
  - **Tests**: `tests/unit/test_config/test_settings.py` (update)
  - **Dependencies**: None – required before repository/model work

- [ ] Step 1: Create Data Models and Repository Infrastructure → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-1-multi-table-data-foundation/Multi-Table Data Foundation.md`
  - **Description**: Establish foundational data layer with BibleReaders/ROE models, repository interfaces, and client factory
  - **Linear Issue**: TDB-66
  - **Dependencies**: None - this is the foundation for all other subtasks

- [ ] Step 2: Extend Airtable Client Architecture for Multi-Table Support → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-2-airtable-repository-implementation/Airtable Repository Implementation.md`
  - **Description**: Implement concrete Airtable repositories for BibleReaders and ROE tables with proper table ID mapping
  - **Linear Issue**: TDB-67
  - **Dependencies**: Requires completion of Subtask 1 (data models and interfaces)

- [ ] Step 3: Create Export Selection Infrastructure → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-4-conversation-ui-integration/Conversation UI Integration.md`
  - **Description**: Convert /export command to interactive conversation flow with selection menu and state management
  - **Linear Issue**: TDB-69
  - **Dependencies**: Requires completion of Subtask 3 (export services) for service integration

- [ ] Step 4: Extend Export Services with Filtering → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-3-export-services-and-filtering/Export Services and Filtering.md`
  - **Description**: Create BibleReaders/ROE export services and extend ParticipantExportService with role/department filtering
  - **Linear Issue**: TDB-68
  - **Dependencies**: Requires completion of Subtask 2 (repository implementations) for data access

- [ ] Step 5: Update Service Factory and Integration → **MERGED INTO SUBTASKS**
  - **Integration**: Service factory updates included in Subtask 3 (Export Services)
  - **Integration**: Handler updates included in Subtask 4 (Conversation UI)
  - **Rationale**: These integration points are better handled within their respective functional areas

- [ ] Step 6: Integration Testing and Documentation → **DISTRIBUTED ACROSS SUBTASKS**
  - **Integration**: Repository integration testing included in Subtask 2
  - **Integration**: Export service integration testing included in Subtask 3
  - **Integration**: End-to-end workflow testing included in Subtask 4
  - **Integration**: Main application registration included in Subtask 4
  - **Rationale**: Integration testing is more effective when distributed within each functional area

### Constraints
- Must maintain admin-only access control throughout selection workflow
- File size validation required for all export types
- Progress tracking must work across all export options
- Error handling must be consistent with existing export functionality
- Database structure references in `/docs/data-integration/airtable_database_structure.md`
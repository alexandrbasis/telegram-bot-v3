# Task: Repository and Service Layer Department Filtering
**Created**: 2025-01-19 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement department filtering and chief-first sorting in the data and service layers to enable efficient participant retrieval by department with proper hierarchical ordering.

### Use Cases
1. **Retrieve participants by department**: System can filter participants based on department assignment
   - **Acceptance Criteria**:
     - Repository supports filtering by specific department (ROE, Chapel, etc.)
     - Repository supports "all participants" retrieval (no filter)
     - Repository supports "unassigned" participants (null department)
     - Airtable formulas generate correctly for each filter type
     - Results include all necessary participant data

2. **Department chief prioritization**: Chiefs appear first in all filtered lists
   - **Acceptance Criteria**:
     - Chiefs (IsDepartmentChief = true) always appear at top of lists
     - Airtable sorting includes IsDepartmentChief field as primary sort
     - Secondary sort by Church field alphabetically
     - Null/empty church values appear at end of list
     - Sorting is case-insensitive

3. **Visual chief identification**: Chiefs are clearly marked in list display
   - **Acceptance Criteria**:
     - Chiefs display with crown emoji (👑) indicator
     - Chief status shows before participant name
     - Visual formatting consistent across all lists
     - Indicator works with existing list formatting

### Success Metrics
- [ ] Department filtering reduces query results by 80-90% for targeted searches
- [ ] Chiefs consistently appear first in all department lists
- [ ] Visual indicators clearly distinguish department leadership
- [ ] Performance maintains sub-1-second response times

### Constraints
- Must work with existing Airtable schema and API limitations
- Rate limiting (5 req/sec) must be respected
- Backward compatibility with existing list functionality required
- All department names must match enum values exactly

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-64
- **URL**: https://linear.app/alexandrbasis/issue/TDB-64/subtask-2-repository-and-service-layer-department-filtering
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Extend repository interface with department filtering capability
- [ ] Implement Airtable filtering with complex formula generation
- [ ] Add multi-field sorting (IsDepartmentChief, then Church)
- [ ] Extend service layer with department parameter support while keeping existing callers working via sensible defaults
- [ ] Add visual chief indicators to list formatting
- [ ] Ensure proper error handling for invalid departments

## Implementation Steps & Change Log
- [ ] Step 1: Extend Repository with Filtering and Sorting
  - [ ] Sub-step 1.1: Add department filtering to participant repository
    - **Directory**: `src/data/repositories/`
    - **Files to create/modify**: `src/data/repositories/participant_repository.py`
    - **Accept**: Abstract method for filtered retrieval defined
    - **Tests**: Test in `tests/unit/test_data/test_repositories/test_participant_repository.py`
    - **Done**: Repository interface includes get_team_members_by_department method
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Implement Airtable filtering with sorting
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_participant_repo.py`
    - **Accept**: Implementation generates correct Airtable formulas and sort parameters
    - **Tests**: Test in `tests/unit/test_data/test_airtable/test_airtable_participant_repo.py`
    - **Done**: Airtable queries include Department filter and IsDepartmentChief/Church sorting
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Update List Service with Department Filtering
  - [ ] Sub-step 2.1: Add optional department parameter to list service methods
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_list_service.py`
    - **Accept**: Service accepts an optional department filter (defaulting to current behaviour when omitted) and applies chief-first sorting logic without breaking existing call sites
    - **Tests**: Test in `tests/unit/test_services/test_participant_list_service.py`
    - **Done**: Service methods support department filtering with chief-first sorting
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 2.2: Add chief indicator formatting to list display
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_list_service.py`
    - **Accept**: Chiefs marked with visual indicator in formatted output
    - **Tests**: Verify formatting in `tests/unit/test_services/test_participant_list_service.py`
    - **Done**: List display shows "👑" for department chiefs
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Repository filtering logic in `tests/unit/test_data/test_repositories/`
- [ ] Unit tests: Airtable formula generation in `tests/unit/test_data/test_airtable/`
- [ ] Unit tests: Service layer filtering in `tests/unit/test_services/`
- [ ] Integration tests: End-to-end data flow with real filtering

## Success Criteria
- [ ] All acceptance criteria met
- [ ] Tests pass (100% required)
- [ ] No regressions in existing list functionality
- [ ] Code review approved
- [ ] Data layer ready for handler integration in next subtask

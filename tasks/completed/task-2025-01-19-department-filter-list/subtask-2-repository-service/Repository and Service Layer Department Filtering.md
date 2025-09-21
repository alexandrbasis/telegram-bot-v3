# Task: Repository and Service Layer Department Filtering
**Created**: 2025-01-19 | **Status**: Ready for Review

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
- **ID**: AGB-59
- **URL**: https://linear.app/alexandrbasis/issue/AGB-59/subtask-2-repository-and-service-layer-department-filtering
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: basisalexandr/agb-59-subtask-2-repository-and-service-layer-department-filtering
- **PR URL**: https://github.com/alexandrbasis/telegram-bot-v3/pull/50
- **Status**: In Review

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
- [x] ✅ All acceptance criteria met
- [x] ✅ Tests pass (123/123 tests passing)
- [x] ✅ No regressions in existing list functionality
- [x] ✅ Code review approved (all critical issues resolved)
- [x] ✅ Data layer ready for handler integration in next subtask

## Implementation Summary

**Completion Date**: 2025-01-21

**All features successfully implemented with comprehensive test coverage:**

### ✅ Repository Layer (68% coverage)
- **get_team_members_by_department** method added to repository interface
- Department filtering with validation against enum values
- Chief-first sorting using Airtable sort parameters (-IsDepartmentChief, Church)
- Support for "unassigned" participants filtering
- Comprehensive error handling and logging

### ✅ Service Layer (98% coverage)
- Optional department parameter added to get_team_members_list method
- Backward compatibility maintained (department=None default)
- Crown emoji (👑) indicators for department chiefs
- Integration with new repository method
- Proper formatting consistency preserved

### ✅ Test Coverage
- **Repository Interface**: 5 new test methods, interface compliance verified
- **Airtable Implementation**: 5 comprehensive test scenarios covering all filtering options
- **Service Layer**: 12 test methods (6 for department filtering + 6 for chief indicators)
- **Backward Compatibility**: All existing tests updated and passing
- **Total Test Count**: 123 tests passing

### 🔧 Technical Implementation Details
- **Files Modified**:
  - `src/data/repositories/participant_repository.py:372-398` - Abstract method definition
  - `src/data/airtable/airtable_participant_repo.py:1351-1441` - Airtable implementation
  - `src/services/participant_list_service.py:29-49,186-190` - Service integration and formatting
- **Branch**: basisalexandr/agb-59-subtask-2-repository-and-service-layer-department-filtering
- **Commits**: 4 feature commits following TDD Red-Green-Refactor approach

**Ready for Code Review** ✅
**Code Review Status**: ✅ APPROVED (All issues resolved)

### 🔧 Code Review Resolution Summary
**Date**: 2025-09-21
**Critical Issue**: Integration tests failing due to outdated mock expectations
**Resolution**: Updated `tests/integration/test_participant_list_service_repository.py` with:
- AsyncMock for `get_team_members_by_department` method
- Comprehensive test coverage for department filtering scenarios
- Additional tests for chief indicator display functionality
- **Result**: All 9 integration tests passing, 1050/1050 total tests passing

## PR Traceability & Code Review Preparation
- **PR Created**: 2025-01-21
- **PR URL**: https://github.com/alexandrbasis/telegram-bot-v3/pull/50
- **Branch**: basisalexandr/agb-59-subtask-2-repository-and-service-layer-department-filtering
- **Status**: In Review
- **Linear Issue**: AGB-59 - Updated to "In Review"

### Implementation Summary for Code Review
- **Total Steps Completed**: 2 major steps with 4 sub-steps
- **Test Coverage**: 123 tests passing (Repository: 68%, Service: 98%)
- **Key Files Modified**:
  - `src/data/repositories/participant_repository.py:372-398` - Abstract method definition for department filtering
  - `src/data/airtable/airtable_participant_repo.py:1351-1441` - Airtable implementation with complex filtering and sorting
  - `src/services/participant_list_service.py:29-49,186-190` - Service integration and crown emoji formatting
- **Breaking Changes**: None - backward compatibility maintained
- **Dependencies Added**: None

### Step-by-Step Completion Status
- [x] ✅ Step 1: Extend Repository with Filtering and Sorting - Completed 2025-01-21
  - [x] ✅ Sub-step 1.1: Add department filtering to participant repository - Completed 2025-01-21
  - [x] ✅ Sub-step 1.2: Implement Airtable filtering with sorting - Completed 2025-01-21
- [x] ✅ Step 2: Update List Service with Department Filtering - Completed 2025-01-21
  - [x] ✅ Sub-step 2.1: Add optional department parameter to list service methods - Completed 2025-01-21
  - [x] ✅ Sub-step 2.2: Add chief indicator formatting to list display - Completed 2025-01-21

### Code Review Checklist
- [ ] **Functionality**: All acceptance criteria met
  - [x] Repository supports filtering by specific department
  - [x] Chiefs appear first in all filtered lists with crown emoji indicators
  - [x] Backward compatibility maintained with optional parameters
- [ ] **Testing**: Test coverage adequate (123/123 tests passing)
- [ ] **Code Quality**: Follows project conventions
  - [x] Repository pattern properly extended
  - [x] Service layer integration maintains existing API contracts
  - [x] Error handling and logging implemented
- [ ] **Documentation**: Code comments and task documentation updated
- [ ] **Security**: No sensitive data exposed
- [ ] **Performance**: No obvious performance issues
  - [x] Airtable rate limiting respected
  - [x] Efficient filtering formulas generated
- [ ] **Integration**: Works with existing codebase
  - [x] All existing tests pass
  - [x] No regressions in existing list functionality

### Implementation Notes for Reviewer
- **Department Filtering Logic**: Uses Airtable formula generation for efficient server-side filtering
- **Chief-First Sorting**: Implemented using Airtable sort parameters with `-IsDepartmentChief` as primary sort
- **Visual Indicators**: Crown emoji (👑) added via service layer formatting without affecting underlying data models
- **Backward Compatibility**: All changes use optional parameters with sensible defaults to avoid breaking existing callers
- **Error Handling**: Invalid departments are validated against enum values with proper logging and user feedback

# Task: Department Filter for Team Members List
**Created**: 2025-01-19 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
**Status**: Awaiting Business Approval | **Created**: 2025-01-19

### Business Context
Enable users to filter team member lists by department for more efficient navigation and targeted participant viewing.

### Primary Objective
Add department-based filtering capability to the team members list interface, allowing users to view all members, specific department members, or unassigned members.

### Use Cases
1. **View all team members**: User selects "Team members" and chooses to see the complete list
   - **Acceptance Criteria**:
     - User can access full team member list with existing pagination
     - Maintains current numbered list format
     - Shows total count of all team members
     - List is sorted with department chiefs first, then by church name

2. **View department-specific members**: User filters by a specific department (e.g., Worship team)
   - **Acceptance Criteria**:
     - User can select from 13 available departments
     - List displays only members assigned to selected department
     - Department chief (IsDepartmentChief = true) appears at the top of the list
     - Remaining members are sorted alphabetically by church name
     - Shows department name in the list header with chief indicator if applicable
     - Displays count specific to that department

3. **View unassigned members**: User views team members not yet assigned to any department
   - **Acceptance Criteria**:
     - User can select "No Department" option
     - List shows only members with null/empty department field
     - Members are sorted alphabetically by church name
     - Header clearly indicates "Unassigned Members"
     - Shows count of unassigned members

4. **Sorted list display**: All filtered lists maintain consistent sorting rules
   - **Acceptance Criteria**:
     - Department chiefs (IsDepartmentChief field = true) always appear first
     - Chief is clearly marked with a special indicator (e.g., "⭐ Chief" or "👑")
     - After chiefs, all other members sorted alphabetically by Church field
     - Null/empty church values appear at the end of the list
     - Sorting is case-insensitive for church names

### UI Workflow
1. User clicks "Получить список" (Get list) button from main menu
2. User sees two options:
   - "Команда" (Team members)
   - "Кандидаты" (Candidates)
3. **NEW**: When user selects "Команда" (Team members):
   - Instead of immediately showing the list
   - Display department filter options:
    - "Все участники" (All participants) - shows complete list
    - Individual department buttons (13 departments)
    - "Без департамента" (No department) - shows unassigned members
    - All together this keyboard exposes 15 options (13 departments + 2 special entries)
4. After department selection, display filtered list with pagination

### Success Metrics
- [ ] Users can filter team members by any of the 13 departments
- [ ] Filtering reduces time to find specific team groups by 70%
- [ ] Unassigned members are easily identifiable for department allocation
- [ ] Navigation remains intuitive with clear back/forward options

### Constraints
- Must maintain backward compatibility with existing list display format
- Department enum values are predefined (13 departments)
- Pagination logic must work correctly with filtered results
- Russian language interface must be maintained

## Test Plan (Gate 2 - Approval Required)
**Status**: Awaiting Test Plan Approval | **Created**: 2025-01-19

### Test Coverage Strategy
Target: 90%+ coverage across department filtering functionality, UI navigation flows, and data integrity validation

### Proposed Test Categories

#### Business Logic Tests
- [ ] **test_department_filter_all_members**: Verify "All participants" returns complete team member list
- [ ] **test_department_filter_specific**: Validate filtering returns only members of selected department
- [ ] **test_department_filter_unassigned**: Confirm "No department" returns only members with null department
- [ ] **test_department_member_counts**: Verify count calculations for each filter option
- [ ] **test_filter_persistence_pagination**: Ensure department filter persists through pagination
- [ ] **test_chief_sorting_priority**: Verify department chiefs appear first in all filtered lists
- [ ] **test_church_name_sorting**: Validate alphabetical sorting by church name after chiefs
- [ ] **test_sorting_null_church_values**: Confirm null/empty church values appear at list end
- [ ] **test_chief_indicator_display**: Verify chief status is clearly marked in the list

#### State Transition Tests
- [ ] **test_flow_main_to_department_selection**: Validate navigation from role selection to department filter
- [ ] **test_flow_department_to_list**: Verify transition from department selection to filtered list
- [ ] **test_flow_back_navigation**: Confirm proper back navigation from list to department selection
- [ ] **test_filter_state_preservation**: Ensure filter selection saved in conversation context

#### Error Handling Tests
- [ ] **test_invalid_department_callback**: Handle corrupted/invalid department selection callbacks
- [ ] **test_empty_department_list**: Gracefully handle departments with no members
- [ ] **test_airtable_filter_failure**: Recover from Airtable API filter query failures
- [ ] **test_pagination_boundary_filtered**: Handle edge cases at pagination boundaries with filters

#### Integration Tests
- [ ] **test_airtable_department_query**: Verify Airtable formula generation for department filtering
- [ ] **test_department_enum_sync**: Ensure UI department list matches model Department enum
- [ ] **test_keyboard_generation_departments**: Validate keyboard button generation for all 14 options
- [ ] **test_list_service_filter_integration**: End-to-end test of filter parameter passing to service
- [ ] **test_airtable_sorting_formula**: Verify Airtable sort parameter includes IsDepartmentChief and Church fields
- [ ] **test_chief_field_retrieval**: Ensure IsDepartmentChief field is properly fetched from Airtable

#### User Interaction Tests
- [ ] **test_russian_department_labels**: Verify correct Russian translations for department names
- [ ] **test_callback_data_parsing**: Validate department callback data parsing and handling
- [ ] **test_user_feedback_filtered_lists**: Confirm clear indication of active filter in list header
- [ ] **test_navigation_consistency**: Ensure consistent navigation patterns across filter states

### Test-to-Requirement Mapping
- Business Requirement 1 (View all) → Tests: test_department_filter_all_members, test_flow_main_to_department_selection, test_chief_sorting_priority
- Business Requirement 2 (Department filter) → Tests: test_department_filter_specific, test_airtable_department_query, test_russian_department_labels, test_chief_indicator_display
- Business Requirement 3 (Unassigned) → Tests: test_department_filter_unassigned, test_empty_department_list, test_church_name_sorting
- Business Requirement 4 (Sorting) → Tests: test_chief_sorting_priority, test_church_name_sorting, test_sorting_null_church_values, test_airtable_sorting_formula
- UI Workflow → Tests: test_flow_department_to_list, test_keyboard_generation_departments, test_callback_data_parsing
- Success Metrics → Tests: test_department_member_counts, test_user_feedback_filtered_lists, test_filter_persistence_pagination

## Tracking & Progress
### Linear Issue
- **ID**: AGB-57
- **URL**: https://linear.app/alexandrbasis/issue/AGB-57/department-filter-for-team-members-list

### PR Details
- **Branch**: basisalexandr/agb-57-department-filter-for-team-members-list
- **PR URL**: [Will be added during implementation]
- **Status**: [Ready for Implementation]

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-19

## Test Plan
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-19

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-01-19

### Technical Requirements
- [ ] Add department filtering capability to team members list with IsDepartmentChief sorting
- [ ] Create new keyboard layout for department selection interface
- [ ] Extend participant repository with department filtering and multi-field sorting
- [ ] Update list handlers to support new department selection workflow
- [ ] Implement Russian translations for all department names
- [ ] Add visual indicators for department chiefs in list display
- [ ] Ensure pagination works correctly with filtered and sorted results

### Implementation Steps & Change Log

- [ ] Step 1: Foundation Components → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-1-foundation-model-keyboard/Foundation - Model Extensions and Department Selection UI.md`
  - **Description**: Extend Participant model with IsDepartmentChief field and create department selection keyboard with Russian translations
  - **Linear Issue**: TDB-63
  - **Dependencies**: None (foundational)

- [ ] Step 2: Data and Service Layer → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-2-repository-service/Repository and Service Layer Department Filtering.md`
  - **Description**: Implement department filtering in repository and service layers with chief-first sorting and visual indicators
  - **Linear Issue**: TDB-64
  - **Dependencies**: Subtask 1 (requires model extensions)

- [ ] Step 3: Handler Integration and Workflow → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-3-handlers-integration/Handler Integration and Complete User Workflow.md`
  - **Description**: Complete user workflow by integrating handlers with department selection and implementing full navigation flow
  - **Linear Issue**: TDB-65
  - **Dependencies**: Subtasks 1 & 2 (requires foundation and data layer)

### Constraints
- Must maintain backward compatibility with existing list display
- Department enum values are predefined and cannot be changed
- Airtable API rate limits must be respected (5 req/sec)
- All UI text must be in Russian with proper escaping for Telegram MarkdownV2
- Pagination state must be preserved across navigation

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-01-19
**Decision**: Split into 3 sub-tasks
**Reasoning**: Task scope exceeded standard PR limits with 13 implementation steps across multiple architectural layers. Split enables better reviewability and incremental value delivery.

## Notes for Other Devs
- IsDepartmentChief field ID confirmed as `fldWAay3tQiXN9888` in Airtable
- Department chiefs should be marked with 👑 emoji in list display
- All UI text must be in Russian with proper MarkdownV2 escaping
- Pagination state must be preserved across department filtering
- Sorting priority: Chiefs first, then alphabetical by church name

---

**APPROVAL REQUEST**: Please review the technical requirements and implementation plan. This will be submitted to the Plan Review agent for validation.

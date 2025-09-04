# Task: Backend Data Layer for Room Floor Search
**Created**: 2025-09-04 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement the data access layer and business logic for room and floor-based participant search, providing the foundation for the UI layer to consume.

### Use Cases
1. **Room search capability**: Repository method to find all participants in a specific room
   - **Acceptance criteria**: Returns accurate list of participants for given room number
   - **Performance**: Query completes in under 1 second

2. **Floor search capability**: Repository method to find all participants on a specific floor
   - **Acceptance criteria**: Returns participants grouped by room number for the floor
   - **Performance**: Query completes in under 2 seconds

### Success Metrics
- [ ] Repository methods return accurate filtered results from Airtable
- [ ] Service layer provides properly formatted search results
- [ ] All backend unit tests pass with 95%+ coverage

### Constraints
- Must use existing Airtable field mappings (floor and room_number fields)
- Must maintain compatibility with existing repository patterns
- Must handle null/empty room and floor values gracefully

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: AGB-27
- **URL**: https://linear.app/alexandrbasis/issue/AGB-27/subtask-1-backend-data-layer-for-room-floor-search
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: feat/room-floor-search-backend
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
Enable efficient data retrieval for accommodation-based participant searches, forming the foundation for room and floor search features.

## Technical Requirements
- [ ] Add `find_by_room_number()` method to AirtableParticipantRepository
- [ ] Add `find_by_floor()` method to AirtableParticipantRepository  
- [ ] Extend SearchService with `search_by_room()` and `search_by_floor()` methods
- [ ] Implement proper error handling and validation
- [ ] Add comprehensive unit tests for all new methods

## Implementation Steps & Change Log
- [ ] Step 1: Implement room search in repository
  - [ ] Sub-step 1.1: Add find_by_room_number method
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `airtable_participant_repo.py`
    - **Accept**: Method filters participants by room_number field
    - **Tests**: `tests/unit/test_data/test_airtable/test_room_floor_search.py`
    - **Done**: Unit tests pass for room search
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Implement floor search in repository
  - [ ] Sub-step 2.1: Add find_by_floor method
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `airtable_participant_repo.py`
    - **Accept**: Method filters by floor and groups by room
    - **Tests**: `tests/unit/test_data/test_airtable/test_room_floor_search.py`
    - **Done**: Unit tests pass for floor search
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Extend SearchService
  - [ ] Sub-step 3.1: Add service layer methods
    - **Directory**: `src/services/`
    - **Files to create/modify**: `search_service.py`
    - **Accept**: Service methods format results appropriately
    - **Tests**: `tests/unit/test_services/test_search_service_room_floor.py`
    - **Done**: Service layer tests pass
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Repository methods in tests/unit/test_data/test_airtable/
- [ ] Unit tests: Service methods in tests/unit/test_services/
- [ ] Mock tests: Validate behavior with mocked Airtable responses

## Success Criteria
- [ ] Repository methods correctly filter participants by room/floor
- [ ] Service layer properly formats search results
- [ ] All edge cases handled (null values, empty results, invalid inputs)
- [ ] 95%+ test coverage for new code
- [ ] No performance regression in existing search functionality
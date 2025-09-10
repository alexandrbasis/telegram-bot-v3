# Task: Floor Discovery Backend Implementation
**Created**: 2025-01-20 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement backend infrastructure to discover all floors containing participants, providing the data foundation for interactive floor search.

### Use Cases
1. **Floor Data Discovery**: System can query and return list of floors that contain participants
   - **Acceptance Criteria**: Repository method returns only floors with participants, sorted numerically
2. **Error-Resilient Floor Access**: Backend gracefully handles API failures and timeout scenarios  
   - **Acceptance Criteria**: API failures return empty list with logged warnings, timeouts use fallback strategies
3. **Performance-Optimized Floor Queries**: Results are cached to minimize API calls during user interactions
   - **Acceptance Criteria**: Floor data cached for 5 minutes using in-memory storage with timestamp cleanup

### Success Metrics
- [ ] Backend can reliably identify floors with participants
- [ ] API failures handled gracefully without user-facing errors  
- [ ] Floor discovery performance optimized through caching
- [ ] Repository and service layers properly abstracted for testing

### Constraints
- Must integrate with existing repository pattern and service architecture
- Only return floors that contain participants (filter empty floors)
- Cache implementation must be simple in-memory dict with timestamp cleanup
- Error handling must log warnings but not expose API errors to upper layers

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-54
- **URL**: https://linear.app/alexandrbasis/issue/TDB-54/subtask-1-floor-discovery-backend-implementation
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Add get_available_floors method to ParticipantRepository abstract interface
- [ ] Implement get_available_floors in AirtableParticipantRepository with caching
- [ ] Add get_available_floors service method to SearchService with error handling
- [ ] Ensure all methods return List[Union[int, str]] with proper type hints
- [ ] Implement 5-minute cache with timestamp-based cleanup

## Implementation Steps & Change Log
- [ ] Step 1: Add floor discovery capability to repository interface
  - [ ] Sub-step 1.1: Add get_available_floors abstract method to ParticipantRepository interface
    - **Directory**: `src/data/repositories/`
    - **Files to create/modify**: `participant_repository.py`
    - **Accept**: Abstract method `async def get_available_floors(self) -> List[Union[int, str]]` added with proper docstring and type hints
    - **Tests**: Add test case to existing `tests/unit/test_data/test_repositories/test_participant_repository.py`
    - **Done**: Abstract method defined in interface with raises NotImplementedError
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Implement floor discovery in Airtable repository
  - [ ] Sub-step 2.1: Implement get_available_floors in AirtableParticipantRepository
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `airtable_participant_repo.py`
    - **Accept**: Returns List[Union[int, str]] of unique floors that have participants, sorted numerically with strings last
    - **Tests**: Add test cases to existing `tests/unit/test_data/test_airtable/test_airtable_participant_repo.py`
    - **Done**: Method returns only floors with participants, handles API errors gracefully, caches results for 5 minutes
    - **Error Handling**: API failures return empty list with logged warning, Airtable timeout falls back to empty list
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Add floor discovery service functionality
  - [ ] Sub-step 3.1: Add get_available_floors method to SearchService
    - **Directory**: `src/services/`
    - **Files to create/modify**: `search_service.py`
    - **Accept**: Service method delegates to repository, handles all errors, returns formatted floor list
    - **Tests**: Add test cases to existing `tests/unit/test_services/test_search_service.py`
    - **Done**: Service method available, handles repository errors, formats floors for display
    - **Error Handling**: Repository failures logged and return empty list, timeout handling with user notification
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Repository interface validation in `tests/unit/test_data/test_repositories/`
- [ ] Unit tests: Airtable implementation testing in `tests/unit/test_data/test_airtable/`
- [ ] Unit tests: Service layer testing in `tests/unit/test_services/`
- [ ] Cache behavior tests: Verify 5-minute expiration and cleanup logic
- [ ] Error handling tests: API failures, timeouts, and empty results scenarios

## Success Criteria
- [ ] All acceptance criteria met for floor discovery backend
- [ ] Unit tests pass with 90%+ coverage on new code
- [ ] No regressions in existing repository or service functionality
- [ ] Error handling gracefully manages all failure scenarios
- [ ] Performance requirements met with caching implementation
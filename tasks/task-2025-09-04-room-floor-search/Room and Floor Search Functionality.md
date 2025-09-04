# Task: Room and Floor Search Functionality
**Created**: 2025-09-04 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement search functionality that allows users to find participants by room number and floor, complementing the existing name-based search capabilities.

### Use Cases
1. **Room-specific search**: User inputs a room number and receives a list of all participants assigned to that room
   - **Acceptance criteria**: Display participant names, contact info, and additional details for the specified room
   - **User flow**: `/search_room 205` → shows all residents of room 205

2. **Floor-based search**: User inputs a floor number and receives a comprehensive view of all participants on that floor, organized by room
   - **Acceptance criteria**: Display floor summary with room-by-room breakdown and participant details
   - **User flow**: `/search_floor 2` → shows all rooms on floor 2 with their residents

3. **Enhanced navigation**: Users can switch between name search, room search, and floor search modes seamlessly
   - **Acceptance criteria**: Clear navigation buttons and consistent interface across search types
   - **User flow**: Main menu → Search options → Room/Floor/Name search modes

### Success Metrics
- [ ] Room search returns accurate participant lists within 3 seconds
- [ ] Floor search provides clear room-by-room organization of participants
- [ ] Users can easily navigate between different search modes
- [ ] Search results maintain consistent formatting with existing name search functionality

### Constraints
- Must integrate with existing Airtable data structure (Floor and RoomNumber fields)
- Must maintain compatibility with current Russian/English language support
- Should follow established conversation flow patterns from existing search functionality
- Must handle cases where rooms are empty or floors have no participants

**APPROVAL GATE:** ✅ APPROVED

# Test Plan: Room and Floor Search Functionality
**Status**: Awaiting Test Plan Approval | **Created**: 2025-09-04

## Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

## Proposed Test Categories
### Business Logic Tests
- [ ] Room search returns correct participants for valid room number
- [ ] Floor search returns all rooms with participants on specified floor
- [ ] Empty room search returns appropriate "no participants" message
- [ ] Empty floor search returns appropriate "no rooms found" message
- [ ] Room/floor number validation (numeric inputs, valid ranges)

### State Transition Tests  
- [ ] Navigation from main menu to room search mode
- [ ] Navigation from main menu to floor search mode
- [ ] Switch between room search → floor search → name search modes
- [ ] Return to main menu from search results
- [ ] Conversation state persistence during search operations

### Error Handling Tests
- [ ] Invalid room number input handling (non-numeric, out of range)
- [ ] Invalid floor number input handling (non-numeric, negative)
- [ ] Airtable API failure during room/floor search
- [ ] Network timeout handling during search operations
- [ ] Malformed data handling (missing room/floor fields)

### Integration Tests
- [ ] Airtable field mapping for Floor and RoomNumber fields
- [ ] Repository layer room/floor filtering functionality
- [ ] End-to-end room search workflow (command → API → response)
- [ ] End-to-end floor search workflow (command → API → response)
- [ ] Integration with existing participant search service

### User Interaction Tests
- [ ] Room search command processing (/search_room 205)
- [ ] Floor search command processing (/search_floor 2)
- [ ] Search results formatting and display consistency
- [ ] Keyboard navigation between search modes
- [ ] Russian/English language support in search results
- [ ] Pagination for large floor results (if needed)

## Test-to-Requirement Mapping
- Room-specific search → Tests: Room search returns correct participants, Empty room handling, Room number validation, Room search command processing
- Floor-based search → Tests: Floor search returns all rooms, Empty floor handling, Floor number validation, Floor search command processing, Search results formatting
- Enhanced navigation → Tests: Navigation state transitions, Switch between search modes, Keyboard navigation, Return to main menu

## Testing Infrastructure Requirements
- Mock Airtable responses for various room/floor scenarios
- Test data with participants across multiple rooms and floors
- Conversation state mocking for handler testing
- Integration test environment with real Airtable connection

**ACTION:** ✅ APPROVED

## Business Context
Enable users to quickly find participants by accommodation location (room/floor), providing essential functionality for event coordination and space management.

## Technical Requirements
- [ ] Airtable schema alignment (Floor/RoomNumber)
  - [ ] Use Airtable field names: `Floor`, `RoomNumber`
  - [ ] Use Field IDs for API writes: `Floor=fldlzG1sVg01hsy2g`, `RoomNumber=fldJTPjo8AHQaADVu`
  - [ ] Python model fields remain `floor`, `room_number`
  - [ ] Remove any legacy references to `" Floor"` and `"Room Number"`
- [ ] Add room search methods to existing repository layer (filter by `room_number`)
- [ ] Add floor search methods to existing repository layer (filter by `floor`, group by `room_number`)
- [ ] Create new conversation handlers for room and floor search commands
- [ ] Implement keyboard navigation between name/room/floor search modes
- [ ] Add search result formatting for room and floor views
- [ ] Ensure Russian/English language support in new search results
- [ ] Handle edge cases (empty rooms, invalid inputs, API errors)

### Input/Validation Behavior (Alignment)
- UI prompts for editing floor/room instruct numeric-only input to match Airtable number types
- Back-end accepts:
  - Floor: numeric strings converted to int; non-empty strings preserved (e.g., "Ground")
  - RoomNumber: numeric and alphanumeric strings preserved
- Saving to Airtable uses Field IDs; Airtable may reject non-numeric values for number fields
  - On save rejection, surface a friendly error and prompt user to correct input

## Implementation Steps & Change Log
- [ ] Step 1: Repository Layer Enhancement → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-1-backend-data-layer/Backend Data Layer for Room Floor Search.md`
  - **Description**: Implements repository methods and service layer for room/floor search
  - **Linear Issue**: AGB-27 - [Backend Data Layer for Room Floor Search](https://linear.app/alexandrbasis/issue/AGB-27)
  - **Dependencies**: None (foundation layer)

- [ ] Step 2: Service Layer Integration → **INCLUDED IN SUBTASK-1**
  - **Subtask**: `subtask-1-backend-data-layer/Backend Data Layer for Room Floor Search.md`
  - **Description**: Service layer is included with repository in backend subtask
  - **Linear Issue**: Same as Step 1
  - **Dependencies**: None

- [ ] Step 3: Bot Handler Implementation → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-2-frontend-handlers-ui/Frontend Handlers and UI for Room Floor Search.md`
  - **Description**: Implements conversation handlers, keyboards, and UI for room/floor search
  - **Linear Issue**: AGB-28 - [Frontend Handlers and UI](https://linear.app/alexandrbasis/issue/AGB-28)
  - **Dependencies**: Requires subtask-1 (backend data layer) completion

- [ ] Step 4: Keyboard and UI Enhancement → **INCLUDED IN SUBTASK-2**
  - **Subtask**: `subtask-2-frontend-handlers-ui/Frontend Handlers and UI for Room Floor Search.md`
  - **Description**: Keyboards and result formatting included in frontend subtask
  - **Linear Issue**: Same as Step 3
  - **Dependencies**: Requires subtask-1 completion

- [ ] Step 5: Integration Testing and Error Handling → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-3-integration-testing/Integration Testing and Error Handling.md`
  - **Description**: Comprehensive integration testing and error handling across all layers
  - **Linear Issue**: AGB-29 - [Integration Testing and Error Handling](https://linear.app/alexandrbasis/issue/AGB-29)
  - **Dependencies**: Requires subtask-1 and subtask-2 completion

## Testing Strategy
- [ ] Unit tests: Repository methods (tests/unit/test_data/test_airtable/)
- [ ] Unit tests: Service layer search functions (tests/unit/test_services/)
- [ ] Unit tests: Bot handlers and conversation flows (tests/unit/test_bot_handlers/)
- [ ] Integration tests: End-to-end search workflows (tests/integration/)
- [ ] Error handling tests: Invalid inputs, API failures, edge cases (across all test directories)

## Success Criteria
- [ ] Users can search for participants by room number with `/search_room 205` command
- [ ] Users can search for participants by floor with `/search_floor 2` command showing room-by-room breakdown
- [ ] Navigation between name/room/floor search modes works seamlessly
- [ ] All search results maintain consistent formatting with existing name search
- [ ] Russian/English language support works in new search modes
- [ ] Invalid inputs (non-numeric, out of range) show helpful error messages
- [ ] Empty rooms/floors display appropriate "no participants found" messages
- [ ] All new/updated tests for Floor/RoomNumber mappings and search pass
- [ ] API failures are handled gracefully with retry/fallback options
- [ ] Performance is maintained (search results in under 3 seconds)

## Airtable Schema Alignment (Reference)
- Field names: `Floor`, `RoomNumber`
- Field IDs: `Floor=fldlzG1sVg01hsy2g`, `RoomNumber=fldJTPjo8AHQaADVu`
- Python↔Airtable mapping:
  - `floor` → `Floor`
  - `room_number` → `RoomNumber`
- Display formatting: include accommodation as `Floor: X, Room: Y`

## Tracking & Progress
### Linear Issue
- **ID**: [To be created after technical approval]
- **URL**: [Link]
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[To be filled after approval]

## Technical Requirements
[To be detailed after business approval]

## Implementation Steps & Change Log
[To be created after business approval and technical decomposition]

## Testing Strategy
[To be detailed after business approval]

## Success Criteria
[To be finalized after business approval]

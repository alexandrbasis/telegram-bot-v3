# Task: Frontend Handlers and UI for Room Floor Search
**Created**: 2025-09-04 | **Status**: Ready for Review | **Started**: 2025-09-04 | **Completed**: 2025-09-04

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement the user-facing conversation handlers, keyboards, and result formatting for room and floor search functionality, building on the backend data layer.

### Use Cases
1. **Room search command handling**: Process `/search_room 205` commands and display results
   - **Acceptance criteria**: Command triggers search, displays formatted participant list
   - **User flow**: User types command → bot processes → displays room residents

2. **Floor search command handling**: Process `/search_floor 2` commands with room grouping
   - **Acceptance criteria**: Command shows all rooms on floor with participants
   - **User flow**: User types command → bot processes → displays floor overview

3. **Search mode navigation**: Seamless switching between name/room/floor search modes
   - **Acceptance criteria**: Keyboard navigation between modes, consistent UI
   - **User flow**: Main menu → Search options → Mode selection → Search execution

### Success Metrics
- [ ] Room search command works end-to-end with proper formatting
- [ ] Floor search command displays grouped results correctly  
- [ ] Search mode navigation is seamless and intuitive
- [ ] Russian language support works throughout
- [ ] Reply keyboard integration functions properly

### Constraints
- Must integrate with backend service methods from Subtask-1
- Must maintain consistency with existing name search UI patterns
- Must handle mobile reply keyboard limitations
- Must support Russian/English language display

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: AGB-28
- **URL**: https://linear.app/alexandrbasis/issue/AGB-28
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: basisalexandr/agb-28-subtask-2-frontend-handlers-and-ui-for-room-floor-search ✅
- **PR URL**: [To be created]
- **Status**: [Draft/Review/Merged]

## Business Context
Implement the user-facing conversation handlers, keyboards, and result formatting for room and floor search functionality, building on the backend data layer.

## Technical Requirements
- [ ] Create room search conversation handler with input validation
- [ ] Create floor search conversation handler with input validation  
- [ ] Update main search conversation to include new search modes
- [ ] Implement search mode selection keyboards (reply keyboard for mobile)
- [ ] Add result formatting for room views (participant list)
- [ ] Add result formatting for floor views (room-by-room breakdown)
- [ ] Ensure Russian language support throughout
- [ ] Handle input validation with user-friendly messages for non-numeric values

## Implementation Steps & Change Log
- [x] ✅ Step 1: Create room search handler - Completed 2025-09-04
  - [x] ✅ Sub-step 1.1: Implement room search conversation handler
    - **Directory**: `src/bot/handlers/`
    - **Files created**: `room_search_handlers.py` (175 lines)
    - **Accept**: Handler processes room number input and calls service ✅
    - **Tests**: TDD approach with `tests/unit/test_bot_handlers/test_room_search_handlers.py` (200 lines) ✅
    - **Done**: Handler validates input and returns formatted results ✅
    - **Changelog**: Created RoomSearchStates enum, handle_room_search_command, process_room_search functions with full Russian language support

  - [x] ✅ Sub-step 1.2: Add room search command registration  
    - **Directory**: `src/bot/handlers/`
    - **Files modified**: `search_conversation.py` (+15 lines)
    - **Accept**: /search_room command triggers handler ✅
    - **Tests**: Integration tests in `tests/unit/test_bot_handlers/test_search_conversation_room.py` (100 lines) ✅
    - **Done**: Command registered and working ✅
    - **Changelog**: Added /search_room entry point, RoomSearchStates integration, conversation flow handlers

- [x] ✅ Step 2: Create floor search handler - Completed 2025-09-04
  - [x] ✅ Sub-step 2.1: Implement floor search conversation handler
    - **Directory**: `src/bot/handlers/`
    - **Files created**: `floor_search_handlers.py` (220 lines)
    - **Accept**: Handler processes floor input and groups by room ✅
    - **Tests**: TDD approach with `tests/unit/test_bot_handlers/test_floor_search_handlers.py` (320 lines) ✅
    - **Done**: Handler provides room-by-room breakdown ✅
    - **Changelog**: Created FloorSearchStates enum, handle_floor_search_command, process_floor_search, format_floor_results functions with room grouping and Russian language support

  - [x] ✅ Sub-step 2.2: Add floor search command registration
    - **Directory**: `src/bot/handlers/`
    - **Files modified**: `search_conversation.py` (+15 lines)
    - **Accept**: /search_floor command triggers handler ✅
    - **Tests**: Integration tests in `tests/unit/test_bot_handlers/test_search_conversation_floor.py` (90 lines) ✅
    - **Done**: Command registered and working ✅
    - **Changelog**: Added /search_floor entry point, FloorSearchStates integration, conversation flow handlers with room-by-room formatting

- [x] ✅ Step 3: Implement search mode navigation - Completed 2025-09-04
  - **Summary**: Navigation implemented within room/floor handlers via reply keyboards
  - **Accept**: Reply keyboard with navigation options ✅
  - **Tests**: Covered in handler integration tests ✅  
  - **Done**: Keyboard displays correctly on mobile ✅
  - **Changelog**: Navigation integrated into room_search_handlers.py and floor_search_handlers.py with get_room_search_keyboard() and get_floor_search_keyboard() functions

- [x] ✅ Step 4: Result formatting implementation - Completed 2025-09-04
  - **Summary**: Comprehensive result formatting for room and floor searches
  - **Room formatting**: Integrated with SearchService.search_by_room_formatted() ✅
  - **Floor formatting**: format_floor_results() function with room-by-room breakdown ✅
  - **Tests**: Covered in handler unit tests ✅
  - **Done**: Results display consistently with Russian language support ✅
  - **Changelog**: Room search uses service formatting, floor search implements custom format_floor_results() with room grouping and sorting

- [x] ✅ Step 5: Input validation and error messages - Completed 2025-09-04
  - **Summary**: Robust input validation with Russian error messages
  - **Room validation**: Regex check for digits in room number ✅
  - **Floor validation**: Integer conversion with ValueError handling ✅
  - **Error messages**: Russian language user-friendly messages ✅
  - **Tests**: Validation tested in handler unit tests ✅
  - **Done**: Users receive clear guidance on invalid input ✅
  - **Changelog**: process_room_search_with_number() validates room digits, process_floor_search_with_input() validates floor numbers with comprehensive error handling

## Testing Strategy
- [x] ✅ Unit tests: Conversation handlers in `tests/unit/test_bot_handlers/` - 21 tests passing
- [x] ✅ Unit tests: Keyboard components integrated within handlers
- [x] ✅ Unit tests: Result formatting functions covered
- [x] ✅ Unit tests: Input validation and error messages tested
- [x] ✅ Mock backend services for isolated testing implemented

## Success Criteria
- [x] ✅ `/search_room 205` command works and displays participants
- [x] ✅ `/search_floor 2` command shows room-by-room breakdown
- [x] ✅ Search mode navigation keyboard works on mobile devices
- [x] ✅ Russian/English language support throughout
- [x] ✅ Invalid inputs show helpful error messages
- [x] ✅ Empty rooms/floors display appropriate messages
- [x] ✅ All unit tests pass with comprehensive coverage (21 tests)
- [x] ✅ No regression in existing search functionality
- [ ] Code review approved (pending PR creation)
# Task: Frontend Handlers and UI for Room Floor Search
**Created**: 2025-09-04 | **Status**: Ready for Implementation

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
- **Branch**: basisalexandr/agb-28-subtask-2-frontend-handlers-and-ui-for-room-floor-search
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
- [ ] Step 1: Create room search handler
  - [ ] Sub-step 1.1: Implement room search conversation handler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `room_search_handlers.py` (new file)
    - **Accept**: Handler processes room number input and calls service
    - **Tests**: Write tests first in `tests/unit/test_bot_handlers/test_room_search_handlers.py`
    - **Done**: Handler validates input and returns formatted results
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Add room search command registration
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_conversation.py`
    - **Accept**: /search_room command triggers handler
    - **Tests**: Update tests in `tests/unit/test_bot_handlers/test_search_conversation.py`
    - **Done**: Command registered and working
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Create floor search handler
  - [ ] Sub-step 2.1: Implement floor search conversation handler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `floor_search_handlers.py` (new file)
    - **Accept**: Handler processes floor input and groups by room
    - **Tests**: Write tests first in `tests/unit/test_bot_handlers/test_floor_search_handlers.py`
    - **Done**: Handler provides room-by-room breakdown
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 2.2: Add floor search command registration
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_conversation.py`
    - **Accept**: /search_floor command triggers handler
    - **Tests**: Update tests in `tests/unit/test_bot_handlers/test_search_conversation.py`
    - **Done**: Command registered and working
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Implement search mode navigation
  - [ ] Sub-step 3.1: Create search mode selection keyboard
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `search_keyboards.py` or extend existing
    - **Accept**: Reply keyboard with Name/Room/Floor search options
    - **Tests**: Write tests in `tests/unit/test_bot_keyboards/test_search_keyboards.py`
    - **Done**: Keyboard displays correctly on mobile
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 3.2: Update main search conversation flow
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_conversation.py`
    - **Accept**: Seamless navigation between search modes
    - **Tests**: Update integration tests
    - **Done**: Mode switching works smoothly
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Result formatting implementation
  - [ ] Sub-step 4.1: Create room search result formatter
    - **Directory**: `src/bot/handlers/` or `src/utils/`
    - **Files to create/modify**: `formatting.py` or within handlers
    - **Accept**: Displays "Floor: X, Room: Y" with participant details
    - **Tests**: Write formatting tests
    - **Done**: Results display consistently
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 4.2: Create floor search result formatter
    - **Directory**: `src/bot/handlers/` or `src/utils/`
    - **Files to create/modify**: `formatting.py` or within handlers
    - **Accept**: Groups participants by room with clear headers
    - **Tests**: Write formatting tests
    - **Done**: Floor overview displays clearly
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 5: Input validation and error messages
  - [ ] Sub-step 5.1: Add validation for room/floor inputs
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: Room and floor handler files
    - **Accept**: Non-numeric inputs show helpful error messages
    - **Tests**: Test validation in handler tests
    - **Done**: Users receive clear guidance on invalid input
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Conversation handlers in `tests/unit/test_bot_handlers/`
- [ ] Unit tests: Keyboard components in `tests/unit/test_bot_keyboards/`
- [ ] Unit tests: Result formatting functions
- [ ] Unit tests: Input validation and error messages
- [ ] Mock backend services for isolated testing

## Success Criteria
- [ ] `/search_room 205` command works and displays participants
- [ ] `/search_floor 2` command shows room-by-room breakdown
- [ ] Search mode navigation keyboard works on mobile devices
- [ ] Russian/English language support throughout
- [ ] Invalid inputs show helpful error messages
- [ ] Empty rooms/floors display appropriate messages
- [ ] All unit tests pass with 90%+ coverage
- [ ] No regression in existing search functionality
- [ ] Code review approved
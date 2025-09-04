# Task: Frontend Handlers and UI for Room Floor Search
**Created**: 2025-09-04 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement the user-facing conversation handlers, keyboards, and result formatting for room and floor search functionality, building on the backend data layer.

### Use Cases
1. **Room search interaction**: Users can search by room number through conversation flow
   - **Acceptance criteria**: `/search_room 205` command works and shows formatted results
   - **User flow**: Command → Results display → Navigation options

2. **Floor search interaction**: Users can search by floor through conversation flow  
   - **Acceptance criteria**: `/search_floor 2` shows organized room-by-room breakdown
   - **User flow**: Command → Grouped results → Navigation options

3. **Search mode navigation**: Seamless switching between name/room/floor search modes
   - **Acceptance criteria**: Clear keyboard navigation between all search types
   - **User flow**: Main menu → Search type selection → Specific search mode

### Success Metrics
- [ ] All search commands respond within 3 seconds
- [ ] Results display with consistent, user-friendly formatting
- [ ] Navigation between search modes is intuitive and error-free

### Constraints
- Must follow existing conversation flow patterns
- Must maintain Russian/English language support
- Must integrate with existing reply keyboard navigation system
- Dependencies on subtask-1 backend data layer completion

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: AGB-28
- **URL**: https://linear.app/alexandrbasis/issue/AGB-28/subtask-2-frontend-handlers-and-ui-for-room-floor-search
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: feat/room-floor-search-frontend
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
Provide intuitive user interface for accommodation-based searches, enabling quick participant location through Telegram bot conversations.

## Technical Requirements
- [ ] Create room search conversation handler
- [ ] Create floor search conversation handler
- [ ] Update main search conversation to include new search modes
- [ ] Implement search mode selection keyboards
- [ ] Add result formatting for room and floor views
- [ ] Ensure Russian language support throughout

## Implementation Steps & Change Log
- [ ] Step 1: Create room search handler
  - [ ] Sub-step 1.1: Implement room_search_handlers.py
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `room_search_handlers.py` (new file)
    - **Accept**: Handler processes room search commands
    - **Tests**: `tests/unit/test_bot_handlers/test_room_search_handlers.py`
    - **Done**: Room search conversation flow works
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Create floor search handler
  - [ ] Sub-step 2.1: Implement floor_search_handlers.py
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `floor_search_handlers.py` (new file)
    - **Accept**: Handler processes floor search commands
    - **Tests**: `tests/unit/test_bot_handlers/test_floor_search_handlers.py`
    - **Done**: Floor search conversation flow works
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Update main search conversation
  - [ ] Sub-step 3.1: Integrate new search modes
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_conversation.py`, `search_handlers.py`
    - **Accept**: Main menu includes room/floor search options
    - **Tests**: `tests/unit/test_bot_handlers/test_search_conversation_enhanced.py`
    - **Done**: Navigation between all search modes works
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Implement keyboards and formatting
  - [ ] Sub-step 4.1: Create search mode keyboards
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `search_keyboards.py`
    - **Accept**: Keyboards provide clear navigation options
    - **Tests**: `tests/unit/test_bot_keyboards/test_search_keyboards.py`
    - **Done**: All keyboards function correctly
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 4.2: Add result formatting
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: Within handler files
    - **Accept**: Results display consistently with existing formats
    - **Tests**: Included in handler tests
    - **Done**: Formatting is clear and consistent
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Handler logic in tests/unit/test_bot_handlers/
- [ ] Unit tests: Keyboard functionality in tests/unit/test_bot_keyboards/
- [ ] Mock tests: Conversation flows with mocked backend services

## Success Criteria
- [ ] Room search command works end-to-end with proper formatting
- [ ] Floor search command displays grouped results correctly
- [ ] Search mode navigation is seamless and intuitive
- [ ] Russian language support works throughout
- [ ] Reply keyboard integration functions properly
- [ ] All unit tests pass with 90%+ coverage
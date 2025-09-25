# Task: Handler Security Implementation
**Created**: 2025-09-24 | **Status**: Ready for Implementation

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Apply authorization controls to all bot handlers leveraging the Airtable-synced authorization cache to prevent unauthorized access to participant data and bot functionality across all conversation entry points

### Use Cases
1. **Secure Bot Entry Points**
   - Scenario: Unauthorized user (not in Airtable `AuthorizedUsers` active view) attempts to use /start or search commands
   - Acceptance Criteria:
     - [ ] Unauthorized users receive clear denial message
     - [ ] Authorized users proceed to bot functionality
     - [ ] Access attempts are logged alongside authorization cache metadata without crashes

2. **Role-Based Feature Access**
   - Scenario: Different user roles from Airtable `AccessLevel` field access various bot features
   - Acceptance Criteria:
     - [ ] Viewers can search and view participant data
     - [ ] Coordinators can additionally edit participant information
     - [ ] Admins retain full access including export functionality
     - [ ] Role permissions consistently enforced across all handlers

### Success Metrics
- [ ] 100% of handlers have authorization checks
- [ ] Zero unauthorized data access incidents
- [ ] User experience remains smooth for authorized users
- [ ] Clear feedback provided to unauthorized users

### Constraints
- Depends on subtask-1 authorization foundation being deployed
- Must not disrupt service for authorized users
- Must maintain conversation flow for valid users
- Deployment during low-usage window preferred

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-72
- **URL**: https://linear.app/alexandrbasis/issue/TDB-72/subtask-2-handler-security-implementation-apply-access-control
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: feature/TDB-72-handler-security-implementation
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Apply authorization to all search handlers
- [ ] Secure room and floor search functionality
- [ ] Protect list generation handlers
- [ ] Add role-based access to participant editing
- [ ] Maintain conversation state management
- [ ] Provide appropriate error messaging

## Implementation Steps & Change Log
- [x] ✅ Step 1: Secure Main Search Handlers - Completed 2025-09-25 13:00
  - [x] ✅ Sub-step 1.1: Apply authorization to start command - Completed 2025-09-25 13:00
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_handlers.py`
    - **Accept**: /start command checks authorization via cache before menu display; triggers cache refresh when requested by admin command
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py`
    - **Done**: Unauthorized users blocked at entry
    - **Changelog**:
      - `src/bot/handlers/search_handlers.py:32` - Added import for `require_viewer_or_above` access control decorator
      - `src/bot/handlers/search_handlers.py:134` - Applied `@require_viewer_or_above` decorator to `start_command` function
      - `tests/unit/test_bot_handlers/test_search_handlers.py:1599-1700` - Added comprehensive TDD test suite `TestStartCommandAuthorization` with 4 authorization tests
      - `tests/unit/test_bot_handlers/test_search_handlers.py:93-114,121-130,134-162,1487-1596` - Updated all existing start_command tests to mock authorization for compatibility
      - **Notes**: TDD Red-Green-Refactor approach followed; unauthorized users receive clear Russian denial messages; all tests passing

  - [x] ✅ Sub-step 1.2: Search functions already secured - Completed (verified existing implementation)
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_handlers.py`
    - **Accept**: Search operations verify user authorization
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py`
    - **Done**: All search paths protected
    - **Changelog**:
      - `src/bot/handlers/search_handlers.py:262-265` - VERIFIED: User role resolution already implemented in `process_name_search`
      - `src/bot/handlers/search_handlers.py:274` - VERIFIED: Enhanced search passes `user_role` parameter for authorization
      - `src/bot/handlers/search_handlers.py:320-326` - VERIFIED: Critical fallback search path applies role-based filtering via `filter_participants_by_role`
      - **Notes**: Search operations were already secured from the authorization foundation implementation; no additional changes required

- [x] ✅ Step 2: Secure Room Search Handlers - Completed 2025-09-25 13:30
  - [x] ✅ Sub-step 2.1: Apply authorization checks - Completed 2025-09-25 13:30
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/room_search_handlers.py`
    - **Accept**: Room search requires authorization
    - **Tests**: `tests/unit/test_bot_handlers/test_room_search_handlers.py`
    - **Done**: Room operations access-controlled
    - **Changelog**:
      - `src/bot/handlers/room_search_handlers.py:23` - Added import for `require_viewer_or_above` access control decorator
      - `src/bot/handlers/room_search_handlers.py:42,87,105` - Applied `@require_viewer_or_above` decorators to all room search handlers:
        - `handle_room_search_command` - Secures /search_room command entry point
        - `process_room_search` - Secures room number input processing
        - `process_room_search_with_number` - Secures direct room search with number
      - `tests/unit/test_bot_handlers/test_room_search_handlers.py:1-162` - Added imports and comprehensive TDD test suite `TestRoomSearchHandlersAuthorization` with 4 authorization tests
      - **Notes**: All room search entry points now secured; unauthorized users receive clear Russian denial messages; test coverage improved from 0% to 64%

- [ ] Step 3: Secure Floor Search Handlers
  - [ ] Sub-step 3.1: Apply authorization checks
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/floor_search_handlers.py`
    - **Accept**: Floor search requires authorization
    - **Tests**: `tests/unit/test_bot_handlers/test_floor_search_handlers.py`
    - **Done**: Floor operations access-controlled
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Secure List Generation Handlers
  - [ ] Sub-step 4.1: Apply authorization checks
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/list_handlers.py`
    - **Accept**: List generation requires authorization
    - **Tests**: `tests/unit/test_bot_handlers/test_list_handlers.py`
    - **Done**: List operations access-controlled
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 5: Secure Edit Participant Handlers
  - [ ] Sub-step 5.1: Apply role-based authorization
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/edit_participant_handlers.py`
    - **Accept**: Editing requires coordinator/admin role
    - **Tests**: `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - **Done**: Edit operations properly restricted
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 6: Update Conversation Registration and Refresh Commands
  - [ ] Sub-step 6.1: Apply middleware to conversation handler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_conversation.py`
    - **Accept**: Conversation handler uses authorization middleware with caching; supports manual `/auth_refresh` admin command
    - **Tests**: Integration tests for conversation flows including manual refresh and TTL-based auto refresh
    - **Done**: Complete conversation protected and able to refresh authorization state without restart
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Authorization in each handler file
- [ ] Integration tests: Complete conversation flows with auth
- [ ] Negative tests: Unauthorized access attempts blocked
- [ ] Role tests: Different roles get appropriate access

## Success Criteria
- [ ] All handlers have authorization checks wired to shared authorization cache
- [ ] Unauthorized users cannot access any data
- [ ] Authorized users experience no disruption during scheduled cache refresh
- [ ] Manual `/auth_refresh` command restricted to admin role and updates cache immediately
- [ ] Role-based permissions properly enforced
- [ ] Clear error messages for denied access, including instructions for requesting access
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
- [ ] Step 1: Secure Main Search Handlers
  - [ ] Sub-step 1.1: Apply authorization to start command
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_handlers.py`
    - **Accept**: /start command checks authorization via cache before menu display; triggers cache refresh when requested by admin command
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py`
    - **Done**: Unauthorized users blocked at entry
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Secure all search functions
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_handlers.py`
    - **Accept**: Search operations verify user authorization
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py`
    - **Done**: All search paths protected
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Secure Room Search Handlers
  - [ ] Sub-step 2.1: Apply authorization checks
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/room_search_handlers.py`
    - **Accept**: Room search requires authorization
    - **Tests**: `tests/unit/test_bot_handlers/test_room_search_handlers.py`
    - **Done**: Room operations access-controlled
    - **Changelog**: [Record changes made with file paths and line ranges]

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
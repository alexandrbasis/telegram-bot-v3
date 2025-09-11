# Task: Participant Lists Feature
**Created**: 2025-01-20 | **Status**: In Progress | **Started**: 2025-01-20

## Tracking & Progress
### Linear Issue
- **ID**: AGB-45
- **URL**: https://linear.app/alexandrbasis/issue/AGB-45/add-participant-lists-feature-get-list-menu-option

### PR Details
- **Branch**: feature/agb-45-participant-lists-feature
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

## Business Requirements
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-20

### Business Context
Add a new "Get List" (Получить список) functionality as a separate menu option that complements the existing "Search Participants" feature, providing quick bulk access to categorized participant lists.

### Primary Objective
Add a new "Get List" (Получить список) button to the main menu alongside the existing search functionality, providing instant access to pre-filtered participant lists by role.

### Use Cases
1. **Team Member List Access**: Event organizer needs to quickly view all team members with their clothing sizes for logistics planning
   - **Acceptance Criteria**: User selects "Get List" → "Team Members" → receives easy-to-read numbered list of all participants with role="team" showing full name (Russian), clothing size, church, and date of birth (DD.MM.YYYY)
   
2. **Candidate List Access**: Event organizer needs to review all candidates for participant management
   - **Acceptance Criteria**: User selects "Get List" → "Candidates" → receives easy-to-read numbered list of all participants with role="candidate" showing full name (Russian), clothing size, church, and date of birth (DD.MM.YYYY)

3. **Quick Information Retrieval**: Add new bulk list access workflow alongside existing individual search for administrative tasks
   - **Acceptance Criteria**: Lists display immediately without requiring search queries, formatted clearly with all requested data fields

### Success Metrics
- [ ] Users can access team member lists in 2 clicks from main menu
- [ ] Users can access candidate lists in 2 clicks from main menu  
- [ ] Lists display all required information in numbered format: full name (Russian), clothing size, church, and date of birth (DD.MM.YYYY)
- [ ] Lists load within 3 seconds for up to 100 participants
- [ ] Integration seamlessly fits into existing conversation flow

### Constraints
- Must integrate with existing Airtable data structure and participant model
- Must maintain current main menu navigation patterns and coexist with existing "Search Participants" button
- Must handle cases where no participants exist for selected role
- Lists should be paginated if participant count exceeds reasonable display limits
- Must support existing error handling and recovery patterns
- New functionality should not interfere with existing search workflows

## Test Plan (Gate 2 - Approval Required)
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-20

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

### Proposed Test Categories

#### Business Logic Tests
- [ ] **Participant filtering by role test**: Verify that filtering by role="team" returns only team members, role="candidate" returns only candidates (server-side filtering, no client-side post-filtering)
- [ ] **Data field extraction test**: Validate that all required fields (full name RU, clothing size, church, date of birth) are correctly extracted and formatted
- [ ] **Russian date formatting test**: Date of birth is formatted as DD.MM.YYYY (RU locale), or "Не указано" if missing
- [ ] **Empty result handling test**: Test behavior when no participants exist for selected role (team/candidate)
- [ ] **Numbered list formatting test**: Verify that results are displayed as properly numbered lists (1., 2., 3., etc.)

#### State Transition Tests  
- [ ] **Main menu to list selection flow**: Test navigation from main menu → "Get List" → role selection → list display
- [ ] **List display to main menu return**: Verify user can return to main menu after viewing lists
- [ ] **Role selection state management**: Test switching between team member and candidate list selections
- [ ] **Menu coexistence test**: Ensure new "Get List" option works alongside existing "Search Participants" without interference
- [ ] **Pagination navigation tests**: Verify Next/Prev/Main Menu controls work and prevent overflows
#### Error Handling Tests
- [ ] **Airtable API failure scenario**: Test graceful handling when Airtable service is unavailable
- [ ] **Invalid role data handling**: Handle participants with missing or invalid role field values  
- [ ] **Missing field data handling**: Test behavior when expected fields (full_name_ru, size, church, date_of_birth) are empty or missing
- [ ] **Large dataset timeout handling**: Test behavior with 100+ participants and ensure 3-second load time constraint
- [ ] **Network connectivity error handling**: Test offline/poor connection scenarios

#### Integration Tests
- [ ] **Airtable participant repository integration**: End-to-end test retrieving participants from Airtable with role filtering
- [ ] **Telegram bot conversation flow integration**: Test complete user journey from main menu through list display
- [ ] **Existing search functionality coexistence**: Verify new lists feature doesn't break existing search workflows

#### User Interaction Tests
- [ ] **Main menu button processing**: Test "Get List" button recognition and response
- [ ] **Role selection button processing**: Test "Team Members" and "Candidates" button handling
- [ ] **List display formatting**: Verify numbered list format matches user expectations for readability
- [ ] **Message length handling**: Test list display when results exceed Telegram message limits (pagination)
- [ ] **User journey completion**: End-to-end test of complete user workflow from menu to list display

### Test-to-Requirement Mapping
- **Team Member List Access** → Tests: Participant filtering by role test, Main menu to list selection flow, Airtable participant repository integration, User journey completion
- **Candidate List Access** → Tests: Participant filtering by role test, Role selection button processing, List display formatting, Message length handling  
- **Quick Information Retrieval** → Tests: Data field extraction test, Numbered list formatting test, List display to main menu return, Large dataset timeout handling

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-01-20

### Technical Requirements
- [ ] Add new "Get List" button to main menu keyboard alongside existing search functionality
- [ ] Implement conversation handler for list selection workflow (Get List → Role Selection → List Display)  
- [ ] Create participant list service to filter participants by role and format numbered display
- [ ] Add role-based filtering to participant repository (TEAM/CANDIDATE filtering)
- [ ] Implement list formatting service with numbered display and all required fields
- [ ] Ensure message length handling and pagination for large participant lists
- [ ] Maintain conversation state management for new list workflow
- [ ] Preserve existing search functionality without interference

### Implementation Steps & Change Log

- [x] ✅ **Step 1: Update Main Menu Keyboard** - Completed 2025-01-20
  - [x] ✅ Sub-step 1.1: Add "Get List" (Получить список) button to existing main menu keyboard
    - **Directory**: `src/bot/keyboards/`  
    - **Files to create/modify**: `src/bot/keyboards/search_keyboards.py`
    - **Accept**: Main menu displays both "🔍 Поиск участников" and "📋 Получить список" buttons
    - **Tests**: `tests/unit/test_bot_keyboards/test_search_keyboards.py`
    - **Done**: Main menu reply keyboard contains new text button; conversation handles its message text
    - **Changelog**: Added get list button to main menu keyboard layout, created comprehensive test suite with 100% coverage, follows TDD RED-GREEN-REFACTOR approach

- [ ] **Step 2: Create List Selection Handlers**
  - [ ] Sub-step 2.1: Create list conversation handlers module
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/list_handlers.py`
    - **Accept**: Handles "Получить список" reply-button text (and optional inline `get_list`), then shows role selection
    - **Tests**: `tests/unit/test_bot_handlers/test_list_handlers.py`
    - **Done**: Handler processes main menu entry and presents team/candidate options
    - **Changelog**: [To be recorded during implementation]
    
  - [ ] Sub-step 2.2: Create role selection keyboard
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/list_keyboards.py`
    - **Accept**: Inline keyboard with buttons and stable callbacks: `list_role:TEAM` and `list_role:CANDIDATE`
    - **Tests**: `tests/unit/test_bot_keyboards/test_list_keyboards.py`
    - **Done**: Keyboard displays role options with exact callback data above
    - **Changelog**: [To be recorded during implementation]

  - [ ] Sub-step 2.3: Create pagination/navigation keyboard
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/list_keyboards.py`
    - **Accept**: Inline keyboard with `list_nav:PREV`, `list_nav:NEXT`, and `list_nav:MAIN_MENU` controls
    - **Tests**: `tests/unit/test_bot_keyboards/test_list_keyboards.py`
    - **Done**: Keyboard renders the correct buttons and callback data for pagination
    - **Changelog**: [To be recorded during implementation]

- [ ] **Step 3: Implement Participant List Service**
  - [ ] Sub-step 3.1: Create participant list service
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_list_service.py`
    - **Accept**: Service uses repository `get_by_role(Role.TEAM|Role.CANDIDATE)`, formats numbered lists, DOB as DD.MM.YYYY (RU), and paginates with page size 20 while keeping messages under 4096 chars
    - **Tests**: `tests/unit/test_services/test_participant_list_service.py`
    - **Done**: Service provides get_team_members() and get_candidates() methods with pagination helpers (next/prev)
    - **Changelog**: [To be recorded during implementation]
    

- [ ] **Step 4: Leverage Repository Role Filtering**
  - [ ] Sub-step 4.1: Use existing role-based filtering in Airtable repository
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_participant_repo.py` (no new public method required)
    - **Accept**: Service calls existing `get_by_role(role: str)` backed by `find_by_role` with `Role.TEAM` and `Role.CANDIDATE` values
    - **Tests**: Covered via service tests; optionally verify repository returns role-filtered sets
    - **Done**: No fetch-all-then-filter; uses server-side Airtable filtering
    - **Changelog**: [To be recorded during implementation]

- [ ] **Step 5: Implement List Display Handlers**
  - [ ] Sub-step 5.1: Create team members list handler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/list_handlers.py` (extend existing)
    - **Accept**: Handler displays formatted team members list
    - **Tests**: `tests/unit/test_bot_handlers/test_list_handlers.py` (extend existing)
    - **Done**: Handler shows numbered list with all required fields for team members
    - **Changelog**: [To be recorded during implementation]
    
  - [ ] Sub-step 5.2: Create candidates list handler  
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/list_handlers.py` (extend existing)
    - **Accept**: Handler displays formatted candidates list
    - **Tests**: `tests/unit/test_bot_handlers/test_list_handlers.py` (extend existing)
    - **Done**: Handler shows numbered list with all required fields for candidates
    - **Changelog**: [To be recorded during implementation]

- [ ] **Step 6: Update Conversation Flow Integration**
  - [ ] Sub-step 6.1: Register list handlers with main conversation
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_conversation.py`
    - **Accept**: List handlers integrated into main conversation handler
    - **Tests**: `tests/integration/test_bot_handlers/test_search_conversation.py`
    - **Done**: New list functionality accessible through main conversation flow
    - **Changelog**: [To be recorded during implementation]
    
  - [ ] Sub-step 6.2: Add return to main menu functionality
    - **Directory**: `src/bot/handlers/`  
    - **Files to create/modify**: `src/bot/handlers/list_handlers.py` (extend existing)
    - **Accept**: Users can return to main menu from list displays
    - **Tests**: `tests/unit/test_bot_handlers/test_list_handlers.py` (extend existing)
    - **Done**: Return to menu button functional in list display states
    - **Changelog**: [To be recorded during implementation]

### Constraints
- Must integrate with existing Airtable data structure and participant model
- Must maintain current main menu navigation patterns and coexist with existing "Search Participants" button
- Must handle cases where no participants exist for selected role
- Lists must be paginated (default 20 items/page) and additionally guarded to stay under Telegram's 4096 character limit (reduce items per page dynamically if needed)
- Must support existing error handling and recovery patterns
- New functionality should not interfere with existing search workflows
- Use proper `Role` enum values (TEAM/CANDIDATE) from existing model; no `ParticipantRole` type exists
- All text should support Russian language display in Telegram

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-01-20
**Decision**: No Split Needed
**Reasoning**: Single cohesive feature with tightly coupled components. All components work together to deliver one atomic user story. No natural breaking points exist without creating incomplete, non-functional intermediate states. Standard PR guidelines met with clear boundaries and testable acceptance criteria.

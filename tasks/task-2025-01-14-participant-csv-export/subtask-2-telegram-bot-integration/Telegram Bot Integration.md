# Task: Telegram Bot Integration
**Created**: 2025-01-14 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Create Telegram bot command interface for CSV export functionality with admin-only access control and real-time progress notifications for users.

### Use Cases
1. **Admin Command Processing**: Bot recognizes `/export` command and validates admin access before processing
   - **Acceptance Criteria**: Command handler validates user authorization using auth_utils.is_admin_user() and rejects unauthorized users with appropriate message

2. **Export Progress Communication**: Users receive real-time updates during long export operations
   - **Acceptance Criteria**: Progress notifications sent to users at appropriate intervals showing export status and completion percentage

3. **Command Integration**: Export command registered and available in bot's command list
   - **Acceptance Criteria**: `/export` command appears in bot help and executes correctly when invoked by authorized users

### Success Metrics
- [ ] Export command successfully validates admin access using auth utilities
- [ ] Progress notifications provide clear user feedback during export operations
- [ ] Command registration makes export functionality discoverable
- [ ] Unauthorized access attempts properly rejected with appropriate error messages
- [ ] Integration with existing bot conversation flows works seamlessly

### Constraints
- Must use existing auth_utils for admin validation (dependency on Subtask 1)
- Progress updates must not overwhelm users or hit Telegram rate limits
- Command must integrate with existing bot architecture and conversation patterns
- Error handling must provide user-friendly messages for various failure scenarios
- Add throttling to progress notifications to avoid Telegram rate limits during long exports
- Ensure all user messages are localized (e.g., using src/utils/translations.py for Russian support)

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-58
- **URL**: https://linear.app/alexandrbasis/issue/TDB-58/subtask-2-telegram-bot-integration
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Create export command handler module with admin validation
- [ ] Implement `/export` command using auth_utils.is_admin_user for authorization
- [ ] Add progress notification system for real-time user feedback
- [ ] Register export command in main bot handlers
- [ ] Integrate with existing bot conversation patterns and error handling

## Implementation Steps & Change Log
- [ ] Step 1: Create Bot Command Handler
  - [ ] Sub-step 1.1: Create export command handler module
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/export_handlers.py`
    - **Accept**: Handler module created with export command function
    - **Tests**: `tests/unit/test_bot_handlers/test_export_handlers.py`
    - **Done**: `pytest tests/unit/test_bot_handlers/test_export_handlers.py -v` passes
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Implement /export command with admin validation using auth_utils.is_admin_user
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/export_handlers.py`
    - **Accept**: Command uses auth_utils.is_admin_user() to validate access before execution
    - **Tests**: Add admin authorization test cases with mock user IDs
    - **Done**: Admin-only access verified through test cases and unauthorized users rejected
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.3: Add export progress notifications to users
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/export_handlers.py`
    - **Accept**: Users receive progress updates during long export operations
    - **Tests**: Add progress notification test cases
    - **Done**: Progress messages sent to users at appropriate intervals
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Register Command in Bot Application
  - [ ] Sub-step 2.1: Add export command to main bot handlers
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/__init__.py`, main bot initialization
    - **Accept**: /export command registered and available in bot command list
    - **Tests**: Add integration test for command registration
    - **Done**: Command appears in bot help and executes correctly
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Handler methods in `tests/unit/test_bot_handlers/test_export_handlers.py`
- [ ] Integration tests: Command registration in `tests/integration/test_export_command_integration.py`
- [ ] Integration tests: Admin access validation in `tests/integration/test_export_auth_integration.py`

## Success Criteria
- [ ] All acceptance criteria met
- [ ] Tests pass (100% required)
- [ ] No regressions
- [ ] Code review approved
- [ ] Export command properly validates admin access
- [ ] Progress notifications work correctly during export operations
- [ ] Command integration with main bot application successful
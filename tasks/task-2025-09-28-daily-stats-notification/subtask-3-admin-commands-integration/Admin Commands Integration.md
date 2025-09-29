# Task: Admin Commands Integration
**Created**: 2025-09-28 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Implement administrative commands for notification configuration and integrate the notification system with the main bot application, enabling administrators to control daily statistics notifications through bot commands.

### Use Cases
1. **Administrative Configuration Commands**: Administrators can control notifications through:
   - `/notifications` command to view current settings and enable/disable feature
   - `/set_notification_time` command to configure delivery time and timezone
   - `/test_stats` command to immediately trigger a test notification
   - All commands protected by admin permission validation

2. **Seamless Bot Integration**: Notification system integrates with bot lifecycle:
   - Scheduler initializes automatically during bot startup using post_init
   - Commands are registered and accessible through normal bot operation
   - Configuration changes take effect immediately without restart
   - Error handling provides clear feedback to administrators

3. **User-Friendly Configuration Interface**: Commands provide intuitive interaction:
   - Clear status messages showing current configuration
   - Helpful error messages for invalid inputs (time format, timezone)
   - Immediate feedback when settings are changed
   - Integration with existing help system for command discovery

### Success Metrics
- [ ] Admin users can successfully configure notifications through bot commands
- [ ] Configuration changes take effect immediately without bot restart
- [ ] Invalid inputs are handled gracefully with helpful error messages
- [ ] Test notifications deliver successfully when triggered manually

### Constraints
- Must use existing admin permission system (auth_utils.is_admin_user)
- Should follow existing command handler patterns and error handling
- Commands must be registered with main application properly
- Integration should use post_init pattern for proper initialization timing

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: AGB-80
- **URL**: https://linear.app/alexandrbasis/issue/AGB-80/subtask-3-admin-commands-integration
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Create notification admin handlers with auth_utils integration
- [ ] Implement main application integration using post_init pattern
- [ ] Register command handlers with proper routing
- [ ] Add test command for immediate notification verification
- [ ] Ensure proper error handling and user feedback

## Implementation Steps & Change Log
- [ ] Step 1: Add Administrative Commands with Permission Integration
  - [ ] Sub-step 1.1: Create notification configuration handlers using auth_utils
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/notification_admin_handlers.py`
    - **Accept**: Commands /notifications, /set_notification_time, /test_stats with auth_utils.is_admin_user() validation, timezone input parsing, immediate feedback
    - **Tests**: `tests/unit/test_bot_handlers/test_notification_admin_handlers.py` - Test admin permission validation, time parsing, error messages
    - **Done**: Handlers validate admin permissions, parse time/timezone input, provide clear user feedback
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Integrate Scheduler with Main Application using post_init
  - [ ] Sub-step 2.1: Add post_init scheduler initialization to main.py
    - **Directory**: `src/`
    - **Files to create/modify**: `src/main.py`
    - **Accept**: Uses Application.post_init callback to initialize scheduler after bot starts, checks notification settings, handles errors gracefully
    - **Tests**: `tests/unit/test_main.py` - Test post_init callback, conditional initialization, error handling
    - **Done**: Application properly initializes scheduler after bot startup using post_init pattern
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 2.2: Register notification admin commands with CommandHandler
    - **Directory**: `src/`
    - **Files to create/modify**: `src/main.py`
    - **Accept**: CommandHandler instances for /notifications, /set_notification_time, /test_stats registered in create_application()
    - **Tests**: `tests/integration/test_bot_handlers/test_notification_integration.py` - Test handler registration, end-to-end command execution
    - **Done**: Commands are properly registered and accessible to admin users through the bot
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Command handlers in tests/unit/test_bot_handlers/
- [ ] Unit tests: Main application integration in tests/unit/test_main.py
- [ ] Integration tests: End-to-end command execution in tests/integration/
- [ ] Permission tests: Admin authorization validation

## Success Criteria
- [ ] All acceptance criteria met
- [ ] Tests pass (100% required)
- [ ] No regressions in existing bot functionality
- [ ] Commands are properly registered and accessible
- [ ] Admin permissions work correctly
- [ ] post_init integration works with bot lifecycle
- [ ] Code review approved

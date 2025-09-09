# Business Requirements: Conversation Timeout Handler Implementation
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-09

## Business Context
Improve user experience by automatically handling inactive conversations with clear recovery options, preventing users from getting stuck in stale conversation states.

## Primary Objective
Implement automatic conversation timeout handling that gracefully terminates inactive conversations and provides users with a clear path to restart their session through the main menu.

## Use Cases
1. **Inactive User Session Recovery**
   - User starts a conversation flow (e.g., participant search) but becomes inactive for an extended period
   - After timeout period expires, bot automatically displays "Сессия истекла, начните заново" message
   - User receives a button to return to the main menu and can restart their workflow
   - **Acceptance Criteria**: Timeout triggers after configurable period, message displays in Russian, main menu button is functional

2. **Consistent Timeout Behavior Across All States** 
   - All conversation handler states (search, edit, confirm, etc.) should have consistent timeout behavior
   - No conversation state should be left without timeout handling
   - **Acceptance Criteria**: Every ConversationHandler state includes TIMEOUT handler, behavior is uniform across all flows

3. **Graceful State Cleanup**
   - When timeout occurs, any temporary conversation state should be properly cleaned up
   - User should not experience any residual state from the timed-out conversation
   - **Acceptance Criteria**: No memory leaks or stale state after timeout, clean transition to main menu

## Success Metrics
- [ ] Zero instances of users getting stuck in conversation states without recovery options
- [ ] Improved user satisfaction with bot responsiveness and clear error recovery
- [ ] Reduced support requests related to "bot not responding" or "stuck in conversation"

## Constraints
- Must maintain backwards compatibility with existing conversation flows
- Timeout period should be configurable without code changes
- Russian language requirement for timeout message
- Must not interfere with legitimate long-running conversations

---

# Test Plan: Conversation Timeout Handler Implementation
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-01-09

## Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

## Proposed Test Categories

### Business Logic Tests
- [ ] Test conversation timeout configuration loading from settings
- [ ] Test timeout message content in Russian ("Сессия истекла, начните заново")
- [ ] Test main menu button creation and functionality after timeout
- [ ] Test timeout period validation and default value handling

### State Transition Tests  
- [ ] Test timeout handler registration in all ConversationHandler states
- [ ] Test transition from any conversation state to ConversationHandler.END on timeout
- [ ] Test proper cleanup of conversation context data on timeout
- [ ] Test main menu restoration after timeout occurs

### Error Handling Tests
- [ ] Test timeout handler when conversation state is already ended
- [ ] Test timeout behavior with malformed conversation context
- [ ] Test timeout handling during network interruptions
- [ ] Test timeout message delivery failure scenarios

### Integration Tests
- [ ] Test end-to-end timeout flow from search conversation states
- [ ] Test timeout integration with existing keyboard handlers
- [ ] Test timeout behavior across all conversation handler types (search, edit, etc.)
- [ ] Test configuration reload without bot restart

### User Interaction Tests
- [ ] Test timeout message display formatting and Russian text
- [ ] Test main menu button click handling after timeout
- [ ] Test conversation restart capability after timeout recovery
- [ ] Test user experience flow: start conversation → timeout → recover → restart

## Test-to-Requirement Mapping
- **Inactive User Session Recovery** → Tests: timeout message content, main menu button functionality, end-to-end timeout flow
- **Consistent Timeout Behavior** → Tests: timeout handler registration, state transition tests, all conversation handler integration  
- **Graceful State Cleanup** → Tests: conversation context cleanup, proper transition to END state, configuration reload

---

# TECHNICAL TASK
**Status**: 🟡 In Progress | **Started by**: Implementation Agent | **Date**: 2025-01-09

## Technical Requirements
- [ ] Add conversation_timeout parameter to ConversationHandler configuration
- [ ] Implement ConversationHandler.TIMEOUT handler for all conversation states
- [ ] Create reusable timeout handler function that displays Russian timeout message
- [ ] Generate main menu keyboard for timeout recovery
- [ ] Ensure timeout period is configurable via TelegramSettings
- [ ] Maintain backward compatibility with existing conversation flows
- [ ] Apply timeout handling to all states in the integrated search/edit conversation handler

## Implementation Steps & Change Log

- [x] ✅ Step 1: Add timeout configuration to settings - Completed 2025-01-09
  - [x] ✅ Sub-step 1.1: Add conversation timeout settings to TelegramSettings - Completed 2025-01-09
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/settings.py`
    - **Accept**: TelegramSettings contains conversation_timeout_minutes with env var support and validation
    - **Tests**: `tests/unit/test_config/test_settings.py`
    - **Done**: Settings validation passes, timeout accessible via get_telegram_settings()
    - **Changelog**: [Added conversation_timeout_minutes field with 30-minute default, TELEGRAM_CONVERSATION_TIMEOUT_MINUTES env var support, validation for 1-1440 minutes range, comprehensive test coverage]

- [x] ✅ Step 2: Create timeout handler function and keyboard - Completed 2025-01-09
  - [x] ✅ Sub-step 2.1: Implement timeout message handler - Completed 2025-01-09
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/timeout_handlers.py`
    - **Accept**: Function returns Russian timeout message with main menu keyboard
    - **Tests**: `tests/unit/test_bot_handlers/test_timeout_handlers.py`
    - **Done**: Handler function created, tested, and properly formatted
    - **Changelog**: [Created handle_conversation_timeout function with Russian timeout message, main menu keyboard recovery, edge case handling, 100% test coverage with 6 comprehensive test cases]

- [x] ✅ Step 3: Update ConversationHandler with timeout configuration - Completed 2025-01-09
  - [x] ✅ Sub-step 3.1: Add timeout parameter to conversation handler - Completed 2025-01-09
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_conversation.py`
    - **Accept**: ConversationHandler includes conversation_timeout and ConversationHandler.TIMEOUT handler
    - **Tests**: `tests/unit/test_bot_handlers/test_search_conversation_timeout.py`
    - **Done**: Timeout configuration applied, handler registered for TIMEOUT state
    - **Changelog**: [Added conversation_timeout parameter with minutes-to-seconds conversion, registered handle_conversation_timeout for TIMEOUT state, imported settings for dynamic configuration, comprehensive integration tests with 7 test cases covering all timeout scenarios]

- [ ] Step 4: Test integration and verify timeout behavior
  - [ ] Sub-step 4.1: Create comprehensive integration tests
    - **Directory**: `tests/integration/test_bot_handlers/`
    - **Files to create/modify**: `tests/integration/test_bot_handlers/test_conversation_timeout_integration.py`
    - **Accept**: Tests cover timeout from all states, proper cleanup, and recovery workflow
    - **Tests**: Test file itself provides integration coverage
    - **Done**: All timeout scenarios tested, edge cases covered
    - **Changelog**: []

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-01-09
**Decision**: No Split Needed  
**Reasoning**: Atomic feature implementation with tightly coupled components (~300-400 lines total). Sequential dependencies between config → handler → integration make independent delivery impractical. Optimal PR size for single review session with complete functionality delivery.

## Tracking & Progress
### Linear Issue
- **ID**: AGB-37
- **URL**: https://linear.app/alexandrbasis/issue/AGB-37/add-conversation-timeout-handler-to-telegram-bot

### PR Details
- **Branch**: feature/AGB-37-conversation-timeout-handler
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]
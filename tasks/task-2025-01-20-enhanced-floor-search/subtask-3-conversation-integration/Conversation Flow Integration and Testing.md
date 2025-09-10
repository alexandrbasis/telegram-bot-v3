# Task: Conversation Flow Integration and Testing
**Created**: 2025-01-20 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Integrate floor discovery UI components with conversation handler registration and validate the complete user journey through comprehensive testing.

### Use Cases
1. **Seamless Conversation Flow**: Floor discovery callbacks work within existing conversation states
   - **Acceptance Criteria**: CallbackQueryHandler entries registered for "floor_discovery" and "floor_select_*" patterns in WAITING_FOR_FLOOR state
2. **Complete User Journey**: End-to-end flow from floor search to discovery to selection to results
   - **Acceptance Criteria**: User can navigate: floor search → discovery button → floor selection → participant results
3. **Backward Compatibility**: Traditional numeric floor input continues to work alongside new interactive features
   - **Acceptance Criteria**: Manual floor number input processed identically to previous behavior

### Success Metrics
- [ ] Complete user journey works without state transition errors
- [ ] Callback handlers properly registered and responding in conversation flow
- [ ] Both interactive and traditional input methods function simultaneously
- [ ] Integration testing validates all error recovery scenarios

### Constraints
- Must not break existing conversation flow or state transitions
- Both callback handlers must be registered in FloorSearchStates.WAITING_FOR_FLOOR state
- Integration testing must cover both success and failure paths
- All error recovery scenarios must return users to appropriate states

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-56
- **URL**: https://linear.app/alexandrbasis/issue/TDB-56/subtask-3-conversation-flow-integration-and-testing
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Register floor discovery callback handlers in ConversationHandler
- [ ] Implement comprehensive integration testing for complete user journey
- [ ] Validate error recovery scenarios and callback timeout handling
- [ ] Ensure backward compatibility with existing floor search functionality
- [ ] Verify all state transitions work correctly with new callback handlers

## Implementation Steps & Change Log
- [ ] Step 1: Update conversation handler registration
  - [ ] Sub-step 1.1: Register floor discovery callback handlers in ConversationHandler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `search_conversation.py`
    - **Accept**: CallbackQueryHandler entries for "floor_discovery" and "floor_select_*" patterns
    - **Tests**: Update existing `tests/unit/test_bot_handlers/test_search_conversation_floor.py`
    - **Done**: Conversation flow includes callback handlers in WAITING_FOR_FLOOR state
    - **Callback Registration**: Both handlers registered in FloorSearchStates.WAITING_FOR_FLOOR state
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Comprehensive integration testing
  - [ ] Sub-step 2.1: End-to-end floor discovery flow integration testing
    - **Directory**: `tests/integration/test_bot_handlers/`
    - **Files to create/modify**: Add test cases to existing integration test files
    - **Accept**: Complete user journey: floor search → discovery button → floor selection → results
    - **Tests**: Integration test covering both discovery path and traditional input path
    - **Done**: Integration test validates all state transitions, error recovery, callback handling
    - **Error Recovery**: Tests API failure fallback, empty results handling, callback timeout scenarios
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Backward compatibility validation
  - [ ] Sub-step 3.1: Validate traditional floor input still works
    - **Directory**: `tests/integration/test_bot_handlers/`
    - **Files to create/modify**: Enhance existing floor search integration tests
    - **Accept**: Manual numeric floor input processes identically to previous behavior
    - **Tests**: Integration test validates traditional input method unaffected by callback handlers
    - **Done**: Both interactive and manual input methods work simultaneously without interference
    - **Compatibility Tests**: Verify existing functionality unaffected by new callback registration
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Error scenario and timeout handling validation
  - [ ] Sub-step 4.1: Comprehensive error handling testing
    - **Directory**: `tests/integration/test_bot_handlers/`
    - **Files to create/modify**: Add error scenario tests to integration suite
    - **Accept**: All error scenarios properly handled: API failures, empty results, callback timeouts
    - **Tests**: Error handling integration tests validate fallback behavior and user guidance
    - **Done**: Error recovery scenarios return users to appropriate conversation states
    - **Error Coverage**: API failures, timeout scenarios, empty floor results, invalid callback data
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Integration tests: Complete user journey from start to finish in `tests/integration/test_bot_handlers/`
- [ ] Integration tests: Backward compatibility with traditional floor input methods
- [ ] Integration tests: Error recovery and callback timeout scenarios
- [ ] Integration tests: Conversation state transitions with new callback handlers
- [ ] Performance tests: Verify callback handler response times within acceptable limits

## Success Criteria
- [ ] All acceptance criteria met for conversation integration
- [ ] Integration tests pass with comprehensive error scenario coverage
- [ ] Backward compatibility maintained for traditional floor input
- [ ] Callback handlers properly registered and responding in conversation flow
- [ ] Complete end-to-end user journey validates successfully
- [ ] All error recovery scenarios return users to appropriate states
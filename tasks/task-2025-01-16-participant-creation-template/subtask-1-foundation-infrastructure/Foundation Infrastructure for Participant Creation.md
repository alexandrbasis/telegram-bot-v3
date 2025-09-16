# Task: Foundation Infrastructure for Participant Creation
**Created**: 2025-01-16 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Establish the foundational infrastructure for participant creation including conversation handlers, keyboard interfaces, field configuration, and template generation capabilities.

### Use Cases
1. **Handler Infrastructure Setup**
   - User sends `/create_participant` command
   - Bot recognizes command and initiates creation flow
   - User selects "Создать участника" from menu
   - Bot responds with appropriate creation interface
   - **Acceptance Criteria**: Commands and menu selections properly routed to creation handlers

2. **Template Generation System**
   - System generates participant template with required fields first
   - Template includes Russian field labels and clear formatting
   - Required fields marked with asterisk (*) for user clarity
   - Template format follows: "Поле: (описание ожидаемого значения)"
   - **Acceptance Criteria**: Template contains all participant fields in correct order with Russian labels

### Success Metrics
- [ ] Handler responds to creation commands and menu selections
- [ ] Template generation includes all required and optional fields
- [ ] Russian language support implemented correctly
- [ ] Integration with existing bot infrastructure maintained

### Constraints
- Must integrate with existing conversation dispatcher patterns
- Template must follow established Russian language conventions
- No breaking changes to existing bot functionality
- Field configuration must extend existing field_mappings.py structure

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: TDB-60
- **URL**: https://linear.app/alexandrbasis/issue/TDB-60/subtask-1-foundation-infrastructure-for-participant-creation
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

## Technical Requirements
- [ ] Create participant creation conversation handler infrastructure
- [ ] Implement keyboard components for creation workflow
- [ ] Extend field configuration with creation metadata
- [ ] Build template generation service with Russian language support

## Implementation Steps & Change Log
- [ ] Step 1: Create Participant Creation Handler Infrastructure
  - [ ] Sub-step 1.1: Create participant creation conversation handler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/participant_creation_handlers.py`
    - **Accept**: Handler responds to `/create_participant` command and menu selection
    - **Tests**: `tests/unit/test_bot_handlers/test_participant_creation_handlers.py`
    - **Done**: Handler registered in conversation dispatcher and responds to creation requests
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 1.2: Add participant creation keyboard options
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/participant_creation_keyboards.py`
    - **Accept**: Keyboard includes "Создать участника" option and integrates with main menu
    - **Tests**: `tests/unit/test_bot_keyboards/test_participant_creation_keyboards.py`
    - **Done**: Keyboard displays correctly and triggers creation flow
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Extend Existing Field Infrastructure and Template Generation
  - [ ] Sub-step 2.1: Extend field_mappings.py with creation metadata
    - **Directory**: `src/config/`
    - **Files to create/modify**: `src/config/field_mappings.py`
    - **Accept**: Field mappings include creation metadata without duplicating existing structure
    - **Tests**: `tests/unit/test_config/test_field_mappings.py`
    - **Done**: Creation metadata integrated with existing field configuration
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 2.2: Create template generation service using extended field mappings
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_template_service.py`
    - **Accept**: Service generates template with required fields first, Russian labels
    - **Tests**: `tests/unit/test_services/test_participant_template_service.py`
    - **Done**: Template includes all participant fields in correct order
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Handler components in `tests/unit/test_bot_handlers/`
- [ ] Unit tests: Keyboard components in `tests/unit/test_bot_keyboards/`
- [ ] Unit tests: Configuration in `tests/unit/test_config/`
- [ ] Unit tests: Template service in `tests/unit/test_services/`

## Success Criteria
- [ ] All acceptance criteria met for handler infrastructure
- [ ] Template generation working with Russian language support
- [ ] Tests pass (100% required)
- [ ] No regressions in existing bot functionality
- [ ] Code review approved
- [ ] Integration with existing conversation patterns maintained
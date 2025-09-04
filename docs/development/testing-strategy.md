# Testing Strategy

## Overview

Comprehensive testing strategy following the 3-layer architecture with emphasis on unit testing, integration testing, and conversation flow validation.

## Testing Philosophy

### Test-Driven Development
- Unit tests written alongside implementation
- 100% test pass rate required for all features
- Comprehensive coverage for complex business logic

### Layer-Specific Testing
- **Bot Layer**: Handler logic and conversation state management
- **Service Layer**: Business logic validation and error handling  
- **Data Layer**: Repository pattern and data access

## Unit Testing Framework

### Technology Stack
- **Framework**: pytest
- **Mocking**: unittest.mock and pytest fixtures
- **Coverage**: pytest-cov with HTML reports
- **Test Structure**: Tests mirror `src/` directory structure

### Test Organization
```
tests/
├── unit/
│   ├── test_bot/
│   │   ├── test_handlers/
│   │   └── test_keyboards/
│   ├── test_services/
│   └── test_data/
├── integration/
├── fixtures/
└── conftest.py
```

## Participant Editing Interface Testing

### Test Coverage Summary (2025-09-02)
**Total Tests**: 41 tests (29 unit + 8 repository + 4 integration) - Enhanced with 11 regression tests
**Pass Rate**: 100%  
**Coverage Areas**: Handler logic, keyboard generation, field validation, save/cancel workflow, integration flows, participant display after edits, display regression prevention, error handling

#### Handler Testing (`test_edit_participant_handlers.py`)
**Tests**: 29 unit tests (22 original + 7 regression tests)
**Coverage**:
- Conversation state transitions (FIELD_SELECTION → TEXT_INPUT → BUTTON_SELECTION)
- Field selection button handling
- Text input processing with validation
- Button selection processing for enum fields
- Save/cancel workflow
- Error handling and recovery
- Context preservation across states
- Complete participant display after field edits
- Participant reconstruction with applied changes
- **Display Regression Prevention**: Exception handling in display functions, context corruption scenarios
- **Error Resilience**: Comprehensive error handling with graceful degradation and meaningful user feedback

**Key Test Scenarios**:
```python
# State transition testing
test_field_selection_display()
test_text_field_editing_flow()
test_button_field_editing_flow()
test_save_changes_workflow()
test_cancel_changes_workflow()

# Complete participant display testing
test_text_field_success_shows_complete_participant()
test_button_field_success_shows_complete_participant()
test_display_updated_participant_function()
test_participant_reconstruction_with_edits()

# Error handling testing
test_invalid_field_validation()
test_airtable_error_recovery()
test_conversation_timeout_handling()

# Russian localization testing
test_russian_field_labels()
test_russian_error_messages()
```

#### Keyboard Testing (`test_edit_keyboards.py`)
**Tests**: 13 unit tests
**Coverage**:
- Field-specific keyboard generation for all 13 fields
- Russian label validation
- Button layout verification (2-3 columns)
- Cancel button presence
- Option completeness for enum fields

**Key Test Scenarios**:
```python
# Keyboard generation testing
test_gender_keyboard_options()  # М/Ж options
test_size_keyboard_layout()     # XS-3XL layout
test_role_keyboard_labels()     # Кандидат/Команда
test_department_keyboard_completeness()  # All 13 departments
test_payment_status_keyboard()  # Оплачено/Частично/Не оплачено

# Layout and localization testing
test_keyboard_column_layout()
test_cancel_button_presence()
test_russian_label_mapping()
```

#### Service Testing (`test_participant_update_service.py`) 
**Tests**: 26 unit tests
**Coverage**:
- Field validation for all 13 fields
- Enum value conversion (Gender, Size, Role, Department, Payment Status)
- Special field validation (payment amount, payment date)
- Russian error message generation
- Airtable field mapping
- Partial update logic

**Key Test Scenarios**:
```python
# Field validation testing
test_required_field_validation()     # Russian name required
test_optional_field_validation()     # Other text fields
test_enum_field_conversion()         # M/F → Male/Female
test_special_field_validation()      # Amount ≥ 0, date format

# Error message testing  
test_russian_validation_errors()
test_format_specific_error_messages()

# Airtable integration testing
test_field_mapping_accuracy()
test_partial_update_payload()
test_update_error_handling()
```

## Integration Testing

### End-to-End Conversation Flows (`test_search_to_edit_flow.py`)
**Tests**: 4 integration tests (314 lines)
**Coverage**:
- Complete search → edit → save workflows with real conversation states
- Cancel workflow testing with state cleanup verification
- Error recovery and retry mechanisms with change preservation
- Integration between search results and editing interface

**Key Test Scenarios**:
```python
# Complete workflow testing
test_complete_search_to_edit_to_save_flow()     # Happy path end-to-end
test_search_to_edit_cancel_flow()              # Cancel workflow validation
test_search_to_edit_save_retry_flow()          # Error recovery with retry
test_search_to_edit_validation_error_flow()    # Validation error handling
```

### Airtable Integration Testing
**Tests**: 8 repository tests covering `update_by_id()` method
**Coverage**:
- Successful field updates with proper field mapping
- Validation error handling and error message generation
- Network error simulation and retry behavior
- Edge cases and boundary conditions

### Save/Cancel Workflow Integration
- **Change Confirmation**: Verification that confirmation screen shows all pending changes
- **Data Preservation**: Changes maintained through error scenarios and retries
- **State Cleanup**: Clean conversation state transitions on cancel operations
- **Error Recovery**: Failed save operations recoverable without data loss

### Regression Testing

#### Participant Edit Display Regression Tests (`test_edit_participant_handlers.py`)
**Tests**: 11 comprehensive regression prevention tests
**Coverage**:
- **TestDisplayRegressionIssue**: Reproduces root cause scenario where current_participant becomes None
- **TestComprehensiveDisplayRegressionPrevention**: Covers exception handling, context corruption, save success behavior
- **Critical Scenarios**: Display function exceptions, button field display failures, multiple field editing integrity
- **Error Recovery**: Silent failure detection and prevention with detailed logging
- **Production Debugging**: REGRESSION markers for enhanced production monitoring

#### Button Functionality Regression Tests (`test_search_button_regression.py`)
**Tests**: 2 regression tests
**Coverage**:
- ConversationHandler per_message configuration validation
- Search button callback_data pattern matching
- Handler registration in correct state verification
- State collision prevention (SearchStates 10-12 vs EditStates 0-2)

**Key Test Scenarios**:
```python
# ConversationHandler configuration testing
test_conversation_handler_per_message_configuration()
  # Validates per_message=None prevents CallbackQueryHandler tracking issues
  # Confirms mixed handler types work correctly

test_search_button_callback_data_pattern_match()
  # Verifies callback_data="search" matches pattern="^search$"
  # Ensures proper handler registration in SearchStates.MAIN_MENU
```

#### State Management Regression Tests
**Coverage**:
- State enum collision detection and prevention
- ConversationHandler registration conflict avoidance
- CallbackQueryHandler tracking functionality validation
- Button response verification across different conversation states

### Future Integration Test Areas
- Multi-user concurrent editing scenarios  
- Performance testing under load
- Long conversation session stability testing
- State collision stress testing with multiple ConversationHandlers

## Test Execution Commands

### Running All Tests
```bash
# All tests with coverage
./venv/bin/pytest tests/ --cov=src --cov-report=html --cov-report=term

# Unit tests only
./venv/bin/pytest tests/unit/ -v

# Integration tests only  
./venv/bin/pytest tests/integration/ -v
```

### Specific Test Execution
```bash
# Edit functionality tests
./venv/bin/pytest tests/unit/test_bot_handlers/test_edit_participant_handlers.py -v
./venv/bin/pytest tests/unit/test_bot_keyboards/test_edit_keyboards.py -v
./venv/bin/pytest tests/unit/test_services/test_participant_update_service.py -v

# Single test file
./venv/bin/pytest path/to/test_file.py::test_function_name -v
```

### Coverage Analysis
```bash
# Generate HTML coverage report
./venv/bin/pytest tests/ --cov=src --cov-report=html
# View: open htmlcov/index.html

# Terminal coverage summary
./venv/bin/pytest tests/ --cov=src --cov-report=term
```

## Testing Best Practices

### Unit Test Design
- **Isolation**: Each test focuses on single functionality
- **Mocking**: External dependencies mocked (Airtable API, Telegram API)
- **Fixtures**: Shared test data in `tests/fixtures/`
- **Assertion Clarity**: Descriptive test names and clear assertions

### Conversation Testing Patterns
```python
# Handler testing pattern
def test_conversation_state_transition():
    # Setup: Mock context, user data
    # Action: Call handler method
    # Assert: State change, response content, side effects
    
# Service testing pattern  
def test_field_validation():
    # Setup: Input data (valid/invalid)
    # Action: Call validation method
    # Assert: Success/error result, error messages
```

### Error Testing
- **Happy Path**: Normal operation scenarios
- **Validation Errors**: Invalid input handling
- **System Errors**: API failures, timeouts
- **Edge Cases**: Boundary conditions, empty inputs

## Quality Gates

### Code Quality Requirements
- **Test Coverage**: Minimum 90% line coverage
- **Pass Rate**: 100% test pass rate required
- **Code Style**: flake8 and black compliance
- **Type Checking**: mypy validation passing

### Pre-commit Validation
```bash
# Quality check pipeline
./venv/bin/pytest tests/ -v           # All tests pass
./venv/bin/mypy src --no-error-summary  # Type checking
./venv/bin/flake8 src tests            # Code style
./venv/bin/black src tests --check     # Code formatting
```

### Performance Testing
- **Response Time**: Handler execution < 2 seconds
- **Memory Usage**: Conversation context < 1MB per user
- **Rate Limiting**: Airtable API calls within limits

## Room and Floor Search Testing

### Test Coverage Summary (2025-09-04)  
**Total Tests**: 55 tests (Backend: 34, Frontend: 21)
**Backend Tests**: Repository: 12, Service: 6, Validation: 14, Security: 2
**Frontend Tests**: Room Handler: 9, Floor Handler: 9, Integration: 3
**Pass Rate**: 100%  
**Coverage Areas**: Complete end-to-end testing from backend services to frontend conversation flows

#### Repository Testing (`test_airtable_participant_repo.py`)
**Tests**: 12 tests covering room and floor search methods (lines 764-894)
**Coverage**:
- `find_by_room_number()` method with proper field mapping
- `find_by_floor()` method with Union[int, str] support
- Empty result handling and error cases
- Airtable field ID validation (Floor: fldlzG1sVg01hsy2g, RoomNumber: fldJTPjo8AHQaADVu)
- Participant object conversion and data integrity

**Key Test Scenarios**:
```python
# Room search testing
test_find_by_room_number_success()
test_find_by_room_number_empty_results()
test_find_by_room_number_error_handling()

# Floor search testing  
test_find_by_floor_success_with_int()
test_find_by_floor_success_with_str()
test_find_by_floor_empty_results()
test_find_by_floor_error_handling()

# Field mapping validation
test_room_floor_field_mapping_accuracy()
```

#### Service Layer Testing (`test_search_service.py`)
**Tests**: 6 tests covering service layer room/floor methods (lines 583-684)
**Coverage**:
- `search_by_room()` method with input validation
- `search_by_floor()` method with type conversion
- `search_by_room_formatted()` method with result formatting
- Async operation handling and error propagation
- Integration with validation utilities

**Key Test Scenarios**:
```python
# Service method testing
test_search_by_room_with_validation()
test_search_by_floor_with_type_conversion()
test_search_by_room_formatted_output()

# Error handling testing
test_search_service_room_validation_errors()
test_search_service_floor_validation_errors()
test_search_service_repository_error_propagation()
```

#### Validation Testing (`test_validation.py`)
**Tests**: 14 comprehensive validation tests (NEW FILE)
**Coverage**:
- Room number validation with edge cases
- Floor validation with Union[int, str] support
- ValidationResult dataclass functionality
- Empty input handling and error messages
- Whitespace trimming and sanitization

**Key Test Scenarios**:
```python
# Room validation testing
test_validate_room_number_valid_cases()
test_validate_room_number_invalid_cases()
test_validate_room_number_edge_cases()
test_validate_room_number_whitespace_handling()

# Floor validation testing
test_validate_floor_valid_int()
test_validate_floor_valid_str()
test_validate_floor_invalid_cases()
test_validate_floor_type_conversion()

# ValidationResult testing
test_validation_result_success_case()
test_validation_result_error_case()
```

#### Security Testing (`test_airtable_client.py`)
**Tests**: 2 formula injection prevention tests (lines 731-750)
**Coverage**:
- Single quote escaping in search formulas
- Special character handling (O'Connor, Room 'A')
- Formula construction security validation
- Injection attack prevention

**Key Test Scenarios**:
```python
# Security testing
test_search_by_field_escapes_single_quotes()
test_search_by_field_handles_complex_quotes()
```

### Integration with Existing Test Suite

#### Test Infrastructure Enhancements
- **File**: `tests/conftest.py` (NEW FILE)
- **Purpose**: Pytest configuration for src module imports
- **Benefit**: Eliminates PYTHONPATH setup requirements for test execution
- **Coverage**: Ensures all 34 new tests run without environment configuration

#### Async Testing Patterns
- **Framework**: pytest-asyncio with @pytest.mark.asyncio decorators
- **Coverage**: All service layer methods use async/await patterns
- **Integration**: Follows existing async test patterns in the codebase
- **Validation**: Ensures proper async repository method calls

### Test Quality Assurance

#### Code Review Fixes Applied
- **Async/Sync Mismatch**: All service methods converted to async with proper await calls
- **Type Annotations**: Abstract repository methods added for proper type checking
- **Error Handling**: Comprehensive exception handling with graceful degradation
- **Security Enhancement**: Formula injection prevention with quote escaping

#### Test Execution Verification
```bash
# Room/floor search tests
./venv/bin/pytest tests/unit/test_data/test_airtable/test_airtable_participant_repo.py::TestRoomFloorSearch -v
./venv/bin/pytest tests/unit/test_services/test_search_service.py::TestRoomFloorSearch -v
./venv/bin/pytest tests/unit/test_utils/test_validation.py -v

# Security tests
./venv/bin/pytest tests/unit/test_data/test_airtable/test_airtable_client.py::TestFormulaEscaping -v
```

## Frontend Handler Testing (2025-09-04)

### Room Search Handler Testing (`test_room_search_handlers.py`)
**Tests**: 9 comprehensive tests covering room search conversation flow
**Coverage**:
- Room search command handling with `/search_room` entry point
- Room number input validation and error handling  
- Search result formatting and display
- Russian error messages for invalid input
- Empty room handling with user-friendly messages
- Navigation between search modes via reply keyboards
- ConversationHandler state management and transitions

**Key Test Scenarios**:
```python
# Command and input testing
test_room_search_command_handler()
test_room_search_with_valid_input()
test_room_search_with_invalid_input()
test_room_search_empty_results()

# Navigation and state management
test_room_search_keyboard_navigation()
test_room_search_conversation_states()
test_room_search_context_preservation()
```

### Floor Search Handler Testing (`test_floor_search_handlers.py`) 
**Tests**: 9 comprehensive tests covering floor search conversation flow
**Coverage**:
- Floor search command handling with `/search_floor` entry point
- Floor number input validation with Union[int, str] support
- Room-by-room result formatting and grouping
- Participant count display and room organization  
- Russian localization throughout conversation flow
- Error handling for invalid floor inputs
- Empty floor handling with appropriate messaging
- Integration with search mode selection interface

**Key Test Scenarios**:
```python
# Command and input testing  
test_floor_search_command_handler()
test_floor_search_with_valid_input()
test_floor_search_with_invalid_input()
test_floor_search_empty_results()

# Result formatting and display
test_floor_search_room_grouping()
test_floor_search_participant_counting()
test_floor_search_russian_formatting()
```

### Search Integration Testing (`test_search_handlers.py`)  
**Tests**: 3 additional tests covering search mode selection integration
**Coverage**:
- Search mode selection keyboard functionality
- Navigation between name/room/floor search modes
- ConversationHandler integration with existing search flows
- State management across different search types

## Testing Roadmap

### Current Status
- [x] ✅ Comprehensive unit testing (29 unit tests with regression coverage, 100% pass)
- [x] ✅ Handler conversation flow testing with save/cancel workflow
- [x] ✅ Service layer validation testing
- [x] ✅ Keyboard generation testing
- [x] ✅ Repository integration testing (8 update_by_id tests)
- [x] ✅ End-to-end integration testing (4 workflow tests)
- [x] ✅ Save confirmation and retry mechanism testing
- [x] ✅ **Display regression prevention testing (11 comprehensive tests)**
- [x] ✅ **Error handling and graceful degradation testing**
- [x] ✅ **Production debugging support with REGRESSION logging markers**
- [x] ✅ Regression testing for search button functionality (2 tests)
- [x] ✅ State collision prevention testing and validation
- [x] ✅ ConversationHandler configuration testing (per_message parameter)
- [x] ✅ **Room and floor search backend testing (34 comprehensive tests)**
- [x] ✅ **Room and floor search frontend testing (21 comprehensive tests)**
- [x] ✅ **Input validation utilities testing with edge case coverage**
- [x] ✅ **Security enhancement testing (formula injection prevention)**
- [x] ✅ **Test infrastructure improvements (conftest.py for module imports)**
- [x] ✅ **Complete conversation flow testing for room/floor search modes**
- [x] ✅ **Russian localization testing throughout search interfaces**
- [ ] ⏳ Performance benchmarking
- [ ] ⏳ Load testing for concurrent users

### Future Enhancements
- **Property-Based Testing**: Hypothesis integration for edge case discovery
- **Contract Testing**: API contract validation with Airtable
- **Visual Testing**: UI screenshot comparison for Telegram interfaces
- **Chaos Engineering**: Fault injection and recovery testing
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
│   ├── test_data/
│   ├── test_config/
│   └── test_main.py
├── integration/
├── fixtures/
└── conftest.py
```

## Participant Editing Interface Testing

### Test Coverage Summary (2025-08-31)
**Total Tests**: 59 tests (47 unit + 8 repository + 4 integration)
**Pass Rate**: 100%  
**Coverage Areas**: Handler logic, keyboard generation, field validation, save/cancel workflow, integration flows, file logging service

#### Handler Testing (`test_edit_participant_handlers.py`)
**Tests**: 17 unit tests
**Coverage**:
- Conversation state transitions (FIELD_SELECTION → TEXT_INPUT → BUTTON_SELECTION)
- Field selection button handling
- Text input processing with validation
- Button selection processing for enum fields
- Save/cancel workflow
- Error handling and recovery
- Context preservation across states

**Key Test Scenarios**:
```python
# State transition testing
test_field_selection_display()
test_text_field_editing_flow()
test_button_field_editing_flow()
test_save_changes_workflow()
test_cancel_changes_workflow()

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

#### File Logging Service Testing (`test_file_logging_service.py`)
**Tests**: 11 unit tests (New - 2025-08-31)
**Coverage**:
- File logging service initialization and configuration
- Directory creation and management (application/, user-interactions/, errors/, archived/)
- Log handler setup and file writing
- Error handling (disk space, permissions, file system issues)
- Integration with existing logging system
- Performance validation (zero impact on application)

**Key Test Scenarios**:
```python
# File logging service testing
test_file_logging_service_initialization()
test_log_directory_creation()
test_file_handler_setup_and_configuration()
test_log_writing_to_correct_files()
test_error_handling_disk_space_insufficient()
test_error_handling_permission_denied()
test_integration_with_console_logging()
test_performance_impact_measurement()
```

#### Configuration Testing (`test_settings.py`)
**Tests**: 6 unit tests for file logging configuration (New - 2025-08-31)
**Coverage**:
- File logging settings default values
- Environment variable loading and parsing
- Configuration validation and error handling
- FileLoggingConfig creation and integration

**Key Test Scenarios**:
```python
# Configuration testing
test_file_logging_default_settings()
test_file_logging_environment_variables()
test_file_logging_validation_errors()
test_get_file_logging_config_creation()
```

#### Main Application Integration Testing (`test_main.py`)
**Tests**: 9 unit tests (New - 2025-08-31)
**Coverage**:
- File logging initialization during application startup
- Integration with existing console logging configuration
- Error handling when file logging setup fails
- Graceful degradation scenarios

**Key Test Scenarios**:
```python
# Main application testing
test_configure_logging_with_file_logging()
test_file_logging_initialization_failure_handling()
test_get_file_logging_service_access()
test_console_logging_preservation()
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

## Testing Roadmap

### Current Status
- [x] ✅ Comprehensive unit testing (47 unit tests, 100% pass)
- [x] ✅ Handler conversation flow testing with save/cancel workflow
- [x] ✅ Service layer validation testing
- [x] ✅ Keyboard generation testing
- [x] ✅ Repository integration testing (8 update_by_id tests)
- [x] ✅ End-to-end integration testing (4 workflow tests)
- [x] ✅ Save confirmation and retry mechanism testing
- [x] ✅ Regression testing for search button functionality (2 tests)
- [x] ✅ State collision prevention testing and validation
- [x] ✅ ConversationHandler configuration testing (per_message parameter)
- [x] ✅ File logging service testing (11 comprehensive tests)
- [x] ✅ Configuration system testing for file logging (6 tests)
- [x] ✅ Main application integration testing (9 tests)
- [ ] ⏳ Performance benchmarking
- [ ] ⏳ Load testing for concurrent users

### Future Enhancements
- **Property-Based Testing**: Hypothesis integration for edge case discovery
- **Contract Testing**: API contract validation with Airtable
- **Visual Testing**: UI screenshot comparison for Telegram interfaces
- **Chaos Engineering**: Fault injection and recovery testing
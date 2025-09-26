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
│   ├── test_bot_handlers/
│   │   ├── test_search_handlers.py      # Includes equivalence tests for start/main menu
│   │   ├── test_cancel_handler.py       # Cancel handler consistency tests
│   │   └── test_edit_participant_handlers.py
│   ├── test_bot_keyboards/
│   ├── test_services/
│   │   ├── test_security_audit_service.py      # Security audit logging (23 tests)
│   │   ├── test_participant_export_service.py  # CSV export service testing
│   │   └── test_participant_update_service.py
│   ├── test_utils/
│   │   ├── test_auth_utils.py           # Admin authentication testing
│   │   └── test_auth_performance.py     # Authorization performance benchmarks (12 tests)
│   └── test_data/
├── integration/
│   ├── test_bot_handlers/
│   │   └── test_timeout_recovery_integration.py  # Timeout recovery with text buttons
│   ├── test_access_control_integration.py        # End-to-end security validation (6 tests)
│   └── test_security_bypass_attempts.py          # Penetration testing (7 attack vectors)
├── fixtures/
└── conftest.py
```

### Main Menu Start Command Equivalence Testing (2025-09-09)
**Test Coverage**: 12 comprehensive tests across multiple files ensuring Main Menu button provides identical functionality to `/start` command.

**Test Categories**:
1. **Shared Helper Tests**: Validation of `initialize_main_menu_session()` and `get_welcome_message()` functions
2. **Equivalence Tests**: Verification that both handlers produce identical results (state, messages, keyboard)
3. **Integration Tests**: Text button entry points for timeout recovery
4. **Cancel Handler Tests**: Consistency with shared initialization helpers

## Security Testing Framework (Added 2025-09-25)

### Comprehensive Security Validation
**Total Security Tests**: 71 tests across multiple categories ensuring complete security coverage

#### Security Audit Service Testing (`test_security_audit_service.py`)
**Test Coverage**: 23 comprehensive unit tests
- **Authorization Event Testing**: Event creation, logging, and structured data validation
- **Performance Metrics Testing**: Threshold-based severity assignment and performance correlation
- **Sync Event Testing**: Airtable synchronization event tracking and error handling
- **Cache State Tracking**: Hit/miss monitoring and security event correlation
- **Error Handling**: Security service error conditions and graceful recovery
- **Integration Testing**: Service integration with authorization system components

#### Authorization Performance Benchmarking (`test_auth_performance.py`)
**Test Coverage**: 12 performance validation tests
- **Cache Hit Performance**: Validation of 0.22ms response times (450x faster than requirements)
- **Cache Miss Performance**: Validation of 0.45ms response times (665x faster than requirements)
- **Concurrent Access Testing**: Thread-safe operation validation under load
- **Large Scale Testing**: Performance maintenance with 10K+ user cache
- **Health Monitoring**: Cache statistics accuracy and real-time performance tracking
- **Manual Invalidation**: Cache clearing functionality and performance impact

#### Security Integration Testing (`test_access_control_integration.py`)
**Test Coverage**: 6 comprehensive end-to-end security scenarios
- **Admin Workflow Testing**: Complete authorization workflow with audit logging
- **Role Transition Testing**: Dynamic role changes and cache invalidation validation
- **Decorator Integration**: Authorization decorator enforcement across handler types
- **Audit Trail Completeness**: Security event logging across complete request flows
- **Cache Performance Integration**: Real-world cache behavior with audit service
- **Error Recovery Testing**: Security during system failures and recovery scenarios

#### Security Penetration Testing (`test_security_bypass_attempts.py`)
**Test Coverage**: 7 attack vector validation tests
- **Cache Poisoning Attacks**: CRITICAL vulnerability discovered - privilege escalation prevention
- **Timing Attack Testing**: MEDIUM vulnerability identified - 0.60ms timing variance validation
- **Injection Attack Prevention**: SQL/NoSQL injection protection across input vectors
- **Privilege Escalation Prevention**: Authorization bypass attempt blocking
- **Race Condition Testing**: Concurrent authorization request security validation
- **Session Hijacking Prevention**: Session security and token validation
- **Boundary Value Testing**: Edge case security validation and input sanitization

### Security Testing Methodology

#### Test-Driven Security Development
- **Red-Green-Refactor**: Security tests written first, implementation follows
- **Vulnerability Discovery**: Real security issues found through comprehensive testing
- **Regression Prevention**: Security test suite prevents future vulnerability introduction
- **Coverage Validation**: Security requirements validated through automated testing

#### Security Test Categories
1. **Authentication Testing**: User identity validation and token security
2. **Authorization Testing**: Role-based access control enforcement across all layers
3. **Data Protection Testing**: PII filtering and sensitive data exposure prevention
4. **Performance Security**: DoS protection and resource exhaustion prevention
5. **Input Validation**: Injection attack prevention and input sanitization
6. **Audit Trail Testing**: Complete security event logging and monitoring
7. **Cache Security**: Authorization cache integrity and poisoning prevention

#### Discovered Security Issues
**CRITICAL Vulnerabilities**:
- **Cache Poisoning**: Direct `_ROLE_CACHE` manipulation allows privilege escalation
- **Impact**: Memory access attackers could gain admin privileges
- **Status**: Documented with mitigation strategies, pending implementation

**MEDIUM Vulnerabilities**:
- **Timing Attacks**: 0.60ms authorization timing variance enables user enumeration
- **Impact**: Attackers could determine valid user IDs through timing analysis
- **Status**: Confirmed through testing, timing normalization recommended

### Security Testing Automation
- **CI/CD Integration**: All security tests run on every commit
- **Regression Prevention**: Security test failures block deployment
- **Performance Validation**: Authorization performance benchmarks enforced
- **Vulnerability Scanning**: Automated dependency vulnerability checks

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

## Line Numbers Export Feature Testing (2025-01-26)

### Test Coverage Summary
**Total Tests**: 36 new line number specific tests (29 unit + 5 integration + 2 utility tests)
**Pass Rate**: 100%
**Coverage**: Complete line number functionality across all export services

#### Line Number Utility Functions Testing (`test_export_utils.py`)
**Tests**: 18 comprehensive unit tests covering core line number utilities
**Coverage**:
- `format_line_number()`: Line number formatting with consistent padding
- `add_line_numbers_to_csv()`: CSV string enhancement with line numbers
- `add_line_numbers_to_rows()`: Row data structure line number addition
- `extract_participant_count_from_csv()`: Total count extraction from CSV
- `format_export_success_message()`: Success message formatting with counts
- Unicode content handling and edge case validation

**Key Test Scenarios**:
```python
# Line number formatting testing
test_format_line_number_basic()
test_format_line_number_padding()
test_format_line_number_edge_cases()

# CSV enhancement testing
test_add_line_numbers_to_csv_basic()
test_add_line_numbers_to_csv_empty()
test_add_line_numbers_to_csv_unicode_content()

# Count extraction testing
test_extract_participant_count_basic()
test_extract_participant_count_empty()
test_extract_participant_count_edge_cases()

# Success message formatting
test_format_export_success_message_basic()
test_format_export_success_message_zero_count()
```

#### Export Services Line Number Integration Testing
**ParticipantExportService Tests**: 7 new line number integration tests
**BibleReadersExportService Tests**: 6 comprehensive line number tests
**RoeExportService Tests**: 6 comprehensive line number tests

**Coverage**:
- Line numbers as first column in all CSV exports
- Sequential numbering starting from 1
- Header modification to include "#" column
- Integration with existing export functionality
- Backward compatibility preservation

**Key Test Scenarios**:
```python
# Service integration testing
test_line_numbers_appear_as_first_column()
test_line_numbers_are_sequential()
test_headers_include_line_number_column()
test_empty_export_handles_line_numbers()
test_large_export_line_numbering()
```

#### Integration Testing for Line Numbers (`test_export_selection_workflow.py`)
**Tests**: 5 end-to-end integration tests validating complete export workflows
**Coverage**:
- Line numbers in participant exports (all, team, candidates)
- Line numbers in department-specific exports
- Line numbers in Bible readers and ROE exports
- Export success message count display
- Complete user workflow validation

**Key Test Scenarios**:
```python
# End-to-end line number validation
test_participant_export_includes_line_numbers()
test_department_export_includes_line_numbers()
test_bible_readers_export_includes_line_numbers()
test_roe_export_includes_line_numbers()
test_export_success_messages_show_counts()
```

#### Testing Methodology
**TDD Implementation**: Strict Test-Driven Development with Red-Green-Refactor cycles
- All utility functions developed using TDD approach
- Comprehensive edge case coverage including empty exports
- Unicode and Russian text validation
- Error handling and validation testing

**Performance Testing**: Line number addition tested with large datasets
- No performance impact validation
- Memory efficiency confirmation
- Large export handling (100+ participants)

## CSV Export Service Testing (2025-01-15)

### Test Coverage Summary
**Total Tests**: 30 tests (19 service tests + 11 authentication tests)
**Pass Rate**: 100%
**Coverage**: 91% for export service, 100% for authentication utilities

#### Export Service Testing (`test_participant_export_service.py`)
**Tests**: 19 comprehensive unit tests covering all methods and edge cases
**Coverage**:
- CSV generation with repository integration
- Progress tracking callback functionality
- File management and secure temporary file creation
- Size estimation and Telegram limit validation
- UTF-8 encoding support for Russian text
- Error handling and resource cleanup
- Large dataset handling (1500+ records)

**Key Test Scenarios**:
```python
# CSV export testing
test_get_all_participants_as_csv_success()
test_get_all_participants_as_csv_empty_dataset()
test_get_all_participants_as_csv_with_progress_callback()
test_csv_generation_with_none_values()
test_csv_generation_large_dataset()

# File management testing
test_save_to_file_default_directory()
test_save_to_file_custom_directory()
test_save_to_file_cleanup_on_error()
test_file_size_estimation()
test_telegram_limit_validation()

# Field mapping integration testing
test_field_mapping_integration()
test_csv_headers_match_airtable_structure()
test_utf8_encoding_support()

# Error handling testing
test_repository_error_handling()
test_invalid_directory_handling()
test_resource_cleanup_on_exceptions()
```

#### Authentication Utilities Testing (`test_auth_utils.py`)
**Tests**: 11 comprehensive unit tests with 100% coverage
**Coverage**:
- Admin user validation with various input types
- Type conversion and validation (int, str, None handling)
- Settings integration and configuration validation
- Edge cases and error scenarios
- Logging validation for authentication attempts

**Key Test Scenarios**:
```python
# Authentication testing
test_is_admin_user_valid_int_user_id()
test_is_admin_user_valid_str_user_id()
test_is_admin_user_invalid_user_id()
test_is_admin_user_none_user_id()
test_is_admin_user_empty_admin_list()

# Type conversion testing
test_is_admin_user_type_conversion()
test_is_admin_user_invalid_type_conversion()

# Settings integration testing
test_is_admin_user_settings_integration()
test_is_admin_user_multiple_admins()

# Edge case testing
test_is_admin_user_edge_cases()
test_is_admin_user_logging_validation()
```

### Testing Methodology

#### Test-Driven Development Approach
- **Implementation**: All tests written alongside service implementation
- **Coverage Goals**: Minimum 90% code coverage achieved (91% service, 100% auth)
- **Edge Case Focus**: Comprehensive testing of boundary conditions and error scenarios
- **Mock Strategy**: Repository mocking for isolated service testing

#### Performance and Scalability Testing
- **Large Dataset Testing**: Validated with 1500+ participant records
- **Memory Efficiency**: Streaming CSV generation prevents memory exhaustion
- **Progress Tracking**: Minimal overhead callback testing with mock verification
- **File Size Estimation**: Accurate size prediction for large datasets

#### Security and Error Handling Testing
- **Admin Authentication**: Comprehensive validation of unauthorized access prevention
- **Type Safety**: Robust testing of input type handling and conversion
- **Resource Cleanup**: Try-finally block testing ensures proper file cleanup
- **Error Recovery**: Exception handling testing with graceful degradation

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

## Integration Testing for Room and Floor Search (2025-09-05)

### Comprehensive Integration Test Suite
**Test Files**: 3 dedicated integration test files with 28 total tests
**Coverage**: End-to-end workflows, performance validation, schema verification, error handling

#### Room Search Integration Tests (`test_room_search_integration.py`)
**Tests**: 7 comprehensive integration test cases (298 lines)
**Coverage**:
- Complete room search workflow from command to response
- Valid room search with real Airtable field mapping validation
- Invalid room input handling with standardized error messages
- Empty room result handling with appropriate user feedback
- API error scenarios with graceful degradation
- Performance validation ensuring <3 second response times
- Alphanumeric room number support ("101", "A1", "Conference")

**Key Test Scenarios**:
```python
# End-to-end workflow testing
test_room_search_valid_input_integration()
test_room_search_invalid_input_integration()
test_room_search_empty_results_integration()
test_room_search_api_error_integration()
test_room_search_performance_integration()
test_room_search_alphanumeric_support_integration()
test_room_search_field_mapping_integration()
```

#### Floor Search Integration Tests (`test_floor_search_integration.py`)
**Tests**: 11 comprehensive integration test cases (414 lines)
**Coverage**:
- Complete floor search workflow with multi-room grouping
- String and numeric floor number support ("1", "2", "Ground")
- Room-by-room result formatting and participant counting
- Empty floor handling with user-friendly messaging
- API error scenarios with proper error propagation
- Missing room number handling for robust data processing
- Alphanumeric room sorting with numeric-first ordering
- Performance validation for complex floor queries

**Key Test Scenarios**:
```python
# Comprehensive floor search testing
test_floor_search_multi_room_integration()
test_floor_search_string_floor_integration()
test_floor_search_empty_floor_integration()
test_floor_search_missing_room_numbers_integration()
test_floor_search_alphanumeric_room_sorting_integration()
test_floor_search_api_error_integration()
test_floor_search_performance_integration()
```

#### Airtable Schema Validation Tests (`test_airtable_schema_validation.py`)
**Tests**: 10 schema validation test cases (321 lines)
**Coverage**: 
- Field ID mapping validation (Floor: fldlzG1sVg01hsy2g, RoomNumber: fldJTPjo8AHQaADVu)
- Repository integration with correct field usage
- Missing field handling and format validation
- Schema alignment verification with production Airtable structure
- Repository factory service integration testing

**Key Test Scenarios**:
```python
# Schema and field mapping validation
test_airtable_field_ids_are_correct()
test_repository_uses_correct_field_mappings()
test_service_factory_integration()
test_missing_field_handling()
test_field_format_validation()
```

### Error Handling and Performance Validation

#### Standardized Error Message Implementation
**Implementation**: Centralized message templates in `src/bot/messages.py` (161 lines)
**Coverage**:
- Room validation errors: "Пожалуйста, введите корректный номер комнаты"
- Floor validation errors: "Пожалуйста, введите корректный номер этажа"
- Empty result messages: "По заданному запросу ничего не найдено"
- API failure messages: "Произошла ошибка. Попробуйте позже"
- Consistent formatting and retry guidance across all handlers

#### Performance Testing Integration
**Performance Requirements**: All searches must complete within 3 seconds
**Test Implementation**: Every integration test includes performance validation
**Coverage Areas**:
- Room search response time measurement
- Floor search with multi-room processing performance
- API response time monitoring
- Complex query optimization validation

### Test Quality and Reliability

#### Test Infrastructure Enhancements
- **Comprehensive Mocking**: Proper Airtable API mocking while validating real field mappings
- **Error Scenario Testing**: API failures, network timeouts, malformed data handling
- **Production Alignment**: Tests verify actual field IDs used in production
- **Integration Verification**: Service factory and repository layer integration validated

#### Code Quality Fixes Applied During Integration
- **Factory Wiring**: Fixed SearchService construction to use keyword arguments
- **Field Mapping Updates**: Repository uses mapping-based field names in formulas
- **Schema Alignment**: RoomNumber set to TEXT type with alphanumeric support
- **Test Normalization**: All tests follow repository contract patterns
- **Backward Compatibility**: Existing search functionality fully preserved

## Department Filtering Integration Testing (2025-01-21)

### Repository and Service Layer Testing
**Test Coverage**: Department filtering functionality with chief-first ordering and AsyncMock integration
**Total Tests**: 123 tests passing (enhanced from previous count)
**Coverage Areas**: Repository interface compliance, Airtable implementation, service layer integration, chief indicator formatting

#### Repository Interface Testing
**Tests**: Repository interface compliance for `get_team_members_by_department` method
**Coverage**:
- Abstract method definition validation
- Department parameter handling (Optional[Department])
- Chief-first sorting implementation
- Airtable formula generation for department filtering
- Error handling for invalid departments

#### Airtable Implementation Testing
**Tests**: Comprehensive testing of department filtering with complex queries
**Coverage**:
- Department-specific filtering formulas (`{Department} = 'ROE'`)
- Chief-first sorting with multi-field sort parameters
- "Unassigned" participant filtering (`{Department} = BLANK()`)
- All participants retrieval (no filter applied)
- Performance optimization with server-side filtering

#### Service Layer Integration Testing
**Tests**: Service layer department filtering with backward compatibility
**Coverage**:
- Optional department parameter integration
- Chief indicator formatting with crown emoji (👑)
- Backward compatibility validation (existing callers unaffected)
- Integration with existing pagination and list functionality
- Russian formatting preservation with new chief indicators

#### Integration Test Updates (Critical Fix)
**Issue Resolved**: Integration tests failing due to outdated mock expectations
**Solution Applied**: Updated `tests/integration/test_participant_list_service_repository.py` with:
- AsyncMock configuration for `get_team_members_by_department` method
- Comprehensive test scenarios for department filtering workflows
- Chief indicator display functionality validation
- **Result**: All 9 integration tests passing, maintaining 1050/1050 total test suite success

**Key Test Scenarios**:
```python
# Department filtering integration testing
test_department_filtering_with_chief_ordering()
test_all_participants_retrieval_integration()
test_unassigned_participants_filtering()
test_chief_indicator_display_integration()
test_backward_compatibility_preservation()
```

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

# CSV export functionality tests
./venv/bin/pytest tests/unit/test_services/test_participant_export_service.py -v
./venv/bin/pytest tests/unit/test_utils/test_auth_utils.py -v

# File delivery error handling tests
./venv/bin/pytest tests/unit/test_bot_handlers/test_export_handlers.py::test_handle_export_command_retry_after_error -v
./venv/bin/pytest tests/unit/test_bot_handlers/test_export_handlers.py::test_handle_export_command_bad_request_error -v
./venv/bin/pytest tests/unit/test_bot_handlers/test_export_handlers.py::test_handle_export_command_network_error -v
./venv/bin/pytest tests/unit/test_bot_handlers/test_export_handlers.py::test_handle_export_command_telegram_error -v

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

## Airtable Schema Update Testing (2025-09-10)

### Demographic Fields Testing Summary
**Total Tests**: Comprehensive coverage for DateOfBirth and Age field integration
**Test Categories**: Field mapping validation, participant model testing, schema discovery verification, backward compatibility validation
**Pass Rate**: 100%  
**Coverage Areas**: Complete validation of new field integration with existing codebase

#### DateOfBirth and Age Field Testing
**Test Coverage**:
- **Field Mapping Tests**: Validation of real field IDs (DateOfBirth: fld1rN2cffxKuZh4i, Age: fldZPh65PIekEbgvs)
- **Participant Model Tests**: Serialization, deserialization, and validation of Optional[date] and Optional[int] fields
- **Conversion Tests**: Bidirectional conversion between Python objects and Airtable format
- **Backward Compatibility Tests**: Existing records without new fields process correctly with None values
- **Constraint Validation Tests**: Age field 0-120 range validation, DateOfBirth date format validation

**Key Test Scenarios**:
```python
# Field mapping validation
test_new_field_mappings_exist()
test_dateofbirth_field_id_format()
test_age_field_id_format()

# Participant model testing
test_participant_creation_with_new_fields()
test_participant_serialization_with_new_fields()
test_participant_deserialization_with_new_fields()
test_roundtrip_conversion_preserves_data()

# Validation testing
test_age_constraint_validation()
test_dateofbirth_format_validation()
test_optional_field_handling()

# Backward compatibility
test_existing_records_without_new_fields()
test_none_value_handling()
test_partial_field_updates()
```

#### Schema Discovery and Validation Testing
**Test Coverage**:
- **Schema Discovery Script**: Verification that scripts connect to live Airtable API
- **Field ID Discovery**: Validation that discovered field IDs match configured mappings
- **Production Validation**: Tests confirm field IDs exist in production Airtable base
- **Error Handling**: API connection failures and validation error scenarios

**Key Test Results**:
- **Real Field IDs Validated**: Both DateOfBirth and Age fields confirmed to exist in production
- **17-Character Format**: Field IDs follow proper Airtable format (fld + 14 characters)
- **Type Validation**: DateOfBirth is DATE type, Age is NUMBER type as expected
- **API Integration**: Successfully connects to live Airtable base using valid credentials

## Floor Search Callback Integration Testing (2025-01-21)

### Conversation Flow Integration Test Suite
**Test File**: `tests/integration/test_floor_search_integration.py` - Enhanced with callback integration
**Tests Added**: 7 new integration tests (367 lines) covering complete callback workflow
**Test Coverage**: Complete user journey from floor search to discovery to selection to results

#### Callback Integration Test Class (`TestFloorSearchCallbackIntegration`)
**Tests**: 7 comprehensive callback integration test cases (lines 490-775)
**Coverage**:
- Complete user journey: floor search → discovery button → floors list → floor selection → results
- Callback handler registration validation for `floor_discovery` and `floor_select_*` patterns in WAITING_FOR_FLOOR state
- Error recovery scenarios: API failure fallback, empty results handling, callback timeout scenarios
- Backward compatibility validation with traditional numeric floor input methods
- State transition validation with new callback handlers properly registered in conversation flow
- Comprehensive error scenario testing with proper callback acknowledgment and user guidance
- Performance validation ensuring callback response times within acceptable limits

**Key Test Scenarios**:
```python
# Complete callback workflow testing
test_floor_search_callback_integration_complete_flow()
test_floor_discovery_button_shows_available_floors()
test_floor_selection_button_triggers_search()
test_floor_discovery_api_error_fallback()
test_floor_discovery_empty_results_handling()
test_backward_compatibility_traditional_and_interactive_coexist()
test_callback_timeout_scenarios()
```

#### Integration Testing Achievements
**Implementation Status**: All acceptance criteria met for conversation integration
**Test Coverage**: 98% coverage achieved (118/120 lines) for floor search handlers
**Quality Assurance**: All 36 tests pass with zero linting/type errors
**Backward Compatibility**: Traditional numeric input continues working alongside interactive features
**Error Coverage**: 100% error scenario coverage including API failures, timeouts, empty results, and invalid callback data

#### Conversation Handler Validation
**Callback Registration Testing**: Tests verify proper registration of callback handlers in FloorSearchStates.WAITING_FOR_FLOOR state:
- `^floor_discovery$` pattern for discovery button
- `^floor_select_(\\d+)$` pattern for floor selection buttons
- Callback acknowledgment testing ensures `answer()` is called for all callback queries
- Message editing validation for seamless user experience updates

## Room and Floor Search Testing

### Test Coverage Summary (2025-09-05, Enhanced 2025-01-21)  
**Total Tests**: 138+ tests (Backend: 46, Frontend: 21, Integration: 64)
**Backend Tests**: Repository: 19, Service: 10, Validation: 14, Security: 2, Floor Discovery: 12
**Frontend Tests**: Room Handler: 9, Floor Handler: 9, Integration: 3
**Integration Tests**: 64 comprehensive end-to-end tests across 4 test files
**Pass Rate**: 100%  
**Coverage Areas**: Complete end-to-end testing from backend services to frontend conversation flows, comprehensive integration testing with Airtable schema validation, floor discovery backend with caching, conversation flow callback integration

#### Repository Testing (`test_airtable_participant_repo.py`)
**Tests**: 19 tests covering room, floor search, and floor discovery methods (lines 764-894, 966-1103)
**Coverage**:
- `find_by_room_number()` method with proper field mapping
- `find_by_floor()` method with Union[int, str] support
- **Floor Discovery Method** (New - 2025-01-20): `get_available_floors()` method with comprehensive testing:
  - 5-minute TTL caching with module-level persistence
  - 10-second API timeout with graceful fallback
  - API error handling returning empty list with logging
  - Cache expiry and cleanup validation
  - Optimized API calls fetching only floor field data
  - Cache key generation for multi-base support
  - Empty and None floor value filtering
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
**Tests**: 10 tests covering service layer room/floor methods and floor discovery (lines 583-684, 807-870)
**Coverage**:
- `search_by_room()` method with input validation
- `search_by_floor()` method with type conversion
- `search_by_room_formatted()` method with result formatting
- **Floor Discovery Service** (New - 2025-01-20): `get_available_floors()` method with error handling
- Async operation handling and error propagation
- Integration with validation utilities
- Repository delegation and error resilience testing

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

## Multi-Table Repository Implementation Testing (2025-01-21)

### Test Coverage Summary
**Total Tests**: 65 comprehensive tests with 100% pass rate
**Coverage Areas**: Complete Airtable repository implementations, field mapping helpers, integration testing
**Implementation Status**: Complete multi-table repository implementation with comprehensive CRUD operations

#### Data Model Testing
**BibleReader Model Testing** (`test_bible_readers.py`):
- **Tests**: 13 comprehensive unit tests
- **Coverage**: Field validation, API integration, lookup field handling, serialization
- **Key Scenarios**:
  ```python
  # Model validation testing
  test_bible_reader_creation_with_required_fields()
  test_bible_reader_creation_with_all_fields()
  test_bible_reader_validation_errors()

  # API integration testing
  test_from_airtable_record_conversion()
  test_to_airtable_fields_conversion()
  test_roundtrip_conversion_preserves_data()

  # Lookup field testing
  test_lookup_fields_excluded_from_airtable_fields()
  test_lookup_fields_populated_from_airtable_record()
  ```

**ROE Model Testing** (`test_roe.py`):
- **Tests**: 14 comprehensive unit tests
- **Coverage**: Presenter relationships, lookup fields, typo compatibility
- **Key Scenarios**:
  ```python
  # Model validation testing
  test_roe_creation_with_required_fields()
  test_roe_creation_with_all_fields()
  test_roe_validation_errors()

  # Presenter relationship testing
  test_roista_and_assistant_handling()
  test_multiple_presenters_per_role()

  # Lookup field testing
  test_seven_lookup_fields_excluded_from_writes()
  test_airtable_typo_compatibility()  # "AssistantChuch"
  ```

#### Repository Interface Testing
**Abstract Interface Validation** (`test_bible_readers_repository.py`, `test_roe_repository.py`):
- **Tests**: 9 tests validating interface compliance
- **Coverage**: Method signatures, async patterns, dependency injection support
- **Key Scenarios**:
  ```python
  # Interface compliance testing
  test_bible_readers_repository_interface_methods()
  test_roe_repository_interface_methods()
  test_abstract_method_signatures()
  test_async_pattern_consistency()
  ```

#### Client Factory Testing
**Multi-Table Client Creation** (`test_airtable_client_factory.py`):
- **Tests**: 6 comprehensive factory tests
- **Coverage**: Table-specific client creation, configuration integration, error handling
- **Key Scenarios**:
  ```python
  # Factory pattern testing
  test_create_participants_client()
  test_create_bible_readers_client()
  test_create_roe_client()
  test_invalid_table_type_handling()
  test_configuration_integration()
  test_dependency_injection_support()
  ```

#### Configuration Testing
**Multi-Table Settings Validation** (`test_multi_table_settings.py`):
- **Tests**: 7 configuration validation tests
- **Coverage**: Environment variables, table metadata, validation errors
- **Key Scenarios**:
  ```python
  # Configuration testing
  test_multi_table_environment_variables()
  test_table_configuration_defaults()
  test_get_table_config_method()
  test_to_airtable_config_with_table_types()
  test_configuration_validation_errors()
  ```

### Testing Methodology

#### Test-Driven Development Approach
- **Implementation**: All 64 tests written alongside feature implementation
- **Coverage Goals**: 100% code coverage achieved on new components
- **Edge Case Focus**: Comprehensive boundary condition and error scenario testing
- **Mock Strategy**: Repository interface mocking for isolated component testing

#### Data Model Testing Patterns
- **Field Validation**: Required field enforcement and optional field handling
- **API Integration**: Round-trip serialization between Python objects and Airtable format
- **Lookup Field Management**: Read-only lookup fields properly excluded from write operations
- **Type Safety**: Pydantic v2 validation with proper type conversion and error handling

#### Repository Interface Testing Patterns
- **Abstract Method Validation**: All repository interfaces follow consistent patterns
- **Async Pattern Enforcement**: Proper async/await usage across all repository methods
- **Dependency Injection**: Factory pattern enables proper service layer integration
- **CRUD Operation Coverage**: Complete Create, Read, Update, Delete method validation

#### Integration Readiness Validation
- **Factory Pattern Testing**: AirtableClientFactory properly creates table-specific clients
- **Configuration Integration**: Settings system supports multi-table environment variables
- **Error Handling**: Comprehensive error scenarios with graceful degradation
- **Backward Compatibility**: Existing Participants table functionality completely preserved

### Code Quality Assurance

#### Test Infrastructure Enhancements
- **Comprehensive Mocking**: Proper environment variable mocking for isolated testing
- **Configuration Testing**: Environment variable validation with defaults and error cases
- **Type Safety Validation**: All models and interfaces properly typed with mypy compliance
- **Documentation Integration**: Test scenarios align with implementation documentation

#### Performance and Scalability Considerations
- **Factory Pattern Efficiency**: Client creation optimized for reuse and dependency injection
- **Model Serialization**: Efficient Pydantic v2 serialization for API integration
- **Repository Interface Design**: Abstract interfaces enable future optimization and backend switching
- **Configuration Loading**: Startup-time validation prevents runtime configuration errors

### Future Testing Enhancements
- **Integration Testing**: End-to-end multi-table data flow testing
- **Performance Testing**: Load testing for multi-table operations
- **Export Service Testing**: CSV export functionality with multi-table data
- **UI Integration Testing**: Multi-table data display and management interfaces

## Handler Security Testing Implementation (Added 2025-09-25)

### Comprehensive Authorization Test Coverage
**Total Security Tests**: 35+ authorization tests across all handler modules
**Implementation Method**: Test-driven development with Red-Green-Refactor methodology
**Coverage Areas**: Complete handler security validation from entry points to data access

#### Handler-Specific Authorization Testing

**Search Handlers** (`test_search_handlers.py`):
- **Tests**: 11 comprehensive authorization tests
- **Coverage**: /start command security, search button authorization, main menu entry points
- **Methodology**: TDD approach with unauthorized/authorized access validation
- **Integration**: Updated existing tests with authorization mocks for compatibility

**Room Search Handlers** (`test_room_search_handlers.py`):
- **Tests**: 4 authorization tests covering all entry points
- **Coverage**: /search_room command, room number processing, direct room search
- **Security**: @require_viewer_or_above decorator validation on all 3 handlers
- **Error Handling**: Russian denial messages for unauthorized access

**Floor Search Handlers** (`test_floor_search_handlers.py`):
- **Tests**: Authorization validation for core floor search entry points
- **Coverage**: /search_floor command and floor number processing
- **Security**: @require_viewer_or_above decorator implementation
- **Integration**: Compatible with existing floor search test infrastructure

**List Handlers** (`test_list_handlers.py`):
- **Tests**: 8 comprehensive authorization tests (4 unauthorized + 4 authorized)
- **Coverage**: List generation, role selection, navigation, department filtering
- **Security**: @require_viewer_or_above decorator on all 4 list handlers
- **Pattern**: TDD Red-Green-Refactor approach with comprehensive test scenarios

**Edit Participant Handlers** (`test_edit_participant_handlers.py`):
- **Tests**: Complete authorization test suite for all 10 editing operations
- **Coverage**: Participant editing menu, field selection, text input, button selection
- **Security**: @require_coordinator_or_above decorator (higher privilege requirement)
- **Critical**: Ensures only coordinators/admins can modify participant data

**Admin Handlers** (`test_admin_handlers.py`):
- **Tests**: 5 comprehensive tests for /auth_refresh command
- **Coverage**: Admin-only access validation, cache invalidation functionality
- **Security**: @require_admin decorator with highest privilege requirement
- **Integration**: Real-time role updates without bot restart capability

#### Security Testing Methodology

**Test Pattern Implementation**:
```python
class TestHandlerAuthorization:
    def test_handler_unauthorized_access(self, mock_update, mock_context):
        # Mock unauthorized user
        # Attempt handler access
        # Assert denial message and blocked access

    def test_handler_authorized_access(self, mock_update, mock_context):
        # Mock authorized user with appropriate role
        # Execute handler logic
        # Assert successful processing
```

**Security Validation Features**:
- **Zero Bypass**: No unauthorized access paths remain in any handler
- **Role Hierarchy**: Proper enforcement of viewer → coordinator → admin levels
- **Consistent Messaging**: Standardized Russian denial messages across handlers
- **Integration Compatibility**: Updated existing tests to work with authorization system

## Testing Roadmap

### Current Status
- [x] ✅ **Handler Security Implementation Testing (2025-09-25)**: 35+ authorization tests across all handler modules with TDD methodology, zero unauthorized access paths, complete role hierarchy enforcement, and integration compatibility
- [x] ✅ Comprehensive unit testing (29 unit tests with regression coverage, 100% pass)
- [x] ✅ Handler conversation flow testing with save/cancel workflow
- [x] ✅ Service layer validation testing
- [x] ✅ Keyboard generation testing
- [x] ✅ Repository integration testing (8 update_by_id tests)
- [x] ✅ End-to-end integration testing (4 workflow tests)
- [x] ✅ **Multi-Table Data Foundation Testing (2025-01-21)**: 64 comprehensive tests with 100% pass rate covering data models, repository interfaces, and client factory patterns
- [x] ✅ **CSV Export Service Testing (2025-01-15)**: 30 comprehensive tests with 91% service coverage and 100% auth coverage
- [x] ✅ **Admin Authentication Testing**: Complete validation of user authorization with type safety and edge case coverage
- [x] ✅ **File Management Testing**: Secure temporary file creation, cleanup, and size estimation validation
- [x] ✅ **Progress Tracking Testing**: CSV generation with callback functionality and large dataset support
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
- [x] ✅ **Comprehensive integration testing for room and floor search (28 tests across 3 files)**
- [x] ✅ **Airtable schema validation and field mapping verification**
- [x] ✅ **Standardized error message implementation with centralized templates**
- [x] ✅ **Performance validation ensuring <3 second response times**
- [x] ✅ **End-to-end workflow testing with real Airtable field integration**
- [x] ✅ **Alphanumeric room number support and multi-room floor grouping**
- [x] ✅ **Main Menu Start Command Equivalence Testing (2025-09-09)**: Comprehensive test coverage for shared initialization helpers, start/main menu button equivalence, timeout recovery entry points, and cancel handler consistency
- [x] ✅ **Airtable Schema Update Testing (2025-09-10)**: Comprehensive test coverage for DateOfBirth and Age field integration including field mapping validation, participant model conversion testing, backward compatibility validation, and schema discovery script verification
- [x] ✅ **Floor Search Callback Integration Testing (2025-01-21)**: Comprehensive test coverage for conversation flow integration with floor discovery callbacks, complete user journey validation, error recovery scenarios, callback timeout handling, and backward compatibility with traditional floor input
- [x] ✅ **Department Filtering Repository and Service Testing (2025-01-21)**: Comprehensive test coverage for repository layer department filtering with chief-first ordering, service layer integration with backward compatibility, chief indicator formatting with crown emoji, and AsyncMock integration test fixes resolving all test failures
- [x] ✅ **Multi-Table Model Testing (2025-01-21)**: 27 comprehensive tests (13 BibleReader + 14 ROE) covering Pydantic model validation, API integration, field serialization, and lookup field handling
- [x] ✅ **Repository Interface Testing (2025-01-21)**: 9 tests validating abstract repository interfaces for BibleReaders and ROE with consistent method signatures and async patterns
- [x] ✅ **Client Factory Testing (2025-01-21)**: 6 tests covering multi-table client creation, configuration integration, and dependency injection patterns
- [x] ✅ **Multi-Table Configuration Testing (2025-01-21)**: 7 tests validating environment variable configuration, table metadata exposure, and factory integration
- [x] ✅ **Multi-Table Repository Implementation Testing (2025-01-21)**: 65 comprehensive tests covering complete Airtable repository implementations for BibleReaders and ROE tables
  - **BibleReaders Repository Testing**: 25 unit tests with 80% coverage for all CRUD operations
  - **ROE Repository Testing**: Comprehensive testing with presenter relationship validation
  - **Field Mapping Helpers Testing**: 36 tests with 100% coverage for BibleReaders and ROE field mapping utilities
  - **Integration Testing**: 4 tests validating multi-table coordination and client isolation
- [x] ✅ **Airtable Repository Pattern Consistency**: All new repositories follow existing AirtableParticipantRepo patterns for error handling and API integration
- [ ] ⏳ Performance benchmarking
- [ ] ⏳ Load testing for concurrent users

### Future Enhancements
- **Property-Based Testing**: Hypothesis integration for edge case discovery
- **Contract Testing**: API contract validation with Airtable
- **Visual Testing**: UI screenshot comparison for Telegram interfaces
- **Chaos Engineering**: Fault injection and recovery testing
- **Cross-Table Relationship Testing**: Validation of participant linking across multiple tables
- **Performance Testing**: Multi-table query optimization and response time validation
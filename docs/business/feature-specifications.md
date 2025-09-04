# Feature Specifications

## Participant Editing Interface

### Overview
Comprehensive participant profile editing interface accessible through search results. Supports all 13 participant fields with appropriate input methods and validation.

**Status**: ✅ Implemented (2025-09-01)
**Implementation**: 4-state ConversationHandler with Russian localization
**Test Coverage**: 34 unit tests (100% pass rate)

### Core Features

#### 1. Participant Selection Interface
- **Access**: Click "Подробнее" (Details) button on any search result
- **Display**: Complete participant profile with all field values
- **Layout**: 13 individual "Изменить [Field]" edit buttons
- **Actions**: Save Changes, Cancel, Back to Search
- **Enhanced Display**: After field updates, shows complete participant information with updated values

#### 2. Field-Specific Editing Methods

**Button-Based Fields (5 fields)**
- Immediate selection through inline keyboards
- No text input required
- Shows complete participant display after update

Fields:
- **Gender (Пол)**: Мужской/Женский (2 options)
- **Size (Размер)**: XS, S, M, L, XL, XXL, 3XL (7 options) 
- **Role (Роль)**: Кандидат/Команда (2 options)
- **Department (Департамент)**: 13 department options
- **Payment Status (Статус платежа)**: Оплачено/Частично/Не оплачено (3 options)

**Text Input Fields (6 fields)**
- Prompted text input workflow
- Russian prompts and validation messages
- Optional/required field validation
- Shows complete participant display after update

Fields:
- **Full Name Russian (Имя русское)**: Required, min length 1
- **Full Name English (Имя английское)**: Optional
- **Church (Церковь)**: Optional
- **Location (Местоположение)**: Optional
- **Contact (Контакты)**: Optional 
- **Submitted By (Кто подал)**: Optional

**Special Validation Fields (2 fields)**
- Custom validation logic
- Format-specific error messages  
- Shows complete participant display after update

Fields:
- **Payment Amount (Сумма платежа)**: Integer ≥ 0
- **Payment Date (Дата платежа)**: YYYY-MM-DD format

#### 3. Conversation Flow Management

**State Machine**: 4-state ConversationHandler
1. **FIELD_SELECTION**: Display participant profile with edit buttons
2. **TEXT_INPUT**: Handle text input for free text fields
3. **BUTTON_SELECTION**: Handle inline keyboard selections
4. **CONFIRMATION**: Save/cancel workflow

**State Transitions**:
- Field Selection → Text Input (for text fields)
- Field Selection → Button Selection (for predefined fields) 
- Text/Button Input → Field Selection (after update)
- Field Selection → Confirmation (save/cancel)

#### 4. Russian Localization

**User Interface Elements**:
- All button labels in Russian
- Field names translated (e.g., "Изменить пол", "Изменить размер")
- Navigation buttons ("Назад", "Далее", "Отмена")

**User Prompts**:
- Input prompts in Russian (e.g., "Отправьте новое имя на русском")
- Validation error messages in Russian
- Success/confirmation messages in Russian

**Field Values**:
- Enum values displayed in Russian (Мужской/Женский, Оплачено/Частично)
- Department names localized where applicable

#### 5. Enhanced User Experience

**Complete Participant Context Display**
- **Post-Edit Display**: After each successful field update, users see the complete participant profile with all current information
- **Save Success Enhancement**: Save operations display complete updated participant information using format_participant_result() instead of simple confirmation messages
- **Consistency**: Uses the same rich formatting as initial search results for visual consistency
- **Context Preservation**: Users maintain full context of participant data without needing to navigate back
- **Edit Workflow Continuity**: All edit buttons remain available for continued editing after display updates
- **Error Resilience**: Enhanced error handling prevents silent display failures with comprehensive logging and graceful degradation

**Implementation Details**:
- Leverages `display_updated_participant()` helper function with comprehensive error handling
- Reconstructs participant object with all current session changes
- Uses `format_participant_result()` for consistent formatting in both field edits and save success
- Maintains conversation state and editing context
- **REGRESSION markers** in logs for production debugging and monitoring
- Graceful degradation when participant context is lost with meaningful user feedback

#### 6. Data Validation & Error Handling

**Field-Specific Validation**:
- Required field enforcement (Russian name)
- Format validation (date: YYYY-MM-DD, amount: integer)
- Enum value conversion (Gender, Size, Role, etc.)

**Error Messages**:
- Russian error messages for all validation failures
- Clear instruction on correct input format
- Retry prompts after validation errors

**System Error Handling**:
- Airtable API error recovery
- Rate limiting protection
- Graceful conversation state cleanup

### Technical Architecture

#### Implementation Components
1. **Handler**: `src/bot/handlers/edit_participant_handlers.py` (501 lines)
2. **Keyboards**: `src/bot/keyboards/edit_keyboards.py` (160 lines)
3. **Service**: `src/services/participant_update_service.py` (151 lines)
4. **Repository**: Extended `airtable_participant_repo.py` with `update_by_id`

#### Integration Points
- Extends existing search conversation handler
- Integrates with Airtable repository pattern
- Uses participant update service for validation
- Maintains conversation context across state transitions

### Acceptance Criteria

- [x] ✅ All 13 participant fields accessible through editing interface
- [x] ✅ Button-based fields show correct options with Russian labels
- [x] ✅ Text fields accept and validate input with Russian prompts
- [x] ✅ State management maintains editing context properly
- [x] ✅ Field validation prevents invalid data with clear error messages
- [x] ✅ **Save confirmation workflow** with change preview and explicit user confirmation
- [x] ✅ **Cancel workflow** discards changes and returns to main menu cleanly
- [x] ✅ **Error handling with retry** preserves user changes during failed save operations
- [x] ✅ **Enhanced post-edit display** shows complete participant information after each field update
- [x] ✅ **Save success enhancement** displays complete participant information instead of simple confirmation
- [x] ✅ **Display regression prevention** with comprehensive error handling and graceful degradation
- [x] ✅ **Error resilience** prevents silent display failures with detailed logging and user guidance
- [x] ✅ **Display consistency** matches initial search result formatting for seamless user experience
- [x] ✅ Complete test coverage (41 tests total including 11 regression tests, 100% pass rate)
- [x] ✅ Russian localization across all UI elements including error messages
- [x] ✅ Integration with existing search functionality and conversation flows

### Future Enhancements

**Potential Improvements**:
- Bulk edit functionality for multiple participants
- Field history/audit trail
- Advanced validation rules (e.g., phone number format)
- Export functionality for edited data
- Role-based edit permissions

**Integration Opportunities**:
- Integration with participant import/export
- Reporting dashboard for field changes
- Notification system for significant updates

## Room and Floor Search Functionality

### Overview
Location-based participant search functionality enabling users to find participants by room number or floor assignment. Provides the backend data layer foundation for future UI implementation.

**Status**: ✓ Backend Implementation Complete (2025-09-04)
**Implementation**: Repository and service layer methods with comprehensive validation
**Test Coverage**: 34 tests (100% pass rate)

### Core Features

#### 1. Room-Based Search
- **Purpose**: Find all participants assigned to a specific room
- **Input**: Room number (alphanumeric: "101", "A1", "Conference")
- **Validation**: Non-empty string validation with whitespace trimming
- **Output**: List of participants filtered by room assignment

**Technical Implementation**:
```python
# Repository method
async def find_by_room_number(self, room: str) -> List[Participant]:
    # Filters by Airtable RoomNumber field (fldJTPjo8AHQaADVu)
    
# Service method  
async def search_by_room(self, room: str) -> List[Participant]:
    # Includes input validation and error handling
```

#### 2. Floor-Based Search
- **Purpose**: Find all participants on a specific floor, optionally grouped by room
- **Input**: Floor number or name (Union[int, str]: 1, "2", "Ground")
- **Validation**: Accepts both numeric and string floor identifiers
- **Output**: List of participants filtered by floor assignment

**Technical Implementation**:
```python
# Repository method
async def find_by_floor(self, floor: Union[int, str]) -> List[Participant]:
    # Filters by Airtable Floor field (fldlzG1sVg01hsy2g)
    
# Service method
async def search_by_floor(self, floor: Union[int, str]) -> List[Participant]:
    # Includes type conversion and validation

# Formatted service method  
async def search_by_room_formatted(self, room: str) -> str:
    # Returns formatted string results for UI consumption
```

#### 3. Input Validation
- **Room Validation**: Non-empty string requirement with whitespace handling
- **Floor Validation**: Union[int, str] support with type conversion
- **Security**: Formula injection prevention with proper quote escaping
- **Error Handling**: Comprehensive validation result objects with error messages

**Validation Utilities**:
```python
# src/utils/validation.py - NEW FILE
class ValidationResult:
    is_valid: bool
    cleaned_value: Optional[Any] = None
    error_message: Optional[str] = None

def validate_room_number(room: str) -> ValidationResult
def validate_floor(floor: Union[int, str]) -> ValidationResult
```

### Field Mapping Integration

#### Airtable Schema Alignment
- **RoomNumber Field**: `fldJTPjo8AHQaADVu` (Single line text)
- **Floor Field**: `fldlzG1sVg01hsy2g` (Number or single line text)
- **Model Fields**: `room_number: Optional[str]`, `floor: Optional[Union[int, str]]`
- **API Names**: "RoomNumber", "Floor" (for Airtable API calls)

### Security Enhancements

#### Formula Injection Prevention
- **Problem**: User input like "O'Connor" could break Airtable formulas
- **Solution**: Proper single quote escaping by doubling (`'` → `''`)
- **Implementation**: Enhanced `search_by_field` method in AirtableClient
- **Testing**: Comprehensive formula escaping validation tests

### Error Handling Strategy

#### Validation Errors
- Empty room/floor input validation
- Type conversion errors for floor numbers
- Invalid character handling

#### Data Access Errors
- Airtable API connectivity issues
- Rate limiting protection (5 requests/second)
- Network timeout recovery
- Empty result set handling

#### Security Errors
- Formula injection attempt detection
- Malformed input sanitization
- SQL-injection-style attack prevention

### Technical Architecture

#### Repository Layer Extensions
- **File**: `src/data/airtable/airtable_participant_repo.py`
- **Methods**: `find_by_room_number()`, `find_by_floor()` (lines 983-1055)
- **Features**: Async/await support, comprehensive error handling, participant conversion

#### Service Layer Extensions
- **File**: `src/services/search_service.py`
- **Methods**: `search_by_room()`, `search_by_floor()`, `search_by_room_formatted()` (lines 435-503)
- **Features**: Input validation, error handling, result formatting

#### Validation Utilities
- **File**: `src/utils/validation.py` (NEW FILE)
- **Components**: ValidationResult dataclass, room/floor validation functions
- **Features**: Comprehensive edge case handling, type safety

### Test Coverage

#### Repository Tests
- **File**: `tests/unit/test_data/test_airtable/test_airtable_participant_repo.py`
- **Tests**: 12 tests covering room/floor search methods (lines 764-894)
- **Coverage**: Success cases, empty results, error handling, field mapping

#### Service Tests
- **File**: `tests/unit/test_services/test_search_service.py`
- **Tests**: 6 tests covering service layer methods (lines 583-684)
- **Coverage**: Validation, async operations, error propagation

#### Validation Tests
- **File**: `tests/unit/test_utils/test_validation.py` (NEW FILE)
- **Tests**: 14 comprehensive validation tests
- **Coverage**: Edge cases, type conversion, error messages, boundary conditions

#### Security Tests
- **File**: `tests/unit/test_data/test_airtable/test_airtable_client.py`
- **Tests**: 2 formula escaping tests (lines 731-750)
- **Coverage**: Quote injection prevention, special character handling

### Integration Points

#### Future UI Integration
- **Ready**: Backend methods ready for bot handler integration
- **Search Commands**: Can extend existing `/search` command with room/floor syntax
- **Result Display**: Formatted service methods provide UI-ready output
- **Error Handling**: Comprehensive error objects support user-friendly messages

#### Existing System Integration
- **Search Service**: Extends existing SearchService without breaking changes
- **Repository Pattern**: Follows established repository interface pattern
- **Model Compatibility**: Works with existing Participant model structure
- **Test Integration**: Uses existing test infrastructure and patterns

### Acceptance Criteria

- [✓] ✅ Repository methods filter participants by room/floor using correct Airtable fields
- [✓] ✅ Service layer provides validation and formatting for room/floor searches
- [✓] ✅ Input validation handles numeric and alphanumeric room numbers
- [✓] ✅ Floor search supports both integer and string inputs
- [✓] ✅ Security enhancements prevent formula injection attacks
- [✓] ✅ Comprehensive error handling for all edge cases
- [✓] ✅ Test coverage exceeds 95% with 34 passing tests
- [✓] ✅ No regressions in existing search functionality
- [✓] ✅ Proper field mapping alignment with Airtable schema
- [✓] ✅ Code quality meets project standards (linting, type checking)

### Future Development

#### UI Implementation (Next Phase)
- Bot handlers for room/floor search commands
- Interactive keyboard interfaces for floor/room selection
- Paginated results display for large result sets
- Integration with existing search conversation flow

#### Enhanced Features
- Room occupancy reporting
- Floor-based bulk operations
- Room assignment validation
- Capacity management integration

## Save/Cancel Workflow with Airtable Integration

### Overview
Complete save/cancel workflow system with change confirmation, error handling, and Airtable integration for the participant editing feature.

**Status**: ✅ Implemented (2025-09-01)
**Implementation**: Enhanced edit_participant_handlers.py with confirmation screens and retry logic
**Test Coverage**: 34 tests total (22 unit + 8 repository + 4 integration tests) - 100% pass rate

### Core Features

#### 1. Save Confirmation Screen
- **Change Preview**: Shows all pending changes in "Current Value → **New Value**" format
- **Explicit Confirmation**: Requires user confirmation before committing to Airtable
- **Change Summary**: Groups all field modifications in a single confirmation view
- **Actions**: "Подтвердить сохранение" (Confirm) or "Отмена" (Cancel)

#### 2. Cancel Workflow
- **Change Discard**: Cancel discards all pending changes without saving
- **Clean State**: Returns user to main menu with clean conversation state
- **Confirmation**: "Вернуться в главное меню" confirmation option
- **Context Reset**: Clears editing context to prevent state conflicts

#### 3. Error Handling and Retry
- **Automatic Retry**: Failed save operations show "Попробовать снова" (Try Again) button
- **Change Preservation**: User changes preserved during retry attempts
- **Error Details**: Clear Russian error messages explaining failure reasons
- **Recovery Path**: Multiple retry attempts allowed until success or user cancellation

#### 4. Airtable Integration
- **Atomic Updates**: All changes committed in single Airtable update operation
- **Rate Limiting**: Respects Airtable API rate limits (5 requests/second)
- **Field Mapping**: Proper translation between internal models and Airtable schema
- **Error Classification**: Network, validation, and API errors handled appropriately

### Technical Implementation

#### Save Confirmation Flow
- **Function**: `show_save_confirmation()` (lines 506-591)
- **Change Tracking**: Modified fields tracked in conversation context
- **Confirmation Display**: Russian field names with before/after values
- **User Actions**: Confirmation or cancellation buttons

#### Retry Mechanism
- **Function**: `retry_save()` (lines 594-614)
- **Error Classification**: Distinguishes between different failure types
- **User Feedback**: Specific error messages for network vs validation issues
- **State Recovery**: Maintains editing context through retry cycles

#### Integration Testing
- **Test Suite**: `tests/integration/test_search_to_edit_flow.py` (314 lines)
- **Coverage**: Complete user journeys from search through edit to save
- **Scenarios**: Success, cancel, retry, and validation workflows
- **Quality Assurance**: All 4 integration tests passing

### Acceptance Criteria

- [x] ✅ Save confirmation displays all pending changes clearly
- [x] ✅ Cancel workflow discards changes and returns to main menu
- [x] ✅ Error recovery allows retry without data loss
- [x] ✅ Airtable integration handles all error scenarios gracefully
- [x] ✅ Complete conversation flow integration without state conflicts
- [x] ✅ Russian localization for all user-facing messages
- [x] ✅ Comprehensive test coverage (100% pass rate)

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
Complete location-based participant search functionality enabling users to find participants by room number or floor assignment. Includes both backend data layer and full frontend user interface implementation with enhanced Russian language support.

**Status**: ✅ Enhanced Implementation (2025-01-09)
**Implementation**: Backend services + Frontend handlers with structured Russian UI and translation utilities
**Test Coverage**: Enhanced test suite with comprehensive translation and formatting coverage

### Core Features

#### 1. Room-Based Search with Enhanced Russian Results
- **Purpose**: Find all participants assigned to a specific room with structured Russian formatting
- **Input**: Room number (alphanumeric: "101", "A1", "Conference")
- **Validation**: Non-empty string validation with whitespace trimming
- **Output**: Structured Russian results showing participant names, roles, departments, and floor information

**Enhanced Features (2025-01-09)**:
- **Structured Display**: Russian-formatted results with role and department translations
- **Comprehensive Information**: Shows participant names (Russian/English), role, department, and floor
- **Translation Support**: Complete Russian translations for all departments and roles
- **Conversation Flow**: Proper state management with Russian prompts and error messages

**Technical Implementation**:
```python
# Repository method
async def find_by_room_number(self, room: str) -> List[Participant]:
    # Filters by Airtable RoomNumber field (fldJTPjo8AHQaADVu)
    
# Service method  
async def search_by_room(self, room: str) -> List[Participant]:
    # Includes input validation and error handling

# Enhanced formatting method (NEW)
def format_room_results_russian(participants: List[Participant], room: str) -> str:
    # Formats results with Russian labels, role/department translations, and floor info
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

#### Frontend Implementation (Completed 2025-09-04)
- **Command Handlers**: `/search_room` and `/search_floor` commands fully implemented
- **Conversation Flow**: Complete ConversationHandler integration with state management
- **Russian Interface**: Full Russian language support with localized messages and keyboards
- **Search Mode Selection**: Reply keyboard navigation between name/room/floor search modes
- **Result Formatting**: Room-by-room breakdown for floor searches, formatted participant lists for room searches
- **Input Validation**: User-friendly Russian error messages for invalid room/floor inputs
- **Mobile Optimization**: Reply keyboards designed for mobile device constraints

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

### Technical Implementation Details

#### Frontend Components (2025-09-04)
- **Files Created**: 
  - `src/bot/handlers/room_search_handlers.py` (204 lines) - Room search conversation flow
  - `src/bot/handlers/floor_search_handlers.py` (247 lines) - Floor search with room grouping
  - `src/bot/keyboards/search_keyboards.py` (73 lines) - Search mode selection keyboards
  - `src/services/service_factory.py` (35 lines) - Centralized dependency injection
- **Files Enhanced**:
  - `src/bot/handlers/search_conversation.py` (+42 lines) - ConversationHandler integration
  - `src/bot/handlers/search_handlers.py` (+108 lines) - Search mode selection handlers

#### Conversation States
- **RoomSearchStates**: AWAITING_ROOM_INPUT (room number entry)
- **FloorSearchStates**: AWAITING_FLOOR_INPUT (floor number entry)  
- **SearchStates**: MODE_SELECTION (search type selection)
- **State Management**: Non-overlapping enum values prevent handler conflicts

#### User Experience Features
- **Room Search Results**: Formatted participant list with roles and departments
- **Floor Search Results**: Room-by-room breakdown with participant counts and names
- **Navigation Flow**: Seamless switching between search modes via reply keyboards
- **Error Handling**: Comprehensive input validation with retry mechanisms
- **Empty Results**: User-friendly messages for empty rooms/floors

### Future Enhancements
- **Paginated Results**: For large result sets (>10 participants)
- **Export Functionality**: CSV export of room/floor participant lists
- **Room Occupancy Analytics**: Capacity utilization reporting
- **Bulk Operations**: Floor-based bulk participant actions
- **Room Assignment Validation**: Prevent overbooking and conflicts

## Conversation Timeout Handler

### Overview
Automatic conversation timeout handling to prevent users from getting stuck in stale conversation states. Provides graceful session termination with clear recovery options.

**Status**: ✅ Implemented (2025-01-09)
**Implementation**: Integrated timeout handler across all ConversationHandler states
**Test Coverage**: 18 comprehensive tests (100% pass rate)

### Core Features

#### 1. Automatic Session Timeout
- **Timeout Period**: Configurable via `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES` environment variable
- **Default Value**: 30 minutes of inactivity
- **Valid Range**: 1-1440 minutes (1 minute to 24 hours)
- **Coverage**: Applied to all conversation states (search, edit, room/floor search)
- **Behavior**: Automatic conversation termination after inactivity period

#### 2. Russian User Interface
- **Timeout Message**: "Сессия истекла, начните заново" (Session expired, start again)
- **Recovery Button**: "Вернуться в главное меню" (Return to main menu)
- **User Experience**: Clear communication and easy recovery path
- **Consistency**: Follows existing Russian localization patterns

#### 3. Graceful State Cleanup
- **Memory Management**: Prevents conversation state leaks and memory buildup
- **Context Cleanup**: Properly clears conversation context data on timeout
- **State Transition**: Clean transition to ConversationHandler.END state
- **Error Prevention**: Eliminates stale conversation state issues

#### 4. Universal Integration
- **ConversationHandler Integration**: Applied to all conversation handlers
- **State Coverage**: Timeout handler registered for all conversation states
- **Consistent Behavior**: Uniform timeout handling across search, edit, and location-based conversations
- **Configuration Loading**: Dynamic timeout configuration from settings

### Technical Implementation

#### Timeout Handler Function
- **File**: `src/bot/handlers/timeout_handlers.py`
- **Function**: `handle_conversation_timeout()`
- **Features**: Russian message display, main menu keyboard, error handling
- **Error Recovery**: Try/catch around message sending with graceful conversation termination

#### ConversationHandler Integration
- **Configuration**: `conversation_timeout` parameter with minutes-to-seconds conversion
- **Handler Registration**: `ConversationHandler.TIMEOUT` state mapped to timeout handler
- **Settings Integration**: Dynamic configuration loading via `get_telegram_settings()`
- **Universal Application**: Applied to all conversation handlers in the system

#### Configuration Management
- **Environment Variable**: `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES`
- **Validation**: Range validation (1-1440 minutes) with descriptive error messages
- **Default Value**: 30 minutes for optimal user experience
- **Settings Integration**: Integrated into TelegramSettings dataclass

### Acceptance Criteria

- [x] ✅ Configurable timeout period via environment variable with validation
- [x] ✅ Russian timeout message displayed to users ("Сессия истекла, начните заново")
- [x] ✅ Main menu recovery button provides clear recovery path
- [x] ✅ All conversation states include consistent timeout handling
- [x] ✅ Graceful state cleanup prevents memory leaks and stale data
- [x] ✅ Universal integration across search, edit, and location-based conversations
- [x] ✅ Error handling ensures conversation termination even if message sending fails
- [x] ✅ Comprehensive test coverage with 18 passing tests
- [x] ✅ Integration tests validate end-to-end timeout behavior
- [x] ✅ Configuration validation and settings integration

### User Experience Impact

#### Before Implementation
- Users could get stuck in conversation states without clear recovery
- Stale conversation context could cause unexpected behavior
- No automatic cleanup of inactive sessions
- Support requests for "bot not responding" situations

#### After Implementation
- Automatic session cleanup after configurable inactivity period
- Clear Russian instructions for session recovery
- One-click return to main menu functionality
- Elimination of stale conversation state issues
- Improved bot responsiveness and user satisfaction

### Future Enhancements

**Potential Improvements**:
- Per-conversation-type timeout configuration
- Warning messages before timeout (e.g., "Session expires in 5 minutes")
- Session extension functionality for active users
- Timeout analytics and user behavior insights
- Configurable timeout messages per conversation type

**Integration Opportunities**:
- User activity tracking and analytics
- Timeout-based user engagement metrics
- Integration with notification system for timeout warnings
- Custom timeout periods based on user preferences

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

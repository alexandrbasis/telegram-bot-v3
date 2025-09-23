# Field Mappings

## Airtable Field Mappings

### Room and Floor Search Fields (Added 2025-09-04)
The following field mappings enable room and floor-based participant search functionality:

```python
# Field mappings for location-based search and demographic data
FIELD_MAPPINGS = {
    # Room/Floor search fields
    "room_number": "fldJTPjo8AHQaADVu",  # RoomNumber field in Airtable
    "floor": "fldlzG1sVg01hsy2g",        # Floor field in Airtable
    
    # Demographic data fields (Added 2025-09-10)
    "date_of_birth": "fld1rN2cffxKuZh4i",  # DateOfBirth field in Airtable
    "age": "fldZPh65PIekEbgvs",           # Age field in Airtable

    # Extended participant fields (Added 2025-01-14)
    "church_leader": "fldbQr0R6nEtg1nXM",   # ChurchLeader field in Airtable
    "table_name": "fldwIopXniSHk94v9",     # TableName field in Airtable
    "notes": "fldL4wmlV9de1kKa1",         # Notes field in Airtable

    # Leadership identification fields (Added 2025-01-19)
    "is_department_chief": "fldWAay3tQiXN9888",  # IsDepartmentChief field in Airtable
    
    # Other participant fields
    "full_name_ru": "fld...",
    "full_name_en": "fld...",
    # ... other field mappings
}
```

### Critical Bug Fixes (2025-09-11)

#### Date of Birth and Age Field Issues Resolution
Resolved critical bugs affecting participant editing interface:

**Issue**: Date of birth and age fields not displaying correctly in edit interface and causing JSON serialization errors during save operations.

**Root Causes**:
1. Participant reconstruction missing `date_of_birth` and `age` fields in `display_updated_participant()` function
2. Airtable repository missing date serialization for `date_of_birth` field (only had `payment_date`)
3. Missing UI labels and formatting in edit menu and confirmation screens

**Solutions Implemented**:
- **Participant Reconstruction**: Added date_of_birth and age to all participant display functions
- **Date Serialization**: Extended `_convert_field_updates_to_airtable()` to serialize date_of_birth to ISO format
- **UI Enhancement**: Added proper Russian labels (🎂 Дата рождения, 🔢 Возраст) in edit menu and confirmation
- **Clearing Support**: Implemented robust clearing behavior for both fields via whitespace detection
- **Error Messaging**: Enhanced validation with InfoMessages for consistent user guidance

**Files Modified**:
- `src/bot/handlers/edit_participant_handlers.py`: Added field reconstruction and UI labels
- `src/data/airtable/airtable_participant_repo.py`: Extended date serialization
- `src/services/participant_update_service.py`: Added clearing behavior and enhanced error messaging

### Extended Participant Fields (Added 2025-01-14)

#### ChurchLeader Field (fldbQr0R6nEtg1nXM)
- **Internal Model**: `church_leader: Optional[str]`
- **Airtable Field**: "ChurchLeader"
- **Data Type**: Single line text
- **Validation**: Optional text field, accepts any string input
- **Usage**: Track which church leader is associated with each participant
- **UI Integration**: Full edit menu support with Russian labels ("⛪ Церковный лидер")

#### TableName Field (fldwIopXniSHk94v9)
- **Internal Model**: `table_name: Optional[str]`
- **Airtable Field**: "TableName"
- **Data Type**: Single line text
- **Validation**: Optional text field with role-based business rules
- **Role Restriction**: Only available for participants with role="CANDIDATE"
- **Usage**: Manage event seating arrangements and table assignments
- **UI Integration**: Role-based visibility in edit interface ("🍽️ Название стола")
- **Business Logic**: Field blocked for TEAM role participants with validation error

#### Notes Field (fldL4wmlV9de1kKa1)
- **Internal Model**: `notes: Optional[str]`
- **Airtable Field**: "Notes"
- **Data Type**: Long text (multiline support)
- **Validation**: Optional multiline text field
- **Usage**: Capture special requirements, administrative information, or extended notes
- **UI Integration**: Multiline text input support with Russian labels ("📝 Заметки")
- **Display Features**: Markdown-safe text escaping and truncation in search results
- **Special Handling**: Supports line breaks and preserves multiline formatting

### Field Usage Guidelines

#### RoomNumber Field (fldJTPjo8AHQaADVu)
- **Internal Model**: `room_number: Optional[str]`
- **Airtable Field**: "RoomNumber"
- **Data Type**: Single line text
- **Validation**: Accepts alphanumeric room identifiers ("101", "A1", "Conference")
- **Search Usage**: `find_by_room_number(room: str)` method in repository

#### Floor Field (fldlzG1sVg01hsy2g)
- **Internal Model**: `floor: Optional[Union[int, str]]`
- **Airtable Field**: "Floor"
- **Data Type**: Number or single line text
- **Validation**: Accepts numeric floors (1, 2, 3) or named floors ("Ground", "Basement")
- **Search Usage**: `find_by_floor(floor: Union[int, str])` method in repository
- **Floor Discovery Usage** (New - 2025-01-20): `get_available_floors()` method for backend floor discovery with caching

#### DateOfBirth Field (fld1rN2cffxKuZh4i) - Updated 2025-09-11
- **Internal Model**: `date_of_birth: Optional[date]`
- **Airtable Field**: "DateOfBirth"
- **Data Type**: Date
- **Validation**: ISO date format (YYYY-MM-DD), Python date object
- **Constraints**: Valid date values, application-side validation
- **Conversion**: to_airtable_fields() serializes as ISO string, from_airtable_record() deserializes to date object
- **Clearing Behavior**: Whitespace-only input clears field (sets to None)
- **UI Integration**: Full edit menu and confirmation screen support with Russian labels
- **Serialization Fix**: Proper date serialization for Airtable API (resolves JSON serialization errors)

#### Age Field (fldZPh65PIekEbgvs) - Updated 2025-09-11
- **Internal Model**: `age: Optional[int]`
- **Airtable Field**: "Age"
- **Data Type**: Number
- **Validation**: Integer values with application-side constraints (0-120 range)
- **Constraints**: Minimum 0, Maximum 120 (application-enforced, not Airtable-enforced)
- **Conversion**: Bidirectional integer handling in conversion methods
- **Clearing Behavior**: Whitespace-only input clears field (sets to None)
- **UI Integration**: Full edit menu and confirmation screen support with Russian labels
- **Display Fix**: Proper participant reconstruction includes age field in all display contexts

#### ChurchLeader Field Integration (Added 2025-01-14)
- **Search Results Display**: Shows in participant details with fallback to "—" for empty values
- **Edit Interface**: Text input field with Russian prompt "Отправьте имя церковного лидера"
- **Save Workflow**: Included in confirmation screens and save operations
- **Length Validation**: Respects maximum text field length constraints

#### TableName Field Integration with Role Logic (Added 2025-01-14)
- **Role-Based Visibility**: Only displayed when participant role is CANDIDATE
- **Dynamic Interface**: Edit button appears/disappears based on current role (including unsaved changes)
- **Business Rule Enforcement**: Prevents saving TableName for TEAM role participants
- **Edit Interface**: Text input field with Russian prompt "Отправьте название стола"
- **Search Results**: Conditionally displayed only for CANDIDATE role participants

#### Notes Field Integration with Multiline Support (Added 2025-01-14)
- **Multiline Text Input**: Supports line breaks and extended text entry
- **Search Results Formatting**: Shows truncated version with "..." indicator for long content
- **Full Display**: Complete notes shown in detailed participant view with proper escaping
- **Edit Interface**: Multiline text input field with Russian prompt "Отправьте заметки"
- **Markdown Safety**: Content properly escaped to prevent formatting injection

#### IsDepartmentChief Field Integration (Added 2025-01-19)
- **Internal Model**: `is_department_chief: Optional[bool]`
- **Airtable Field**: "IsDepartmentChief"
- **Data Type**: Checkbox (boolean)
- **Validation**: Optional boolean field with true/false/None handling
- **Usage**: Identify department chiefs for filtering and prioritization in participant lists
- **UI Integration**: Boolean field support with proper serialization/deserialization
- **Business Logic**: Enables department-based filtering with chief identification

### Security Enhancements

#### Formula Injection Prevention
All search operations include proper quote escaping to prevent Airtable formula injection:

```python
# Secure formula construction with quote escaping
def build_search_formula(field_name: str, value: str) -> str:
    # Escape single quotes by doubling them
    escaped_value = value.replace("'", "''")
    return f"{{field_name}} = '{escaped_value}'"
```

**Examples**:
- Input: `"O'Connor"` → Formula: `{RoomNumber} = 'O''Connor'`
- Input: `"Room 'A'"` → Formula: `{RoomNumber} = 'Room ''A'''`

### Validation Rules

#### Room Number Validation
```python
def validate_room_number(room: str) -> ValidationResult:
    """Validate room number format and constraints."""
    if not room or not room.strip():
        return ValidationResult(
            is_valid=False, 
            error_message="Room number cannot be empty"
        )
    
    # Accept any non-empty string (alphanumeric support)
    return ValidationResult(is_valid=True, cleaned_value=room.strip())
```

#### Floor Validation
```python
def validate_floor(floor: Union[int, str]) -> ValidationResult:
    """Validate floor number or name."""
    if floor is None:
        return ValidationResult(
            is_valid=False, 
            error_message="Floor cannot be empty"
        )
    
    # Convert to string for consistency
    floor_str = str(floor).strip()
    if not floor_str:
        return ValidationResult(
            is_valid=False, 
            error_message="Floor cannot be empty"
        )
    
    return ValidationResult(is_valid=True, cleaned_value=floor_str)
```

### Russian Translation Utilities (Added 2025-01-09)

#### Department and Role Translation Support
Complete Russian translation mappings for all participant fields have been implemented to provide consistent localized user interface. The department field is now actively used in team list displays, showing organizational context instead of personal data.

**Translation File**: `src/utils/translations.py`

```python
# Department translations (all 13 departments)
DEPARTMENT_RUSSIAN = {
    Department.ROE: "ROE",
    Department.CHAPEL: "Капелла",
    Department.SETUP: "Setup",
    Department.PALANKA: "Паланка",
    Department.ADMINISTRATION: "Администрация",
    Department.KITCHEN: "Kitchen",
    Department.DECORATION: "Декорация",
    Department.BELL: "Колокол",
    Department.REFRESHMENT: "Освежение",
    Department.WORSHIP: "Богослужение",
    Department.MEDIA: "Медиа",
    Department.CLERGY: "Клир",
    Department.RECTORATE: "Ректорат"
}

# Role translations
ROLE_RUSSIAN = {
    Role.CANDIDATE: "Кандидат",
    Role.TEAM: "Команда"
}

# Translation helper function
def translate_to_russian(value, translation_dict):
    """Translate enum value to Russian with fallback to original value"""
    return translation_dict.get(value, str(value))
```

#### Usage in Team List Display (Updated 2025-01-14)
The department field is now prominently displayed in team list results, providing organizational context instead of personal information. This enhances team management by showing which department each team member belongs to, facilitating better coordination and organization.

#### Usage in Room Search Results
These translations are also used by the `format_room_results_russian()` function to display all participant information in Russian, providing a consistent and user-friendly experience.

### Bot Access Requests Field Mappings (Added 2025-09-23)

#### BotAccessRequests Table Field Mappings
The BotAccessRequests table uses the following field mappings for user access control workflow:

```python
# BotAccessRequests table field mappings (src/config/field_mappings.py)
BOT_ACCESS_REQUESTS_FIELD_MAPPINGS = {
    "telegram_user_id": "fldeiF3gxg4fZMirc",    # TelegramUserId (Number - Integer)
    "telegram_username": "fld1RzNGWTGl8fSE4",   # TelegramUsername (Single line text)
    "status": "fldcuRa8qeUDKY3hN",              # Status (Single select)
    "access_level": "fldRBCoHwrJ87hdjr",        # AccessLevel (Single select)

    # Airtable field names for API calls
    "telegram_user_id_airtable": "TelegramUserId",
    "telegram_username_airtable": "TelegramUsername",
    "status_airtable": "Status",
    "access_level_airtable": "AccessLevel",
}
```

**Field Usage Guidelines**:
- **TelegramUserId**: Required primary key field for user identification and uniqueness enforcement
- **TelegramUsername**: Optional username field captured without @ prefix for admin reference
- **Status**: Required single select field with values: Pending (default), Approved, Denied
- **AccessLevel**: Required single select field with values: VIEWER (default), COORDINATOR, ADMIN
- **Enum Conversion**: Uses display values in Airtable ("Pending", "Approved") mapped to internal enums

**Repository Implementation** (Added 2025-09-23):
- **File**: `src/data/airtable/airtable_user_access_repo.py` (270 lines)
- **Methods**: Complete CRUD operations (create, get_by_id, get_by_telegram_user_id, get_by_status, approve, deny, update, delete)
- **Features**: Status filtering, approve/deny workflows with audit metadata, enum-to-display-value conversion
- **Test Coverage**: 9 comprehensive unit tests with full workflow coverage
- **Field Mapping Helper**: Integrated BotAccessRequestsFieldMapping class with comprehensive field ID mappings

**Model Integration**:
```python
# UserAccessRequest model (src/models/user_access_request.py)
class UserAccessRequest(BaseModel):
    id: Optional[str] = None
    telegram_user_id: int
    telegram_username: Optional[str] = None
    status: AccessRequestStatus = AccessRequestStatus.PENDING
    access_level: AccessLevel = AccessLevel.VIEWER
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Enum definitions
    class AccessRequestStatus(str, Enum):
        PENDING = "Pending"
        APPROVED = "Approved"
        DENIED = "Denied"

    class AccessLevel(str, Enum):
        VIEWER = "VIEWER"
        COORDINATOR = "COORDINATOR"
        ADMIN = "ADMIN"
```

**Configuration Integration**:
```python
# Environment variable configuration
AIRTABLE_ACCESS_REQUESTS_TABLE_NAME=BotAccessRequests
AIRTABLE_ACCESS_REQUESTS_TABLE_ID=tblQWWEcHx9sfhsgN

# Service layer usage
from src.services.access_request_service import AccessRequestService
access_service = AccessRequestService(user_access_repo)

# Create new access request
request = await access_service.submit_request(user_id=123456789, username="user123")

# Admin approval workflow
await access_service.approve_request(request_id="recABC123", admin_user_id=987654321)
```

### Multi-Table Field Mappings (Added 2025-01-21)

#### BibleReaders Table Field Mappings
The BibleReaders table uses the following field mappings for session management with complete repository implementation:

```python
# BibleReaders table field mappings (src/config/field_mappings/bible_readers.py)
BIBLE_READERS_FIELD_MAPPINGS = {
    "where": "fldsSNHSXJBhewCxq",         # Where (Primary field)
    "participants": "fldVBlRvv295QhBlX",   # Participants (Link to Participants)
    "when": "fld6WfIcctT2WZnNO",          # When (Date)
    "bible": "fldi18WKRAa7iUXBQ",         # Bible (Single line text)

    # Lookup fields (read-only)
    "churches": "fldadEnWickpmcDCE",       # Church (from Participants)
    "room_numbers": "fldOGZxVkpFycVs38",   # RoomNumber (from Participants)
}
```

**Field Usage Guidelines**:
- **Where**: Required primary field for session location/context
- **Participants**: Multiple record links to Participants table for reader assignments
- **When**: Optional date field for scheduling Bible reading sessions with localized date formatting (`format = l`)
- **Bible**: Optional text field for Scripture passage references
- **Lookup Fields**: Automatically populated from linked participant records

**Repository Implementation** (Added 2025-01-21):
- **File**: `src/data/airtable/airtable_bible_readers_repo.py` (267 lines)
- **Methods**: Complete CRUD operations (create, get_by_id, get_by_where, update, delete, list_all, get_by_participant_id)
- **Features**: Writable field filtering, date formatting utilities, comprehensive error handling
- **Test Coverage**: 25 unit tests with 80% coverage
- **Field Mapping Helper**: 133 lines with comprehensive field ID mappings and utilities

#### ROE Table Field Mappings
The ROE table uses the following field mappings for Rollo session management with presenter validation:

```python
# ROE table field mappings (src/config/field_mappings/roe.py)
ROE_FIELD_MAPPINGS = {
    "roe_topic": "fldSniGvfWpmkpc1r",       # RoeTopic (Primary field)
    "roista": "fldLWsfnGvJ26GwMI",         # Roista (Link to Participants)
    "assistant": "fldtTUTsJy6oCg1sE",      # Assistant (Link to Participants)

    # Roista lookup fields (read-only)
    "roista_church": "flday5BYiQsP8njau",    # RoistaChurch
    "roista_department": "fldomNR0M0AHolSmj", # RoistaDepartment
    "roista_room": "fldNlkZv2bktVqFDl",     # RoistaRoom
    "roista_notes": "fldHa1gyW60Dz9wfC",    # RoistaNotes

    # Assistant lookup fields (read-only)
    "assistant_church": "fldsDcqcSfilntPws",     # AssistantChuch (preserves Airtable typo)
    "assistant_department": "fldgDVWQNFeooDRo7",  # AssistantDepartment
    "assistant_room": "fldBlcyDcW0NcUVcX",      # AssistantRoom
}
```

**Field Usage Guidelines**:
- **RoeTopic**: Required primary field for ROE session topic
- **Roista**: Multiple record links to main presenters from Participants table
- **Assistant**: Multiple record links to assistant presenters from Participants table
- **Lookup Fields**: Automatically display presenter details for planning purposes
- **Typo Preservation**: "AssistantChuch" maintains Airtable compatibility

**Repository Implementation** (Added 2025-01-21):
- **File**: `src/data/airtable/airtable_roe_repo.py` (310 lines)
- **Methods**: Complete CRUD operations (create, get_by_id, get_by_topic, update, delete, list_all, get_by_roista_id, get_by_assistant_id)
- **Features**: Presenter relationship validation (Roista OR Assistant required, not both), duration formatting utilities
- **Business Logic**: Create/update operations validate presenter relationships to ensure data integrity
- **Field Mapping Helper**: 198 lines with comprehensive field ID mappings and presenter validation logic

#### Multi-Table Configuration Integration
The field mappings integrate with the multi-table configuration system:

```python
# Environment variable configuration
AIRTABLE_BIBLE_READERS_TABLE_NAME=BibleReaders
AIRTABLE_BIBLE_READERS_TABLE_ID=tblGEnSfpPOuPLXcm
AIRTABLE_ROE_TABLE_NAME=ROE
AIRTABLE_ROE_TABLE_ID=tbl0j8bcgkV3lVAdc

# Usage in data models
class BibleReader(BaseModel):
    # Uses BIBLE_READERS_FIELD_MAPPINGS for Airtable integration

class ROE(BaseModel):
    # Uses ROE_FIELD_MAPPINGS for Airtable integration
```

### Extended Fields Testing and Validation (2025-01-14)

#### Comprehensive Field Testing
The three new participant fields have been thoroughly tested with comprehensive test coverage:

**Model Testing**:
- Round-trip serialization/deserialization for all new fields
- Airtable field mapping validation (fldbQr0R6nEtg1nXM, fldwIopXniSHk94v9, fldL4wmlV9de1kKa1)
- Optional field handling and backward compatibility
- Multiline text support for Notes field

**Business Logic Testing**:
- Role-based TableName field visibility and validation
- Church leader text input validation
- Notes multiline text handling and formatting
- Field length constraints and edge cases

**Integration Testing**:
- End-to-end workflow from search → edit → save for all new fields
- Airtable API integration with proper field mapping
- UI integration with role-based field display
- Save/cancel workflow with new fields included

**Test Coverage Metrics**:
- 90%+ coverage across all implementation areas
- Comprehensive unit tests for model extensions
- Service layer validation testing
- UI integration testing with role-based logic

### Integration Testing and Validation (2025-01-09)

#### Enhanced Test Coverage with Translation Validation  
**Test Files**: Enhanced integration test coverage including translation testing
- `test_room_search_integration.py`: Enhanced with Russian translation validation
- `test_floor_search_integration.py`: 11 tests covering floor search workflows  
- `test_airtable_schema_validation.py`: 10 tests validating field mappings
- `test_translations.py`: New test file for translation utilities validation

#### Verified Field Mappings
Field IDs have been validated through comprehensive integration testing with actual Airtable API calls:

```python
# Verified field mappings (Integration tested 2025-09-05, Extended 2025-01-19)
FIELD_MAPPINGS = {
    "room_number": "fldJTPjo8AHQaADVu",  # Validated: TEXT type, alphanumeric support
    "floor": "fldlzG1sVg01hsy2g",        # Validated: Union[int, str] support
    "church_leader": "fldbQr0R6nEtg1nXM", # Validated: TEXT type, optional
    "table_name": "fldwIopXniSHk94v9",   # Validated: TEXT type, role-restricted
    "notes": "fldL4wmlV9de1kKa1",       # Validated: LONG_TEXT type, multiline
    "is_department_chief": "fldWAay3tQiXN9888",  # Validated: CHECKBOX type, boolean
}
```

### Multi-Table Integration Testing (Added 2025-01-21)

#### BibleReaders Model Testing
**Test Coverage**: 13 comprehensive tests covering all model scenarios
- **Field Validation**: Required `where` field and optional fields validation
- **Relationship Handling**: Participant ID list serialization and validation
- **Date Handling**: ISO date serialization for `when` field
- **Lookup Fields**: Read-only lookup field exclusion from write operations
- **API Integration**: Complete `from_airtable_record` and `to_airtable_fields` testing

#### ROE Model Testing
**Test Coverage**: 14 comprehensive tests covering all model scenarios
- **Field Validation**: Required `roe_topic` field and optional presenter fields
- **Presenter Relationships**: Roista and Assistant ID list handling
- **Lookup Field Management**: Seven lookup fields properly excluded from writes
- **Typo Compatibility**: "AssistantChuch" field name preserved for Airtable compatibility
- **API Integration**: Complete round-trip serialization testing

#### Repository Interface Testing
**Test Coverage**: Interface compliance validation for both new repositories
- **BibleReadersRepository**: 7 abstract methods validated
- **ROERepository**: 8 abstract methods validated
- **Method Signatures**: Consistent async patterns across all repository interfaces
- **Dependency Injection**: Factory pattern integration testing

#### Client Factory Testing
**Test Coverage**: 6 comprehensive tests for multi-table client creation
- **Table Type Support**: Participants, BibleReaders, ROE client creation
- **Configuration Integration**: Environment variable and settings integration
- **Dependency Injection**: Service integration with factory pattern
- **Error Handling**: Invalid table type validation

#### Integration Points

#### Repository Layer Integration (Tested)
- `AirtableParticipantRepository.find_by_room_number(room: str)` → List[Participant] ✅ Tested
- `AirtableParticipantRepository.find_by_floor(floor: Union[int, str])` → List[Participant] ✅ Tested
- **Floor Discovery** (New - 2025-01-20): `AirtableParticipantRepository.get_available_floors()` → List[int] ✅ Tested (12 tests including caching and error handling)

#### Service Layer Integration (Tested)
- `SearchService.search_by_room(room: str)` → List[Participant] (with validation) ✅ Tested
- `SearchService.search_by_floor(floor: Union[int, str])` → List[Participant] (with validation) ✅ Tested
- `SearchService.search_by_room_formatted(room: str)` → str (formatted results) ✅ Tested
- **Floor Discovery Service** (New - 2025-01-20): `SearchService.get_available_floors()` → List[int] (with caching and error handling) ✅ Tested

#### Error Handling (Comprehensive Testing)
- **Validation Errors**: Invalid room/floor format ✅ Tested with standardized messages
- **Data Access Errors**: Airtable API failures ✅ Tested with graceful degradation
- **Security Errors**: Formula injection attempts ✅ Tested with quote escaping
- **Empty Result Handling**: No participants found for specified room/floor ✅ Tested
- **Performance Validation**: All operations validated to complete within 3 seconds ✅ Tested

#### Production Readiness Verification
- **Schema Alignment**: All field mappings verified against production Airtable structure
- **Alphanumeric Room Support**: Tested with rooms like "101", "A1", "Conference"
- **Multi-Room Floor Processing**: Tested floor search with participant grouping and sorting
- **Error Message Standardization**: Centralized templates provide consistent UX
- **Multi-Table Schema Validation**: BibleReaders and ROE table structures verified
- **Cross-Table Relationships**: Participant linking tested across all table types
- **Lookup Field Validation**: Read-only lookup fields properly excluded from write operations
- **API Integration**: Complete multi-table API integration tested with 64 tests (100% pass rate)
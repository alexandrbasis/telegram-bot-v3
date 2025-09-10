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
    
    # Other participant fields
    "full_name_ru": "fld...",
    "full_name_en": "fld...",
    # ... other field mappings
}
```

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

#### DateOfBirth Field (fld1rN2cffxKuZh4i) - Added 2025-09-10
- **Internal Model**: `date_of_birth: Optional[date]`
- **Airtable Field**: "DateOfBirth"
- **Data Type**: Date
- **Validation**: ISO date format (YYYY-MM-DD), Python date object
- **Constraints**: Valid date values, application-side validation
- **Conversion**: to_airtable_fields() serializes as ISO string, from_airtable_record() deserializes to date object

#### Age Field (fldZPh65PIekEbgvs) - Added 2025-09-10
- **Internal Model**: `age: Optional[int]`
- **Airtable Field**: "Age"
- **Data Type**: Number
- **Validation**: Integer values with application-side constraints (0-120 range)
- **Constraints**: Minimum 0, Maximum 120 (application-enforced, not Airtable-enforced)
- **Conversion**: Bidirectional integer handling in conversion methods

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
Complete Russian translation mappings for all participant fields have been implemented to provide consistent localized user interface.

**Translation File**: `src/utils/translations.py`

```python
# Department translations (all 13 departments)
DEPARTMENT_RUSSIAN = {
    Department.ROE: "ROE",
    Department.CHAPEL: "Капелла", 
    Department.SETUP: "Подготовка",
    Department.PALANKA: "Паланка",
    Department.ADMINISTRATION: "Администрация",
    Department.KITCHEN: "Кухня",
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

#### Usage in Room Search Results
These translations are used by the `format_room_results_russian()` function to display all participant information in Russian, providing a consistent and user-friendly experience.

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
# Verified field mappings (Integration tested 2025-09-05)
FIELD_MAPPINGS = {
    "room_number": "fldJTPjo8AHQaADVu",  # Validated: TEXT type, alphanumeric support
    "floor": "fldlzG1sVg01hsy2g",        # Validated: Union[int, str] support
}
```

#### Integration Points

#### Repository Layer Integration (Tested)
- `AirtableParticipantRepository.find_by_room_number(room: str)` → List[Participant] ✅ Tested
- `AirtableParticipantRepository.find_by_floor(floor: Union[int, str])` → List[Participant] ✅ Tested

#### Service Layer Integration (Tested)
- `SearchService.search_by_room(room: str)` → List[Participant] (with validation) ✅ Tested
- `SearchService.search_by_floor(floor: Union[int, str])` → List[Participant] (with validation) ✅ Tested
- `SearchService.search_by_room_formatted(room: str)` → str (formatted results) ✅ Tested

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
# Field Mappings

## Airtable Field Mappings

### Room and Floor Search Fields (Added 2025-09-04)
The following field mappings enable room and floor-based participant search functionality:

```python
# Field mappings for location-based search
FIELD_MAPPINGS = {
    # Room/Floor search fields
    "room_number": "fldJTPjo8AHQaADVu",  # RoomNumber field in Airtable
    "floor": "fldlzG1sVg01hsy2g",        # Floor field in Airtable
    
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

### Integration Points

#### Repository Layer Integration
- `AirtableParticipantRepository.find_by_room_number(room: str)` → List[Participant]
- `AirtableParticipantRepository.find_by_floor(floor: Union[int, str])` → List[Participant]

#### Service Layer Integration
- `SearchService.search_by_room(room: str)` → List[Participant] (with validation)
- `SearchService.search_by_floor(floor: Union[int, str])` → List[Participant] (with validation)
- `SearchService.search_by_room_formatted(room: str)` → str (formatted results)

#### Error Handling
- **Validation Errors**: Invalid room/floor format
- **Data Access Errors**: Airtable API failures
- **Security Errors**: Formula injection attempts
- **Empty Result Handling**: No participants found for specified room/floor
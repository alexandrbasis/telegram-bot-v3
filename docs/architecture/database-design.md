# Database Design

## Participant Data Model

### Extended Participant Schema (Updated 2025-01-14)

The participant data model has been extended with additional fields to support enhanced event organization and management capabilities.

#### Core Participant Fields
```python
class Participant(BaseModel):
    # Identity fields
    participant_id: Optional[str]
    full_name_ru: str  # Required
    full_name_en: Optional[str]
    nickname: Optional[str]

    # Contact and location
    church: Optional[str]
    location: Optional[str]
    contact: Optional[str]

    # Physical attributes
    gender: Optional[Gender]  # M/F
    size: Optional[Size]  # XS-3XL

    # Role and organization
    role: Optional[Role]  # CANDIDATE/TEAM
    department: Optional[Department]  # 13 departments

    # Payment information
    payment_status: Optional[PaymentStatus]
    payment_amount: Optional[int]
    payment_date: Optional[date]

    # Accommodation (Added 2025-09-04)
    room_number: Optional[str]
    floor: Optional[Union[int, str]]

    # Demographics (Added 2025-09-10)
    date_of_birth: Optional[date]
    age: Optional[int]

    # Extended fields (Added 2025-01-14)
    church_leader: Optional[str]  # Church leadership tracking
    table_name: Optional[str]     # Event seating management (CANDIDATE only)
    notes: Optional[str]          # Multiline administrative notes

    # Administrative
    submitted_by: Optional[str]
```

#### Field Categories and Business Logic

**Identity Fields**:
- `full_name_ru`: Required field for participant identification
- `full_name_en`: Optional English name for international participants
- `nickname`: Alternative name for search and identification

**Extended Management Fields (2025-01-14)**:
- `church_leader`: Optional text field for tracking church leadership associations
- `table_name`: Role-restricted field (CANDIDATE only) for event seating arrangements
- `notes`: Multiline text field for administrative information and special requirements

**Role-Based Field Access**:
- `table_name` field has business logic restrictions:
  - Only visible in UI when participant role is CANDIDATE
  - Validation prevents saving for TEAM role participants
  - Dynamic visibility based on current role (including unsaved changes)

### Airtable Schema Mapping

#### Extended Field Mappings (Updated 2025-01-14)
```python
FIELD_MAPPINGS = {
    # Extended participant fields
    "church_leader": "fldbQr0R6nEtg1nXM",   # ChurchLeader (Single line text)
    "table_name": "fldwIopXniSHk94v9",     # TableName (Single line text)
    "notes": "fldL4wmlV9de1kKa1",         # Notes (Long text)

    # Existing fields
    "full_name_ru": "fldXXXXXXXXXXXXX",    # Full Name Russian
    "role": "fldYYYYYYYYYYYYY",           # Role (Candidate/Team)
    # ... other field mappings
}
```

#### Data Type Specifications
- **ChurchLeader**: Airtable Single line text → Python Optional[str]
- **TableName**: Airtable Single line text → Python Optional[str] (role-restricted)
- **Notes**: Airtable Long text → Python Optional[str] (multiline support)

### Data Access Patterns

#### Repository Layer Extensions
The participant repository has been extended to handle new fields:

```python
class AirtableParticipantRepository:
    def update_by_id(self, participant_id: str, participant: Participant) -> bool:
        # Handles all 18 fields including extended fields
        # Includes role-based validation for table_name
        # Supports multiline text for notes field
```

#### Service Layer Integration
```python
class ParticipantUpdateService:
    TEXT_FIELDS = [
        'full_name_ru', 'full_name_en', 'church', 'location', 'contact',
        'submitted_by', 'church_leader', 'table_name', 'notes'  # Extended fields
    ]

    def validate_field_input(self, field_name: str, value: str) -> ValidationResult:
        # Extended validation for new fields
        # Role-based business rules for table_name
        # Multiline text handling for notes
```

### Data Integrity and Validation

#### Field Validation Rules
1. **church_leader**: Optional text, no length restrictions beyond Airtable limits
2. **table_name**:
   - Optional text field
   - Business rule: Only valid for CANDIDATE role participants
   - Validation error returned if attempted save for TEAM role
3. **notes**:
   - Optional multiline text
   - Supports line breaks and special characters
   - Markdown-safe escaping in display contexts

#### Role-Based Business Logic
```python
def validate_table_name_access(participant: Participant) -> bool:
    """Validate TableName field access based on participant role."""
    effective_role = participant.role or Role.CANDIDATE  # Default role
    return effective_role == Role.CANDIDATE
```

### Migration Strategy

#### Backward Compatibility
- All new fields are optional to maintain compatibility with existing data
- Existing participant records work without modification
- API responses include new fields with null/empty values for legacy data

#### Data Population
- New fields can be populated gradually through the editing interface
- Bulk import functionality can be extended to include new fields
- Search functionality automatically includes new fields in results

### Performance Considerations

#### Query Optimization
- New fields are indexed in Airtable for efficient filtering
- Search operations include new fields without performance degradation
- Multiline notes field uses truncation in list views to optimize display

#### Memory Management
- Multiline notes field handled efficiently with proper text truncation
- Role-based field visibility reduces unnecessary data transfer
- Field validation prevents oversized data storage

### Security and Data Protection

#### Input Validation
- All text fields sanitized to prevent injection attacks
- Multiline notes field escaped for safe Markdown display
- Role-based access controls prevent unauthorized field modifications

#### Data Privacy
- Extended fields follow same privacy patterns as existing fields
- Notes field can contain sensitive information - handled with appropriate care
- Church leader information treated as administrative data
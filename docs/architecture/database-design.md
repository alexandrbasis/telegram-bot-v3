# Database Design

## Multi-Table Data Architecture (Updated 2025-01-21)

### Overview
The Tres Dias Telegram Bot v3 now supports multi-table data management with three primary tables:
- **Participants**: Core participant information and event management
- **BibleReaders**: Bible reading session assignments and scheduling
- **ROE**: Rollo of Encouragement session management with presenter assignments

### Table Relationships
- Participants table serves as the central hub with relationships to both BibleReaders and ROE tables
- Cross-table relationships enable comprehensive activity tracking across events
- Lookup fields provide automated data synchronization between related tables

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

    # Leadership and management (Added 2025-01-19)
    is_department_chief: Optional[bool]  # Department chief identification

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

**Leadership Identification Fields (2025-01-19)**:
- `is_department_chief`: Optional boolean field for identifying department chiefs within their assigned departments

**Role-Based Field Access**:
- `table_name` field has business logic restrictions:
  - Only visible in UI when participant role is CANDIDATE
  - Validation prevents saving for TEAM role participants
  - Dynamic visibility based on current role (including unsaved changes)

### Airtable Schema Mapping

#### Extended Field Mappings (Updated 2025-01-19)
```python
FIELD_MAPPINGS = {
    # Extended participant fields
    "church_leader": "fldbQr0R6nEtg1nXM",   # ChurchLeader (Single line text)
    "table_name": "fldwIopXniSHk94v9",     # TableName (Single line text)
    "notes": "fldL4wmlV9de1kKa1",         # Notes (Long text)

    # Leadership identification fields
    "is_department_chief": "fldWAay3tQiXN9888",  # IsDepartmentChief (Checkbox)

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
- **IsDepartmentChief**: Airtable Checkbox → Python Optional[bool] (department leadership indicator)

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

    BOOLEAN_FIELDS = [
        'is_department_chief'  # Leadership identification fields
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
- Multi-table architecture maintains backward compatibility with single-table operations

#### Data Population
- New fields can be populated gradually through the editing interface
- Bulk import functionality can be extended to include new fields
- Search functionality automatically includes new fields in results
- Multi-table data can be managed independently without affecting existing participant workflows

## BibleReaders Data Model (New 2025-01-21)

### Schema Definition
```python
class BibleReader(BaseModel):
    record_id: Optional[str]  # Airtable record ID
    where: str  # Primary field - location/context (required)
    participants: Optional[List[str]]  # Linked participant record IDs
    when: Optional[date]  # Date of reading session
    bible: Optional[str]  # Bible passage reference

    # Lookup fields (read-only)
    churches: Optional[List[str]]  # From linked participants
    room_numbers: Optional[List[Union[int, str]]]  # From linked participants
```

### Key Features
- **Session Management**: Tracks Bible reading sessions with location and timing
- **Participant Linking**: Multiple participants can be assigned to each session
- **Lookup Fields**: Automatically displays participant churches and room numbers
- **Scheduling Support**: Date field enables conflict detection and schedule generation

### Airtable Integration
- **Table ID**: `tblGEnSfpPOuPLXcm`
- **Primary Field**: `Where` (fldsSNHSXJBhewCxq)
- **Relationship Fields**: Links to Participants table for reader assignments
- **Validation**: Required `where` field, optional scheduling and reference fields
- **Repository Implementation**: AirtableBibleReadersRepo with full CRUD operations
- **Field Mapping Helper**: `src/config/field_mappings/bible_readers.py` with comprehensive field ID mappings

## ROE Data Model (New 2025-01-21)

### Schema Definition
```python
class ROE(BaseModel):
    record_id: Optional[str]  # Airtable record ID
    roe_topic: str  # Primary field - ROE session topic (required)
    roista: Optional[List[str]]  # Main presenter participant record IDs
    assistant: Optional[List[str]]  # Assistant presenter participant record IDs

    # Lookup fields (read-only)
    roista_church: Optional[List[str]]  # From main presenter
    roista_department: Optional[List[str]]  # From main presenter
    roista_room: Optional[List[Union[int, str]]]  # From main presenter
    roista_notes: Optional[List[str]]  # From main presenter
    assistant_church: Optional[List[str]]  # From assistant presenter
    assistant_department: Optional[List[str]]  # From assistant presenter
    assistant_room: Optional[List[Union[int, str]]]  # From assistant presenter
```

### Key Features
- **Session Topic Management**: Tracks ROE topics and presenter assignments
- **Dual Presenter Support**: Separate fields for main and assistant presenters
- **Comprehensive Lookup Fields**: Displays detailed presenter information automatically
- **Organizational Context**: Shows department and location data for planning

### Airtable Integration
- **Table ID**: `tbl0j8bcgkV3lVAdc`
- **Primary Field**: `RoeTopic` (fldSniGvfWpmkpc1r)
- **Relationship Fields**: Links to Participants table for presenter assignments
- **Validation**: Required `roe_topic` field, optional presenter assignments
- **Repository Implementation**: AirtableROERepo with full CRUD operations and presenter validation
- **Field Mapping Helper**: `src/config/field_mappings/roe.py` with presenter relationship validation

## Multi-Table Repository Architecture

### Repository Interface Pattern
All table repositories follow consistent abstract interface patterns:

```python
# Abstract repository interfaces
class BibleReadersRepository(ABC):
    @abstractmethod
    async def create(self, bible_reader: BibleReader) -> str: ...
    @abstractmethod
    async def get_by_id(self, record_id: str) -> Optional[BibleReader]: ...
    @abstractmethod
    async def get_by_where(self, where: str) -> List[BibleReader]: ...
    @abstractmethod
    async def update(self, record_id: str, bible_reader: BibleReader) -> bool: ...
    @abstractmethod
    async def delete(self, record_id: str) -> bool: ...
    @abstractmethod
    async def list_all(self) -> List[BibleReader]: ...
    @abstractmethod
    async def get_by_participant_id(self, participant_id: str) -> List[BibleReader]: ...

class ROERepository(ABC):
    @abstractmethod
    async def create(self, roe: ROE) -> str: ...
    @abstractmethod
    async def get_by_id(self, record_id: str) -> Optional[ROE]: ...
    @abstractmethod
    async def get_by_topic(self, topic: str) -> List[ROE]: ...
    @abstractmethod
    async def update(self, record_id: str, roe: ROE) -> bool: ...
    @abstractmethod
    async def delete(self, record_id: str) -> bool: ...
    @abstractmethod
    async def list_all(self) -> List[ROE]: ...
    @abstractmethod
    async def get_by_roista_id(self, participant_id: str) -> List[ROE]: ...
    @abstractmethod
    async def get_by_assistant_id(self, participant_id: str) -> List[ROE]: ...
```

### Client Factory Pattern
AirtableClientFactory provides table-specific client creation with complete multi-table support:

```python
class AirtableClientFactory:
    def __init__(self, settings: DatabaseSettings):
        self.settings = settings

    def create_client(self, table_type: str) -> AirtableClient:
        """Create Airtable client for specific table type."""
        config = self.settings.to_airtable_config(table_type)
        return AirtableClient(config)
```

**Supported Table Types**:
- `participants`: Participants table (tbl8ivwOdAUvMi3Jy)
- `bible_readers`: BibleReaders table (tblGEnSfpPOuPLXcm)
- `roe`: ROE table (tbl0j8bcgkV3lVAdc)

**Repository Implementations** (Added 2025-01-21):
- **AirtableBibleReadersRepo**: Complete CRUD operations with 7 methods (create, get_by_id, get_by_where, update, delete, list_all, get_by_participant_id)
- **AirtableROERepo**: Complete CRUD operations with 8 methods including presenter-specific queries (get_by_roista_id, get_by_assistant_id)
- **Multi-table Coordination**: Integration tests verify repositories use separate clients without connection conflicts

### Data Model Validation
- **Pydantic v2 Integration**: All models use modern Pydantic patterns
- **Field Validation**: Comprehensive validation for required and optional fields
- **API Serialization**: `from_airtable_record` and `to_airtable_fields` methods
- **Lookup Field Handling**: Read-only lookup fields excluded from write operations
- **Business Logic Validation**: ROE repository includes presenter relationship validation (Roista OR Assistant required, not both)
- **Date Formatting**: BibleReaders field mapping includes localized date formatting utilities
- **Field Mapping Helpers**: Dedicated helpers for each table type with field ID translations and validation logic

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
- Multi-table relationships maintain data privacy across linked records
- Lookup fields provide controlled access to related participant information
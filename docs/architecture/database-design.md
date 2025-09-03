# Database Design

This document describes the database design and data model for the Tres Dias Telegram Bot, including the participant data structure, relationships, and accommodation tracking capabilities.

## Data Model Overview

The bot uses a single-table design with the `Participant` model as the core entity, containing comprehensive participant information including personal details, role assignments, payment tracking, and accommodation information.

## Participant Model Structure

### Core Fields
| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `id` | str | Yes (Primary) | Unique Airtable record identifier |
| `full_name_ru` | str | Yes | Full name in Russian (primary field) |
| `full_name_en` | str | No | Full name in English |
| `church` | str | No | Church affiliation |
| `country_and_city` | str | No | Location information |
| `contact_information` | str | No | Contact details |
| `submitted_by` | str | No | Person who submitted the record |

### Enum Fields (Single Select)
| Field Name | Type | Options | Description |
|------------|------|---------|-------------|
| `gender` | Gender | M, F | Participant gender |
| `size` | Size | XS, S, M, L, XL, XXL, 3XL | Clothing size |
| `role` | Role | CANDIDATE, TEAM | Participant role in event |
| `department` | Department | ROE, Chapel, Setup, Palanka, Administration, Kitchen, Decoration, Bell, Refreshment, Worship, Media, Clergy, Rectorate | Department assignment |
| `payment_status` | PaymentStatus | Paid, Partial, Unpaid | Payment tracking status |

### Numeric and Date Fields
| Field Name | Type | Validation | Description |
|------------|------|------------|-------------|
| `payment_amount` | int | ≥ 0 | Payment amount in integer format |
| `payment_date` | str | YYYY-MM-DD | Payment date in ISO format |

### Accommodation Fields (New)
| Field Name | Type | Validation | Description |
|------------|------|------------|-------------|
| `floor` | Optional[Union[int, str]] | Integer or descriptive string | Floor level (supports "1", "2", "Ground", "Basement") |
| `room_number` | Optional[str] | Alphanumeric | Room number or identifier (supports "101", "A12B", "Suite 100") |

## Accommodation Tracking Design

### Floor Field Design
The `floor` field uses a flexible Union type to support different accommodation numbering systems:

**Numeric Floors**: 1, 2, 3, 4, etc.
**Descriptive Floors**: "Ground", "Basement", "Mezzanine", "Penthouse"
**Mixed Systems**: Allows properties to use their preferred naming convention

**Implementation Details**:
- Stored as string in Airtable for maximum flexibility
- Python model accepts both int and str types
- Validation accepts any non-empty string or positive integer
- Display formatting preserves original input format

### Room Number Design
The `room_number` field supports various room identification formats:

**Standard Numeric**: "101", "205", "1001"
**Alphanumeric Codes**: "A12B", "C204", "Room-301"
**Descriptive Names**: "Conference Room A", "Suite 100", "Presidential Suite"

**Implementation Details**:
- Stored as string in Airtable
- Accepts any alphanumeric string
- Special validator converts empty strings to None for proper null handling
- No length restrictions to accommodate various naming conventions

## Data Relationships

### Single Entity Design
The bot uses a simplified single-table approach with all participant information stored in one entity. This design choice provides:

- **Simplicity**: No complex joins or relationships to manage
- **Performance**: Single-record operations for all participant data
- **Consistency**: All data modifications happen atomically
- **Flexibility**: Easy to add new fields without schema migrations

### Future Extensibility
While currently using a single-table design, the architecture supports future expansion:

- **Audit Trail**: Could add a separate table for change history
- **Event Management**: Could add event/session entities linked to participants
- **Room Management**: Could add dedicated room inventory management
- **Payment History**: Could separate payments into detailed transaction records

## Database Access Patterns

### Search Operations
**Primary Search**: By name (Russian and English) with fuzzy matching
**Secondary Search**: By accommodation (floor and room number)
**Filter Operations**: By role, department, payment status

### Update Operations
**Field-Level Updates**: Individual field modifications with validation
**Atomic Updates**: All changes committed in single Airtable operation
**Accommodation Updates**: Floor and room number can be updated independently

### Validation Patterns
**Required Field Validation**: Only Russian name is required
**Enum Validation**: Strict validation for single-select fields
**Accommodation Validation**: Flexible validation for floor and room formats
**Date/Number Validation**: Format and range validation for payment fields

## Data Storage Implementation

### Airtable as Primary Database
The bot uses Airtable as the primary database with the following benefits:

- **Built-in UI**: Web interface for manual data management
- **No Infrastructure**: Cloud-hosted with automatic backups
- **API Integration**: REST API with Python client library
- **Collaboration**: Multi-user access and permissions

### Repository Pattern
Data access is abstracted through the repository pattern:

```python
class ParticipantRepository(ABC):
    @abstractmethod
    async def create(self, participant: Participant) -> str: ...
    
    @abstractmethod  
    async def update_by_id(self, participant_id: str, updates: dict) -> bool: ...
    
    @abstractmethod
    async def search_by_name(self, name: str) -> List[Participant]: ...
```

This design enables:
- **Database Migration**: Easy switching to other databases (PostgreSQL, SQLite)
- **Testing**: Mock repository implementations for unit tests
- **Performance**: Optimized query implementations per database type

## Schema Evolution Strategy

### Accommodation Fields Addition (AGB-25)
The recent addition of Floor and Room Number fields demonstrates the schema evolution approach:

1. **Model Extension**: Added optional fields to Participant model
2. **Validation Updates**: Extended validation service with new field rules
3. **Mapping Updates**: Updated Airtable field mappings
4. **UI Integration**: Added accommodation fields to edit interface
5. **Backward Compatibility**: Existing records continue to work without accommodation data

### Future Schema Changes
The established pattern for schema evolution:

1. **Optional by Default**: New fields should be optional to maintain compatibility
2. **Validation First**: Define validation rules before implementation
3. **Model-Driven**: Update the Participant model as the source of truth
4. **Service Integration**: Update validation and business logic services
5. **UI Last**: Update user interface to expose new functionality

## Performance Considerations

### Airtable Rate Limiting
- **Rate Limit**: 5 requests per second
- **Batch Operations**: Single update operations for multiple field changes
- **Caching Strategy**: Not implemented (simple architecture)

### Search Performance
- **Fuzzy Matching**: Client-side fuzzy search with ranking
- **Field Indexing**: Relies on Airtable's built-in indexing
- **Pagination**: Results limited to 10 per page for responsiveness

### Accommodation Search Performance
- **Floor Search**: String matching on floor field
- **Room Search**: Alphanumeric matching on room number field
- **Combined Search**: Both accommodation fields included in general search

## Data Integrity

### Validation Layers
1. **Model Validation**: Pydantic validation at the data model level
2. **Service Validation**: Business logic validation in update service
3. **Airtable Validation**: Server-side validation by Airtable

### Error Handling
- **Graceful Degradation**: Missing accommodation fields display as "N/A"
- **Validation Errors**: Clear Russian error messages for users
- **API Failures**: Retry mechanisms with change preservation

### Data Migration Safety
- **Non-Breaking Changes**: All new fields are optional
- **Schema Discovery**: Automatic field ID discovery for robustness
- **Fallback Handling**: Field name fallbacks if IDs are unavailable
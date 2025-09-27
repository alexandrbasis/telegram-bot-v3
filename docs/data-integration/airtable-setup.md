# Airtable Setup

# Airtable Configuration and Setup

## Multi-Table Configuration (Added 2025-01-21)

### Supported Tables
The application now supports three Airtable tables with dedicated repository implementations:

#### Participants Table
- **Table Name**: Participants
- **Table ID**: `tbl8ivwOdAUvMi3Jy` (default)
- **Repository**: AirtableParticipantRepository
- **Primary Use**: Core participant information and event management

#### BibleReaders Table
- **Table Name**: BibleReaders
- **Table ID**: `tblGEnSfpPOuPLXcm`
- **Repository**: AirtableBibleReadersRepo
- **Primary Use**: Bible reading session assignments and scheduling
- **Field Mapping Helper**: `src/config/field_mappings/bible_readers.py`

#### ROE Table
- **Table Name**: ROE
- **Table ID**: `tbl0j8bcgkV3lVAdc`
- **Repository**: AirtableROERepo
- **Primary Use**: Rollo of Encouragement session management with presenter assignments
- **Field Mapping Helper**: `src/config/field_mappings/roe.py`

### Environment Variable Configuration
```bash
# Base configuration (shared across all tables)
AIRTABLE_API_KEY=your_api_key_here
AIRTABLE_BASE_ID=appRp7Vby2JMzN0mC

# Participants table (existing)
AIRTABLE_TABLE_NAME=Participants
AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy

# BibleReaders table (new)
AIRTABLE_BIBLE_READERS_TABLE_NAME=BibleReaders
AIRTABLE_BIBLE_READERS_TABLE_ID=tblGEnSfpPOuPLXcm

# ROE table (new)
AIRTABLE_ROE_TABLE_NAME=ROE
AIRTABLE_ROE_TABLE_ID=tbl0j8bcgkV3lVAdc

# View-aligned export configuration (Added 2025-09-27)
AIRTABLE_PARTICIPANT_EXPORT_VIEW=Кандидаты
AIRTABLE_ROE_EXPORT_VIEW=РОЕ: Расписание
AIRTABLE_BIBLE_READERS_EXPORT_VIEW=Чтецы: Расписание
```

### Client Factory Integration
The AirtableClientFactory creates table-specific clients using configuration:

```python
# Usage in service layer
factory = AirtableClientFactory(settings.database)
client = factory.create_client("bible_readers")  # or "roe" or "participants"
```

### Multi-Table Repository Testing
- **Integration Tests**: 4 comprehensive tests validating multi-table coordination
- **Client Isolation**: Repositories use separate clients without connection conflicts
- **Factory Pattern**: Proper dependency injection with AirtableClientFactory
- **Test Coverage**: 100% coverage for multi-table integration scenarios

## Floor Discovery Integration (2025-01-20)

### Floor Field Configuration
**Field Name**: Floor
**Field ID**: `fldlzG1sVg01hsy2g`
**Type**: Number or Text (Union[int, str] support)
**Usage**: Used by `get_available_floors()` backend service for floor discovery

### API Optimization
- **Selective Field Retrieval**: Floor discovery only fetches floor field data to minimize API payload
- **Field Mapping**: Uses `AirtableFieldMapping.get_airtable_field_name("floor")` for internal-to-Airtable field name conversion
- **Data Processing**: Filters out None/empty values, converts to integers, deduplicates and sorts ascending

### Caching Implementation
**Cache Strategy**: Module-level in-memory cache with TTL cleanup
**Cache Key Format**: `f"{base_id}:{table_identifier}"`
**TTL**: 300 seconds (5 minutes)
**Storage**: `Dict[str, Tuple[float, List[int]]]` mapping cache keys to (timestamp, floors)

### Error Handling
- **API Failures**: Return empty list with warning logs, never crash user flows
- **Timeouts**: 10-second timeout with graceful fallback to empty list
- **Rate Limiting**: Built into Airtable client (5 requests/second)
- **Cache Persistence**: Cache persists across service factory calls for efficiency

## View-Aligned Export Configuration (Added 2025-09-27)

### Overview
The bot now supports view-aligned exports that leverage specific Airtable views to maintain exact column ordering and field structure. This ensures exported CSV files match operational dashboards and prevents schema drift.

### Configured Views
The following Airtable views are used for exports:

#### Participants View (Кандидаты)
- **Environment Variable**: `AIRTABLE_PARTICIPANT_EXPORT_VIEW`
- **Default Value**: `Кандидаты`
- **Purpose**: Candidate participant exports with view-defined column ordering
- **Features**:
  - Maintains exact Airtable view column order
  - Includes sequential line numbers as first column
  - Supports graceful fallback when view unavailable

#### ROE View (РОЕ: Расписание)
- **Environment Variable**: `AIRTABLE_ROE_EXPORT_VIEW`
- **Default Value**: `РОЕ: Расписание`
- **Purpose**: ROE session data exports with presenter information
- **Features**:
  - View-aligned column structure with participant hydration
  - Linked participant names resolved from IDs
  - Sequential line numbering for easy reference

#### Bible Readers View (Чтецы: Расписание)
- **Environment Variable**: `AIRTABLE_BIBLE_READERS_EXPORT_VIEW`
- **Default Value**: `Чтецы: Расписание`
- **Purpose**: Bible reading assignment exports with participant details
- **Features**:
  - View-defined field ordering preserved
  - Participant name hydration for linked records
  - Line numbers maintained for counting and reference

### Implementation Features

#### Repository Layer Support
All repository implementations include `list_view_records(view_name: str)` method:
- Returns raw Airtable view records preserving field order
- Supports all three data types (Participants, ROE, Bible Readers)
- Maintains exact view structure for export alignment

#### Export Service Integration
Export services leverage view-based data retrieval:
- **Header Extraction**: Column headers derived from actual view data
- **Column Order Preservation**: Maintains exact Airtable view ordering
- **Participant Hydration**: Linked participant IDs resolved to names
- **Fallback Logic**: Graceful degradation when views unavailable

#### Configuration Management
View names are configurable via environment variables:
- **Cyrillic Support**: Russian view names properly handled
- **Validation**: View names validated at startup
- **Fallback Handling**: Automatic fallback to repository filtering when views not found

### Error Handling and Resilience

#### View Unavailability
- **Detection**: 422 VIEW_NAME_NOT_FOUND errors automatically detected
- **Fallback**: Seamless transition to repository-based filtering
- **User Experience**: Transparent fallback maintains export functionality
- **Logging**: Clear warnings logged for operational awareness

#### Export Reliability
- **Error Recovery**: Comprehensive retry logic for transient failures
- **Resource Management**: Automatic cleanup prevents file accumulation
- **Progress Tracking**: Real-time progress updates during exports
- **Line Number Consistency**: Sequential numbering preserved across all export methods
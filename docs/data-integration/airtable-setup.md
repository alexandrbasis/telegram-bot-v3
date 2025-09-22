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
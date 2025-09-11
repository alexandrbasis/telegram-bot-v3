# Airtable Setup

# Airtable Configuration and Setup

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

*Additional Airtable configuration and setup instructions will be documented here.*
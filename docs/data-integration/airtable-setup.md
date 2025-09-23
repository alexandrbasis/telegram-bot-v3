# Airtable Setup

# Airtable Configuration and Setup

## Multi-Table Configuration (Added 2025-01-21)

### Supported Tables
The application now supports four Airtable tables with dedicated repository implementations:

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

#### BotAccessRequests Table
- **Table Name**: BotAccessRequests
- **Table ID**: `tblQWWEcHx9sfhsgN`
- **Repository**: AirtableUserAccessRepo
- **Primary Use**: Bot access approval workflow and user access management
- **Field Mapping Helper**: `src/config/field_mappings.py` (BotAccessRequestsFieldMapping)
- **Views**: Grid view (`viwVDrguxKWbRS9Xz`) for admin queue filtered by Status = Pending

### Environment Variable Configuration
```bash
# Base configuration (shared across all tables)
AIRTABLE_API_KEY=your_api_key_here
AIRTABLE_BASE_ID=appRp7Vby2JMzN0mC

# Participants table (existing)
AIRTABLE_TABLE_NAME=Participants
AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy

# BibleReaders table
AIRTABLE_BIBLE_READERS_TABLE_NAME=BibleReaders
AIRTABLE_BIBLE_READERS_TABLE_ID=tblGEnSfpPOuPLXcm

# ROE table
AIRTABLE_ROE_TABLE_NAME=ROE
AIRTABLE_ROE_TABLE_ID=tbl0j8bcgkV3lVAdc

# BotAccessRequests table (access approval workflow)
AIRTABLE_ACCESS_REQUESTS_TABLE_NAME=BotAccessRequests
AIRTABLE_ACCESS_REQUESTS_TABLE_ID=tblQWWEcHx9sfhsgN
```

### Client Factory Integration
The AirtableClientFactory creates table-specific clients using configuration:

```python
# Usage in service layer
factory = AirtableClientFactory(settings.database)
client = factory.create_client("bible_readers")  # or "roe", "participants", "access_requests"
```

### Multi-Table Repository Testing
- **Integration Tests**: Comprehensive tests validating multi-table coordination including access requests workflow
- **Client Isolation**: Repositories use separate clients without connection conflicts
- **Factory Pattern**: Proper dependency injection with AirtableClientFactory
- **Test Coverage**: 100% coverage for multi-table integration scenarios including access approval workflow
- **Access Request Testing**: Dedicated test suite for bot access approval workflow with 62 passing tests

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

## Bot Access Requests Schema

### Table Structure
**Table Name**: BotAccessRequests
**Table ID**: `tblQWWEcHx9sfhsgN`
**Primary View**: Grid view (`viwVDrguxKWbRS9Xz`) filtered to show pending requests

### Field Schema

| Field Name | Field ID | Type | Description | Default |
|------------|----------|------|-------------|----------|
| TelegramUserId | fldeiF3gxg4fZMirc | Number (Integer) | Primary key storing Telegram user ID for lookup and uniqueness enforcement | Required |
| TelegramUsername | fld1RzNGWTGl8fSE4 | Single line text | Telegram username captured without @ prefix; optional if user has none | Optional |
| Status | fldcuRa8qeUDKY3hN | Single select | Tracks current request state (Pending, Approved, Denied) | Pending |
| AccessLevel | fldRBCoHwrJ87hdjr | Single select | Effective permissions granted after approval (VIEWER, COORDINATOR, ADMIN) | VIEWER |

### Views and Indexing
- **Default View**: Grid view filtered to `Status = Pending` sorted by `TelegramUserId` ascending for admin queue
- **Secondary View**: Filtered to `Status = Approved` for quick roster of active users
- **Admin Interface**: Uses default view for paginated request review in `/requests` command

### Integration with Access Control
- **Repository**: `src/data/airtable/airtable_user_access_repo.py`
- **Service**: `src/services/access_request_service.py`
- **Field Mapping**: `src/config/field_mappings.py` (BotAccessRequestsFieldMapping class)
- **Bot Handlers**: `src/bot/handlers/auth_handlers.py` and `src/bot/handlers/admin_handlers.py`

### Usage in Access Approval Workflow
```python
# Repository operations
user_access_repo = AirtableUserAccessRepo(client)

# Create new access request
request = UserAccessRequest(
    telegram_user_id=user_id,
    telegram_username=username,
    status=AccessRequestStatus.PENDING,
    access_level=AccessLevel.VIEWER
)
await user_access_repo.create(request)

# Admin approval workflow
pending_requests = await user_access_repo.get_by_status(AccessRequestStatus.PENDING)
for request in pending_requests:
    # Admin reviews and approves/denies via /requests command
    await user_access_repo.approve(request.id, admin_user_id)
```

### Error Handling
- **API Failures**: Return empty list with warning logs, never crash user flows
- **Timeouts**: 10-second timeout with graceful fallback to empty list
- **Rate Limiting**: Built into Airtable client (5 requests/second)
- **Cache Persistence**: Cache persists across service factory calls for efficiency
- **Access Request Failures**: Comprehensive error handling for approval workflow with retry mechanisms
- **Notification Failures**: Robust retry logic with exponential backoff for admin and user notifications
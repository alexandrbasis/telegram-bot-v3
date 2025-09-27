# Configuration

## Environment Variables

### Required Variables

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot API token from @BotFather | `1234567890:ABCDEF...` | None |
| `AIRTABLE_API_KEY` | Airtable personal access token | `patABC123...` | None |
| `AIRTABLE_BASE_ID` | Airtable base identifier | `appRp7Vby2JMzN0mC` | `appRp7Vby2JMzN0mC` |

### Multi-Table Configuration Variables (Added 2025-01-21)

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `AIRTABLE_TABLE_NAME` | Participants table name | `Participants` | `Participants` |
| `AIRTABLE_TABLE_ID` | Participants table identifier | `tbl8ivwOdAUvMi3Jy` | `tbl8ivwOdAUvMi3Jy` |
| `AIRTABLE_BIBLE_READERS_TABLE_NAME` | BibleReaders table name | `BibleReaders` | `BibleReaders` |
| `AIRTABLE_BIBLE_READERS_TABLE_ID` | BibleReaders table identifier | `tblGEnSfpPOuPLXcm` | `tblGEnSfpPOuPLXcm` |
| `AIRTABLE_ROE_TABLE_NAME` | ROE table name | `ROE` | `ROE` |
| `AIRTABLE_ROE_TABLE_ID` | ROE table identifier | `tbl0j8bcgkV3lVAdc` | `tbl0j8bcgkV3lVAdc` |

### View-Aligned Export Configuration Variables (Added 2025-09-27)

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `AIRTABLE_PARTICIPANT_EXPORT_VIEW` | Airtable view name for participant exports | `Кандидаты` | `Кандидаты` |
| `AIRTABLE_ROE_EXPORT_VIEW` | Airtable view name for ROE exports | `РОЕ: Расписание` | `РОЕ: Расписание` |
| `AIRTABLE_BIBLE_READERS_EXPORT_VIEW` | Airtable view name for Bible Readers exports | `Чтецы: Расписание` | `Чтецы: Расписание` |

| `LOG_LEVEL` | Logging level | `INFO`, `DEBUG`, `WARNING` | `INFO` |
| `ENVIRONMENT` | Runtime environment | `development`, `production` | `development` |
| `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES` | Conversation timeout in minutes | `30`, `60` | `30` |
| `TELEGRAM_ADMIN_IDS` | Comma-separated admin user IDs | `123456789,987654321` | None |
| `TELEGRAM_COORDINATOR_IDS` | Comma-separated coordinator user IDs | `555666777,444333222` | None |
| `TELEGRAM_VIEWER_IDS` | Comma-separated viewer user IDs | `111222333,999888777` | None |

### Optional Variables

### Feature Flags

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `ENABLE_SCHEDULE_FEATURE` | Enables `/schedule` command and handlers | `true` | `false` |

Set `ENABLE_SCHEDULE_FEATURE=true` to register the schedule command and callbacks. When disabled, the schedule feature is not available in production.

## Telegram Settings

### Conversation Timeout

The bot automatically handles inactive conversations to prevent users from getting stuck in stale conversation states.

- **Environment Variable**: `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES`
- **Default Value**: 30 minutes
- **Valid Range**: 1-1440 minutes (1 minute to 24 hours)
- **Behavior**: After the specified timeout period, inactive conversations are automatically terminated
- **User Experience**: Users receive "Сессия истекла, начните заново" (Session expired, start again) message with main menu recovery button

**Configuration Examples:**
```bash
# Short timeout for development
TELEGRAM_CONVERSATION_TIMEOUT_MINUTES=5

# Standard timeout for production
TELEGRAM_CONVERSATION_TIMEOUT_MINUTES=30

# Extended timeout for complex operations
TELEGRAM_CONVERSATION_TIMEOUT_MINUTES=60
```

### Role-Based Authorization System (Added 2025-09-24)

The bot implements a comprehensive three-tier role-based access control system with environment-based configuration.

#### Role Hierarchy
**Admin > Coordinator > Viewer** (roles inherit permissions from lower tiers)

- **Admin**: Full access to all functionality including exports and sensitive participant data
- **Coordinator**: Access to participant data with some restrictions (no financial/payment info)
- **Viewer**: Limited access with strict data filtering (no PII, contact info, or sensitive data)

#### Environment Configuration

**Role-Based User ID Variables:**
- **TELEGRAM_ADMIN_IDS**: Comma-separated list of admin user IDs
- **TELEGRAM_COORDINATOR_IDS**: Comma-separated list of coordinator user IDs
- **TELEGRAM_VIEWER_IDS**: Comma-separated list of viewer user IDs

**Configuration Examples:**
```bash
# Complete role-based configuration
TELEGRAM_ADMIN_IDS=123456789,987654321
TELEGRAM_COORDINATOR_IDS=555666777,444333222,333444555
TELEGRAM_VIEWER_IDS=111222333,999888777,777666555

# Single user per role
TELEGRAM_ADMIN_IDS=123456789
TELEGRAM_COORDINATOR_IDS=555666777
TELEGRAM_VIEWER_IDS=111222333

# Mixed configuration (some roles empty)
TELEGRAM_ADMIN_IDS=123456789,987654321
TELEGRAM_COORDINATOR_IDS=555666777
# No viewers configured - TELEGRAM_VIEWER_IDS can be omitted
```

#### Authorization Utilities

**Core Functions** (`src/utils/auth_utils.py`):
- **`get_user_role(user_id, settings)`**: Returns highest role for a user ("admin", "coordinator", "viewer", or None)
- **`is_admin_user(user_id, settings)`**: Checks admin access (existing function, maintained for compatibility)
- **`is_coordinator_user(user_id, settings)`**: Checks coordinator or above access
- **`is_viewer_user(user_id, settings)`**: Checks viewer or above access (any authorized user)

**Access Control Middleware** (`src/utils/access_control.py`):
- **`@require_admin()`**: Decorator for admin-only handlers
- **`@require_coordinator_or_above()`**: Decorator for coordinator/admin handlers
- **`@require_viewer_or_above()`**: Decorator for any authorized user handlers
- **`@require_role(roles)`**: Flexible decorator accepting single role or role list

#### Performance & Security Features

**Caching System:**
- **Performance**: Role resolution cached with 5-minute TTL for <50ms response times
- **Cache Invalidation**: Manual cache clearing via `invalidate_role_cache()` for testing
- **Memory Efficient**: Module-level cache prevents memory leaks

**Security Features:**
- **Type Safety**: Handles Union[int, str, None] user ID types with robust validation
- **Privacy Compliance**: User IDs hashed in authorization logs to protect privacy
- **Secure by Default**: Unknown roles default to viewer-level access
- **Input Validation**: Comprehensive validation with clear error messages

**Data Filtering** (`src/utils/participant_filter.py`):
- **Role-Based Filtering**: `filter_participants_by_role(participants, user_role)` applies appropriate restrictions
- **PII Protection**: Viewers cannot access phone, email, contact information
- **Financial Data Protection**: Coordinators cannot access payment amounts or financial data
- **Field-Level Security**: Granular control over which fields each role can access

#### Integration Examples

**Handler Integration:**
```python
from src.utils.auth_utils import get_user_role
from src.utils.participant_filter import filter_participants_by_role

async def search_handler(update, context):
    user_id = update.effective_user.id
    user_role = get_user_role(user_id, get_settings())

    # Get search results with role-based filtering
    participants = await repo.find_by_name(query, user_role=user_role)
    filtered_participants = filter_participants_by_role(participants, user_role)
```

**Decorator Usage:**
```python
from src.utils.access_control import require_admin, require_coordinator_or_above

@require_admin()
async def export_handler(update, context):
    # Admin-only export functionality
    pass

@require_coordinator_or_above()
async def participant_details_handler(update, context):
    # Coordinator/admin access to detailed participant info
    pass
```

### Multi-Table Configuration

The bot now supports multi-table data management with separate configuration for each table:

**Configuration Examples:**
```bash
# Complete multi-table configuration
AIRTABLE_API_KEY=patYourApiKeyHere
AIRTABLE_BASE_ID=appRp7Vby2JMzN0mC

# Participants table (primary)
AIRTABLE_TABLE_NAME=Participants
AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy

# BibleReaders table
AIRTABLE_BIBLE_READERS_TABLE_NAME=BibleReaders
AIRTABLE_BIBLE_READERS_TABLE_ID=tblGEnSfpPOuPLXcm

# ROE table
AIRTABLE_ROE_TABLE_NAME=ROE
AIRTABLE_ROE_TABLE_ID=tbl0j8bcgkV3lVAdc
```

**Factory Pattern Usage:**
```python
# Create table-specific clients
from src.config.settings import get_database_settings, Settings
from src.data.airtable.airtable_client_factory import AirtableClientFactory

settings = get_database_settings()
factory = AirtableClientFactory(settings)

# Get clients for different tables
participants_client = factory.create_client("participants")
bible_readers_client = factory.create_client("bible_readers")
roe_client = factory.create_client("roe")

# Enhanced Settings API (2025-09-22)
# Settings.get_airtable_config() now supports table_type parameter
from src.config.settings import Settings
app_settings = Settings()
participants_config = app_settings.get_airtable_config("participants")
bible_readers_config = app_settings.get_airtable_config("bible_readers")
roe_config = app_settings.get_airtable_config("roe")
```

**Repository Implementation Integration:**
```python
# Use repositories with factory-created clients
from src.data.airtable.airtable_bible_readers_repo import AirtableBibleReadersRepo
from src.data.airtable.airtable_roe_repo import AirtableROERepo

# Create repositories with dependency injection
bible_readers_repo = AirtableBibleReadersRepo(factory.create_client("bible_readers"))
roe_repo = AirtableROERepo(factory.create_client("roe"))

# Repositories provide full CRUD operations
bible_reader = await bible_readers_repo.get_by_id("rec123...")
roe_sessions = await roe_repo.get_by_roista_id("rec456...")
```

### Validation Rules

- **Timeout Minutes**: Must be between 1 and 1440 minutes
- **Bot Token**: Must be provided for bot functionality
- **Airtable API Key**: Required for data persistence
- **Environment**: Validates against known environments
- **Role User IDs**: Must be valid integer user IDs if provided (TELEGRAM_ADMIN_IDS, TELEGRAM_COORDINATOR_IDS, TELEGRAM_VIEWER_IDS)
- **Role Hierarchy**: Enforced at runtime - users with multiple roles receive highest role privileges
- **Multi-Table Configuration**: All table configurations validated with defaults and error cases
- **Table Type Validation**: Factory validates supported table types (participants, bible_readers, roe)
- **Field Mapping Validation**: Each table has dedicated field mapping helpers with comprehensive field ID validation
- **Repository Pattern**: All repositories follow consistent interface patterns with async operations and proper error handling
- **View Name Validation**: Export view names must be valid Airtable view identifiers for view-aligned exports
- **Export View Configuration**: View names support Cyrillic characters for Russian Airtable interface alignment
- **View-Based Export Fallback**: System gracefully handles view unavailability with automatic fallback to repository filtering

## Configuration Loading

Configuration is loaded via dataclasses from environment variables with automatic validation at startup:

```python
# Settings validation occurs in __post_init__ methods
from src.config.settings import get_telegram_settings, get_database_settings

# Telegram settings
telegram_settings = get_telegram_settings()
print(f"Timeout: {telegram_settings.conversation_timeout_minutes} minutes")

# Database settings with multi-table support
db_settings = get_database_settings()
print(f"Base ID: {db_settings.base_id}")
print(f"Tables: {db_settings.table_name}, {db_settings.bible_readers_table_name}, {db_settings.roe_table_name}")

# Get table-specific configuration
participants_config = db_settings.to_airtable_config("participants")
bible_readers_config = db_settings.to_airtable_config("bible_readers")
roe_config = db_settings.to_airtable_config("roe")

# Access view-aligned export configuration (2025-09-27)
participant_export_view = settings.database.participant_export_view  # "Кандидаты"
roe_export_view = settings.database.roe_export_view                  # "РОЕ: Расписание"
bible_readers_export_view = settings.database.bible_readers_export_view  # "Чтецы: Расписание"
```

### Error Handling

- **Missing Required Variables**: Application fails to start with clear error messages
- **Invalid Values**: Validation errors displayed with acceptable value ranges
- **Runtime Changes**: Some settings can be updated via environment variables without restart
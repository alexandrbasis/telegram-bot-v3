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
| `LOG_LEVEL` | Logging level | `INFO`, `DEBUG`, `WARNING` | `INFO` |
| `ENVIRONMENT` | Runtime environment | `development`, `production` | `development` |
| `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES` | Conversation timeout in minutes | `30`, `60` | `30` |
| `ADMIN_USER_IDS` | Comma-separated admin user IDs | `123456789,987654321` | None |

### Optional Variables

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

### Admin Authentication

The bot includes admin-only features that require proper user authorization. Admin access is controlled through environment configuration.

- **Environment Variable**: `ADMIN_USER_IDS`
- **Format**: Comma-separated list of Telegram user IDs
- **Example**: `123456789,987654321`
- **Usage**: Controls access to admin features like CSV export functionality

**Configuration Examples:**
```bash
# Single admin user
ADMIN_USER_IDS=123456789

# Multiple admin users
ADMIN_USER_IDS=123456789,987654321,555666777
```

**Authentication Utilities:**
- **Function**: `is_admin_user(user_id, settings)` in `src/utils/auth_utils.py`
- **Type Safety**: Handles Union[int, str, None] user ID types with robust validation
- **Logging**: Comprehensive logging for authentication attempts and failures
- **Integration**: Uses existing settings configuration for admin user list

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
- **Admin User IDs**: Must be valid integer user IDs if provided
- **Multi-Table Configuration**: All table configurations validated with defaults and error cases
- **Table Type Validation**: Factory validates supported table types (participants, bible_readers, roe)
- **Field Mapping Validation**: Each table has dedicated field mapping helpers with comprehensive field ID validation
- **Repository Pattern**: All repositories follow consistent interface patterns with async operations and proper error handling

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
```

### Error Handling

- **Missing Required Variables**: Application fails to start with clear error messages
- **Invalid Values**: Validation errors displayed with acceptable value ranges
- **Runtime Changes**: Some settings can be updated via environment variables without restart
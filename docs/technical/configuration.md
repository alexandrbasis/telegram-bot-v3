# Configuration

## Environment Variables

### Required Variables

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot API token from @BotFather | `1234567890:ABCDEF...` | None |
| `AIRTABLE_API_KEY` | Airtable personal access token | `patABC123...` | None |
| `AIRTABLE_BASE_ID` | Airtable base identifier | `appRp7Vby2JMzN0mC` | `appRp7Vby2JMzN0mC` |

### Optional Variables

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `AIRTABLE_TABLE_NAME` | Table name in Airtable base | `Participants` | `Participants` |
| `AIRTABLE_TABLE_ID` | Table identifier | `tbl8ivwOdAUvMi3Jy` | `tbl8ivwOdAUvMi3Jy` |
| `LOG_LEVEL` | Logging level | `INFO`, `DEBUG`, `WARNING` | `INFO` |
| `ENVIRONMENT` | Runtime environment | `development`, `production` | `development` |
| `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES` | Conversation timeout in minutes | `30`, `60` | `30` |

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

### Validation Rules

- **Timeout Minutes**: Must be between 1 and 1440 minutes
- **Bot Token**: Must be provided for bot functionality
- **Airtable API Key**: Required for data persistence
- **Environment**: Validates against known environments

## Configuration Loading

Configuration is loaded via dataclasses from environment variables with automatic validation at startup:

```python
# Settings validation occurs in __post_init__ methods
from src.config.settings import get_telegram_settings

settings = get_telegram_settings()
print(f"Timeout: {settings.conversation_timeout_minutes} minutes")
```

### Error Handling

- **Missing Required Variables**: Application fails to start with clear error messages
- **Invalid Values**: Validation errors displayed with acceptable value ranges
- **Runtime Changes**: Some settings can be updated via environment variables without restart
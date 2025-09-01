# Configuration

## Overview

Centralized configuration system using dataclasses and environment variables for all application settings including Telegram bot, Airtable integration, logging, and file logging.

## Configuration Architecture

### Settings Structure
Configuration is organized into specialized dataclasses in `src/config/settings.py`:

- `DatabaseSettings`: Airtable API configuration
- `TelegramSettings`: Bot token and behavior settings  
- `LoggingSettings`: Console and file logging configuration
- `ApplicationSettings`: Environment and feature flags

### Environment Variable Loading
All settings load from environment variables with sensible defaults:

```python
@dataclass
class Settings:
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    telegram: TelegramSettings = field(default_factory=TelegramSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    application: ApplicationSettings = field(default_factory=ApplicationSettings)
```

## File Logging Configuration

### Overview
Persistent file-based logging system with organized directory structure and configurable behavior.

**Implementation**: Added in 2025-08-31 as part of LoggingSettings extension

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FILE_LOGGING_ENABLED` | `true` | Enable/disable file logging system |
| `LOG_DIR` | `logs` | Base directory for log files |
| `LOG_MAX_BYTES` | `10485760` | Maximum log file size (10MB) |
| `LOG_BACKUP_COUNT` | `5` | Number of backup files to retain |

### Configuration Properties

```python
@dataclass
class LoggingSettings:
    # Existing console logging settings
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File logging settings (New - 2025-08-31)
    file_logging_enabled: bool = True
    log_dir: str = "logs"
    log_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
```

### Directory Structure
File logging creates organized subdirectories:

```
logs/
├── application/        # General application logs
├── user-interactions/  # User interaction specific logs  
├── errors/            # Error and exception logs
└── archived/          # Rotated/archived log files
```

### File Logging Integration

The configuration system provides a dedicated method for file logging setup:

```python
def get_file_logging_config(self) -> 'FileLoggingConfig':
    """Get file logging configuration from current settings."""
    return FileLoggingConfig(
        enabled=self.logging.file_logging_enabled,
        log_dir=self.logging.log_dir,
        max_bytes=self.logging.log_max_bytes,
        backup_count=self.logging.log_backup_count,
        log_level=self.logging.level
    )
```

## Required Environment Variables

### Telegram Configuration
```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Optional
TELEGRAM_TIMEOUT=30
```

### Airtable Configuration  
```bash
# Required
AIRTABLE_API_KEY=your_personal_access_token
AIRTABLE_BASE_ID=appRp7Vby2JMzN0mC  # Default base

# Optional
AIRTABLE_TABLE_NAME=Participants     # Default table name
AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy # Default table ID
```

### Logging Configuration
```bash
# Optional - Console logging
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Optional - File logging (New - 2025-08-31)
FILE_LOGGING_ENABLED=true
LOG_DIR=logs
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

### Application Configuration
```bash
# Optional
ENVIRONMENT=development
DEBUG=false
```

## Configuration Validation

### Startup Validation
All configuration validation happens at application startup via dataclass `__post_init__` methods:

```python
def __post_init__(self):
    """Validate configuration after initialization."""
    if not self.api_key:
        raise ValueError("AIRTABLE_API_KEY is required")
    if not self.base_id:
        raise ValueError("AIRTABLE_BASE_ID is required")
```

### File Logging Validation
The file logging configuration includes specific validation:

```python
def __post_init__(self):
    """Validate file logging configuration."""
    if self.max_bytes <= 0:
        raise ValueError("LOG_MAX_BYTES must be positive")
    if self.backup_count < 0:
        raise ValueError("LOG_BACKUP_COUNT must be non-negative")
    if not self.log_dir.strip():
        raise ValueError("LOG_DIR cannot be empty")
```

## Configuration Usage

### Loading Settings
```python
from src.config.settings import Settings

# Load configuration from environment
settings = Settings()

# Access specific settings
telegram_token = settings.telegram.token
log_level = settings.logging.level
file_logging_enabled = settings.logging.file_logging_enabled
```

### File Logging Integration
```python
from src.config.settings import Settings
from src.services.file_logging_service import FileLoggingService

settings = Settings()
file_logging_config = settings.get_file_logging_config()
file_logging_service = FileLoggingService(file_logging_config)
file_logging_service.setup_file_logging()
```

## Development vs Production

### Development Environment
- Console logging at INFO level
- File logging enabled by default
- Debug-friendly log formats

### Production Environment  
- Console logging at WARNING level
- File logging highly recommended
- Structured log formats for parsing
- Log rotation to prevent disk space issues

## Configuration Testing

### Test Coverage
File logging configuration testing included in `tests/unit/test_config/test_settings.py`:

- Default value validation
- Environment variable loading
- Configuration validation
- Error handling scenarios
- FileLoggingConfig creation and integration

### Example Test
```python
def test_file_logging_settings_from_environment():
    """Test file logging settings load correctly from environment."""
    with patch.dict(os.environ, {
        'FILE_LOGGING_ENABLED': 'false',
        'LOG_DIR': 'custom_logs',
        'LOG_MAX_BYTES': '5242880',  # 5MB
        'LOG_BACKUP_COUNT': '3'
    }):
        settings = Settings()
        assert not settings.logging.file_logging_enabled
        assert settings.logging.log_dir == "custom_logs"
        assert settings.logging.log_max_bytes == 5242880
        assert settings.logging.log_backup_count == 3
```
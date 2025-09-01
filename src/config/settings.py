"""
Configuration settings for the Tres Dias Telegram Bot.

This module provides centralized configuration management using environment
variables and default values for database connections, API settings, and 
application behavior.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path

from src.data.airtable.airtable_client import AirtableConfig


@dataclass
class DatabaseSettings:
    """Database connection and configuration settings."""
    
    # Airtable API Configuration
    airtable_api_key: str = field(default_factory=lambda: os.getenv('AIRTABLE_API_KEY', ''))
    airtable_base_id: str = field(default_factory=lambda: os.getenv('AIRTABLE_BASE_ID', 'appRp7Vby2JMzN0mC'))
    airtable_table_name: str = field(default_factory=lambda: os.getenv('AIRTABLE_TABLE_NAME', 'Participants'))
    airtable_table_id: str = field(default_factory=lambda: os.getenv('AIRTABLE_TABLE_ID', 'tbl8ivwOdAUvMi3Jy'))
    
    # Rate limiting and performance
    rate_limit_per_second: int = field(default_factory=lambda: int(os.getenv('AIRTABLE_RATE_LIMIT', '5')))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv('AIRTABLE_TIMEOUT', '30')))
    max_retries: int = field(default_factory=lambda: int(os.getenv('AIRTABLE_MAX_RETRIES', '3')))
    retry_delay_seconds: float = field(default_factory=lambda: float(os.getenv('AIRTABLE_RETRY_DELAY', '1.0')))
    
    # Connection pool settings
    max_connections: int = field(default_factory=lambda: int(os.getenv('DB_MAX_CONNECTIONS', '10')))
    connection_timeout: int = field(default_factory=lambda: int(os.getenv('DB_CONNECTION_TIMEOUT', '60')))
    
    def validate(self) -> None:
        """
        Validate database settings and raise errors for missing required values.
        
        Raises:
            ValueError: If required settings are missing or invalid
        """
        if not self.airtable_api_key:
            raise ValueError("AIRTABLE_API_KEY environment variable is required")
        
        if not self.airtable_base_id:
            raise ValueError("AIRTABLE_BASE_ID environment variable is required")
        
        if not self.airtable_table_name:
            raise ValueError("AIRTABLE_TABLE_NAME must be specified")
        
        if not self.airtable_table_id:
            raise ValueError("AIRTABLE_TABLE_ID must be specified")
        
        if self.rate_limit_per_second <= 0 or self.rate_limit_per_second > 100:
            raise ValueError("Rate limit must be between 1 and 100 requests per second")
        
        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
    
    def to_airtable_config(self) -> AirtableConfig:
        """
        Convert database settings to AirtableConfig instance.
        
        Returns:
            AirtableConfig instance with current settings
        """
        return AirtableConfig(
            api_key=self.airtable_api_key,
            base_id=self.airtable_base_id,
            table_name=self.airtable_table_name,
            table_id=self.airtable_table_id,
            rate_limit_per_second=self.rate_limit_per_second,
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
            retry_delay_seconds=self.retry_delay_seconds
        )


@dataclass  
class TelegramSettings:
    """Telegram Bot API configuration settings."""
    
    bot_token: str = field(default_factory=lambda: os.getenv('TELEGRAM_BOT_TOKEN', ''))
    webhook_url: Optional[str] = field(default_factory=lambda: os.getenv('TELEGRAM_WEBHOOK_URL'))
    webhook_secret: Optional[str] = field(default_factory=lambda: os.getenv('TELEGRAM_WEBHOOK_SECRET'))
    
    # Bot behavior settings
    max_message_length: int = field(default_factory=lambda: int(os.getenv('TELEGRAM_MAX_MESSAGE_LENGTH', '4096')))
    command_timeout: int = field(default_factory=lambda: int(os.getenv('TELEGRAM_COMMAND_TIMEOUT', '30')))
    
    # Admin settings
    admin_user_ids: list[int] = field(default_factory=lambda: [
        int(uid.strip()) for uid in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',') if uid.strip()
    ])
    
    def validate(self) -> None:
        """
        Validate Telegram settings.
        
        Raises:
            ValueError: If required settings are missing or invalid
        """
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        if self.max_message_length <= 0 or self.max_message_length > 4096:
            raise ValueError("Max message length must be between 1 and 4096 characters")
        
        if self.command_timeout <= 0:
            raise ValueError("Command timeout must be positive")


@dataclass
class LoggingSettings:
    """Logging configuration settings."""
    
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    log_format: str = field(default_factory=lambda: os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log_file: Optional[str] = field(default_factory=lambda: os.getenv('LOG_FILE'))
    
    # Specific logger levels
    airtable_log_level: str = field(default_factory=lambda: os.getenv('AIRTABLE_LOG_LEVEL', 'INFO'))
    telegram_log_level: str = field(default_factory=lambda: os.getenv('TELEGRAM_LOG_LEVEL', 'INFO'))
    
    # User interaction logging settings
    enable_user_interaction_logging: bool = field(default_factory=lambda: os.getenv('ENABLE_USER_INTERACTION_LOGGING', 'true').lower() == 'true')
    user_interaction_log_level: str = field(default_factory=lambda: os.getenv('USER_INTERACTION_LOG_LEVEL', 'INFO'))
    
    # File logging settings
    enable_file_logging: bool = field(default_factory=lambda: os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true')
    file_log_dir: Path = field(default_factory=lambda: Path(os.getenv('FILE_LOG_DIR', 'logs')))
    file_max_size: int = field(default_factory=lambda: int(os.getenv('FILE_LOG_MAX_SIZE', str(10 * 1024 * 1024))))  # 10MB default
    file_backup_count: int = field(default_factory=lambda: int(os.getenv('FILE_LOG_BACKUP_COUNT', '5')))
    
    def validate(self) -> None:
        """
        Validate logging settings.
        
        Raises:
            ValueError: If log levels are invalid
        """
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        
        if self.airtable_log_level.upper() not in valid_levels:
            raise ValueError(f"AIRTABLE_LOG_LEVEL must be one of {valid_levels}")
        
        if self.telegram_log_level.upper() not in valid_levels:
            raise ValueError(f"TELEGRAM_LOG_LEVEL must be one of {valid_levels}")
        
        if self.user_interaction_log_level.upper() not in valid_levels:
            raise ValueError(f"USER_INTERACTION_LOG_LEVEL must be one of {valid_levels}")
        
        # File logging validation
        if self.file_max_size <= 0:
            raise ValueError("file_max_size must be positive")
        
        if self.file_backup_count < 0:
            raise ValueError("file_backup_count cannot be negative")


@dataclass
class ApplicationSettings:
    """General application settings."""
    
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'false').lower() == 'true')
    
    # Feature flags
    enable_metrics: bool = field(default_factory=lambda: os.getenv('ENABLE_METRICS', 'true').lower() == 'true')
    enable_health_checks: bool = field(default_factory=lambda: os.getenv('ENABLE_HEALTH_CHECKS', 'true').lower() == 'true')
    
    # Performance settings  
    max_concurrent_operations: int = field(default_factory=lambda: int(os.getenv('MAX_CONCURRENT_OPERATIONS', '10')))
    operation_timeout: int = field(default_factory=lambda: int(os.getenv('OPERATION_TIMEOUT', '60')))
    
    def validate(self) -> None:
        """
        Validate application settings.
        
        Raises:
            ValueError: If settings are invalid
        """
        valid_environments = ['development', 'testing', 'staging', 'production']
        if self.environment not in valid_environments:
            raise ValueError(f"ENVIRONMENT must be one of {valid_environments}")
        
        if self.max_concurrent_operations <= 0:
            raise ValueError("Max concurrent operations must be positive")
        
        if self.operation_timeout <= 0:
            raise ValueError("Operation timeout must be positive")


@dataclass
class Settings:
    """
    Main settings container combining all configuration sections.
    
    Provides centralized access to all application settings with validation
    and environment variable loading.
    """
    
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    telegram: TelegramSettings = field(default_factory=TelegramSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    application: ApplicationSettings = field(default_factory=ApplicationSettings)
    
    def __post_init__(self) -> None:
        """Validate all settings after initialization."""
        self.validate_all()
    
    def validate_all(self) -> None:
        """
        Validate all configuration sections.
        
        Raises:
            ValueError: If any settings are invalid
        """
        self.database.validate()
        self.telegram.validate()
        self.logging.validate()
        self.application.validate()
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.application.environment == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.application.environment == 'production'
    
    def get_airtable_config(self) -> AirtableConfig:
        """
        Get Airtable configuration from database settings.
        
        Returns:
            AirtableConfig instance ready for use with AirtableClient
        """
        return self.database.to_airtable_config()
    
    def get_file_logging_config(self):
        """
        Get file logging configuration from logging settings.
        
        Returns:
            FileLoggingConfig instance ready for use with FileLoggingService
        """
        from src.services.file_logging_service import FileLoggingConfig
        
        return FileLoggingConfig(
            enabled=self.logging.enable_file_logging,
            log_dir=self.logging.file_log_dir,
            max_file_size=self.logging.file_max_size,
            backup_count=self.logging.file_backup_count,
            create_subdirs=True
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary format.
        
        Returns:
            Dictionary representation of all settings
        """
        return {
            'database': {
                'base_id': self.database.airtable_base_id,
                'table_name': self.database.airtable_table_name,
                'rate_limit': self.database.rate_limit_per_second,
                'timeout': self.database.timeout_seconds
            },
            'telegram': {
                'max_message_length': self.telegram.max_message_length,
                'command_timeout': self.telegram.command_timeout,
                'admin_count': len(self.telegram.admin_user_ids)
            },
            'logging': {
                'level': self.logging.log_level,
                'airtable_level': self.logging.airtable_log_level,
                'telegram_level': self.logging.telegram_log_level
            },
            'application': {
                'environment': self.application.environment,
                'debug': self.application.debug,
                'max_concurrent': self.application.max_concurrent_operations
            }
        }


def load_settings() -> Settings:
    """
    Load settings from environment variables with validation.
    
    Returns:
        Settings instance with all configuration loaded and validated
        
    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    return Settings()


def load_env_file(file_path: Optional[str] = None) -> None:
    """
    Load environment variables from .env file.
    
    Args:
        file_path: Path to .env file, defaults to .env in current directory
    """
    if file_path is None:
        file_path = '.env'
    
    env_path = Path(file_path)
    if not env_path.exists():
        return
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    if key and not os.getenv(key):
                        os.environ[key] = value


# Global settings instance - load once and reuse
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get global settings instance (singleton pattern).
    
    Returns:
        Settings instance, loading from environment on first call
        
    Raises:
        ValueError: If configuration is invalid
    """
    global _settings
    if _settings is None:
        # Try to load .env file first
        load_env_file()
        _settings = load_settings()
    return _settings


def reset_settings() -> None:
    """Reset global settings instance (useful for testing)."""
    global _settings
    _settings = None


# Convenience functions for common access patterns
def get_airtable_config() -> AirtableConfig:
    """Get Airtable configuration for client initialization."""
    return get_settings().get_airtable_config()


def get_database_settings() -> DatabaseSettings:
    """Get database-specific settings."""
    return get_settings().database


def get_telegram_settings() -> TelegramSettings:
    """Get Telegram-specific settings."""
    return get_settings().telegram


def is_debug_mode() -> bool:
    """Check if application is in debug mode."""
    return get_settings().application.debug


def is_production() -> bool:
    """Check if application is in production environment."""
    return get_settings().is_production()
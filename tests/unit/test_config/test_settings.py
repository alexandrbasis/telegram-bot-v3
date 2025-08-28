"""
Unit tests for configuration settings.

Tests cover:
- Environment variable loading and defaults
- Settings validation and error handling
- Configuration section functionality
- Settings conversion and serialization
"""

import pytest
import os
from unittest.mock import patch, mock_open

from src.config.settings import (
    DatabaseSettings,
    TelegramSettings, 
    LoggingSettings,
    ApplicationSettings,
    Settings,
    load_settings,
    load_env_file,
    get_settings,
    reset_settings
)
from src.data.airtable.airtable_client import AirtableConfig


class TestDatabaseTableID:
    """Test suite for Airtable Table ID configuration."""
    
    def test_default_table_id(self):
        """Test that default Table ID is set correctly."""
        # RED phase - this test will fail until we implement airtable_table_id
        
        with patch.dict(os.environ, {}, clear=True):
            settings = DatabaseSettings()
            
            # Should have the exact Table ID from task requirements
            assert hasattr(settings, 'airtable_table_id')
            assert settings.airtable_table_id == "tbl8ivwOdAUvMi3Jy"
    
    def test_environment_table_id_override(self):
        """Test that Table ID can be overridden via environment variable."""
        # RED phase - this test will fail until we implement AIRTABLE_TABLE_ID env var
        
        env_vars = {
            'AIRTABLE_TABLE_ID': 'tblCustomTableID123'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()
            
            assert settings.airtable_table_id == "tblCustomTableID123"
    
    def test_table_id_validation(self):
        """Test that Table ID is validated during settings validation."""
        # RED phase - this test will fail until we implement Table ID validation
        
        env_vars = {
            'AIRTABLE_API_KEY': 'valid_key',
            'AIRTABLE_BASE_ID': 'valid_base',
            'AIRTABLE_TABLE_ID': ''  # Empty Table ID should fail validation
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()
            
            with pytest.raises(ValueError) as exc_info:
                settings.validate()
            
            assert "AIRTABLE_TABLE_ID" in str(exc_info.value)
    
    def test_airtable_config_includes_table_id(self):
        """Test that AirtableConfig includes the Table ID."""
        # RED phase - this test will fail until we pass table_id to AirtableConfig
        
        env_vars = {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'AIRTABLE_TABLE_ID': 'tbl8ivwOdAUvMi3Jy'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()
            config = settings.to_airtable_config()
            
            # AirtableConfig should have table_id attribute
            assert hasattr(config, 'table_id')
            assert config.table_id == "tbl8ivwOdAUvMi3Jy"


class TestDatabaseSettings:
    """Test suite for DatabaseSettings functionality."""
    
    def test_default_values(self):
        """Test default values when environment variables are not set."""
        with patch.dict(os.environ, {}, clear=True):
            settings = DatabaseSettings()
            
            assert settings.airtable_api_key == ""
            assert settings.airtable_base_id == "appRp7Vby2JMzN0mC"
            assert settings.airtable_table_name == "Participants"
            assert settings.rate_limit_per_second == 5
            assert settings.timeout_seconds == 30
            assert settings.max_retries == 3
            assert settings.retry_delay_seconds == 1.0
    
    def test_environment_variable_loading(self):
        """Test loading values from environment variables."""
        env_vars = {
            'AIRTABLE_API_KEY': 'test_api_key',
            'AIRTABLE_BASE_ID': 'test_base_id',
            'AIRTABLE_TABLE_NAME': 'TestTable',
            'AIRTABLE_RATE_LIMIT': '10',
            'AIRTABLE_TIMEOUT': '60',
            'AIRTABLE_MAX_RETRIES': '5',
            'AIRTABLE_RETRY_DELAY': '2.0'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()
            
            assert settings.airtable_api_key == "test_api_key"
            assert settings.airtable_base_id == "test_base_id"
            assert settings.airtable_table_name == "TestTable"
            assert settings.rate_limit_per_second == 10
            assert settings.timeout_seconds == 60
            assert settings.max_retries == 5
            assert settings.retry_delay_seconds == 2.0
    
    def test_validation_success(self):
        """Test successful validation with valid settings."""
        env_vars = {
            'AIRTABLE_API_KEY': 'valid_key',
            'AIRTABLE_BASE_ID': 'valid_base'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()
            settings.validate()  # Should not raise
    
    def test_validation_missing_api_key(self):
        """Test validation failure when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            settings = DatabaseSettings()
            
            with pytest.raises(ValueError) as exc_info:
                settings.validate()
            
            assert "AIRTABLE_API_KEY" in str(exc_info.value)
    
    def test_validation_missing_base_id(self):
        """Test validation failure when base ID is missing."""
        env_vars = {'AIRTABLE_API_KEY': 'valid_key', 'AIRTABLE_BASE_ID': ''}
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()
            
            with pytest.raises(ValueError) as exc_info:
                settings.validate()
            
            assert "AIRTABLE_BASE_ID" in str(exc_info.value)
    
    def test_validation_invalid_rate_limit(self):
        """Test validation failure with invalid rate limit."""
        env_vars = {
            'AIRTABLE_API_KEY': 'valid_key',
            'AIRTABLE_BASE_ID': 'valid_base',
            'AIRTABLE_RATE_LIMIT': '0'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()
            
            with pytest.raises(ValueError) as exc_info:
                settings.validate()
            
            assert "Rate limit" in str(exc_info.value)
    
    def test_to_airtable_config(self):
        """Test conversion to AirtableConfig."""
        env_vars = {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'AIRTABLE_TABLE_NAME': 'TestTable',
            'AIRTABLE_RATE_LIMIT': '10'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()
            config = settings.to_airtable_config()
            
            assert isinstance(config, AirtableConfig)
            assert config.api_key == "test_key"
            assert config.base_id == "test_base"
            assert config.table_name == "TestTable"
            assert config.rate_limit_per_second == 10


class TestTelegramSettings:
    """Test suite for TelegramSettings functionality."""
    
    def test_default_values(self):
        """Test default values for Telegram settings."""
        with patch.dict(os.environ, {}, clear=True):
            settings = TelegramSettings()
            
            assert settings.bot_token == ""
            assert settings.webhook_url is None
            assert settings.webhook_secret is None
            assert settings.max_message_length == 4096
            assert settings.command_timeout == 30
            assert settings.admin_user_ids == []
    
    def test_environment_variable_loading(self):
        """Test loading Telegram settings from environment."""
        env_vars = {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'TELEGRAM_WEBHOOK_URL': 'https://example.com/webhook',
            'TELEGRAM_WEBHOOK_SECRET': 'secret',
            'TELEGRAM_MAX_MESSAGE_LENGTH': '2048',
            'TELEGRAM_COMMAND_TIMEOUT': '60',
            'TELEGRAM_ADMIN_IDS': '123456789,987654321'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()
            
            assert settings.bot_token == "test_token"
            assert settings.webhook_url == "https://example.com/webhook"
            assert settings.webhook_secret == "secret"
            assert settings.max_message_length == 2048
            assert settings.command_timeout == 60
            assert settings.admin_user_ids == [123456789, 987654321]
    
    def test_admin_ids_parsing(self):
        """Test parsing of admin user IDs from comma-separated string."""
        env_vars = {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'TELEGRAM_ADMIN_IDS': '111, 222, 333 '  # With spaces
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()
            
            assert settings.admin_user_ids == [111, 222, 333]
    
    def test_validation_missing_token(self):
        """Test validation failure when bot token is missing."""
        with patch.dict(os.environ, {}, clear=True):
            settings = TelegramSettings()
            
            with pytest.raises(ValueError) as exc_info:
                settings.validate()
            
            assert "TELEGRAM_BOT_TOKEN" in str(exc_info.value)
    
    def test_validation_invalid_message_length(self):
        """Test validation failure with invalid message length."""
        env_vars = {
            'TELEGRAM_BOT_TOKEN': 'valid_token',
            'TELEGRAM_MAX_MESSAGE_LENGTH': '5000'  # Too long
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()
            
            with pytest.raises(ValueError) as exc_info:
                settings.validate()
            
            assert "Max message length" in str(exc_info.value)


class TestLoggingSettings:
    """Test suite for LoggingSettings functionality."""
    
    def test_default_values(self):
        """Test default logging settings."""
        with patch.dict(os.environ, {}, clear=True):
            settings = LoggingSettings()
            
            assert settings.log_level == "INFO"
            assert settings.log_file is None
            assert settings.airtable_log_level == "INFO"
            assert settings.telegram_log_level == "INFO"
    
    def test_environment_variable_loading(self):
        """Test loading logging settings from environment."""
        env_vars = {
            'LOG_LEVEL': 'DEBUG',
            'LOG_FILE': '/var/log/bot.log',
            'AIRTABLE_LOG_LEVEL': 'WARNING',
            'TELEGRAM_LOG_LEVEL': 'ERROR'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = LoggingSettings()
            
            assert settings.log_level == "DEBUG"
            assert settings.log_file == "/var/log/bot.log"
            assert settings.airtable_log_level == "WARNING"
            assert settings.telegram_log_level == "ERROR"
    
    def test_validation_invalid_log_level(self):
        """Test validation failure with invalid log level."""
        env_vars = {'LOG_LEVEL': 'INVALID'}
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = LoggingSettings()
            
            with pytest.raises(ValueError) as exc_info:
                settings.validate()
            
            assert "LOG_LEVEL must be one of" in str(exc_info.value)


class TestApplicationSettings:
    """Test suite for ApplicationSettings functionality."""
    
    def test_default_values(self):
        """Test default application settings."""
        with patch.dict(os.environ, {}, clear=True):
            settings = ApplicationSettings()
            
            assert settings.environment == "development"
            assert settings.debug is False
            assert settings.enable_metrics is True
            assert settings.enable_health_checks is True
            assert settings.max_concurrent_operations == 10
            assert settings.operation_timeout == 60
    
    def test_environment_variable_loading(self):
        """Test loading application settings from environment."""
        env_vars = {
            'ENVIRONMENT': 'production',
            'DEBUG': 'true',
            'ENABLE_METRICS': 'false',
            'ENABLE_HEALTH_CHECKS': 'false',
            'MAX_CONCURRENT_OPERATIONS': '20',
            'OPERATION_TIMEOUT': '120'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = ApplicationSettings()
            
            assert settings.environment == "production"
            assert settings.debug is True
            assert settings.enable_metrics is False
            assert settings.enable_health_checks is False
            assert settings.max_concurrent_operations == 20
            assert settings.operation_timeout == 120
    
    def test_validation_invalid_environment(self):
        """Test validation failure with invalid environment."""
        env_vars = {'ENVIRONMENT': 'invalid_env'}
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = ApplicationSettings()
            
            with pytest.raises(ValueError) as exc_info:
                settings.validate()
            
            assert "ENVIRONMENT must be one of" in str(exc_info.value)


class TestSettings:
    """Test suite for main Settings container."""
    
    def test_initialization_with_validation(self):
        """Test that Settings initializes and validates all sections."""
        env_vars = {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'TELEGRAM_BOT_TOKEN': 'test_token'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            # Should initialize without errors
            assert isinstance(settings.database, DatabaseSettings)
            assert isinstance(settings.telegram, TelegramSettings)
            assert isinstance(settings.logging, LoggingSettings)
            assert isinstance(settings.application, ApplicationSettings)
    
    def test_initialization_validation_failure(self):
        """Test that Settings validation catches errors from subsections."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                Settings()  # Should fail due to missing required env vars
    
    def test_environment_detection(self):
        """Test environment detection methods."""
        env_vars = {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'TELEGRAM_BOT_TOKEN': 'test_token'
        }
        
        # Test development
        env_vars['ENVIRONMENT'] = 'development'
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.is_development() is True
            assert settings.is_production() is False
        
        # Test production
        env_vars['ENVIRONMENT'] = 'production'
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.is_development() is False
            assert settings.is_production() is True
    
    def test_get_airtable_config(self):
        """Test getting Airtable configuration from settings."""
        env_vars = {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'TELEGRAM_BOT_TOKEN': 'test_token'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            config = settings.get_airtable_config()
            
            assert isinstance(config, AirtableConfig)
            assert config.api_key == "test_key"
            assert config.base_id == "test_base"
    
    def test_to_dict(self):
        """Test converting settings to dictionary."""
        env_vars = {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'TELEGRAM_ADMIN_IDS': '123,456'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            settings_dict = settings.to_dict()
            
            assert isinstance(settings_dict, dict)
            assert 'database' in settings_dict
            assert 'telegram' in settings_dict
            assert 'logging' in settings_dict
            assert 'application' in settings_dict
            
            # Check specific values
            assert settings_dict['database']['base_id'] == 'test_base'
            assert settings_dict['telegram']['admin_count'] == 2


class TestSettingsLoading:
    """Test suite for settings loading functions."""
    
    def test_load_settings(self):
        """Test load_settings function."""
        env_vars = {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'TELEGRAM_BOT_TOKEN': 'test_token'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = load_settings()
            
            assert isinstance(settings, Settings)
            assert settings.database.airtable_api_key == 'test_key'
    
    def test_load_env_file(self):
        """Test loading environment variables from .env file."""
        env_content = """
# Comment line
AIRTABLE_API_KEY=file_key
AIRTABLE_BASE_ID=file_base
TELEGRAM_BOT_TOKEN="file_token"

EMPTY_LINE=

INVALID_LINE_NO_EQUALS
        """
        
        with patch('builtins.open', mock_open(read_data=env_content)):
            with patch('pathlib.Path.exists', return_value=True):
                with patch.dict(os.environ, {}, clear=True):
                    load_env_file('.env')
                    
                    assert os.getenv('AIRTABLE_API_KEY') == 'file_key'
                    assert os.getenv('AIRTABLE_BASE_ID') == 'file_base'
                    assert os.getenv('TELEGRAM_BOT_TOKEN') == 'file_token'
    
    def test_load_env_file_nonexistent(self):
        """Test loading from non-existent .env file."""
        with patch('pathlib.Path.exists', return_value=False):
            # Should not raise exception
            load_env_file('.env')
    
    @patch('src.config.settings._settings', None)
    def test_get_settings_singleton(self):
        """Test that get_settings() returns singleton instance."""
        env_vars = {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'TELEGRAM_BOT_TOKEN': 'test_token'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('src.config.settings.load_env_file'):
                # First call should create instance
                settings1 = get_settings()
                
                # Second call should return same instance
                settings2 = get_settings()
                
                assert settings1 is settings2
    
    def test_reset_settings(self):
        """Test resetting global settings instance."""
        # This test mainly verifies the function exists and can be called
        reset_settings()  # Should not raise exception


class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    def test_convenience_functions(self):
        """Test that convenience functions work correctly."""
        env_vars = {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'DEBUG': 'true',
            'ENVIRONMENT': 'production'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('src.config.settings._settings', None):  # Reset singleton
                from src.config.settings import (
                    get_airtable_config,
                    get_database_settings,
                    get_telegram_settings,
                    is_debug_mode,
                    is_production
                )
                
                config = get_airtable_config()
                assert isinstance(config, AirtableConfig)
                
                db_settings = get_database_settings()
                assert isinstance(db_settings, DatabaseSettings)
                
                tg_settings = get_telegram_settings()
                assert isinstance(tg_settings, TelegramSettings)
                
                assert is_debug_mode() is True
                assert is_production() is True
"""
Unit tests for user interaction logging service.

Tests button click logging, bot response logging, user journey tracking,
and error handling for all user interaction scenarios.
"""

import pytest
import logging
from datetime import datetime
from unittest.mock import Mock, patch, call

from src.services.user_interaction_logger import (
    UserInteractionLogger,
    InteractionType,
    LoggingError
)


class TestUserInteractionLogger:
    """Test UserInteractionLogger functionality."""
    
    def setup_method(self):
        """Set up test instance."""
        self.logger = UserInteractionLogger()
        
        # Mock the underlying logger to capture calls
        self.mock_logger = Mock()
        self.logger._logger = self.mock_logger


class TestButtonClickLogging:
    """Test button click logging functionality."""
    
    def setup_method(self):
        """Set up test instance."""
        self.logger = UserInteractionLogger()
        self.mock_logger = Mock()
        self.logger._logger = self.mock_logger
    
    def test_log_button_click_with_valid_data(self):
        """Test logging button click with valid callback query data."""
        user_id = 12345
        button_data = "search"
        username = "testuser"
        
        self.logger.log_button_click(
            user_id=user_id,
            button_data=button_data,
            username=username
        )
        
        # Verify logger was called with structured data
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args[0][0]
        
        assert "BUTTON_CLICK" in call_args
        assert f"user_id={user_id}" in call_args
        assert f"button_data={button_data}" in call_args
        assert f"username={username}" in call_args
    
    def test_log_button_click_without_username(self):
        """Test logging button click without username."""
        user_id = 12345
        button_data = "main_menu"
        
        self.logger.log_button_click(
            user_id=user_id,
            button_data=button_data
        )
        
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args[0][0]
        
        assert "BUTTON_CLICK" in call_args
        assert f"user_id={user_id}" in call_args
        assert f"button_data={button_data}" in call_args
        assert "username=None" in call_args
    
    def test_log_button_click_with_complex_callback_data(self):
        """Test logging button click with complex callback data."""
        user_id = 67890
        button_data = "select_participant:rec123456"
        username = "john_doe"
        
        self.logger.log_button_click(
            user_id=user_id,
            button_data=button_data,
            username=username
        )
        
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args[0][0]
        
        assert "BUTTON_CLICK" in call_args
        assert f"button_data={button_data}" in call_args
        assert "select_participant:rec123456" in call_args
    
    def test_log_button_click_sanitizes_sensitive_data(self):
        """Test button click logging sanitizes sensitive data."""
        user_id = 12345
        button_data = "token:abc123secret"
        
        self.logger.log_button_click(
            user_id=user_id,
            button_data=button_data
        )
        
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args[0][0]
        
        # Should not contain the actual token
        assert "abc123secret" not in call_args
        assert "token:[REDACTED]" in call_args


class TestBotResponseLogging:
    """Test bot response logging functionality."""
    
    def setup_method(self):
        """Set up test instance."""
        self.logger = UserInteractionLogger()
        self.mock_logger = Mock()
        self.logger._logger = self.mock_logger
    
    def test_log_bot_response_with_text(self):
        """Test logging bot response with text content."""
        user_id = 12345
        response_type = "text_message"
        content = "Найдено участников: 3"
        
        self.logger.log_bot_response(
            user_id=user_id,
            response_type=response_type,
            content=content
        )
        
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args[0][0]
        
        assert "BOT_RESPONSE" in call_args
        assert f"user_id={user_id}" in call_args
        assert f"response_type={response_type}" in call_args
        assert content in call_args
    
    def test_log_bot_response_with_keyboard(self):
        """Test logging bot response with keyboard markup."""
        user_id = 67890
        response_type = "message_with_keyboard"
        content = "Выберите участника:"
        keyboard_info = "3 buttons: select_participant"
        
        self.logger.log_bot_response(
            user_id=user_id,
            response_type=response_type,
            content=content,
            keyboard_info=keyboard_info
        )
        
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args[0][0]
        
        assert "BOT_RESPONSE" in call_args
        assert keyboard_info in call_args
    
    def test_log_bot_response_with_timing(self):
        """Test bot response logging includes timing information."""
        user_id = 12345
        response_type = "edit_message"
        content = "Участник обновлен"
        
        with patch('src.services.user_interaction_logger.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 12, 30, 45)
            
            self.logger.log_bot_response(
                user_id=user_id,
                response_type=response_type,
                content=content
            )
        
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args[0][0]
        
        assert "2024-01-15 12:30:45" in call_args


class TestMissingResponseDetection:
    """Test missing response detection and error logging."""
    
    def setup_method(self):
        """Set up test instance."""
        self.logger = UserInteractionLogger()
        self.mock_logger = Mock()
        self.logger._logger = self.mock_logger
    
    def test_log_timeout_error(self):
        """Test logging of callback query timeout errors."""
        user_id = 12345
        button_data = "search"
        error_message = "Callback query timed out after 30 seconds"
        
        self.logger.log_missing_response(
            user_id=user_id,
            button_data=button_data,
            error_type="timeout",
            error_message=error_message
        )
        
        self.mock_logger.warning.assert_called_once()
        call_args = self.mock_logger.warning.call_args[0][0]
        
        assert "MISSING_RESPONSE" in call_args
        assert f"user_id={user_id}" in call_args
        assert f"error_type=timeout" in call_args
        assert error_message in call_args
    
    def test_log_handler_error(self):
        """Test logging of handler execution errors."""
        user_id = 67890
        button_data = "edit_field:name"
        error_message = "Handler raised unhandled exception"
        
        self.logger.log_missing_response(
            user_id=user_id,
            button_data=button_data,
            error_type="handler_error",
            error_message=error_message
        )
        
        self.mock_logger.error.assert_called_once()
        call_args = self.mock_logger.error.call_args[0][0]
        
        assert "MISSING_RESPONSE" in call_args
        assert f"error_type=handler_error" in call_args


class TestUserJourneyTracking:
    """Test user journey tracking functionality."""
    
    def setup_method(self):
        """Set up test instance."""
        self.logger = UserInteractionLogger()
        self.mock_logger = Mock()
        self.logger._logger = self.mock_logger
    
    def test_log_user_journey_step(self):
        """Test logging individual user journey steps."""
        user_id = 12345
        step = "search_results_displayed"
        context = {"results_count": 3, "query": "Иван"}
        
        self.logger.log_journey_step(
            user_id=user_id,
            step=step,
            context=context
        )
        
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args[0][0]
        
        assert "JOURNEY_STEP" in call_args
        assert f"user_id={user_id}" in call_args
        assert f"step={step}" in call_args
        assert "results_count=3" in call_args
        assert "query=Иван" in call_args
    
    def test_log_conversation_state_change(self):
        """Test logging conversation state transitions."""
        user_id = 67890
        from_state = "WAITING_FOR_NAME" 
        to_state = "SHOWING_RESULTS"
        trigger = "name_search_completed"
        
        self.logger.log_state_change(
            user_id=user_id,
            from_state=from_state,
            to_state=to_state,
            trigger=trigger
        )
        
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args[0][0]
        
        assert "STATE_CHANGE" in call_args
        assert f"from_state={from_state}" in call_args
        assert f"to_state={to_state}" in call_args
        assert f"trigger={trigger}" in call_args


class TestLoggingConfiguration:
    """Test logging configuration and integration."""
    
    def test_logger_initialization_with_default_config(self):
        """Test logger initializes with default configuration."""
        logger = UserInteractionLogger()
        
        assert logger._logger.name == "user_interaction"
        assert logger._logger.level == logging.INFO
    
    def test_logger_initialization_with_custom_config(self):
        """Test logger initializes with custom configuration."""
        logger = UserInteractionLogger(
            logger_name="custom_interactions",
            log_level=logging.DEBUG
        )
        
        assert logger._logger.name == "custom_interactions"
        assert logger._logger.level == logging.DEBUG
    
    @patch('src.services.user_interaction_logger.get_settings')
    def test_logger_uses_settings_configuration(self, mock_get_settings):
        """Test logger uses application settings configuration."""
        mock_settings = Mock()
        mock_settings.logging.log_level = "DEBUG"
        mock_get_settings.return_value = mock_settings
        
        logger = UserInteractionLogger()
        
        # Should use settings from configuration
        mock_get_settings.assert_called_once()


class TestErrorHandling:
    """Test error handling in logging service."""
    
    def setup_method(self):
        """Set up test instance."""
        self.logger = UserInteractionLogger()
    
    def test_logging_failure_does_not_raise_exception(self):
        """Test that logging failures do not crash the application."""
        # Mock logger to raise exception
        self.logger._logger = Mock()
        self.logger._logger.info.side_effect = Exception("Logging system down")
        
        # Should not raise exception
        try:
            self.logger.log_button_click(
                user_id=12345,
                button_data="test"
            )
        except Exception:
            pytest.fail("Logging failure should not raise exception")
    
    def test_invalid_user_id_logs_warning(self):
        """Test invalid user ID logs warning but continues."""
        mock_logger = Mock()
        self.logger._logger = mock_logger
        
        self.logger.log_button_click(
            user_id=None,  # Invalid user ID
            button_data="test"
        )
        
        # Should log warning about invalid user ID
        mock_logger.warning.assert_called()
    
    def test_empty_button_data_logs_warning(self):
        """Test empty button data logs warning but continues."""
        mock_logger = Mock()
        self.logger._logger = mock_logger
        
        self.logger.log_button_click(
            user_id=12345,
            button_data=""  # Empty button data
        )
        
        # Should log warning about empty button data
        mock_logger.warning.assert_called()


class TestDataSanitization:
    """Test data sanitization for privacy compliance."""
    
    def setup_method(self):
        """Set up test instance."""
        self.logger = UserInteractionLogger()
        self.mock_logger = Mock()
        self.logger._logger = self.mock_logger
    
    def test_sanitizes_token_data(self):
        """Test sanitization of token-like data."""
        sensitive_patterns = [
            "token:abc123",
            "api_key:secret456",
            "password:mypass",
            "auth:bearer_token"
        ]
        
        for pattern in sensitive_patterns:
            self.mock_logger.reset_mock()
            
            self.logger.log_button_click(
                user_id=12345,
                button_data=pattern
            )
            
            call_args = self.mock_logger.info.call_args[0][0]
            
            # Should not contain the sensitive part
            assert "abc123" not in call_args
            assert "secret456" not in call_args 
            assert "mypass" not in call_args
            assert "bearer_token" not in call_args
            
            # Should contain redacted version
            assert "[REDACTED]" in call_args
    
    def test_preserves_non_sensitive_data(self):
        """Test that non-sensitive data is preserved."""
        non_sensitive_data = [
            "select_participant:rec123",
            "edit_field:name", 
            "save_changes",
            "main_menu"
        ]
        
        for data in non_sensitive_data:
            self.mock_logger.reset_mock()
            
            self.logger.log_button_click(
                user_id=12345,
                button_data=data
            )
            
            call_args = self.mock_logger.info.call_args[0][0]
            
            # Should contain the original data
            assert data in call_args
            assert "[REDACTED]" not in call_args


class TestInteractionTypeEnum:
    """Test InteractionType enum values."""
    
    def test_interaction_type_values(self):
        """Test all interaction type enum values are defined."""
        assert InteractionType.BUTTON_CLICK.value == "button_click"
        assert InteractionType.BOT_RESPONSE.value == "bot_response" 
        assert InteractionType.MISSING_RESPONSE.value == "missing_response"
        assert InteractionType.JOURNEY_STEP.value == "journey_step"
        assert InteractionType.STATE_CHANGE.value == "state_change"


class TestLoggingErrorException:
    """Test LoggingError exception class."""
    
    def test_logging_error_creation(self):
        """Test LoggingError can be created with message."""
        error = LoggingError("Logging system unavailable")
        assert str(error) == "Logging system unavailable"
        assert isinstance(error, Exception)
    
    def test_logging_error_inheritance(self):
        """Test LoggingError inherits from Exception."""
        error = LoggingError("Test error")
        assert isinstance(error, Exception)
        
        # Should be catchable as Exception
        try:
            raise LoggingError("Test logging error")
        except Exception as e:
            assert isinstance(e, LoggingError)
            assert str(e) == "Test logging error"
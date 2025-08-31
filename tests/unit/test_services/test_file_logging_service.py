"""
Tests for file logging service functionality.

Tests the core file logging service that handles directory management,
log file creation, and persistent logging infrastructure.
"""

import pytest
import tempfile
import shutil
import os
import logging
from pathlib import Path
from unittest.mock import Mock, patch

from src.services.file_logging_service import FileLoggingService, FileLoggingConfig


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def basic_config(temp_log_dir):
    """Basic file logging configuration for testing."""
    return FileLoggingConfig(
        enabled=True,
        log_dir=temp_log_dir,
        max_file_size=1024*1024,  # 1MB
        backup_count=3,
        create_subdirs=True
    )


class TestFileLoggingService:
    """Test file logging service core functionality."""
    
    def test_file_logger_creation_with_config(self, basic_config):
        """Verify file logger instances are created with correct handlers and configurations."""
        # Arrange & Act
        service = FileLoggingService(basic_config)
        
        # Assert
        assert service.config == basic_config
        assert service.config.enabled is True
        assert service.config.log_dir == basic_config.log_dir
        assert service.config.max_file_size == 1024*1024
        assert service.config.backup_count == 3
    
    def test_log_directory_creation(self, basic_config):
        """Verify automatic creation of log directories (application/, user-interactions/, errors/, archived/)."""
        # Arrange & Act
        service = FileLoggingService(basic_config)
        service.initialize_directories()
        
        # Assert - Check all required directories are created
        expected_dirs = [
            basic_config.log_dir / "application",
            basic_config.log_dir / "user-interactions", 
            basic_config.log_dir / "errors",
            basic_config.log_dir / "archived"
        ]
        
        for dir_path in expected_dirs:
            assert dir_path.exists(), f"Directory {dir_path} should exist"
            assert dir_path.is_dir(), f"{dir_path} should be a directory"
    
    def test_log_file_writing_with_formatting(self, basic_config):
        """Verify logs are written to correct files with proper formatting and timestamps."""
        # Arrange
        service = FileLoggingService(basic_config)
        service.initialize_directories()
        
        # Act
        app_logger = service.get_application_logger("test_module")
        app_logger.setLevel(logging.DEBUG)  # Ensure all messages are logged
        app_logger.info("Test application log message")
        
        # Flush handlers to ensure content is written
        for handler in app_logger.handlers:
            handler.flush()
        
        # Assert
        app_log_file = basic_config.log_dir / "application" / "app.log"
        assert app_log_file.exists(), "Application log file should exist"
        
        with open(app_log_file, 'r') as f:
            content = f.read()
            assert "Test application log message" in content
            assert "test_module" in content
            # Timestamp format check
            import re
            timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            assert re.search(timestamp_pattern, content), "Log should contain timestamp"
    
    def test_configuration_enable_disable(self, temp_log_dir):
        """Verify file logging respects environment variable enable/disable settings."""
        # Test disabled configuration
        disabled_config = FileLoggingConfig(
            enabled=False,
            log_dir=temp_log_dir
        )
        
        service = FileLoggingService(disabled_config)
        assert service.config.enabled is False
        
        # When disabled, should not create loggers that write to files
        logger = service.get_application_logger("test")
        
        # Verify that when disabled, no file handlers are added
        file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
        assert len(file_handlers) == 0, "No file handlers should exist when disabled"
    
    def test_multiple_log_types_routing(self, basic_config):
        """Verify different log levels (DEBUG, INFO, WARNING, ERROR) route to appropriate files."""
        # Arrange
        service = FileLoggingService(basic_config) 
        service.initialize_directories()
        
        # Act - Create different loggers and log at different levels
        app_logger = service.get_application_logger("app_test")
        app_logger.setLevel(logging.DEBUG)  # Ensure all messages are logged
        
        error_logger = service.get_error_logger("error_test")
        error_logger.setLevel(logging.DEBUG)
        
        app_logger.info("Info message")
        app_logger.warning("Warning message") 
        error_logger.error("Error message")
        
        # Flush handlers to ensure content is written
        for handler in app_logger.handlers:
            handler.flush()
        for handler in error_logger.handlers:
            handler.flush()
        
        # Assert - Check messages go to correct files
        app_log_file = basic_config.log_dir / "application" / "app.log"
        error_log_file = basic_config.log_dir / "errors" / "errors.log"
        
        with open(app_log_file, 'r') as f:
            app_content = f.read()
            assert "Info message" in app_content
            assert "Warning message" in app_content
        
        with open(error_log_file, 'r') as f:
            error_content = f.read()
            assert "Error message" in error_content
    
    def test_directory_structure_consistency(self, basic_config):
        """Verify log directory structure remains consistent during operations."""
        # Arrange & Act
        service = FileLoggingService(basic_config)
        service.initialize_directories()
        
        # Perform various logging operations
        app_logger = service.get_application_logger("test1")
        app_logger.setLevel(logging.DEBUG)
        
        user_logger = service.get_user_interaction_logger()
        user_logger.setLevel(logging.DEBUG)
        
        error_logger = service.get_error_logger("test2")
        error_logger.setLevel(logging.DEBUG)
        
        app_logger.info("Test 1")
        user_logger.info("User interaction test")
        error_logger.error("Error test")
        
        # Flush all handlers
        for logger in [app_logger, user_logger, error_logger]:
            for handler in logger.handlers:
                handler.flush()
        
        # Assert - Directory structure remains intact
        expected_structure = {
            "application": ["app.log"],
            "user-interactions": ["user_interactions.log"], 
            "errors": ["errors.log"],
            "archived": []  # Empty initially
        }
        
        for subdir, expected_files in expected_structure.items():
            dir_path = basic_config.log_dir / subdir
            assert dir_path.exists(), f"{subdir} directory should exist"
            
            actual_files = [f.name for f in dir_path.glob("*.log")]
            for expected_file in expected_files:
                assert expected_file in actual_files, f"{expected_file} should exist in {subdir}"


class TestFileLoggingConfig:
    """Test file logging configuration validation and creation."""
    
    def test_config_validation_with_valid_settings(self):
        """Test configuration validation with valid settings."""
        config = FileLoggingConfig(
            enabled=True,
            log_dir=Path("/tmp/test_logs"),
            max_file_size=1024*1024,
            backup_count=5,
            create_subdirs=True
        )
        
        # Should not raise any validation errors
        config.validate()
        
        assert config.enabled is True
        assert config.max_file_size == 1024*1024
        assert config.backup_count == 5
    
    def test_config_validation_with_invalid_settings(self):
        """Test configuration validation with invalid settings."""
        # Test invalid file size
        with pytest.raises(ValueError, match="max_file_size must be positive"):
            config = FileLoggingConfig(enabled=True, max_file_size=-1)
            config.validate()
        
        # Test invalid backup count
        with pytest.raises(ValueError, match="backup_count cannot be negative"):
            config = FileLoggingConfig(enabled=True, backup_count=-1)
            config.validate()


class TestFileLoggingServiceErrorHandling:
    """Test error handling scenarios for file logging service."""
    
    def test_disk_space_handling(self, temp_log_dir):
        """Verify graceful handling when disk space is insufficient for log files."""
        config = FileLoggingConfig(enabled=True, log_dir=temp_log_dir)
        service = FileLoggingService(config)
        
        # Mock disk space error
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            # Should not raise exception - graceful degradation
            logger = service.get_application_logger("test")
            logger.error("This should not crash the service")
    
    def test_permission_error_handling(self, temp_log_dir):
        """Verify fallback behavior when log directory is not writable."""
        config = FileLoggingConfig(enabled=True, log_dir=temp_log_dir)
        service = FileLoggingService(config)
        
        # Mock permission error
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            # Should handle gracefully and not crash
            try:
                service.initialize_directories()
            except PermissionError:
                pytest.fail("Service should handle permission errors gracefully")
    
    def test_logging_system_failure_resilience(self, temp_log_dir):
        """Verify bot continues functioning when file logging system fails."""
        config = FileLoggingConfig(enabled=True, log_dir=temp_log_dir)
        service = FileLoggingService(config)
        
        # Test actual error handling within the method, not mocking the whole method
        # Simulate a file system error during logger creation
        with patch('logging.handlers.RotatingFileHandler', side_effect=Exception("Logging system failed")):
            # Bot should continue - this test verifies no exception propagates
            try:
                # This would be called during bot initialization
                logger = service.get_application_logger("main")
                # Should return a fallback logger without crashing
                assert logger is not None, "Should return a fallback logger"
                assert logger.name == "app.main", "Should return the correct logger name"
            except Exception as e:
                pytest.fail(f"Logging system failure should not crash the application: {e}")
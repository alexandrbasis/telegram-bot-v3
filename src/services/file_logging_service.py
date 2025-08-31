"""
File logging service for persistent log storage with organized directory structure.

Provides file-based logging with automatic directory management, log rotation,
and dual output capabilities to complement console logging.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class FileLoggingConfig:
    """Configuration for file logging service."""
    
    enabled: bool = True
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    max_file_size: int = 10 * 1024 * 1024  # 10MB default
    backup_count: int = 5  # Keep 5 backup files
    create_subdirs: bool = True
    
    def validate(self) -> None:
        """
        Validate configuration settings.
        
        Raises:
            ValueError: If settings are invalid
        """
        if self.max_file_size <= 0:
            raise ValueError("max_file_size must be positive")
        
        if self.backup_count < 0:
            raise ValueError("backup_count cannot be negative")


class FileLoggingService:
    """
    Service for persistent file-based logging with organized directory structure.
    
    Manages log directories, file handlers, and provides loggers for different
    log types (application, user interactions, errors) with automatic rotation.
    """
    
    def __init__(self, config: FileLoggingConfig):
        """
        Initialize file logging service.
        
        Args:
            config: File logging configuration
        """
        self.config = config
        self.config.validate()
        self._loggers: Dict[str, logging.Logger] = {}
        
        if self.config.enabled:
            self.initialize_directories()
    
    def _create_rotating_handler(self, log_file_path: Path, formatter: logging.Formatter) -> Optional[logging.Handler]:
        """
        Create a rotating file handler with error handling.
        
        Args:
            log_file_path: Path to the log file
            formatter: Log formatter to use
            
        Returns:
            Rotating file handler or None if creation fails
        """
        try:
            handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count
            )
            handler.setFormatter(formatter)
            return handler
        except (OSError, PermissionError, Exception) as e:
            logging.getLogger(__name__).warning(f"Failed to create file handler for {log_file_path}: {e}")
            return None
    
    def initialize_directories(self) -> None:
        """Create log directory structure if it doesn't exist."""
        if not self.config.enabled:
            return
            
        try:
            # Create main log directory
            self.config.log_dir.mkdir(parents=True, exist_ok=True)
            
            if self.config.create_subdirs:
                # Create subdirectories for different log types
                subdirs = ["application", "user-interactions", "errors", "archived"]
                for subdir in subdirs:
                    (self.config.log_dir / subdir).mkdir(exist_ok=True)
                    
        except (OSError, PermissionError) as e:
            # Graceful degradation - log error but don't crash
            logging.getLogger(__name__).warning(f"Failed to create log directories: {e}")
    
    def get_application_logger(self, module_name: str) -> logging.Logger:
        """
        Get logger for application logs.
        
        Args:
            module_name: Name of the module requesting the logger
            
        Returns:
            Logger configured for application logging
        """
        try:
            if not self.config.enabled:
                # Return standard logger without file handler when disabled
                return logging.getLogger(module_name)
            
            logger_key = f"app_{module_name}"
            
            if logger_key not in self._loggers:
                logger = logging.getLogger(f"app.{module_name}")
                
                # Add rotating file handler
                log_file = self.config.log_dir / "application" / "app.log"
                formatter = logging.Formatter(
                    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                
                handler = self._create_rotating_handler(log_file, formatter)
                if handler:
                    logger.addHandler(handler)
                
                self._loggers[logger_key] = logger
            
            return self._loggers[logger_key]
            
        except Exception as e:
            # Ultimate fallback - return standard logger to prevent application crashes
            logging.getLogger(__name__).error(f"Failed to create application logger for {module_name}: {e}")
            return logging.getLogger(module_name)
    
    def get_user_interaction_logger(self) -> logging.Logger:
        """
        Get logger for user interaction logs.
        
        Returns:
            Logger configured for user interaction logging
        """
        if not self.config.enabled:
            return logging.getLogger("user_interaction")
        
        logger_key = "user_interaction"
        
        if logger_key not in self._loggers:
            logger = logging.getLogger("user_interaction")
            
            # Add rotating file handler
            log_file = self.config.log_dir / "user-interactions" / "user_interactions.log"
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            handler = self._create_rotating_handler(log_file, formatter)
            if handler:
                logger.addHandler(handler)
            
            self._loggers[logger_key] = logger
        
        return self._loggers[logger_key]
    
    def get_error_logger(self, module_name: str) -> logging.Logger:
        """
        Get logger for error logs.
        
        Args:
            module_name: Name of the module requesting the logger
            
        Returns:
            Logger configured for error logging
        """
        if not self.config.enabled:
            return logging.getLogger(f"error.{module_name}")
        
        logger_key = f"error_{module_name}"
        
        if logger_key not in self._loggers:
            logger = logging.getLogger(f"error.{module_name}")
            
            # Add rotating file handler
            log_file = self.config.log_dir / "errors" / "errors.log"
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            handler = self._create_rotating_handler(log_file, formatter)
            if handler:
                logger.addHandler(handler)
            
            self._loggers[logger_key] = logger
        
        return self._loggers[logger_key]
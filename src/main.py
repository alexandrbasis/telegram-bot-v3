"""
Main bot application entry point.

Initializes and runs the Telegram bot with search conversation functionality,
proper error handling, and logging configuration including persistent file logging.
"""

import asyncio
import logging
from typing import NoReturn, Optional

from telegram import Update
from telegram.ext import Application, ContextTypes
from telegram.error import Conflict, NetworkError, TimedOut, RetryAfter
from pathlib import Path
import tempfile

from src.utils.single_instance import InstanceLock

from src.config.settings import get_settings
from src.bot.handlers.search_conversation import get_search_conversation_handler
from src.services.file_logging_service import FileLoggingService

logger = logging.getLogger(__name__)

# Global file logging service instance
_file_logging_service: Optional[FileLoggingService] = None


def configure_logging(settings) -> None:
    """
    Configure logging based on settings, including file logging if enabled.
    
    Args:
        settings: Application settings with logging configuration
    """
    global _file_logging_service
    
    log_level = getattr(logging, settings.logging.log_level.upper())
    
    # Configure basic console logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set specific loggers
    logging.getLogger('telegram').setLevel(logging.INFO)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    # Initialize file logging if enabled
    try:
        file_config = settings.get_file_logging_config()
        if file_config.enabled:
            _file_logging_service = FileLoggingService(file_config)
            _file_logging_service.initialize_directories()
            
            # Get application logger with file handler
            app_logger = _file_logging_service.get_application_logger("main")
            app_logger.setLevel(log_level)
            
            logger.info(f"File logging initialized: {file_config.log_dir}")
        else:
            logger.info("File logging disabled in configuration")
    except Exception as e:
        logger.error(f"Failed to initialize file logging: {e}")
        logger.warning("Continuing with console logging only")
    
    logger.info(f"Logging configured with level: {settings.logging.log_level}")


def get_file_logging_service() -> Optional[FileLoggingService]:
    """
    Get the global file logging service instance.
    
    Returns:
        FileLoggingService instance if initialized, None otherwise
    """
    return _file_logging_service


def create_application() -> Application:
    """
    Create and configure the Telegram bot application.
    
    Sets up the bot with conversation handlers, error handling, and proper
    initialization based on configuration settings.
    
    Returns:
        Configured Application instance ready to run
        
    Raises:
        ValueError: If bot token is missing or invalid
        Exception: If application setup fails
    """
    logger.info("Creating Telegram bot application")
    
    # Load settings
    settings = get_settings()
    
    # Configure logging first
    configure_logging(settings)
    
    # Validate bot token
    if not settings.telegram.bot_token:
        raise ValueError("Bot token is required but not configured")
    
    logger.info("Building Telegram Application")
    
    async def post_init(app: Application) -> None:
        """Post-init hook to ensure polling mode is clean and log context."""
        try:
            info = await app.bot.get_webhook_info()
            if info and info.url:
                logger.warning(
                    "Webhook is configured (%s). Deleting to enable polling mode...",
                    info.url,
                )
                await app.bot.delete_webhook(drop_pending_updates=True)
                logger.info("Webhook deleted; proceeding with polling.")
        except Exception as e:
            logger.warning(f"Failed to check/delete webhook: {e}")

        try:
            me = await app.bot.get_me()
            logger.info("Bot identity: @%s (id=%s)", getattr(me, "username", "?"), getattr(me, "id", "?"))
        except Exception:
            # Non-fatal: continue without bot identity
            pass

    app = (
        Application.builder()
        .token(settings.telegram.bot_token)
        .post_init(post_init)
        .build()
    )
    
    # Add conversation handler for search functionality
    logger.info("Adding search conversation handler")
    search_handler = get_search_conversation_handler()
    app.add_handler(search_handler)
    
    # Register global error handler for better diagnostics
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        err = getattr(context, "error", None)
        # Collect brief update context
        summary = {}
        try:
            if isinstance(update, Update):
                chat = getattr(update, "effective_chat", None)
                user = getattr(update, "effective_user", None)
                summary = {
                    "chat_id": getattr(chat, "id", None),
                    "user_id": getattr(user, "id", None),
                    "text": getattr(getattr(update, "message", None), "text", None),
                    "callback_data": getattr(getattr(update, "callback_query", None), "data", None),
                }
            else:
                summary = {"update": str(update)}
        except Exception:
            summary = {"update": repr(update)}

        # Log the actual exception object, if available
        if err:
            # Classify common network errors for clearer logs
            if isinstance(err, Conflict):
                logger.error(
                    "Polling conflict detected (another instance may be running). Context: %s",
                    summary,
                    exc_info=err,
                )
            elif isinstance(err, (RetryAfter, TimedOut)):
                logger.warning("Temporary Telegram API backoff/timeout: %s | %s", err, summary)
            elif isinstance(err, NetworkError):
                logger.warning("Network error while polling: %s | %s", err, summary)
            else:
                logger.error("Unhandled exception while handling update: %s", summary, exc_info=err)
        else:
            logger.error("Unhandled exception while handling update: %s", summary)

    app.add_error_handler(error_handler)

    logger.info("Bot application created and configured successfully")
    return app


def run_bot() -> None:
    """
    Run the Telegram bot with polling.
    
    Creates the application and starts polling for updates with proper
    error handling and graceful shutdown.
    
    Raises:
        Exception: If bot fails to start or encounters critical error
    """
    logger.info("Starting Telegram bot")
    
    try:
        # Create and configure application
        app = create_application()
        
        # Ensure a current event loop exists for PTB on Python 3.11+
        try:
            # Create a loop only if there is none running/available
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())

        # Start the bot with polling - this handles everything
        logger.info("Bot starting with polling mode")
        # Drop pending updates to avoid reprocessing backlog after restarts
        try:
            app.run_polling(drop_pending_updates=True)
        except Conflict as e:
            # Provide a clearer error message for the common multi-instance issue
            logger.error(
                "Polling conflict: %s. Likely another bot instance or service is polling this token.",
                str(e),
            )
            raise
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user interrupt")
    except Exception as e:
        logger.error(f"Critical error running bot: {e}")
        raise
    finally:
        logger.info("Bot shutdown complete")


def main() -> NoReturn:
    """
    Main entry point for the bot application.
    
    Sets up and runs the bot with proper error handling and logging.
    This function does not return under normal circumstances.
    """
    try:
        # Run the bot
        run_bot()
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        logger.exception("Fatal error in main")
    finally:
        print("Application terminated")


if __name__ == "__main__":
    # Ensure only a single instance of the bot runs per host
    # Use a lock file in the OS temp directory for cross-session safety
    lock_file = Path(tempfile.gettempdir()) / "telegram-bot-v3.lock"
    try:
        with InstanceLock(lock_file):
            main()
    except RuntimeError as e:
        # If another instance holds the lock, inform and exit gracefully
        print(str(e))

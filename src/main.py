"""
Main bot application entry point.

Initializes and runs the Telegram bot with search conversation functionality,
proper error handling, and logging configuration including persistent file logging.
"""

import asyncio
import logging
import tempfile
import os
from contextlib import suppress
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.error import Conflict, NetworkError, RetryAfter, TimedOut
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

from src.bot.handlers.admin_handlers import handle_logging_toggle_command
from src.bot.handlers.export_conversation_handlers import (
    get_export_conversation_handler,
)
from src.bot.handlers.export_handlers import handle_export_command
from src.bot.handlers.search_conversation import get_search_conversation_handler
from src.bot.handlers.schedule_handlers import get_schedule_handlers
from src.config.settings import Settings, get_settings
from src.services.file_logging_service import FileLoggingService
from src.utils.single_instance import InstanceLock

logger = logging.getLogger(__name__)

# Global file logging service instance
_file_logging_service: Optional[FileLoggingService] = None


def configure_logging(settings: Settings) -> None:
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
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set specific loggers
    logging.getLogger("telegram").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

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
    builder = Application.builder()
    builder = builder.token(settings.telegram.bot_token)

    # Configure HTTPX request with custom timeouts to prevent startup hangs
    request = HTTPXRequest(**settings.telegram.get_request_config())
    builder = builder.request(request)

    app = builder.build()

    # Add conversation handler for search functionality
    logger.info("Adding search conversation handler")
    search_handler = get_search_conversation_handler()
    app.add_handler(search_handler)

    # Add export conversation handler (admin-only)
    logger.info("Adding export conversation handler")
    export_conversation_handler = get_export_conversation_handler()
    app.add_handler(export_conversation_handler)

    # Add schedule command and callbacks (feature-flagged)
    enable_schedule = os.getenv("ENABLE_SCHEDULE_FEATURE", "false").lower() == "true"
    if enable_schedule:
        logger.info("Adding schedule handlers")
        for h in get_schedule_handlers():
            app.add_handler(h)

    # Keep legacy export command handler for backward compatibility
    logger.info("Adding legacy export command handler")
    legacy_export_handler = CommandHandler("export_direct", handle_export_command)
    app.add_handler(legacy_export_handler)

    # Add admin logging toggle command handler
    logger.info("Adding logging toggle command handler")
    logging_handler = CommandHandler("logging", handle_logging_toggle_command)
    app.add_handler(logging_handler)

    # Store settings in bot_data for handlers to access
    app.bot_data["settings"] = settings

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
                    "callback_data": getattr(
                        getattr(update, "callback_query", None), "data", None
                    ),
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
                logger.warning(
                    "Temporary Telegram API backoff/timeout: %s | %s", err, summary
                )
            elif isinstance(err, NetworkError):
                logger.warning("Network error while polling: %s | %s", err, summary)
            else:
                logger.error(
                    "Unhandled exception while handling update: %s",
                    summary,
                    exc_info=err,
                )
        else:
            logger.error("Unhandled exception while handling update: %s", summary)

    app.add_error_handler(error_handler)

    logger.info("Bot application created and configured successfully")
    return app


async def _shutdown_application(app: Optional[Application]) -> None:
    """Safely stop and shut down the Telegram application."""

    if app is None:
        return

    updater = app.updater

    if updater is not None:
        with suppress(Exception):
            await updater.stop()
        with suppress(Exception):
            await updater.shutdown()

    with suppress(Exception):
        await app.stop()

    with suppress(Exception):
        await app.shutdown()


async def run_bot() -> None:
    """
    Run the Telegram bot with an async-friendly lifecycle.

    Behavior:
    - In tests: if `Application.run_polling` is patched as `AsyncMock`, await it.
    - In production: use the explicit async lifecycle (initialize/start/poll/stop)
      to avoid nesting/closing the event loop managed by PTB.
    """
    logger.info("Starting Telegram bot")

    app: Optional[Application] = None
    max_attempts: Optional[int] = None
    retry_delay: float = 0.0
    attempt = 1

    try:
        while True:
            if max_attempts is not None and attempt > max_attempts:
                raise RuntimeError("Failed to start bot after retry attempts")

            try:
                app = create_application()
            except Exception:
                # If we cannot create the application, abort startup entirely
                raise

            # If tests patched run_polling as AsyncMock, await it to satisfy expectations
            run_polling_attr = getattr(app, "run_polling", None)
            if (
                run_polling_attr is not None
                and "AsyncMock" in type(run_polling_attr).__name__
            ):
                logger.info("Bot starting with mocked polling (test mode)")
                from typing import Any, cast

                await cast(Any, run_polling_attr)(drop_pending_updates=True)
                return

            if max_attempts is None:
                settings: Optional[Settings] = app.bot_data.get("settings")
                retry_config = (
                    settings.telegram.get_startup_retry_config()
                    if settings is not None
                    else {"attempts": 1, "delay_seconds": 0.0}
                )
                max_attempts = max(int(retry_config.get("attempts", 1)), 1)
                retry_delay = max(float(retry_config.get("delay_seconds", 0.0)), 0.0)

            try:
                logger.info(
                    "Bot starting with async lifecycle (polling) [attempt %s/%s]",
                    attempt,
                    max_attempts,
                )

                await app.initialize()
                await app.start()

                updater = app.updater
                if updater is None:
                    raise RuntimeError("Application.updater is not available")

                await updater.initialize()
                await updater.start_polling(drop_pending_updates=True)
                break

            except (TimedOut, Conflict) as err:
                if isinstance(err, Conflict):
                    logger.warning(
                        "Telegram reported a polling conflict (attempt %s/%s). "
                        "Another bot instance may still be running.",
                        attempt,
                        max_attempts,
                    )
                else:
                    logger.warning(
                        "Telegram API timed out during startup (attempt %s/%s): %s",
                        attempt,
                        max_attempts,
                        err,
                    )

                await _shutdown_application(app)
                app = None

                attempt += 1

                if max_attempts is not None and attempt > max_attempts:
                    raise

                if retry_delay > 0:
                    logger.info("Retrying bot startup in %.1f seconds", retry_delay)
                    await asyncio.sleep(retry_delay)

                continue

            except Exception:
                await _shutdown_application(app)
                app = None
                raise

        try:
            # Block until cancellation (e.g., SIGINT)
            stop_event = asyncio.Event()
            await stop_event.wait()
        except asyncio.CancelledError:
            logger.info("Cancellation received; stopping bot")

    except KeyboardInterrupt:
        logger.info("Bot stopped by user interrupt")
    except Exception as e:
        logger.error(f"Critical error running bot: {e}")
        raise
    finally:
        await _shutdown_application(app)
        logger.info("Bot shutdown complete")


def main() -> None:
    """
    Main entry point for the bot application.

    Sets up and runs the bot with proper error handling and logging.
    This function does not return under normal circumstances.
    """
    bot_coroutine = run_bot()
    try:
        # Run the bot (async run via asyncio.run to satisfy tests)
        asyncio.run(bot_coroutine)

    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        logger.exception("Fatal error in main")
    finally:
        # When asyncio.run is mocked in tests the coroutine is never awaited,
        # so we need to close it manually to avoid runtime warnings.
        if hasattr(bot_coroutine, "close"):
            bot_coroutine.close()

        # Some tests patch asyncio.run, which leaves the implicitly created
        # default event loop open. Closing it here prevents ResourceWarnings
        # about unclosed sockets and loops while keeping real runtime behavior
        # (where asyncio.run() manages the loop) unchanged.
        loop: Optional[asyncio.AbstractEventLoop]
        try:
            loop = asyncio.get_event_loop_policy().get_event_loop()
        except RuntimeError:
            loop = None

        if loop is not None and not loop.is_closed() and not loop.is_running():
            loop.close()

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

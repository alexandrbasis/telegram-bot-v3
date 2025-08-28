"""
Main bot application entry point.

Initializes and runs the Telegram bot with search conversation functionality,
proper error handling, and logging configuration.
"""

import asyncio
import logging
from typing import NoReturn

from telegram.ext import Application

from src.config.settings import get_settings
from src.bot.handlers.search_conversation import get_search_conversation_handler

logger = logging.getLogger(__name__)


def configure_logging(settings) -> None:
    """
    Configure logging based on settings.
    
    Args:
        settings: Application settings with logging configuration
    """
    log_level = getattr(logging, settings.logging.level.upper())
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set specific loggers
    logging.getLogger('telegram').setLevel(logging.INFO)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    logger.info(f"Logging configured with level: {settings.logging.level}")


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
    if not settings.telegram.token:
        raise ValueError("Bot token is required but not configured")
    
    logger.info("Building Telegram Application")
    
    # Create Application
    app = (
        Application.builder()
        .token(settings.telegram.token)
        .build()
    )
    
    # Add conversation handler for search functionality
    logger.info("Adding search conversation handler")
    search_handler = get_search_conversation_handler()
    app.add_handler(search_handler)
    
    logger.info("Bot application created and configured successfully")
    return app


async def run_bot() -> None:
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
        
        # Start the bot with polling
        logger.info("Bot starting with polling mode")
        await app.run_polling()
        
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
        asyncio.run(run_bot())
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        logger.exception("Fatal error in main")
    finally:
        print("Application terminated")


if __name__ == "__main__":
    main()
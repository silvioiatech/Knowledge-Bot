#!/usr/bin/env python3
"""
Enhanced Knowledge Bot - Main Application Entry Point
"""

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from bot.handlers.video_handler import register_video_handlers


async def setup_logging():
    """Setup logging configuration."""
    # Remove default loguru logger
    logger.remove()
    
    # Add console logger with colors
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file logger for errors
    logger.add(
        "logs/knowledge_bot.log",
        level="WARNING",
        rotation="10 MB",
        retention="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)


async def setup_bot() -> tuple[Bot, Dispatcher]:
    """Setup and configure the Telegram bot."""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        sys.exit(1)
    
    # Initialize bot with enhanced defaults
    bot = Bot(
        token=Config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN
        )
    )
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Register handlers
    register_video_handlers(dp)
    
    logger.info("✅ Bot setup completed successfully")
    return bot, dp


async def on_startup(bot: Bot):
    """Handle bot startup."""
    bot_info = await bot.get_me()
    logger.info(f"🤖 Enhanced Knowledge Bot started: @{bot_info.username}")
    logger.info(f"🎯 Features enabled:")
    logger.info(f"   • Smart image generation: {Config.ENABLE_IMAGE_GENERATION}")
    logger.info(f"   • Notion integration: {Config.USE_NOTION_STORAGE}")
    logger.info(f"   • Railway storage: {bool(Config.RAILWAY_STATIC_URL)}")
    logger.info(f"   • Max processing time: {Config.MAX_PROCESSING_TIME}s")


async def on_shutdown(bot: Bot):
    """Handle bot shutdown."""
    logger.info("🛑 Shutting down Enhanced Knowledge Bot...")
    await bot.session.close()


async def main():
    """Main application entry point."""
    try:
        # Setup logging
        await setup_logging()
        logger.info("🚀 Starting Enhanced Knowledge Bot...")
        
        # Setup bot
        bot, dp = await setup_bot()
        
        # Register startup/shutdown handlers
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Start polling
        logger.info("📡 Starting bot polling...")
        await dp.start_polling(
            bot,
            skip_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        raise
    finally:
        logger.info("🔄 Cleanup completed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Application terminated by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

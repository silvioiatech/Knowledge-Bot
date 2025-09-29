"""Main Telegram bot entry point for Knowledge Bot MVP."""

import asyncio
import sys
from pathlib import Path

try:
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from loguru import logger
except ImportError:
    Bot = Dispatcher = DefaultBotProperties = ParseMode = None
    logger = None

from config import Config
from bot.handlers.video_handler import register_video_handlers
from bot.middleware import RateLimitMiddleware


class KnowledgeBot:
    """Main Knowledge Bot class."""
    
    def __init__(self):
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            if logger:
                logger.error(f"Configuration error: {e}")
            else:
                print(f"Configuration error: {e}")
            sys.exit(1)
        
        # Initialize bot and dispatcher
        if not Bot:
            raise RuntimeError("aiogram not installed")
            
        self.bot = Bot(
            token=Config.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        
        # Setup logging
        self._setup_logging()
        
        # Register middleware
        self._setup_middleware()
        
        # Register handlers
        self._register_handlers()
    
    def _setup_logging(self):
        """Configure logging with loguru."""
        if not logger:
            return
            
        # Remove default handler
        logger.remove()
        
        # Add console handler
        logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # Add file handler with rotation
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logger.add(
            log_dir / "bot_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )
        
        logger.info("Knowledge Bot logging initialized")
    
    def _setup_middleware(self):
        """Setup bot middleware."""
        # Add rate limiting middleware
        self.dp.message.middleware(RateLimitMiddleware())
        if logger:
            logger.info("Middleware registered")
    
    def _register_handlers(self):
        """Register all bot handlers."""
        # Register video handlers
        register_video_handlers(self.dp)
        
        # Import and start session cleanup
        from bot.handlers.video_handler import start_session_cleanup
        start_session_cleanup()
        
        # Register start command
        self._register_start_handler()
        
        if logger:
            logger.info("Bot handlers registered")
    
    def _register_start_handler(self):
        """Register /start command handler."""
        try:
            from aiogram.filters import Command
            from aiogram.types import Message
            
            @self.dp.message(Command("start"))
            async def start_command(message: Message):
                """Handle /start command."""
                welcome_text = """
🤖 <b>Welcome to Knowledge Bot!</b>

I help you build a knowledge base from TikTok and Instagram videos.

<b>How it works:</b>
1️⃣ Send me a TikTok or Instagram video URL
2️⃣ I'll download and analyze the content
3️⃣ Review the analysis and approve it
4️⃣ I'll create an enriched Markdown file for your knowledge base

<b>Supported platforms:</b>
• TikTok (tiktok.com, vm.tiktok.com)
• Instagram (instagram.com/p/, instagram.com/reel/)

<b>Limits:</b>
• Max 10 videos per hour
• Max 10 minutes per video

Send me a video URL to get started! 🚀
"""
                await message.answer(welcome_text)
        except ImportError:
            if logger:
                logger.warning("aiogram not available - start handler not registered")
            else:
                print("Warning: aiogram not available - start handler not registered")
    
    async def start_polling(self):
        """Start bot polling."""
        logger.info("Starting Knowledge Bot...")
        
        # Create knowledge base directory
        Config.KNOWLEDGE_BASE_PATH.mkdir(exist_ok=True)
        
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
        finally:
            await self.bot.session.close()
    
    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down Knowledge Bot...")
        await self.bot.session.close()


async def main():
    """Main entry point."""
    bot = KnowledgeBot()
    
    try:
        await bot.start_polling()
    except KeyboardInterrupt:
        if logger:
            logger.info("Bot stopped by user")
        else:
            print("Bot stopped by user")
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error: {e}")
        else:
            print(f"Unexpected error: {e}")
    finally:
        await bot.shutdown()


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("Python 3.8+ is required")
        sys.exit(1)
    
    # Run bot
    try:
        asyncio.run(main())
    except Exception as e:
        if logger:
            logger.critical(f"Failed to start bot: {e}")
        else:
            print(f"Failed to start bot: {e}")
        sys.exit(1)
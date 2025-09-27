"""Enhanced Knowledge Bot main entry point."""

import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from bot.handlers.video_handler import register_video_handlers
from bot.middleware import RateLimitMiddleware, LoggingMiddleware
from config import Config


class KnowledgeBotApp:
    """Main Knowledge Bot application."""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        
    async def _setup_logging(self):
        """Configure enhanced logging."""
        # Configure loguru
        logger.remove()
        logger.add(
            "logs/bot_{time}.log",
            rotation="1 day",
            retention="7 days", 
            format="{time} | {level} | {module}:{function}:{line} - {message}",
            level="DEBUG"
        )
        
        # Suppress aiogram INFO logs
        logging.getLogger("aiogram").setLevel(logging.WARNING)
        logger.info("Knowledge Bot logging initialized")
        
    async def _setup_middleware(self):
        """Setup bot middleware."""
        self.dp.message.middleware(RateLimitMiddleware())
        self.dp.callback_query.middleware(RateLimitMiddleware())
        self.dp.message.middleware(LoggingMiddleware())
        self.dp.callback_query.middleware(LoggingMiddleware())
        logger.info("Middleware registered")
    
    async def _register_handlers(self):
        """Register all bot handlers."""
        register_video_handlers(self.dp)
        logger.info("Bot handlers registered")
    
    async def _setup_commands(self):
        """Setup bot commands menu."""
        from aiogram.types import BotCommand
        
        commands = [
            BotCommand(command="start", description="🚀 Start the Knowledge Bot"),
        ]
        
        await self.bot.set_my_commands(commands)
        logger.info("Bot commands menu configured")
    
    async def _create_directories(self):
        """Create necessary directories."""
        directories = [
            Config.TEMP_DIR,
            Config.KNOWLEDGE_BASE_PATH,
            Path("logs"),
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
    
    async def _startup_message(self):
        """Send startup notification."""
        startup_text = """
🤖 **Knowledge Bot Enhanced - Online!**

🔧 **Capabilities Active:**
• Video Analysis with Web Research
• Technical Preview Generation  
• Multi-AI Content Pipeline (Gemini → Claude → GPT)
• Advanced Quality Metrics
• Notion + Markdown Storage
• Interactive Approval Workflow

Ready to process educational content!
        """
        
        # Send to admin if configured
        if hasattr(Config, 'ADMIN_CHAT_ID') and Config.ADMIN_CHAT_ID:
            try:
                await self.bot.send_message(
                    chat_id=Config.ADMIN_CHAT_ID,
                    text=startup_text
                )
            except Exception as e:
                logger.warning(f"Could not send startup message to admin: {e}")
    
    async def start_polling(self):
        """Start the bot with polling."""
        try:
            # Initialize bot configuration
            Config.validate()
            
            # Create bot and dispatcher
            self.bot = Bot(
                token=Config.TELEGRAM_BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            self.dp = Dispatcher()
            
            # Setup components
            await self._setup_logging()
            await self._setup_middleware()
            await self._register_handlers()
            await self._create_directories()
            await self._setup_commands()
            
            logger.info("Starting Knowledge Bot...")
            
            # Send startup notification
            await self._startup_message()
            
            # Start polling
            await self.dp.start_polling(
                self.bot,
                allowed_updates=["message", "callback_query"]
            )
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down Knowledge Bot...")
        
        if self.bot:
            await self.bot.session.close()
        
        logger.info("Knowledge Bot shutdown complete")


async def main():
    """Main entry point."""
    # Print startup info
    print("🚀 Knowledge Bot starting...")
    print(f"📂 Working directory: {Path.cwd()}")
    print(f"🐍 Python path: {Path.cwd() / 'venv' / 'bin' / 'python'}")
    
    app = KnowledgeBotApp()
    
    try:
        await app.start_polling()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        await app.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AttributeError:
        # Python < 3.7 compatibility
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main())
        finally:
            loop.close()

"""Enhanced Knowledge Bot main application using the 6-stage AI pipeline."""

import asyncio
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config import Config, TELEGRAM_BOT_TOKEN
from core.pipeline import KnowledgeBotPipeline
from interfaces.telegram.enhanced_interface import EnhancedTelegramInterface
from utils.helpers import ensure_directory


class EnhancedKnowledgeBot:
    """Enhanced Knowledge Bot with 6-stage AI pipeline."""
    
    def __init__(self):
        # Validate configuration
        Config.validate()
        
        # Initialize core components
        self.pipeline = KnowledgeBotPipeline()
        self.telegram_interface = EnhancedTelegramInterface()
        
        # Initialize bot and dispatcher
        self.bot = Bot(
            token=TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.MARKDOWN
            )
        )
        self.dispatcher = Dispatcher()
        
        # Set up logging
        self._setup_logging()
        
        # Register handlers
        self._setup_handlers()
        
        # Ensure directories exist
        self._setup_directories()
    
    def _setup_logging(self):
        """Configure logging with appropriate levels and formats."""
        
        # Remove default logger
        logger.remove()
        
        # Console logging
        logger.add(
            sys.stdout,
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True
        )
        
        # File logging
        ensure_directory("logs")
        logger.add(
            "logs/knowledge_bot_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="7 days",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            compression="zip"
        )
        
        # Error file logging
        logger.add(
            "logs/errors_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="30 days",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            compression="zip"
        )
        
        logger.info("Enhanced Knowledge Bot logging initialized")
    
    def _setup_handlers(self):
        """Set up Telegram message handlers."""
        
        # Get router from interface
        router = self.telegram_interface.get_router()
        
        # Include the router in dispatcher
        self.dispatcher.include_router(router)
        
        # Add middleware for the pipeline
        self._add_pipeline_middleware()
        
        logger.info("Telegram handlers configured")
    
    def _add_pipeline_middleware(self):
        """Add middleware to inject pipeline into handlers."""
        
        @self.dispatcher.message.outer_middleware()
        async def pipeline_middleware(handler, event, data):
            """Inject pipeline into handler data."""
            data['pipeline'] = self.pipeline
            return await handler(event, data)
        
        @self.dispatcher.callback_query.outer_middleware() 
        async def callback_pipeline_middleware(handler, event, data):
            """Inject pipeline into callback handler data."""
            data['pipeline'] = self.pipeline
            return await handler(event, data)
    
    def _setup_directories(self):
        """Ensure required directories exist."""
        
        directories = [
            Config.TEMP_DIR,
            Config.KNOWLEDGE_BASE_PATH,
            "logs"
        ]
        
        for directory in directories:
            ensure_directory(directory)
            logger.debug(f"Ensured directory exists: {directory}")
    
    async def start_polling(self):
        """Start the bot with polling."""
        
        logger.info("Starting Enhanced Knowledge Bot...")
        
        try:
            # Set bot commands
            await self._set_bot_commands()
            
            # Start cleanup task
            cleanup_task = asyncio.create_task(self._periodic_cleanup())
            
            # Start health check task
            health_task = asyncio.create_task(self._periodic_health_check())
            
            # Start polling
            logger.info("🚀 Enhanced Knowledge Bot is running!")
            logger.info("Ready to process educational videos with 6-stage AI pipeline:")
            logger.info("1. 🧠 Gemini Analysis + Web Research")
            logger.info("2. 📱 Telegram User Approval")
            logger.info("3. ✍️  Claude Textbook Generation")
            logger.info("4. 🎨 Banana Image Generation")
            logger.info("5. 🔧 GPT Assembly & QA")
            logger.info("6. 📊 Notion Database Storage")
            
            await self.dispatcher.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"Bot startup failed: {e}")
            raise
        finally:
            # Cleanup tasks
            if 'cleanup_task' in locals():
                cleanup_task.cancel()
            if 'health_task' in locals():
                health_task.cancel()
            
            # Close pipeline
            await self.pipeline.close()
    
    async def _set_bot_commands(self):
        """Set bot commands menu."""
        
        from aiogram.types import BotCommand
        
        commands = [
            BotCommand(command="start", description="🚀 Start the bot and see features"),
            BotCommand(command="help", description="❓ Get help and usage instructions"),
            BotCommand(command="stats", description="📊 View your processing statistics"),
        ]
        
        await self.bot.set_my_commands(commands)
        logger.info("Bot commands configured")
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of temporary files."""
        
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self.pipeline.cleanup_temp_files()
                logger.debug("Periodic cleanup completed")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup task failed: {e}")
    
    async def _periodic_health_check(self):
        """Periodic health check of system components."""
        
        while True:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes
                health = await self.pipeline.get_system_health()
                
                if health['status'] != 'healthy':
                    logger.warning(f"System health check: {health['status']}")
                    for component, status in health['components'].items():
                        if status != 'healthy':
                            logger.warning(f"Component {component} is {status}")
                else:
                    logger.debug("System health check: all components healthy")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check failed: {e}")
    
    async def shutdown(self):
        """Graceful shutdown."""
        
        logger.info("Shutting down Enhanced Knowledge Bot...")
        
        # Close pipeline
        await self.pipeline.close()
        
        # Close bot session
        await self.bot.session.close()
        
        logger.info("Shutdown complete")


async def main():
    """Main application entry point."""
    
    try:
        # Create and start bot
        bot = EnhancedKnowledgeBot()
        await bot.start_polling()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        # Ensure cleanup
        if 'bot' in locals():
            await bot.shutdown()


if __name__ == "__main__":
    # Handle different Python versions
    try:
        asyncio.run(main())
    except AttributeError:
        # Python < 3.7
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main())
        finally:
            loop.close()
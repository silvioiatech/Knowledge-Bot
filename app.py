#!/usr/bin/env python3
"""
Railway deployment entry point with bot and file server.
Starts both the Telegram bot and the file serving API.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def start_file_server():
    """Start the FastAPI file server."""
    try:
        import uvicorn
        from railway_server import app
        
        # Check if running on Railway
        port = int(os.getenv('PORT', 8000))
        host = "0.0.0.0" if os.getenv('RAILWAY_ENVIRONMENT') else "127.0.0.1"
        
        print(f"🌐 Starting file server on {host}:{port}")
        
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        
        await server.serve()
        
    except Exception as e:
        print(f"❌ File server error: {e}")

async def start_telegram_bot():
    """Start the Telegram bot."""
    try:
        from bot.main import main as bot_main
        print("🤖 Starting Telegram bot...")
        await bot_main()
    except Exception as e:
        print(f"❌ Bot error: {e}")

async def main():
    """Main entry point - run both services."""
    print("🚀 Knowledge Bot with Railway Storage starting...")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.executable}")
    
    try:
        # Check if we should run file server only
        if os.getenv('RUN_FILE_SERVER_ONLY'):
            await start_file_server()
        # Check if we should run bot only
        elif os.getenv('RUN_BOT_ONLY'):
            await start_telegram_bot()
        else:
            # Run both services concurrently
            await asyncio.gather(
                start_file_server(),
                start_telegram_bot(),
                return_exceptions=True
            )
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please check that all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Railway deployment entry point with comprehensive error handling and fallbacks.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check and log environment configuration."""
    print("🔍 Environment Check:")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"🌐 Railway environment: {os.getenv('RAILWAY_ENVIRONMENT', 'Not detected')}")
    print(f"🔑 Port: {os.getenv('PORT', 'Not set')}")
    
    # Check critical environment variables
    critical_vars = [
        "TELEGRAM_BOT_TOKEN",
        "GEMINI_API_KEY", 
        "OPENROUTER_API_KEY"
    ]
    
    missing_vars = []
    for var in critical_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Set")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

async def start_file_server():
    """Start the FastAPI file server."""
    try:
        import uvicorn
        from railway_server import app
        
        port = int(os.getenv('PORT', 8000))
        host = "0.0.0.0"
        
        print(f"🌐 Starting file server on {host}:{port}")
        
        config = uvicorn.Config(
            app, 
            host=host, 
            port=port, 
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        
        await server.serve()
        
    except Exception as e:
        print(f"❌ File server error: {e}")
        import traceback
        traceback.print_exc()

async def start_telegram_bot():
    """Start the Telegram bot with error handling."""
    try:
        # Test imports first
        print("📦 Testing bot imports...")
        
        try:
            from config import Config
            print("✅ Config loaded")
        except Exception as e:
            print(f"❌ Config error: {e}")
            return
        
        try:
            Config.validate()
            print("✅ Configuration validated")
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return
        
        try:
            from bot.main import main as bot_main
            print("✅ Bot main imported")
        except Exception as e:
            print(f"❌ Bot import error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("🤖 Starting Telegram bot...")
        await bot_main()
        
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main entry point with comprehensive error handling."""
    print("🚀 Knowledge Bot with Railway Storage starting...")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed - exiting")
        sys.exit(1)
    
    # Create required directories
    try:
        os.makedirs("/tmp/knowledge_bot", exist_ok=True)
        os.makedirs("./knowledge_base", exist_ok=True)
        os.makedirs("./logs", exist_ok=True)
        print("✅ Directories created")
    except Exception as e:
        print(f"⚠️ Directory creation warning: {e}")
    
    try:
        # Determine run mode
        run_mode = os.getenv('RUN_MODE', 'both')
        
        if run_mode == 'server' or os.getenv('RUN_FILE_SERVER_ONLY'):
            print("🌐 Running in file server only mode")
            await start_file_server()
        elif run_mode == 'bot' or os.getenv('RUN_BOT_ONLY'):
            print("🤖 Running in bot only mode")
            await start_telegram_bot()
        else:
            print("🔄 Running both services")
            # Run both services concurrently
            tasks = [
                asyncio.create_task(start_file_server()),
                asyncio.create_task(start_telegram_bot())
            ]
            
            # Wait for first task to complete or fail
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
            
            # Check if any task failed
            for task in done:
                if task.exception():
                    print(f"❌ Service failed: {task.exception()}")
                    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📦 Missing dependencies - check requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped by user")
    except Exception as e:
        print(f"💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
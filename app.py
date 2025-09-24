#!/usr/bin/env python3
"""
Simple app.py entry point for Railway deployment.
Railway automatically detects and runs app.py files.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point."""
    try:
        # Import the main bot function
        from bot.main import main as bot_main
        
        print("🚀 Knowledge Bot starting...")
        print(f"📂 Working directory: {os.getcwd()}")
        print(f"🐍 Python path: {sys.executable}")
        
        # Run the bot
        asyncio.run(bot_main())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please check that all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Railway startup script for Knowledge Bot.
This is the main entry point that Railway will use to start the bot.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for Railway deployment."""
    try:
        from bot.main import main as bot_main
        print("🚀 Knowledge Bot starting on Railway...")
        asyncio.run(bot_main())
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
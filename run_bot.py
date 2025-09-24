#!/usr/bin/env python3
"""Launch script for Knowledge Bot MVP."""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run main bot
try:
    from bot.main import main
    import asyncio
    
    if __name__ == "__main__":
        print("🚀 Starting Knowledge Bot...")
        asyncio.run(main())
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n👋 Bot stopped by user")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
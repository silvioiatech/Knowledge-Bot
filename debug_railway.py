#!/usr/bin/env python3
"""
Debug script to test Railway API directly.
Run this to see what's happening with the Railway download service.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_railway_api():
    """Test the Railway API with a sample URL."""
    
    from services.railway_client import RailwayClient, RailwayDownloadError
    from config import Config
    
    print("🔧 Railway API Debug Tool")
    print(f"📡 API URL: {Config.RAILWAY_API_URL}")
    print(f"🔑 API Key: {'✅ Set' if Config.RAILWAY_API_KEY else '❌ Not set'}")
    print()
    
    # Use a real TikTok URL for testing
    test_url = input("Enter a TikTok or Instagram URL to test: ").strip()
    if not test_url:
        test_url = "https://www.tiktok.com/@test/video/1234567890123456789"
    
    print(f"🎥 Testing with URL: {test_url}")
    print()
    
    try:
        client = RailwayClient()
        
        # Test health check first
        print("🏥 Testing health check...")
        is_healthy = await client.health_check()
        print(f"Health check result: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        print()
        
        # Test the download
        print("⏳ Starting download test...")
        result = await client.download_video(test_url)
        
        print("✅ Download successful!")
        print(f"📊 Result: {result}")
        
    except RailwayDownloadError as e:
        print(f"❌ Railway API Error: {e}")
    except Exception as e:
        print(f"💥 Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_railway_api())
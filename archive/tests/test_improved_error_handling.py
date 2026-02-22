#!/usr/bin/env python3
"""
Test improved GoAPI.ai error handling with proper task_id extraction
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

async def test_improved_error_handling():
    print("🔧 Testing Improved GoAPI.ai Error Handling")
    print("=" * 50)
    
    try:
        from cocoa_music import GoAPIMusicAPI, MusicConfig
        
        config = MusicConfig()
        api = GoAPIMusicAPI(config)
        api.console = __import__('rich').console.Console()
        
        print(f"✅ GoAPI Music API initialized")
        print(f"🔑 API Key: {config.music_api_key[:10]}...")
        
        # Test music generation (expect credit error but with proper task_id extraction)
        print(f"\n🧪 Testing music generation with improved error handling...")
        
        result = await api.generate_music(
            prompt="test credit error handling",
            style="ambient",
            mood="peaceful", 
            duration=30
        )
        
        print(f"\n📋 Result from improved error handling:")
        print(f"  Task ID: {result.get('task_id', 'NOT FOUND')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Success: {result.get('success')}")
        print(f"  Error: {result.get('error')}")
        print(f"  Message: {result.get('message')}")
        
        if result.get('task_id'):
            print(f"✅ SUCCESS: Task ID now properly extracted even from error responses!")
        else:
            print(f"❌ FAILED: Still no task_id in error responses")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_improved_error_handling())
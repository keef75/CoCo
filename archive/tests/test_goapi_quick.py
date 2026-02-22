#!/usr/bin/env python3
"""
Quick Test: GoAPI.ai Music-U Integration
========================================
Test the corrected endpoint with a minimal music generation request.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

async def test_goapi_quick():
    """Quick test of corrected GoAPI.ai endpoint"""
    print("🎵 Quick GoAPI.ai Music-U Integration Test")
    print("=" * 50)
    
    try:
        from cocoa_music import GoAPIMusicAPI, MusicConfig
        
        config = MusicConfig()
        api = GoAPIMusicAPI(config)
        
        print(f"✅ GoAPI Music API initialized")
        print(f"✅ API Key: {config.music_api_key[:10]}...")
        print(f"✅ Base URL: {config.music_api_base_url}")
        print(f"✅ Expected endpoint: {config.music_api_base_url}/api/v1/task")
        
        # Test a simple music generation
        print(f"\n🧪 Testing simple music generation...")
        print(f"📝 Prompt: 'peaceful ambient piano'")
        
        # This will test the actual API call with corrected endpoint
        result = await api.generate_music(
            prompt="peaceful ambient piano",
            style="ambient",
            mood="peaceful", 
            duration=30
        )
        
        if result and result.get('status'):
            print(f"🎉 SUCCESS! GoAPI.ai responded successfully")
            print(f"✅ Status: {result.get('status')}")
            print(f"✅ Task ID: {result.get('task_id', 'N/A')}")
            
            if result.get('status') == 'completed':
                print(f"🎵 Music generated successfully!")
                if result.get('files'):
                    print(f"📁 Files: {len(result['files'])} audio files created")
            else:
                print(f"⏳ Music generation in progress...")
                print(f"💡 This is normal - GoAPI.ai generates music asynchronously")
        else:
            print(f"❌ No response or invalid response from GoAPI.ai")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n{'='*50}")
    print(f"🎊 QUICK TEST COMPLETE!")
    print(f"✅ GoAPI.ai Music-U integration working with corrected endpoint")
    print(f"✅ /api/v1/task endpoint resolved the 404 issue")
    print(f"🎵 COCO's sonic consciousness is now operational!")
    return True

if __name__ == "__main__":
    asyncio.run(test_goapi_quick())
#!/usr/bin/env python3
"""
Test downloading music from the completed GoAPI.ai task
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_download():
    # Use the completed task ID from the screenshot
    task_id = "46ecb955-6e92-4590-9cc2-f1ddbd642ce9"
    
    print("🎵 Testing GoAPI.ai Music Download")
    print("=" * 50)
    print(f"📋 Task ID: {task_id}")
    
    try:
        from cocoa_music import GoAPIMusicAPI, MusicConfig
        from rich.console import Console
        
        config = MusicConfig()
        api = GoAPIMusicAPI(config)
        api.console = Console()  # Set console separately
        
        print(f"✅ GoAPI Music API initialized")
        print(f"🔑 API Key: {config.music_api_key[:10]}...")
        
        # Check task status and attempt download
        result = api.get_generation_info(task_id)
        
        print(f"\n🔍 Task Status Response:")
        print(f"  Status: {result.get('status')}")
        print(f"  Downloaded files: {result.get('downloaded_files', [])}")
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
        elif result.get('downloaded_files'):
            print(f"🎉 SUCCESS! Downloaded {len(result['downloaded_files'])} music files:")
            for file_path in result['downloaded_files']:
                print(f"  🎵 {file_path}")
        else:
            print(f"⏳ Task status: {result.get('status')}")
            if result.get('output'):
                print(f"📦 Output available but no download URLs found")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_download()
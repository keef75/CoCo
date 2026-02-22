#!/usr/bin/env python3
"""
Test that the compose method now returns the actual GoAPI.ai task_id
"""

import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

async def test_task_id_fix():
    print("🔧 Testing GoAPI.ai Task ID Fix")
    print("=" * 50)
    
    try:
        from cocoa_music import MusicCognition, MusicConfig
        from rich.console import Console
        
        config = MusicConfig()
        console = Console()
        workspace_path = Path("coco_workspace")
        
        music_consciousness = MusicCognition(config, workspace_path, console)
        
        print(f"✅ Music consciousness initialized")
        print(f"🔑 API Key: {config.music_api_key[:10]}...")
        
        # Test music generation - should now return actual task_id
        print(f"\n🧪 Testing task_id return value...")
        
        result = await music_consciousness.compose(
            prompt="test task id fix",
            style="ambient",
            duration=30
        )
        
        if result.get('status') == 'success':
            composition_spec = result.get('composition_specification', {})
            composition_id = composition_spec.get('composition_id', 'NOT FOUND')
            task_id = composition_spec.get('task_id', 'NOT FOUND')
            internal_id = composition_spec.get('internal_id', 'NOT FOUND')
            
            print(f"✅ Status: {result.get('status')}")
            print(f"🆔 Composition ID (shown to user): {composition_id}")
            print(f"📋 Task ID (for monitoring): {task_id}")
            print(f"🔢 Internal ID (for library): {internal_id}")
            
            # Check if composition_id is now a valid GoAPI task_id format
            if composition_id != 'NOT FOUND' and len(composition_id) > 20:
                print(f"🎉 SUCCESS: composition_id is now a valid GoAPI task_id!")
                print(f"   - Length: {len(composition_id)} chars (GoAPI format)")
                print(f"   - Background monitoring can now poll this ID")
            else:
                print(f"❌ FAILED: composition_id still not a valid GoAPI task_id")
                print(f"   - Length: {len(composition_id)} chars (too short)")
                
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_task_id_fix())
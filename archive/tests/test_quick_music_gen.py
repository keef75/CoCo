#!/usr/bin/env python3
"""
Quick test of corrected GoAPI.ai Music-U integration
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to the path so we can import cocoa modules
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

async def test_quick_generation():
    """Test one quick generation to verify everything works"""
    print("🎵 Quick GoAPI.ai Music-U Test")
    print("=" * 40)
    
    from cocoa_music import GoAPIMusicAPI, MusicConfig
    from rich.console import Console
    
    console = Console()
    config = MusicConfig()
    
    if not config.enabled:
        print("❌ Music generation disabled - check API key")
        return False
        
    api = GoAPIMusicAPI(config)
    
    try:
        print("🧪 Testing single generation...")
        result = await api.generate_music("peaceful ambient piano", style="ambient")
        
        if result:
            print("✅ Generation request successful!")
            print(f"   Task ID: {result.get('task_id', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            return True
        else:
            print("❌ No result returned")
            return False
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_quick_generation())
        if success:
            print(f"\n🎊 SUCCESS: GoAPI.ai Music-U integration working!")
        else:
            print(f"\n💥 FAILED: Still has issues")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
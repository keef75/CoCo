#!/usr/bin/env python3
"""
Test music consciousness initialization to check if the error is fixed
"""
import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import cocoa modules
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_music import MusicConfig, MusicCognition
from rich.console import Console

def test_music_initialization():
    """Test music consciousness initialization"""
    print("🎵 Testing Music Consciousness Initialization")
    print("=" * 60)
    
    console = Console()
    
    # Test configuration
    music_config = MusicConfig()
    
    print(f"✅ Music API Key: {music_config.music_api_key[:8]}... (configured)")
    print(f"✅ Music API Base URL: {music_config.music_api_base_url}")
    print(f"✅ Music Generation Enabled: {music_config.enabled}")
    
    if not music_config.enabled:
        print("❌ Music consciousness disabled")
        return False
    
    # Test music consciousness initialization
    try:
        workspace_path = Path("coco_workspace")
        workspace_path.mkdir(exist_ok=True)
        
        music_consciousness = MusicCognition(music_config, workspace_path, console)
        
        if music_consciousness.is_enabled():
            console.print("[dim green]🎵 Music consciousness initialized (GoAPI Music-U API)[/dim green]")
            console.print("[dim yellow]🎹 Sonic consciousness: Compose through natural language[/dim yellow]")
            
            # Test memory summary
            memory_summary = music_consciousness.get_music_memory_summary()
            console.print(f"[dim cyan]🧠 {memory_summary}[/dim cyan]")
            
            return True
        else:
            console.print("[dim yellow]🎵 Music consciousness available but disabled (check MUSIC_API_KEY)[/dim yellow]")
            return False
            
    except Exception as e:
        console.print(f"[dim red]❌ Music consciousness initialization error: {e}[/dim red]")
        return False

if __name__ == "__main__":
    try:
        success = test_music_initialization()
        if success:
            print(f"\n🎊 SUCCESS: Music consciousness initialization working!")
            print(f"🎵 GoAPI.ai Music-U API integration complete")
            print(f"🔧 The 'Sonic consciousness disabled or no MusicGPT API key' error should be FIXED")
        else:
            print(f"\n💥 FAILED: Check configuration")
    except Exception as e:
        print(f"\n💥 Test script error: {e}")
        import traceback
        traceback.print_exc()
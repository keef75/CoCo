#!/usr/bin/env python3
"""
Test script to verify that the background monitoring system is working
"""

import time
import json
from pathlib import Path

def check_active_generations():
    """Check for any active music generation tasks"""
    print("🔍 Checking for active music generation tasks...")
    
    # Check for composition metadata files (new system)
    music_dir = Path("coco_workspace/music/compositions")
    if music_dir.exists():
        metadata_files = list(music_dir.glob("*.json"))
        print(f"📁 Found {len(metadata_files)} composition metadata files")
        
        for metadata_file in metadata_files[-3:]:  # Show last 3
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                
                print(f"🎵 {metadata_file.name}:")
                print(f"   Prompt: {data.get('prompt', 'Unknown')}")
                print(f"   Status: {data.get('status', 'Unknown')}")
                print(f"   Task ID: {data.get('task_id', 'None')}")
                print(f"   Timestamp: {data.get('timestamp', 'Unknown')}")
                print()
                
            except Exception as e:
                print(f"❌ Error reading {metadata_file.name}: {e}")
    
    # Check for generated music files
    generated_dir = Path("coco_workspace/ai_songs/generated")
    if generated_dir.exists():
        music_files = list(generated_dir.glob("*.mp3"))
        metadata_files = list(generated_dir.glob("*.json"))
        print(f"🎧 Found {len(music_files)} MP3 files and {len(metadata_files)} metadata files in generated/")
        
        for music_file in music_files[-3:]:  # Show last 3
            stat = music_file.stat()
            print(f"🎶 {music_file.name} (Created: {time.ctime(stat.st_ctime)})")
    else:
        print("📂 No generated music directory found")

def main():
    """Test the background monitoring system"""
    print("🎼 Background Monitoring Test")
    print("=" * 50)
    
    check_active_generations()
    
    print("\n💡 To test background monitoring:")
    print("1. Start COCO: ./venv_cocoa/bin/python cocoa.py")
    print("2. Run: /compose test song")
    print("3. Watch for background monitoring messages")
    print("4. Check: /check-music")
    print("5. Look for files in coco_workspace/ai_songs/generated/")

if __name__ == "__main__":
    main()
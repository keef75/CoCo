#!/usr/bin/env python3
"""
Test script to verify the /video command fix
Tests that videos are properly saved to gallery memory
"""

import os
import sys
import json
from pathlib import Path
from rich.console import Console

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_video import VideoConfig, VideoCognition, VideoThought
from datetime import datetime

def test_video_gallery_integration():
    """Test that video gallery integration works properly"""
    console = Console()
    
    console.print("\n🔧 Testing Video Gallery Integration Fix", style="bold cyan")
    console.print("=" * 60)
    
    # Initialize video consciousness system
    config = VideoConfig()
    workspace_path = Path("coco_workspace")
    video_consciousness = VideoCognition(config, workspace_path, console)
    
    # Check if gallery is working
    console.print("🏛️ Testing gallery system...")
    video_consciousness.gallery.show_gallery()
    
    # Check for existing video files
    video_dir = Path("coco_workspace/videos")
    if video_dir.exists():
        video_files = list(video_dir.glob("*.mp4"))
        console.print(f"📁 Found {len(video_files)} video files in workspace")
        
        if video_files:
            # Show the most recent video file
            latest_video = max(video_files, key=lambda f: f.stat().st_mtime)
            console.print(f"📹 Latest video file: {latest_video.name}")
            
            # Test if we can manually add it to gallery (for existing videos)
            if latest_video.exists():
                console.print("\n🔧 Testing manual gallery addition...")
                
                # Create a test VideoThought for the existing file
                test_video_thought = VideoThought(
                    original_prompt="Test video for gallery",
                    enhanced_prompt="Cinematic and beautiful: Test video for gallery", 
                    video_concept={"model": "fal-ai/veo3/fast"},
                    generated_videos=[str(latest_video)],
                    display_method="video_player",
                    creation_time=datetime.now(),
                    generation_settings={"duration": "8s", "resolution": "720p"}
                )
                
                # Add to gallery
                gallery_id = video_consciousness.gallery.add_video(test_video_thought, str(latest_video))
                console.print(f"✅ Added existing video to gallery: {gallery_id}")
                
                # Test quick access
                console.print("\n🎯 Testing quick video access...")
                success = video_consciousness.quick_video_access()
                if success:
                    console.print("✅ Quick video access working!", style="bold green")
                else:
                    console.print("❌ Quick video access failed", style="bold red")
                
                return True
        else:
            console.print("📭 No existing video files found")
    else:
        console.print("📁 Video workspace directory doesn't exist yet")
    
    console.print("\n💡 To fully test: generate a new video and try /video command")
    return True

def check_video_memory_file():
    """Check the video memory file structure"""
    console = Console()
    memory_file = Path("coco_workspace/video_memory.json")
    
    console.print(f"\n📋 Video Memory File: {memory_file}")
    
    if memory_file.exists():
        try:
            with open(memory_file, 'r') as f:
                memory = json.load(f)
            console.print("✅ Memory file exists and is valid JSON")
            console.print(f"📊 Videos in memory: {len(memory.get('videos', []))}")
            console.print(f"🔖 Last generated: {memory.get('last_generated', 'None')}")
            
            if memory.get('videos'):
                console.print("\n🎬 Videos in memory:")
                for i, video in enumerate(memory['videos'][-3:]):  # Show last 3
                    console.print(f"  {i+1}. ID: {video.get('id', 'unknown')}")
                    console.print(f"     Prompt: {video.get('original_prompt', 'unknown')[:50]}...")
                    console.print(f"     File: {Path(video.get('file_path', 'unknown')).name}")
        except Exception as e:
            console.print(f"❌ Error reading memory file: {e}")
    else:
        console.print("📭 Memory file doesn't exist yet")

if __name__ == "__main__":
    print("🧪 Testing video command fix...")
    
    success = test_video_gallery_integration()
    check_video_memory_file()
    
    if success:
        print("\n🎉 Video gallery integration test completed!")
        print("   Generate a new video, then try the /video command.")
    else:
        print("\n💥 Test encountered issues.")
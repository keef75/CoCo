#!/usr/bin/env python3
"""
Test script for Fal AI Veo3 Fast API fix
Tests the corrected video generation with proper schema validation
"""

import os
import asyncio
from pathlib import Path
from rich.console import Console

# Add current directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_video import VideoConfig, FalAIVideoAPI

async def test_fal_api():
    """Test the corrected Fal AI implementation"""
    console = Console()
    
    console.print("\n🎬 Testing Fal AI Veo3 Fast API Fix", style="bold cyan")
    console.print("=" * 50)
    
    # Check API key
    fal_key = os.getenv("FAL_API_KEY")
    if not fal_key or fal_key == "your-fal-api-key-here":
        console.print("❌ FAL_API_KEY not set in environment", style="red")
        console.print("💡 Set with: export FAL_API_KEY=your-actual-key", style="yellow")
        return
    
    console.print(f"✅ FAL_API_KEY found: {fal_key[:10]}...", style="green")
    
    # Initialize video config and API
    config = VideoConfig()
    fal_api = FalAIVideoAPI(config)
    
    console.print(f"🔧 Default Duration: {config.default_duration}", style="cyan")
    console.print(f"🔧 Default Aspect Ratio: {config.default_aspect_ratio}", style="cyan")
    console.print(f"🔧 Default Resolution: {config.default_resolution}", style="cyan")
    
    # Test prompt
    test_prompt = "A dog walking on the beach, cinematic, beautiful lighting"
    
    console.print(f"\n🎯 Testing prompt: '{test_prompt}'", style="bold")
    
    try:
        # Test the fixed video generation
        console.print("\n⏳ Generating video with corrected API parameters...", style="yellow")
        
        video_info = await fal_api.generate_video(
            prompt=test_prompt,
            aspect_ratio="16:9",  # Valid option
            duration="8s",        # Only valid option  
            resolution="720p"     # Valid option
        )
        
        console.print("\n✅ Video generation successful!", style="bold green")
        console.print(f"📹 Video URL: {video_info['video_url']}")
        console.print(f"⏱️ Duration: {video_info['duration']}")
        console.print(f"🤖 Model: {video_info['model']}")
        
        return True
        
    except Exception as e:
        console.print(f"\n❌ Video generation failed: {str(e)}", style="red")
        
        # Show detailed error for debugging
        import traceback
        console.print("\n🔍 Full traceback:", style="yellow")
        console.print(traceback.format_exc(), style="dim")
        
        return False

if __name__ == "__main__":
    print("🧪 Running Fal AI API fix test...")
    result = asyncio.run(test_fal_api())
    
    if result:
        print("\n🎉 Test passed! Video generation is working.")
    else:
        print("\n💥 Test failed. Check the error details above.")
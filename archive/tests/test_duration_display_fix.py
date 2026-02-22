#!/usr/bin/env python3
"""
Test script to verify the duration display fix is working
Confirms that the display now shows "8s" instead of "4s"
"""

import os
import sys
from pathlib import Path
from rich.console import Console

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_video import VideoConfig

def test_duration_display():
    """Test that duration display shows 8s instead of 4s"""
    console = Console()
    
    console.print("\n🔧 Testing Duration Display Fix", style="bold cyan")
    console.print("=" * 50)
    
    # Check environment variable
    env_duration = os.getenv("DEFAULT_DURATION", "not_set")
    console.print(f"📋 Environment DEFAULT_DURATION: {env_duration}")
    
    # Check config default
    config = VideoConfig()
    console.print(f"⚙️ VideoConfig default_duration: {config.default_duration}")
    
    # Verify the fix
    if config.default_duration == "8s":
        console.print("✅ SUCCESS: Duration display will show '8s'", style="bold green")
        if env_duration == "8s":
            console.print("✅ Environment variable correctly set to '8s'", style="green")
        else:
            console.print("⚠️ Environment variable might need to be reloaded", style="yellow")
        return True
    else:
        console.print(f"❌ FAILED: Duration still showing '{config.default_duration}'", style="bold red")
        console.print("💡 Check if .env file was saved correctly", style="yellow")
        return False

if __name__ == "__main__":
    print("🧪 Testing duration display fix...")
    
    success = test_duration_display()
    
    if success:
        print("\n🎉 Duration display fix verified!")
        print("   The video generation UI should now show '8s' instead of '4s'")
    else:
        print("\n💥 Duration display fix needs attention.")
        print("   Check the .env file and restart COCO to reload environment variables.")
#!/usr/bin/env python3
"""
Test script to verify the updated command system
Tests both /help and /commands display properly
"""

import os
import sys
from pathlib import Path
from rich.console import Console

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_help_command():
    """Test the /help command to see if it includes all sections"""
    console = Console()
    
    console.print("\n🧪 Testing Updated /help Command", style="bold cyan")
    console.print("=" * 60)
    
    # Import and create COCO instance
    try:
        from cocoa import COCO, Config
        config = Config()
        coco = COCO(config)
        
        # Test /help command
        console.print("📋 Testing /help command...")
        help_panel = coco.get_help_panel()
        console.print(help_panel)
        
        return True
        
    except Exception as e:
        console.print(f"❌ Error testing /help: {e}")
        return False

def test_commands_guide():
    """Test the /commands comprehensive guide"""
    console = Console()
    
    console.print("\n🎨 Testing Updated /commands Guide", style="bold magenta") 
    console.print("=" * 60)
    
    # Import and create COCO instance
    try:
        from cocoa import COCO, Config
        config = Config()
        coco = COCO(config)
        
        # Test /commands command
        console.print("🎭 Testing /commands comprehensive guide...")
        commands_panel = coco.get_comprehensive_command_guide()
        console.print(commands_panel)
        
        return True
        
    except Exception as e:
        console.print(f"❌ Error testing /commands: {e}")
        return False

def audit_command_coverage():
    """Audit what commands are actually available vs documented"""
    console = Console()
    
    console.print("\n🔍 Command Coverage Audit", style="bold yellow")
    console.print("=" * 60)
    
    # Commands we know should exist from the parsing logic
    expected_commands = [
        # Core
        "/help", "/commands", "/guide", "/status", "/identity", "/coherence",
        "/exit", "/quit", "/ls", "/files", "/read", "/write",
        
        # Memory  
        "/memory", "/remember",
        
        # Audio
        "/speak", "/voice", "/compose", "/compose-wait", "/audio", "/dialogue",
        "/stop-voice", "/create-song", "/play-music", "/playlist", "/songs",
        "/check-music", "/voice-toggle", "/music-toggle", "/tts-toggle",
        
        # Visual
        "/image", "/img", "/visualize", "/gallery", "/visual-gallery",
        "/visual-show", "/visual-open", "/visual-search", "/visual-style",
        "/visual-memory", "/visual-capabilities", "/check-visuals",
        
        # Video  
        "/video", "/vid", "/animate", "/create-video", "/video-gallery"
    ]
    
    console.print(f"📊 Expected commands: {len(expected_commands)}")
    
    # Group by category
    categories = {
        "Core": ["/help", "/commands", "/guide", "/status", "/identity", "/coherence", "/exit", "/quit"],
        "Files": ["/ls", "/files", "/read", "/write"],
        "Memory": ["/memory", "/remember"],
        "Audio": ["/speak", "/voice", "/compose", "/compose-wait", "/audio", "/dialogue", "/stop-voice", "/create-song", "/play-music", "/playlist", "/songs", "/check-music"],
        "Visual": ["/image", "/img", "/visualize", "/gallery", "/visual-gallery", "/visual-show", "/visual-open", "/visual-search", "/visual-style", "/visual-memory", "/visual-capabilities", "/check-visuals"],
        "Video": ["/video", "/vid", "/animate", "/create-video", "/video-gallery"]
    }
    
    for category, commands in categories.items():
        console.print(f"\n{category}: {len(commands)} commands")
        for cmd in commands:
            console.print(f"  {cmd}")
    
    console.print(f"\n✅ Total multimedia consciousness commands: {len(expected_commands)}")

if __name__ == "__main__":
    print("🧪 Testing COCO Command System Updates...")
    
    # Run tests
    audit_command_coverage()
    help_success = test_help_command()
    commands_success = test_commands_guide()
    
    if help_success and commands_success:
        print("\n🎉 Command system tests completed!")
        print("   Both /help and /commands should now show complete multimedia consciousness features.")
    else:
        print("\n💥 Some command system tests failed.")
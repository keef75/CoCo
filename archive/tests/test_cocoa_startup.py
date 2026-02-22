#!/usr/bin/env python3
"""
Test COCOA Startup and Music Command
====================================
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add current directory to path
sys.path.insert(0, '/Users/keithlambert/Desktop/Cocoa 0.1')

def test_cocoa_startup():
    print("🧠 Testing COCOA Startup...")
    
    try:
        # Import main COCOA class
        from cocoa import COCOA
        print("✅ COCOA imports successfully")
        
        # Create COCOA instance (this should initialize audio consciousness)
        cocoa = COCOA()
        print("✅ COCOA instance created")
        
        # Check if audio consciousness is available
        if hasattr(cocoa, 'audio_consciousness') and cocoa.audio_consciousness:
            print("✅ Audio consciousness initialized")
            
            # Check if music generation is enabled
            if cocoa.audio_consciousness.config.music_generation_enabled:
                print("✅ Music generation enabled - /compose should work!")
            else:
                print("❌ Music generation disabled")
                
        else:
            print("❌ Audio consciousness not available")
            
        return cocoa
        
    except Exception as e:
        print(f"❌ COCOA startup failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    cocoa = test_cocoa_startup()
    
    if cocoa and hasattr(cocoa, 'audio_consciousness') and cocoa.audio_consciousness:
        print("\n🎵 Music system ready!")
        print("You can now use: /compose techno")
    else:
        print("\n❌ Music system not ready")
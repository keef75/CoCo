#!/usr/bin/env python3
"""
Test COCOA Music Integration
============================
Test if COCOA can properly initialize audio consciousness with API keys
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_cocoa_music():
    print("🎵 Testing COCOA Music Integration")
    print("=" * 50)
    
    # Check environment variables
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    musicgpt_key = os.getenv('MUSICGPT_API_KEY')
    
    print(f"ElevenLabs Key: {'✅ Found' if elevenlabs_key else '❌ Missing'}")
    print(f"MusicGPT Key: {'✅ Found' if musicgpt_key else '❌ Missing'}")
    
    if not musicgpt_key:
        print("\n❌ MusicGPT API key missing - music generation won't work")
        return
    
    try:
        # Test audio system import
        from cocoa_audio import AudioCognition
        print("✅ cocoa_audio imports successfully")
        
        # Test audio cognition initialization
        audio = AudioCognition(
            elevenlabs_api_key=elevenlabs_key,
            musicgpt_api_key=musicgpt_key
        )
        print("✅ AudioCognition initialized successfully")
        
        # Check configuration
        if audio.config.music_generation_enabled:
            print("✅ Music generation enabled")
        else:
            print("❌ Music generation disabled")
            
        if audio.config.musicgpt_api_key:
            print("✅ MusicGPT API key loaded")
        else:
            print("❌ MusicGPT API key not loaded")
            
        print("\n🎼 Ready for music generation!")
        print("Try: /compose techno")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Initialization error: {e}")

if __name__ == "__main__":
    test_cocoa_music()
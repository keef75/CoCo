#!/usr/bin/env python3
"""
Quick test of the new spinner system
===================================
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_spinner():
    print("🎵 Testing Spinner System")
    print("=" * 30)
    
    try:
        from cocoa_audio import AudioCognition
        
        elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        musicgpt_key = os.getenv('MUSICGPT_API_KEY')
        
        audio = AudioCognition(
            elevenlabs_api_key=elevenlabs_key,
            musicgpt_api_key=musicgpt_key
        )
        
        print("✅ AudioCognition initialized")
        print("🎵 Testing spinner workflow...")
        
        # Test the spinner system with a short concept
        result = await audio.create_and_play_music(
            concept="test spinner",
            duration=10,  # Short duration for testing
            auto_play=False
        )
        
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_spinner())
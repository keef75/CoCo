#!/usr/bin/env python3
"""Quick audio test"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def quick_test():
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    musicgpt_key = os.getenv("MUSICGPT_API_KEY")
    
    if not elevenlabs_key or elevenlabs_key == "your-elevenlabs-api-key-here":
        print("❌ Please add your ElevenLabs API key to .env first!")
        return
        
    if not musicgpt_key or musicgpt_key == "your-musicgpt-api-key-here":
        print("⚠️ MusicGPT API key not found - music generation will be disabled")
        print("✅ Voice synthesis available with ElevenLabs")
    else:
        print("✅ Both API keys found!")
    
    print("\nTesting basic imports...")
    
    try:
        from cocoa_audio import AudioCognition
        print("✅ Audio system imports successfully!")
        
        # Initialize
        audio = AudioCognition(elevenlabs_key, musicgpt_key)
        print("✅ Audio cognition initialized!")
        
        if musicgpt_key and musicgpt_key != "your-musicgpt-api-key-here":
            print("🎵 Music generation ready!")
        
        print("\n✨ All tests passed! Audio system is ready.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure cocoa_audio.py is properly installed")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())

#!/usr/bin/env python3
"""
Test the final COCO TTS implementation
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_coco_tts():
    """Test COCO's TTS system after fixes"""
    
    print("🧪 Testing COCO TTS System")
    print("=" * 40)
    
    # Test 1: Audio consciousness initialization
    print("1. Testing audio consciousness...")
    try:
        from cocoa_audio import create_audio_consciousness
        
        audio = create_audio_consciousness()
        if audio and audio.config.enabled:
            print("   ✅ Audio consciousness initialized and enabled")
            print(f"   🔑 API key configured: {bool(audio.config.elevenlabs_api_key)}")
        else:
            print("   ❌ Audio consciousness not properly configured")
            return False
            
    except Exception as e:
        print(f"   ❌ Audio consciousness error: {e}")
        return False
    
    # Test 2: COCO initialization 
    print("2. Testing COCO integration...")
    try:
        # Import what we need without full initialization
        from cocoa import Config
        
        config = Config()
        print("   ✅ COCO config initialized")
        print(f"   🔑 ElevenLabs key present: {bool(os.getenv('ELEVENLABS_API_KEY'))}")
        
    except Exception as e:
        print(f"   ❌ COCO integration error: {e}")
        return False
    
    # Test 3: Direct TTS call
    print("3. Testing direct TTS...")
    try:
        from elevenlabs import ElevenLabs
        
        client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        
        # Generate short test audio
        audio_generator = client.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            output_format="mp3_44100_128", 
            text="COCO TTS is now working correctly.",
            model_id="eleven_multilingual_v2"
        )
        
        audio_bytes = b''.join(audio_generator)
        print(f"   ✅ TTS generation successful: {len(audio_bytes)} bytes")
        
        # Test playback
        from elevenlabs import play
        play(audio_bytes)
        print("   ✅ TTS playback completed")
        
    except Exception as e:
        print(f"   ❌ Direct TTS error: {e}")
        return False
    
    print("=" * 40)
    print("✅ ALL TESTS PASSED!")
    print()
    print("🎉 COCO TTS System Status:")
    print("   ✅ ElevenLabs TTS working")
    print("   ✅ Audio consciousness enabled") 
    print("   ✅ /voice-on command should work")
    print("   ✅ /speak command should work")
    print("   ❌ Music system disabled (as requested)")
    print()
    print("🚀 Ready to start COCO with: ./venv_cocoa/bin/python cocoa.py")
    
    return True

if __name__ == "__main__":
    success = test_coco_tts()
    if not success:
        print("❌ Some tests failed - check your configuration")
        sys.exit(1)
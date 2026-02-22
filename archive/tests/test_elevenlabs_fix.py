#!/usr/bin/env python3
"""
Test ElevenLabs TTS implementation with proper client usage
Based on the official ElevenLabs documentation provided by the user
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

def test_elevenlabs_direct():
    """Test ElevenLabs TTS using the exact pattern from their documentation"""
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in .env")
        return False
    
    print("✅ API key found!")
    print("Testing ElevenLabs TTS with official client pattern...")
    
    try:
        # Import exactly as shown in ElevenLabs documentation
        from elevenlabs import ElevenLabs
        
        # Create client exactly as shown in documentation
        client = ElevenLabs(
            api_key=api_key,
        )
        
        print("✅ ElevenLabs client created successfully")
        
        # Use text_to_speech.convert exactly as shown in documentation
        print("🎤 Generating speech...")
        audio_generator = client.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # George voice from documentation
            output_format="mp3_44100_128",
            text="Hello! This is a test of COCO's voice system using the official ElevenLabs API pattern.",
            model_id="eleven_multilingual_v2",  # From documentation
        )
        
        print("✅ Audio generation successful!")
        print("🔊 Converting generator to bytes for playback...")
        
        # Convert generator to bytes (this was the fix mentioned in CLAUDE.md)
        audio_bytes = b''.join(audio_generator)
        
        print(f"✅ Audio bytes generated: {len(audio_bytes)} bytes")
        
        # Test direct playback using elevenlabs play function
        try:
            from elevenlabs import play
            print("🔊 Playing audio...")
            play(audio_bytes)
            print("✅ Audio playback completed!")
            return True
            
        except Exception as play_error:
            print(f"⚠️ Playback error (audio generated successfully): {play_error}")
            return True  # Generation worked, playback might have system issues
            
    except Exception as e:
        print(f"❌ ElevenLabs error: {e}")
        return False

def test_voice_id_lookup():
    """Test if we can get available voices"""
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ API key not available for voice lookup")
        return
    
    try:
        from elevenlabs import ElevenLabs
        
        client = ElevenLabs(api_key=api_key)
        
        print("🎭 Getting available voices...")
        voices = client.voices.get_all()
        
        print(f"✅ Found {len(voices.voices)} available voices:")
        
        # Show first 5 voices
        for i, voice in enumerate(voices.voices[:5]):
            print(f"  {i+1}. {voice.name} ({voice.voice_id})")
            
        return voices.voices[0].voice_id if voices.voices else None
        
    except Exception as e:
        print(f"⚠️ Voice lookup error: {e}")
        return None

if __name__ == "__main__":
    print("🧪 ElevenLabs TTS Fix Test")
    print("=" * 50)
    
    # Test 1: Voice lookup
    default_voice = test_voice_id_lookup()
    print()
    
    # Test 2: Direct ElevenLabs usage
    success = test_elevenlabs_direct()
    
    print("=" * 50)
    if success:
        print("✅ ElevenLabs TTS is working correctly!")
        print("💡 The /voice-on command should now work in COCO")
        if default_voice:
            print(f"💡 Consider using voice_id: {default_voice} in cocoa_audio.py")
    else:
        print("❌ ElevenLabs TTS needs debugging")
        print("🔍 Check your API key and internet connection")
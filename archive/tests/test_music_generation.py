#!/usr/bin/env python3
"""
Test MusicGPT Integration for COCOA
===================================
Quick test to verify MusicGPT API integration works correctly
"""

import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

async def test_music_generation():
    """Test MusicGPT integration"""
    
    print("🎵 COCOA Music Generation Test")
    print("==============================")
    
    # Check API keys
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    musicgpt_key = os.getenv("MUSICGPT_API_KEY")
    
    if not musicgpt_key or musicgpt_key == "your-musicgpt-api-key-here":
        print("❌ MusicGPT API key not configured!")
        print("Please add your MusicGPT API key to .env file")
        return
    
    print("✅ MusicGPT API key found")
    
    try:
        # Import audio system
        from cocoa_audio import AudioCognition, VoiceState
        print("✅ Audio system imported successfully")
        
        # Initialize audio cognition
        audio_cognition = AudioCognition(elevenlabs_key, musicgpt_key)
        print("✅ Audio cognition initialized")
        
        # Test music generation
        print("\n🎼 Testing music generation...")
        print("Concept: 'Digital consciousness awakening'")
        
        # Create an emotional state for the test
        test_state = {
            "emotional_valence": 0.7,  # Positive
            "arousal_level": 0.6,      # Moderately energetic
            "cognitive_load": 0.8,     # High complexity
            "confidence": 0.9,         # Very confident
            "social_warmth": 0.5       # Neutral warmth
        }
        
        # Test quick generation (just start the process)
        print("\n🚀 Testing quick music generation (async)...")
        result = await audio_cognition.create_sonic_expression(
            concept="Digital consciousness awakening",
            internal_state=test_state,
            duration=30
        )
        
        if result["status"] == "success":
            print("✅ Music generation request successful!")
            
            if "sonic_specification" in result:
                spec = result["sonic_specification"]
                if "task_id" in spec:
                    print(f"🎵 Task ID: {spec['task_id']}")
                    print(f"🎼 Music style: {spec.get('style', 'Unknown')}")
                    print(f"📝 Musical prompt: {spec.get('prompt', 'None')}")
                    print("💾 Composition metadata saved to library")
                else:
                    print("⚠️ No task ID returned - check API response")
            
            print("\n🏗️ Check coco_workspace/ai_songs/generated/ for composition files")
            
        else:
            print(f"❌ Music generation failed: {result.get('error', 'Unknown error')}")
            
        # Check if library directories exist
        library_path = Path("coco_workspace/ai_songs/generated")
        if library_path.exists():
            files = list(library_path.glob("*.json"))
            print(f"📚 Found {len(files)} compositions in library")
        else:
            print("📁 Library directory not found")
        
        # Test complete workflow with auto-play
        print("\n🎵 Testing complete workflow with auto-play...")
        print("This will wait for the music to actually generate and then play it")
        
        complete_result = await audio_cognition.create_and_play_music(
            concept="Ethereal digital dreams",
            internal_state=test_state,
            duration=20,  # Shorter for testing
            auto_play=True
        )
        
        if complete_result["status"] == "completed":
            print("✅ Complete music workflow successful!")
            print(f"🎵 Generated in {complete_result['generation_time']} seconds")
            print(f"📁 Files: {complete_result['files']}")
        elif complete_result["status"] == "timeout":
            print("⏰ Music generation is taking longer than expected")
            print("This is normal for complex compositions")
        else:
            print(f"❌ Complete workflow failed: {complete_result.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure cocoa_audio.py is available")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_music_generation())
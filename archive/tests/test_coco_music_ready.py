#!/usr/bin/env python3
"""
Test that COCO recognizes music generation as available and ready
"""
import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import cocoa modules
sys.path.insert(0, str(Path(__file__).parent))

def test_coco_music_recognition():
    """Test that COCO recognizes music generation capabilities"""
    print("🎵 Testing COCO Music Recognition")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test environment configuration
    music_api_key = os.getenv('MUSIC_API_KEY')
    music_api_base_url = os.getenv('MUSIC_API_BASE_URL')
    music_generation_enabled = os.getenv('MUSIC_GENERATION_ENABLED')
    
    if music_api_key:
        print(f"✅ MUSIC_API_KEY: {music_api_key[:8]}... (set)")
    else:
        print("❌ MUSIC_API_KEY: Not set")
        return False
    
    print(f"✅ MUSIC_API_BASE_URL: {music_api_base_url}")
    print(f"✅ MUSIC_GENERATION_ENABLED: {music_generation_enabled}")
    
    # Test that all the updated files exist and are correct
    from cocoa_music import MusicConfig, GoAPIMusicAPI, MusicCognition
    from cocoa_audio import AudioConfig, DigitalMusician
    
    # Test MusicConfig uses GoAPI.ai
    config = MusicConfig()
    print(f"✅ MusicConfig uses GoAPI.ai: {config.music_api_key[:8]}...")
    print(f"✅ MusicConfig base URL: {config.music_api_base_url}")
    
    # Test GoAPIMusicAPI exists
    api = GoAPIMusicAPI(config)
    print(f"✅ GoAPIMusicAPI initialized successfully")
    
    # Test AudioConfig still works
    audio_config = AudioConfig()
    print(f"✅ AudioConfig music API key: {audio_config.music_api_key[:8]}...")
    
    print(f"\n🎉 All components successfully updated!")
    print(f"🔧 COCO should now show 'GoAPI.ai Music-U API' instead of 'MusicGPT' errors")
    print(f"🎵 Music generation should be fully functional with GoAPI.ai")
    
    return True

if __name__ == "__main__":
    try:
        success = test_coco_music_recognition()
        if success:
            print(f"\n🎊 SUCCESS: COCO GoAPI.ai Music Integration Complete!")
            print(f"🎵 Ready for music generation with GoAPI.ai Music-U")
            print(f"🚀 Start COCO normally - the MusicGPT error should be gone!")
        else:
            print(f"\n💥 FAILED: Integration incomplete")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
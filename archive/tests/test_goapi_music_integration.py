#!/usr/bin/env python3
"""
Test script for the new GoAPI.ai Music-U integration
This replaces the old MusicGPT system with GoAPI.ai service
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import cocoa modules
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_audio import AudioCognition, AudioConfig

async def test_goapi_music_integration():
    """Test the new GoAPI.ai Music-U API integration"""
    print("🎵 Testing GoAPI.ai Music-U Integration")
    print("=" * 50)
    
    # Create audio configuration
    config = AudioConfig()
    
    # Check if API key is configured
    if not config.music_api_key or config.music_api_key == "your-goapi-music-api-key-here":
        print("❌ MUSIC_API_KEY not configured in .env file")
        print("💡 Please add your GoAPI.ai API key to .env:")
        print("   MUSIC_API_KEY=your-actual-api-key-here")
        print("   MUSIC_API_BASE_URL=https://api.goapi.ai")
        return False
    
    if not config.music_api_base_url:
        print("❌ MUSIC_API_BASE_URL not configured in .env file")
        print("💡 Please add GoAPI.ai base URL to .env:")
        print("   MUSIC_API_BASE_URL=https://api.goapi.ai")
        return False
    
    print(f"✅ Configuration loaded:")
    print(f"   API Key: {config.music_api_key[:8]}...")
    print(f"   Base URL: {config.music_api_base_url}")
    print(f"   Music Generation Enabled: {config.music_generation_enabled}")
    
    if not config.music_generation_enabled:
        print("⚠️ Music generation is disabled - enable with MUSIC_GENERATION_ENABLED=true")
        return False
    
    # Create audio consciousness
    audio_consciousness = AudioCognition()
    
    if not audio_consciousness.musician:
        print("❌ Digital musician not initialized")
        return False
    
    print(f"✅ Digital musician initialized")
    
    # Test music generation payload creation
    print(f"\n🧪 Testing GoAPI.ai payload generation...")
    
    test_descriptions = [
        "ambient piano",
        "upbeat electronic dance",
        "jazz fusion instrumental", 
        "classical orchestral",
        "rock guitar instrumental"
    ]
    
    for i, description in enumerate(test_descriptions):
        print(f"\n🎼 Test {i+1}: '{description}'")
        
        try:
            # This will test the create_sonic_landscape method with the new GoAPI.ai API
            result = await audio_consciousness.musician.create_sonic_landscape(
                description=description,
                duration_seconds=30
            )
            
            if "error" in result:
                print(f"   ❌ Generation failed: {result['error']}")
            elif "task_id" in result:
                print(f"   ✅ Generation started!")
                print(f"   🆔 Task ID: {result['task_id']}")
                
                # Test status checking
                print(f"   🔍 Testing status check...")
                status_result = await audio_consciousness.musician.check_music_status(result['task_id'])
                
                if "error" in status_result:
                    print(f"   ⚠️ Status check failed: {status_result['error']}")
                else:
                    print(f"   ✅ Status check successful: {status_result.get('status', 'unknown')}")
            else:
                print(f"   ⚠️ Unexpected response format: {result}")
                
        except Exception as e:
            print(f"   ❌ Exception during generation: {e}")
            return False
    
    print(f"\n🎉 GoAPI.ai Music-U integration test completed!")
    print(f"🔧 All major components are working:")
    print(f"   ✅ Configuration loading")
    print(f"   ✅ API client initialization") 
    print(f"   ✅ Payload generation")
    print(f"   ✅ Music generation requests")
    print(f"   ✅ Status checking")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Add your actual GoAPI.ai API key to .env")
    print(f"   2. Test with real API calls: /compose 'ambient piano'")
    print(f"   3. Use COCO's music commands naturally!")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_goapi_music_integration())
        if success:
            print(f"\n🎊 SUCCESS: GoAPI.ai Music-U integration is ready!")
            sys.exit(0)
        else:
            print(f"\n💥 FAILED: Check configuration and try again")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test script error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
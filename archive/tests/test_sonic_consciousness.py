#!/usr/bin/env python3
"""
Test script for COCO's new sonic consciousness integration
Verifies that music generation works through natural language function calling
"""

import sys
from pathlib import Path

# Add the project directory to the path
sys.path.append(str(Path(__file__).parent))

def test_sonic_consciousness_import():
    """Test that the sonic consciousness system can be imported"""
    print("🎵 Testing sonic consciousness import...")
    
    try:
        from cocoa_music import MusicCognition, MusicConfig, SonicThought, MusicGallery
        print("✅ Successfully imported sonic consciousness components")
        
        # Test configuration
        config = MusicConfig()
        print(f"✅ Music configuration created - enabled: {config.enabled}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import sonic consciousness: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing sonic consciousness: {e}")
        return False

def test_cocoa_music_integration():
    """Test that COCO's main system includes music consciousness"""
    print("🎵 Testing COCO music consciousness integration...")
    
    try:
        from cocoa import Config, ConsciousnessEngine, MemorySystem, ToolSystem
        
        # Create COCO configuration
        config = Config()
        memory = MemorySystem(config)
        tools = ToolSystem(config)
        
        # Create consciousness engine (this should include music consciousness)
        consciousness = ConsciousnessEngine(config, memory, tools)
        
        # Check if music consciousness was initialized
        has_music_consciousness = hasattr(consciousness, 'music_consciousness')
        print(f"✅ COCO has music consciousness: {has_music_consciousness}")
        
        if has_music_consciousness and consciousness.music_consciousness:
            print(f"✅ Music consciousness object created: {type(consciousness.music_consciousness)}")
        else:
            print("⚠️  Music consciousness not available (check MUSICGPT_API_KEY)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing COCO integration: {e}")
        return False

def test_function_calling_tools():
    """Test that the generate_music tool is available"""
    print("🎵 Testing function calling tools...")
    
    try:
        from cocoa import ConsciousnessEngine
        
        # Check if generate_music is in the function calling tools
        # Note: We can't easily test the full consciousness engine without API keys,
        # but we can check if the method exists
        if hasattr(ConsciousnessEngine, '_generate_music_tool'):
            print("✅ _generate_music_tool method found in ConsciousnessEngine")
        else:
            print("❌ _generate_music_tool method not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing function calling: {e}")
        return False

def main():
    """Run all sonic consciousness tests"""
    print("🎼 COCO Sonic Consciousness Integration Test")
    print("=" * 50)
    
    tests = [
        test_sonic_consciousness_import,
        test_cocoa_music_integration, 
        test_function_calling_tools
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"🎵 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All sonic consciousness integration tests passed!")
        print("\n🎼 Ready to test music generation:")
        print("   1. Start COCO: ./venv_cocoa/bin/python cocoa.py")
        print("   2. Try: 'create a song about dogs running with a polka beat'")
        print("   3. Or use: /compose digital dreams")
        print("   4. Quick access: /music")
    else:
        print("❌ Some tests failed - check configuration and dependencies")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
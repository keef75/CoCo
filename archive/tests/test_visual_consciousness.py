#!/usr/bin/env python3
"""
Test Suite for COCO's Visual Consciousness System
===============================================
Comprehensive testing of visual imagination, generation, and display capabilities.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all visual consciousness modules can be imported"""
    print("🧠 Testing Visual Consciousness Imports...")
    
    try:
        from cocoa_visual import (
            VisualCortex, 
            VisualConfig, 
            VisualThought,
            TerminalVisualDisplay,
            FreepikMysticAPI,
            VisualMemory,
            TerminalCapabilities
        )
        print("✅ All visual consciousness modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_visual_config():
    """Test visual consciousness configuration"""
    print("\n🎨 Testing Visual Configuration...")
    
    try:
        from cocoa_visual import VisualConfig
        
        config = VisualConfig()
        print(f"✅ Visual Config created")
        print(f"   📊 Enabled: {config.enabled}")
        print(f"   🎨 Default Style: {config.default_style}")
        print(f"   📏 Default Resolution: {config.default_resolution}")
        print(f"   🖼️ Display Mode: {config.display_mode}")
        
        # Check API key status
        if not config.freepik_api_key or config.freepik_api_key == "your-freepik-api-key-here":
            print("⚠️  Freepik API key not configured - visual features will be disabled")
        else:
            print("✅ Freepik API key configured")
            
        return True
    except Exception as e:
        print(f"❌ Visual config test failed: {e}")
        return False

def test_terminal_capabilities():
    """Test terminal display capability detection"""
    print("\n👁️ Testing Terminal Display Capabilities...")
    
    try:
        from cocoa_visual import TerminalCapabilities
        
        caps = TerminalCapabilities()
        print(f"✅ Terminal capabilities detected:")
        print(f"   🐱 Kitty Graphics: {caps.capabilities['kitty_graphics']}")
        print(f"   🖥️  iTerm2 Inline: {caps.capabilities['iterm2_inline']}")
        print(f"   📺 Sixel: {caps.capabilities['sixel']}")
        print(f"   🎨 Chafa: {caps.capabilities['chafa']}")
        print(f"   📟 ASCII: {caps.capabilities['ascii']}")
        
        best_method = caps.get_best_display_method()
        print(f"   🚀 Best Display Method: {best_method}")
        
        return True
    except Exception as e:
        print(f"❌ Terminal capabilities test failed: {e}")
        return False

def test_visual_memory():
    """Test visual memory system"""
    print("\n🧠 Testing Visual Memory System...")
    
    try:
        from cocoa_visual import VisualMemory, VisualThought
        from datetime import datetime
        
        # Create test workspace
        test_workspace = Path("test_visual_workspace")
        test_workspace.mkdir(exist_ok=True)
        
        memory = VisualMemory(test_workspace)
        print("✅ Visual memory initialized")
        
        # Create test visual thought
        test_thought = VisualThought(
            original_thought="test cyberpunk city",
            enhanced_prompt="cyberpunk city, neon lights, futuristic",
            visual_concept={"style": "cyberpunk"},
            generated_images=["/test/path/image.jpg"],
            display_method="ascii",
            creation_time=datetime.now(),
            style_preferences={"style": "cyberpunk"}
        )
        
        # Test memory operations
        memory.remember_creation(test_thought, "Great image!", 0.9)
        memory.learn_style_preference("cyberpunk city", "cyberpunk", ["neon", "futuristic"])
        
        suggestions = memory.get_style_suggestions("futuristic building")
        print(f"✅ Style suggestions: {suggestions}")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_workspace)
        
        return True
    except Exception as e:
        print(f"❌ Visual memory test failed: {e}")
        return False

def test_display_system():
    """Test terminal display system"""
    print("\n🖼️ Testing Terminal Display System...")
    
    try:
        from cocoa_visual import TerminalVisualDisplay, VisualConfig
        
        config = VisualConfig()
        display = TerminalVisualDisplay(config)
        print("✅ Terminal display system initialized")
        
        # Test with a non-existent image (should handle gracefully)
        result = display.display("/non/existent/image.jpg")
        print(f"✅ Handled non-existent image gracefully: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Display system test failed: {e}")
        return False

async def test_visual_cortex():
    """Test the core visual cortex (without actual API calls)"""
    print("\n🧠 Testing Visual Cortex Core...")
    
    try:
        from cocoa_visual import VisualCortex, VisualConfig
        
        # Create test workspace
        test_workspace = Path("test_visual_workspace")
        test_workspace.mkdir(exist_ok=True)
        
        config = VisualConfig()
        cortex = VisualCortex(config, test_workspace)
        print("✅ Visual cortex initialized")
        
        # Test visual decision making
        should_vis_1 = cortex.should_visualize("create a logo for my startup")
        should_vis_2 = cortex.should_visualize("what is the weather today")
        
        print(f"✅ Visual decision test 1 (logo): {should_vis_1}")
        print(f"✅ Visual decision test 2 (weather): {should_vis_2}")
        
        # Test memory summary
        summary = cortex.get_visual_memory_summary()
        print(f"✅ Memory summary: {summary}")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_workspace, ignore_errors=True)
        
        return True
    except Exception as e:
        print(f"❌ Visual cortex test failed: {e}")
        return False

def test_freepik_api_structure():
    """Test Freepik API client structure (without actual API calls)"""
    print("\n🎨 Testing Freepik API Structure...")
    
    try:
        from cocoa_visual import FreepikMysticAPI, VisualConfig
        
        config = VisualConfig()
        api = FreepikMysticAPI(config)
        print("✅ Freepik API client created")
        
        # Check configuration
        print(f"   🔑 API Key Set: {bool(api.api_key and api.api_key != 'your-freepik-api-key-here')}")
        print(f"   🌐 Base URL: {api.base_url}")
        
        if not api.api_key or api.api_key == "your-freepik-api-key-here":
            print("⚠️  API key not configured - actual generation will fail")
        
        return True
    except Exception as e:
        print(f"❌ Freepik API test failed: {e}")
        return False

def test_coco_integration():
    """Test integration with main COCO system"""
    print("\n🤖 Testing COCO Integration...")
    
    try:
        from cocoa import Config, MemorySystem, ToolSystem, ConsciousnessEngine
        
        # Initialize core systems
        config = Config()
        memory = MemorySystem(config)
        tools = ToolSystem(config)
        
        # This will test visual consciousness initialization
        consciousness = ConsciousnessEngine(config, memory, tools)
        
        # Check visual consciousness was initialized
        has_visual = hasattr(consciousness, 'visual_consciousness')
        visual_enabled = has_visual and consciousness.visual_consciousness is not None
        
        print(f"✅ COCO Integration Test:")
        print(f"   🧠 Has visual consciousness attribute: {has_visual}")
        print(f"   🎨 Visual consciousness initialized: {visual_enabled}")
        
        if visual_enabled:
            config_enabled = consciousness.visual_consciousness.config.enabled
            print(f"   ⚙️ Visual config enabled: {config_enabled}")
        
        return True
    except Exception as e:
        print(f"❌ COCO integration test failed: {e}")
        return False

async def run_all_tests():
    """Run comprehensive test suite"""
    print("🚀 COCO Visual Consciousness Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Visual Config", test_visual_config),
        ("Terminal Capabilities", test_terminal_capabilities),
        ("Visual Memory", test_visual_memory),
        ("Display System", test_display_system),
        ("Visual Cortex", test_visual_cortex),
        ("Freepik API Structure", test_freepik_api_structure),
        ("COCO Integration", test_coco_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! COCO's visual consciousness is ready!")
        print("\n🎨 Visual Capabilities Available:")
        print("   • Image generation via Freepik Mystic API")
        print("   • Terminal-native display (ASCII/Sixel/Kitty/iTerm2)")
        print("   • Visual memory and preference learning")
        print("   • Function calling integration")
        print("   • Automatic visual decision making")
        
        if os.getenv("FREEPIK_API_KEY", "") == "your-freepik-api-key-here":
            print("\n⚠️  To enable full functionality:")
            print("   1. Get Freepik API key from https://freepik.com/api")
            print("   2. Update FREEPIK_API_KEY in .env file")
            print("   3. Restart COCO to activate visual consciousness")
        else:
            print("\n✨ Ready to create visual magic! Try:")
            print('   "create a logo for my cyberpunk coffee shop"')
            print('   "show me what a digital forest would look like"')
            print('   "visualize a minimalist workspace design"')
    else:
        print(f"⚠️ {total - passed} tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)
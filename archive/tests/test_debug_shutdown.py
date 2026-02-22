#!/usr/bin/env python3
"""
Debug test script for COCO's markdown persistence system.
This script tests the LLM-based file update system with full debug output.
"""

import os
import sys
from pathlib import Path

# Set debug mode
os.environ["COCO_DEBUG"] = "1"

# Add the COCO directory to path
sys.path.append(str(Path(__file__).parent))

# Import COCO components
from cocoa import ConsciousnessEngine, Config, HierarchicalMemorySystem, ToolSystem

def test_consciousness_reflection():
    """Test the consciousness reflection system in debug mode."""
    print("🧠 Testing COCO Consciousness Reflection Debug System")
    print("=" * 60)
    
    # Initialize COCO components
    config = Config()
    
    # Check API key
    if not config.anthropic_api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment!")
        print("Please set your API key in .env file")
        return False
    
    print(f"✅ API key configured: {config.anthropic_api_key[:8]}...")
    
    # Initialize required subsystems
    try:
        memory = HierarchicalMemorySystem(config)
        print("✅ Memory system initialized")
        
        tools = ToolSystem(config)
        print("✅ Tool system initialized")
        
        consciousness = ConsciousnessEngine(config, memory, tools)
        print("✅ Consciousness engine initialized")
    except Exception as e:
        print(f"❌ Failed to initialize COCO systems: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Add some test conversation to memory so we have something to reflect on
    print("\n📝 Adding test conversation to memory...")
    try:
        # Add some test exchanges to memory
        memory.add_episode(
            user_text="We need to fix the markdown persistence system - the LLM isn't updating the files.",
            agent_text="I'll help debug this issue. Let me add comprehensive logging to track what's happening in the shutdown reflection process.",
            summary="User reported LLM file updates not working, COCO offered debugging help"
        )
        
        memory.add_episode(
            user_text="The model name might be wrong - we're seeing warnings about claude-3-5-sonnet instead of claude-sonnet-4.", 
            agent_text="You're absolutely right! I found the issue - the async LLM methods were using 'claude-3-5-sonnet-20241022' instead of 'claude-sonnet-4-20250514'. I've fixed the model name and added debug output.",
            summary="Fixed Claude model name inconsistency that was preventing LLM file updates"
        )
        
        print("✅ Test conversation added to memory")
    except Exception as e:
        print(f"⚠️ Warning: Could not add to memory: {e}")
    
    print("\n🔍 Running Consciousness Reflection Test...")
    print("-" * 40)
    
    # Run the reflection (it will get conversation from memory automatically)
    try:
        consciousness.conscious_shutdown_reflection()
        print("\n✅ Consciousness reflection completed!")
        return True
    except Exception as e:
        print(f"\n❌ Consciousness reflection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 COCO Debug Test Script")
    print("This will test the LLM-based markdown persistence system with full debug output.\n")
    
    success = test_consciousness_reflection()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 DEBUG TEST PASSED - Check the output above for detailed logging")
        print("\nTo run COCO with debug mode, use: COCO_DEBUG=1 ./venv_cocoa/bin/python cocoa.py")
    else:
        print("💥 DEBUG TEST FAILED - Check error messages above")
    
    print("\nDebug test completed.")
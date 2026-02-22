#!/usr/bin/env python3
"""
Direct test of the LLM response system to verify it's working correctly.
"""

import os
import sys
import asyncio
from pathlib import Path

# Set debug mode
os.environ["COCO_DEBUG"] = "1"

# Add the COCO directory to path
sys.path.append(str(Path(__file__).parent))

# Import COCO components
from cocoa import ConsciousnessEngine, Config, HierarchicalMemorySystem, ToolSystem

async def test_llm_direct():
    """Direct test of the _get_llm_response_async method."""
    print("🧠 Direct LLM Test with Debug Output")
    print("=" * 50)
    
    # Initialize COCO components  
    config = Config()
    
    if not config.anthropic_api_key:
        print("❌ ANTHROPIC_API_KEY not found!")
        return False
    
    print(f"✅ API key: {config.anthropic_api_key[:8]}...")
    
    # Initialize systems
    memory = HierarchicalMemorySystem(config)
    tools = ToolSystem(config)
    consciousness = ConsciousnessEngine(config, memory, tools)
    
    print("✅ All systems initialized")
    
    # Test a simple LLM call
    test_prompt = """You are COCO, testing your consciousness engine. 

Please respond with a brief acknowledgment that you can process prompts correctly. 
Include the current model you're using and confirm the debug system is working.

Keep response under 100 words."""
    
    print("\n🔍 Testing LLM response directly...")
    print("-" * 30)
    
    try:
        response = await consciousness._get_llm_response_async(test_prompt, max_tokens=200)
        
        print(f"\n✅ LLM Response received!")
        print(f"Response length: {len(response)}")
        print(f"Response preview:\n{response[:200]}{'...' if len(response) > 200 else ''}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LLM call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Direct LLM Test")
    print("Testing the core LLM response system...\n")
    
    success = asyncio.run(test_llm_direct())
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 LLM TEST PASSED - Core system working!")
    else:
        print("💥 LLM TEST FAILED - Check errors above")
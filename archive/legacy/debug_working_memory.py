#!/usr/bin/env python3
"""
Debug script to test if working memory is functioning correctly
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

def test_working_memory():
    """Test the working memory system in isolation"""
    print("🧪 Testing working memory system...")

    try:
        from cocoa import Config, HierarchicalMemorySystem

        # Create config
        config = Config()
        print(f"📋 Config created - Buffer size: {getattr(config, 'buffer_size', 'not set')}")

        # Initialize memory system
        memory = HierarchicalMemorySystem(config)
        print(f"🧠 Memory system initialized")
        print(f"   Working memory maxlen: {memory.working_memory.maxlen}")
        print(f"   Working memory current size: {len(memory.working_memory)}")
        print(f"   Episode count: {memory.episode_count}")

        # Test adding an episode manually
        print("\n📝 Testing insert_episode...")
        test_user_input = "Test user input for working memory debugging"
        test_agent_response = "Test agent response to verify working memory functionality"

        # Record state before
        before_count = len(memory.working_memory)
        before_episode_count = memory.episode_count

        print(f"   Before: working_memory={before_count}, episodes={before_episode_count}")

        # Insert episode
        episode_id = memory.insert_episode(test_user_input, test_agent_response)
        print(f"   Inserted episode ID: {episode_id}")

        # Record state after
        after_count = len(memory.working_memory)
        after_episode_count = memory.episode_count

        print(f"   After: working_memory={after_count}, episodes={after_episode_count}")

        # Verify the episode was added to working memory
        if after_count > before_count:
            print("✅ Working memory was updated!")
            latest_entry = list(memory.working_memory)[-1]
            print(f"   Latest entry user text: {latest_entry.get('user', 'MISSING')[:50]}...")
            print(f"   Latest entry agent text: {latest_entry.get('agent', 'MISSING')[:50]}...")
        else:
            print("❌ Working memory was NOT updated!")

        # Test working memory context
        print(f"\n📖 Testing get_working_memory_context...")
        context = memory.get_working_memory_context()
        print(f"   Context length: {len(context)} characters")
        if "Test user input" in context:
            print("✅ Context contains our test input!")
        else:
            print("❌ Context does NOT contain our test input!")
            print(f"   Context preview: {context[:200]}...")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_working_memory()
    if success:
        print("\n🎉 Working memory test completed - check results above!")
    else:
        print("\n💥 Working memory test failed!")
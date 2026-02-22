#!/usr/bin/env python3
"""
Test script to verify the working memory fix is working correctly
"""

import sys
sys.path.insert(0, '.')

def test_working_memory_fix():
    """Test that the working memory fix properly loads recent episodes"""
    print("🧪 Testing working memory fix...")

    try:
        from cocoa import Config, HierarchicalMemorySystem

        # Initialize memory system (this should trigger loading of recent episodes)
        config = Config()
        memory = HierarchicalMemorySystem(config)

        print(f"📊 Memory Statistics:")
        print(f"   Working memory size: {len(memory.working_memory)}/50")
        print(f"   Total episode count: {memory.episode_count}")

        # Test that working memory has episodes if any exist
        if memory.episode_count > 0:
            working_memory_count = len(memory.working_memory)
            expected_count = min(memory.episode_count, 50)

            print(f"   Expected working memory entries: {expected_count}")

            if working_memory_count > 0:
                print(f"✅ Working memory populated with {working_memory_count} episodes")

                # Test a few entries
                print(f"📋 Sample working memory entries:")
                for i, entry in enumerate(list(memory.working_memory)[-3:]):
                    print(f"   {i+1}. User: {entry.get('user', 'MISSING')[:60]}...")
                    print(f"       Agent: {entry.get('agent', 'MISSING')[:60]}...")

                # Test working memory context
                context = memory.get_working_memory_context()
                print(f"📖 Working memory context: {len(context)} characters")

                if len(context) > 100:
                    print("✅ Working memory context is substantial")
                    return True
                else:
                    print("❌ Working memory context is too short")
                    return False
            else:
                print("❌ Working memory is still empty despite having episodes")
                return False
        else:
            print("ℹ️ No episodes in database yet - working memory correctly empty")
            return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_working_memory_fix()
    if success:
        print("\n🎉 Working memory fix test PASSED!")
        print("COCO should now have perfect recall within the conversation buffer!")
    else:
        print("\n💥 Working memory fix test FAILED!")
        print("Additional debugging may be needed.")
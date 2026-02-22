#!/usr/bin/env python3
"""
Test script to simulate how working memory should work during a current conversation
"""

import sys
sys.path.insert(0, '.')

def test_current_session_memory():
    """Test that working memory works correctly during a conversation"""
    print("🧪 Testing current session memory behavior...")

    try:
        from cocoa import Config, HierarchicalMemorySystem

        # Initialize fresh memory system
        config = Config()
        memory = HierarchicalMemorySystem(config)

        print(f"📊 Initial state:")
        print(f"   Working memory: {len(memory.working_memory)}/50")
        print(f"   Session ID: {memory.session_id}")

        # Simulate a conversation with multiple episodes
        conversation_episodes = [
            ("Hello, I want to test the memory system", "Hi! I'm ready to test memory functionality."),
            ("Can you remember what I just said?", "Yes, you said you want to test the memory system."),
            ("What was the first thing I said to you?", "You said 'Hello, I want to test the memory system'"),
            ("Perfect! Now let's add more episodes", "Great! I'm tracking all our exchanges."),
            ("This is episode 5 of our conversation", "Yes, this is episode 5, and I should remember all previous episodes."),
        ]

        print(f"\n📝 Simulating {len(conversation_episodes)} episodes...")

        for i, (user_text, agent_text) in enumerate(conversation_episodes, 1):
            print(f"   Episode {i}: Adding to memory...")
            episode_id = memory.insert_episode(user_text, agent_text)

            working_memory_size = len(memory.working_memory)
            print(f"     Working memory: {working_memory_size}/50")

            if working_memory_size >= i:
                print(f"     ✅ Episode {i} added successfully")
            else:
                print(f"     ❌ Episode {i} NOT in working memory!")
                return False

        # Test memory access after adding episodes
        print(f"\n📖 Testing memory context after {len(conversation_episodes)} episodes...")
        context = memory.get_working_memory_context()

        if "Hello, I want to test the memory system" in context:
            print("✅ First episode is accessible in working memory context")
        else:
            print("❌ First episode is NOT accessible in working memory context")
            return False

        if "This is episode 5 of our conversation" in context:
            print("✅ Latest episode is accessible in working memory context")
        else:
            print("❌ Latest episode is NOT accessible in working memory context")
            return False

        print(f"📊 Final working memory state: {len(memory.working_memory)}/50")
        print(f"💾 Context size: {len(context)} characters")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_current_session_memory()
    if success:
        print("\n🎉 Current session memory test PASSED!")
        print("Working memory should work correctly during conversations.")
    else:
        print("\n💥 Current session memory test FAILED!")
        print("There's still an issue with working memory during conversations.")
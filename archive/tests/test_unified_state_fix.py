#!/usr/bin/env python3
"""
Test the unified state memory fragmentation fix
Tests the exact failing scenario: "Kerry is my wife" → file operations → context preservation
"""

import sys
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from unified_state import UnifiedConversationState
from cocoa import Config, HierarchicalMemorySystem, ConsciousnessEngine, ToolSystem

def test_unified_state_basic():
    """Test basic unified state functionality"""
    print("🧪 Testing UnifiedConversationState basic functionality...")

    # Test 1: Fact extraction
    state = UnifiedConversationState(window_size=10)
    state.add_exchange("My wife's name is Kerry", "That's wonderful! I'll remember that Kerry is your wife.")

    assert 'wife_name' in state.facts_extracted, "Failed to extract wife fact"
    assert state.facts_extracted['wife_name'] == 'Kerry', f"Expected 'Kerry', got {state.facts_extracted['wife_name']}"
    print("✅ Basic fact extraction working")

    # Test 2: Context generation
    context = state.get_context_for_tool('write_file')
    assert 'facts' in context, "Context missing facts"
    assert context['facts']['wife_name'] == 'Kerry', "Context facts incorrect"
    print("✅ Context generation working")

    # Test 3: Working memory search
    result = state.search_working_memory("wife")
    assert result is not None, "Failed to find wife in working memory"
    assert "Kerry" in result, f"Kerry not found in search result: {result}"
    print("✅ Working memory search working")

    return True

def test_consciousness_engine_integration():
    """Test integration with ConsciousnessEngine"""
    print("\n🧠 Testing ConsciousnessEngine integration...")

    try:
        # Create test configuration
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        # Test unified state initialization
        assert hasattr(engine, 'unified_state'), "ConsciousnessEngine missing unified_state"
        if engine.unified_state is None:
            print("⚠️ Unified state not available - check UNIFIED_STATE_AVAILABLE flag")
            return False

        print("✅ Unified state properly initialized in ConsciousnessEngine")

        # Test memory system back-reference
        assert hasattr(memory, 'consciousness_engine'), "Memory missing consciousness_engine reference"
        assert memory.consciousness_engine is engine, "Memory back-reference incorrect"
        print("✅ Memory system back-reference established")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_memory_fragmentation_scenario():
    """Test the exact failing scenario: 'Kerry is my wife' → file operations"""
    print("\n🔧 Testing memory fragmentation fix scenario...")

    try:
        # Setup
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        if engine.unified_state is None:
            print("⚠️ Skipping scenario test - unified state not available")
            return False

        # Simulate the conversation that establishes context
        user_input = "My wife's name is Kerry and she loves reading books"
        assistant_response = "That's lovely! I'll remember that Kerry is your wife and she enjoys reading."

        # This should trigger unified state update via insert_episode hook
        memory.insert_episode(user_input, assistant_response)

        # Verify context was captured
        context = engine.unified_state.get_context_for_tool('write_file')
        assert 'wife_name' in context['facts'], "Failed to capture wife fact in unified state"
        assert context['facts']['wife_name'] == 'Kerry', "Wrong wife name captured"
        print("✅ Context captured in unified state")

        # Simulate tool execution that should preserve context
        tool_input = {'path': 'test_file.txt', 'content': 'Test content'}

        # This should inject context via _execute_tool
        result = engine._execute_tool('write_file', tool_input)

        # Check that conversation facts were injected
        assert '_conversation_facts' in tool_input, "Conversation facts not injected into tool_input"
        assert 'wife_name' in tool_input['_conversation_facts'], "Wife fact not in injected context"
        assert tool_input['_conversation_facts']['wife_name'] == 'Kerry', "Wrong wife name in injected context"
        print("✅ Context successfully injected into file operations")

        # Test memory recall with working memory priority
        recall_input = {'query': 'wife'}
        recall_result = engine._execute_tool('recall_memory', recall_input)

        # Should find from working memory
        assert "Kerry" in recall_result, f"Kerry not found in recall result: {recall_result}"
        print("✅ Memory recall checks working memory first")

        return True

    except Exception as e:
        print(f"❌ Scenario test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_context_injection():
    """Test that various tools receive conversation context"""
    print("\n🔧 Testing tool context injection...")

    try:
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        if engine.unified_state is None:
            print("⚠️ Skipping context injection test - unified state not available")
            return False

        # Establish context
        engine.unified_state.add_exchange("My wife Kerry loves Python programming", "Great! I'll remember that.")

        # Test file operation context injection
        file_input = {'path': 'test.py', 'content': 'print("hello")'}
        engine._execute_tool('write_file', file_input)

        assert '_conversation_facts' in file_input, "File operation missing conversation facts"
        print("✅ File operations receive conversation context")

        # Test memory operations working memory check
        memory_input = {'query': 'wife'}
        result = engine._execute_tool('recall_memory', memory_input)
        assert "Kerry" in result, "Memory recall not checking working memory first"
        print("✅ Memory operations check working memory first")

        return True

    except Exception as e:
        print(f"❌ Context injection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Unified State Memory Fragmentation Fix Tests\n")

    tests = [
        test_unified_state_basic,
        test_consciousness_engine_integration,
        test_memory_fragmentation_scenario,
        test_tool_context_injection
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Memory fragmentation fix working correctly.")
        print("\nThe fix should resolve:")
        print("✅ 'Kerry is my wife' persisting through file operations")
        print("✅ No mid-task resets during searches")
        print("✅ Tools having awareness of current conversation")
        print("✅ Working memory accessible to recall functions")
    else:
        print("⚠️ Some tests failed. Check the implementation.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
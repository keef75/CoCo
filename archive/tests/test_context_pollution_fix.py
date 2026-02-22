#!/usr/bin/env python3
"""
Test Context Pollution Fix
==========================
Tests that the unified state doesn't inject irrelevant context from previous conversations.
Specifically tests the Pacman vs Kerry scenario where COCO confused contexts.
"""

import sys
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from unified_state import UnifiedConversationState
from cocoa import Config, HierarchicalMemorySystem, ConsciousnessEngine, ToolSystem

def test_context_relevance_filtering():
    """Test that irrelevant facts are filtered out"""
    print("🧪 Testing Context Relevance Filtering...")

    try:
        # Setup unified state
        state = UnifiedConversationState(window_size=50)

        # Step 1: Establish Kerry context (previous conversation)
        print("📝 Step 1: Establishing Kerry context (previous conversation)...")
        state.add_exchange(
            "My wife Kerry loves reading books",
            "That's wonderful! I'll remember that Kerry is your wife and enjoys reading."
        )

        # Verify Kerry facts were extracted
        kerry_facts = state.current_facts
        print(f"   Kerry facts: {kerry_facts}")

        # Step 2: Start NEW conversation about Pacman (current conversation)
        print("🎮 Step 2: Starting NEW conversation about Pacman...")
        state.add_exchange(
            "I'm looking for a Pacman game in this directory",
            "I'll help you find the Pacman game. Let me search the directory."
        )
        state.add_exchange(
            "keep looking, its in there",
            "I'll continue searching for the Pacman game."
        )

        # Step 3: Test context filtering for Pacman conversation
        print("🔍 Step 3: Testing context filtering for Pacman conversation...")

        # Get context for Pacman-related tool execution
        pacman_context = state.get_context_for_tool('search_files', {
            'current_input': 'keep looking for pacman game'
        })

        relevant_facts = pacman_context.get('facts', {})
        print(f"   Relevant facts for Pacman search: {relevant_facts}")

        # Should NOT include Kerry facts in Pacman context
        has_kerry_pollution = any('kerry' in str(v).lower() for v in relevant_facts.values())
        print(f"   ✅ Kerry facts filtered out: {not has_kerry_pollution}")

        # Step 4: Test context filtering for Kerry conversation
        print("👩 Step 4: Testing context filtering for Kerry conversation...")

        # Get context for Kerry-related tool execution
        kerry_context = state.get_context_for_tool('write_file', {
            'current_input': 'update profile with Kerry information'
        })

        kerry_relevant_facts = kerry_context.get('facts', {})
        print(f"   Relevant facts for Kerry context: {kerry_relevant_facts}")

        # SHOULD include Kerry facts when Kerry is mentioned
        has_kerry_when_relevant = any('kerry' in str(v).lower() for v in kerry_relevant_facts.values())
        print(f"   ✅ Kerry facts included when relevant: {has_kerry_when_relevant}")

        # Overall test result
        filtering_works = not has_kerry_pollution and has_kerry_when_relevant

        if filtering_works:
            print("🎉 Context relevance filtering working correctly!")
            print("✅ Irrelevant facts filtered out for unrelated conversations")
            print("✅ Relevant facts included when context matches")
        else:
            print("❌ Context relevance filtering needs adjustment")
            print(f"Debug: Pollution={has_kerry_pollution}, Relevance={has_kerry_when_relevant}")

        return filtering_works

    except Exception as e:
        print(f"❌ Context relevance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_working_memory_scope_limiting():
    """Test that working memory search is limited to recent exchanges"""
    print("\n🔍 Testing Working Memory Scope Limiting...")

    try:
        state = UnifiedConversationState(window_size=50)

        # Add old Kerry conversation
        print("📝 Adding old Kerry conversation...")
        state.add_exchange("My wife Kerry", "I'll remember Kerry is your wife")

        # Add many other exchanges to push Kerry out of recent scope
        print("📚 Adding many exchanges to push Kerry out of scope...")
        for i in range(15):
            state.add_exchange(f"Random conversation {i}", f"Response {i}")

        # Add current Pacman conversation
        print("🎮 Adding current Pacman conversation...")
        state.add_exchange("Looking for Pacman game", "I'll help find the Pacman game")
        state.add_exchange("keep looking", "Continuing search")

        # Test working memory search for Kerry (should NOT find it)
        print("🔍 Testing working memory search for Kerry...")
        kerry_result = state.search_working_memory('kerry')
        kerry_not_found = kerry_result is None

        print(f"   ✅ Kerry not found in recent working memory: {kerry_not_found}")

        # Test working memory search for Pacman (SHOULD find it)
        print("🎮 Testing working memory search for Pacman...")
        pacman_result = state.search_working_memory('pacman')
        pacman_found = pacman_result is not None

        print(f"   ✅ Pacman found in recent working memory: {pacman_found}")
        if pacman_found:
            print(f"   Result: {pacman_result}")

        scope_limiting_works = kerry_not_found and pacman_found

        if scope_limiting_works:
            print("🎉 Working memory scope limiting working correctly!")
            print("✅ Old conversations don't pollute current context")
            print("✅ Recent conversations remain accessible")
        else:
            print("❌ Working memory scope limiting needs adjustment")

        return scope_limiting_works

    except Exception as e:
        print(f"❌ Working memory scope test failed: {e}")
        return False

def test_pacman_kerry_scenario():
    """Test the exact failing scenario: Pacman search vs Kerry context"""
    print("\n🎭 Testing Pacman vs Kerry Scenario...")

    try:
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        if not hasattr(engine, 'unified_state') or engine.unified_state is None:
            print("⚠️ Skipping scenario test - unified state not available")
            return False

        # Step 1: Previous conversation about Kerry
        print("📝 Step 1: Previous conversation about Kerry...")
        engine.unified_state.add_exchange("My wife Kerry", "I'll remember Kerry is your wife")

        # Step 2: Current conversation about Pacman
        print("🎮 Step 2: Current conversation about Pacman...")
        engine.unified_state.add_exchange("Looking for Pacman game", "I'll help find it")

        # Step 3: User says "keep looking" (the critical moment)
        print("🔄 Step 3: User says 'keep looking' for Pacman...")

        # Get context that would be injected (this is what was failing)
        context = {'working_memory': memory.get_working_memory_context()}

        if hasattr(engine, 'unified_state') and engine.unified_state:
            unified_context = engine.unified_state.get_context_for_tool('consciousness_think', {
                'current_input': 'keep looking for the pacman game',
                'conversation_turn': True
            })
            context.update({
                'unified_state_facts': unified_context.get('facts', {}),
                'recent_exchanges': unified_context.get('recent_exchanges', ''),
                'persistent_context': unified_context.get('persistent_context', ''),
                'conversation_length': unified_context.get('conversation_length', 0)
            })

        # Check if Kerry context pollutes Pacman context
        unified_facts = context.get('unified_state_facts', {})
        has_kerry_pollution = any('kerry' in str(v).lower() for v in unified_facts.values())

        print(f"   ✅ No Kerry pollution in Pacman context: {not has_kerry_pollution}")
        print(f"   Facts in context: {unified_facts}")

        # Check recent exchanges for context
        recent_exchanges = context.get('recent_exchanges', '')
        has_pacman_context = 'pacman' in recent_exchanges.lower()

        print(f"   ✅ Pacman context preserved: {has_pacman_context}")

        scenario_fixed = not has_kerry_pollution and has_pacman_context

        if scenario_fixed:
            print("🎉 Pacman vs Kerry scenario fixed!")
            print("✅ COCO should now continue Pacman search instead of searching for Kerry")
        else:
            print("❌ Pacman vs Kerry scenario still has issues")

        return scenario_fixed

    except Exception as e:
        print(f"❌ Pacman vs Kerry scenario test failed: {e}")
        return False

def main():
    """Run all context pollution fix tests"""
    print("🚀 Running Context Pollution Fix Tests\n")

    tests = [
        test_context_relevance_filtering,
        test_working_memory_scope_limiting,
        test_pacman_kerry_scenario
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

    print(f"\n📊 Context Pollution Fix Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Context pollution fix working correctly!")
        print("\nKey improvements:")
        print("✅ Irrelevant facts filtered out from context injection")
        print("✅ Working memory search limited to recent exchanges")
        print("✅ Context relevance filtering prevents confusion")
        print("✅ Pacman vs Kerry scenario should work correctly")
    else:
        print("⚠️ Some context pollution tests failed. Check the implementation.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
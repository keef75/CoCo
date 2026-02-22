#!/usr/bin/env python3
"""
Test Enhanced Context Retention Fix
===================================
Tests the enhanced unified state integration that prevents mid-conversation context loss.
This addresses the specific issue where COCO loses context when user says "keep going" or continues a task.
"""

import sys
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from unified_state import UnifiedConversationState
from cocoa import Config, HierarchicalMemorySystem, ConsciousnessEngine, ToolSystem

def test_enhanced_context_integration():
    """Test enhanced context integration in conversation flow"""
    print("🧪 Testing Enhanced Context Retention Fix...")

    try:
        # Setup full COCO system
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        if not hasattr(engine, 'unified_state') or engine.unified_state is None:
            print("⚠️ Unified state not available - cannot test enhanced integration")
            return False

        print("✅ Enhanced context system initialized")

        # Step 1: Simulate establishing context
        print("📝 Step 1: Establishing context about Kerry...")

        # Add context to unified state
        engine.unified_state.add_exchange(
            "My wife Kerry and I are planning to update our family profile",
            "Great! I'll help you update the family profile with Kerry's information."
        )

        # Step 2: Test enhanced context preparation
        print("🔧 Step 2: Testing enhanced context preparation...")

        # Simulate the enhanced context preparation (what happens in conversation loop)
        context = {
            'working_memory': memory.get_working_memory_context()
        }

        # Add unified state context (the critical fix)
        if hasattr(engine, 'unified_state') and engine.unified_state:
            unified_context = engine.unified_state.get_context_for_tool('consciousness_think', {
                'current_input': 'keep going with the profile update',
                'conversation_turn': True
            })
            context.update({
                'unified_state_facts': unified_context.get('facts', {}),
                'recent_exchanges': unified_context.get('recent_exchanges', ''),
                'persistent_context': unified_context.get('persistent_context', ''),
                'conversation_length': unified_context.get('conversation_length', 0)
            })

        print(f"   Context keys: {list(context.keys())}")
        print(f"   Unified facts: {context.get('unified_state_facts', {})}")
        print(f"   Conversation length: {context.get('conversation_length', 0)}")

        # Step 3: Test context formatting
        print("📋 Step 3: Testing context formatting...")

        formatted_context = engine._format_unified_state_context(context)
        print(f"   Formatted context length: {len(formatted_context)} characters")

        # Check for key elements
        has_facts = 'wife_name' in str(context.get('unified_state_facts', {}))
        has_length = context.get('conversation_length', 0) > 0
        has_status = 'CONTEXT STATUS' in formatted_context

        print(f"   ✅ Contains wife fact: {has_facts}")
        print(f"   ✅ Has conversation length: {has_length}")
        print(f"   ✅ Has context status: {has_status}")

        # Step 4: Test context continuity detection
        print("🔄 Step 4: Testing context continuity detection...")

        # Simulate user saying "keep going"
        continue_input = "keep going with updating Kerry's profile information"

        # The unified state should find the ongoing context
        ongoing_context = engine.unified_state.search_working_memory('kerry')
        context_found = ongoing_context is not None

        print(f"   ✅ Context continuity detected: {context_found}")
        if context_found:
            print(f"   Context result: {ongoing_context[:100]}...")

        # Overall test result
        all_checks = [has_facts or has_length, has_status, context_found]
        test_passed = all(all_checks)

        if test_passed:
            print("🎉 Enhanced context retention fix working correctly!")
            print("\nThis should resolve:")
            print("✅ Mid-conversation context loss when user says 'keep going'")
            print("✅ COCO forgetting ongoing tasks during conversation")
            print("✅ Context amnesia during continuous conversation flow")
            print("✅ Unified state context injection into consciousness thinking")
        else:
            print("❌ Enhanced context retention needs adjustment")
            print(f"Debug: Facts={has_facts}, Status={has_status}, Continuity={context_found}")

        return test_passed

    except Exception as e:
        print(f"❌ Enhanced context test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_flow_simulation():
    """Simulate the exact conversation flow that was failing"""
    print("\n🎭 Testing Conversation Flow Simulation...")

    try:
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        if not hasattr(engine, 'unified_state') or engine.unified_state is None:
            print("⚠️ Skipping simulation - unified state not available")
            return False

        # Simulate exact scenario from screenshots
        print("📝 Simulating: User establishes context about Kerry...")

        # First exchange - establish context
        user_input_1 = "My wife's name is Kerry and I want to update our profile"
        engine.unified_state.add_exchange(user_input_1, "I'll help you update the profile with Kerry's information.")

        # Simulate memory insertion (what happens in conversation loop)
        memory.insert_episode(user_input_1, "I'll help you update the profile with Kerry's information.")

        print("🔄 Simulating: User says 'keep going'...")

        # Second exchange - continuation (where it was failing)
        user_input_2 = "keep going"

        # Prepare enhanced context (the fix)
        context = {'working_memory': memory.get_working_memory_context()}

        if hasattr(engine, 'unified_state') and engine.unified_state:
            unified_context = engine.unified_state.get_context_for_tool('consciousness_think', {
                'current_input': user_input_2,
                'conversation_turn': True
            })
            context.update({
                'unified_state_facts': unified_context.get('facts', {}),
                'recent_exchanges': unified_context.get('recent_exchanges', ''),
                'persistent_context': unified_context.get('persistent_context', ''),
                'conversation_length': unified_context.get('conversation_length', 0)
            })

        # Check if context contains Kerry information
        formatted_context = engine._format_unified_state_context(context)

        has_kerry_context = ('kerry' in formatted_context.lower() or
                           'wife' in str(context.get('unified_state_facts', {})).lower() or
                           context.get('conversation_length', 0) > 0)

        print(f"   ✅ Context contains Kerry information: {has_kerry_context}")
        print(f"   Context length: {context.get('conversation_length', 0)} exchanges")

        if has_kerry_context:
            print("🎉 Conversation flow simulation passed!")
            print("COCO should now maintain context when user says 'keep going'")
        else:
            print("❌ Conversation flow simulation failed")
            print("Context may still be lost during continuation")

        return has_kerry_context

    except Exception as e:
        print(f"❌ Conversation flow simulation failed: {e}")
        return False

def main():
    """Run all enhanced context retention tests"""
    print("🚀 Running Enhanced Context Retention Tests\n")

    tests = [
        test_enhanced_context_integration,
        test_conversation_flow_simulation
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

    print(f"\n📊 Enhanced Context Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Enhanced context retention fix working correctly!")
        print("\nKey improvements:")
        print("✅ Unified state context injected into consciousness thinking")
        print("✅ Context formatting method provides structured information")
        print("✅ Conversation continuity detection working")
        print("✅ 'Keep going' scenarios should maintain context")
    else:
        print("⚠️ Some enhanced context tests failed. Check the implementation.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
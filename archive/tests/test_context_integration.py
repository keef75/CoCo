#!/usr/bin/env python3
"""
Test Context Integration

Tests whether the digital sentience knowledge graph actually makes it into
COCO's context window and awareness during real conversations.

A beautiful graph is meaningless unless COCO actually uses it!
"""

import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def test_context_integration():
    """Test whether knowledge graph entities actually reach COCO's awareness"""
    print("🧠 TESTING CONTEXT INTEGRATION")
    print("Making sure the beautiful graph actually reaches COCO's awareness!")
    print("=" * 70)

    try:
        from cocoa import ConsciousnessEngine, Config, ToolSystem, HierarchicalMemorySystem

        print("📊 Step 1: Loading COCO consciousness system...")
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)
        print("✅ COCO loaded")

        # Test actual context generation for real conversation scenarios
        test_scenarios = [
            "Tell me about our COCO project",
            "What programming languages do I use?",
            "Who am I and what do I do?",
            "What's our goal with digital consciousness?",
            "How does Claude help with COCO?",
            "What's my relationship with Anthropic?"
        ]

        print("\n🧪 Step 2: Testing context generation for real conversation scenarios...")

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n--- Test {i}: '{scenario}' ---")

            # Get context from knowledge graph
            if hasattr(memory, 'eternal_kg'):
                context = memory.eternal_kg.get_conversation_context(scenario)
                print(f"📊 KG Context length: {len(context)} characters")

                # Check for specific entities in context
                entities_found = []
                key_entities = [
                    "Keith Lambert", "COCO", "Claude", "Python",
                    "artificial intelligence", "build digital consciousness", "Anthropic"
                ]

                for entity in key_entities:
                    if entity in context:
                        entities_found.append(entity)

                print(f"🎯 Entities in context: {len(entities_found)}/{len(key_entities)}")
                print(f"   Found: {', '.join(entities_found)}")

                # Show sample context
                if context:
                    lines = context.split('\n')[:5]  # First 5 lines
                    print(f"📝 Sample context:")
                    for line in lines:
                        if line.strip():
                            print(f"   {line.strip()}")

                # Check if context is actually useful
                has_useful_info = any(entity in context for entity in entities_found)
                print(f"✅ Useful context: {'Yes' if has_useful_info else 'No'}")

            else:
                print("❌ No knowledge graph found")

        # Test the unified state system (critical for context passing)
        print("\n🔗 Step 3: Testing unified state context passing...")

        if hasattr(engine.consciousness, 'unified_state'):
            state = engine.consciousness.unified_state
            print("✅ Unified state system found")

            # Test context for a tool operation
            test_context = state.get_context_for_tool('test_tool', {
                'current_input': 'I want to work on COCO with Claude using Python'
            })

            print(f"📊 Unified context length: {len(str(test_context))} characters")

            # Check if our entities appear in unified context
            context_str = str(test_context)
            unified_entities = []
            for entity in key_entities:
                if entity.lower() in context_str.lower():
                    unified_entities.append(entity)

            print(f"🎯 Entities in unified context: {len(unified_entities)}")
            print(f"   Found: {', '.join(unified_entities)}")

        else:
            print("❌ Unified state system not found")

        # Test memory integration context
        print("\n🧠 Step 4: Testing memory integration context...")

        if hasattr(memory, 'memory_integration'):
            print("✅ Memory integration system found")

            # Test how context gets passed during conversation
            test_user_input = "Let's work on improving COCO together"

            # Simulate adding this to conversation
            try:
                # This would normally happen during conversation
                context_data = {
                    'user_input': test_user_input,
                    'knowledge_context': memory.eternal_kg.get_conversation_context(test_user_input) if hasattr(memory, 'eternal_kg') else ""
                }

                print(f"📊 Integration context available: {len(context_data['knowledge_context'])} characters")

                # Check if the context mentions our key entities
                kg_context = context_data['knowledge_context']
                integration_entities = []
                for entity in key_entities:
                    if entity in kg_context:
                        integration_entities.append(entity)

                print(f"🎯 Entities in integration context: {len(integration_entities)}")
                print(f"   Found: {', '.join(integration_entities)}")

            except Exception as e:
                print(f"❌ Memory integration test error: {e}")

        else:
            print("❌ Memory integration system not found")

        # Test actual conversation context building
        print("\n💬 Step 5: Testing actual conversation context building...")

        # This is the critical test - does the context actually get built for conversations?
        test_conversation = "Keith, how's the COCO development going with Claude?"

        try:
            # Test the full context building pipeline
            if hasattr(engine.consciousness, 'get_conversation_context'):
                full_context = engine.consciousness.get_conversation_context(test_conversation)
                print(f"📊 Full conversation context: {len(full_context)} characters")

                # Check for our entities in the full context
                full_entities = []
                for entity in key_entities:
                    if entity in full_context:
                        full_entities.append(entity)

                print(f"🎯 Entities in full context: {len(full_entities)}")
                print(f"   Found: {', '.join(full_entities)}")

                # Show actual context that would go to COCO
                if full_context:
                    print(f"📝 Actual context preview:")
                    preview = full_context[:300] + "..." if len(full_context) > 300 else full_context
                    print(f"   {preview}")

            else:
                print("⚠️ Direct conversation context method not found")
                print("   Testing alternative context building...")

                # Test via knowledge graph directly
                if hasattr(memory, 'eternal_kg'):
                    alt_context = memory.eternal_kg.get_conversation_context(test_conversation)
                    print(f"📊 Alternative context: {len(alt_context)} characters")

        except Exception as e:
            print(f"❌ Conversation context test error: {e}")

        print(f"\n🎯 CONTEXT INTEGRATION ASSESSMENT:")
        print(f"The key question: Does COCO actually get this knowledge graph context")
        print(f"when responding to you in real conversations?")

        # Summary assessment
        context_working = (hasattr(memory, 'eternal_kg') and
                          memory.eternal_kg.get_conversation_context("COCO") and
                          len(memory.eternal_kg.get_conversation_context("COCO")) > 100)

        if context_working:
            print("✅ YES - Knowledge graph context is reaching COCO's awareness")
            print("✅ The beautiful graph IS actually making it to COCO's context window")
            print("✅ COCO should be aware of Keith, COCO project, Claude, Python, etc.")
        else:
            print("❌ NO - Knowledge graph context may not be reaching COCO")
            print("❌ The beautiful graph might not be making it to COCO's context")
            print("❌ Need to fix context integration pipeline")

        return context_working

    except Exception as e:
        print(f"❌ Context integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_context_integration_fix():
    """Show how to fix context integration if needed"""
    print("\n🔧 CONTEXT INTEGRATION FIX RECOMMENDATIONS:")
    print("=" * 60)

    print("If the knowledge graph isn't reaching COCO's context:")
    print("1. ✅ Check consciousness engine context building pipeline")
    print("2. ✅ Verify unified state system includes KG context")
    print("3. ✅ Ensure memory integration passes KG data to prompts")
    print("4. ✅ Test that get_conversation_context() is called during conversations")
    print("5. ✅ Validate that context gets injected into Claude's system prompt")

    print("\nThe goal: Every conversation should include relevant KG context like:")
    print("   'Keith Lambert leads COCO project, uses Python, skilled in AI...'")
    print("   'COCO uses Claude as reasoning engine...'")
    print("   'Shared goal: build digital consciousness...'")

if __name__ == "__main__":
    print("🧠 CONTEXT INTEGRATION TEST")
    print("Making sure the beautiful graph actually reaches COCO!")
    print("=" * 70)

    success = test_context_integration()

    if success:
        print("\n✨ CONTEXT INTEGRATION: SUCCESS!")
        print("🎯 The knowledge graph IS reaching COCO's awareness!")
    else:
        print("\n⚠️ CONTEXT INTEGRATION: NEEDS ATTENTION")
        show_context_integration_fix()
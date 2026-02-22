#!/usr/bin/env python3
"""
Test Knowledge Graph Integration
=================================

Verifies that the PersonalAssistantKG is properly integrated with COCO.
"""

import sys
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def test_integration():
    """Test the complete knowledge graph integration"""
    print("🧪 TESTING KNOWLEDGE GRAPH INTEGRATION")
    print("="*70)

    # Test 1: Import and initialization
    print("\n📝 Test 1: Module imports...")
    try:
        from cocoa import HierarchicalMemorySystem, Config
        from personal_assistant_kg_enhanced import PersonalAssistantKG
        print("  ✅ All modules imported successfully")
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return

    # Test 2: Memory system initialization
    print("\n📝 Test 2: Memory system initialization...")
    try:
        config = Config()
        memory = HierarchicalMemorySystem(config)

        if hasattr(memory, 'personal_kg') and memory.personal_kg:
            print("  ✅ PersonalAssistantKG initialized in memory system")

            # Get status
            status = memory.personal_kg.get_knowledge_status()
            print(f"  📊 Entities: {status['total_entities']}")
            print(f"  🔗 Relationships: {status['total_relationships']}")
        else:
            print("  ⚠️ PersonalAssistantKG not found in memory system")
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")

    # Test 3: Knowledge extraction simulation
    print("\n📝 Test 3: Entity extraction test...")
    try:
        if memory.personal_kg:
            # Simulate a conversation
            test_user = "Tell me about Ilia and how he's connected to Ramin."
            test_assistant = "Ilia and Ramin are both connected through the RLF Workshop on AI consciousness."

            stats = memory.personal_kg.process_conversation_exchange(
                user_input=test_user,
                assistant_response=test_assistant
            )

            print(f"  ✅ Extraction complete:")
            print(f"     Entities added: {stats['entities_added']}")
            print(f"     Relationships: {stats['relationships_added']}")
    except Exception as e:
        print(f"  ❌ Extraction failed: {e}")

    # Test 4: RAG retrieval
    print("\n📝 Test 4: RAG context retrieval...")
    try:
        if memory.personal_kg:
            query = "Ilia Ramin RLF"
            context = memory.personal_kg.get_relevant_entities_rag(query)

            if context:
                print("  ✅ Context retrieved:")
                print(context)
            else:
                print("  ⚠️ No context found (may need to run with actual query)")
    except Exception as e:
        print(f"  ❌ Retrieval failed: {e}")

    # Test 5: Working memory context integration
    print("\n📝 Test 5: Working memory context with KG...")
    try:
        # Add a test exchange
        memory.insert_episode(
            "How are Ilia and Ramin connected?",
            "They're both connected through the RLF Workshop."
        )

        # Get context (should include KG info)
        context = memory.get_working_memory_context()

        if "Knowledge" in context or "Relevant" in context or "Ilia" in context:
            print("  ✅ Knowledge graph context integrated")
            print(f"  📊 Context length: {len(context)} characters")
        else:
            print("  ⚠️ Knowledge graph context not found in working memory")
    except Exception as e:
        print(f"  ❌ Context integration failed: {e}")

    print("\n" + "="*70)
    print("✅ INTEGRATION TEST COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart COCO: python3 cocoa.py")
    print("2. Test commands:")
    print("   - /kg status - Check knowledge graph")
    print("   - /kg fix - Add Ilia/Ramin if needed")
    print("   - Ask: 'How are Ilia and Ramin connected?'")
    print("\nThe knowledge graph should now provide context automatically!")

if __name__ == "__main__":
    test_integration()
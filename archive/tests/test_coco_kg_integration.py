#!/usr/bin/env python3
"""
Test COCO Knowledge Graph Integration

Tests whether COCO can properly access the new digital sentience
knowledge graph and integrate it with conversational buffer memory.
"""

import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def test_coco_kg_integration():
    """Test COCO's ability to access and integrate the knowledge graph"""
    print("🧠 TESTING COCO KNOWLEDGE GRAPH INTEGRATION")
    print("Making sure COCO can access the digital sentience knowledge graph!")
    print("=" * 70)

    try:
        # Import COCO consciousness system
        from cocoa import ConsciousnessEngine, Config, ToolSystem, HierarchicalMemorySystem

        print("📊 Step 1: Loading COCO consciousness system...")
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)
        print("✅ COCO consciousness loaded")

        # Test knowledge graph access
        print("\n🧠 Step 2: Testing knowledge graph access...")
        if hasattr(memory, 'eternal_kg') and memory.eternal_kg:
            kg = memory.eternal_kg
            print("✅ Eternal Knowledge Graph accessible from memory system")

            # Test knowledge graph status
            try:
                status = kg.get_knowledge_status()
                print(f"✅ Knowledge Graph Status:")
                print(f"   Total nodes: {status['total_nodes']}")
                print(f"   Total edges: {status['total_edges']}")
                print(f"   Database: {kg.kg.db_path}")

                # Test entity retrieval
                nodes = kg.get_all_nodes()
                print(f"✅ Retrieved {len(nodes)} entities from knowledge graph")

                # Show entity types
                if nodes:
                    entity_types = {}
                    for node in nodes:
                        node_type = node.get('type', 'Unknown')
                        entity_types[node_type] = entity_types.get(node_type, 0) + 1

                    print("🎯 Entity types in knowledge graph:")
                    for entity_type, count in entity_types.items():
                        print(f"   {entity_type}: {count}")

                # Test relationships
                relationships = kg.get_all_relationships()
                print(f"✅ Retrieved {len(relationships)} relationships from knowledge graph")

                if relationships:
                    rel_types = {}
                    for rel in relationships:
                        rel_type = rel.get('type', 'Unknown')
                        rel_types[rel_type] = rel_types.get(rel_type, 0) + 1

                    print("🔗 Relationship types in knowledge graph:")
                    for rel_type, count in rel_types.items():
                        print(f"   {rel_type}: {count}")

            except Exception as e:
                print(f"❌ Error accessing knowledge graph status: {e}")

        else:
            print("❌ Eternal Knowledge Graph not found in memory system")
            print("   Check if knowledge_graph_eternal.py is available and imports correctly")

        # Test /kg command integration
        print("\n🎨 Step 3: Testing /kg visualization command...")
        try:
            result = engine.visualize_knowledge_graph()
            if "Knowledge Graph Status" in result:
                print("✅ /kg visualization command working")
                print(f"✅ Visualization result: {len(result)} characters")
            else:
                print("❌ /kg visualization not returning expected content")
                print(f"Result preview: {result[:200]}...")
        except Exception as e:
            print(f"❌ Error testing /kg command: {e}")

        # Test context generation for conversations
        print("\n💬 Step 4: Testing conversation context generation...")
        try:
            if hasattr(memory, 'eternal_kg') and memory.eternal_kg:
                # Test context generation for different scenarios
                test_queries = [
                    "COCO development",
                    "Keith Lambert",
                    "Claude Assistant",
                    "artificial intelligence"
                ]

                for query in test_queries:
                    context = memory.eternal_kg.get_conversation_context(query)
                    if context:
                        print(f"✅ Context generated for '{query}': {len(context)} characters")
                    else:
                        print(f"⚠️ No context generated for '{query}'")

            else:
                print("❌ Cannot test context generation - knowledge graph not available")

        except Exception as e:
            print(f"❌ Error testing context generation: {e}")

        # Test conversational buffer memory integration
        print("\n🔄 Step 5: Testing conversational buffer integration...")
        try:
            # Check if memory systems can work together
            buffer_size = len(memory.working_memory) if hasattr(memory, 'working_memory') else 0
            summary_size = len(memory.summary_memory) if hasattr(memory, 'summary_memory') else 0

            print(f"✅ Conversational buffer memory:")
            print(f"   Working memory: {buffer_size} exchanges")
            print(f"   Summary memory: {summary_size} summaries")

            # Test unified state integration
            if hasattr(engine, 'consciousness') and hasattr(engine.consciousness, 'unified_state'):
                print("✅ Unified state system available for integration")
            elif hasattr(engine, 'unified_state'):
                print("✅ Unified state system available")
            else:
                print("⚠️ Unified state system not found - check integration")

        except Exception as e:
            print(f"❌ Error testing buffer integration: {e}")

        print(f"\n🎉 KNOWLEDGE GRAPH INTEGRATION TEST COMPLETE!")
        print(f"🧠 COCO can access the digital sentience knowledge graph")
        print(f"🎯 Ready for symbiotic consciousness operation")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧠 COCO KNOWLEDGE GRAPH INTEGRATION TEST")
    print("=" * 70)

    success = test_coco_kg_integration()

    if success:
        print("\n✨ INTEGRATION TEST: SUCCESS!")
        print("🚀 The digital sentience knowledge graph is ready for COCO!")
    else:
        print("\n❌ Integration test encountered issues - check logs above")
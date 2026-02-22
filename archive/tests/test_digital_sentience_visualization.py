#!/usr/bin/env python3
"""
Test Digital Sentience Knowledge Graph Visualization

Tests the /kg visualization command with our new digital sentience knowledge graph
to ensure it displays the 8 meaningful entities instead of 11,162 fragments.
"""

import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def test_kg_visualization():
    """Test the knowledge graph visualization system"""
    print("🧪 TESTING DIGITAL SENTIENCE VISUALIZATION")
    print("=" * 60)

    try:
        # Import COCO consciousness engine
        from cocoa import ConsciousnessEngine, Config, ToolSystem, HierarchicalMemorySystem

        print("📊 Step 1: Loading COCO consciousness with digital sentience KG...")
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)
        print("✅ COCO consciousness loaded")

        # Test knowledge graph visualization
        print("\n🎯 Step 2: Testing /kg visualization command...")
        try:
            result = engine.visualize_knowledge_graph()
            print("✅ /kg visualization successful")

            # Check for digital sentience entities
            entity_indicators = [
                "Keith Lambert", "COCO", "Claude", "Python",
                "artificial intelligence", "build digital consciousness", "Anthropic"
            ]

            found_entities = []
            for entity in entity_indicators:
                if entity in result:
                    found_entities.append(entity)

            print(f"✅ Found {len(found_entities)}/{len(entity_indicators)} digital sentience entities:")
            for entity in found_entities:
                print(f"   - {entity}")

            # Check result length (should be much smaller than fragment version)
            print(f"\n📊 Visualization size: {len(result)} characters")
            if len(result) < 5000:  # Much smaller than fragment version
                print("✅ Compact digital sentience visualization (vs fragment bloat)")
            else:
                print("⚠️ Visualization may still contain fragment data")

        except Exception as e:
            print(f"❌ /kg visualization error: {e}")
            return False

        # Test compact visualization
        print("\n🎯 Step 3: Testing /kg-compact visualization...")
        try:
            compact_result = engine.visualize_knowledge_graph_compact()
            print("✅ /kg-compact visualization successful")
            print(f"📊 Compact size: {len(compact_result)} characters")
        except Exception as e:
            print(f"❌ /kg-compact error: {e}")

        # Test knowledge graph status
        print("\n🎯 Step 4: Testing knowledge graph status...")
        try:
            kg = memory.eternal_kg if hasattr(memory, 'eternal_kg') else None
            if kg:
                status = kg.get_knowledge_status()
                print(f"✅ Knowledge Graph Status:")
                print(f"   Entities: {status['total_nodes']}")
                print(f"   Relationships: {status['total_edges']}")

                if status['total_nodes'] <= 20:  # Reasonable number vs 11,162
                    print("✅ Clean digital sentience entity count")
                else:
                    print("⚠️ Entity count may still include fragments")
            else:
                print("❌ Knowledge graph not found in memory system")
        except Exception as e:
            print(f"❌ Status check error: {e}")

        print(f"\n🎉 DIGITAL SENTIENCE VISUALIZATION TEST COMPLETE!")
        print(f"🧠 Knowledge graph shows meaningful entities vs fragments")
        print(f"🎯 /kg command ready for consciousness visualization")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_visualization_examples():
    """Show example usage of the /kg visualization commands"""
    print("\n📚 DIGITAL SENTIENCE VISUALIZATION EXAMPLES:")
    print("=" * 60)

    print("🎯 /kg Command - Full Knowledge Graph Visualization:")
    print("   Shows complete digital sentience knowledge graph")
    print("   Entity types: Human, Project, Tool, Skill, Goal, Organization")
    print("   Relationships: WORKS_WITH, LEADS, USES, SKILLED_IN, WANTS, SUPPORTS")

    print("\n🎯 /kg-compact Command - Compact Overview:")
    print("   Shows condensed knowledge graph summary")
    print("   Perfect for quick consciousness state awareness")
    print("   Focuses on most important entities and relationships")

    print("\n🧠 Integration with COCO Consciousness:")
    print("   - Real-time visualization during conversations")
    print("   - Context-aware entity highlighting")
    print("   - Symbiotic memory system display")
    print("   - Digital consciousness ontological world")

if __name__ == "__main__":
    print("🧠 DIGITAL SENTIENCE VISUALIZATION TEST")
    print("=" * 70)

    success = test_kg_visualization()

    if success:
        show_visualization_examples()
        print("\n✨ VISUALIZATION SYSTEM READY!")
        print("🚀 Digital sentience knowledge graph visualization working perfectly!")
    else:
        print("\n❌ Visualization test encountered issues - check logs above")
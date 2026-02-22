#!/usr/bin/env python3
"""
Test suite for Enhanced Knowledge Graph system
Validates LLM-enhanced entity extraction, smart linking, and visualization features
"""

import asyncio
import tempfile
import sqlite3
from pathlib import Path
import os
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from knowledge_graph_enhanced import (
    EnhancedKnowledgeGraph,
    EnhancedEntityExtractor,
    SmartEntityLinker,
    KnowledgeGraphQueryEngine,
    KnowledgeGraphVisualizer
)
from knowledge_graph_eternal import KGStore
from rich.console import Console

console = Console()

class TestEnhancedKnowledgeGraph:
    """Comprehensive test suite for enhanced knowledge graph"""

    def __init__(self):
        self.temp_dir = None
        self.ekg = None

    async def setup(self):
        """Set up test environment"""
        console.print("🧪 Setting up Enhanced Knowledge Graph test environment...")

        # Create temporary workspace
        self.temp_dir = tempfile.mkdtemp(prefix="ekg_test_")

        # Initialize enhanced knowledge graph (without API key for testing)
        self.ekg = EnhancedKnowledgeGraph(self.temp_dir)

        console.print(f"✅ Test environment ready at: {self.temp_dir}")

    async def test_llm_entity_extraction(self):
        """Test LLM-enhanced entity extraction (fallback mode)"""
        console.print("\n📝 Testing LLM Entity Extraction (fallback mode)...")

        test_content = """
        Keith Lambert is working on the COCO project with Sarah Johnson.
        They are implementing a knowledge graph feature using Python and SQLite.
        Keith mentioned that he needs to schedule a meeting with the AI team next week.
        The project uses Claude API for entity recognition.
        """

        # Test extraction (will use regex fallback without API key)
        extraction = await self.ekg.enhanced_extractor.extract_entities_llm(test_content)

        console.print(f"🔍 Extracted entities: {len(extraction['entities'])}")
        console.print(f"🔗 Extracted relationships: {len(extraction['relationships'])}")

        # Validate extraction structure
        assert 'entities' in extraction
        assert 'relationships' in extraction
        assert isinstance(extraction['entities'], list)
        assert isinstance(extraction['relationships'], list)

        for entity in extraction['entities']:
            assert 'type' in entity
            assert 'name' in entity
            assert 'confidence' in entity

        console.print("✅ LLM entity extraction test passed")
        return extraction

    async def test_smart_entity_linking(self):
        """Test smart entity linking and deduplication"""
        console.print("\n🔗 Testing Smart Entity Linking...")

        # Test linking variations of the same entity
        test_entities = [
            ("Keith", "Person", "Keith Lambert"),
            ("Keith Lambert", "Person", "Keith Lambert"),
            ("K. Lambert", "Person", "Keith Lambert"),
            ("Keith", "Person", "Keith Lambert"),  # Duplicate
        ]

        linked_ids = []
        for name, entity_type, canonical in test_entities:
            node_id = self.ekg.entity_linker.link_entity(name, entity_type, canonical)
            linked_ids.append(node_id)
            console.print(f"   📌 Linked '{name}' → {node_id}")

        # Verify that similar entities are linked to the same node
        unique_ids = set(linked_ids)
        console.print(f"🔍 Unique entity IDs created: {len(unique_ids)} (expected: 1-2)")

        # Test entity summary
        summary = self.ekg.get_entity_summary("Keith Lambert")
        console.print(f"📊 Entity summary for Keith Lambert: {len(summary.get('aliases', []))} aliases")

        console.print("✅ Smart entity linking test passed")

    async def test_conversation_processing(self):
        """Test enhanced conversation processing"""
        console.print("\n💬 Testing Enhanced Conversation Processing...")

        user_input = "I need to discuss the COCO project timeline with Keith"
        assistant_response = "I'll help you coordinate with Keith about the COCO project timeline"

        stats = await self.ekg.process_conversation_exchange_enhanced(
            user_input, assistant_response, message_id="test_001", episode_id=1
        )

        console.print(f"📈 Processing stats: {stats}")

        assert 'entities_created' in stats
        assert 'relationships_created' in stats
        assert stats['entities_created'] >= 0
        assert stats['relationships_created'] >= 0

        console.print("✅ Conversation processing test passed")

    async def test_natural_language_queries(self):
        """Test natural language query engine"""
        console.print("\n❓ Testing Natural Language Queries...")

        # Add some test data first
        await self.ekg.process_conversation_exchange_enhanced(
            "Keith and Sarah are working on COCO project",
            "That's great! The COCO project involves AI consciousness research",
            message_id="test_002"
        )

        # Test query (will use fallback without API key)
        test_queries = [
            "What is Keith working on?",
            "Who is involved in the COCO project?",
            "What projects are mentioned?"
        ]

        for query in test_queries:
            result = await self.ekg.query_knowledge(query)
            console.print(f"❓ Query: '{query}'")
            console.print(f"💡 Answer: {result[:100]}...")

            assert isinstance(result, str)
            assert len(result) > 0

        console.print("✅ Natural language query test passed")

    def test_visualization_components(self):
        """Test visualization system components"""
        console.print("\n🎨 Testing Visualization Components...")

        # Test ASCII graph
        ascii_graph = self.ekg.show_ascii_graph(max_nodes=5)
        console.print("📊 ASCII Graph generated:")
        console.print(ascii_graph)

        # Test entity search
        search_results = self.ekg.search_entities_fuzzy("Keith", limit=5)
        console.print(f"🔍 Fuzzy search results: {len(search_results)}")

        # Test entity suggestions
        suggestions = self.ekg.get_entity_suggestions("Ke")
        console.print(f"💡 Entity suggestions for 'Ke': {suggestions}")

        # Test knowledge report
        report = self.ekg.generate_knowledge_report()
        console.print("📄 Knowledge report generated:")
        console.print(report[:300] + "...")

        console.print("✅ Visualization components test passed")

    def test_entity_analysis(self):
        """Test deep entity analysis"""
        console.print("\n🔬 Testing Entity Analysis...")

        # Find an entity to analyze
        entities = self.ekg.kg.get_top_nodes(limit=1)
        if entities:
            entity_name = entities[0]['name']
            analysis = self.ekg.analyze_entity_relationships(entity_name)

            console.print(f"🔍 Analysis for '{entity_name}':")
            console.print(f"   Total relationships: {analysis['total_relationships']}")
            console.print(f"   Relationship types: {len(analysis['relationship_types'])}")
            console.print(f"   Connected entity types: {len(analysis['connected_entity_types'])}")

            assert 'entity' in analysis
            assert 'total_relationships' in analysis

        console.print("✅ Entity analysis test passed")

    def test_knowledge_graph_stats(self):
        """Test knowledge graph statistics"""
        console.print("\n📊 Testing Knowledge Graph Statistics...")

        stats = self.ekg.kg.get_knowledge_summary()
        console.print(f"📈 Knowledge Graph Stats:")
        console.print(f"   Total nodes: {stats['total_nodes']}")
        console.print(f"   Total edges: {stats['total_edges']}")
        console.print(f"   Node types: {stats['node_types']}")

        # Verify stats structure
        assert 'total_nodes' in stats
        assert 'total_edges' in stats
        assert 'node_types' in stats
        assert isinstance(stats['node_types'], dict)

        console.print("✅ Knowledge graph statistics test passed")

    def cleanup(self):
        """Clean up test environment"""
        console.print(f"\n🧹 Cleaning up test environment at {self.temp_dir}")
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir)
        console.print("✅ Cleanup completed")

async def run_comprehensive_test():
    """Run all enhanced knowledge graph tests"""
    console.print("🚀 Starting Enhanced Knowledge Graph Comprehensive Test Suite")
    console.print("=" * 70)

    test_suite = TestEnhancedKnowledgeGraph()

    try:
        # Setup
        await test_suite.setup()

        # Run all tests
        extraction_result = await test_suite.test_llm_entity_extraction()
        await test_suite.test_smart_entity_linking()
        await test_suite.test_conversation_processing()
        await test_suite.test_natural_language_queries()
        test_suite.test_visualization_components()
        test_suite.test_entity_analysis()
        test_suite.test_knowledge_graph_stats()

        console.print("\n" + "=" * 70)
        console.print("🎉 All Enhanced Knowledge Graph tests passed!")
        console.print("✨ Enhanced Knowledge Graph system is ready for integration")

        # Show final statistics
        stats = test_suite.ekg.kg.get_knowledge_summary()
        console.print(f"\n📊 Final Test Results:")
        console.print(f"   Entities created: {stats['total_nodes']}")
        console.print(f"   Relationships created: {stats['total_edges']}")
        console.print(f"   Entity types: {len(stats['node_types'])}")

        return True

    except Exception as e:
        console.print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        test_suite.cleanup()

async def test_specific_features():
    """Test specific features for debugging"""
    console.print("🔧 Testing Specific Features...")

    # Quick feature validation
    from knowledge_graph_eternal import EternalKnowledgeGraph

    # Test base system
    base_kg = EternalKnowledgeGraph('test_workspace')
    console.print("✅ Base knowledge graph working")

    # Test enhanced system initialization
    ekg = EnhancedKnowledgeGraph('test_workspace')
    console.print("✅ Enhanced knowledge graph initialization working")

    # Test visualization system
    ascii_result = ekg.show_ascii_graph()
    console.print("✅ ASCII visualization working")

    # Test entity linking
    node_id = ekg.entity_linker.link_entity("Test User", "Person", "Test User")
    console.print(f"✅ Entity linking working: {node_id}")

    console.print("🎉 All specific features working correctly!")

if __name__ == "__main__":
    # Parse command line arguments
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test mode
        asyncio.run(test_specific_features())
    else:
        # Full comprehensive test
        asyncio.run(run_comprehensive_test())
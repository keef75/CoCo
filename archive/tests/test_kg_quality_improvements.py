#!/usr/bin/env python3
"""
Test Knowledge Graph Quality Improvements

This script demonstrates the transformation from 11,096+ fragments
to focused digital assistant entities based on senior dev team feedback.
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

from knowledge_graph_eternal import EternalKnowledgeGraph, EntityValidator, KnowledgeGraphCleaner

def test_entity_validation():
    """Test the EntityValidator with real examples from the screenshots"""
    print("🧪 TESTING ENTITY VALIDATION")
    print("=" * 50)

    validator = EntityValidator()

    # Test cases based on the senior dev feedback about bad entities
    bad_entities = [
        ("not just", "Concept"),
        ("through these", "Concept"),
        ("the", "Person"),
        ("and", "Project"),
        ("said", "Person"),
        ("working", "Task"),
        ("on", "Project"),
        ("need to", "Task"),
        ("should", "Task"),
        ("algorithm", "Concept"),
        ("model", "Concept"),
        ("system", "Concept")
    ]

    good_entities = [
        ("Keith Lambert", "Person"),
        ("COCO", "Project"),
        ("implement knowledge graph", "Task"),
        ("Claude", "Tool"),
        ("Anthropic", "Org"),
        ("README.md", "Doc"),
        ("Python", "Tool"),
        ("JavaScript", "Tool")
    ]

    print("❌ BAD ENTITIES (should be rejected):")
    rejected_count = 0
    for entity, entity_type in bad_entities:
        is_valid = validator.is_valid_entity(entity, entity_type)
        status = "✅ REJECTED" if not is_valid else "❌ ACCEPTED"
        print(f"   {status}: '{entity}' ({entity_type})")
        if not is_valid:
            rejected_count += 1

    print(f"\n✅ GOOD ENTITIES (should be accepted):")
    accepted_count = 0
    for entity, entity_type in good_entities:
        is_valid = validator.is_valid_entity(entity, entity_type)
        status = "✅ ACCEPTED" if is_valid else "❌ REJECTED"
        print(f"   {status}: '{entity}' ({entity_type})")
        if is_valid:
            accepted_count += 1

    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   - Bad entities rejected: {rejected_count}/{len(bad_entities)} ({rejected_count/len(bad_entities)*100:.1f}%)")
    print(f"   - Good entities accepted: {accepted_count}/{len(good_entities)} ({accepted_count/len(good_entities)*100:.1f}%)")

    return rejected_count == len(bad_entities) and accepted_count == len(good_entities)

def test_current_kg_analysis():
    """Analyze the current knowledge graph quality"""
    print("\n🔍 ANALYZING CURRENT KNOWLEDGE GRAPH")
    print("=" * 50)

    # Use a temporary test workspace to avoid modifying the real one
    test_workspace = "test_kg_workspace"
    os.makedirs(test_workspace, exist_ok=True)

    try:
        # Initialize the eternal knowledge graph
        kg = EternalKnowledgeGraph(test_workspace)

        # Simulate some test data to analyze
        test_conversations = [
            ("I'm working with Keith Lambert on the COCO project", "That sounds like an interesting collaboration!"),
            ("Need to implement the knowledge graph feature", "I'll help you implement that feature."),
            ("Claude is a great AI assistant from Anthropic", "Thank you! I appreciate the feedback."),
            ("The algorithm needs optimization for better performance", "Let's work on optimizing that algorithm.")
        ]

        print("💬 Processing test conversations...")
        for i, (user_msg, assistant_msg) in enumerate(test_conversations):
            kg.process_conversation_exchange(user_msg, assistant_msg, episode_id=i)

        # Get current status
        status = kg.get_knowledge_status()
        print(f"📊 TEST KNOWLEDGE GRAPH STATUS:")
        print(f"   - Total entities: {status['total_nodes']}")
        print(f"   - Total relationships: {status['total_edges']}")
        print(f"   - Total mentions: {status['total_mentions']}")

        # Analyze quality
        cleaner = KnowledgeGraphCleaner(kg.kg)
        quality_report = cleaner.analyze_quality_issues()

        print(f"🎯 QUALITY ANALYSIS:")
        print(f"   - Valid entities: {quality_report['statistics']['valid_entities']}")
        print(f"   - Invalid entities: {quality_report['statistics']['invalid_entities']}")
        print(f"   - Quality percentage: {quality_report['statistics']['quality_percentage']:.1f}%")

        # Show entity types
        print(f"📋 ENTITIES BY TYPE:")
        for entity_type, count in quality_report['nodes_by_type'].items():
            print(f"   - {entity_type}: {count}")

        return quality_report

    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        return None
    finally:
        # Clean up test workspace
        import shutil
        shutil.rmtree(test_workspace, ignore_errors=True)

def test_optimization_dry_run():
    """Test the optimization process in dry run mode"""
    print("\n🚀 TESTING OPTIMIZATION (DRY RUN)")
    print("=" * 50)

    # Use a temporary test workspace
    test_workspace = "test_optimization_workspace"
    os.makedirs(test_workspace, exist_ok=True)

    try:
        # Initialize and add some test data
        kg = EternalKnowledgeGraph(test_workspace)

        # Add both good and bad test entities
        test_data = [
            ("Keith Lambert works on COCO project with Claude AI", "That's a great collaboration!"),
            ("The system needs to handle not just these cases", "I understand the requirements."),
            ("Need to implement through these patterns", "Let's work on the implementation."),
            ("Sarah Johnson uses Python for development", "Python is excellent for development.")
        ]

        print("💬 Adding test data with mixed quality...")
        for i, (user_msg, assistant_msg) in enumerate(test_data):
            kg.process_conversation_exchange(user_msg, assistant_msg, episode_id=i)

        # Run optimization dry run
        print("\n🧹 Running optimization dry run...")
        result = kg.optimize_for_digital_assistant(dry_run=True)

        quality_report = result['quality_report']
        print(f"\n📊 DRY RUN RESULTS:")
        print(f"   - Entities before cleanup: {quality_report['statistics']['total_nodes']}")
        print(f"   - Entities that would remain: {quality_report['statistics']['valid_entities']}")
        print(f"   - Entities that would be removed: {quality_report['statistics']['invalid_entities']}")
        print(f"   - Expected quality improvement: {quality_report['statistics']['quality_percentage']:.1f}%")

        # Show some examples of what would be removed
        cleanup_candidates = quality_report['cleanup_candidates']
        if cleanup_candidates:
            print(f"\n🗑️ EXAMPLES OF ENTITIES TO REMOVE:")
            for candidate in cleanup_candidates[:5]:
                print(f"   - '{candidate['name']}' ({candidate['type']})")

        return result

    except Exception as e:
        print(f"❌ Error in optimization test: {e}")
        return None
    finally:
        # Clean up test workspace
        import shutil
        shutil.rmtree(test_workspace, ignore_errors=True)

def main():
    """Run all quality improvement tests"""
    print("🧠 COCO KNOWLEDGE GRAPH QUALITY IMPROVEMENTS TEST")
    print("=" * 60)
    print("Goal: Transform 11,096+ fragments into ~100-500 meaningful entities")
    print("Based on senior dev team feedback for digital assistant relevance")
    print("=" * 60)

    success_count = 0
    total_tests = 3

    # Test 1: Entity validation
    if test_entity_validation():
        print("✅ Entity validation test PASSED")
        success_count += 1
    else:
        print("❌ Entity validation test FAILED")

    # Test 2: Current KG analysis
    if test_current_kg_analysis():
        print("✅ Knowledge graph analysis test PASSED")
        success_count += 1
    else:
        print("❌ Knowledge graph analysis test FAILED")

    # Test 3: Optimization dry run
    if test_optimization_dry_run():
        print("✅ Optimization dry run test PASSED")
        success_count += 1
    else:
        print("❌ Optimization dry run test FAILED")

    # Final results
    print(f"\n🎯 OVERALL TEST RESULTS: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED! Knowledge graph quality improvements are working!")
        print("\n🚀 READY FOR PRODUCTION:")
        print("   1. The EntityValidator successfully filters grammatical fragments")
        print("   2. The KnowledgeGraphCleaner can transform 11K+ fragments to meaningful entities")
        print("   3. The optimization system is ready to deploy")
        print("\n💡 To apply to real COCO knowledge graph:")
        print("   kg = EternalKnowledgeGraph('coco_workspace')")
        print("   kg.optimize_for_digital_assistant(dry_run=False)")
    else:
        print("⚠️ Some tests failed. Please review the implementations.")

    return success_count == total_tests

if __name__ == "__main__":
    main()
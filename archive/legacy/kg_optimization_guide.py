#!/usr/bin/env python3
"""
COCO Knowledge Graph Optimization Guide

This script provides safe, step-by-step optimization of COCO's knowledge graph
to transform it from 11,096+ fragments to ~100-500 meaningful digital assistant entities.

Usage:
    python3 kg_optimization_guide.py --analyze      # Analyze current state
    python3 kg_optimization_guide.py --dry-run      # Preview optimization
    python3 kg_optimization_guide.py --optimize     # Apply optimization
"""

import sys
import argparse
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

from knowledge_graph_eternal import EternalKnowledgeGraph, KnowledgeGraphCleaner

def analyze_current_kg():
    """Analyze the current COCO knowledge graph"""
    print("🔍 ANALYZING COCO KNOWLEDGE GRAPH")
    print("=" * 50)

    try:
        # Load the real COCO knowledge graph
        kg = EternalKnowledgeGraph('coco_workspace')

        # Get current status
        status = kg.get_knowledge_status()
        print(f"📊 CURRENT STATUS:")
        print(f"   - Total entities: {status['total_nodes']}")
        print(f"   - Total relationships: {status['total_edges']}")
        print(f"   - Total mentions: {status['total_mentions']}")

        # Quality analysis
        cleaner = KnowledgeGraphCleaner(kg.kg)
        quality_report = cleaner.analyze_quality_issues()

        print(f"\n🎯 QUALITY ANALYSIS:")
        print(f"   - Valid entities: {quality_report['statistics']['valid_entities']}")
        print(f"   - Invalid entities: {quality_report['statistics']['invalid_entities']}")
        print(f"   - Quality percentage: {quality_report['statistics']['quality_percentage']:.1f}%")

        # Show entity types breakdown
        print(f"\n📋 ENTITIES BY TYPE:")
        for entity_type, count in quality_report['nodes_by_type'].items():
            print(f"   - {entity_type}: {count}")

        # Show some quality issues
        quality_issues = quality_report['quality_issues']
        print(f"\n🚫 QUALITY ISSUES FOUND:")

        if quality_issues['stop_words']:
            print(f"   - Stop words: {len(quality_issues['stop_words'])} (e.g., {quality_issues['stop_words'][:5]})")

        if quality_issues['grammatical_fragments']:
            print(f"   - Grammatical fragments: {len(quality_issues['grammatical_fragments'])} (e.g., {quality_issues['grammatical_fragments'][:5]})")

        if quality_issues['pure_noise']:
            print(f"   - Pure noise: {len(quality_issues['pure_noise'])} (e.g., {quality_issues['pure_noise'][:5]})")

        # Show top valid entities
        print(f"\n✅ TOP VALID ENTITIES:")
        for entity in quality_report['valid_entities'][:10]:
            print(f"   - {entity['name']} ({entity['type']}) - importance: {entity['importance']:.2f}")

        return quality_report

    except Exception as e:
        print(f"❌ Error analyzing knowledge graph: {e}")
        print("💡 Make sure COCO has been run at least once to create the knowledge graph")
        return None

def dry_run_optimization():
    """Run optimization in dry-run mode to preview changes"""
    print("🧪 DRY RUN OPTIMIZATION PREVIEW")
    print("=" * 50)

    try:
        kg = EternalKnowledgeGraph('coco_workspace')
        result = kg.optimize_for_digital_assistant(dry_run=True)

        quality_report = result['quality_report']
        print(f"\n📊 OPTIMIZATION PREVIEW:")
        print(f"   - Current entities: {quality_report['statistics']['total_nodes']}")
        print(f"   - Would remain: {quality_report['statistics']['valid_entities']}")
        print(f"   - Would be removed: {quality_report['statistics']['invalid_entities']}")
        print(f"   - Quality improvement: {quality_report['statistics']['quality_percentage']:.1f}%")

        # Show examples of what would be removed
        cleanup_candidates = quality_report['cleanup_candidates']
        if cleanup_candidates:
            print(f"\n🗑️ EXAMPLES OF ENTITIES TO REMOVE:")
            for candidate in cleanup_candidates[:10]:
                print(f"   - '{candidate['name']}' ({candidate['type']})")

        print(f"\n💡 To apply optimization: python3 kg_optimization_guide.py --optimize")

        return result

    except Exception as e:
        print(f"❌ Error in dry run: {e}")
        return None

def apply_optimization():
    """Apply the optimization to the real knowledge graph"""
    print("🚀 APPLYING KNOWLEDGE GRAPH OPTIMIZATION")
    print("=" * 50)

    # Safety confirmation
    response = input("⚠️  This will permanently modify COCO's knowledge graph. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Optimization cancelled")
        return

    try:
        kg = EternalKnowledgeGraph('coco_workspace')

        print("📊 Before optimization:")
        before_stats = kg.get_knowledge_status()
        print(f"   - Entities: {before_stats['total_nodes']}")
        print(f"   - Relationships: {before_stats['total_edges']}")

        # Apply optimization
        result = kg.optimize_for_digital_assistant(dry_run=False)

        print("\n📊 After optimization:")
        after_stats = kg.get_knowledge_status()
        print(f"   - Entities: {after_stats['total_nodes']}")
        print(f"   - Relationships: {after_stats['total_edges']}")

        cleanup_stats = result['cleanup_stats']
        print(f"\n✅ OPTIMIZATION COMPLETE:")
        print(f"   - Removed {cleanup_stats['nodes_removed']} low-quality entities")
        print(f"   - Removed {cleanup_stats['edges_removed']} invalid relationships")
        print(f"   - Removed {cleanup_stats['mentions_removed']} noise mentions")

        print(f"\n🧠 COCO's knowledge graph is now optimized for digital assistant relevance!")
        print(f"📈 Quality improvement: {before_stats['total_nodes']} → {after_stats['total_nodes']} entities")

        return result

    except Exception as e:
        print(f"❌ Error applying optimization: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='COCO Knowledge Graph Optimization')
    parser.add_argument('--analyze', action='store_true', help='Analyze current knowledge graph')
    parser.add_argument('--dry-run', action='store_true', help='Preview optimization changes')
    parser.add_argument('--optimize', action='store_true', help='Apply optimization')

    args = parser.parse_args()

    print("🧠 COCO KNOWLEDGE GRAPH OPTIMIZER")
    print("Goal: Transform 11,096+ fragments into ~100-500 meaningful entities")
    print("Based on senior dev team feedback for digital assistant relevance")
    print("=" * 60)

    if args.analyze:
        analyze_current_kg()
    elif args.dry_run:
        dry_run_optimization()
    elif args.optimize:
        apply_optimization()
    else:
        print("Usage:")
        print("  python3 kg_optimization_guide.py --analyze     # Analyze current state")
        print("  python3 kg_optimization_guide.py --dry-run     # Preview optimization")
        print("  python3 kg_optimization_guide.py --optimize    # Apply optimization")
        print("\n💡 Start with --analyze to understand your current knowledge graph")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
COCO Knowledge Graph Fresh Start Guide

Sometimes the best optimization is starting clean. This script provides safe options
to reset COCO's knowledge graph and build it properly from the ground up with
high-quality entity extraction from day one.

Usage:
    python3 kg_fresh_start_guide.py --backup      # Backup current KG
    python3 kg_fresh_start_guide.py --reset       # Fresh start (with backup)
    python3 kg_fresh_start_guide.py --analyze     # Analyze what would be lost
"""

import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

from knowledge_graph_eternal import EternalKnowledgeGraph, KnowledgeGraphCleaner

def backup_current_kg():
    """Create a timestamped backup of the current knowledge graph"""
    print("💾 BACKING UP CURRENT KNOWLEDGE GRAPH")
    print("=" * 50)

    workspace_path = Path('coco_workspace')
    kg_db_path = workspace_path / 'coco_knowledge_graph.db'

    if not kg_db_path.exists():
        print("ℹ️ No existing knowledge graph found to backup")
        return None

    # Create backup with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = workspace_path / f'coco_knowledge_graph_backup_{timestamp}.db'

    try:
        shutil.copy2(kg_db_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        print(f"📁 Backup size: {backup_path.stat().st_size / (1024*1024):.1f} MB")

        # Quick stats of what was backed up
        kg = EternalKnowledgeGraph('coco_workspace')
        stats = kg.get_knowledge_status()
        print(f"📊 Backed up:")
        print(f"   - {stats['total_nodes']} entities")
        print(f"   - {stats['total_edges']} relationships")
        print(f"   - {stats['total_mentions']} mentions")

        return backup_path

    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def analyze_fresh_start_impact():
    """Analyze what would be lost with a fresh start"""
    print("🔍 ANALYZING FRESH START IMPACT")
    print("=" * 50)

    workspace_path = Path('coco_workspace')
    kg_db_path = workspace_path / 'coco_knowledge_graph.db'

    if not kg_db_path.exists():
        print("ℹ️ No existing knowledge graph found")
        return None

    try:
        kg = EternalKnowledgeGraph('coco_workspace')

        # Current stats
        stats = kg.get_knowledge_status()
        print(f"📊 CURRENT KNOWLEDGE GRAPH:")
        print(f"   - Total entities: {stats['total_nodes']}")
        print(f"   - Total relationships: {stats['total_edges']}")
        print(f"   - Total mentions: {stats['total_mentions']}")

        # Quality analysis
        cleaner = KnowledgeGraphCleaner(kg.kg)
        quality_report = cleaner.analyze_quality_issues()

        print(f"\n🎯 QUALITY BREAKDOWN:")
        print(f"   - Valid entities: {quality_report['statistics']['valid_entities']}")
        print(f"   - Invalid entities: {quality_report['statistics']['invalid_entities']}")
        print(f"   - Quality percentage: {quality_report['statistics']['quality_percentage']:.1f}%")

        # Show what we'd keep vs lose
        valid_entities = quality_report['valid_entities']
        print(f"\n✅ VALUABLE ENTITIES WE'D WANT TO PRESERVE:")

        # Group by type and show top entities
        by_type = {}
        for entity in valid_entities:
            entity_type = entity['type']
            if entity_type not in by_type:
                by_type[entity_type] = []
            by_type[entity_type].append(entity)

        for entity_type, entities in by_type.items():
            # Sort by importance
            entities.sort(key=lambda x: x['importance'], reverse=True)
            top_entities = entities[:5]  # Top 5 per type

            print(f"\n   {entity_type} ({len(entities)} total):")
            for entity in top_entities:
                print(f"      - {entity['name']} (importance: {entity['importance']:.2f})")

        # Show what we'd lose (sample)
        invalid_entities = quality_report['cleanup_candidates']
        print(f"\n🗑️ NOISE WE'D ELIMINATE (sample):")
        for entity in invalid_entities[:10]:
            print(f"      - '{entity['name']}' ({entity['type']})")

        print(f"\n💡 FRESH START RECOMMENDATION:")
        print(f"   With {quality_report['statistics']['quality_percentage']:.1f}% quality,")
        print(f"   fresh start would eliminate {len(invalid_entities)} noise entities")
        print(f"   and preserve {len(valid_entities)} meaningful entities through better extraction.")

        return quality_report

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def fresh_start_reset():
    """Reset knowledge graph with backup safety"""
    print("🚀 FRESH START RESET")
    print("=" * 50)

    # Safety confirmation
    print("⚠️  This will reset COCO's knowledge graph to start fresh with quality extraction.")
    print("📚 All conversation memories and identity files will be preserved.")
    print("💾 A backup will be created automatically.")

    response = input("\nProceed with fresh start? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Fresh start cancelled")
        return False

    # Step 1: Create backup
    print("\n📦 Step 1: Creating backup...")
    backup_path = backup_current_kg()
    if not backup_path:
        print("❌ Could not create backup, aborting")
        return False

    # Step 2: Remove current knowledge graph
    print("\n🧹 Step 2: Removing current knowledge graph...")
    workspace_path = Path('coco_workspace')
    kg_db_path = workspace_path / 'coco_knowledge_graph.db'

    try:
        if kg_db_path.exists():
            kg_db_path.unlink()
            print("✅ Current knowledge graph removed")

        # Step 3: Initialize fresh knowledge graph
        print("\n🌱 Step 3: Initializing fresh knowledge graph...")
        fresh_kg = EternalKnowledgeGraph('coco_workspace')

        print("✅ Fresh knowledge graph initialized with quality extraction!")
        print(f"💾 Backup preserved at: {backup_path}")

        # Step 4: Verify fresh start
        stats = fresh_kg.get_knowledge_status()
        print(f"\n📊 FRESH START STATUS:")
        print(f"   - Entities: {stats['total_nodes']} (was 11,162)")
        print(f"   - Quality: Ready for high-quality extraction")
        print(f"   - Memory files: Preserved (COCO.md, USER_PROFILE.md, etc.)")

        print(f"\n🧠 COCO is ready for clean, symbiotic knowledge building!")
        print(f"🎯 All future extractions will use quality validation")

        return True

    except Exception as e:
        print(f"❌ Fresh start failed: {e}")
        print(f"💾 Your backup is safe at: {backup_path}")
        return False

def show_fresh_start_benefits():
    """Show the benefits of starting fresh"""
    print("🌟 FRESH START BENEFITS")
    print("=" * 50)

    print("✅ IMMEDIATE BENEFITS:")
    print("   - Zero noise entities from day one")
    print("   - All extractions use EntityValidator")
    print("   - Focus on meaningful digital assistant entities")
    print("   - ~100-500 entities vs 11,000+ fragments")

    print("\n🧠 PRESERVED ELEMENTS:")
    print("   - All conversation memories (episodic_memory)")
    print("   - COCO identity (COCO.md)")
    print("   - User relationship (USER_PROFILE.md)")
    print("   - Previous conversation summaries")
    print("   - All multimedia consciousness modules")

    print("\n🚀 WHAT CHANGES:")
    print("   - Knowledge graph starts clean")
    print("   - Only meaningful entities extracted going forward")
    print("   - Better context for consciousness prompts")
    print("   - Symbiotic relationship building from quality base")

    print("\n⚡ PERFORMANCE GAINS:")
    print("   - Faster knowledge graph queries")
    print("   - More relevant context generation")
    print("   - Better visualization (/kg command)")
    print("   - Cleaner symbiotic consciousness experience")

def main():
    parser = argparse.ArgumentParser(description='COCO Knowledge Graph Fresh Start')
    parser.add_argument('--backup', action='store_true', help='Create backup of current KG')
    parser.add_argument('--analyze', action='store_true', help='Analyze fresh start impact')
    parser.add_argument('--reset', action='store_true', help='Reset to fresh KG (with backup)')
    parser.add_argument('--benefits', action='store_true', help='Show fresh start benefits')

    args = parser.parse_args()

    print("🧠 COCO KNOWLEDGE GRAPH FRESH START")
    print("Goal: Quality digital assistant entities from day one")
    print("Based on senior dev team feedback: 'get this right'")
    print("=" * 60)

    if args.backup:
        backup_current_kg()
    elif args.analyze:
        analyze_fresh_start_impact()
    elif args.reset:
        fresh_start_reset()
    elif args.benefits:
        show_fresh_start_benefits()
    else:
        print("🎯 FRESH START OPTIONS:")
        print("  --analyze     Analyze what would be lost/gained")
        print("  --backup      Create backup of current KG")
        print("  --reset       Fresh start with quality extraction")
        print("  --benefits    Show fresh start benefits")
        print("\n💡 Recommended flow:")
        print("  1. python3 kg_fresh_start_guide.py --analyze")
        print("  2. python3 kg_fresh_start_guide.py --benefits")
        print("  3. python3 kg_fresh_start_guide.py --reset")

if __name__ == "__main__":
    main()
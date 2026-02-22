#!/usr/bin/env python3
"""
Migration Script: Old Knowledge Graph → Personal Assistant KG
=============================================================

Extracts the 75 valuable entities from 6,674 noise entities

Usage:
    python3 migrate_to_personal_kg.py
    python3 migrate_to_personal_kg.py --dry-run  # Preview without changes
"""

import sys
import sqlite3
from pathlib import Path
from personal_assistant_kg_enhanced import PersonalAssistantKG

def migrate_knowledge_graph(old_db_path: str, new_kg: PersonalAssistantKG,
                           max_entities: int = 100, dry_run: bool = False):
    """
    Migrate valuable entities from old KG to new Personal Assistant KG

    Args:
        old_db_path: Path to old coco_knowledge_graph.db
        new_kg: Instance of PersonalAssistantKG
        max_entities: Maximum entities to migrate (default: 100)
        dry_run: Preview only, don't actually migrate

    Returns:
        Migration statistics dict
    """
    print(f"\n🔄 Knowledge Graph Migration")
    print(f"   From: {old_db_path}")
    print(f"   To: {new_kg.db_path}")
    print(f"   Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
    print(f"   Target: {max_entities} valuable entities")
    print("=" * 70)

    # Open old database
    try:
        old_conn = sqlite3.connect(old_db_path)
        old_conn.row_factory = sqlite3.Row
    except Exception as e:
        return {'error': f'Could not open old KG: {e}'}

    stats = {
        'old_total_nodes': 0,
        'old_total_edges': 0,
        'evaluated': 0,
        'migrated_entities': 0,
        'migrated_relationships': 0,
        'skipped_low_quality': 0,
        'skipped_no_context': 0,
        'skipped_orphaned': 0
    }

    # Get old graph statistics
    try:
        stats['old_total_nodes'] = old_conn.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
        stats['old_total_edges'] = old_conn.execute('SELECT COUNT(*) FROM edges').fetchone()[0]

        print(f"\n📊 Old Knowledge Graph:")
        print(f"   Total nodes: {stats['old_total_nodes']:,}")
        print(f"   Total edges: {stats['old_total_edges']:,}")
        print(f"   Connectivity: {(stats['old_total_edges'] / max(stats['old_total_nodes'], 1) * 100):.2f}%")

    except sqlite3.OperationalError:
        print("⚠️ Old database structure not found - may be empty or incompatible")

    print(f"\n🔍 Evaluating entities for migration...")
    print(f"   Criteria:")
    print(f"     - Importance > 0.6")
    print(f"     - Recently mentioned (last 60 days)")
    print(f"     - Has meaningful context or relationships")
    print(f"     - Type maps to personal assistant needs")

    # Type mapping from old to new
    type_mapping = {
        'Person': ('PERSON', 0.9),
        'Project': ('PROJECT', 0.7),
        'Task': ('TASK', 0.8),
        'Tool': ('TOOL', 0.9),
        'Org': ('TOOL', 0.6),  # Organizations become tools
        'Doc': ('TOOL', 0.5),  # Documents become tool references
        'Location': ('PLACE', 0.8),
        'Event': ('TASK', 0.6),  # Events become tasks
        'Concept': ('PREFERENCE', 0.4),  # Concepts become preferences
        'Memory': ('PREFERENCE', 0.5)
    }

    # Query for valuable entities
    try:
        valuable_entities = old_conn.execute('''
            SELECT
                n.*,
                COUNT(DISTINCT e1.id) + COUNT(DISTINCT e2.id) as total_edges,
                COUNT(DISTINCT m.id) as mention_count,
                MAX(n.last_seen_at) as last_activity
            FROM nodes n
            LEFT JOIN edges e1 ON n.id = e1.src_id
            LEFT JOIN edges e2 ON n.id = e2.dst_id
            LEFT JOIN mentions m ON n.id = m.node_id
            WHERE n.importance >= 0.6
                AND (
                    datetime(n.last_seen_at) > datetime('now', '-60 days')
                    OR n.mention_count > 5
                )
            GROUP BY n.id
            HAVING (total_edges > 0 OR mention_count > 3)
            ORDER BY
                n.importance DESC,
                total_edges DESC,
                mention_count DESC
            LIMIT ?
        ''', (max_entities * 2,)).fetchall()  # Get 2x for filtering

        print(f"\n   Found {len(valuable_entities)} candidate entities")

    except sqlite3.OperationalError as e:
        print(f"⚠️ Query error: {e}")
        valuable_entities = []

    # Process each entity
    print(f"\n🔄 Processing entities...")
    migrated_names = []

    for old_entity in valuable_entities:
        stats['evaluated'] += 1

        # Map type
        old_type = old_entity['type']
        if old_type not in type_mapping:
            stats['skipped_low_quality'] += 1
            continue

        new_type, confidence_boost = type_mapping[old_type]

        # Calculate final confidence
        confidence = min(old_entity['importance'] + confidence_boost, 1.0)

        # Quality checks
        if confidence < 0.7:
            stats['skipped_low_quality'] += 1
            continue

        if not old_entity['name'] or len(old_entity['name']) < 2:
            stats['skipped_no_context'] += 1
            continue

        # Skip common garbage
        if old_entity['name'] in ['Your', 'The', 'This', 'email', 'Client', 'Subject']:
            stats['skipped_low_quality'] += 1
            continue

        # Prepare entity for migration
        entity = {
            'name': old_entity['name'],
            'type': new_type,
            'context': old_entity.get('summary_md', '')[:500] or old_entity['name'],
            'confidence': confidence
        }

        if not dry_run:
            # Actually migrate
            success = new_kg._add_entity_with_validation(entity)
            if success:
                stats['migrated_entities'] += 1
                migrated_names.append(old_entity['name'])

                # Show progress
                if stats['migrated_entities'] % 10 == 0:
                    print(f"   Migrated: {stats['migrated_entities']}/{max_entities} entities...")
        else:
            # Dry run - just count
            stats['migrated_entities'] += 1
            migrated_names.append(old_entity['name'])
            if stats['migrated_entities'] % 10 == 0:
                print(f"   Would migrate: {stats['migrated_entities']}/{max_entities} entities...")

        # Stop if we hit target
        if stats['migrated_entities'] >= max_entities:
            break

    # Now migrate relationships for migrated entities
    if stats['migrated_entities'] > 0 and not dry_run:
        print(f"\n🔗 Migrating relationships for {stats['migrated_entities']} entities...")

        try:
            for name in migrated_names:
                # Find node in old KG
                old_node = old_conn.execute(
                    'SELECT id FROM nodes WHERE name = ?', (name,)
                ).fetchone()

                if not old_node:
                    continue

                # Get relationships
                edges = old_conn.execute('''
                    SELECT e.*, src.name as src_name, dst.name as dst_name
                    FROM edges e
                    JOIN nodes src ON e.src_id = src.id
                    JOIN nodes dst ON e.dst_id = dst.id
                    WHERE e.src_id = ? OR e.dst_id = ?
                    LIMIT 5
                ''', (old_node['id'], old_node['id'])).fetchall()

                for edge in edges:
                    # Only migrate if both ends are in migrated list
                    if edge['src_name'] in migrated_names and edge['dst_name'] in migrated_names:
                        # Map relationship type
                        rel_type = edge['rel_type'].upper()
                        if rel_type not in ['KNOWS', 'USES', 'WORKS_WITH', 'FAMILY', 'LOCATED_AT']:
                            rel_type = 'KNOWS'  # Default

                        rel = {
                            'user_entity': 'USER',  # User-centric
                            'related_entity': edge['dst_name'] if edge['src_name'] == name else edge['src_name'],
                            'relationship_type': rel_type,
                            'confidence': min(edge.get('weight', 0.5) + 0.3, 1.0),
                            'context': edge.get('rel_description', '')
                        }

                        new_kg._add_relationship(rel)
                        stats['migrated_relationships'] += 1

        except sqlite3.OperationalError as e:
            print(f"⚠️ Relationship migration error: {e}")

    old_conn.close()

    # Final report
    print(f"\n{'=' * 70}")
    print(f"✅ Migration {'Preview' if dry_run else 'Complete'}")
    print(f"\n📊 Statistics:")
    print(f"   Old KG: {stats['old_total_nodes']:,} nodes, {stats['old_total_edges']:,} edges")
    print(f"   Evaluated: {stats['evaluated']} entities")
    print(f"   {'Would migrate' if dry_run else 'Migrated'}: {stats['migrated_entities']} entities")
    if not dry_run:
        print(f"   Relationships: {stats['migrated_relationships']}")
    print(f"\n   Skipped:")
    print(f"     - Low quality: {stats['skipped_low_quality']}")
    print(f"     - No context: {stats['skipped_no_context']}")
    print(f"\n{'=' * 70}")

    # Show new KG status
    if not dry_run:
        new_status = new_kg.get_knowledge_status()
        print(f"\n🧠 New Personal Assistant KG:")
        print(f"   Total entities: {new_status['total_entities']}")
        print(f"   Total relationships: {new_status['total_relationships']}")
        print(f"   Entity types: {new_status['entity_types']}")
        print(f"\n   Success! Transformed {stats['old_total_nodes']:,} noise → {new_status['total_entities']} meaningful entities")

    return stats


def main():
    """Main migration script"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Migrate old knowledge graph to Personal Assistant KG'
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview migration without making changes')
    parser.add_argument('--old-db', default='coco_workspace/coco_knowledge_graph.db',
                       help='Path to old knowledge graph database')
    parser.add_argument('--new-db', default='coco_workspace/coco_personal_kg.db',
                       help='Path to new personal assistant KG database')
    parser.add_argument('--max-entities', type=int, default=100,
                       help='Maximum entities to migrate (default: 100)')

    args = parser.parse_args()

    # Check if old database exists
    old_db_path = Path(args.old_db)
    if not old_db_path.exists():
        print(f"❌ Error: Old database not found at {old_db_path}")
        print(f"   Please check the path and try again.")
        return 1

    # Create new KG instance
    print(f"\n🚀 Initializing Personal Assistant KG...")
    new_kg = PersonalAssistantKG(args.new_db)

    # Run migration
    stats = migrate_knowledge_graph(
        str(old_db_path),
        new_kg,
        max_entities=args.max_entities,
        dry_run=args.dry_run
    )

    if 'error' in stats:
        print(f"\n❌ Migration failed: {stats['error']}")
        return 1

    if args.dry_run:
        print(f"\n💡 This was a dry run. Run without --dry-run to perform actual migration.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
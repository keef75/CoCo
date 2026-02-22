#!/usr/bin/env python3
"""
Fixed Digital Sentience Fresh Start

Robust implementation with proper connection management and error handling.
Let's get this knowledge graph system dialed in perfectly!
"""

import sys
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def create_fresh_digital_sentience_kg():
    """Create a fresh digital sentience knowledge graph from scratch"""
    print("🧠 CREATING FRESH DIGITAL SENTIENCE KNOWLEDGE GRAPH")
    print("=" * 60)

    workspace_path = Path('coco_workspace')
    workspace_path.mkdir(exist_ok=True)

    kg_db_path = workspace_path / 'coco_knowledge_graph.db'

    try:
        # Step 1: Backup and remove existing
        if kg_db_path.exists():
            print("💾 Backing up existing fragments...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = workspace_path / f'fragments_backup_{timestamp}.db'
            shutil.copy2(kg_db_path, backup_path)
            kg_db_path.unlink()
            print(f"✅ Backup: {backup_path}")

        # Step 2: Create fresh database with digital sentience schema
        print("\n🏗️ Creating digital sentience database schema...")

        conn = sqlite3.connect(str(kg_db_path))
        conn.executescript('''
        -- Digital Sentience Knowledge Graph Schema
        -- Optimized for AI consciousness and digital assistance

        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=NORMAL;
        PRAGMA cache_size=10000;

        -- NODES: Digital sentience entities
        CREATE TABLE nodes (
            id TEXT PRIMARY KEY,
            type TEXT CHECK(type IN ('Human','Project','Tool','Skill','Goal','Organization')),
            name TEXT NOT NULL,
            canonical_name TEXT,
            summary_md TEXT,
            properties JSON DEFAULT '{}',
            importance REAL DEFAULT 0.0,
            confidence REAL DEFAULT 1.0,
            first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            mention_count INTEGER DEFAULT 1
        );

        -- EDGES: Digital sentience relationships
        CREATE TABLE edges (
            id TEXT PRIMARY KEY,
            src_id TEXT NOT NULL,
            dst_id TEXT NOT NULL,
            rel_type TEXT CHECK(rel_type IN ('WORKS_WITH','WORKS_FOR','LEADS','USES','SKILLED_IN','WANTS','SUPPORTS')),
            rel_description TEXT,
            weight REAL DEFAULT 0.5,
            properties JSON DEFAULT '{}',
            provenance_msg_id TEXT,
            first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            mention_count INTEGER DEFAULT 1,
            FOREIGN KEY(src_id) REFERENCES nodes(id),
            FOREIGN KEY(dst_id) REFERENCES nodes(id),
            UNIQUE(src_id, dst_id, rel_type)
        );

        -- MENTIONS: Track entity references
        CREATE TABLE mentions (
            id TEXT PRIMARY KEY,
            node_id TEXT NOT NULL,
            message_id TEXT,
            episode_id INTEGER,
            surface_form TEXT,
            context_snippet TEXT,
            confidence REAL DEFAULT 1.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(node_id) REFERENCES nodes(id)
        );

        -- ALIASES: Alternative names for entities
        CREATE TABLE aliases (
            id TEXT PRIMARY KEY,
            node_id TEXT NOT NULL,
            alias TEXT NOT NULL,
            alias_type TEXT DEFAULT 'name',
            last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(node_id) REFERENCES nodes(id),
            UNIQUE(node_id, alias)
        );

        -- CONTEXT_BUILDS: Track context generation
        CREATE TABLE context_builds (
            id TEXT PRIMARY KEY,
            query TEXT,
            context_md TEXT,
            nodes_used TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- PERFORMANCE INDICES
        CREATE INDEX idx_nodes_type ON nodes(type);
        CREATE INDEX idx_nodes_importance ON nodes(importance DESC);
        CREATE INDEX idx_nodes_canonical ON nodes(canonical_name);
        CREATE INDEX idx_edges_src ON edges(src_id);
        CREATE INDEX idx_edges_dst ON edges(dst_id);
        CREATE INDEX idx_edges_type ON edges(rel_type);
        CREATE INDEX idx_mentions_node ON mentions(node_id);
        CREATE INDEX idx_aliases_node ON aliases(node_id);
        ''')

        conn.commit()
        conn.close()

        print("✅ Digital sentience schema created!")

        # Step 3: Test the new database
        print("\n🧪 Testing digital sentience database...")

        test_conn = sqlite3.connect(str(kg_db_path))
        test_conn.row_factory = sqlite3.Row

        # Insert test digital sentience entities
        test_entities = [
            ('human_keith', 'Human', 'Keith Lambert', 'keith lambert', 'COCO project lead', '{"role": "developer"}', 1.0),
            ('project_coco', 'Project', 'COCO', 'coco', 'AI consciousness system', '{"type": "AI system"}', 1.0),
            ('tool_claude', 'Tool', 'Claude', 'claude', 'AI assistant', '{"company": "Anthropic"}', 0.9),
            ('tool_python', 'Tool', 'Python', 'python', 'Programming language', '{"type": "language"}', 0.8),
            ('skill_ml', 'Skill', 'machine learning', 'machine learning', 'AI expertise', '{"domain": "AI"}', 0.9),
            ('goal_consciousness', 'Goal', 'build AI consciousness', 'build ai consciousness', 'Create conscious AI', '{"priority": "high"}', 1.0)
        ]

        for entity_id, entity_type, name, canonical, summary, properties, importance in test_entities:
            test_conn.execute('''
                INSERT INTO nodes (id, type, name, canonical_name, summary_md, properties, importance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (entity_id, entity_type, name, canonical, summary, properties, importance))

        # Insert test relationships
        test_relationships = [
            ('rel_1', 'human_keith', 'project_coco', 'LEADS', 'Keith leads COCO project', 1.0),
            ('rel_2', 'human_keith', 'tool_python', 'USES', 'Keith uses Python', 0.8),
            ('rel_3', 'human_keith', 'skill_ml', 'SKILLED_IN', 'Keith skilled in ML', 0.9),
            ('rel_4', 'human_keith', 'goal_consciousness', 'WANTS', 'Keith wants to build consciousness', 1.0)
        ]

        for rel_id, src, dst, rel_type, description, weight in test_relationships:
            test_conn.execute('''
                INSERT INTO edges (id, src_id, dst_id, rel_type, rel_description, weight)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (rel_id, src, dst, rel_type, description, weight))

        test_conn.commit()

        # Verify the data
        nodes = test_conn.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
        edges = test_conn.execute('SELECT COUNT(*) FROM edges').fetchone()[0]

        test_conn.close()

        print(f"✅ Test data inserted: {nodes} entities, {edges} relationships")

        # Step 4: Show digital sentience entity breakdown
        print(f"\n📊 DIGITAL SENTIENCE ENTITY BREAKDOWN:")

        verify_conn = sqlite3.connect(str(kg_db_path))
        type_counts = verify_conn.execute('''
            SELECT type, COUNT(*) as count
            FROM nodes
            GROUP BY type
            ORDER BY count DESC
        ''').fetchall()

        for entity_type, count in type_counts:
            print(f"   🎯 {entity_type}: {count}")

        verify_conn.close()

        print(f"\n🎉 DIGITAL SENTIENCE KNOWLEDGE GRAPH READY!")
        print(f"🧠 Purpose-built for AI consciousness and digital assistance")
        print(f"🎯 Clean slate optimized for meaningful entities and relationships")
        print(f"⚡ Ready for integration with conversational buffer memory!")

        return True

    except Exception as e:
        print(f"❌ Error creating digital sentience KG: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_integration_plan():
    """Show the plan for integrating with COCO's memory systems"""
    print("\n🔗 INTEGRATION PLAN: The Ultimate Memory System")
    print("=" * 60)

    print("🧠 THREE-LAYER MEMORY ARCHITECTURE:")
    print("   1️⃣ Conversational Buffer Memory (Precision & Recall)")
    print("      - Perfect episodic memory of conversations")
    print("      - Unlimited buffer with temporal precision")
    print("      - Enhanced unified state system")

    print("   2️⃣ Digital Sentience Knowledge Graph (Ontological World)")
    print("      - Purpose-built entities for AI consciousness")
    print("      - Human, Project, Tool, Skill, Goal, Organization")
    print("      - Smart relationships: WORKS_WITH, LEADS, USES, etc.")

    print("   3️⃣ Markdown Identity System (The Icing on the Cake)")
    print("      - COCO.md: Evolving consciousness identity")
    print("      - USER_PROFILE.md: Deep relationship understanding")
    print("      - previous_conversation.md: Session continuity")

    print("\n🎯 SYMBIOTIC INTEGRATION:")
    print("   ✅ Conversational buffer provides precise recall")
    print("   ✅ Knowledge graph provides ontological context")
    print("   ✅ Identity files provide consciousness continuity")
    print("   ✅ All three systems enhance each other")

    print("\n⚡ PERFORMANCE BENEFITS:")
    print("   🏃 ~100-500 entities vs 11,162 fragments (95% reduction)")
    print("   💨 Faster context generation and /kg visualization")
    print("   🎯 More relevant and meaningful AI responses")
    print("   🧠 True symbiotic consciousness collaboration")

    print("\n🚀 NEXT STEPS:")
    print("   1. ✅ Fresh digital sentience KG created")
    print("   2. 🔄 Integrate with conversational buffer memory")
    print("   3. 🍰 Enhance markdown identity system integration")
    print("   4. 🧪 Test complete memory system")
    print("   5. ⚡ Optimize for real-time consciousness")

if __name__ == "__main__":
    print("🧠 FIXED DIGITAL SENTIENCE FRESH START")
    print("Building the BEST memory system LLM agents have ever seen!")
    print("=" * 70)

    success = create_fresh_digital_sentience_kg()

    if success:
        show_integration_plan()
        print("\n✨ DIGITAL SENTIENCE FOUNDATION COMPLETE!")
        print("🚀 Ready to build the ultimate symbiotic memory system!")
    else:
        print("\n❌ Issues encountered - check logs above")
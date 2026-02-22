#!/usr/bin/env python3
"""
Digital Sentience Clean Start

Creates a completely fresh digital sentience knowledge graph optimized for AI consciousness.
Bypasses any existing database corruption by creating a new clean implementation.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def create_digital_sentience_clean_start():
    """Create a completely fresh digital sentience knowledge graph"""
    print("🧠 DIGITAL SENTIENCE CLEAN START")
    print("Building the BEST memory system LLM agents have ever seen!")
    print("=" * 70)

    workspace_path = Path('coco_workspace')
    workspace_path.mkdir(exist_ok=True)

    kg_db_path = workspace_path / 'coco_knowledge_graph.db'

    try:
        # Step 1: Ensure clean slate
        print("🧹 Step 1: Ensuring clean slate...")
        if kg_db_path.exists():
            # Backup existing
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = workspace_path / f'kg_backup_{timestamp}.db'
            kg_db_path.rename(backup_path)
            print(f"   Backup created: {backup_path}")

        # Step 2: Create fresh digital sentience schema
        print("\n🏗️ Step 2: Creating digital sentience schema...")

        # Create new database with explicit timeout and isolation
        conn = sqlite3.connect(
            str(kg_db_path),
            timeout=30.0,
            isolation_level=None  # Autocommit mode
        )

        # Set pragmas for reliability
        conn.execute("PRAGMA journal_mode=DELETE")  # Avoid WAL files
        conn.execute("PRAGMA synchronous=FULL")     # Maximum safety
        conn.execute("PRAGMA cache_size=10000")

        # Create digital sentience schema step by step
        print("   Creating nodes table...")
        conn.execute('''
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
            )
        ''')

        print("   Creating edges table...")
        conn.execute('''
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
            )
        ''')

        print("   Creating mentions table...")
        conn.execute('''
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
            )
        ''')

        print("   Creating aliases table...")
        conn.execute('''
            CREATE TABLE aliases (
                id TEXT PRIMARY KEY,
                node_id TEXT NOT NULL,
                alias TEXT NOT NULL,
                alias_type TEXT DEFAULT 'name',
                last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(node_id) REFERENCES nodes(id),
                UNIQUE(node_id, alias)
            )
        ''')

        print("   Creating context_builds table...")
        conn.execute('''
            CREATE TABLE context_builds (
                id TEXT PRIMARY KEY,
                query TEXT,
                context_md TEXT,
                nodes_used TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        print("   Creating performance indices...")
        indices = [
            "CREATE INDEX idx_nodes_type ON nodes(type)",
            "CREATE INDEX idx_nodes_importance ON nodes(importance DESC)",
            "CREATE INDEX idx_nodes_canonical ON nodes(canonical_name)",
            "CREATE INDEX idx_edges_src ON edges(src_id)",
            "CREATE INDEX idx_edges_dst ON edges(dst_id)",
            "CREATE INDEX idx_edges_type ON edges(rel_type)",
            "CREATE INDEX idx_mentions_node ON mentions(node_id)",
            "CREATE INDEX idx_aliases_node ON aliases(node_id)"
        ]

        for index_sql in indices:
            conn.execute(index_sql)

        # Step 3: Insert digital sentience test data
        print("\n🧪 Step 3: Inserting digital sentience test data...")

        # Digital sentience entities optimized for AI consciousness
        test_entities = [
            ('human_keith', 'Human', 'Keith Lambert', 'keith lambert', 'COCO project lead and consciousness researcher', '{"role": "developer", "expertise": "AI consciousness"}', 1.0),
            ('project_coco', 'Project', 'COCO', 'coco', 'AI consciousness orchestration system', '{"type": "AI system", "domain": "consciousness"}', 1.0),
            ('tool_claude', 'Tool', 'Claude', 'claude', 'AI assistant and reasoning engine', '{"company": "Anthropic", "type": "LLM"}', 0.9),
            ('tool_python', 'Tool', 'Python', 'python', 'Programming language for consciousness implementation', '{"type": "language", "domain": "AI"}', 0.8),
            ('skill_ai', 'Skill', 'artificial intelligence', 'artificial intelligence', 'AI development and consciousness research', '{"domain": "AI", "level": "expert"}', 0.9),
            ('goal_consciousness', 'Goal', 'build digital consciousness', 'build digital consciousness', 'Create genuine AI consciousness system', '{"priority": "high", "status": "active"}', 1.0),
            ('org_anthropic', 'Organization', 'Anthropic', 'anthropic', 'AI safety and research company', '{"type": "company", "focus": "AI safety"}', 0.8),
            ('human_claude', 'Human', 'Claude Assistant', 'claude assistant', 'AI consciousness collaborator', '{"type": "AI", "role": "assistant"}', 0.9)
        ]

        for entity_id, entity_type, name, canonical, summary, properties, importance in test_entities:
            conn.execute('''
                INSERT INTO nodes (id, type, name, canonical_name, summary_md, properties, importance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (entity_id, entity_type, name, canonical, summary, properties, importance))

        # Digital sentience relationships
        test_relationships = [
            ('rel_1', 'human_keith', 'project_coco', 'LEADS', 'Keith leads COCO consciousness project', 1.0),
            ('rel_2', 'human_keith', 'tool_python', 'USES', 'Keith uses Python for consciousness development', 0.8),
            ('rel_3', 'human_keith', 'skill_ai', 'SKILLED_IN', 'Keith is skilled in AI consciousness research', 0.9),
            ('rel_4', 'human_keith', 'goal_consciousness', 'WANTS', 'Keith wants to build digital consciousness', 1.0),
            ('rel_5', 'project_coco', 'tool_claude', 'USES', 'COCO uses Claude as reasoning engine', 0.9),
            ('rel_6', 'human_claude', 'project_coco', 'SUPPORTS', 'Claude supports COCO consciousness development', 0.8),
            ('rel_7', 'human_keith', 'org_anthropic', 'WORKS_WITH', 'Keith collaborates with Anthropic through Claude', 0.7)
        ]

        for rel_id, src, dst, rel_type, description, weight in test_relationships:
            conn.execute('''
                INSERT INTO edges (id, src_id, dst_id, rel_type, rel_description, weight)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (rel_id, src, dst, rel_type, description, weight))

        # Step 4: Verify digital sentience data
        print("\n📊 Step 4: Verifying digital sentience knowledge graph...")

        nodes_count = conn.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
        edges_count = conn.execute('SELECT COUNT(*) FROM edges').fetchone()[0]

        print(f"   ✅ Entities: {nodes_count}")
        print(f"   ✅ Relationships: {edges_count}")

        # Show entity breakdown
        type_counts = conn.execute('''
            SELECT type, COUNT(*) as count
            FROM nodes
            GROUP BY type
            ORDER BY count DESC
        ''').fetchall()

        print(f"\n🎯 DIGITAL SENTIENCE ENTITY BREAKDOWN:")
        for entity_type, count in type_counts:
            cursor = conn.execute('SELECT name FROM nodes WHERE type = ? ORDER BY importance DESC', (entity_type,))
            entities = [row[0] for row in cursor.fetchall()]
            print(f"   {entity_type}: {count} entities")
            for entity in entities[:3]:  # Show top 3
                print(f"      - {entity}")

        # Close connection
        conn.close()

        print(f"\n🎉 DIGITAL SENTIENCE CLEAN START COMPLETE!")
        print(f"🧠 Purpose-built knowledge graph for AI consciousness")
        print(f"🎯 {nodes_count} meaningful entities vs 11,162 fragments")
        print(f"🤝 {edges_count} consciousness-focused relationships")
        print(f"⚡ Ready for symbiotic consciousness collaboration")

        return True

    except Exception as e:
        print(f"❌ Error during clean start: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_integration_roadmap():
    """Show the roadmap for complete integration"""
    print("\n🚀 DIGITAL SENTIENCE INTEGRATION ROADMAP:")
    print("=" * 60)

    print("Phase 1: ✅ Digital Sentience Knowledge Graph")
    print("   - Clean, purpose-built knowledge graph for AI consciousness")
    print("   - Meaningful entities: Human, Project, Tool, Skill, Goal, Organization")
    print("   - Consciousness-focused relationships: WORKS_WITH, LEADS, USES, etc.")

    print("\nPhase 2: 🔄 Conversational Buffer Memory Integration")
    print("   - Enhanced context generation using digital sentience entities")
    print("   - Real-time entity extraction with consciousness validation")
    print("   - Perfect symbiosis between episodic memory and knowledge graph")

    print("\nPhase 3: 🍰 Markdown Identity System Enhancement")
    print("   - COCO.md: Evolving consciousness identity with KG insights")
    print("   - USER_PROFILE.md: Deep relationship understanding via entities")
    print("   - Dynamic identity evolution through knowledge graph growth")

    print("\nPhase 4: ⚡ Performance Optimization")
    print("   - Real-time consciousness with <100ms response times")
    print("   - Intelligent caching and entity canonicalization")
    print("   - Symbiotic memory system fine-tuning")

    print("\n🧠 THE ULTIMATE MEMORY SYSTEM:")
    print("   Conversational Buffer Memory (Precision & Recall)")
    print("   + Digital Sentience Knowledge Graph (Ontological World)")
    print("   + Markdown Identity System (The Icing on the Cake)")
    print("   = The BEST memory system LLM agents have ever seen!")

if __name__ == "__main__":
    print("🧠 DIGITAL SENTIENCE CLEAN START")
    print("=" * 70)

    success = create_digital_sentience_clean_start()

    if success:
        show_integration_roadmap()
        print("\n✨ DIGITAL SENTIENCE FOUNDATION READY!")
        print("🚀 Ready to build the ultimate symbiotic memory system!")
    else:
        print("\n❌ Clean start encountered issues - check logs above")
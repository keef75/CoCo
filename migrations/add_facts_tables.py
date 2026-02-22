#!/usr/bin/env python3
"""
Dual-Stream Memory Migration: Facts Database + Compression Tracking

This migration adds:
1. Facts table for perfect recall (commands, code, files, decisions)
2. Compression tracking columns to episodes table
3. Comprehensive indexes for performance
4. Validation and rollback support

Author: COCO Development Team
Date: October 24, 2025
Status: Phase 1 - Foundation
"""

import psycopg2
from psycopg2 import sql
import sys
import os
from datetime import datetime

class DualStreamMigration:
    """Migration manager for dual-stream memory architecture"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.cursor = self.conn.cursor()
            print("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def check_prerequisites(self) -> bool:
        """Verify required tables exist"""
        print("\n🔍 Checking prerequisites...")

        try:
            # Check if episodes table exists
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'episodes'
                )
            """)

            episodes_exists = self.cursor.fetchone()[0]

            if not episodes_exists:
                print("❌ Episodes table not found. Please ensure COCO database is initialized.")
                return False

            print("✅ Episodes table exists")

            # Check if sessions table exists
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'sessions'
                )
            """)

            sessions_exists = self.cursor.fetchone()[0]

            if not sessions_exists:
                print("⚠️  Sessions table not found - will skip foreign key constraint")
            else:
                print("✅ Sessions table exists")

            return True

        except Exception as e:
            print(f"❌ Prerequisites check failed: {e}")
            return False

    def check_existing_migration(self) -> bool:
        """Check if migration already applied"""
        try:
            # Check if facts table exists
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'facts'
                )
            """)

            facts_exists = self.cursor.fetchone()[0]

            if facts_exists:
                print("\n⚠️  Facts table already exists!")

                # Get facts count
                self.cursor.execute("SELECT COUNT(*) FROM facts")
                facts_count = self.cursor.fetchone()[0]
                print(f"   Found {facts_count:,} existing facts")

                response = input("\n   Continue with migration? (y/n): ")
                return response.lower() == 'y'

            return True

        except Exception as e:
            print(f"❌ Migration check failed: {e}")
            return False

    def create_facts_table(self):
        """Create facts table for perfect recall"""
        print("\n📊 Creating facts table...")

        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id SERIAL PRIMARY KEY,
                    fact_type VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    context TEXT,
                    session_id INTEGER,
                    episode_id INTEGER,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    embedding TEXT,
                    tags TEXT[],
                    importance FLOAT DEFAULT 0.5,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMPTZ,
                    metadata JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            print("✅ Facts table created")

            # Add comment
            self.cursor.execute("""
                COMMENT ON TABLE facts IS
                'Perfect recall storage for commands, code, files, decisions, and URLs';
            """)

            # Add column comments
            comments = {
                'fact_type': 'Type of fact: command, code, file, decision, url, error, config, tool_use',
                'content': 'Exact content of the fact (perfect fidelity)',
                'context': 'Surrounding context (2-3 exchanges)',
                'embedding': 'Hash-based or vector embedding for semantic search',
                'importance': 'Importance score (0.0-1.0) for ranking',
                'access_count': 'Number of times fact has been accessed (working set)',
                'metadata': 'Flexible JSONB for extensibility'
            }

            for column, comment in comments.items():
                self.cursor.execute(
                    sql.SQL("COMMENT ON COLUMN facts.{} IS %s").format(
                        sql.Identifier(column)
                    ),
                    (comment,)
                )

            return True

        except Exception as e:
            print(f"❌ Failed to create facts table: {e}")
            return False

    def create_indexes(self):
        """Create performance indexes"""
        print("\n🔍 Creating indexes...")

        indexes = [
            ("idx_facts_type", "CREATE INDEX IF NOT EXISTS idx_facts_type ON facts(fact_type)"),
            ("idx_facts_timestamp", "CREATE INDEX IF NOT EXISTS idx_facts_timestamp ON facts(timestamp DESC)"),
            ("idx_facts_session", "CREATE INDEX IF NOT EXISTS idx_facts_session ON facts(session_id)"),
            ("idx_facts_episode", "CREATE INDEX IF NOT EXISTS idx_facts_episode ON facts(episode_id)"),
            ("idx_facts_tags", "CREATE INDEX IF NOT EXISTS idx_facts_tags ON facts USING GIN(tags)"),
            ("idx_facts_importance", "CREATE INDEX IF NOT EXISTS idx_facts_importance ON facts(importance DESC)"),
            ("idx_facts_access", "CREATE INDEX IF NOT EXISTS idx_facts_access ON facts(access_count DESC)"),
            ("idx_facts_content", "CREATE INDEX IF NOT EXISTS idx_facts_content ON facts USING GIN(to_tsvector('english', content))"),
        ]

        for name, query in indexes:
            try:
                self.cursor.execute(query)
                print(f"  ✅ {name}")
            except Exception as e:
                print(f"  ⚠️  {name} failed: {e}")

        return True

    def add_compression_tracking(self):
        """Add compression tracking to episodes table"""
        print("\n🗜️ Adding compression tracking to episodes...")

        try:
            # Add compression_level column
            self.cursor.execute("""
                ALTER TABLE episodes
                ADD COLUMN IF NOT EXISTS compression_level INTEGER DEFAULT 0;
            """)
            print("  ✅ compression_level column")

            # Add facts_extracted column
            self.cursor.execute("""
                ALTER TABLE episodes
                ADD COLUMN IF NOT EXISTS facts_extracted BOOLEAN DEFAULT FALSE;
            """)
            print("  ✅ facts_extracted column")

            # Add compressed_content column
            self.cursor.execute("""
                ALTER TABLE episodes
                ADD COLUMN IF NOT EXISTS compressed_content TEXT;
            """)
            print("  ✅ compressed_content column")

            # Add compression_timestamp column
            self.cursor.execute("""
                ALTER TABLE episodes
                ADD COLUMN IF NOT EXISTS compression_timestamp TIMESTAMPTZ;
            """)
            print("  ✅ compression_timestamp column")

            # Create indexes for compression tracking
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_compression
                ON episodes(compression_level, created_at);
            """)
            print("  ✅ idx_episodes_compression")

            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_facts_extracted
                ON episodes(facts_extracted)
                WHERE facts_extracted = FALSE;
            """)
            print("  ✅ idx_episodes_facts_extracted (partial)")

            return True

        except Exception as e:
            print(f"❌ Failed to add compression tracking: {e}")
            return False

    def create_statistics_view(self):
        """Create helpful statistics view"""
        print("\n📊 Creating statistics view...")

        try:
            self.cursor.execute("""
                CREATE OR REPLACE VIEW facts_statistics AS
                SELECT
                    fact_type,
                    COUNT(*) as count,
                    AVG(importance) as avg_importance,
                    AVG(access_count) as avg_access,
                    MAX(timestamp) as latest_fact,
                    MIN(timestamp) as earliest_fact
                FROM facts
                GROUP BY fact_type
                ORDER BY count DESC;
            """)

            print("✅ facts_statistics view created")
            return True

        except Exception as e:
            print(f"⚠️  Statistics view creation failed: {e}")
            return False

    def get_statistics(self):
        """Get post-migration statistics"""
        print("\n📊 Post-Migration Statistics:")

        try:
            # Episodes stats
            self.cursor.execute("SELECT COUNT(*) FROM episodes")
            total_episodes = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT COUNT(*) FROM episodes
                WHERE facts_extracted = FALSE
            """)
            pending_extraction = self.cursor.fetchone()[0]

            print(f"\n  📚 Episodes:")
            print(f"     Total: {total_episodes:,}")
            print(f"     Pending extraction: {pending_extraction:,}")

            # Facts stats
            self.cursor.execute("SELECT COUNT(*) FROM facts")
            total_facts = self.cursor.fetchone()[0]

            if total_facts > 0:
                print(f"\n  🔍 Facts:")
                print(f"     Total: {total_facts:,}")

                # Get breakdown by type
                self.cursor.execute("""
                    SELECT fact_type, COUNT(*)
                    FROM facts
                    GROUP BY fact_type
                    ORDER BY COUNT(*) DESC
                    LIMIT 5
                """)

                print(f"\n  Top fact types:")
                for fact_type, count in self.cursor.fetchall():
                    print(f"     {fact_type}: {count:,}")

        except Exception as e:
            print(f"⚠️  Statistics error: {e}")

    def run_migration(self):
        """Run complete migration"""
        print("=" * 80)
        print("COCO DUAL-STREAM MEMORY MIGRATION")
        print("Phase 1: Facts Database + Compression Tracking")
        print("=" * 80)

        # Connect to database
        if not self.connect():
            return False

        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False

            # Check if already migrated
            if not self.check_existing_migration():
                print("\n⏹️  Migration aborted by user")
                return False

            # Create facts table
            if not self.create_facts_table():
                self.conn.rollback()
                return False

            # Create indexes
            if not self.create_indexes():
                self.conn.rollback()
                return False

            # Add compression tracking
            if not self.add_compression_tracking():
                self.conn.rollback()
                return False

            # Create statistics view
            self.create_statistics_view()

            # Commit all changes
            self.conn.commit()

            print("\n" + "=" * 80)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY")
            print("=" * 80)

            # Show statistics
            self.get_statistics()

            print("\n🚀 Next Steps:")
            print("   1. Run: python3 test_facts_migration.py")
            print("   2. Implement FactsMemory class")
            print("   3. Integrate with HierarchicalMemorySystem")

            return True

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            print("   Rolling back changes...")
            self.conn.rollback()
            return False

        finally:
            self.disconnect()


def main():
    """Main migration entry point"""

    # Get database URL
    db_url = os.getenv('POSTGRES_URL')

    if not db_url:
        print("❌ POSTGRES_URL environment variable not set")
        print("\n   Please set it in your .env file:")
        print("   POSTGRES_URL=postgresql://user:password@localhost/coco_memory")
        sys.exit(1)

    print(f"\n🔗 Database: {db_url.split('@')[1] if '@' in db_url else 'localhost'}")

    # Create migration instance
    migration = DualStreamMigration(db_url)

    # Run migration
    success = migration.run_migration()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

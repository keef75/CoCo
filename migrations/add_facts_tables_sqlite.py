#!/usr/bin/env python3
"""
Dual-Stream Memory Migration: Facts Database + Compression Tracking (SQLite)

This migration adds:
1. Facts table for perfect recall (commands, code, files, decisions)
2. Compression tracking columns to episodes table
3. Indexes for performance
4. Validation and rollback support

Author: COCO Development Team
Date: October 24, 2025
Status: Phase 1 - Foundation (SQLite Edition)
"""

import sqlite3
import sys
import os
from datetime import datetime
import json

class DualStreamMigrationSQLite:
    """Migration manager for dual-stream memory architecture (SQLite)"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print(f"✅ Connected to SQLite database: {os.path.basename(self.db_path)}")
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
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='episodes'
            """)

            episodes_exists = self.cursor.fetchone() is not None

            if not episodes_exists:
                print("❌ Episodes table not found. Please ensure COCO database is initialized.")
                return False

            print("✅ Episodes table exists")

            # Get episode count
            self.cursor.execute("SELECT COUNT(*) FROM episodes")
            episode_count = self.cursor.fetchone()[0]
            print(f"   Found {episode_count:,} existing episodes")

            return True

        except Exception as e:
            print(f"❌ Prerequisites check failed: {e}")
            return False

    def check_existing_migration(self) -> bool:
        """Check if migration already applied"""
        try:
            # Check if facts table exists
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='facts'
            """)

            facts_exists = self.cursor.fetchone() is not None

            if facts_exists:
                print("\n⚠️  Facts table already exists!")

                # Get facts count
                self.cursor.execute("SELECT COUNT(*) FROM facts")
                facts_count = self.cursor.fetchone()[0]
                print(f"   Found {facts_count:,} existing facts")

                response = input("\n   Continue with migration? This may add new columns. (y/n): ")
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    context TEXT,
                    session_id INTEGER,
                    episode_id INTEGER,
                    timestamp TEXT DEFAULT (datetime('now')),
                    embedding TEXT,
                    tags TEXT,
                    importance REAL DEFAULT 0.5,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            """)

            print("✅ Facts table created")
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
            ("idx_facts_importance", "CREATE INDEX IF NOT EXISTS idx_facts_importance ON facts(importance DESC)"),
            ("idx_facts_access", "CREATE INDEX IF NOT EXISTS idx_facts_access ON facts(access_count DESC)"),
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

        # SQLite doesn't support ALTER TABLE ADD COLUMN IF NOT EXISTS directly
        # We need to check each column individually

        columns_to_add = [
            ("compression_level", "INTEGER DEFAULT 0"),
            ("facts_extracted", "INTEGER DEFAULT 0"),  # SQLite uses 0/1 for boolean
            ("compressed_content", "TEXT"),
            ("compression_timestamp", "TEXT"),
        ]

        # Get existing columns
        self.cursor.execute("PRAGMA table_info(episodes)")
        existing_columns = {row[1] for row in self.cursor.fetchall()}

        for col_name, col_def in columns_to_add:
            if col_name not in existing_columns:
                try:
                    self.cursor.execute(f"ALTER TABLE episodes ADD COLUMN {col_name} {col_def}")
                    print(f"  ✅ {col_name} column added")
                except Exception as e:
                    print(f"  ⚠️  {col_name} failed: {e}")
            else:
                print(f"  ℹ️  {col_name} already exists")

        # Create indexes for compression tracking
        try:
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_compression
                ON episodes(compression_level, created_at)
            """)
            print("  ✅ idx_episodes_compression")
        except Exception as e:
            print(f"  ⚠️  idx_episodes_compression failed: {e}")

        try:
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_facts_extracted
                ON episodes(facts_extracted)
                WHERE facts_extracted = 0
            """)
            print("  ✅ idx_episodes_facts_extracted (partial)")
        except Exception as e:
            # Partial indexes might not be supported in all SQLite versions
            print(f"  ℹ️  idx_episodes_facts_extracted (partial index not supported)")
            # Create regular index instead
            try:
                self.cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_episodes_facts_extracted
                    ON episodes(facts_extracted)
                """)
                print("  ✅ idx_episodes_facts_extracted (regular)")
            except Exception as e2:
                print(f"  ⚠️  idx_episodes_facts_extracted failed: {e2}")

        return True

    def create_statistics_view(self):
        """Create helpful statistics view"""
        print("\n📊 Creating statistics view...")

        try:
            self.cursor.execute("""
                CREATE VIEW IF NOT EXISTS facts_statistics AS
                SELECT
                    fact_type,
                    COUNT(*) as count,
                    AVG(importance) as avg_importance,
                    AVG(access_count) as avg_access,
                    MAX(timestamp) as latest_fact,
                    MIN(timestamp) as earliest_fact
                FROM facts
                GROUP BY fact_type
                ORDER BY count DESC
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
                WHERE facts_extracted = 0
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
                for row in self.cursor.fetchall():
                    print(f"     {row[0]}: {row[1]:,}")

            # Database file size
            db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
            print(f"\n  💾 Database size: {db_size:.2f} MB")

        except Exception as e:
            print(f"⚠️  Statistics error: {e}")

    def run_migration(self):
        """Run complete migration"""
        print("=" * 80)
        print("COCO DUAL-STREAM MEMORY MIGRATION (SQLite)")
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

            # Begin transaction
            self.conn.execute("BEGIN TRANSACTION")

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
            print("   2. Implement FactsMemory class: memory/facts_memory.py")
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

    # Get database path from environment or use default
    db_path = os.getenv('COCO_MEMORY_DB', 'coco_memory.db')

    # Check if running from COCO directory
    if not os.path.exists('cocoa.py'):
        print("⚠️  Warning: cocoa.py not found in current directory")
        print("   Please run this script from the COCO root directory")

    # Use absolute path
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.getcwd(), db_path)

    print(f"\n🔗 Database: {db_path}")

    if not os.path.exists(db_path):
        print(f"\n❌ Database file not found: {db_path}")
        print("   Please ensure COCO has been run at least once to create the database")
        sys.exit(1)

    # Backup database before migration
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n💾 Creating backup: {os.path.basename(backup_path)}")

    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"   ✅ Backup created")
    except Exception as e:
        print(f"   ⚠️  Backup failed: {e}")
        response = input("   Continue without backup? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

    # Create migration instance
    migration = DualStreamMigrationSQLite(db_path)

    # Run migration
    success = migration.run_migration()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Database Migration Script: Add missing 'summarized' column to episodes table
Fixes: "no such column: summarized" error after long COCO sessions

This script safely adds the missing column to existing databases without data loss.
"""

import sqlite3
import os
from pathlib import Path

def migrate_database(db_path: str):
    """Add summarized column if missing"""

    print(f"🔍 Checking database: {db_path}")

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute("PRAGMA table_info(episodes)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'summarized' in columns:
            print("✅ Column 'summarized' already exists - no migration needed")

            # Show stats
            cursor.execute("SELECT COUNT(*) FROM episodes")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM episodes WHERE summarized = TRUE")
            summarized_count = cursor.fetchone()[0]

            print(f"📊 Episodes: {total} total, {summarized_count} summarized, {total - summarized_count} unsummarized")

            conn.close()
            return True

        print("⚠️  Column 'summarized' missing - starting migration...")

        # Add the summarized column
        cursor.execute("""
            ALTER TABLE episodes
            ADD COLUMN summarized BOOLEAN DEFAULT FALSE
        """)

        # Backfill existing rows
        cursor.execute("""
            UPDATE episodes
            SET summarized = FALSE
            WHERE summarized IS NULL
        """)

        # Check if in_buffer column exists before creating compound index
        cursor.execute("PRAGMA table_info(episodes)")
        columns_after = [row[1] for row in cursor.fetchall()]

        if 'in_buffer' in columns_after:
            # Create compound index if both columns exist
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_summarized
                ON episodes(summarized, in_buffer)
            """)
        else:
            # Create simple index if only summarized exists
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_summarized
                ON episodes(summarized)
            """)

        conn.commit()

        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM episodes")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM episodes WHERE summarized = FALSE")
        unsummarized = cursor.fetchone()[0]

        print(f"✅ Migration complete!")
        print(f"📊 Found {total} episodes (all marked as unsummarized)")
        print(f"🔍 Index created for faster summarization queries")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Run migration on COCO memory database"""

    print("=" * 60)
    print("COCO Memory Database Migration")
    print("Adding 'summarized' column to episodes table")
    print("=" * 60)
    print()

    # Default workspace location
    workspace = Path.home() / ".cocoa" / "coco_workspace"

    # Also check current directory
    if not workspace.exists():
        workspace = Path("coco_workspace")

    db_path = workspace / "coco_memory.db"

    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print("Please specify the correct path to coco_memory.db")
        return

    success = migrate_database(str(db_path))

    print()
    if success:
        print("=" * 60)
        print("✅ Migration successful!")
        print("You can now restart COCO - summarization will work properly.")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ Migration failed - check errors above")
        print("=" * 60)

if __name__ == "__main__":
    main()

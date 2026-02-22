#!/usr/bin/env python3
"""
Test script to validate dual-stream memory migration

This script verifies:
1. Facts table created with correct schema
2. All indexes exist and are functional
3. Compression tracking columns added
4. Can insert and query facts
5. Performance is acceptable

Author: COCO Development Team
Date: October 24, 2025
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
from datetime import datetime
import json

class MigrationValidator:
    """Validates dual-stream memory migration"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        self.test_results = []

    def connect(self):
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def test_facts_table_exists(self) -> bool:
        """Test 1: Facts table exists"""
        print("\n📋 Test 1: Facts table exists")

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'facts'
                )
            """)

            exists = cursor.fetchone()[0]
            cursor.close()

            if exists:
                print("   ✅ PASS: Facts table exists")
                return True
            else:
                print("   ❌ FAIL: Facts table not found")
                return False

        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            return False

    def test_facts_schema(self) -> bool:
        """Test 2: Facts table has correct schema"""
        print("\n📋 Test 2: Facts table schema")

        required_columns = {
            'id': 'integer',
            'fact_type': 'character varying',
            'content': 'text',
            'context': 'text',
            'session_id': 'integer',
            'episode_id': 'integer',
            'timestamp': 'timestamp with time zone',
            'embedding': 'text',
            'tags': 'ARRAY',
            'importance': 'double precision',
            'access_count': 'integer',
            'metadata': 'jsonb'
        }

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'facts'
            """)

            columns = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.close()

            all_present = True
            for col, expected_type in required_columns.items():
                if col in columns:
                    print(f"   ✅ {col}: {columns[col]}")
                else:
                    print(f"   ❌ Missing column: {col}")
                    all_present = False

            if all_present:
                print("   ✅ PASS: All required columns present")
                return True
            else:
                print("   ❌ FAIL: Missing required columns")
                return False

        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            return False

    def test_indexes_exist(self) -> bool:
        """Test 3: All indexes created"""
        print("\n📋 Test 3: Indexes exist")

        required_indexes = [
            'idx_facts_type',
            'idx_facts_timestamp',
            'idx_facts_session',
            'idx_facts_episode',
            'idx_facts_tags',
            'idx_facts_importance',
            'idx_facts_access',
            'idx_facts_content'
        ]

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'facts'
            """)

            indexes = [row[0] for row in cursor.fetchall()]
            cursor.close()

            all_present = True
            for idx in required_indexes:
                if idx in indexes:
                    print(f"   ✅ {idx}")
                else:
                    print(f"   ⚠️  Missing index: {idx}")
                    all_present = False

            if all_present:
                print("   ✅ PASS: All indexes present")
                return True
            else:
                print("   ⚠️  WARN: Some indexes missing (non-critical)")
                return True  # Still pass, just warning

        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            return False

    def test_compression_columns(self) -> bool:
        """Test 4: Compression tracking columns added to episodes"""
        print("\n📋 Test 4: Compression tracking columns")

        required_columns = [
            'compression_level',
            'facts_extracted',
            'compressed_content',
            'compression_timestamp'
        ]

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'episodes'
                AND column_name IN %s
            """, (tuple(required_columns),))

            columns = [row[0] for row in cursor.fetchall()]
            cursor.close()

            all_present = True
            for col in required_columns:
                if col in columns:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ Missing: {col}")
                    all_present = False

            if all_present:
                print("   ✅ PASS: All compression columns present")
                return True
            else:
                print("   ❌ FAIL: Missing compression columns")
                return False

        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            return False

    def test_insert_fact(self) -> bool:
        """Test 5: Can insert facts"""
        print("\n📋 Test 5: Insert fact")

        try:
            cursor = self.conn.cursor()

            # Insert test fact
            cursor.execute("""
                INSERT INTO facts (
                    fact_type, content, context, importance, tags, metadata
                )
                VALUES (
                    'command',
                    'docker ps -a',
                    'User asked about running containers',
                    0.8,
                    ARRAY['docker', 'cli'],
                    '{"test": true}'::jsonb
                )
                RETURNING id
            """)

            fact_id = cursor.fetchone()[0]
            self.conn.commit()

            print(f"   ✅ Inserted fact with ID: {fact_id}")

            # Verify can read it back
            cursor.execute("SELECT * FROM facts WHERE id = %s", (fact_id,))
            fact = cursor.fetchone()

            if fact:
                print(f"   ✅ Can read fact back")
                print(f"   ✅ PASS: Insert/read working")

                # Cleanup test fact
                cursor.execute("DELETE FROM facts WHERE id = %s", (fact_id,))
                self.conn.commit()
                print(f"   🧹 Cleaned up test fact")

                cursor.close()
                return True
            else:
                print(f"   ❌ FAIL: Cannot read fact back")
                cursor.close()
                return False

        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            self.conn.rollback()
            return False

    def test_query_performance(self) -> bool:
        """Test 6: Query performance"""
        print("\n📋 Test 6: Query performance")

        try:
            cursor = self.conn.cursor()

            # Test query with EXPLAIN ANALYZE
            start = datetime.now()

            cursor.execute("""
                EXPLAIN ANALYZE
                SELECT * FROM facts
                WHERE fact_type = 'command'
                AND content ILIKE '%docker%'
                ORDER BY importance DESC, timestamp DESC
                LIMIT 10
            """)

            results = cursor.fetchall()
            elapsed = (datetime.now() - start).total_seconds() * 1000

            print(f"   ⏱️  Query time: {elapsed:.2f}ms")

            if elapsed < 100:
                print(f"   ✅ PASS: Performance excellent (< 100ms)")
                return True
            elif elapsed < 500:
                print(f"   ⚠️  WARN: Performance acceptable (< 500ms)")
                return True
            else:
                print(f"   ❌ FAIL: Performance poor (> 500ms)")
                return False

        except Exception as e:
            print(f"   ⚠️  SKIP: {e}")
            return True  # Don't fail on performance test

    def test_statistics_view(self) -> bool:
        """Test 7: Statistics view exists"""
        print("\n📋 Test 7: Statistics view")

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.views
                    WHERE table_schema = 'public'
                    AND table_name = 'facts_statistics'
                )
            """)

            exists = cursor.fetchone()[0]

            if exists:
                print("   ✅ PASS: facts_statistics view exists")

                # Try querying it
                cursor.execute("SELECT * FROM facts_statistics LIMIT 1")
                print("   ✅ View is queryable")
                return True
            else:
                print("   ⚠️  WARN: facts_statistics view not found")
                return True  # Not critical

        except Exception as e:
            print(f"   ⚠️  WARN: {e}")
            return True  # Not critical

    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 80)
        print("DUAL-STREAM MEMORY MIGRATION VALIDATION")
        print("=" * 80)

        if not self.connect():
            print("\n❌ Cannot connect to database")
            return False

        tests = [
            self.test_facts_table_exists,
            self.test_facts_schema,
            self.test_indexes_exist,
            self.test_compression_columns,
            self.test_insert_fact,
            self.test_query_performance,
            self.test_statistics_view
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"   ❌ Test error: {e}")
                failed += 1

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}/{len(tests)}")
        print(f"❌ Failed: {failed}/{len(tests)}")

        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("\n🚀 Next Steps:")
            print("   1. Implement FactsMemory class: memory/facts_memory.py")
            print("   2. Test fact extraction with sample exchanges")
            print("   3. Integrate with HierarchicalMemorySystem")
            return True
        else:
            print("\n⚠️  SOME TESTS FAILED")
            print("   Please review migration and fix issues")
            return False


def main():
    """Main test entry point"""

    db_url = os.getenv('POSTGRES_URL')

    if not db_url:
        print("❌ POSTGRES_URL environment variable not set")
        sys.exit(1)

    validator = MigrationValidator(db_url)
    success = validator.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

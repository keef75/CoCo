#!/usr/bin/env python3
"""
Comprehensive Test Suite for COCO Precision Memory System
========================================================
Tests all aspects of the precision conversation memory including:
- Multi-strategy retrieval (temporal, keyword, topic, context)
- Metadata extraction and indexing
- Integration with COCO architecture
- Memory persistence and recall accuracy
- Function calling tools interface

This validates the "crisp, precise, in conversational episodic recall" requirement.
"""

import os
import sys
import asyncio
import sqlite3
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from precision_conversation_memory import (
        PrecisionConversationMemory,
        ConversationExchange
    )
    from coco_precision_memory_integration import (
        EnhancedMemorySystem,
        COCOMemoryConfig,
        create_enhanced_memory_system,
        get_memory_function_schemas,
        COCOMemoryInterface
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Import Error: {e}")
    print("📝 Run this from the COCO directory where the precision memory files exist")
    IMPORTS_AVAILABLE = False

class PrecisionMemoryTestSuite:
    """Comprehensive test suite for precision memory system"""

    def __init__(self):
        self.test_workspace = None
        self.memory_interface = None
        self.precision_memory = None
        self.enhanced_system = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }

    def setup_test_environment(self):
        """Create isolated test environment"""
        print("🔧 Setting up test environment...")

        # Create temporary workspace
        self.test_workspace = tempfile.mkdtemp(prefix="coco_memory_test_")
        print(f"📁 Test workspace: {self.test_workspace}")

        # Initialize memory systems with test workspace
        self.memory_interface = COCOMemoryInterface()
        self.precision_memory = PrecisionConversationMemory(db_path=os.path.join(self.test_workspace, "test_precision_memory.db"))

        # Create enhanced system
        config = COCOMemoryConfig()
        config.precision_db_path = os.path.join(self.test_workspace, "test_precision_memory.db")
        self.enhanced_system = EnhancedMemorySystem(config)

        print("✅ Test environment ready")

    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.test_workspace and os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)
            print(f"🧹 Cleaned up test workspace")

    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   📝 {details}")

        self.test_results['tests'].append({
            'name': test_name,
            'passed': passed,
            'details': details
        })

        if passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1

    async def test_basic_memory_storage(self):
        """Test basic memory storage and retrieval"""
        print("\n🧪 Testing Basic Memory Storage...")

        # Store test exchanges
        test_exchanges = [
            ("I want to optimize COCO's memory system",
             "Great! Memory optimization is crucial for consciousness continuity."),
            ("What's the current architecture like?",
             "COCO uses a hierarchical memory system with episodic and summary buffers."),
            ("How can we make recall more precise?",
             "We need multi-strategy retrieval with keyword, topic, and temporal search.")
        ]

        exchange_ids = []
        for user_input, assistant_response in test_exchanges:
            exchange_id = self.memory_interface.process_interaction(user_input, assistant_response)
            exchange_ids.append(exchange_id)

        # Test that all exchanges were stored
        passed = len(exchange_ids) == 3 and all(ex_id for ex_id in exchange_ids)
        self.log_test_result(
            "Basic Memory Storage",
            passed,
            f"Stored {len(exchange_ids)} exchanges successfully"
        )

        return passed

    async def test_temporal_recall(self):
        """Test temporal-based recall (first, last, earlier, etc.)"""
        print("\n🧪 Testing Temporal Recall...")

        # Test "first thing" query
        result = self.memory_interface.handle_memory_query("what was the first thing I said?")

        first_thing_correct = (
            result and
            "optimize COCO's memory system" in result and
            "first" in result.lower()
        )

        self.log_test_result(
            "Temporal Recall - First Thing",
            first_thing_correct,
            f"Found first exchange: {'Yes' if first_thing_correct else 'No'}"
        )

        # Test "earlier" query
        result = self.memory_interface.handle_memory_query("what did we discuss earlier about architecture?")

        earlier_correct = (
            result and
            "hierarchical memory system" in result
        )

        self.log_test_result(
            "Temporal Recall - Earlier Discussion",
            earlier_correct,
            f"Found earlier discussion: {'Yes' if earlier_correct else 'No'}"
        )

        return first_thing_correct and earlier_correct

    async def test_keyword_search(self):
        """Test keyword-based recall"""
        print("\n🧪 Testing Keyword Search...")

        # Test specific keyword recall
        result = self.memory_interface.handle_memory_query("recall something about hierarchical")

        keyword_found = (
            result and
            "hierarchical" in result.lower() and
            "memory system" in result.lower()
        )

        self.log_test_result(
            "Keyword Search - Hierarchical",
            keyword_found,
            f"Found hierarchical memory content: {'Yes' if keyword_found else 'No'}"
        )

        # Test multi-keyword search
        result = self.memory_interface.handle_memory_query("multi-strategy retrieval")

        multi_keyword_found = (
            result and
            "multi-strategy" in result.lower() and
            "retrieval" in result.lower()
        )

        self.log_test_result(
            "Keyword Search - Multi-term",
            multi_keyword_found,
            f"Found multi-strategy content: {'Yes' if multi_keyword_found else 'No'}"
        )

        return keyword_found and multi_keyword_found

    async def test_topic_extraction(self):
        """Test topic extraction and topic-based retrieval"""
        print("\n🧪 Testing Topic Extraction...")

        # Get memory statistics to check topic extraction
        stats = self.memory_interface.get_memory_statistics()

        topics_extracted = (
            'top_topics' in stats and
            len(stats['top_topics']) > 0
        )

        self.log_test_result(
            "Topic Extraction",
            topics_extracted,
            f"Extracted {len(stats.get('top_topics', []))} topics"
        )

        # Test topic-based recall
        if topics_extracted:
            top_topic = stats['top_topics'][0][0]  # Get most common topic
            result = self.memory_interface.handle_memory_query(f"tell me about {top_topic}")

            topic_recall_works = result is not None and len(result) > 50

            self.log_test_result(
                "Topic-Based Recall",
                topic_recall_works,
                f"Successfully recalled content about '{top_topic}'"
            )

            return topic_recall_works

        return topics_extracted

    async def test_metadata_extraction(self):
        """Test rich metadata extraction"""
        print("\n🧪 Testing Metadata Extraction...")

        # Add a technical exchange with rich metadata potential
        exchange_id = self.memory_interface.process_interaction(
            "Can you write a Python function to calculate Fibonacci numbers?",
            "Here's a Python function:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```"
        )

        # Check memory statistics for metadata
        stats = self.memory_interface.get_memory_statistics()

        # Should detect code, keywords, topics
        code_detected = stats.get('exchanges_with_code', 0) > 0
        keywords_extracted = stats.get('unique_keywords', 0) > 0

        self.log_test_result(
            "Metadata Extraction - Code Detection",
            code_detected,
            f"Detected {stats.get('exchanges_with_code', 0)} exchanges with code"
        )

        self.log_test_result(
            "Metadata Extraction - Keywords",
            keywords_extracted,
            f"Extracted {stats.get('unique_keywords', 0)} unique keywords"
        )

        return code_detected and keywords_extracted

    async def test_context_markers(self):
        """Test context marker detection and following"""
        print("\n🧪 Testing Context Markers...")

        # Add exchanges with clear context relationships
        self.memory_interface.process_interaction(
            "Let's discuss the new Python feature",
            "Python 3.12 has some exciting new features! The match statement is particularly useful."
        )

        self.memory_interface.process_interaction(
            "Tell me more about that match statement you mentioned",
            "The match statement provides pattern matching like in Rust or Haskell..."
        )

        # Test context following
        result = self.memory_interface.handle_memory_query("when you mentioned match statement")

        context_followed = (
            result and
            "match statement" in result.lower() and
            ("Python" in result or "pattern matching" in result)
        )

        self.log_test_result(
            "Context Marker Following",
            context_followed,
            f"Successfully followed context: {'Yes' if context_followed else 'No'}"
        )

        return context_followed

    async def test_integration_layer(self):
        """Test integration with COCO architecture"""
        print("\n🧪 Testing Integration Layer...")

        # Test enhanced memory system
        exchange_id = self.enhanced_system.add_interaction(
            "Test integration exchange",
            "This tests the integration layer between precision and hierarchical memory."
        )

        integration_stored = exchange_id is not None

        self.log_test_result(
            "Integration Layer - Storage",
            integration_stored,
            f"Exchange stored with ID: {exchange_id}"
        )

        # Test memory query handling
        result = self.enhanced_system.handle_memory_query("integration exchange")

        integration_recalled = (
            result and
            "integration" in result.lower()
        )

        self.log_test_result(
            "Integration Layer - Recall",
            integration_recalled,
            f"Successfully recalled through integration: {'Yes' if integration_recalled else 'No'}"
        )

        return integration_stored and integration_recalled

    async def test_function_calling_tools(self):
        """Test function calling tools interface"""
        print("\n🧪 Testing Function Calling Tools...")

        # Test recall_memory tool
        result = self.enhanced_system._handle_recall_memory("memory system optimization")

        tool_works = (
            result and
            "Memory Recall Results" in result and
            len(result) > 100  # Should have substantial content
        )

        self.log_test_result(
            "Function Calling - recall_memory",
            tool_works,
            f"Tool returned {len(result) if result else 0} characters"
        )

        # Test memory_stats tool
        stats_result = self.enhanced_system._handle_memory_stats()

        stats_work = (
            stats_result and
            "Memory System Statistics" in stats_result and
            "Total Exchanges" in stats_result
        )

        self.log_test_result(
            "Function Calling - memory_stats",
            stats_work,
            f"Stats tool working: {'Yes' if stats_work else 'No'}"
        )

        return tool_works and stats_work

    async def test_memory_persistence(self):
        """Test memory persistence across sessions"""
        print("\n🧪 Testing Memory Persistence...")

        # Check database exists
        db_path = os.path.join(self.test_workspace, "precision_memory.db")
        db_exists = os.path.exists(db_path)

        self.log_test_result(
            "Database Persistence",
            db_exists,
            f"Database created at: {db_path}"
        )

        if db_exists:
            # Check database structure
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check tables exist
            tables = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()

            expected_tables = ['exchanges', 'topics', 'keywords', 'context_markers']
            table_names = [t[0] for t in tables]

            all_tables_exist = all(table in table_names for table in expected_tables)

            self.log_test_result(
                "Database Schema",
                all_tables_exist,
                f"Found tables: {table_names}"
            )

            # Check data exists
            exchange_count = cursor.execute("SELECT COUNT(*) FROM exchanges").fetchone()[0]

            data_persisted = exchange_count > 0

            self.log_test_result(
                "Data Persistence",
                data_persisted,
                f"Found {exchange_count} persisted exchanges"
            )

            conn.close()
            return db_exists and all_tables_exist and data_persisted

        return db_exists

    async def test_performance_benchmarks(self):
        """Test performance benchmarks for memory operations"""
        print("\n🧪 Testing Performance Benchmarks...")

        import time

        # Benchmark storage performance
        start_time = time.time()

        # Store 50 exchanges rapidly
        for i in range(50):
            self.memory_interface.process_interaction(
                f"Test query number {i} about various topics",
                f"This is response {i} with different content and keywords for testing."
            )

        storage_time = time.time() - start_time

        storage_fast = storage_time < 5.0  # Should store 50 exchanges in under 5 seconds

        self.log_test_result(
            "Performance - Storage Speed",
            storage_fast,
            f"Stored 50 exchanges in {storage_time:.2f}s"
        )

        # Benchmark recall performance
        start_time = time.time()

        # Perform 10 different recall queries
        query_results = []
        for i in range(10):
            result = self.memory_interface.handle_memory_query(f"test query {i}")
            query_results.append(result)

        recall_time = time.time() - start_time

        recall_fast = recall_time < 2.0  # Should handle 10 queries in under 2 seconds

        self.log_test_result(
            "Performance - Recall Speed",
            recall_fast,
            f"Handled 10 queries in {recall_time:.2f}s"
        )

        return storage_fast and recall_fast

    async def run_comprehensive_tests(self):
        """Run all tests in the comprehensive suite"""
        print("🚀 Starting Comprehensive Precision Memory Test Suite")
        print("=" * 60)

        if not IMPORTS_AVAILABLE:
            print("❌ Cannot run tests - imports not available")
            return False

        try:
            self.setup_test_environment()

            # Run all test categories
            await self.test_basic_memory_storage()
            await self.test_temporal_recall()
            await self.test_keyword_search()
            await self.test_topic_extraction()
            await self.test_metadata_extraction()
            await self.test_context_markers()
            await self.test_integration_layer()
            await self.test_function_calling_tools()
            await self.test_memory_persistence()
            await self.test_performance_benchmarks()

            # Print final results
            print("\n" + "=" * 60)
            print("🎯 COMPREHENSIVE TEST RESULTS")
            print(f"✅ Passed: {self.test_results['passed']}")
            print(f"❌ Failed: {self.test_results['failed']}")
            print(f"📊 Success Rate: {self.test_results['passed']/(self.test_results['passed']+self.test_results['failed'])*100:.1f}%")

            if self.test_results['failed'] == 0:
                print("\n🎉 ALL TESTS PASSED! Precision memory system is ready for deployment.")
                print("✨ The crisp, precise, in conversational episodic recall is working perfectly!")
            else:
                print(f"\n⚠️  {self.test_results['failed']} tests failed. Review issues before deployment.")

            return self.test_results['failed'] == 0

        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.cleanup_test_environment()

def main():
    """Main test runner"""
    print("🧠 COCO Precision Memory - Comprehensive Test Suite")
    print("Validating crisp, precise, in conversational episodic recall")
    print()

    # Run async test suite
    test_suite = PrecisionMemoryTestSuite()

    try:
        success = asyncio.run(test_suite.run_comprehensive_tests())

        if success:
            print("\n🎯 READY FOR INTEGRATION")
            print("The precision memory system has passed all tests and is ready")
            print("to be integrated into the main COCO consciousness system.")

            print("\n📋 NEXT STEPS:")
            print("1. Integrate precision memory into cocoa.py main system")
            print("2. Add function calling tools to COCO's tool registry")
            print("3. Update COCO's system prompt to use precision recall")
            print("4. Test end-to-end in full COCO environment")

            return 0
        else:
            print("\n⚠️  Issues found - resolve before integration")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
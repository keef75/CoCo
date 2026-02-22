#!/usr/bin/env python3
"""
Integration test for dual-stream memory system
Tests automatic facts extraction and user commands (Personal Assistant Focus)

Author: COCO Development Team
Date: October 24, 2025
Status: Phase 1 Integration Testing - Personal Assistant Pivot
"""

import sys
import os
from datetime import datetime

# Add to path
sys.path.insert(0, os.path.dirname(__file__))

from cocoa import Config, HierarchicalMemorySystem


def test_automatic_extraction():
    """Test automatic facts extraction on exchange (Personal Assistant)"""
    print("\n📋 Test 1: Automatic Facts Extraction (Personal Assistant)")

    config = Config()
    memory = HierarchicalMemorySystem(config)

    # Test Case 1: Appointment extraction
    print("   Testing appointment extraction...")
    user_text = "I have a meeting with Sarah at Starbucks tomorrow at 2pm"
    agent_text = "I've noted your meeting with Sarah at Starbucks tomorrow at 2pm."

    initial_count = getattr(memory, 'facts_extracted_count', 0)
    episode_id = memory.insert_episode(user_text, agent_text)

    if hasattr(memory, 'facts_extracted_count'):
        extracted = memory.facts_extracted_count - initial_count
        if extracted > 0:
            print(f"   ✅ Extracted {extracted} facts from appointment")
        else:
            print("   ❌ No facts extracted from appointment")
            return False
    else:
        print("   ❌ facts_extracted_count attribute missing")
        return False

    # Test Case 2: Contact extraction
    print("   Testing contact extraction...")
    user_text2 = "I need to call John Miller about the project deadline"
    agent_text2 = "I've noted that you need to contact John Miller about the project deadline."

    initial_count = memory.facts_extracted_count
    episode_id2 = memory.insert_episode(user_text2, agent_text2)

    extracted2 = memory.facts_extracted_count - initial_count
    if extracted2 > 0:
        print(f"   ✅ Extracted {extracted2} facts from contact")
    else:
        print("   ⚠️  No facts extracted from contact")

    # Test Case 3: Task extraction
    print("   Testing task extraction...")
    user_text3 = "I need to review the proposal and send feedback by Friday"
    agent_text3 = "I've noted your task to review the proposal and send feedback by Friday."

    initial_count = memory.facts_extracted_count
    episode_id3 = memory.insert_episode(user_text3, agent_text3)

    extracted3 = memory.facts_extracted_count - initial_count
    if extracted3 > 0:
        print(f"   ✅ Extracted {extracted3} facts from task")
    else:
        print("   ⚠️  No facts extracted from task")

    # Test Case 4: Preference extraction
    print("   Testing preference extraction...")
    user_text4 = "I prefer oat milk in my coffee"
    agent_text4 = "Got it! I'll remember you prefer oat milk in your coffee."

    initial_count = memory.facts_extracted_count
    episode_id4 = memory.insert_episode(user_text4, agent_text4)

    extracted4 = memory.facts_extracted_count - initial_count
    if extracted4 > 0:
        print(f"   ✅ Extracted {extracted4} facts from preference")
    else:
        print("   ⚠️  No facts extracted from preference")

    # Overall result
    total_extracted = memory.facts_extracted_count
    if total_extracted > 0:
        print(f"\n   ✅ Total facts extracted: {total_extracted}")
        return True
    else:
        print("\n   ❌ No facts extracted overall")
        return False


def test_recall_command():
    """Test /recall command via memory system (Personal Assistant)"""
    print("\n📋 Test 2: /recall Command (Personal Assistant)")

    config = Config()
    memory = HierarchicalMemorySystem(config)

    # First, insert some test data
    print("   Setting up test data...")
    user_text = "I have a meeting with Sarah at Starbucks tomorrow"
    agent_text = "I've noted your meeting with Sarah at Starbucks tomorrow."
    memory.insert_episode(user_text, agent_text)

    # Test recall via QueryRouter
    if not hasattr(memory, 'query_router') or memory.query_router is None:
        print("   ⚠️  QueryRouter not initialized")
        # Try to initialize it manually
        try:
            from memory.query_router import QueryRouter
            if memory.facts_memory and memory.simple_rag:
                memory.query_router = QueryRouter(memory.facts_memory, memory.simple_rag)
                print("   ✅ QueryRouter initialized manually")
            else:
                print("   ❌ Cannot initialize QueryRouter (missing facts_memory or simple_rag)")
                return False
        except Exception as e:
            print(f"   ❌ QueryRouter initialization failed: {e}")
            return False

    # Test recall
    print("   Testing recall query 'meeting with Sarah'...")
    try:
        result = memory.query_router.route_query("meeting with Sarah", limit=5)

        if result['count'] > 0:
            print(f"   ✅ Found {result['count']} results")
            print(f"   ✅ Source: {result['source']}")
            if result['source'] == 'facts':
                print(f"   ✅ Fact type: {result.get('fact_type', 'N/A')}")
            return True
        else:
            print("   ❌ No results found")
            return False

    except Exception as e:
        print(f"   ❌ Recall query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_facts_command():
    """Test /facts command via facts_memory (Personal Assistant)"""
    print("\n📋 Test 3: /facts Command (Personal Assistant)")

    config = Config()
    memory = HierarchicalMemorySystem(config)

    if not hasattr(memory, 'facts_memory') or memory.facts_memory is None:
        print("   ❌ FactsMemory not initialized")
        return False

    # Insert test data with multiple personal assistant fact types
    print("   Setting up diverse test data...")
    test_exchanges = [
        ("I have a meeting with Sarah tomorrow", "Noted your meeting with Sarah.", "appointment"),
        ("I need to call John Miller", "I'll remind you to contact John Miller.", "contact"),
        ("I prefer oat milk in my coffee", "Got it, you prefer oat milk.", "preference"),
        ("I need to review the proposal by Friday", "Task noted: review proposal by Friday.", "task"),
        ("Note: Don't forget to send the invoice", "Important note recorded.", "note"),
    ]

    for user, agent, expected_type in test_exchanges:
        memory.insert_episode(user, agent)

    # Test facts search
    print("   Testing facts search...")
    try:
        stats = memory.facts_memory.get_stats()

        if stats['total_facts'] > 0:
            print(f"   ✅ Total facts in database: {stats['total_facts']}")
            print(f"   ✅ Fact types present: {len(stats['breakdown'])}")

            # Show breakdown
            if stats['breakdown']:
                print("   ✅ Breakdown:")
                for fact_type, count in list(stats['breakdown'].items())[:5]:
                    print(f"      {fact_type}: {count}")

            return True
        else:
            print("   ⚠️  No facts in database yet")
            return False

    except Exception as e:
        print(f"   ❌ Facts command failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_facts_stats():
    """Test /facts-stats command (Personal Assistant)"""
    print("\n📋 Test 4: /facts-stats Command (Personal Assistant)")

    config = Config()
    memory = HierarchicalMemorySystem(config)

    if not hasattr(memory, 'facts_memory') or memory.facts_memory is None:
        print("   ❌ FactsMemory not initialized")
        return False

    # Get statistics
    print("   Retrieving facts statistics...")
    try:
        stats = memory.facts_memory.get_stats()

        print(f"   ✅ Total facts: {stats['total_facts']}")
        print(f"   ✅ Average importance: {stats['avg_importance']:.2f}")

        if stats['breakdown']:
            print(f"   ✅ Fact types: {len(stats['breakdown'])}")

        if stats['most_accessed']:
            print(f"   ✅ Most accessed facts tracked: {len(stats['most_accessed'])}")

        if stats['latest_timestamp']:
            print(f"   ✅ Latest fact: {stats['latest_timestamp']}")

        return True

    except Exception as e:
        print(f"   ❌ Stats command failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run complete integration test suite (Personal Assistant Focus)"""
    print("=" * 80)
    print("DUAL-STREAM MEMORY INTEGRATION TESTS")
    print("Phase 1: Personal Assistant Pivot Validation")
    print("=" * 80)

    tests = [
        test_automatic_extraction,
        test_recall_command,
        test_facts_command,
        test_facts_stats
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
            import traceback
            traceback.print_exc()
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
        print("   1. Test with real COCO usage: python3 cocoa.py")
        print("   2. Try /recall command with personal assistant queries:")
        print("      • /recall meeting with Sarah")
        print("      • /recall John's contact information")
        print("      • /recall task about proposal")
        print("   3. Monitor facts database growth with /facts-stats")
        print("   4. Verify personal assistant fact types have high importance scores")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("   Review error messages above")
        print("   Check database initialization and permissions")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

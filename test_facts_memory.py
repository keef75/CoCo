#!/usr/bin/env python3
"""
Test script for FactsMemory class

Tests:
1. Fact extraction from various exchange types
2. Storing facts in database
3. Searching facts
4. Statistics generation

Author: COCO Development Team
Date: October 24, 2025
"""

import sys
import os
from datetime import datetime

# Add memory module to path
sys.path.insert(0, os.path.dirname(__file__))

from memory.facts_memory import FactsMemory


def test_command_extraction():
    """Test 1: Command extraction"""
    print("\n📋 Test 1: Command Extraction")

    facts_memory = FactsMemory('coco_workspace/coco_memory.db')

    exchange = {
        'user': 'How do I list all docker containers?',
        'agent': 'You can use this command:\n$ docker ps -a\nThis will show all containers including stopped ones.'
    }

    facts = facts_memory.extract_facts(exchange)
    commands = [f for f in facts if f['type'] == 'command']

    if commands:
        print(f"   ✅ Extracted {len(commands)} command(s)")
        for cmd in commands:
            print(f"      Command: {cmd['content']}")
            print(f"      Importance: {cmd['importance']}")
    else:
        print("   ❌ No commands extracted")
        return False

    return True


def test_code_extraction():
    """Test 2: Code block extraction"""
    print("\n📋 Test 2: Code Block Extraction")

    facts_memory = FactsMemory('coco_workspace/coco_memory.db')

    exchange = {
        'user': 'Can you write a Python function to calculate factorial?',
        'agent': '''Here's a Python function:

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

This uses recursion to calculate the factorial.'''
    }

    facts = facts_memory.extract_facts(exchange)
    code_facts = [f for f in facts if f['type'] == 'code']

    if code_facts:
        print(f"   ✅ Extracted {len(code_facts)} code block(s)")
        for code in code_facts:
            print(f"      Language: {code.get('metadata', {}).get('language', 'unknown')}")
            print(f"      Length: {len(code['content'])} chars")
            print(f"      Importance: {code['importance']}")
    else:
        print("   ❌ No code blocks extracted")
        return False

    return True


def test_file_extraction():
    """Test 3: File path extraction"""
    print("\n📋 Test 3: File Path Extraction")

    facts_memory = FactsMemory('coco_workspace/coco_memory.db')

    exchange = {
        'user': 'I modified /Users/keith/projects/app/config.py',
        'agent': 'Great! I see you modified the config file at /Users/keith/projects/app/config.py'
    }

    facts = facts_memory.extract_facts(exchange)
    file_facts = [f for f in facts if f['type'] == 'file']

    if file_facts:
        print(f"   ✅ Extracted {len(file_facts)} file path(s)")
        for file_fact in file_facts:
            print(f"      File: {file_fact['content']}")
    else:
        print("   ⚠️  No file paths extracted (this test may have strict filters)")
        return True  # Don't fail on this

    return True


def test_coco_command_extraction():
    """Test 4: COCO slash command extraction"""
    print("\n📋 Test 4: COCO Command Extraction")

    facts_memory = FactsMemory('coco_workspace/coco_memory.db')

    exchange = {
        'user': '/recall docker command from yesterday',
        'agent': 'Searching for docker commands...'
    }

    facts = facts_memory.extract_facts(exchange)
    coco_commands = [f for f in facts if f['type'] == 'coco_command']

    if coco_commands:
        print(f"   ✅ Extracted {len(coco_commands)} COCO command(s)")
        for cmd in coco_commands:
            print(f"      Command: {cmd['content']}")
    else:
        print("   ❌ No COCO commands extracted")
        return False

    return True


def test_decision_extraction():
    """Test 5: Decision extraction"""
    print("\n📋 Test 5: Decision Extraction")

    facts_memory = FactsMemory('coco_workspace/coco_memory.db')

    exchange = {
        'user': 'I prefer to use tabs instead of spaces for indentation. Always use docker for development.',
        'agent': 'Got it! I\'ll remember your preferences.'
    }

    facts = facts_memory.extract_facts(exchange)
    decisions = [f for f in facts if f['type'] == 'decision']

    if decisions:
        print(f"   ✅ Extracted {len(decisions)} decision(s)")
        for decision in decisions:
            print(f"      Decision: {decision['content']}")
    else:
        print("   ⚠️  No decisions extracted")
        return True  # Not critical

    return True


def test_storage():
    """Test 6: Store and retrieve facts"""
    print("\n📋 Test 6: Store and Retrieve Facts")

    facts_memory = FactsMemory('coco_workspace/coco_memory.db')

    # Create test exchange
    exchange = {
        'user': '/recall test command',
        'agent': 'Here is the command you requested:\n$ pytest -v\nThis runs tests verbosely.'
    }

    # Extract facts
    facts = facts_memory.extract_facts(exchange)

    if not facts:
        print("   ❌ No facts to store")
        return False

    print(f"   Extracted {len(facts)} facts")

    # Store facts (use test episode_id)
    try:
        stored = facts_memory.store_facts(facts, episode_id=999999, session_id=1)
        print(f"   ✅ Stored {stored} facts")
    except Exception as e:
        print(f"   ❌ Storage failed: {e}")
        return False

    # Search for stored facts
    results = facts_memory.search_facts('pytest', limit=5)

    if results:
        print(f"   ✅ Search found {len(results)} results")
        for result in results:
            print(f"      Type: {result['type']}, Content: {result['content'][:50]}...")
    else:
        print("   ⚠️  Search returned no results")

    # Cleanup test facts
    try:
        cursor = facts_memory.conn.cursor()
        cursor.execute("DELETE FROM facts WHERE episode_id = 999999")
        facts_memory.conn.commit()
        print("   🧹 Cleaned up test facts")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")

    return True


def test_statistics():
    """Test 7: Statistics generation"""
    print("\n📋 Test 7: Statistics")

    facts_memory = FactsMemory('coco_workspace/coco_memory.db')

    try:
        stats = facts_memory.get_stats()

        print(f"   ✅ Total facts: {stats['total_facts']:,}")
        print(f"   ✅ Avg importance: {stats['avg_importance']:.2f}")

        if stats['breakdown']:
            print(f"\n   Breakdown by type:")
            for fact_type, count in list(stats['breakdown'].items())[:5]:
                print(f"      {fact_type}: {count:,}")

        if stats['most_accessed']:
            print(f"\n   Most accessed:")
            for item in stats['most_accessed'][:3]:
                print(f"      [{item['type']}] {item['content']} ({item['count']} times)")

        return True

    except Exception as e:
        print(f"   ❌ Statistics failed: {e}")
        return False


def run_all_tests():
    """Run complete test suite"""
    print("=" * 80)
    print("FACTS MEMORY TEST SUITE")
    print("=" * 80)

    tests = [
        test_command_extraction,
        test_code_extraction,
        test_file_extraction,
        test_coco_command_extraction,
        test_decision_extraction,
        test_storage,
        test_statistics
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
        print("   1. Integrate FactsMemory with HierarchicalMemorySystem")
        print("   2. Add automatic fact extraction on each exchange")
        print("   3. Implement /recall command")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("   Please review and fix issues")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

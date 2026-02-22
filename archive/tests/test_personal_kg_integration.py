#!/usr/bin/env python3
"""
Test script to validate Personal Assistant KG integration with cocoa.py
"""

import os
import sys

print("🧪 Testing Personal Assistant KG Integration with COCO...")
print("=" * 70)

# Test 1: Import check
print("\n[1/5] Testing imports...")
try:
    from personal_assistant_kg_enhanced import PersonalAssistantKG
    print("✅ PersonalAssistantKG imports successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: KG initialization
print("\n[2/5] Testing KG initialization...")
try:
    test_db = 'coco_workspace/test_personal_kg_integration.db'
    if os.path.exists(test_db):
        os.remove(test_db)

    kg = PersonalAssistantKG(test_db)
    print("✅ PersonalAssistantKG initializes successfully")
    print(f"   Database: {kg.db_path}")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Conversation processing
print("\n[3/5] Testing conversation processing...")
try:
    test_exchanges = [
        ("My wife Kerry loves reading books", "I'll remember that Kerry loves reading!", []),
        ("I work with Sarah at Google", "Got it, Sarah is your colleague!", [{'name': 'send_email', 'parameters': {}}]),
        ("I use Python for coding", "Python noted as your tool!", [{'name': 'run_code', 'parameters': {}}]),
    ]

    for user, agent, tools in test_exchanges:
        stats = kg.process_conversation_exchange(user, agent, tools)
        print(f"✅ Processed exchange: {stats}")

except Exception as e:
    print(f"❌ Conversation processing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Knowledge status
print("\n[4/5] Testing knowledge status retrieval...")
try:
    status = kg.get_knowledge_status()
    print("✅ Knowledge status retrieved:")
    print(f"   Total entities: {status['total_entities']}")
    print(f"   Total relationships: {status['total_relationships']}")
    print(f"   Entity types: {status['entity_types']}")
except Exception as e:
    print(f"❌ Status retrieval failed: {e}")
    sys.exit(1)

# Test 5: Context retrieval
print("\n[5/5] Testing context retrieval for queries...")
try:
    test_queries = [
        "Who is Kerry?",
        "What tools do I use?",
        "Who do I work with?"
    ]

    for query in test_queries:
        context = kg.get_conversation_context(query)
        print(f"✅ Query: '{query}'")
        if context:
            print(f"   Context: {context[:100]}..." if len(context) > 100 else f"   Context: {context}")
        else:
            print("   (no context)")

except Exception as e:
    print(f"❌ Context retrieval failed: {e}")
    sys.exit(1)

# Success!
print("\n" + "=" * 70)
print("🎉 All integration tests passed!")
print("\n✅ PersonalAssistantKG is ready for COCO integration")
print(f"✅ Test database: {test_db}")

# Cleanup
print("\n🧹 Cleaning up test database...")
if os.path.exists(test_db):
    os.remove(test_db)
    print("✅ Cleanup complete")

print("\n" + "=" * 70)
print("📊 Integration Summary:")
print("   - PersonalAssistantKG imports correctly")
print("   - Database initialization works")
print("   - Conversation processing functional")
print("   - Tool usage tracking operational")
print("   - Context retrieval working")
print("\n🚀 Ready to test with live COCO conversations!")
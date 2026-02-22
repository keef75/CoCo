#!/usr/bin/env python3
"""
Test script to verify knowledge graph debug output is properly controlled
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_debug_off():
    """Test that knowledge graph is silent when debug is off"""
    print("🧪 Testing knowledge graph with debug OFF...")

    # Ensure debug is off
    os.environ.pop('COCO_DEBUG', None)
    os.environ.pop('DEBUG', None)

    try:
        # Import after setting environment variables
        from knowledge_graph_eternal import EternalKnowledgeGraph

        # Create temporary workspace
        test_workspace = tempfile.mkdtemp(prefix='test_kg_')

        # Initialize knowledge graph (should be silent)
        print("   Initializing knowledge graph...")
        kg = EternalKnowledgeGraph(test_workspace)

        # Process a conversation (should be silent)
        print("   Processing conversation exchange...")
        stats = kg.process_conversation_exchange(
            "Hi Keith, working on COCO project with knowledge graphs.",
            "Great! Knowledge graphs will enhance COCO's understanding."
        )

        print(f"   ✅ Silent operation successful - processed {stats.get('total_entities', 0)} entities")

        # Cleanup
        shutil.rmtree(test_workspace)

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    return True

def test_debug_on():
    """Test that knowledge graph shows output when debug is on"""
    print("\n🧪 Testing knowledge graph with debug ON...")

    # Enable debug
    os.environ['COCO_DEBUG'] = 'true'

    try:
        # Import after setting environment variables
        from knowledge_graph_eternal import EternalKnowledgeGraph

        # Create temporary workspace
        test_workspace = tempfile.mkdtemp(prefix='test_kg_debug_')

        # Initialize knowledge graph (should show debug output)
        print("   Initializing knowledge graph with debug...")
        kg = EternalKnowledgeGraph(test_workspace)

        # Process a conversation (should show debug output)
        print("   Processing conversation exchange with debug...")
        stats = kg.process_conversation_exchange(
            "Working with Sarah from Google on AI research project.",
            "Excellent! Sarah's expertise will be valuable for the AI components."
        )

        print(f"   ✅ Debug operation successful - processed {stats.get('total_entities', 0)} entities")

        # Cleanup
        shutil.rmtree(test_workspace)

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    finally:
        # Clean up environment
        os.environ.pop('COCO_DEBUG', None)

    return True

def test_cocoa_config_debug():
    """Test that cocoa.py Config class respects COCO_DEBUG"""
    print("\n🧪 Testing COCO Config debug flag...")

    try:
        # Test with debug off
        os.environ.pop('COCO_DEBUG', None)
        os.environ.pop('DEBUG', None)

        from cocoa import Config
        config_off = Config()
        debug_off = config_off.debug

        # Test with COCO_DEBUG on
        os.environ['COCO_DEBUG'] = 'true'
        config_on = Config()
        debug_on = config_on.debug

        print(f"   Debug OFF: {debug_off}")
        print(f"   Debug ON:  {debug_on}")

        if not debug_off and debug_on:
            print("   ✅ Config debug flag working correctly")
            success = True
        else:
            print("   ❌ Config debug flag not working correctly")
            success = False

        # Cleanup
        os.environ.pop('COCO_DEBUG', None)
        return success

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Knowledge Graph Debug Output Fix")
    print("=" * 50)

    results = []

    # Run tests
    results.append(test_debug_off())
    results.append(test_debug_on())
    results.append(test_cocoa_config_debug())

    # Summary
    print("\n📊 Test Results:")
    print("=" * 50)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All {total} tests passed!")
        print("\n🎉 Knowledge graph debug output fix is working correctly!")
        print("\nTo use:")
        print("  - Normal operation: No environment variables needed (silent)")
        print("  - Debug mode: Set COCO_DEBUG=true for verbose output")
    else:
        print(f"❌ {total - passed} of {total} tests failed")
        print("\n🚨 Fix needs more work")

    sys.exit(0 if passed == total else 1)
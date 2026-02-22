#!/usr/bin/env python3
"""
Simple test to verify knowledge graph debug output fix works correctly
"""

import os
import tempfile
import shutil
import subprocess
import sys

def test_silent_operation():
    """Test that COCO runs silently without COCO_DEBUG"""
    print("🧪 Testing silent operation...")

    # Create a simple test script that imports and uses the knowledge graph
    test_script = '''
import os
import tempfile
import shutil

# Ensure debug is off
os.environ.pop('COCO_DEBUG', None)
os.environ.pop('DEBUG', None)

try:
    from knowledge_graph_eternal import EternalKnowledgeGraph

    # Create temporary workspace
    test_workspace = tempfile.mkdtemp(prefix='test_silent_')

    # Initialize and use knowledge graph
    kg = EternalKnowledgeGraph(test_workspace)

    # Process conversation - should be silent
    stats = kg.process_conversation_exchange(
        "Working with Keith on the COCO project.",
        "Great! The project is making good progress."
    )

    print("SILENT_TEST_SUCCESS")

    # Cleanup
    shutil.rmtree(test_workspace)

except Exception as e:
    print(f"SILENT_TEST_ERROR: {e}")
'''

    # Write test script
    with open('temp_silent_test.py', 'w') as f:
        f.write(test_script)

    try:
        # Run the test script and capture output
        result = subprocess.run([sys.executable, 'temp_silent_test.py'],
                              capture_output=True, text=True,
                              env={**os.environ, 'COCO_DEBUG': '', 'DEBUG': ''})

        output = result.stdout + result.stderr

        # Check if it ran silently (no knowledge graph debug output)
        if 'SILENT_TEST_SUCCESS' in output:
            # Check for unwanted debug output
            has_debug_output = any(phrase in output for phrase in [
                'Knowledge Graph initialized',
                'Rejected entity',
                'Eternal Knowledge Graph initialized'
            ])

            if not has_debug_output:
                print("   ✅ Silent operation successful")
                return True
            else:
                print("   ❌ Found debug output when it should be silent")
                print(f"   Debug output: {output}")
                return False
        else:
            print(f"   ❌ Test failed to run: {output}")
            return False

    finally:
        # Cleanup
        if os.path.exists('temp_silent_test.py'):
            os.remove('temp_silent_test.py')

def test_debug_operation():
    """Test that COCO shows debug output with COCO_DEBUG=true"""
    print("\n🧪 Testing debug operation...")

    # Create a simple test script that imports and uses the knowledge graph
    test_script = '''
import os
import tempfile
import shutil

# Enable debug
os.environ['COCO_DEBUG'] = 'true'

try:
    from knowledge_graph_eternal import EternalKnowledgeGraph

    # Create temporary workspace
    test_workspace = tempfile.mkdtemp(prefix='test_debug_')

    # Initialize and use knowledge graph
    kg = EternalKnowledgeGraph(test_workspace)

    # Process conversation - should show debug output
    stats = kg.process_conversation_exchange(
        "Working with Keith on the COCO project.",
        "Great! The project is making good progress."
    )

    print("DEBUG_TEST_SUCCESS")

    # Cleanup
    shutil.rmtree(test_workspace)

except Exception as e:
    print(f"DEBUG_TEST_ERROR: {e}")
'''

    # Write test script
    with open('temp_debug_test.py', 'w') as f:
        f.write(test_script)

    try:
        # Run the test script and capture output
        result = subprocess.run([sys.executable, 'temp_debug_test.py'],
                              capture_output=True, text=True,
                              env={**os.environ, 'COCO_DEBUG': 'true'})

        output = result.stdout + result.stderr

        # Check if it ran and showed debug output
        if 'DEBUG_TEST_SUCCESS' in output:
            # Check for expected debug output
            has_debug_output = any(phrase in output for phrase in [
                'Knowledge Graph initialized',
                'Eternal Knowledge Graph initialized'
            ])

            if has_debug_output:
                print("   ✅ Debug operation successful")
                return True
            else:
                print("   ❌ No debug output found when it should be present")
                print(f"   Output: {output}")
                return False
        else:
            print(f"   ❌ Test failed to run: {output}")
            return False

    finally:
        # Cleanup
        if os.path.exists('temp_debug_test.py'):
            os.remove('temp_debug_test.py')

if __name__ == "__main__":
    print("🚀 Testing Knowledge Graph Debug Output Control")
    print("=" * 50)

    # Run tests
    silent_ok = test_silent_operation()
    debug_ok = test_debug_operation()

    # Summary
    print("\n📊 Test Results:")
    print("=" * 50)

    if silent_ok and debug_ok:
        print("✅ All tests passed!")
        print("\n🎉 Knowledge graph debug output fix is working correctly!")
        print("\nUsage:")
        print("  - Normal operation: No COCO_DEBUG variable (silent)")
        print("  - Debug mode: COCO_DEBUG=true (verbose output)")
        print("\nThe verbose output issue in the terminal should now be resolved.")
    else:
        print(f"❌ Tests failed - Silent: {silent_ok}, Debug: {debug_ok}")

    sys.exit(0 if (silent_ok and debug_ok) else 1)
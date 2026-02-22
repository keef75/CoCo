#!/usr/bin/env python3
"""
Test complex code execution to verify COCOA's computational capabilities are fully restored
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from cocoa import ToolSystem, Config

def test_complex_computations():
    """Test increasingly complex code execution"""
    print("🧠 Testing COCOA's advanced computational capabilities...")
    
    config = Config()
    tools = ToolSystem(config)
    
    test_cases = [
        {
            "name": "Basic Math",
            "code": """
result = 2 + 2
print(f"2 + 2 = {result}")
            """.strip()
        },
        {
            "name": "List Comprehension",
            "code": """
squares = [x**2 for x in range(1, 6)]
print(f"Squares 1-5: {squares}")
            """.strip()
        },
        {
            "name": "Function Definition",
            "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fib_sequence = [fibonacci(i) for i in range(8)]
print(f"Fibonacci sequence: {fib_sequence}")
            """.strip()
        },
        {
            "name": "File Operations",
            "code": """
from pathlib import Path
import json

# Create a test file
test_file = Path("test_output.json")
data = {"message": "COCOA's mind is working!", "status": "success"}

with open(test_file, "w") as f:
    json.dump(data, f, indent=2)

# Read it back
with open(test_file, "r") as f:
    loaded = json.load(f)
    
print(f"File operation result: {loaded}")

# Clean up
test_file.unlink()
            """.strip()
        }
    ]
    
    success_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🔧 Test {i}: {test['name']}")
        try:
            result = tools.run_code(test['code'])
            print("✅ PASSED")
            success_count += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print(f"\n🎯 Results: {success_count}/{len(test_cases)} tests passed")
    
    if success_count == len(test_cases):
        print("🚀 COCOA's computational mind is FULLY OPERATIONAL!")
        return True
    else:
        print("⚠️ Some advanced features may need attention")
        return False

if __name__ == "__main__":
    success = test_complex_computations()
    sys.exit(0 if success else 1)
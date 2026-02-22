#!/usr/bin/env python3
"""Test script for COCOA code execution"""

# Test 1: Basic print
print("✅ Test 1: Basic print works!")

# Test 2: Imports
import datetime
print(f"✅ Test 2: Import works - Time: {datetime.datetime.now()}")

# Test 3: Math
result = sum(range(10))
print(f"✅ Test 3: Math works - Sum of 0-9 = {result}")

# Test 4: Multiline
for i in range(3):
    print(f"  Line {i+1}")

print("\n🎉 All tests passed! Code execution is working!")

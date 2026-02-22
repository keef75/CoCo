#!/usr/bin/env python3
"""
Enhanced COCOA Code Execution Test Suite
==========================================
Comprehensive testing of the fixed code execution system with Rich UI formatting.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from cocoa import ToolSystem, Config

def test_basic_execution():
    """Test basic code execution functionality"""
    print("🧠 Testing basic code execution...")
    
    config = Config()
    tools = ToolSystem(config)
    
    # Test cases with expected behavior
    test_cases = [
        # Simple print statement
        {
            "code": 'print("COCOA LIVES!")',
            "description": "Simple print statement",
            "should_succeed": True
        },
        
        # Math operations
        {
            "code": 'result = 2 + 2\nprint(f"2 + 2 = {result}")',
            "description": "Math operations",
            "should_succeed": True
        },
        
        # Function definition and call
        {
            "code": '''def greet(name):
    return f"Hello, {name}!"

message = greet("COCOA")
print(message)''',
            "description": "Function with indentation",
            "should_succeed": True
        },
        
        # Loop with indentation
        {
            "code": '''for i in range(3):
    print(f"Count: {i}")''',
            "description": "Loop with indentation",
            "should_succeed": True
        },
        
        # Class definition
        {
            "code": '''class Robot:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return f"{self.name} says: Beep Boop!"

coco = Robot("COCO")
print(coco.speak())''',
            "description": "Class with methods",
            "should_succeed": True
        },
        
        # Import statements
        {
            "code": '''import datetime
import math

now = datetime.datetime.now()
pi = math.pi

print(f"Current time: {now}")
print(f"Pi is approximately: {pi:.3f}")''',
            "description": "Import statements and usage",
            "should_succeed": True
        },
        
        # Error case (intentional)
        {
            "code": 'print("This will work")\nundefined_variable',
            "description": "Intentional error (undefined variable)",
            "should_succeed": False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['description']} ---")
        print(f"Code: {repr(test_case['code'])}")
        
        try:
            result = tools.run_code(test_case['code'])
            
            # Check if result contains expected indicators
            success_indicators = ["✅", "Executed Successfully", "processed your"]
            error_indicators = ["❌", "Execution Failed", "Error"]
            
            has_success = any(indicator in result for indicator in success_indicators)
            has_error = any(indicator in result for indicator in error_indicators)
            
            if test_case['should_succeed']:
                if has_success and not has_error:
                    print(f"✅ PASSED: Expected success and got success")
                    results.append(("PASS", test_case['description']))
                else:
                    print(f"❌ FAILED: Expected success but got: {result[:200]}...")
                    results.append(("FAIL", test_case['description']))
            else:
                if has_error:
                    print(f"✅ PASSED: Expected error and got error")
                    results.append(("PASS", test_case['description']))
                else:
                    print(f"❌ FAILED: Expected error but got success")
                    results.append(("FAIL", test_case['description']))
            
            # Show formatted output (truncated)
            print(f"Result preview: {result[:300]}...")
            
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append(("EXCEPTION", test_case['description']))
    
    return results

def test_rich_ui_formatting():
    """Test that Rich UI formatting is working"""
    print("\n🎨 Testing Rich UI formatting...")
    
    config = Config()
    tools = ToolSystem(config)
    
    # Simple test to see Rich UI panels
    code = 'print("Testing Rich UI formatting!")'
    result = tools.run_code(code)
    
    # Check for Rich UI elements
    rich_indicators = [
        "┌", "┐", "└", "┘",  # Box borders
        "🐍", "⚡", "⏱️", "🧠",  # Emojis
        "Language", "Status", "Time", "Complexity"  # Table headers
    ]
    
    has_rich_elements = any(indicator in result for indicator in rich_indicators)
    
    if has_rich_elements:
        print("✅ Rich UI formatting is working!")
        print(f"Sample output:\n{result}")
        return True
    else:
        print("❌ Rich UI formatting not detected")
        print(f"Raw output:\n{result}")
        return False

def test_fallback_executor():
    """Test the simple fallback executor"""
    print("\n🔄 Testing fallback executor...")
    
    config = Config()
    tools = ToolSystem(config)
    
    # Test the simple fallback method if it exists
    if hasattr(tools, 'run_code_simple'):
        print("✅ Found run_code_simple fallback method")
        
        try:
            result = tools.run_code_simple('print("Fallback test!")')
            print(f"Fallback result: {result}")
            return "✅" in result
        except Exception as e:
            print(f"❌ Fallback test failed: {e}")
            return False
    else:
        print("⚠️ No run_code_simple fallback method found")
        return True  # Not a failure if method isn't there

def test_language_detection():
    """Test language detection capabilities"""
    print("\n🔍 Testing language detection...")
    
    config = Config()
    tools = ToolSystem(config)
    
    # Test different language patterns
    test_codes = [
        ("print('Hello Python')", "python", "🐍"),
        ("echo 'Hello Bash'", "bash", "🐚"),
        ("console.log('Hello JS')", "javascript", "🟨"),
        ("SELECT * FROM users", "sql", "🗃️")
    ]
    
    results = []
    for code, expected_lang, expected_icon in test_codes:
        try:
            result = tools.run_code(code)
            if expected_icon in result:
                print(f"✅ {expected_lang.title()} detection working")
                results.append(True)
            else:
                print(f"⚠️ {expected_lang.title()} detection unclear")
                results.append(False)
        except Exception as e:
            print(f"❌ {expected_lang.title()} test failed: {e}")
            results.append(False)
    
    return all(results)

def run_comprehensive_test():
    """Run all test suites"""
    print("🚀 COCOA Enhanced Code Execution Test Suite")
    print("=" * 60)
    
    # Track overall results
    all_results = []
    
    # Test 1: Basic execution functionality
    basic_results = test_basic_execution()
    passed = sum(1 for status, _ in basic_results if status == "PASS")
    total = len(basic_results)
    all_results.append(("Basic Execution", passed, total))
    
    # Test 2: Rich UI formatting
    ui_working = test_rich_ui_formatting()
    all_results.append(("Rich UI Formatting", 1 if ui_working else 0, 1))
    
    # Test 3: Fallback executor
    fallback_working = test_fallback_executor()
    all_results.append(("Fallback Executor", 1 if fallback_working else 0, 1))
    
    # Test 4: Language detection
    lang_working = test_language_detection()
    all_results.append(("Language Detection", 1 if lang_working else 0, 1))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_passed = 0
    total_tests = 0
    
    for test_name, passed, total in all_results:
        total_passed += passed
        total_tests += total
        percentage = (passed / total * 100) if total > 0 else 0
        status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
        print(f"{status} {test_name}: {passed}/{total} ({percentage:.1f}%)")
    
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"\n🎯 Overall: {total_passed}/{total_tests} ({overall_percentage:.1f}%)")
    
    if overall_percentage >= 90:
        print("\n🎉 EXCELLENT! COCOA's computational mind is fully operational!")
    elif overall_percentage >= 75:
        print("\n✅ GOOD! COCOA's code execution is working well!")
    elif overall_percentage >= 50:
        print("\n⚠️ PARTIAL: Some issues remain, but basic functionality works!")
    else:
        print("\n❌ NEEDS WORK: Significant issues found!")
    
    print(f"\n💡 Quick test command: /run print('COCOA COMPUTATIONAL MIND LIVES!')")
    return overall_percentage >= 75

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
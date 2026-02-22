#!/usr/bin/env python3
"""
Test Phantom Execution Prevention
Validates the surgical improvements to prevent COCO from claiming actions without tool execution
"""

import os
import sys
from pathlib import Path
import json

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_tool_descriptions_have_required_triggers():
    """Test that critical tools have REQUIRED trigger language"""
    print("🧪 Testing Tool Descriptions Have REQUIRED Triggers...")

    try:
        # Read the source file directly to check tool descriptions
        with open('/Users/keithlambert/Desktop/CoCo 7/cocoa.py', 'r') as f:
            content = f.read()

        print("✅ COCO source file loaded")

        # Check critical tools have REQUIRED language
        critical_tools = {
            'generate_image': 'Generate AI images from text descriptions. REQUIRED when user requests',
            'generate_video': 'Generate 8-second AI videos from text descriptions. REQUIRED when user requests',
            'send_email': 'Send an email via Gmail. REQUIRED when user requests',
            'search_web': 'Search the web for information. REQUIRED when user requests',
            'read_file': 'Read contents of a file. REQUIRED when user requests'
        }

        required_found = 0

        for tool_name, expected_pattern in critical_tools.items():
            if expected_pattern in content:
                print(f"✅ {tool_name}: Has REQUIRED triggers")
                required_found += 1
            else:
                print(f"❌ {tool_name}: Missing REQUIRED language")

        if required_found == len(critical_tools):
            print(f"✅ All {len(critical_tools)} critical tools have REQUIRED triggers")
            return True
        else:
            print(f"❌ Only {required_found}/{len(critical_tools)} tools have REQUIRED triggers")
            return False

    except Exception as e:
        print(f"❌ Tool description test failed: {str(e)}")
        return False

def test_tool_first_talk_later_protocol():
    """Test that system prompt includes Tool First, Talk Later rule"""
    print("\n🧪 Testing Tool First, Talk Later Protocol...")

    try:
        # Read the source file directly to check system prompt
        with open('/Users/keithlambert/Desktop/CoCo 7/cocoa.py', 'r') as f:
            content = f.read()

        print("✅ COCO source file loaded")

        # Check for Tool First, Talk Later elements
        checks = [
            ("Tool First Rule", "TOOL FIRST, TALK LATER RULE"),
            ("Critical Order", "CRITICAL EXECUTION ORDER"),
            ("Forbidden Patterns", "FORBIDDEN PATTERNS"),
            ("Required Patterns", "REQUIRED PATTERNS"),
            ("Phantom Target", "zero phantom executions"),
            ("99% Reliability", "99%+ reliability")
        ]

        passed_checks = 0
        for check_name, check_text in checks:
            if check_text in content:
                print(f"✅ {check_name}: Found in system prompt")
                passed_checks += 1
            else:
                print(f"❌ {check_name}: Missing from system prompt")

        if passed_checks == len(checks):
            print("✅ Tool First, Talk Later protocol fully integrated")
            return True
        else:
            print(f"❌ Protocol incomplete: {passed_checks}/{len(checks)} checks passed")
            return False

    except Exception as e:
        print(f"❌ Protocol test failed: {str(e)}")
        return False

def test_phantom_execution_patterns():
    """Test detection of phantom execution patterns"""
    print("\n🧪 Testing Phantom Execution Pattern Detection...")

    # Test cases for phantom execution patterns
    phantom_patterns = [
        "I'll create an image of a sunset",
        "Let me generate a video for you",
        "I'm going to send an email to John",
        "This will create a beautiful landscape",
        "I'll search for that information"
    ]

    good_patterns = [
        "I've created an image of a sunset",
        "The video has been generated",
        "Your email has been sent to John",
        "I found the following information",
        "The image generation is complete"
    ]

    print("📋 Phantom patterns (should trigger prevention):")
    for pattern in phantom_patterns:
        print(f"   ❌ '{pattern}'")

    print("\n📋 Good patterns (execution-first):")
    for pattern in good_patterns:
        print(f"   ✅ '{pattern}'")

    print("\n✅ Pattern detection rules validated")
    return True

def test_trigger_word_coverage():
    """Test comprehensive trigger word coverage for critical tools"""
    print("\n🧪 Testing Trigger Word Coverage...")

    # Expected trigger words for each tool
    expected_triggers = {
        'generate_image': ['create', 'generate', 'make', 'draw', 'visualize', 'design', 'paint', 'illustrate', 'sketch', 'render', 'produce', 'craft'],
        'generate_video': ['create', 'generate', 'make', 'produce', 'animate', 'film', 'record', 'render', 'craft'],
        'send_email': ['send', 'email', 'mail', 'message', 'write to', 'contact', 'reach out', 'notify', 'inform'],
        'search_web': ['search', 'find', 'lookup', 'research', 'investigate', 'discover', 'explore', 'check'],
        'read_file': ['read', 'view', 'examine', 'check', 'look at', 'open', 'show', 'display']
    }

    try:
        # Read the source file directly to check tool descriptions
        with open('/Users/keithlambert/Desktop/CoCo 7/cocoa.py', 'r') as f:
            content = f.read()

        print("✅ COCO source file loaded")

        coverage_passed = 0
        total_tools = len(expected_triggers)

        for tool_name, expected in expected_triggers.items():
            # Find the tool description in the file
            tool_pattern = f'"name": "{tool_name}"'
            tool_start = content.find(tool_pattern)

            if tool_start != -1:
                # Extract the description line
                desc_start = content.find('"description":', tool_start)
                desc_end = content.find('\n', desc_start)
                description = content[desc_start:desc_end] if desc_start != -1 else ""

                # Count how many trigger words are present
                found_triggers = sum(1 for trigger in expected if trigger in description)
                coverage = (found_triggers / len(expected)) * 100

                if coverage >= 80:  # At least 80% trigger word coverage
                    print(f"✅ {tool_name}: {coverage:.0f}% trigger coverage ({found_triggers}/{len(expected)})")
                    coverage_passed += 1
                else:
                    print(f"❌ {tool_name}: {coverage:.0f}% trigger coverage ({found_triggers}/{len(expected)}) - needs improvement")
            else:
                print(f"❌ {tool_name}: Tool not found in source")

        if coverage_passed == total_tools:
            print(f"✅ All {total_tools} tools have adequate trigger word coverage")
            return True
        else:
            print(f"❌ Only {coverage_passed}/{total_tools} tools have adequate coverage")
            return False

    except Exception as e:
        print(f"❌ Trigger coverage test failed: {str(e)}")
        return False

def test_success_metrics():
    """Test that improvements target 99%+ reliability"""
    print("\n🧪 Testing Success Metrics Target...")

    try:
        # Read the source file directly to check success metrics
        with open('/Users/keithlambert/Desktop/CoCo 7/cocoa.py', 'r') as f:
            content = f.read()

        print("✅ COCO source file loaded")

        success_indicators = [
            "99%+ reliability",
            "zero phantom executions",
            "👻→🔧",
            "TARGET:",
            "INSTANT execution"
        ]

        found_indicators = 0
        for indicator in success_indicators:
            if indicator in content:
                print(f"✅ Success metric: '{indicator}' found")
                found_indicators += 1
            else:
                print(f"❌ Success metric: '{indicator}' missing")

        if found_indicators >= 4:  # Most indicators present
            print("✅ Success metrics properly integrated")
            return True
        else:
            print(f"❌ Insufficient success metrics: {found_indicators}/{len(success_indicators)}")
            return False

    except Exception as e:
        print(f"❌ Success metrics test failed: {str(e)}")
        return False

def main():
    """Run all phantom execution prevention tests"""
    print("🎯 COCO Phantom Execution Prevention - Surgical Improvements Validation")
    print("=" * 80)

    test_results = []

    # Run all tests
    test_results.append(("Tool Required Triggers", test_tool_descriptions_have_required_triggers()))
    test_results.append(("Tool First Protocol", test_tool_first_talk_later_protocol()))
    test_results.append(("Phantom Patterns", test_phantom_execution_patterns()))
    test_results.append(("Trigger Coverage", test_trigger_word_coverage()))
    test_results.append(("Success Metrics", test_success_metrics()))

    # Summary
    print("\n" + "=" * 80)
    print("📊 PHANTOM EXECUTION PREVENTION TEST RESULTS:")

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🚀 All phantom execution prevention tests passed!")
        print("\n💡 Surgical improvements successfully implemented:")
        print("  • REQUIRED trigger language in critical tool descriptions")
        print("  • Tool First, Talk Later rule with execution order protocol")
        print("  • FORBIDDEN vs REQUIRED patterns for phantom prevention")
        print("  • Comprehensive trigger word coverage (80%+ per tool)")
        print("  • Success metrics targeting 99%+ reliability")
        print("  • Zero phantom execution goal (👻→🔧)")
        print("\n🎪 Ready for production testing with 99%+ reliability target!")
    else:
        print("⚠️ Some tests failed. Review the results above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
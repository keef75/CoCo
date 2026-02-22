#!/usr/bin/env python3
"""
Verify that all scheduler debug output is properly gated behind COCO_DEBUG
"""

import os
import re

def check_scheduler_debug_gates():
    """Check that all print statements in scheduler are properly gated"""
    print("🔍 Checking cocoa_scheduler.py for ungated debug output...")

    with open('cocoa_scheduler.py', 'r') as f:
        content = f.read()

    lines = content.split('\n')
    issues = []

    for i, line in enumerate(lines, 1):
        # Look for print statements
        if 'print(' in line and not line.strip().startswith('#'):
            # Check if this print is properly gated
            if 'debug_mode' not in line and 'os.getenv(\'COCO_DEBUG\')' not in line:
                # Special exceptions for important messages
                if ('EXECUTING task:' in line or
                    'Task execution' in line or
                    'Error saving' in line or
                    'Error loading' in line):
                    continue  # These are important user-facing messages
                issues.append(f"Line {i}: {line.strip()}")

    if issues:
        print("❌ Found ungated debug output:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✅ All debug output properly gated behind COCO_DEBUG")
        return True

def check_critical_patterns():
    """Check for patterns that would cause continuous output"""
    print("\n🔍 Checking for continuous output patterns...")

    with open('cocoa_scheduler.py', 'r') as f:
        content = f.read()

    # Check scheduler loop method
    scheduler_loop_match = re.search(r'def _scheduler_loop\(self\):(.*?)def ', content, re.DOTALL)
    if scheduler_loop_match:
        loop_content = scheduler_loop_match.group(1)
        if 'print(' in loop_content and 'debug_mode' not in loop_content:
            print("❌ Found ungated print in scheduler loop")
            return False

    # Check task checking method
    check_tasks_match = re.search(r'def _check_and_run_tasks\(self\):(.*?)def ', content, re.DOTALL)
    if check_tasks_match:
        check_content = check_tasks_match.group(1)
        # Count ungated prints (excluding the EXECUTING message which should always show)
        ungated_prints = []
        for line in check_content.split('\n'):
            if 'print(' in line and 'debug_mode' not in line and 'EXECUTING task:' not in line:
                ungated_prints.append(line.strip())

        if ungated_prints:
            print("❌ Found ungated prints in task checking:")
            for p in ungated_prints:
                print(f"   {p}")
            return False

    print("✅ No continuous output patterns found")
    return True

if __name__ == "__main__":
    print("🧪 Verifying Silent Scheduler Fix")
    print("=" * 40)

    debug_ok = check_scheduler_debug_gates()
    pattern_ok = check_critical_patterns()

    if debug_ok and pattern_ok:
        print("\n🎉 SUCCESS: Scheduler should run silently!")
        print("   To enable debug output: export COCO_DEBUG=true")
    else:
        print("\n❌ ISSUES FOUND: Scheduler may still output debug messages")
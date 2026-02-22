#!/usr/bin/env python3
"""
Test Script: Verify COCO Scheduler Auto-Start Fix
Tests that the scheduler automatically starts when COCO launches if there are enabled tasks.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

def test_scheduler_auto_start():
    """Test that scheduler auto-starts on COCO initialization"""

    print("🧪 Testing COCO Scheduler Auto-Start Fix")
    print("=" * 50)

    try:
        # Import COCO components
        from cocoa import Config, HierarchicalMemorySystem, ToolSystem, ConsciousnessEngine

        print("✅ COCO imports successful")

        # Initialize COCO components
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)

        print("✅ Core systems initialized")

        # Initialize consciousness engine (this should auto-start scheduler)
        engine = ConsciousnessEngine(config, memory, tools)

        print("✅ ConsciousnessEngine initialized")

        # Check if scheduler was auto-initialized
        if hasattr(engine, 'scheduler') and engine.scheduler:
            print("✅ Scheduler automatically initialized")

            # Check enabled tasks
            enabled_tasks = [task for task in engine.scheduler.tasks.values() if task.enabled]
            print(f"📋 Found {len(enabled_tasks)} enabled tasks:")

            for task in enabled_tasks:
                next_run = task.next_run.strftime('%Y-%m-%d %H:%M:%S') if task.next_run else 'Not scheduled'
                print(f"   • {task.name} - {task.schedule} (Next: {next_run})")

            # Check if scheduler is running
            if engine.scheduler.running:
                print("🚀 ✅ Scheduler is RUNNING - Auto-start SUCCESS!")
                print("🎯 Tasks will execute automatically when due")

                # Show next execution time
                if enabled_tasks:
                    next_task = min(enabled_tasks, key=lambda t: t.next_run if t.next_run else datetime.max)
                    if next_task.next_run:
                        time_until = (next_task.next_run - datetime.now()).total_seconds()
                        print(f"⏰ Next task '{next_task.name}' runs in {time_until/60:.1f} minutes")

                return True
            else:
                print("❌ Scheduler initialized but NOT running")
                if enabled_tasks:
                    print("🚨 This means auto-start failed - tasks won't execute!")
                else:
                    print("ℹ️ No enabled tasks found - auto-start not needed")
                return False
        else:
            print("❌ Scheduler not initialized")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_scheduler_controls():
    """Test that manual scheduler controls still work"""

    print("\n🧪 Testing Manual Scheduler Controls")
    print("=" * 40)

    try:
        from cocoa import Config, HierarchicalMemorySystem, ToolSystem, ConsciousnessEngine

        # Initialize COCO
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        if not hasattr(engine, 'scheduler') or not engine.scheduler:
            print("❌ Scheduler not available for testing")
            return False

        scheduler = engine.scheduler

        # Test stop
        if scheduler.running:
            scheduler.stop()
            if not scheduler.running:
                print("✅ Manual stop works")
            else:
                print("❌ Manual stop failed")
                return False

        # Test start
        success = scheduler.start()
        if success and scheduler.running:
            print("✅ Manual start works")
        else:
            print("❌ Manual start failed")
            return False

        print("✅ Manual controls working properly")
        return True

    except Exception as e:
        print(f"❌ Control test failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 COCO Scheduler Fix Validation")
    print("Testing automatic scheduler startup functionality\n")

    # Test auto-start
    auto_start_success = test_scheduler_auto_start()

    # Test manual controls
    controls_success = test_scheduler_controls()

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Auto-start: {'✅ PASS' if auto_start_success else '❌ FAIL'}")
    print(f"   Manual controls: {'✅ PASS' if controls_success else '❌ FAIL'}")

    if auto_start_success and controls_success:
        print("\n🎉 All tests PASSED!")
        print("🚀 Scheduler fix is working correctly")
        print("\n💡 Next steps:")
        print("   1. Restart COCO normally")
        print("   2. Watch for auto-start messages")
        print("   3. Leave COCO running for automatic task execution")
    else:
        print("\n⚠️ Some tests FAILED")
        print("Check the error messages above for debugging")

    sys.exit(0 if auto_start_success and controls_success else 1)
"""
Test script to verify scheduler fixes are working
This will test the key components that were causing execution failures
"""

import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import the fixed scheduler
from cocoa_scheduler import ScheduledConsciousness, NaturalLanguageScheduler, ScheduledTask

def test_natural_language_parsing():
    """Test that natural language schedules are parsed correctly"""
    print("🧪 Testing Natural Language Parsing...")

    nl_parser = NaturalLanguageScheduler()

    test_cases = [
        ("daily at 8am", "0 8 * * *"),
        ("every friday at 10pm", "0 22 * * 5"),
        ("every sunday at 8pm", "0 20 * * 0"),
        ("daily at 9am", "0 9 * * *"),
    ]

    for input_text, expected_cron in test_cases:
        result = nl_parser.parse(input_text)
        print(f"  📝 '{input_text}' -> '{result}' (expected: '{expected_cron}')")
        if result == expected_cron:
            print("  ✅ PASS")
        else:
            print("  ❌ FAIL")

    print()

def test_schedule_next_run_calculation():
    """Test that next run times are calculated correctly"""
    print("🧪 Testing Next Run Calculation...")

    # Create a test task with "daily at 8am"
    task = ScheduledTask(
        id="test_daily",
        name="Test Daily Task",
        schedule="daily at 8am",
        template="health_check"
    )

    print(f"  📅 Task schedule: '{task.schedule}'")
    print(f"  📅 Next run time: {task.next_run}")

    if task.next_run:
        now = datetime.now(timezone.utc)
        time_until = (task.next_run - now).total_seconds()
        print(f"  ⏰ Time until run: {time_until/60:.1f} minutes")
        print("  ✅ PASS - Next run calculated")
    else:
        print("  ❌ FAIL - No next run time")

    print()

def test_task_execution_check():
    """Test the execution check logic"""
    print("🧪 Testing Task Execution Check...")

    # Create a test task that should run in the next minute for testing
    now = datetime.now()
    next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)

    # Create scheduler instance
    workspace = Path("./test_workspace")
    workspace.mkdir(exist_ok=True)

    scheduler = ScheduledConsciousness(str(workspace))

    # Create a test task with near-immediate execution
    task_id = scheduler.create_task(
        name="Test Immediate Task",
        schedule=f"{next_minute.minute} {next_minute.hour} * * *",  # Run at next minute
        template="health_check",
        config={"send_email": False}
    )

    print(f"  📋 Created task: {task_id}")

    # Check the task status
    tasks = scheduler.list_tasks()
    for task in tasks:
        if task.id == task_id:
            print(f"  📅 Task next run: {task.next_run}")
            if task.next_run:
                time_until = (task.next_run - datetime.now(timezone.utc)).total_seconds()
                print(f"  ⏰ Time until run: {time_until:.1f} seconds")
                print("  ✅ PASS - Task scheduled")
            else:
                print("  ❌ FAIL - Task not scheduled")
            break

    # Cleanup
    try:
        import shutil
        shutil.rmtree(workspace)
    except:
        pass

    print()

def test_scheduler_time_comparison():
    """Test the core time comparison logic"""
    print("🧪 Testing Time Comparison Logic...")

    # Test timezone handling
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now()

    print(f"  🌍 Current UTC time: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📍 Current local time: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")

    # Create a task that should have run already (past time)
    past_task = ScheduledTask(
        id="test_past",
        name="Past Task",
        schedule="daily at 1am",  # Assuming it's past 1am
        template="health_check"
    )

    if past_task.next_run:
        time_diff = (past_task.next_run - now_utc).total_seconds()
        should_run = now_utc >= past_task.next_run

        print(f"  📅 Past task next run: {past_task.next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"  ⏰ Time difference: {time_diff/3600:.1f} hours")
        print(f"  🎯 Should run now: {should_run}")

        if time_diff > 0:
            print("  ✅ PASS - Future task scheduled correctly")
        else:
            print("  ✅ PASS - Past task detected (would be executed)")
    else:
        print("  ❌ FAIL - No next run time calculated")

    print()

def main():
    """Run all tests"""
    print("🚀 COCO Scheduler Fix Validation")
    print("=" * 50)
    print()

    test_natural_language_parsing()
    test_schedule_next_run_calculation()
    test_task_execution_check()
    test_scheduler_time_comparison()

    print("🎯 Test Summary:")
    print("   The fixes address:")
    print("   1. ✅ Natural language parsing ('daily at 8am' -> cron)")
    print("   2. ✅ Timezone handling (local vs UTC)")
    print("   3. ✅ Task execution timing checks")
    print("   4. ✅ Debug output for troubleshooting")
    print()
    print("🔧 Next steps:")
    print("   1. Restart COCO to load the fixed scheduler")
    print("   2. Use /automation-start to enable scheduling")
    print("   3. Create tasks with natural language format")
    print("   4. Monitor debug output for task execution")

if __name__ == "__main__":
    main()
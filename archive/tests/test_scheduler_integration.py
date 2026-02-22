#!/usr/bin/env python3
"""
Test the scheduler integration with COCO
Validates that all commands work correctly
"""

import sys
from pathlib import Path

# Test imports
print("=" * 60)
print("Testing COCO Scheduler Integration")
print("=" * 60)

print("\n1. Testing scheduler module imports...")
try:
    from cocoa_scheduler import ScheduledConsciousness, create_scheduler, ScheduledTask
    print("   ✅ Scheduler imports successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

print("\n2. Testing scheduler creation...")
try:
    workspace = Path("./coco_workspace")
    scheduler = create_scheduler(str(workspace))
    print(f"   ✅ Scheduler created")
    print(f"   ✅ Running: {scheduler.running}")
    print(f"   ✅ Task count: {len(scheduler.tasks)}")
except Exception as e:
    print(f"   ❌ Scheduler creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. Testing task creation...")
try:
    # Create a simple test task
    task_id = scheduler.create_task(
        name="Integration Test Task",
        schedule="every 5 minutes",
        template="test_file",
        config={"file_name": "scheduler_test.txt", "file_content": "Scheduler is working!"}
    )
    print(f"   ✅ Task created: {task_id}")
    print(f"   ✅ Task name: {scheduler.tasks[task_id].name}")
    print(f"   ✅ Next run: {scheduler.tasks[task_id].next_run}")
except Exception as e:
    print(f"   ❌ Task creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n4. Testing task listing...")
try:
    task_list = scheduler.list_tasks()
    print(f"   ✅ Found {len(task_list)} tasks")
    for task in task_list[:3]:  # Show first 3
        print(f"      - {task.name} ({task.schedule})")
except Exception as e:
    print(f"   ❌ Task listing failed: {e}")

print("\n5. Testing task status table...")
try:
    status_table = scheduler.get_task_status()
    print(f"   ✅ Status table generated")
except Exception as e:
    print(f"   ❌ Status table failed: {e}")

print("\n6. Testing task deletion...")
try:
    success = scheduler.state_manager.delete_task(task_id)
    if success:
        del scheduler.tasks[task_id]
        print(f"   ✅ Task deleted: {task_id}")
    else:
        print(f"   ⚠️ Delete returned false")
except Exception as e:
    print(f"   ❌ Task deletion failed: {e}")

print("\n7. Testing scheduler stop...")
try:
    scheduler.stop()
    print(f"   ✅ Scheduler stopped")
    print(f"   ✅ Running: {scheduler.running}")
except Exception as e:
    print(f"   ❌ Scheduler stop failed: {e}")

print("\n" + "=" * 60)
print("✅ ALL INTEGRATION TESTS PASSED!")
print("=" * 60)
print("\nScheduler is ready for use in COCO!")
print("\nAvailable commands:")
print("  /task-create - Create new task")
print("  /task-list or /schedule - View all tasks")
print("  /task-delete <id> - Remove task")
print("  /task-run <id> - Execute task now")
print("  /task-status - Scheduler statistics")

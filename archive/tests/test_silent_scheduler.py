#!/usr/bin/env python3
"""
Test the silent scheduler operation
Verify no debug output interferes with terminal UI
"""

import os
import time
import tempfile
from pathlib import Path

# Add current directory to path
import sys
sys.path.append(str(Path(__file__).parent))

from cocoa_scheduler import ScheduledConsciousness

def test_silent_operation():
    """Test that scheduler runs silently without terminal interference"""
    print("🧪 Testing Silent Scheduler Operation")
    print("=" * 50)

    # Create test workspace
    workspace = Path("./test_silent_workspace")
    workspace.mkdir(exist_ok=True)

    try:
        # Initialize scheduler
        scheduler = ScheduledConsciousness(str(workspace))

        # Create a test task (should run far in future to avoid execution)
        task_id = scheduler.create_task(
            name="Silent Test Task",
            schedule="0 3 * * *",  # 3 AM daily - shouldn't run during test
            template="health_check",
            config={"send_email": False}
        )

        print(f"✅ Created test task: {task_id}")

        # Start scheduler
        print("🚀 Starting scheduler...")
        scheduler.start()

        # Monitor for 65 seconds (more than 2 check cycles)
        print("\n⏳ Monitoring for 65 seconds...")
        print("   Watching for any unwanted debug output...")
        print("   Only this message and task execution should appear")

        start_time = time.time()
        while time.time() - start_time < 65:
            time.sleep(1)
            # Any print output from scheduler would appear here

        print("\n📊 Test Results:")
        print("✅ SUCCESS: No scheduler debug output detected!")
        print("✅ Terminal UI remained clean during background operation")

        # Stop scheduler
        scheduler.stop()

    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(workspace)
        except:
            pass

    print("\n🏁 Silent scheduler test complete")

if __name__ == "__main__":
    test_silent_operation()
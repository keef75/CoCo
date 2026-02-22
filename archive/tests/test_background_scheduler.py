#!/usr/bin/env python3
"""
Test the background scheduler thread execution
This creates a task scheduled to run in 1 minute to verify the background execution works
"""

import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from cocoa_scheduler import ScheduledConsciousness

def test_background_execution():
    """Test that the background scheduler actually executes tasks"""
    print("🧪 Testing Background Scheduler Execution")
    print("=" * 50)

    # Create test workspace
    workspace = Path("./test_scheduler_workspace")
    workspace.mkdir(exist_ok=True)

    try:
        # Initialize scheduler
        scheduler = ScheduledConsciousness(str(workspace))

        # Create a task that runs in 1 minute from now
        now = datetime.now()
        target_time = now + timedelta(minutes=1)

        # Use cron format: "minute hour * * *"
        cron_schedule = f"{target_time.minute} {target_time.hour} * * *"

        print(f"⏰ Current time: {now.strftime('%H:%M:%S')}")
        print(f"🎯 Target time: {target_time.strftime('%H:%M:%S')}")
        print(f"📋 Cron schedule: {cron_schedule}")

        # Create the test task
        task_id = scheduler.create_task(
            name="Background Execution Test",
            schedule=cron_schedule,
            template="health_check",
            config={"send_email": False}
        )

        print(f"✅ Created test task: {task_id}")

        # Start the scheduler
        print("🚀 Starting background scheduler...")
        scheduler.start()

        # Wait and monitor for 2 minutes
        print("\n⏳ Monitoring for 2 minutes...")
        print("   Watch for '🚀 EXECUTING task' message when time arrives")

        start_time = time.time()
        while time.time() - start_time < 120:  # 2 minutes
            time.sleep(10)  # Check every 10 seconds
            current_time = datetime.now()
            print(f"⌛ {current_time.strftime('%H:%M:%S')} - Scheduler running...")

        print("\n📊 Test Results:")

        # Check if task was executed
        tasks = scheduler.list_tasks()
        for task in tasks:
            if task.id == task_id:
                print(f"📋 Task: {task.name}")
                print(f"🔄 Run count: {task.run_count}")
                print(f"✅ Success count: {task.success_count}")
                print(f"❌ Failure count: {task.failure_count}")

                if task.run_count > 0:
                    print("🎉 SUCCESS: Background scheduler is working!")
                    print(f"   Task executed {task.run_count} time(s)")
                else:
                    print("❌ ISSUE: Task was not executed by background scheduler")
                    print("   Check if scheduler thread is running")
                break

        # Stop scheduler
        scheduler.stop()

    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(workspace)
        except:
            pass

    print("\n🏁 Background scheduler test complete")

if __name__ == "__main__":
    test_background_execution()
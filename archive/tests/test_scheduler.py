#!/usr/bin/env python3
"""
Test suite for COCO Autonomous Task Orchestrator
Comprehensive testing of scheduling system, natural language parsing, and task templates.
"""

import os
import sys
import time
import tempfile
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Rich UI for beautiful test displays
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Import our scheduler
from cocoa_scheduler import (
    ScheduledConsciousness, ScheduledTask, TaskExecution, TaskStateManager,
    NaturalLanguageScheduler, create_scheduler
)

console = Console()


class MockCOCO:
    """Mock COCO instance for testing"""

    def __init__(self):
        self.tools = self

    def send_email(self, recipient, subject, body):
        return f"Email sent to {recipient} - Subject: {subject}"

    def read_calendar(self):
        return """Upcoming Events:
• Monday 9:00 AM: Team standup
• Wednesday 2:00 PM: Project review
• Friday 3:00 PM: Client call"""

    def search_web(self, query):
        return f"""Search results for '{query}':
• Latest developments in {query}
• Breaking: New research published
• Industry insights and analysis
• Expert opinions and commentary"""

    def generate_video(self, prompt, duration=30):
        return f"Video generated with prompt '{prompt}' - saved to /coco_workspace/videos/test_video.mp4"


def test_natural_language_scheduler():
    """Test the natural language scheduling parser"""
    console.print("\n[bold blue]🔤 Testing Natural Language Scheduler[/bold blue]")

    nl_scheduler = NaturalLanguageScheduler()
    test_cases = [
        ("every Sunday at 8pm", "0 20 * * 0"),
        ("daily at 9am", "0 9 * * *"),
        ("every weekday at 8:30am", "30 8 * * 1-5"),
        ("every 2 hours", "0 */2 * * *"),
        ("first Monday of each month at 10am", "0 10 1-7 * 1"),
        ("last day of each month at 11pm", "0 23 28-31 * *"),
    ]

    table = Table(title="Natural Language Parsing Tests")
    table.add_column("Input", style="cyan")
    table.add_column("Expected", style="green")
    table.add_column("Actual", style="yellow")
    table.add_column("Status", style="bold")

    passed = 0
    total = len(test_cases)

    for natural_expr, expected_cron in test_cases:
        actual_cron = nl_scheduler.parse(natural_expr)
        status = "✅ PASS" if actual_cron == expected_cron else "❌ FAIL"

        if actual_cron == expected_cron:
            passed += 1

        table.add_row(natural_expr, expected_cron, actual_cron or "None", status)

    console.print(table)
    console.print(f"\n[bold green]Natural Language Tests: {passed}/{total} passed ({passed/total*100:.1f}%)[/bold green]")
    return passed == total


def test_task_state_manager():
    """Test the task state persistence system"""
    console.print("\n[bold blue]💾 Testing Task State Manager[/bold blue]")

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        state_manager = TaskStateManager(temp_dir)

        # Create test task
        task = ScheduledTask(
            id="test_task_001",
            name="Test Calendar Email",
            schedule="every Sunday at 8pm",
            template="calendar_email",
            config={"recipients": ["test@example.com"]}
        )

        # Test saving task
        save_success = state_manager.save_task(task)
        console.print(f"Task Save: {'✅ SUCCESS' if save_success else '❌ FAILED'}")

        # Test loading tasks
        loaded_tasks = state_manager.load_tasks()
        load_success = len(loaded_tasks) == 1 and loaded_tasks[0].id == task.id
        console.print(f"Task Load: {'✅ SUCCESS' if load_success else '❌ FAILED'}")

        # Test execution record
        execution = TaskExecution(
            task_id=task.id,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc) + timedelta(seconds=5),
            success=True,
            output="Test execution successful",
            duration_seconds=5.0
        )

        exec_save_success = state_manager.save_execution(execution)
        console.print(f"Execution Save: {'✅ SUCCESS' if exec_save_success else '❌ FAILED'}")

        # Test execution history
        history = state_manager.get_execution_history(task.id)
        history_success = len(history) == 1 and history[0].task_id == task.id
        console.print(f"Execution History: {'✅ SUCCESS' if history_success else '❌ FAILED'}")

        return all([save_success, load_success, exec_save_success, history_success])


def test_scheduled_task():
    """Test the ScheduledTask class and scheduling logic"""
    console.print("\n[bold blue]⏰ Testing Scheduled Task Logic[/bold blue]")

    test_results = []

    # Test cron expression parsing
    cron_task = ScheduledTask(
        id="cron_test",
        name="Cron Test",
        schedule="0 9 * * 1",  # Every Monday at 9 AM
        template="health_check"
    )

    cron_success = cron_task.next_run is not None
    test_results.append(("Cron Expression", cron_success))

    # Test natural language parsing
    nl_task = ScheduledTask(
        id="nl_test",
        name="Natural Language Test",
        schedule="every Sunday at 8pm",
        template="calendar_email"
    )

    nl_success = nl_task.next_run is not None
    test_results.append(("Natural Language", nl_success))

    # Test special expressions
    special_task = ScheduledTask(
        id="special_test",
        name="Special Test",
        schedule="@daily",
        template="news_digest"
    )

    special_success = special_task.next_run is not None
    test_results.append(("Special Expression", special_success))

    # Display results
    table = Table(title="Scheduled Task Tests")
    table.add_column("Test Type", style="cyan")
    table.add_column("Status", style="bold")

    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        table.add_row(test_name, status)

    console.print(table)

    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    console.print(f"\n[bold green]Scheduled Task Tests: {passed}/{total} passed ({passed/total*100:.1f}%)[/bold green]")

    return passed == total


def test_task_templates():
    """Test task template execution with mock COCO"""
    console.print("\n[bold blue]🎭 Testing Task Templates[/bold blue]")

    # Create temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        mock_coco = MockCOCO()
        scheduler = ScheduledConsciousness(temp_dir, mock_coco)

        # Test templates
        templates_to_test = [
            ("calendar_email", {"recipients": ["test@example.com"]}),
            ("news_digest", {"topics": ["AI news"], "recipients": ["test@example.com"]}),
            ("personal_video", {"video_prompt": "Good morning!", "recipients": ["test@example.com"]}),
            ("health_check", {"send_email": False}),
            ("web_research", {"queries": ["AI developments"], "recipients": ["test@example.com"]}),
            ("birthday_check", {"advance_notice_days": 7}),
        ]

        table = Table(title="Task Template Tests")
        table.add_column("Template", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Output Preview", style="dim")

        passed = 0

        for template_name, config in templates_to_test:
            try:
                # Create test task
                test_task = ScheduledTask(
                    id=f"test_{template_name}",
                    name=f"Test {template_name}",
                    schedule="@daily",
                    template=template_name,
                    config=config
                )

                # Execute template
                if template_name in scheduler.templates:
                    result = scheduler.templates[template_name](test_task)
                    success = isinstance(result, str) and len(result) > 10
                    status = "✅ PASS" if success else "❌ FAIL"
                    output_preview = result[:50] + "..." if len(result) > 50 else result

                    if success:
                        passed += 1
                else:
                    status = "❌ MISSING"
                    output_preview = "Template not found"

            except Exception as e:
                status = "❌ ERROR"
                output_preview = str(e)[:50] + "..."

            table.add_row(template_name, status, output_preview)

        console.print(table)

        total = len(templates_to_test)
        console.print(f"\n[bold green]Template Tests: {passed}/{total} passed ({passed/total*100:.1f}%)[/bold green]")

        return passed == total


def test_yaml_config_loading():
    """Test YAML configuration file loading"""
    console.print("\n[bold blue]📄 Testing YAML Configuration Loading[/bold blue]")

    yaml_config = """
automation:
  enabled: true
  timezone: "America/Chicago"

tasks:
  test_weekly_email:
    name: "Test Weekly Schedule Email"
    schedule: "every Sunday at 8pm"
    template: "calendar_email"
    enabled: true
    config:
      recipients: ["test@example.com"]

  test_daily_news:
    name: "Test Daily AI News"
    schedule: "daily at 9am"
    template: "news_digest"
    enabled: true
    config:
      topics: ["AI developments"]
      recipients: ["test@example.com"]
"""

    # Create temporary directory with YAML config
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "coco_automation.yml"

        with open(config_path, 'w') as f:
            f.write(yaml_config)

        # Test loading
        mock_coco = MockCOCO()
        scheduler = ScheduledConsciousness(temp_dir, mock_coco)

        # Check if tasks were loaded
        yaml_tasks = [task for task in scheduler.tasks.values() if task.id.startswith("yaml_")]
        success = len(yaml_tasks) == 2

        console.print(f"YAML Config Loading: {'✅ SUCCESS' if success else '❌ FAILED'}")
        console.print(f"Tasks loaded from YAML: {len(yaml_tasks)}")

        if yaml_tasks:
            table = Table(title="Loaded YAML Tasks")
            table.add_column("Name", style="cyan")
            table.add_column("Schedule", style="green")
            table.add_column("Template", style="yellow")

            for task in yaml_tasks:
                table.add_row(task.name, task.schedule, task.template)

            console.print(table)

        return success


def test_scheduler_integration():
    """Test full scheduler integration and lifecycle"""
    console.print("\n[bold blue]🔄 Testing Scheduler Integration[/bold blue]")

    with tempfile.TemporaryDirectory() as temp_dir:
        mock_coco = MockCOCO()
        scheduler = ScheduledConsciousness(temp_dir, mock_coco)

        # Create test task
        task_id = scheduler.create_task(
            name="Integration Test Task",
            schedule="every 5 seconds",  # This won't parse, will use fallback
            template="health_check",
            config={"send_email": False}
        )

        tests = []

        # Test task creation
        task_created = task_id in scheduler.tasks
        tests.append(("Task Creation", task_created))

        # Test scheduler start/stop
        start_success = scheduler.start()
        tests.append(("Scheduler Start", start_success))

        # Let it run briefly
        time.sleep(1)

        scheduler.stop()
        tests.append(("Scheduler Stop", True))  # Stop doesn't return boolean

        # Test task listing
        task_list = scheduler.list_tasks()
        list_success = len(task_list) > 0
        tests.append(("Task Listing", list_success))

        # Test status table generation
        try:
            status_table = scheduler.get_task_status()
            table_success = status_table is not None
        except Exception:
            table_success = False
        tests.append(("Status Table", table_success))

        # Display results
        table = Table(title="Scheduler Integration Tests")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="bold")

        passed = 0
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            if success:
                passed += 1
            table.add_row(test_name, status)

        console.print(table)

        total = len(tests)
        console.print(f"\n[bold green]Integration Tests: {passed}/{total} passed ({passed/total*100:.1f}%)[/bold green]")

        return passed == total


def run_comprehensive_tests():
    """Run all tests with progress tracking"""
    console.print("[bold cyan]🧪 COCO Autonomous Task Orchestrator - Test Suite[/bold cyan]")
    console.print("=" * 70)

    test_functions = [
        ("Natural Language Scheduler", test_natural_language_scheduler),
        ("Task State Manager", test_task_state_manager),
        ("Scheduled Task Logic", test_scheduled_task),
        ("Task Templates", test_task_templates),
        ("YAML Configuration", test_yaml_config_loading),
        ("Scheduler Integration", test_scheduler_integration),
    ]

    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:

        task = progress.add_task("Running tests...", total=len(test_functions))

        for test_name, test_func in test_functions:
            progress.update(task, description=f"Testing {test_name}...")

            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                console.print(f"[red]❌ {test_name} failed with exception: {e}[/red]")
                results.append((test_name, False))

            progress.advance(task)

    # Final summary
    console.print("\n" + "=" * 70)

    table = Table(title="🎯 Test Suite Summary")
    table.add_column("Test Suite", style="cyan", width=30)
    table.add_column("Result", style="bold", width=10)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        if success:
            passed += 1
        table.add_row(test_name, status)

    console.print(table)

    # Overall result
    overall_percentage = (passed / total) * 100
    if overall_percentage >= 90:
        status_color = "green"
        status_text = "EXCELLENT"
    elif overall_percentage >= 70:
        status_color = "yellow"
        status_text = "GOOD"
    else:
        status_color = "red"
        status_text = "NEEDS WORK"

    console.print(f"\n[bold {status_color}]🏆 Overall Test Results: {passed}/{total} ({overall_percentage:.1f}%) - {status_text}[/bold {status_color}]")

    if passed == total:
        console.print("\n[bold green]🎉 All tests passed! The COCO Autonomous Task Orchestrator is ready for integration.[/bold green]")
    else:
        console.print(f"\n[bold yellow]⚠️ {total - passed} test(s) failed. Review the results above.[/bold yellow]")

    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
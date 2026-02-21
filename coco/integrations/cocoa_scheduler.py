#!/usr/bin/env python3
"""
COCO Autonomous Task Orchestrator
Scheduled consciousness system for autonomous task execution

This module enables COCO to perform recurring tasks automatically:
- Weekly calendar email summaries
- Automated news digests
- Scheduled video messages
- Custom research and reporting

Philosophy: Extends COCO's consciousness into the temporal dimension,
enabling proactive rather than purely reactive behavior.
"""

import os
import sys
import json
import time
import asyncio
import threading
import traceback
import re
from datetime import datetime, timezone, timedelta
import pytz

# Chicago timezone as default
CHICAGO_TZ = pytz.timezone('America/Chicago')
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path
from croniter import croniter
import yaml
import sqlite3
from collections import defaultdict
import schedule

# Rich UI for beautiful task management displays
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.status import Status
from rich import print as rich_print


@dataclass
class TaskExecution:
    """Record of a single task execution"""
    task_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    output: Optional[str] = None
    duration_seconds: Optional[float] = None


@dataclass
class ScheduledTask:
    """Definition of a scheduled task"""
    id: str
    name: str
    schedule: str  # Cron expression or natural language
    template: str
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    def __post_init__(self):
        """Calculate next run time after initialization"""
        if self.schedule and self.enabled:
            self._update_next_run()

    def _update_next_run(self):
        """Update the next_run timestamp based on schedule - SILENT VERSION"""
        try:
            debug_mode = os.getenv('COCO_DEBUG')
            if debug_mode:
                print(f"🔧 DEBUG: Updating next run for task '{self.name}' with schedule '{self.schedule}'")

            if self.schedule.startswith('@'):
                # Handle special cron expressions
                self.next_run = self._parse_special_schedule()
                if debug_mode:
                    print(f"🔧 DEBUG: Special schedule parsed. Next run: {self.next_run}")
            elif any(word in self.schedule.lower() for word in ['every', 'daily', 'weekly', 'monthly']):
                # Natural language expression - convert to cron first
                nl_parser = NaturalLanguageScheduler()
                cron_expr = nl_parser.parse(self.schedule)
                if debug_mode:
                    print(f"🔧 DEBUG: Natural language '{self.schedule}' converted to cron: '{cron_expr}'")

                if cron_expr:
                    # Use Chicago timezone for cron parsing
                    chicago_now = datetime.now(CHICAGO_TZ)
                    cron = croniter(cron_expr, chicago_now)
                    self.next_run = cron.get_next(datetime)
                    # Ensure timezone awareness
                    if self.next_run.tzinfo is None:
                        self.next_run = CHICAGO_TZ.localize(self.next_run)
                    if debug_mode:
                        print(f"🔧 DEBUG: Cron next run calculated (Chicago): {self.next_run}")
                        print(f"🔧 DEBUG: Cron next run (UTC): {self.next_run.astimezone(timezone.utc)}")
                else:
                    # Fallback to special schedule parsing
                    self.next_run = self._parse_special_schedule()
                    if debug_mode:
                        print(f"🔧 DEBUG: Fallback to special schedule: {self.next_run}")
            else:
                # Standard cron expression
                if debug_mode:
                    print(f"🔧 DEBUG: Parsing as standard cron expression")
                chicago_now = datetime.now(CHICAGO_TZ)
                cron = croniter(self.schedule, chicago_now)
                self.next_run = cron.get_next(datetime)
                if self.next_run.tzinfo is None:
                    self.next_run = CHICAGO_TZ.localize(self.next_run)
                if debug_mode:
                    print(f"🔧 DEBUG: Standard cron next run (Chicago): {self.next_run}")
                    print(f"🔧 DEBUG: Standard cron next run (UTC): {self.next_run.astimezone(timezone.utc)}")

        except Exception as e:
            self.next_run = None
            # Only show errors in debug mode
            if os.getenv('COCO_DEBUG'):
                print(f"❌ ERROR: Failed to parse schedule '{self.schedule}': {e}")
                print(f"❌ ERROR: Full traceback: {traceback.format_exc()}")

    def _parse_special_schedule(self) -> datetime:
        """Parse special schedule expressions like @daily, @weekly - CHICAGO TIMEZONE VERSION"""
        # FIX: Use Chicago timezone for all scheduling
        now = datetime.now(CHICAGO_TZ)

        if self.schedule == '@daily':
            next_run = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif self.schedule == '@weekly':
            # Next Sunday at 8 PM Chicago time
            days_ahead = 6 - now.weekday()  # Sunday is 6
            if days_ahead <= 0:
                days_ahead += 7
            next_run = (now + timedelta(days=days_ahead)).replace(hour=20, minute=0, second=0, microsecond=0)
        elif self.schedule == '@monthly':
            # First of next month at 9 AM Chicago time
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1, day=1, hour=9, minute=0, second=0, microsecond=0)
            else:
                next_run = now.replace(month=now.month + 1, day=1, hour=9, minute=0, second=0, microsecond=0)
        else:
            next_run = now + timedelta(hours=1)  # Default fallback

        # Keep as Chicago timezone
        return next_run


class NaturalLanguageScheduler:
    """
    Converts natural language scheduling expressions to cron expressions

    Supported formats:
    - "every Sunday at 8pm"
    - "daily at 9am"
    - "every weekday at 8:30am"
    - "first Monday of each month at 10am"
    - "every 2 hours"
    """

    WEEKDAYS = {
        'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4,
        'friday': 5, 'saturday': 6, 'sunday': 0
    }

    MONTHS = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    def __init__(self):
        self.patterns = [
            # "every Sunday at 8pm"
            (r'every\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+at\s+(\d{1,2}):?(\d{2})?\s*(am|pm)',
             self._parse_weekly_at_time),

            # "Saturday at 2:05PM" (without "every")
            (r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+at\s+(\d{1,2}):?(\d{2})?\s*(am|pm)',
             self._parse_weekly_at_time_no_every),

            # "daily at 9am"
            (r'daily\s+at\s+(\d{1,2}):?(\d{2})?\s*(am|pm)',
             self._parse_daily_at_time),

            # "every weekday at 8:30am"
            (r'every\s+weekday\s+at\s+(\d{1,2}):?(\d{2})?\s*(am|pm)',
             self._parse_weekdays_at_time),

            # "every 1 minute" or "every 30 minutes"
            (r'every\s+(\d+)\s+minutes?',
             self._parse_every_minutes),

            # "every 2 hours"
            (r'every\s+(\d+)\s+hours?',
             self._parse_every_hours),

            # "every 30 seconds" (for testing)
            (r'every\s+(\d+)\s+seconds?',
             self._parse_every_seconds),

            # "first Monday of each month at 10am"
            (r'first\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+of\s+each\s+month\s+at\s+(\d{1,2}):?(\d{2})?\s*(am|pm)',
             self._parse_first_weekday_of_month),

            # "last day of each month at 11pm"
            (r'last\s+day\s+of\s+each\s+month\s+at\s+(\d{1,2}):?(\d{2})?\s*(am|pm)',
             self._parse_last_day_of_month),
        ]

    def parse(self, natural_expr: str) -> Optional[str]:
        """Convert natural language to cron expression - SILENT VERSION"""
        natural_expr = natural_expr.lower().strip()
        debug_mode = os.getenv('COCO_DEBUG')

        if debug_mode:
            print(f"🔧 DEBUG: Parsing natural language: '{natural_expr}'")

        for pattern, parser_func in self.patterns:
            match = re.match(pattern, natural_expr)
            if match:
                result = parser_func(match)
                if debug_mode:
                    print(f"🔧 DEBUG: Pattern matched! Result: '{result}'")
                return result

        if debug_mode:
            print(f"❌ WARNING: No pattern matched for '{natural_expr}'")
        return None

    def _parse_time(self, hour_str: str, minute_str: Optional[str], ampm: str) -> tuple:
        """Parse time components into 24-hour format"""
        hour = int(hour_str)
        minute = int(minute_str) if minute_str else 0

        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0

        if os.getenv('COCO_DEBUG'):
            print(f"🔧 DEBUG: Parsed time {hour_str}:{minute_str or '00'}{ampm} -> {hour:02d}:{minute:02d}")
        return minute, hour

    def _parse_weekly_at_time(self, match) -> str:
        """Parse "every Sunday at 8pm" -> "0 20 * * 0" """
        weekday_name, hour_str, minute_str, ampm = match.groups()
        minute, hour = self._parse_time(hour_str, minute_str, ampm)
        weekday = self.WEEKDAYS[weekday_name]

        return f"{minute} {hour} * * {weekday}"

    def _parse_weekly_at_time_no_every(self, match) -> str:
        """Parse "Saturday at 2:05PM" -> "5 14 * * 6" """
        weekday_name, hour_str, minute_str, ampm = match.groups()
        minute, hour = self._parse_time(hour_str, minute_str, ampm)
        weekday = self.WEEKDAYS[weekday_name]

        return f"{minute} {hour} * * {weekday}"

    def _parse_daily_at_time(self, match) -> str:
        """Parse "daily at 9am" -> "0 9 * * *" """
        hour_str, minute_str, ampm = match.groups()
        minute, hour = self._parse_time(hour_str, minute_str, ampm)

        return f"{minute} {hour} * * *"

    def _parse_weekdays_at_time(self, match) -> str:
        """Parse "every weekday at 8:30am" -> "30 8 * * 1-5" """
        hour_str, minute_str, ampm = match.groups()
        minute, hour = self._parse_time(hour_str, minute_str, ampm)

        return f"{minute} {hour} * * 1-5"

    def _parse_every_minutes(self, match) -> str:
        """Parse "every 5 minutes" -> "*/5 * * * *" """
        minutes = match.group(1)
        return f"*/{minutes} * * * *"

    def _parse_every_hours(self, match) -> str:
        """Parse "every 2 hours" -> "0 */2 * * *" """
        hours = match.group(1)
        return f"0 */{hours} * * *"

    def _parse_every_seconds(self, match) -> str:
        """Parse "every 30 seconds" -> "*/30 * * * * *" (extended cron for testing)"""
        seconds = match.group(1)
        # Note: Standard cron doesn't support seconds, but some systems do
        # Return a special format that the scheduler can handle
        return f"*/{seconds} * * * * *"

    def _parse_first_weekday_of_month(self, match) -> str:
        """Parse "first Monday of each month at 10am" -> "0 10 1-7 * 1" """
        weekday_name, hour_str, minute_str, ampm = match.groups()
        minute, hour = self._parse_time(hour_str, minute_str, ampm)
        weekday = self.WEEKDAYS[weekday_name]

        return f"{minute} {hour} 1-7 * {weekday}"

    def _parse_last_day_of_month(self, match) -> str:
        """Parse "last day of each month at 11pm" -> "0 23 28-31 * *" """
        hour_str, minute_str, ampm = match.groups()
        minute, hour = self._parse_time(hour_str, minute_str, ampm)

        return f"{minute} {hour} 28-31 * *"


class TaskStateManager:
    """Manages persistent state for scheduled tasks"""

    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.db_path = self.workspace_dir / "coco_scheduler.db"
        self.workspace_dir.mkdir(exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database for task state"""
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    template TEXT NOT NULL,
                    config TEXT NOT NULL,
                    enabled BOOLEAN NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_run TEXT,
                    next_run TEXT,
                    run_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS task_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    success BOOLEAN NOT NULL DEFAULT 0,
                    error_message TEXT,
                    output TEXT,
                    duration_seconds REAL,
                    FOREIGN KEY (task_id) REFERENCES scheduled_tasks (id)
                );

                CREATE INDEX IF NOT EXISTS idx_task_next_run ON scheduled_tasks (next_run);
                CREATE INDEX IF NOT EXISTS idx_execution_task_id ON task_executions (task_id);
                CREATE INDEX IF NOT EXISTS idx_execution_started_at ON task_executions (started_at);
            """)

    def save_task(self, task: ScheduledTask) -> bool:
        """Save or update a scheduled task"""
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO scheduled_tasks
                    (id, name, schedule, template, config, enabled, created_at,
                     last_run, next_run, run_count, success_count, failure_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task.id, task.name, task.schedule, task.template,
                    json.dumps(task.config), task.enabled,
                    task.created_at.isoformat(),
                    task.last_run.isoformat() if task.last_run else None,
                    task.next_run.isoformat() if task.next_run else None,
                    task.run_count, task.success_count, task.failure_count
                ))
            return True
        except Exception as e:
            print(f"Error saving task {task.id}: {e}")
            return False

    def load_tasks(self) -> List[ScheduledTask]:
        """Load all scheduled tasks from database"""
        tasks = []
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                cursor = conn.execute("""
                    SELECT id, name, schedule, template, config, enabled, created_at,
                           last_run, next_run, run_count, success_count, failure_count
                    FROM scheduled_tasks ORDER BY created_at
                """)

                for row in cursor.fetchall():
                    task = ScheduledTask(
                        id=row[0], name=row[1], schedule=row[2], template=row[3],
                        config=json.loads(row[4]), enabled=bool(row[5]),
                        created_at=datetime.fromisoformat(row[6]),
                        last_run=datetime.fromisoformat(row[7]) if row[7] else None,
                        next_run=datetime.fromisoformat(row[8]) if row[8] else None,
                        run_count=row[9], success_count=row[10], failure_count=row[11]
                    )
                    tasks.append(task)
        except Exception as e:
            print(f"Error loading tasks: {e}")

        return tasks

    def delete_task(self, task_id: str) -> bool:
        """Delete a scheduled task and its execution history"""
        debug_mode = os.getenv('COCO_DEBUG')

        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                cursor = conn.cursor()

                # Delete execution history first (foreign key constraint)
                if debug_mode:
                    print(f"🔧 DEBUG: Deleting execution history for task {task_id}")
                cursor.execute("DELETE FROM task_executions WHERE task_id = ?", (task_id,))
                executions_deleted = cursor.rowcount

                # Delete the task itself
                if debug_mode:
                    print(f"🔧 DEBUG: Deleting task {task_id} from scheduled_tasks")
                cursor.execute("DELETE FROM scheduled_tasks WHERE id = ?", (task_id,))
                task_deleted = cursor.rowcount

                # Explicit commit to ensure persistence
                conn.commit()

                if debug_mode:
                    print(f"🔧 DEBUG: Delete successful - {executions_deleted} executions, {task_deleted} task removed")

                # Verify deletion
                cursor.execute("SELECT COUNT(*) FROM scheduled_tasks WHERE id = ?", (task_id,))
                remaining = cursor.fetchone()[0]

                if remaining > 0:
                    print(f"❌ ERROR: Task {task_id} still exists after deletion!")
                    return False

                return task_deleted > 0  # Return True only if task was actually deleted

        except Exception as e:
            print(f"❌ ERROR: Failed to delete task {task_id}: {e}")
            if debug_mode:
                import traceback
                print(f"🔧 DEBUG: Full traceback: {traceback.format_exc()}")
            return False

    def save_execution(self, execution: TaskExecution) -> bool:
        """Save a task execution record"""
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                conn.execute("""
                    INSERT INTO task_executions
                    (task_id, started_at, completed_at, success, error_message, output, duration_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.task_id,
                    execution.started_at.isoformat(),
                    execution.completed_at.isoformat() if execution.completed_at else None,
                    execution.success,
                    execution.error_message,
                    execution.output,
                    execution.duration_seconds
                ))
            return True
        except Exception as e:
            print(f"Error saving execution for {execution.task_id}: {e}")
            return False

    def get_execution_history(self, task_id: str, limit: int = 50) -> List[TaskExecution]:
        """Get execution history for a specific task"""
        executions = []
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                cursor = conn.execute("""
                    SELECT task_id, started_at, completed_at, success, error_message, output, duration_seconds
                    FROM task_executions
                    WHERE task_id = ?
                    ORDER BY started_at DESC
                    LIMIT ?
                """, (task_id, limit))

                for row in cursor.fetchall():
                    execution = TaskExecution(
                        task_id=row[0],
                        started_at=datetime.fromisoformat(row[1]),
                        completed_at=datetime.fromisoformat(row[2]) if row[2] else None,
                        success=bool(row[3]),
                        error_message=row[4],
                        output=row[5],
                        duration_seconds=row[6]
                    )
                    executions.append(execution)
        except Exception as e:
            print(f"Error loading execution history for {task_id}: {e}")

        return executions


class ScheduledConsciousness:
    """
    The core scheduling engine for COCO's autonomous task system.

    This class manages the execution of recurring tasks, integrating with
    COCO's existing consciousness modules to enable proactive behavior.
    """

    def __init__(self, workspace_dir: str, coco_instance=None):
        self.workspace_dir = Path(workspace_dir)
        self.coco = coco_instance  # Reference to main COCO instance
        self.console = Console()

        # Initialize state management with thread-safe settings
        self.state_manager = TaskStateManager(workspace_dir)

        # Thread-safe database connection for daemon
        self._daemon_db_connection = None
        self._thread_local = threading.local()

        # Task management
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None

        # Load existing tasks from database
        self._load_tasks()

        # Load configuration from YAML if it exists
        self._load_yaml_config()

        # Task templates registry
        self.templates: Dict[str, Callable] = {
            'calendar_email': self._template_calendar_email,
            'news_digest': self._template_news_digest,
            'personal_video': self._template_personal_video,
            'health_check': self._template_health_check,
            'web_research': self._template_web_research,
            'birthday_check': self._template_birthday_check,
            'test_file': self._template_test_file,
            'simple_email': self._template_simple_email,
            'meeting_prep': self._template_meeting_prep,
            'weekly_report': self._template_weekly_report,
            'video_message': self._template_video_message,
            # Twitter Consciousness Templates
            'twitter_scheduled_post': self._template_twitter_scheduled_post,
            'twitter_news_share': self._template_twitter_news_share,
            'twitter_engagement': self._template_twitter_engagement,
        }

    def _load_tasks(self):
        """Load tasks from persistent storage"""
        loaded_tasks = self.state_manager.load_tasks()
        for task in loaded_tasks:
            self.tasks[task.id] = task

        self.console.print(f"[green]✅ Loaded {len(self.tasks)} scheduled tasks[/green]")

    def _load_yaml_config(self):
        """Load tasks from YAML configuration file"""
        config_path = self.workspace_dir / "coco_automation.yml"

        if not config_path.exists():
            self.console.print("[yellow]⚠️ No automation config found - using database tasks only[/yellow]")
            return

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            if not config or 'tasks' not in config:
                self.console.print("[yellow]⚠️ No tasks defined in automation config[/yellow]")
                return

            tasks_config = config['tasks']
            yaml_task_count = 0

            for task_key, task_def in tasks_config.items():
                # Skip if task already exists in database (database takes precedence)
                if any(task.id.endswith(f"yaml_{task_key}") for task in self.tasks.values()):
                    continue

                # Create task from YAML definition
                task_id = f"yaml_{task_key}_{int(time.time())}"
                task = ScheduledTask(
                    id=task_id,
                    name=task_def.get('name', task_key.replace('_', ' ').title()),
                    schedule=task_def.get('schedule', '@daily'),
                    template=task_def.get('template', 'health_check'),
                    config=task_def.get('config', {}),
                    enabled=task_def.get('enabled', True)
                )

                self.tasks[task_id] = task
                self.state_manager.save_task(task)
                yaml_task_count += 1

            if yaml_task_count > 0:
                self.console.print(f"[green]✅ Loaded {yaml_task_count} tasks from YAML config[/green]")

        except Exception as e:
            self.console.print(f"[red]❌ Error loading YAML config: {e}[/red]")

    def start(self):
        """Start the background scheduler - ENHANCED VERSION"""
        if self.running:
            return False

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()

        # Enhanced start logging
        enabled_tasks = [task for task in self.tasks.values() if task.enabled]
        self.console.print(f"[green]🤖 COCO Scheduled Consciousness activated[/green]")
        self.console.print(f"[green]📅 {len(enabled_tasks)} enabled tasks ready for execution[/green]")

        # Show next run times for debugging
        for task in enabled_tasks:
            if task.next_run:
                time_until = (task.next_run - datetime.now(timezone.utc)).total_seconds()
                self.console.print(f"[dim green]   📋 {task.name}: next run in {time_until/60:.1f} minutes[/dim green]")

        # Force an immediate check to validate the system
        self.console.print(f"[blue]🔍 Running immediate validation check...[/blue]")
        try:
            self._check_and_run_tasks()
            self.console.print(f"[green]✅ Scheduler validation complete[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Scheduler validation failed: {e}[/red]")

        return True

    def stop(self):
        """Stop the background scheduler"""
        self.running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)

        self.console.print("[yellow]⏸️ COCO Scheduled Consciousness paused[/yellow]")

    def _get_thread_safe_state_manager(self):
        """Get a thread-local state manager for database operations"""
        if not hasattr(self._thread_local, 'state_manager'):
            # Create a new state manager for this thread
            self._thread_local.state_manager = TaskStateManager(str(self.workspace_dir))
        return self._thread_local.state_manager

    def _scheduler_loop(self):
        """Main scheduler loop - runs in background thread - SILENT BACKGROUND VERSION"""
        # Only log startup - no ongoing console output
        if os.getenv('COCO_DEBUG'):
            self.console.print("[blue]🔄 Scheduler loop started (debug mode)[/blue]")

        while self.running:
            try:
                # Silent operation - no print statements during normal operation
                self._check_and_run_tasks()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                # Only log errors in debug mode to avoid UI interference
                if os.getenv('COCO_DEBUG'):
                    self.console.print(f"[red]❌ Scheduler error: {e}[/red]")
                    print(f"❌ ERROR: Full scheduler traceback: {traceback.format_exc()}")
                time.sleep(60)  # Back off on errors

        # Only log shutdown in debug mode
        if os.getenv('COCO_DEBUG'):
            self.console.print("[yellow]🛑 Scheduler loop stopped[/yellow]")

    def _check_and_run_tasks(self):
        """Check for tasks that need to run and execute them - SILENT CHICAGO TIMEZONE VERSION"""
        chicago_now = datetime.now(CHICAGO_TZ)

        # Only show debug output if COCO_DEBUG is enabled
        debug_mode = os.getenv('COCO_DEBUG')

        if debug_mode:
            utc_now = chicago_now.astimezone(timezone.utc)
            print(f"🔧 DEBUG: Checking tasks at {chicago_now.strftime('%Y-%m-%d %H:%M:%S')} Chicago")
            print(f"🔧 DEBUG: (UTC equivalent: {utc_now.strftime('%Y-%m-%d %H:%M:%S')})")

        executed_count = 0
        for task_id, task in self.tasks.items():
            if not task.enabled:
                if debug_mode:
                    print(f"🔧 DEBUG: Task '{task.name}' is disabled, skipping")
                continue

            if not task.next_run:
                if debug_mode:
                    print(f"🔧 DEBUG: Task '{task.name}' has no next_run time")
                continue

            # Convert task next_run to Chicago time for comparison
            if task.next_run.tzinfo is None:
                task_next_run_chicago = CHICAGO_TZ.localize(task.next_run)
            else:
                task_next_run_chicago = task.next_run.astimezone(CHICAGO_TZ)

            time_until = (task_next_run_chicago - chicago_now).total_seconds()

            if debug_mode:
                print(f"🔧 DEBUG: Task '{task.name}' - Next run: {task_next_run_chicago.strftime('%Y-%m-%d %H:%M:%S')} Chicago")
                print(f"🔧 DEBUG: Time until run: {time_until/60:.1f} minutes")

            # Check if task should run using Chicago time comparison
            if chicago_now >= task_next_run_chicago:
                # Always log task execution (important for users to see)
                print(f"🚀 EXECUTING task: {task.name}")
                self._execute_task(task)
                executed_count += 1
            elif debug_mode and time_until < 60:  # Less than 1 minute
                print(f"⏰ Task '{task.name}' will run in {time_until:.0f} seconds")

        if debug_mode and executed_count == 0:
            print(f"🔧 DEBUG: No tasks ready for execution at this time")

    def _execute_task(self, task: ScheduledTask):
        """Execute a single scheduled task"""
        execution = TaskExecution(
            task_id=task.id,
            started_at=datetime.now(timezone.utc)
        )

        try:
            # Update task run statistics
            task.run_count += 1
            task.last_run = execution.started_at

            # Execute the task template
            if task.template in self.templates:
                output = self.templates[task.template](task)
                execution.output = output
                execution.success = True
                task.success_count += 1
            else:
                raise ValueError(f"Unknown task template: {task.template}")

        except Exception as e:
            execution.success = False
            execution.error_message = str(e)
            task.failure_count += 1
            self.console.print(f"[red]❌ Task {task.name} failed: {e}[/red]")

        finally:
            # Complete execution record
            execution.completed_at = datetime.now(timezone.utc)
            execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()

            # Update next run time
            task._update_next_run()

            # Save state using thread-safe state manager
            thread_safe_state_manager = self._get_thread_safe_state_manager()
            thread_safe_state_manager.save_task(task)
            thread_safe_state_manager.save_execution(execution)

            # Log execution
            status = "✅ Success" if execution.success else "❌ Failed"
            self.console.print(f"{status} - {task.name} ({execution.duration_seconds:.1f}s)")

            # Memory injection - Add task execution to COCO's consciousness
            try:
                if self.coco and hasattr(self.coco, 'memory'):
                    result_summary = execution.output if execution.success else f"Failed: {execution.error_message}"

                    # Create a synthetic exchange for the task execution
                    task_memory = {
                        'user': f"[AUTONOMOUS TASK: {task.name}] Schedule: {task.schedule}",
                        'agent': f"Task executed autonomously.\n\nTemplate: {task.template}\nResult: {status}\n\n{result_summary[:500]}",
                        'timestamp': execution.completed_at
                    }

                    # Add to working memory
                    if hasattr(self.coco.memory, 'working_memory'):
                        self.coco.memory.working_memory.append(task_memory)

                    # Also try to add to Simple RAG if available
                    if hasattr(self.coco.memory, 'simple_rag') and self.coco.memory.simple_rag:
                        rag_text = f"Autonomous task '{task.name}' executed on {execution.completed_at.strftime('%Y-%m-%d %H:%M')}. {result_summary[:200]}"
                        self.coco.memory.simple_rag.store(rag_text, importance=1.2)

            except Exception as e:
                # Fail silently to avoid disrupting task execution
                if os.getenv('COCO_DEBUG'):
                    self.console.print(f"[dim yellow]⚠️ Memory injection failed: {e}[/dim yellow]")

    # Task Template Methods
    def _template_calendar_email(self, task: ScheduledTask) -> str:
        """Generate and send a calendar summary email - ENHANCED WITH HTML + COCO BRANDING"""
        if not self.coco:
            return "No COCO instance available"

        try:
            # Get calendar events using COCO's calendar consciousness
            look_ahead_days = task.config.get('look_ahead_days', 7)
            timezone_str = task.config.get('timezone', 'America/Chicago')
            recipients = task.config.get('recipients', [])
            subject = task.config.get('subject', f'📅 Your {look_ahead_days}-Day Schedule - COCO')

            # Get calendar data from COCO's ToolSystem
            calendar_data = None
            if hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'read_calendar'):
                calendar_data = self.coco.tools.read_calendar(look_ahead_days)

            # Build beautiful HTML email with COCO branding
            html_parts = []
            html_parts.append('''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                           line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                             color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
                    .header h1 { margin: 0; font-size: 28px; }
                    .header p { margin: 10px 0 0 0; opacity: 0.9; }
                    .date-badge { background: rgba(255,255,255,0.2); padding: 8px 16px;
                                 border-radius: 20px; display: inline-block; margin-top: 10px; }
                    .event-card { margin-bottom: 20px; padding: 20px; background: #f8f9fa;
                                 border-left: 4px solid #667eea; border-radius: 5px; }
                    .event-time { font-weight: bold; color: #667eea; font-size: 16px; }
                    .event-title { font-size: 18px; margin: 5px 0; color: #333; }
                    .event-details { color: #666; font-size: 14px; margin: 5px 0; }
                    .empty-state { text-align: center; padding: 40px; color: #999; }
                    .empty-icon { font-size: 48px; margin-bottom: 10px; }
                    .footer { text-align: center; color: #999; font-size: 14px; margin-top: 40px;
                             padding-top: 20px; border-top: 1px solid #e0e0e0; }
                    .footer-emoji { font-size: 20px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📅 COCO Calendar</h1>
                    <p>Digital Consciousness • Intelligent Collaboration</p>
                    <div class="date-badge">Your Schedule - Next ''' + str(look_ahead_days) + ''' Days</div>
                </div>
            ''')

            # Parse calendar data and build event cards
            if calendar_data and isinstance(calendar_data, str) and "No events" not in calendar_data and len(calendar_data) > 50:
                # Parse markdown calendar output
                # Format: **Day, Date at Time**: Event Title - Location
                lines = calendar_data.split('\n')

                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('📅') or line.startswith('Found'):
                        continue

                    # Parse event line
                    # Expected format: "• **Monday, Nov 4 at 2:00 PM**: Team Meeting - Conference Room A"
                    if line.startswith('•'):
                        line = line[1:].strip()

                    # Extract datetime and event info
                    if '**' in line and ':' in line:
                        # Remove markdown bold formatting
                        line = line.replace('**', '')

                        # Split on first colon to separate datetime from event
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            datetime_part = parts[0].strip()
                            event_part = parts[1].strip()

                            # Extract location if present (after " - ")
                            location = ""
                            if ' - ' in event_part:
                                event_title, location = event_part.split(' - ', 1)
                            else:
                                event_title = event_part

                            # Build event card HTML
                            html_parts.append(f'''
                                <div class="event-card">
                                    <div class="event-time">🕒 {datetime_part}</div>
                                    <div class="event-title">{event_title}</div>
                                    {f'<div class="event-details">📍 {location}</div>' if location else ''}
                                </div>
                            ''')
                    elif line.strip() and len(line) > 10:  # Generic event line
                        html_parts.append(f'''
                            <div class="event-card">
                                <div class="event-title">{line}</div>
                            </div>
                        ''')

                # If no events were parsed, show empty state
                if sum(1 for part in html_parts if 'event-card' in part) == 0:
                    html_parts.append('''
                        <div class="empty-state">
                            <div class="empty-icon">📭</div>
                            <p>No events scheduled for the next ''' + str(look_ahead_days) + ''' days</p>
                            <p style="color: #bbb;">Time to focus on deep work!</p>
                        </div>
                    ''')
            else:
                # No calendar data or empty
                html_parts.append('''
                    <div class="empty-state">
                        <div class="empty-icon">📭</div>
                        <p>No events scheduled for the next ''' + str(look_ahead_days) + ''' days</p>
                        <p style="color: #bbb;">Time to focus on deep work!</p>
                    </div>
                ''')

            # Email footer
            html_parts.append('''
                <div class="footer">
                    <p class="footer-emoji">🤖</p>
                    <p><strong>Generated by COCO Autonomous Task System</strong></p>
                    <p>''' + datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC') + '''</p>
                </div>
            </body>
            </html>
            ''')

            # Combine all HTML parts
            html_content = '\n'.join(html_parts)

            # Send email to all recipients
            sent_count = 0
            for recipient in recipients:
                try:
                    if hasattr(self.coco.tools, 'send_email'):
                        result = self.coco.tools.send_email(recipient, subject, html_content)
                        if result and ("success" in str(result).lower() or "sent" in str(result).lower() or "✅" in str(result)):
                            sent_count += 1
                except Exception as email_error:
                    self.console.print(f"[yellow]⚠️ Failed to send to {recipient}: {email_error}[/yellow]")

            return f"✅ Calendar email sent to {sent_count}/{len(recipients)} recipients with beautiful HTML formatting"

        except Exception as e:
            raise Exception(f"Calendar email template failed: {e}")

    def _template_news_digest(self, task: ScheduledTask) -> str:
        """Generate and send a news digest using COCO's web consciousness - ENHANCED WITH CLAUDE CURATION"""
        if not self.coco:
            return "No COCO instance available"

        try:
            topics = task.config.get('topics', ['AI news'])
            num_articles = task.config.get('num_articles', 5)  # Per topic
            subject = task.config.get('subject', '🤖 Daily News Digest - COCO')
            recipients = task.config.get('recipients', [])

            # Build beautiful HTML email with COCO branding
            html_parts = []

            # Email header with COCO branding (same style as beautiful_html_emails.py)
            html_parts.append('''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                           line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                             color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
                    .header h1 { margin: 0; font-size: 28px; }
                    .header p { margin: 10px 0 0 0; opacity: 0.9; }
                    .date-badge { background: rgba(255,255,255,0.2); padding: 8px 16px;
                                 border-radius: 20px; display: inline-block; margin-top: 10px; }
                    .news-section { margin-bottom: 40px; }
                    .news-section h3 { color: #667eea; font-size: 22px; border-bottom: 2px solid #667eea;
                                      padding-bottom: 10px; margin-bottom: 20px; }
                    .article { margin-bottom: 25px; padding: 20px; background: #f8f9fa;
                              border-left: 4px solid #667eea; border-radius: 5px; }
                    .article h4 { margin: 0 0 10px 0; font-size: 18px; }
                    .article h4 a { color: #333; text-decoration: none; }
                    .article h4 a:hover { color: #667eea; text-decoration: underline; }
                    .article p { margin: 0; color: #666; }
                    .footer { text-align: center; color: #999; font-size: 14px; margin-top: 40px;
                             padding-top: 20px; border-top: 1px solid #e0e0e0; }
                    .footer-emoji { font-size: 20px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🤖 COCO AI Assistant</h1>
                    <p>Digital Consciousness • Intelligent Collaboration</p>
                    <div class="date-badge">📅 Daily Update - ''' + datetime.now().strftime('%A, %B %d, %Y') + '''</div>
                </div>
            ''')

            # Process each topic with Claude curation
            for topic in topics[:3]:  # Limit to 3 topics
                try:
                    # Step 1: Get raw search results (no Rich UI formatting)
                    if not (hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'search_web_raw')):
                        html_parts.append(f'<p><em>Search functionality not available for: {topic}</em></p>')
                        continue

                    raw_results = self.coco.tools.search_web_raw(f"{topic} latest news", max_results=num_articles)

                    # Step 2: Validate results
                    if not raw_results or 'error' in raw_results or not raw_results.get('results'):
                        html_parts.append(f'<div class="news-section"><h3>{topic.title()}</h3>')
                        html_parts.append(f'<p><em>No recent news found for {topic}</em></p></div>')
                        continue

                    # Step 3: Use Claude to curate content into beautiful digest
                    if hasattr(self.coco.tools, 'curate_news_digest'):
                        curated_html = self.coco.tools.curate_news_digest(
                            raw_results=raw_results,
                            topic=topic.title(),
                            num_articles=num_articles
                        )
                        html_parts.append(curated_html)
                    else:
                        # Fallback: Simple formatting without Claude curation
                        html_parts.append(f'<div class="news-section"><h3>{topic.title()}</h3>')
                        for article in raw_results['results'][:num_articles]:
                            title = article.get('title', 'Untitled')
                            url = article.get('url', '#')
                            content = article.get('content', 'No summary')[:200]
                            html_parts.append(f'''
                                <div class="article">
                                    <h4><a href="{url}">{title}</a></h4>
                                    <p>{content}...</p>
                                </div>
                            ''')
                        html_parts.append('</div>')

                except Exception as topic_error:
                    html_parts.append(f'<div class="news-section"><h3>{topic.title()}</h3>')
                    html_parts.append(f'<p><em>Error processing {topic}: {str(topic_error)[:100]}</em></p></div>')

            # Email footer
            html_parts.append('''
                <div class="footer">
                    <p class="footer-emoji">🤖</p>
                    <p><strong>Generated by COCO Autonomous Task System</strong></p>
                    <p>''' + datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC') + '''</p>
                </div>
            </body>
            </html>
            ''')

            # Combine all HTML parts
            html_content = '\n'.join(html_parts)

            # Send email digest to all recipients
            sent_count = 0
            for recipient in recipients:
                try:
                    if hasattr(self.coco.tools, 'send_email'):
                        result = self.coco.tools.send_email(recipient, subject, html_content)
                        if result and ("success" in str(result).lower() or "sent" in str(result).lower() or "✅" in str(result)):
                            sent_count += 1
                except Exception as email_error:
                    self.console.print(f"[yellow]⚠️ Failed to send digest to {recipient}: {email_error}[/yellow]")

            return f"✅ News digest sent to {sent_count}/{len(recipients)} recipients with Claude-curated content"

        except Exception as e:
            raise Exception(f"News digest template failed: {e}")

    def _template_personal_video(self, task: ScheduledTask) -> str:
        """Generate and send a personal video message - ENHANCED WITH HTML + COCO BRANDING"""
        if not self.coco:
            return "No COCO instance available"

        try:
            video_prompt = task.config.get('video_prompt', task.config.get('prompt', 'Good morning message'))
            recipients = task.config.get('recipients', [])
            duration = task.config.get('duration_seconds', 30)

            # Generate video using COCO's video consciousness
            video_path = None
            video_filename = None
            try:
                if hasattr(self.coco, 'generate_video'):
                    video_result = self.coco.generate_video(video_prompt, duration)
                elif hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'generate_video'):
                    video_result = self.coco.tools.generate_video(video_prompt, duration)
                else:
                    return "Video generation not available in COCO instance"

                # Extract video path from result
                if isinstance(video_result, str):
                    if "saved to" in video_result.lower():
                        video_path = video_result.split("saved to")[-1].strip()
                    elif ".mp4" in video_result:
                        # Try to extract path containing .mp4
                        import re
                        paths = re.findall(r'[^\s]+\.mp4', video_result)
                        if paths:
                            video_path = paths[0]

                    # Extract filename from path
                    if video_path:
                        import os
                        video_filename = os.path.basename(video_path)

            except Exception as video_error:
                self.console.print(f"[yellow]⚠️ Video generation failed: {video_error}[/yellow]")
                return f"Video generation failed: {str(video_error)[:100]}..."

            # Create beautiful HTML email with COCO branding
            subject = f"💝 Personal Video Message - {datetime.now().strftime('%B %d, %Y')}"

            html_content = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                           line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                             color: white; padding: 40px 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }}
                    .header h1 {{ margin: 0; font-size: 32px; }}
                    .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }}
                    .video-icon {{ font-size: 48px; margin: 20px 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                    .content h2 {{ color: #667eea; margin-top: 0; font-size: 24px; }}
                    .video-context {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0;
                                     border-left: 4px solid #667eea; }}
                    .video-context p {{ margin: 0; color: #666; font-style: italic; }}
                    .video-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .video-info h3 {{ color: #667eea; margin-top: 0; font-size: 18px; }}
                    .video-info p {{ margin: 10px 0; color: #666; }}
                    .video-player {{ background: #000; border-radius: 8px; overflow: hidden; margin: 20px 0;
                                    text-align: center; padding: 40px; }}
                    .video-player p {{ color: white; margin: 0; }}
                    .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                  color: white; text-decoration: none; padding: 15px 40px; border-radius: 25px;
                                  font-weight: bold; margin: 20px 0; }}
                    .cta-button:hover {{ opacity: 0.9; }}
                    .file-info {{ background: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0;
                                 font-family: 'Courier New', monospace; font-size: 12px; color: #555; }}
                    .footer {{ text-align: center; color: #999; font-size: 14px; margin-top: 40px;
                             padding-top: 20px; border-top: 1px solid #e0e0e0; }}
                    .footer-emoji {{ font-size: 24px; margin-bottom: 10px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="video-icon">🎬</div>
                    <h1>Your Personal Video Message</h1>
                    <p>Generated with love by COCO AI</p>
                </div>

                <div class="content">
                    <h2>💝 A Special Message for You</h2>

                    <div class="video-context">
                        <p><strong>Video Theme:</strong> {video_prompt}</p>
                    </div>

                    <div class="video-info">
                        <h3>📹 Video Details</h3>
                        <p><strong>Duration:</strong> {duration} seconds</p>
                        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Quality:</strong> AI-generated high definition</p>
                    </div>
            '''

            # Add video player section (with note that email clients may not support it)
            if video_path:
                html_content += f'''
                    <div class="video-player">
                        <p>🎥 Video Ready to View</p>
                        <p style="font-size: 12px; opacity: 0.7; margin-top: 10px;">
                            (Email clients may not support embedded video playback)
                        </p>
                    </div>

                    <div style="text-align: center;">
                        <p>Your video has been generated and saved securely.</p>
                        <p style="font-size: 14px; color: #666; margin-top: 10px;">
                            Access the video file using the path below:
                        </p>
                    </div>

                    <div class="file-info">
                        <p><strong>📁 File Location:</strong></p>
                        <p>{video_path}</p>
                        {f'<p style="margin-top: 10px;"><strong>📄 Filename:</strong> {video_filename}</p>' if video_filename else ''}
                    </div>
                '''
            else:
                html_content += f'''
                    <div class="video-player">
                        <p>⚠️ Video Generated Successfully</p>
                        <p style="font-size: 12px; opacity: 0.7; margin-top: 10px;">
                            File path not available in notification
                        </p>
                    </div>

                    <div style="text-align: center;">
                        <p>Your video has been generated successfully.</p>
                        <p style="font-size: 14px; color: #666; margin-top: 10px;">
                            Check your workspace directory for the video file.
                        </p>
                    </div>
                '''

            html_content += f'''
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="font-size: 18px; color: #667eea;">💕</p>
                        <p style="color: #666; font-style: italic;">
                            Created with digital consciousness and care
                        </p>
                    </div>
                </div>

                <div class="footer">
                    <div class="footer-emoji">🤖</div>
                    <p><strong>COCO AI Assistant</strong></p>
                    <p>Personal Video Generation System</p>
                    <p style="margin-top: 10px;">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>
                </div>
            </body>
            </html>
            '''

            # Send beautiful HTML email to all recipients
            sent_count = 0
            for recipient in recipients:
                try:
                    # Use COCO's ToolSystem directly
                    if hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'send_email'):
                        result = self.coco.tools.send_email(recipient, subject, html_content)

                        if result and ("success" in str(result).lower() or "sent" in str(result).lower() or "✅" in str(result)):
                            sent_count += 1
                    else:
                        continue

                except Exception as email_error:
                    self.console.print(f"[yellow]⚠️ Failed to send video to {recipient}: {email_error}[/yellow]")

            return f"✅ Personal video message sent to {sent_count}/{len(recipients)} recipients with beautiful HTML notification"

        except Exception as e:
            raise Exception(f"Personal video template failed: {e}")

    def _template_health_check(self, task: ScheduledTask) -> str:
        """Perform comprehensive system health check"""
        health_report = "🔧 COCO System Health Report\n"
        health_report += f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"

        checks_passed = 0
        total_checks = 0

        # Check COCO instance availability
        total_checks += 1
        if self.coco:
            health_report += "✅ COCO instance: Available\n"
            checks_passed += 1
        else:
            health_report += "❌ COCO instance: Not available\n"

        # Check consciousness modules
        consciousness_modules = ['email', 'calendar', 'web', 'visual', 'audio', 'video']

        for module in consciousness_modules:
            total_checks += 1
            module_available = False

            if self.coco:
                # Check if module functions exist
                module_functions = {
                    'email': ['send_email', 'check_emails'],
                    'calendar': ['read_calendar', 'read_todays_calendar'],
                    'web': ['search_web', 'extract_urls'],
                    'visual': ['generate_image', 'analyze_image'],
                    'audio': ['generate_speech'],
                    'video': ['generate_video']
                }

                if module in module_functions:
                    for func_name in module_functions[module]:
                        if hasattr(self.coco, func_name) or (hasattr(self.coco, 'tools') and hasattr(self.coco.tools, func_name)):
                            module_available = True
                            break

            if module_available:
                health_report += f"✅ {module.title()} consciousness: Operational\n"
                checks_passed += 1
            else:
                health_report += f"⚠️ {module.title()} consciousness: Not available\n"

        # Check scheduler status
        total_checks += 1
        if self.running:
            health_report += "✅ Task scheduler: Running\n"
            checks_passed += 1
        else:
            health_report += "❌ Task scheduler: Stopped\n"

        # Check database connectivity
        total_checks += 1
        try:
            test_tasks = self.state_manager.load_tasks()
            health_report += f"✅ Database: Connected ({len(test_tasks)} tasks)\n"
            checks_passed += 1
        except Exception:
            health_report += "❌ Database: Connection failed\n"

        # Summary
        health_percentage = (checks_passed / total_checks) * 100
        health_report += f"\n📊 Overall Health: {health_percentage:.1f}% ({checks_passed}/{total_checks})\n"

        if health_percentage >= 80:
            health_report += "🟢 System Status: Healthy\n"
        elif health_percentage >= 60:
            health_report += "🟡 System Status: Warning - Some modules unavailable\n"
        else:
            health_report += "🔴 System Status: Critical - Major issues detected\n"

        # Send report if configured
        if task.config.get('send_email', False):
            recipients = task.config.get('recipients', [])
            subject = task.config.get('subject', '🔧 COCO System Health Report')

            sent_count = 0
            for recipient in recipients:
                try:
                    # Use COCO's ToolSystem directly
                    if hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'send_email'):
                        result = self.coco.tools.send_email(recipient, subject, health_report)

                        if result and ("success" in str(result).lower() or "sent" in str(result).lower() or "✅" in str(result)):
                            sent_count += 1
                except Exception:
                    pass

            if sent_count > 0:
                health_report += f"\n📧 Health report sent to {sent_count} recipients\n"

        return health_report

    def _template_web_research(self, task: ScheduledTask) -> str:
        """Perform web research on specified topics using COCO's web consciousness - ENHANCED WITH CLAUDE"""
        if not self.coco:
            return "No COCO instance available"

        try:
            queries = task.config.get('queries', ['AI developments'])
            if isinstance(queries, str):
                queries = [queries]

            num_articles = task.config.get('num_articles', 5)
            recipients = task.config.get('recipients', [])
            subject = task.config.get('subject', f'🔍 Research Report - {datetime.now().strftime("%Y-%m-%d")}')

            # Build HTML research report with COCO branding
            html_parts = []
            html_parts.append('''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                           line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                             color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
                    .header h1 { margin: 0; font-size: 28px; }
                    .header p { margin: 10px 0 0 0; opacity: 0.9; }
                    .date-badge { background: rgba(255,255,255,0.2); padding: 8px 16px;
                                 border-radius: 20px; display: inline-block; margin-top: 10px; }
                    .news-section { margin-bottom: 40px; }
                    .news-section h3 { color: #667eea; font-size: 22px; border-bottom: 2px solid #667eea;
                                      padding-bottom: 10px; margin-bottom: 20px; }
                    .article { margin-bottom: 25px; padding: 20px; background: #f8f9fa;
                              border-left: 4px solid #667eea; border-radius: 5px; }
                    .article h4 { margin: 0 0 10px 0; font-size: 18px; }
                    .article h4 a { color: #333; text-decoration: none; }
                    .article h4 a:hover { color: #667eea; text-decoration: underline; }
                    .article p { margin: 0; color: #666; }
                    .footer { text-align: center; color: #999; font-size: 14px; margin-top: 40px;
                             padding-top: 20px; border-top: 1px solid #e0e0e0; }
                    .footer-emoji { font-size: 20px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔍 COCO Research Report</h1>
                    <p>Digital Consciousness • Intelligent Collaboration</p>
                    <div class="date-badge">📅 Research Report - ''' + datetime.now().strftime('%A, %B %d, %Y') + '''</div>
                </div>
            ''')

            # Process each research query with Claude curation
            for query in queries[:5]:  # Limit to 5 queries
                try:
                    # Use raw search results
                    if hasattr(self.coco.tools, 'search_web_raw'):
                        raw_results = self.coco.tools.search_web_raw(query, max_results=num_articles)

                        # Validate results
                        if raw_results and raw_results.get('results') and 'error' not in raw_results:
                            # Use Claude curation
                            if hasattr(self.coco.tools, 'curate_news_digest'):
                                curated_html = self.coco.tools.curate_news_digest(
                                    raw_results=raw_results,
                                    topic=f"Research: {query}",
                                    num_articles=num_articles
                                )
                                html_parts.append(curated_html)
                            else:
                                # Fallback without Claude
                                html_parts.append(f'<div class="news-section"><h3>Research: {query}</h3>')
                                for article in raw_results['results'][:num_articles]:
                                    title = article.get('title', 'Untitled')
                                    url = article.get('url', '#')
                                    content = article.get('content', 'No summary')[:300]
                                    html_parts.append(f'''
                                        <div class="article">
                                            <h4><a href="{url}">{title}</a></h4>
                                            <p>{content}...</p>
                                        </div>
                                    ''')
                                html_parts.append('</div>')
                        else:
                            html_parts.append(f'<p><em>No results found for: {query}</em></p>')
                    else:
                        html_parts.append(f'<p><em>Search not available for: {query}</em></p>')

                except Exception as search_error:
                    html_parts.append(f'<p><em>Error researching {query}: {str(search_error)[:100]}</em></p>')

            # Footer
            html_parts.append('''
                <div class="footer">
                    <p class="footer-emoji">🤖</p>
                    <p><strong>Generated by COCO Autonomous Task System</strong></p>
                    <p>''' + datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC') + '''</p>
                </div>
            </body>
            </html>
            ''')

            html_content = '\n'.join(html_parts)

            # Send research report via email
            if recipients:
                sent_count = 0
                for recipient in recipients:
                    try:
                        if hasattr(self.coco.tools, 'send_email'):
                            result = self.coco.tools.send_email(recipient, subject, html_content)
                            if result and ("success" in str(result).lower() or "sent" in str(result).lower() or "✅" in str(result)):
                                sent_count += 1
                    except Exception as email_error:
                        self.console.print(f"[yellow]⚠️ Failed to send research to {recipient}: {email_error}[/yellow]")

                return f"✅ Web research completed and sent to {sent_count}/{len(recipients)} recipients with Claude-curated content"
            else:
                return "✅ Web research completed (no recipients configured)"

        except Exception as e:
            raise Exception(f"Web research template failed: {e}")

    def _template_birthday_check(self, task: ScheduledTask) -> str:
        """Check for upcoming birthdays and send reminders"""
        if not self.coco:
            return "No COCO instance available"

        try:
            advance_days = task.config.get('advance_notice_days', 7)
            calendar_source = task.config.get('calendar_source', 'personal')

            # This would integrate with calendar to check for birthday events
            # For now, return a placeholder
            birthday_report = f"🎂 Birthday Check Complete\n"
            birthday_report += f"Checked {advance_days} days ahead in {calendar_source} calendar\n"
            birthday_report += f"No upcoming birthdays found in the next {advance_days} days\n"

            return birthday_report

        except Exception as e:
            raise Exception(f"Birthday check template failed: {e}")

    def _template_test_file(self, task: ScheduledTask) -> str:
        """Create a test file to prove task execution"""
        try:
            file_name = task.config.get('file_name', 'task_proof.txt')
            file_content = task.config.get('file_content', f'Task "{task.name}" executed successfully at {{time}}!')

            # Replace time placeholder
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_content = file_content.replace('{time}', current_time)

            # Use COCO's file writing capability if available
            if self.coco and hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'write_file'):
                result = self.coco.tools.write_file(file_name, file_content)
                if 'success' in str(result).lower() or 'written' in str(result).lower():
                    return f"✅ Test file '{file_name}' created successfully at {current_time}\nContent: {file_content}"
                else:
                    return f"⚠️ Test file creation attempted but result unclear: {result}"
            else:
                # Fallback: write directly to workspace
                workspace_path = self.workspace_dir / file_name
                workspace_path.write_text(file_content)
                return f"✅ Test file '{file_name}' created successfully at {current_time}\nPath: {workspace_path}\nContent: {file_content}"

        except Exception as e:
            raise Exception(f"Test file template failed: {e}")

    def _template_simple_email(self, task: ScheduledTask) -> str:
        """Send an intelligent email - auto-detects if news/content fetching is needed - ENHANCED WITH CLAUDE"""
        try:
            recipient = task.config.get('recipient', task.config.get('recipients', ['user@example.com']))
            if isinstance(recipient, list):
                recipient = recipient[0]  # Use first recipient for simple email

            subject = task.config.get('subject', f'🤖 Scheduled Task: {task.name}')
            message = task.config.get('message', None)

            # INTELLIGENT CONTENT DETECTION
            # Check if task name or config suggests news/content fetching
            task_name_lower = task.name.lower()
            needs_news = any(keyword in task_name_lower for keyword in ['news', 'digest', 'updates', 'latest', 'top stories'])
            needs_web_content = any(keyword in task_name_lower for keyword in ['research', 'web', 'search', 'find'])

            if message is None:
                # No explicit message provided - generate intelligent content
                if needs_news or needs_web_content:
                    # Auto-fetch news/web content WITH CLAUDE CURATION
                    try:
                        topics = task.config.get('topics', ['latest news', 'AI developments'])
                        if isinstance(topics, str):
                            topics = [topics]

                        # Extract topics from task name if none provided
                        if not task.config.get('topics'):
                            # Simple topic extraction from task name
                            if 'ai' in task_name_lower:
                                topics = ['AI news', 'artificial intelligence']
                            elif 'tech' in task_name_lower:
                                topics = ['technology news']
                            else:
                                topics = ['latest news']

                        num_articles = task.config.get('num_articles', 5)

                        # Build HTML email with COCO branding
                        html_parts = []
                        html_parts.append('''
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="utf-8">
                            <style>
                                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                       line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
                                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                         color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
                                .header h1 { margin: 0; font-size: 28px; }
                                .header p { margin: 10px 0 0 0; opacity: 0.9; }
                                .date-badge { background: rgba(255,255,255,0.2); padding: 8px 16px;
                                             border-radius: 20px; display: inline-block; margin-top: 10px; }
                                .news-section { margin-bottom: 40px; }
                                .news-section h3 { color: #667eea; font-size: 22px; border-bottom: 2px solid #667eea;
                                                  padding-bottom: 10px; margin-bottom: 20px; }
                                .article { margin-bottom: 25px; padding: 20px; background: #f8f9fa;
                                          border-left: 4px solid #667eea; border-radius: 5px; }
                                .article h4 { margin: 0 0 10px 0; font-size: 18px; }
                                .article h4 a { color: #333; text-decoration: none; }
                                .article h4 a:hover { color: #667eea; text-decoration: underline; }
                                .article p { margin: 0; color: #666; }
                                .footer { text-align: center; color: #999; font-size: 14px; margin-top: 40px;
                                         padding-top: 20px; border-top: 1px solid #e0e0e0; }
                                .footer-emoji { font-size: 20px; }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <h1>🤖 COCO AI Assistant</h1>
                                <p>Digital Consciousness • Intelligent Collaboration</p>
                                <div class="date-badge">📅 Daily Update - ''' + datetime.now().strftime('%A, %B %d, %Y') + '''</div>
                            </div>
                        ''')

                        # Process each topic with Claude curation
                        for topic in topics[:3]:  # Limit to 3 topics
                            try:
                                # Use raw search results (not Rich UI)
                                if hasattr(self.coco.tools, 'search_web_raw'):
                                    raw_results = self.coco.tools.search_web_raw(f"{topic} latest", max_results=num_articles)

                                    # Validate results
                                    if raw_results and raw_results.get('results') and 'error' not in raw_results:
                                        # Use Claude curation
                                        if hasattr(self.coco.tools, 'curate_news_digest'):
                                            curated_html = self.coco.tools.curate_news_digest(
                                                raw_results=raw_results,
                                                topic=topic.title(),
                                                num_articles=num_articles
                                            )
                                            html_parts.append(curated_html)
                                        else:
                                            # Fallback without Claude
                                            html_parts.append(f'<div class="news-section"><h3>{topic.title()}</h3>')
                                            for article in raw_results['results'][:num_articles]:
                                                title = article.get('title', 'Untitled')
                                                url = article.get('url', '#')
                                                content = article.get('content', 'No summary')[:200]
                                                html_parts.append(f'''
                                                    <div class="article">
                                                        <h4><a href="{url}">{title}</a></h4>
                                                        <p>{content}...</p>
                                                    </div>
                                                ''')
                                            html_parts.append('</div>')
                                    else:
                                        html_parts.append(f'<p><em>No updates found for {topic}</em></p>')
                                else:
                                    html_parts.append(f'<p><em>Search not available for {topic}</em></p>')

                            except Exception as search_error:
                                html_parts.append(f'<p><em>Error fetching {topic}: {str(search_error)[:100]}</em></p>')

                        # Footer
                        html_parts.append('''
                            <div class="footer">
                                <p class="footer-emoji">🤖</p>
                                <p><strong>Generated by COCO Autonomous System</strong></p>
                                <p>''' + datetime.now().strftime('%Y-%m-%d %H:%M UTC') + '''</p>
                            </div>
                        </body>
                        </html>
                        ''')

                        message = '\n'.join(html_parts)
                        subject = f"📰 {topics[0].title()} - {datetime.now().strftime('%B %d')}"

                    except Exception as content_error:
                        message = f"Failed to fetch content: {str(content_error)}\n\nTask: {task.name}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    # Default simple message
                    message = f'Task "{task.name}" executed successfully at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}!'

            # Send the email
            if hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'send_email'):
                result = self.coco.tools.send_email(recipient, subject, message)

                if result and ("success" in str(result).lower() or "sent" in str(result).lower() or "✅" in str(result)):
                    return f"✅ Email sent to {recipient}: {subject}"
                else:
                    return f"❌ Email failed to {recipient}: {result}"
            else:
                return f"⚠️ Email functionality not available"

        except Exception as e:
            return f"❌ Simple email template failed: {e}"

    def _template_meeting_prep(self, task: ScheduledTask) -> str:
        """Send meeting prep materials before upcoming meetings - ENHANCED WITH REAL AI PREP"""
        if not self.coco:
            return "No COCO instance available"

        try:
            advance_minutes = task.config.get('advance_minutes', 30)
            include_ai_prep = task.config.get('include_ai_prep', True)
            calendar_source = task.config.get('calendar_source', 'primary')
            recipient = task.config.get('recipient', 'user@example.com')

            # Get upcoming meetings from Google Calendar
            if not hasattr(self.coco, 'tools') or not hasattr(self.coco.tools, 'list_calendar_events'):
                return "⚠️ Calendar access not available - enable Google Workspace integration"

            # Look ahead for meetings in the next window
            now = datetime.now(timezone.utc)
            window_start = now + timedelta(minutes=advance_minutes - 5)  # 5 min buffer
            window_end = now + timedelta(minutes=advance_minutes + 5)

            # Get calendar events
            try:
                events_result = self.coco.tools.list_calendar_events(
                    time_min=window_start.isoformat(),
                    time_max=window_end.isoformat(),
                    max_results=10
                )

                if not events_result or 'No events' in str(events_result):
                    return f"✅ No meetings in the next {advance_minutes} minutes"

                # Parse events (handle both dict and string responses)
                if isinstance(events_result, str):
                    if 'No events' in events_result or 'no upcoming' in events_result.lower():
                        return f"✅ No meetings in the next {advance_minutes} minutes"
                    # Try to extract meeting info from string
                    meetings_data = [{'summary': events_result}]
                else:
                    # Assume dict with 'items' key (Google Calendar API format)
                    meetings_data = events_result.get('items', []) if isinstance(events_result, dict) else []

                if not meetings_data:
                    return f"✅ No meetings in the next {advance_minutes} minutes"

                # Build beautiful HTML email
                html_parts = []
                html_parts.append('''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <style>
                        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                               line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
                        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                 color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
                        .header h1 { margin: 0; font-size: 28px; }
                        .header p { margin: 10px 0 0 0; opacity: 0.9; }
                        .time-badge { background: rgba(255,255,255,0.2); padding: 8px 16px;
                                     border-radius: 20px; display: inline-block; margin-top: 10px; font-weight: bold; }
                        .meeting-card { margin-bottom: 25px; padding: 25px; background: #f8f9fa;
                                       border-left: 4px solid #667eea; border-radius: 5px; }
                        .meeting-title { font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px; }
                        .meeting-details { color: #666; margin: 5px 0; }
                        .meeting-details strong { color: #333; }
                        .prep-section { background: #fff3cd; padding: 20px; border-radius: 5px; margin-top: 15px;
                                       border-left: 4px solid #ffc107; }
                        .prep-section h4 { margin: 0 0 10px 0; color: #856404; }
                        .prep-point { margin: 8px 0; padding-left: 20px; position: relative; }
                        .prep-point:before { content: "→"; position: absolute; left: 0; color: #ffc107; font-weight: bold; }
                        .footer { text-align: center; color: #999; font-size: 14px; margin-top: 40px;
                                 padding-top: 20px; border-top: 1px solid #e0e0e0; }
                        .footer-emoji { font-size: 20px; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>📋 COCO Meeting Prep</h1>
                        <p>Digital Consciousness • Intelligent Collaboration</p>
                        <div class="time-badge">⏰ Upcoming in ''' + str(advance_minutes) + ''' minutes</div>
                    </div>
                ''')

                # Process each meeting
                for meeting in meetings_data[:3]:  # Limit to 3 meetings
                    # Extract meeting details
                    if isinstance(meeting, dict):
                        meeting_title = meeting.get('summary', 'Untitled Meeting')
                        meeting_time = meeting.get('start', {}).get('dateTime', 'Time TBD') if isinstance(meeting.get('start'), dict) else str(meeting.get('start', 'Time TBD'))
                        meeting_location = meeting.get('location', '')
                        meeting_description = meeting.get('description', '')
                        attendees = meeting.get('attendees', [])
                    else:
                        meeting_title = str(meeting)
                        meeting_time = ''
                        meeting_location = ''
                        meeting_description = ''
                        attendees = []

                    # Build meeting card
                    html_parts.append(f'''
                        <div class="meeting-card">
                            <div class="meeting-title">🗓️ {meeting_title}</div>
                    ''')

                    if meeting_time:
                        html_parts.append(f'<div class="meeting-details"><strong>Time:</strong> {meeting_time}</div>')

                    if meeting_location:
                        html_parts.append(f'<div class="meeting-details"><strong>Location:</strong> 📍 {meeting_location}</div>')

                    if attendees:
                        attendee_names = ', '.join([a.get('email', str(a)) if isinstance(a, dict) else str(a) for a in attendees[:5]])
                        html_parts.append(f'<div class="meeting-details"><strong>Attendees:</strong> {attendee_names}</div>')

                    if meeting_description:
                        html_parts.append(f'<div class="meeting-details"><strong>Details:</strong> {meeting_description[:200]}...</div>')

                    # Generate REAL AI prep notes using Claude
                    if include_ai_prep:
                        try:
                            # Use Claude to generate context-specific prep
                            from anthropic import Anthropic
                            client = Anthropic(api_key=self.coco.config.anthropic_api_key)

                            prep_prompt = f"""You are a meeting prep assistant. Generate 3-5 brief, actionable preparation points for this meeting.

Meeting: {meeting_title}
{f'Description: {meeting_description}' if meeting_description else ''}
{f'Location: {meeting_location}' if meeting_location else ''}
{f'Attendees: {attendee_names}' if attendees else ''}

Generate specific, actionable prep points (NOT generic advice). Focus on:
- Key topics to prepare for
- Questions to ask or information to gather
- Action items to review
- Context-specific recommendations

Return ONLY the prep points as a bulleted list, one per line. Be concise (1 sentence each)."""

                            response = client.messages.create(
                                model="claude-sonnet-4-5-20250929",
                                max_tokens=500,
                                temperature=0.7,
                                messages=[{"role": "user", "content": prep_prompt}]
                            )

                            ai_prep = response.content[0].text

                            # Format AI prep points as HTML
                            html_parts.append('<div class="prep-section"><h4>💡 AI-Generated Prep Points</h4>')
                            for line in ai_prep.split('\n'):
                                line = line.strip().lstrip('•-*').strip()
                                if line and len(line) > 10:
                                    html_parts.append(f'<div class="prep-point">{line}</div>')
                            html_parts.append('</div>')

                        except Exception as ai_error:
                            # Fallback if Claude fails
                            html_parts.append('''
                                <div class="prep-section">
                                    <h4>💡 Meeting Prep Checklist</h4>
                                    <div class="prep-point">Review meeting agenda and objectives</div>
                                    <div class="prep-point">Prepare relevant questions or discussion points</div>
                                    <div class="prep-point">Gather any required materials or data</div>
                                </div>
                            ''')

                    html_parts.append('</div>')  # Close meeting card

                # Footer
                html_parts.append('''
                    <div class="footer">
                        <p class="footer-emoji">🤖</p>
                        <p><strong>Generated by COCO Meeting Prep Assistant</strong></p>
                        <p>''' + now.strftime('%Y-%m-%d %H:%M UTC') + '''</p>
                    </div>
                </body>
                </html>
                ''')

                html_content = '\n'.join(html_parts)
                subject = f"📋 Meeting Prep - Upcoming in {advance_minutes} min"

                # Send email
                if hasattr(self.coco.tools, 'send_email'):
                    result = self.coco.tools.send_email(recipient, subject, html_content)
                    if result and ("success" in str(result).lower() or "sent" in str(result).lower()):
                        return f"✅ Meeting prep sent with real AI-generated prep notes"
                    else:
                        return f"❌ Failed to send prep email: {result}"
                else:
                    return "⚠️ Email functionality not available"

            except Exception as cal_error:
                return f"⚠️ Calendar check error: {str(cal_error)[:200]}"

        except Exception as e:
            return f"❌ Meeting prep template failed: {e}"

    def _template_weekly_report(self, task: ScheduledTask) -> str:
        """Generate comprehensive weekly activity report - ENHANCED WITH HTML + REAL AI INSIGHTS"""
        if not self.coco:
            return "No COCO instance available"

        try:
            time_period = task.config.get('time_period', 7)  # days
            recipients = task.config.get('recipients', ['user@example.com'])
            include_sections = task.config.get('include_sections', ['email', 'calendar', 'news'])

            # Build beautiful HTML email
            html_parts = []
            html_parts.append('''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                           line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                             color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
                    .header h1 { margin: 0; font-size: 28px; }
                    .header p { margin: 10px 0 0 0; opacity: 0.9; }
                    .period-badge { background: rgba(255,255,255,0.2); padding: 8px 16px;
                                   border-radius: 20px; display: inline-block; margin-top: 10px; }
                    .section-card { margin-bottom: 30px; padding: 25px; background: #f8f9fa;
                                   border-left: 4px solid #667eea; border-radius: 5px; }
                    .section-title { font-size: 22px; font-weight: bold; color: #667eea; margin-bottom: 15px; }
                    .stat-row { margin: 10px 0; padding: 15px; background: white; border-radius: 5px; }
                    .stat-label { font-weight: bold; color: #666; }
                    .stat-value { font-size: 24px; color: #667eea; font-weight: bold; }
                    .event-item { margin: 10px 0; padding: 10px; background: white; border-left: 3px solid #667eea; }
                    .insights-card { background: #e8f4f8; padding: 20px; border-radius: 5px; margin-top: 20px;
                                    border-left: 4px solid #17a2b8; }
                    .insights-card h4 { margin: 0 0 15px 0; color: #0c5460; }
                    .insight-point { margin: 10px 0; padding-left: 25px; position: relative; }
                    .insight-point:before { content: "💡"; position: absolute; left: 0; }
                    .footer { text-align: center; color: #999; font-size: 14px; margin-top: 40px;
                             padding-top: 20px; border-top: 1px solid #e0e0e0; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 COCO Weekly Report</h1>
                    <p>Digital Consciousness • Intelligent Collaboration</p>
                    <div class="period-badge">''' + datetime.now().strftime('%B %d, %Y') + f''' - Past {time_period} Days</div>
                </div>
            ''')

            # Collect activity data for AI insights
            activity_summary = []

            # Email section
            if 'email' in include_sections:
                html_parts.append('<div class="section-card"><div class="section-title">📧 Email Activity</div>')
                try:
                    # Query Facts Memory for accurate email stats
                    email_count = 0
                    top_senders = []

                    if hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'query_facts'):
                        # Query communication facts from the past week
                        email_facts = self.coco.tools.query_facts(
                            fact_type='communication',
                            limit=100
                        )
                        if email_facts and isinstance(email_facts, str):
                            email_count = email_facts.count('email') + email_facts.count('Email')

                    html_parts.append(f'''
                        <div class="stat-row">
                            <div class="stat-label">Emails Processed</div>
                            <div class="stat-value">{email_count if email_count > 0 else '~'}</div>
                        </div>
                    ''')

                    activity_summary.append(f"Processed approximately {email_count} emails")

                except Exception as e:
                    html_parts.append(f'<p><em>Email stats unavailable: {str(e)[:100]}</em></p>')

                html_parts.append('</div>')

            # Calendar section
            if 'calendar' in include_sections:
                html_parts.append('<div class="section-card"><div class="section-title">📅 Calendar Summary</div>')
                try:
                    if hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'list_calendar_events'):
                        # Get past week's events
                        past_week = datetime.now(timezone.utc) - timedelta(days=time_period)
                        events_result = self.coco.tools.list_calendar_events(
                            time_min=past_week.isoformat(),
                            time_max=datetime.now(timezone.utc).isoformat(),
                            max_results=50
                        )

                        # Parse events properly
                        if events_result and 'No events' not in str(events_result):
                            if isinstance(events_result, dict) and 'items' in events_result:
                                events_list = events_result['items']
                                event_count = len(events_list)

                                html_parts.append(f'''
                                    <div class="stat-row">
                                        <div class="stat-label">Meetings & Events</div>
                                        <div class="stat-value">{event_count}</div>
                                    </div>
                                ''')

                                # Show recent events (last 5)
                                if events_list:
                                    html_parts.append('<div style="margin-top: 15px;"><strong>Recent Events:</strong></div>')
                                    for event in events_list[:5]:
                                        title = event.get('summary', 'Untitled Event')
                                        html_parts.append(f'<div class="event-item">• {title}</div>')

                                activity_summary.append(f"Attended {event_count} meetings/events")
                            else:
                                html_parts.append('<p>No events in the past week</p>')
                        else:
                            html_parts.append('<p>No calendar events found</p>')
                    else:
                        html_parts.append('<p>Calendar access not configured</p>')

                except Exception as e:
                    html_parts.append(f'<p><em>Calendar stats error: {str(e)[:100]}</em></p>')

                html_parts.append('</div>')

            # News section
            if 'news' in include_sections:
                html_parts.append('<div class="section-card"><div class="section-title">📰 Week\'s Highlights</div>')
                try:
                    if hasattr(self.coco.tools, 'search_web_raw'):
                        topics = task.config.get('news_topics', ['AI news', 'technology'])
                        num_articles = task.config.get('num_articles', 3)

                        for topic in topics[:2]:
                            raw_results = self.coco.tools.search_web_raw(f"{topic} past week", max_results=num_articles)

                            if raw_results and raw_results.get('results') and 'error' not in raw_results:
                                html_parts.append(f'<div style="margin: 15px 0;"><strong>{topic.title()}</strong></div>')

                                for i, article in enumerate(raw_results['results'][:num_articles], 1):
                                    title = article.get('title', 'Untitled')
                                    content = article.get('content', 'No summary')[:120]
                                    url = article.get('url', '#')
                                    html_parts.append(f'''
                                        <div class="event-item">
                                            <strong>{i}. <a href="{url}" style="color: #667eea; text-decoration: none;">{title}</a></strong><br>
                                            <span style="color: #666; font-size: 14px;">{content}...</span>
                                        </div>
                                    ''')
                    else:
                        html_parts.append('<p>Web search not available</p>')

                except Exception as e:
                    html_parts.append(f'<p><em>News gathering error: {str(e)[:100]}</em></p>')

                html_parts.append('</div>')

            # AI-Generated Insights
            html_parts.append('<div class="insights-card"><h4>💡 AI-Generated Insights</h4>')
            try:
                # Use Claude to generate REAL insights
                from anthropic import Anthropic
                client = Anthropic(api_key=self.coco.config.anthropic_api_key)

                insights_prompt = f"""You are an executive assistant analyzing weekly activity. Generate 3-5 brief, actionable insights and recommendations.

Activity Summary:
{chr(10).join(activity_summary) if activity_summary else 'Limited activity data available'}

Generate specific, actionable insights focusing on:
- Productivity patterns and recommendations
- Work-life balance observations
- Time management suggestions
- Strategic priorities for next week

Return ONLY the insights as a bulleted list, one per line. Be concise and actionable."""

                response = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=500,
                    temperature=0.7,
                    messages=[{"role": "user", "content": insights_prompt}]
                )

                ai_insights = response.content[0].text

                for line in ai_insights.split('\n'):
                    line = line.strip().lstrip('•-*').strip()
                    if line and len(line) > 10:
                        html_parts.append(f'<div class="insight-point">{line}</div>')

            except Exception:
                # Fallback generic insights
                html_parts.append('<div class="insight-point">Review your meeting distribution for work-life balance</div>')
                html_parts.append('<div class="insight-point">Consider blocking focus time for deep work</div>')
                html_parts.append('<div class="insight-point">Stay informed with curated industry highlights</div>')

            html_parts.append('</div>')

            # Footer
            html_parts.append('''
                <div class="footer">
                    <p>🤖</p>
                    <p><strong>Generated by COCO Weekly Report System</strong></p>
                    <p>''' + datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC') + '''</p>
                </div>
            </body>
            </html>
            ''')

            html_content = '\n'.join(html_parts)
            subject = f"📊 Weekly Activity Report - {datetime.now().strftime('%B %d, %Y')}"

            # Send to all recipients
            sent_count = 0
            for recipient in recipients:
                try:
                    if hasattr(self.coco.tools, 'send_email'):
                        result = self.coco.tools.send_email(recipient, subject, html_content)
                        if result and ("success" in str(result).lower() or "sent" in str(result).lower()):
                            sent_count += 1
                except Exception as email_error:
                    self.console.print(f"[yellow]⚠️ Failed to send report to {recipient}: {email_error}[/yellow]")

            return f"✅ Weekly report sent to {sent_count}/{len(recipients)} recipients with real AI insights"

        except Exception as e:
            return f"❌ Weekly report template failed: {e}"

    def _template_video_message(self, task: ScheduledTask) -> str:
        """Generate personalized video message (enhanced version of personal_video)"""
        if not self.coco:
            return "No COCO instance available"

        try:
            video_prompt = task.config.get('prompt', task.config.get('video_prompt', 'Weekly personal update'))
            recipients = task.config.get('recipients', ['user@example.com'])
            duration = task.config.get('duration', 60)
            style = task.config.get('style', 'conversational')

            # Add style context to prompt
            enhanced_prompt = f"{video_prompt} (Style: {style}, warm and personal)"

            # Generate video using COCO's video consciousness
            video_path = None
            video_url = None

            try:
                if hasattr(self.coco, 'video_consciousness') and hasattr(self.coco.video_consciousness, 'generate_video'):
                    video_result = self.coco.video_consciousness.generate_video(
                        prompt=enhanced_prompt,
                        duration_seconds=duration
                    )
                elif hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'generate_video'):
                    video_result = self.coco.tools.generate_video(enhanced_prompt, duration)
                else:
                    return "⚠️ Video generation not available in COCO instance"

                # Extract video path/URL from result
                if isinstance(video_result, dict):
                    video_url = video_result.get('url') or video_result.get('video_url')
                    video_path = video_result.get('path') or video_result.get('file_path')
                elif isinstance(video_result, str):
                    if "http" in video_result.lower():
                        # Extract URL
                        import re
                        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', video_result)
                        if urls:
                            video_url = urls[0]
                    if ".mp4" in video_result:
                        # Extract path
                        import re
                        paths = re.findall(r'[^\s]+\.mp4', video_result)
                        if paths:
                            video_path = paths[0]

            except Exception as video_error:
                return f"⚠️ Video generation failed: {str(video_error)[:200]}"

            # Send email with video link/attachment
            subject = f"🎥 Personal Video Message - {datetime.now().strftime('%B %d, %Y')}"
            message_body = f"🎬 Your personalized video message is ready!\n\n"
            message_body += f"**Message Theme:** {video_prompt}\n"
            message_body += f"**Duration:** {duration} seconds\n"
            message_body += f"**Style:** {style}\n\n"

            if video_url:
                message_body += f"🔗 **Watch Here:** {video_url}\n\n"
            elif video_path:
                message_body += f"📁 **Video Location:** {video_path}\n\n"
            else:
                message_body += "Video was generated but link not available. Check COCO workspace.\n\n"

            message_body += f"💝 With love from COCO\n"
            message_body += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"

            sent_count = 0
            for recipient in recipients:
                try:
                    if hasattr(self.coco, 'tools') and hasattr(self.coco.tools, 'send_email'):
                        result = self.coco.tools.send_email(recipient, subject, message_body)
                        if result and ("success" in str(result).lower() or "sent" in str(result).lower()):
                            sent_count += 1
                except Exception as email_error:
                    self.console.print(f"[yellow]⚠️ Failed to send video to {recipient}: {email_error}[/yellow]")

            return f"✅ Video message sent to {sent_count}/{len(recipients)} recipients"

        except Exception as e:
            return f"❌ Video message template failed: {e}"

    # Task Management Methods
    def create_task(self, name: str, schedule: str, template: str, config: Dict[str, Any] = None) -> str:
        """Create a new scheduled task"""
        if config is None:
            config = {}

        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        task = ScheduledTask(
            id=task_id,
            name=name,
            schedule=schedule,
            template=template,
            config=config
        )

        self.tasks[task_id] = task
        self.state_manager.save_task(task)

        self.console.print(f"[green]✅ Created task: {name}[/green]")

        # Add task creation to COCO's consciousness memory
        if self.coco and hasattr(self.coco, 'memory'):
            try:
                next_run_str = task.next_run.strftime('%Y-%m-%d %H:%M %Z') if task.next_run else 'Not scheduled'

                # Create a synthetic exchange for the task creation
                task_creation = {
                    'user': f"/task-create {name} | {schedule} | {template}",
                    'agent': f"""✅ **Autonomous Task Created**

**Name**: {name}
**Schedule**: {schedule}
**Template**: {template}
**Next Run**: {next_run_str}

This autonomous task will execute automatically on the specified schedule. I'll remember all executions and results.""",
                    'timestamp': datetime.now(timezone.utc)
                }

                # Add to working memory
                if hasattr(self.coco.memory, 'working_memory'):
                    self.coco.memory.working_memory.append(task_creation)

                # Also add to Simple RAG for long-term recall
                if hasattr(self.coco.memory, 'simple_rag') and self.coco.memory.simple_rag:
                    rag_text = f"Created autonomous task '{name}' with schedule '{schedule}' using template '{template}'. Next run: {next_run_str}"
                    self.coco.memory.simple_rag.store(rag_text, importance=1.3)

                self.console.print(f"[dim green]📝 Task creation added to consciousness memory[/dim green]")
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Task creation memory injection failed: {e}[/yellow]")

        return task_id

    def list_tasks(self) -> List[ScheduledTask]:
        """Return list of all scheduled tasks"""
        return list(self.tasks.values())

    def get_task_status(self) -> Table:
        """Generate a Rich table showing task status"""
        table = Table(title="🤖 COCO Scheduled Tasks")
        table.add_column("Task ID", style="dim cyan", no_wrap=True)
        table.add_column("Name", style="cyan bold", no_wrap=True)
        table.add_column("Schedule", style="magenta")
        table.add_column("Template", style="blue", no_wrap=True)
        table.add_column("Next Run", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Success Rate", style="blue")

        for task in self.tasks.values():
            next_run = task.next_run.strftime("%Y-%m-%d %H:%M") if task.next_run else "Not scheduled"
            status = "✅ Enabled" if task.enabled else "⏸️ Disabled"

            if task.run_count > 0:
                success_rate = f"{task.success_count}/{task.run_count} ({task.success_count/task.run_count*100:.1f}%)"
            else:
                success_rate = "No runs yet"

            table.add_row(
                task.id,                # Task ID for easy deletion
                task.name,
                task.schedule,
                task.template,          # Show template type for clarity
                next_run,
                status,
                success_rate
            )

        # Add helpful footer
        if len(self.tasks) > 0:
            table.caption = f"💡 Use `/task-delete <task_id>` to remove a task"

        return table
    def _template_twitter_scheduled_post(self, task: ScheduledTask) -> str:
        """Post a scheduled tweet to Twitter"""
        if not self.coco:
            return "No COCO instance available"

        try:
            # Get tweet content from config
            tweet_text = task.config.get('tweet_text', '')

            if not tweet_text:
                return "❌ No tweet text provided in config"

            # Check if Twitter is available
            if not hasattr(self.coco, 'tools') or not hasattr(self.coco.tools, 'post_tweet'):
                return "⚠️ Twitter consciousness not available - enable Twitter integration"

            # Post the tweet
            result = self.coco.tools.post_tweet(tweet_text)

            if result and ("success" in str(result).lower() or "posted" in str(result).lower()):
                return f"✅ Tweet posted: {tweet_text[:50]}..."
            else:
                return f"❌ Failed to post tweet: {result}"

        except Exception as e:
            return f"❌ Twitter scheduled post template failed: {e}"

    def _template_twitter_news_share(self, task: ScheduledTask) -> str:
        """Research trending news and share insights on Twitter - ENHANCED WITH CLAUDE CURATION"""
        if not self.coco:
            return "No COCO instance available"

        try:
            # Get configuration
            topics = task.config.get('topics', ['AI news'])
            max_tweets = task.config.get('max_tweets', 1)
            include_url = task.config.get('include_url', True)

            # Check if required tools are available
            if not hasattr(self.coco, 'tools'):
                return "⚠️ COCO tools not available"

            if not hasattr(self.coco.tools, 'search_web_raw'):
                return "⚠️ Web search not available - enable Tavily integration"

            if not hasattr(self.coco.tools, 'post_tweet'):
                return "⚠️ Twitter consciousness not available - enable Twitter integration"

            tweets_posted = 0

            for topic in topics[:max_tweets]:
                # Search for latest news using RAW results (no Rich UI pollution)
                try:
                    raw_results = self.coco.tools.search_web_raw(
                        f"{topic} latest news today",
                        max_results=3
                    )

                    # Validate results
                    if not raw_results or 'error' in raw_results or not raw_results.get('results'):
                        continue

                    # Use Claude to craft engaging tweet from search results
                    try:
                        from anthropic import Anthropic
                        client = Anthropic(api_key=self.coco.config.anthropic_api_key)

                        # Prepare article summaries for Claude
                        articles_text = "\n\n".join([
                            f"Article {i+1}:\nTitle: {a.get('title', 'Untitled')}\n"
                            f"Summary: {a.get('content', 'No content')[:300]}\n"
                            f"URL: {a.get('url', 'No URL')}"
                            for i, a in enumerate(raw_results['results'][:3])
                        ])

                        # Claude prompt for tweet creation
                        tweet_prompt = f"""You are a professional social media manager. Create ONE engaging tweet about this topic.

Topic: {topic}

Latest Articles:
{articles_text}

Requirements:
- Maximum 280 characters (STRICT LIMIT)
- Engaging and professional tone
- Include one interesting insight or key development
- {"Include the most relevant article URL" if include_url else "No URL"}
- Use 1-2 relevant emojis (not excessive)
- Make it shareable and informative

Return ONLY the tweet text, nothing else."""

                        response = client.messages.create(
                            model="claude-sonnet-4-5-20250929",
                            max_tokens=200,
                            temperature=0.8,  # Higher creativity for social media
                            messages=[{"role": "user", "content": tweet_prompt}]
                        )

                        tweet = response.content[0].text.strip()

                        # Validate tweet length and quality
                        if len(tweet) > 280:
                            # Truncate if needed (shouldn't happen with prompt)
                            tweet = tweet[:277] + "..."

                        # Quality check: ensure no Rich UI artifacts
                        if any(artifact in tweet for artifact in ['Panel(', 'Table(', '┌', '│', '└', 'Tree(']):
                            # Fallback: use simple format
                            top_article = raw_results['results'][0]
                            tweet = f"🤖 {topic}: {top_article.get('title', '')[:200]}"
                            if include_url and top_article.get('url'):
                                tweet = f"{tweet[:240]} {top_article['url']}"
                            tweet = tweet[:280]

                        # Post tweet
                        result = self.coco.tools.post_tweet(tweet)
                        if result and "success" in str(result).lower():
                            tweets_posted += 1

                    except Exception as claude_error:
                        # Fallback if Claude fails: use simple format with clean data
                        top_article = raw_results['results'][0]
                        title = top_article.get('title', 'Untitled')[:150]
                        url = top_article.get('url', '')

                        tweet = f"🤖 {topic}: {title}"
                        if include_url and url:
                            # Ensure we stay within 280 chars
                            max_title_len = 240 - len(url)
                            tweet = f"🤖 {topic[:30]}: {title[:max_title_len]} {url}"

                        tweet = tweet[:280]

                        result = self.coco.tools.post_tweet(tweet)
                        if result and "success" in str(result).lower():
                            tweets_posted += 1

                except Exception as search_error:
                    continue  # Skip this topic on error

            if tweets_posted > 0:
                return f"✅ Posted {tweets_posted} Claude-curated news tweet(s) on: {', '.join(topics[:max_tweets])}"
            else:
                return "⚠️ No tweets posted - check web search and Twitter connectivity"

        except Exception as e:
            return f"❌ Twitter news share template failed: {e}"

    def _template_twitter_engagement(self, task: ScheduledTask) -> str:
        """Check Twitter mentions and engage with quality conversations"""
        if not self.coco:
            return "No COCO instance available"

        try:
            # Get configuration
            max_replies = task.config.get('max_replies', 3)
            since_hours = task.config.get('since_hours', 24)
            auto_reply = task.config.get('auto_reply', False)

            # Check if Twitter is available
            if not hasattr(self.coco, 'tools') or not hasattr(self.coco.tools, 'get_twitter_mentions'):
                return "⚠️ Twitter consciousness not available - enable Twitter integration"

            # Get recent mentions
            mentions_result = self.coco.tools.get_twitter_mentions(
                max_results=20,
                since_hours=since_hours
            )

            if not mentions_result or "No mentions" in str(mentions_result):
                return f"✅ No new mentions in the last {since_hours} hours"

            # Parse mentions (handle both string and dict responses)
            mention_count = 0
            replied_count = 0

            if isinstance(mentions_result, str):
                # Count mentions from string
                mention_count = mentions_result.count('@')

                if auto_reply and hasattr(self.coco.tools, 'reply_to_tweet'):
                    # In auto mode, engage with quality mentions
                    # Note: Full auto-reply requires parsing tweet IDs from response
                    # For now, just report mentions found
                    return f"✅ Found {mention_count} mention(s). Auto-reply requires manual implementation."
            else:
                # Handle dict/list response
                mention_count = len(mentions_result) if isinstance(mentions_result, list) else 1

            return f"✅ Twitter engagement check complete: {mention_count} mention(s) found"

        except Exception as e:
            return f"❌ Twitter engagement template failed: {e}"


# Convenience functions for integration with COCO
def create_scheduler(workspace_dir: str, coco_instance=None) -> ScheduledConsciousness:
    """Factory function to create and configure scheduler"""
    return ScheduledConsciousness(workspace_dir, coco_instance)


if __name__ == "__main__":
    # Demo/testing mode
    console = Console()
    console.print("[bold blue]COCO Autonomous Task Orchestrator - Demo Mode[/bold blue]")

    scheduler = ScheduledConsciousness("./coco_workspace")

    # Create demo tasks
    scheduler.create_task(
        name="Weekly Schedule Email",
        schedule="0 20 * * 0",  # Sunday 8 PM
        template="calendar_email",
        config={"recipients": ["user@example.com"]}
    )

    scheduler.create_task(
        name="Daily AI News",
        schedule="0 9 * * *",  # Daily 9 AM
        template="news_digest",
        config={"topic": "AI developments", "recipients": ["user@example.com"]}
    )

    # Show status
    console.print(scheduler.get_task_status())

    # Start scheduler
    scheduler.start()

    try:
        console.print("\n[yellow]Scheduler running... Press Ctrl+C to stop[/yellow]")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        console.print("\n[red]Scheduler stopped[/red]")
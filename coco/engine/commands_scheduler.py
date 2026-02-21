"""
Scheduler and automation slash-command handlers for CoCo.

Covers ``/task-create``, ``/task-list``, ``/task-delete``, ``/task-run``,
``/task-status``, and the five ``/auto-*`` toggle commands.

Extracted from ``cocoa.py`` lines ~10032-10781.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Default placeholder email -- never hardcode real addresses.
_DEFAULT_EMAIL = "user@example.com"


class SchedulerCommandHandler:
    """
    Handles all ``/task-*`` and ``/auto-*`` slash commands.

    Parameters
    ----------
    engine : Any
        Reference to the main engine.  Must expose ``.scheduler`` (the
        ``COCOScheduler`` instance, or ``None``), ``.console``, and
        ``.config``.
    """

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def _scheduler(self) -> Any:
        sched = getattr(self.engine, "scheduler", None)
        return sched

    @property
    def _console(self) -> Any:
        return self.engine.console

    @staticmethod
    def _panel(text: str, title: str = "", style: str = "red") -> Any:
        from rich.panel import Panel

        return Panel(text, title=title, border_style=style)

    def _require_scheduler(self) -> Any | None:
        """Return an error panel if the scheduler is missing, else ``None``."""
        if not self._scheduler:
            return self._panel(
                "**Scheduled consciousness not available**\n\n"
                "The autonomous task orchestrator is not initialized.",
                title="Scheduler Unavailable",
                style="red",
            )
        return None

    # ------------------------------------------------------------------
    # /task-create
    # ------------------------------------------------------------------

    def handle_task_create_command(self, args: str) -> Any:
        """Create a new scheduled task (natural language or structured)."""
        err = self._require_scheduler()
        if err:
            return err

        if not args.strip():
            return self._task_create_help()

        try:
            # Natural-language detection
            if "|" not in args:
                return self._create_from_natural_language(args)

            # Structured format: name | schedule | template | config
            parts = [p.strip() for p in args.split("|")]
            if len(parts) < 3:
                return self._panel(
                    "**Missing required fields**\n\n"
                    "Format: name | schedule | template | config\n"
                    f'Example: Weekly Email | every Sunday at 8pm | calendar_email | {{"recipients": ["{_DEFAULT_EMAIL}"]}}\n\n'
                    "Or just describe what you want naturally!",
                    title="Invalid Format",
                    style="red",
                )

            name = parts[0]
            schedule = parts[1]
            template = parts[2]
            config = self._parse_config(parts[3] if len(parts) > 3 else "")

            if isinstance(config, str):
                # _parse_config returns a Panel (error) when JSON is bad
                return config

            task_id = self._scheduler.create_task(name, schedule, template, config)
            task = self._scheduler.tasks.get(task_id)
            next_run = (
                task.next_run.strftime("%Y-%m-%d %H:%M %Z")
                if task and task.next_run
                else "Not scheduled"
            )

            return self._panel(
                f"**Task created successfully!**\n\n"
                f"**Name:** {name}\n"
                f"**Schedule:** {schedule}\n"
                f"**Template:** {template}\n"
                f"**Next Run:** {next_run}\n"
                f"**Task ID:** {task_id}\n\n"
                f"Use /task-list to see all tasks\n"
                f"Use /task-delete {task_id} to remove this task",
                title="Task Created",
                style="green",
            )

        except Exception as exc:
            return self._panel(
                f"**Task creation failed**\n\n{exc}", title="Error", style="red"
            )

    # ------------------------------------------------------------------
    # /task-list  |  /tasks  |  /schedule
    # ------------------------------------------------------------------

    def handle_task_list_command(self) -> Any:
        """Show all scheduled tasks."""
        err = self._require_scheduler()
        if err:
            return err

        try:
            return self._scheduler.get_task_status()
        except Exception as exc:
            return self._panel(
                f"**Failed to list tasks**\n\n{exc}", title="Error", style="red"
            )

    # ------------------------------------------------------------------
    # /task-delete
    # ------------------------------------------------------------------

    def handle_task_delete_command(self, args: str) -> Any:
        """Delete a scheduled task with verification."""
        err = self._require_scheduler()
        if err:
            return err

        if not args.strip():
            return self._task_delete_help()

        task_id = args.strip()
        tasks_before = len(self._scheduler.tasks)

        try:
            # Resolve partial matches
            if task_id not in self._scheduler.tasks:
                matches = [
                    tid
                    for tid in self._scheduler.tasks
                    if task_id in tid
                ]
                if len(matches) == 1:
                    task_id = matches[0]
                elif len(matches) > 1:
                    match_list = "\n".join(
                        f"- {tid}: {self._scheduler.tasks[tid].name}"
                        for tid in matches
                    )
                    return self._panel(
                        f"**Ambiguous task ID:** {args}\n\n"
                        f"**Multiple matches found:**\n{match_list}\n\n"
                        "Please provide more specific task ID",
                        title="Multiple Matches",
                        style="yellow",
                    )
                else:
                    return self._panel(
                        f"**Task not found:** {args}\n\n"
                        "Use /task-list to see valid task IDs",
                        title="Task Not Found",
                        style="red",
                    )

            task_name = self._scheduler.tasks[task_id].name
            task_template = self._scheduler.tasks[task_id].template
            task_schedule = self._scheduler.tasks[task_id].schedule

            success = self._scheduler.state_manager.delete_task(task_id)

            if success:
                del self._scheduler.tasks[task_id]
                tasks_after = len(self._scheduler.tasks)

                return self._panel(
                    f"**Task deleted successfully**\n\n"
                    f"**Name:** {task_name}\n"
                    f"**Template:** {task_template}\n"
                    f"**Schedule:** {task_schedule}\n"
                    f"**Task ID:** {task_id}\n\n"
                    f"**Tasks remaining:** {tasks_after} (was {tasks_before})",
                    title="Task Deleted",
                    style="green",
                )

            return self._panel(
                f"**Failed to delete task:** {task_id}\n\n"
                "Database deletion returned false.",
                title="Delete Failed",
                style="red",
            )

        except KeyError:
            return self._panel(
                f"**Task not found in memory:** {task_id}\n\n"
                "The task may have been deleted already.\n"
                "Use /task-list to see current tasks.",
                title="Task Not Found",
                style="red",
            )
        except Exception as exc:
            return self._panel(
                f"**Task deletion failed**\n\n**Error:** {exc}\n\n"
                f"**Task ID:** {task_id}\n**Tasks before:** {tasks_before}",
                title="Error",
                style="red",
            )

    # ------------------------------------------------------------------
    # /task-run
    # ------------------------------------------------------------------

    def handle_task_run_command(self, args: str) -> Any:
        """Manually execute a task immediately."""
        err = self._require_scheduler()
        if err:
            return err

        if not args.strip():
            return self._panel(
                "**Usage:** /task-run <task_id>\n\n"
                "Use /task-list to see available task IDs",
                title="Run Task Help",
                style="cyan",
            )

        task_id = args.strip()

        try:
            if task_id not in self._scheduler.tasks:
                return self._panel(
                    f"**Task not found:** {task_id}\n\n"
                    "Use /task-list to see valid task IDs",
                    title="Task Not Found",
                    style="red",
                )

            task = self._scheduler.tasks[task_id]
            self._console.print(f"[cyan]Manually executing task: {task.name}...[/cyan]")
            self._scheduler._execute_task(task)

            return self._panel(
                f"**Task executed**\n\n"
                f"**Name:** {task.name}\n"
                f"**Success Count:** {task.success_count}\n"
                f"**Failure Count:** {task.failure_count}\n\n"
                "Check task output above for results.",
                title="Task Executed",
                style="green",
            )

        except Exception as exc:
            return self._panel(
                f"**Task execution failed**\n\n{exc}", title="Error", style="red"
            )

    # ------------------------------------------------------------------
    # /task-status
    # ------------------------------------------------------------------

    def handle_task_status_command(self) -> Any:
        """Detailed scheduler status overview."""
        err = self._require_scheduler()
        if err:
            return err

        try:
            from rich.markdown import Markdown

            sched = self._scheduler
            enabled_tasks = [t for t in sched.tasks.values() if t.enabled]
            disabled_tasks = [t for t in sched.tasks.values() if not t.enabled]

            total_runs = sum(t.run_count for t in sched.tasks.values())
            total_successes = sum(t.success_count for t in sched.tasks.values())
            total_failures = sum(t.failure_count for t in sched.tasks.values())
            success_rate = (total_successes / total_runs * 100) if total_runs > 0 else 0

            md_text = (
                f"# Autonomous Task Orchestrator Status\n\n"
                f"**Scheduler State:** {'Running' if sched.running else 'Stopped'}\n"
                f"**Total Tasks:** {len(sched.tasks)}\n"
                f"**Enabled Tasks:** {len(enabled_tasks)}\n"
                f"**Disabled Tasks:** {len(disabled_tasks)}\n\n"
                f"**Execution Statistics:**\n"
                f"- Total Runs: {total_runs}\n"
                f"- Successes: {total_successes}\n"
                f"- Failures: {total_failures}\n"
                f"- Success Rate: {success_rate:.1f}%\n\n"
                f"**Available Commands:**\n"
                f"- /task-create - Create new scheduled task\n"
                f"- /task-list - View all tasks\n"
                f"- /task-delete <id> - Remove a task\n"
                f"- /task-run <id> - Execute task immediately\n"
            )

            return self._panel(
                str(Markdown(md_text)),  # type: ignore[arg-type]
                title="Scheduler Status",
                style="bright_blue",
            )

        except Exception as exc:
            return self._panel(
                f"**Status check failed**\n\n{exc}", title="Error", style="red"
            )

    # ------------------------------------------------------------------
    # /auto-news
    # ------------------------------------------------------------------

    def handle_auto_news_command(self, args: str) -> Any:
        """Toggle daily news digest."""
        err = self._require_scheduler()
        if err:
            return err

        action = args.strip().lower() if args else "status"
        news_tasks = [
            t
            for t in self._scheduler.tasks.values()
            if "news" in t.name.lower() and "simple_email" in t.template
        ]

        if action == "on":
            if news_tasks:
                return self._panel(
                    f"Daily news already enabled!\n\n"
                    f"**Task:** {news_tasks[0].name}\n"
                    f"**Schedule:** {news_tasks[0].schedule}",
                    style="green",
                )
            task_id = self._scheduler.create_task(
                name="Daily News Digest",
                schedule="daily at 10am",
                template="simple_email",
                config={
                    "topics": ["latest news", "AI developments"],
                    "recipients": [_DEFAULT_EMAIL],
                },
            )
            return self._panel(
                f"Daily news enabled!\n\n"
                f"**Schedule:** Daily at 10am\n**Task ID:** {task_id}\n\n"
                "Use /auto-news off to disable",
                style="green",
            )

        elif action == "off":
            if not news_tasks:
                return self._panel("Daily news not currently enabled", style="yellow")
            for task in news_tasks:
                self._scheduler.state_manager.delete_task(task.id)
                del self._scheduler.tasks[task.id]
            return self._panel(
                f"Daily news disabled\n\n**Removed:** {len(news_tasks)} task(s)",
                style="green",
            )

        else:
            return self._auto_status_single(
                news_tasks,
                "Daily News",
                "/auto-news",
                "daily AI news at 10am",
            )

    # ------------------------------------------------------------------
    # /auto-calendar
    # ------------------------------------------------------------------

    def handle_auto_calendar_command(self, args: str) -> Any:
        """Toggle calendar summary emails."""
        err = self._require_scheduler()
        if err:
            return err

        action = args.strip().lower() if args else "status"
        cal_tasks = [
            t
            for t in self._scheduler.tasks.values()
            if "calendar" in t.name.lower() and "calendar_email" in t.template
        ]

        if action in ("on", "daily", "weekly"):
            if action == "daily":
                schedule = "every weekday at 7am"
                name = "Daily Calendar Preview"
                config = {"recipients": [_DEFAULT_EMAIL], "days_ahead": 1}
            else:
                schedule = "every Sunday at 8pm"
                name = "Weekly Calendar Preview"
                config = {"recipients": [_DEFAULT_EMAIL], "days_ahead": 7}

            task_id = self._scheduler.create_task(
                name=name, schedule=schedule, template="calendar_email", config=config
            )
            return self._panel(
                f"Calendar summary enabled!\n\n"
                f"**Type:** {action}\n**Schedule:** {schedule}\n**Task ID:** {task_id}",
                style="green",
            )

        elif action == "off":
            if not cal_tasks:
                return self._panel(
                    "Calendar summaries not currently enabled", style="yellow"
                )
            for task in cal_tasks:
                self._scheduler.state_manager.delete_task(task.id)
                del self._scheduler.tasks[task.id]
            return self._panel(
                f"Calendar summaries disabled\n\n**Removed:** {len(cal_tasks)} task(s)",
                style="green",
            )

        else:
            if cal_tasks:
                status_text = "Calendar summaries are **ENABLED**\n\n"
                for task in cal_tasks:
                    status_text += f"- **{task.name}** - {task.schedule}\n"
                status_text += "\nUse /auto-calendar off to disable"
                return self._panel(
                    status_text, title="Calendar Status", style="green"
                )
            return self._panel(
                "Calendar summaries are **DISABLED**\n\n"
                "Use /auto-calendar daily for weekday mornings\n"
                "Use /auto-calendar weekly for Sunday evening preview",
                title="Calendar Status",
                style="yellow",
            )

    # ------------------------------------------------------------------
    # /auto-meetings
    # ------------------------------------------------------------------

    def handle_auto_meetings_command(self, args: str) -> Any:
        """Toggle meeting prep assistant."""
        err = self._require_scheduler()
        if err:
            return err

        action = args.strip().lower() if args else "status"
        meeting_tasks = [
            t
            for t in self._scheduler.tasks.values()
            if "meeting" in t.name.lower() and "meeting_prep" in t.template
        ]

        if action == "on":
            if meeting_tasks:
                return self._panel(
                    f"Meeting prep already enabled!\n\n**Task:** {meeting_tasks[0].name}",
                    style="green",
                )
            task_id = self._scheduler.create_task(
                name="Meeting Prep Assistant",
                schedule="every 30 minutes",
                template="meeting_prep",
                config={
                    "recipient": _DEFAULT_EMAIL,
                    "advance_minutes": 30,
                    "include_ai_prep": True,
                },
            )
            return self._panel(
                f"Meeting prep enabled!\n\n"
                f"**How it works:** Checks calendar every 30min, sends email if meeting found\n"
                f"**Advance notice:** 30 minutes\n"
                f"**Task ID:** {task_id}\n\n"
                "Use /auto-meetings off to disable",
                title="Meeting Prep Enabled",
                style="green",
            )

        elif action == "off":
            if not meeting_tasks:
                return self._panel(
                    "Meeting prep not currently enabled", style="yellow"
                )
            for task in meeting_tasks:
                self._scheduler.state_manager.delete_task(task.id)
                del self._scheduler.tasks[task.id]
            return self._panel("Meeting prep disabled", style="green")

        else:
            return self._auto_status_single(
                meeting_tasks,
                "Meeting Prep",
                "/auto-meetings",
                "automatic meeting preparation",
            )

    # ------------------------------------------------------------------
    # /auto-report
    # ------------------------------------------------------------------

    def handle_auto_report_command(self, args: str) -> Any:
        """Toggle weekly activity report."""
        err = self._require_scheduler()
        if err:
            return err

        action = args.strip().lower() if args else "status"
        report_tasks = [
            t
            for t in self._scheduler.tasks.values()
            if "report" in t.name.lower() and "weekly_report" in t.template
        ]

        if action == "on":
            if report_tasks:
                return self._panel(
                    f"Weekly report already enabled!\n\n**Task:** {report_tasks[0].name}",
                    style="green",
                )
            task_id = self._scheduler.create_task(
                name="Weekly Activity Report",
                schedule="every Sunday at 6pm",
                template="weekly_report",
                config={
                    "recipients": [_DEFAULT_EMAIL],
                    "time_period": 7,
                    "include_sections": ["email", "calendar", "news"],
                    "news_topics": ["AI news", "technology"],
                },
            )
            return self._panel(
                f"Weekly report enabled!\n\n"
                f"**Schedule:** Every Sunday at 6pm\n"
                f"**Includes:** Email stats, calendar, news highlights\n"
                f"**Task ID:** {task_id}\n\n"
                "Use /auto-report off to disable",
                title="Weekly Report Enabled",
                style="green",
            )

        elif action == "off":
            if not report_tasks:
                return self._panel(
                    "Weekly report not currently enabled", style="yellow"
                )
            for task in report_tasks:
                self._scheduler.state_manager.delete_task(task.id)
                del self._scheduler.tasks[task.id]
            return self._panel("Weekly report disabled", style="green")

        else:
            return self._auto_status_single(
                report_tasks,
                "Weekly Report",
                "/auto-report",
                "weekly activity summaries",
            )

    # ------------------------------------------------------------------
    # /auto-video
    # ------------------------------------------------------------------

    def handle_auto_video_command(self, args: str) -> Any:
        """Toggle weekly video messages."""
        err = self._require_scheduler()
        if err:
            return err

        action = args.strip().lower() if args else "status"
        video_tasks = [
            t
            for t in self._scheduler.tasks.values()
            if "video" in t.name.lower() and "video_message" in t.template
        ]

        if action == "on":
            if video_tasks:
                return self._panel(
                    f"Weekly video already enabled!\n\n**Task:** {video_tasks[0].name}",
                    style="green",
                )
            task_id = self._scheduler.create_task(
                name="Weekly Video Message",
                schedule="every Sunday at 3pm",
                template="video_message",
                config={
                    "prompt": "Warm weekly personal update",
                    "duration": 60,
                    "recipients": [_DEFAULT_EMAIL],
                    "style": "conversational",
                },
            )
            return self._panel(
                f"Weekly video enabled!\n\n"
                f"**Schedule:** Every Sunday at 3pm\n"
                f"**Duration:** 60 seconds\n"
                f"**Task ID:** {task_id}\n\n"
                "Use /auto-video off to disable",
                title="Weekly Video Enabled",
                style="green",
            )

        elif action == "off":
            if not video_tasks:
                return self._panel(
                    "Weekly video not currently enabled", style="yellow"
                )
            for task in video_tasks:
                self._scheduler.state_manager.delete_task(task.id)
                del self._scheduler.tasks[task.id]
            return self._panel("Weekly video disabled", style="green")

        else:
            return self._auto_status_single(
                video_tasks,
                "Weekly Video",
                "/auto-video",
                "weekly personalized video messages",
            )

    # ------------------------------------------------------------------
    # /auto-status  |  /auto
    # ------------------------------------------------------------------

    def handle_auto_status_command(self) -> Any:
        """Overview of all five automation templates."""
        err = self._require_scheduler()
        if err:
            return err

        from rich.markdown import Markdown

        tasks = self._scheduler.tasks.values()

        news_on = any(
            "news" in t.name.lower() and "simple_email" in t.template for t in tasks
        )
        cal_on = any(
            "calendar" in t.name.lower() and "calendar_email" in t.template
            for t in tasks
        )
        meet_on = any(
            "meeting" in t.name.lower() and "meeting_prep" in t.template for t in tasks
        )
        report_on = any(
            "report" in t.name.lower() and "weekly_report" in t.template for t in tasks
        )
        video_on = any(
            "video" in t.name.lower() and "video_message" in t.template for t in tasks
        )

        enabled_count = sum([news_on, cal_on, meet_on, report_on, video_on])

        def _flag(on: bool) -> str:
            return "ON" if on else "OFF"

        md = (
            "# Automation Status\n\n"
            "**Your 5 Personal Assistant Templates:**\n\n"
            f"Daily News: {_flag(news_on)} - /auto-news\n"
            f"Calendar: {_flag(cal_on)} - /auto-calendar\n"
            f"Meeting Prep: {_flag(meet_on)} - /auto-meetings\n"
            f"Weekly Report: {_flag(report_on)} - /auto-report\n"
            f"Weekly Video: {_flag(video_on)} - /auto-video\n\n"
            f"**Active:** {enabled_count}/5 templates\n\n"
            "**Commands:**\n"
            "- /auto-<name> on - Enable automation\n"
            "- /auto-<name> off - Disable automation\n"
            "- /auto-<name> - Check status\n"
        )

        return self._panel(
            str(Markdown(md)),  # type: ignore[arg-type]
            title="All Automation Status",
            style="bright_blue",
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _task_create_help(self) -> Any:
        return self._panel(
            f'**Usage:** /task-create <name> | <schedule> | <template> | <config>\n\n'
            f"**Natural Language Format (Alternative):**\n"
            f'Just describe what you want naturally:\n'
            f'- "Send me a test email every day at 6:08 pm"\n'
            f'- "Create a calendar summary every Sunday at 8pm"\n\n'
            f"**Structured Format:**\n"
            f'- /task-create Weekly Email | every Sunday at 8pm | calendar_email | '
            f'{{"recipients": ["{_DEFAULT_EMAIL}"]}}\n\n'
            f"**Available Templates:**\n"
            f"- simple_email, calendar_email, news_digest\n"
            f"- health_check, web_research, personal_video, test_file\n\n"
            f"**Schedule Formats:**\n"
            f'- Natural language: "every Sunday at 8pm", "daily at 9am"\n'
            f'- Cron: "0 20 * * 0" (Sunday 8 PM)\n'
            f'- Special: @daily, @weekly, @monthly',
            title="Task Creation Help",
            style="cyan",
        )

    def _task_delete_help(self) -> Any:
        if self._scheduler and self._scheduler.tasks:
            task_list = "\n".join(
                f"- {t.id}: {t.name}"
                for t in list(self._scheduler.tasks.values())[:5]
            )
            if len(self._scheduler.tasks) > 5:
                task_list += f"\n- ... and {len(self._scheduler.tasks) - 5} more"
            help_text = (
                f"**Usage:** /task-delete <task_id>\n\n"
                f"**Available Tasks:**\n{task_list}\n\n"
                "Use /task-list to see all tasks"
            )
        else:
            help_text = (
                "**Usage:** /task-delete <task_id>\n\n"
                "No tasks currently scheduled.\n"
                "Use /task-create to create a new task"
            )
        return self._panel(help_text, title="Delete Task Help", style="cyan")

    def _create_from_natural_language(self, args: str) -> Any:
        """Attempt to parse natural language and create the task directly."""
        schedule_match = re.search(
            r"(every day|daily|every \w+|every \d+ \w+)(\s+at\s+[\d:apm\s]+)?",
            args.lower(),
        )

        if not schedule_match:
            return self._task_create_help()

        schedule = schedule_match.group(0).strip()
        lower = args.lower()

        # Detect template from keywords
        template = "simple_email"
        if "calendar" in lower:
            template = "calendar_email"
        elif "news" in lower:
            template = "news_digest"
        elif "health" in lower:
            template = "health_check"
        elif "research" in lower:
            template = "web_research"
        elif "video" in lower:
            template = "personal_video"

        name = args[: schedule_match.start()].strip() or f"Auto task - {schedule}"

        config: dict[str, Any] = {}
        if template in ("simple_email", "calendar_email"):
            config = {"recipients": [_DEFAULT_EMAIL]}

        task_id = self._scheduler.create_task(name, schedule, template, config)
        task = self._scheduler.tasks.get(task_id)
        next_run = (
            task.next_run.strftime("%Y-%m-%d %H:%M %Z")
            if task and task.next_run
            else "Not scheduled"
        )

        return self._panel(
            f"**Task created from natural language!**\n\n"
            f"**Interpreted as:**\n"
            f"- **Name:** {name}\n"
            f"- **Schedule:** {schedule}\n"
            f"- **Template:** {template}\n"
            f"- **Config:** {config}\n\n"
            f"**Next Run:** {next_run}\n"
            f"**Task ID:** {task_id}\n\n"
            "Use /task-list to see all tasks\n"
            f"Use /task-delete {task_id} to remove",
            title="Task Created",
            style="green",
        )

    def _parse_config(self, raw: str) -> dict[str, Any] | Any:
        """Parse the optional JSON config part, tolerating common user mistakes."""
        config_str = raw.strip()
        if not config_str:
            return {}

        # Pattern 1: Just an email in braces {user@example.com}
        if re.match(r"^\{[^\":\[\]]+@[^\":\[\]]+\}$", config_str):
            email = config_str.strip("{}").strip()
            return {"recipients": [email]}

        # Pattern 2: Bare email
        if re.match(r"^[^\":\[\]{}]+@[^\":\[\]{}]+$", config_str):
            return {"recipients": [config_str]}

        # Pattern 3: Empty braces
        if config_str in ("{}", "{", "}") or not config_str.strip("{}").strip():
            return {}

        # Pattern 4: Try JSON
        try:
            if not config_str.startswith("{"):
                config_str = "{" + config_str + "}"
            return json.loads(config_str)
        except json.JSONDecodeError as exc:
            return self._panel(
                f"**Invalid JSON config**\n\n"
                f"Error: {exc}\n\n"
                f"Received: {raw}\n\n"
                f"Tips:\n"
                f'- Use double quotes: {{"key": "value"}}\n'
                f'- Or just provide email directly: {_DEFAULT_EMAIL}\n\n'
                f'Example: {{"recipients": ["{_DEFAULT_EMAIL}"]}}',
                title="JSON Parse Error",
                style="red",
            )

    def _auto_status_single(
        self,
        tasks: list[Any],
        label: str,
        toggle_cmd: str,
        enable_desc: str,
    ) -> Any:
        """Generic status display for a single automation type."""
        if tasks:
            task = tasks[0]
            next_str = (
                task.next_run.strftime("%Y-%m-%d %H:%M")
                if task.next_run
                else "Not scheduled"
            )
            return self._panel(
                f"{label} is **ENABLED**\n\n"
                f"**Schedule:** {task.schedule}\n"
                f"**Next run:** {next_str}\n"
                f"**Runs:** {task.run_count}\n\n"
                f"Use {toggle_cmd} off to disable",
                title=f"{label} Status",
                style="green",
            )
        return self._panel(
            f"{label} is **DISABLED**\n\n"
            f"Use {toggle_cmd} on to enable {enable_desc}",
            title=f"{label} Status",
            style="yellow",
        )

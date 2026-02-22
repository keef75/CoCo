"""
Calendar tool provider -- read, add, and create calendar events.

Registers the following tools with the ToolRegistry:
  - read_calendar
  - read_todays_calendar
  - add_calendar_event
  - create_calendar_event

All calendar tools depend on the Google Calendar API.  The CalendarConsciousness
class is imported lazily at call time.  When the import fails (missing
dependencies) the tool returns a descriptive error.

Because CalendarConsciousness handles its own OAuth and service construction,
the tools do NOT require an injected dependency -- they are always registered
with a handler, and availability is checked at execution time.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .registry import ToolDefinition, ToolRegistry

# ---------------------------------------------------------------------------
# JSON schemas
# ---------------------------------------------------------------------------

_READ_CALENDAR_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "days": {
            "type": "integer",
            "description": "Number of days ahead to read (default: 7)",
            "default": 7,
        },
    },
    "required": [],
}

_READ_TODAYS_CALENDAR_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {},
    "required": [],
}

_ADD_CALENDAR_EVENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Event title or description"},
        "when": {
            "type": "string",
            "description": (
                "Natural language time description "
                "(e.g., 'tomorrow at 2pm', 'Monday at 9:30am')"
            ),
        },
    },
    "required": ["title", "when"],
}

_CREATE_CALENDAR_EVENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Event title"},
        "start_time": {
            "type": "string",
            "description": "Start time in natural language or ISO format",
        },
        "end_time": {
            "type": "string",
            "description": "End time (optional, defaults to 1 hour after start)",
        },
        "location": {"type": "string", "description": "Event location (optional)"},
        "description": {"type": "string", "description": "Event description (optional)"},
    },
    "required": ["title", "start_time"],
}


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


class _CalendarTools:
    """Stateful implementation of calendar tools.

    CalendarConsciousness is imported lazily at each call so the module
    does not need to be available at import time.
    """

    def __init__(self, console: Any = None) -> None:
        self.console = console

    def _get_calendar(self):
        """Lazily import and instantiate CalendarConsciousness."""
        from google_calendar_consciousness import CalendarConsciousness

        return CalendarConsciousness()

    # ---- read_calendar ---------------------------------------------------

    def read_calendar(self, days: int = 7) -> str:
        """Read upcoming calendar events."""
        try:
            cal = self._get_calendar()

            if self.console:
                self.console.print("[bold cyan]Accessing temporal consciousness...[/bold cyan]")

            result = cal.read_calendar_events(days_ahead=days)
            if result["success"]:
                cal.display_calendar_rich(result)
                if result["count"] == 0:
                    return (
                        f"**Calendar Awareness**: No events found in the next "
                        f"{days} days ({result['period']})"
                    )
                events_text = []
                for event in result["events"]:
                    line = f"- **{event['start_formatted']}**: {event['summary']}"
                    if event["location"]:
                        line += f" at {event['location']}"
                    events_text.append(line)
                return (
                    f"**Calendar Awareness** ({result['period']})\n"
                    f"Found {result['count']} upcoming events:\n\n"
                    + "\n".join(events_text)
                )
            return f"**Calendar Error**: {result['message']}"
        except ImportError:
            return "**Calendar Consciousness Not Available**: Missing calendar dependencies"
        except Exception as e:
            return f"**Calendar Access Error**: {e}"

    # ---- read_todays_calendar --------------------------------------------

    def read_todays_calendar(self) -> str:
        """Read today's calendar schedule."""
        try:
            cal = self._get_calendar()

            if self.console:
                self.console.print("[bold cyan]Reading today's temporal schedule...[/bold cyan]")

            result = cal.read_todays_schedule()
            if result["success"]:
                if result["count"] == 0:
                    return (
                        f"**Today's Schedule** ({result['date']}): "
                        "Clear schedule - no events today"
                    )
                events_text = []
                for event in result["events"]:
                    line = f"- **{event['time']}**: {event['summary']}"
                    if event["location"]:
                        line += f" at {event['location']}"
                    events_text.append(line)
                return (
                    f"**Today's Schedule** ({result['date']})\n"
                    f"{result['count']} events scheduled:\n\n"
                    + "\n".join(events_text)
                )
            return f"**Today's Schedule Error**: {result['message']}"
        except ImportError:
            return "**Calendar Consciousness Not Available**: Missing calendar dependencies"
        except Exception as e:
            return f"**Today's Calendar Error**: {e}"

    # ---- add_calendar_event ----------------------------------------------

    def add_calendar_event(self, title: str, when: str) -> str:
        """Add a calendar event using natural language."""
        try:
            cal = self._get_calendar()

            if self.console:
                self.console.print(
                    f"[bold cyan]Creating calendar event: '{title}' for {when}...[/bold cyan]"
                )

            result = cal.quick_add_event(title, when)
            if result["success"]:
                return f"**Event Created**: {result['message']}"
            return f"**Event Creation Failed**: {result['message']}"
        except ImportError:
            return "**Calendar Consciousness Not Available**: Missing calendar dependencies"
        except Exception as e:
            return f"**Calendar Event Error**: {e}"

    # ---- create_calendar_event -------------------------------------------

    def create_calendar_event(
        self,
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """Create a detailed calendar event with structured time parsing."""
        try:
            import pytz

            cal = self._get_calendar()

            if self.console:
                self.console.print(
                    f"[bold cyan]Creating structured calendar event: '{title}'...[/bold cyan]"
                )

            chicago_tz = pytz.timezone("America/Chicago")
            now = datetime.now(chicago_tz)

            # Parse start_time
            start_dt = self._parse_time(start_time, now, chicago_tz)
            if isinstance(start_dt, str):
                return start_dt  # error message

            # Parse end_time
            if end_time:
                end_dt = self._parse_time(end_time, now, chicago_tz, reference=start_dt)
                if isinstance(end_dt, str):
                    return end_dt
            else:
                end_dt = start_dt + timedelta(hours=1)

            result = cal.create_calendar_event(title, start_dt, end_dt, location, description)
            if result["success"]:
                d = result["details"]
                return (
                    f"**Event Created**: {d['title']}\n"
                    f"**When**: {d['when']}\n"
                    f"**Location**: {d['location']}\n"
                    f"**Created**: {d['created']}"
                )
            return f"**Event Creation Failed**: {result['message']}"
        except ImportError:
            return "**Calendar Consciousness Not Available**: Missing calendar dependencies"
        except Exception as e:
            return f"**Calendar Event Error**: {e}"

    # ------------------------------------------------------------------
    # Time parsing helpers
    # ------------------------------------------------------------------

    def _parse_time(self, time_str: str, now, tz, reference=None):
        """Parse a time string into a timezone-aware datetime.

        Returns either a ``datetime`` or an error ``str``.
        """
        if not isinstance(time_str, str):
            return time_str

        # Try ISO format first
        try:
            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            else:
                dt = dt.astimezone(tz)
            return dt
        except (ValueError, TypeError):
            pass

        low = time_str.lower().strip()

        # Determine base date from weekday or relative words
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
        }
        base_date = reference if reference else now

        for name, weekday in day_map.items():
            if name in low:
                days_ahead = (weekday - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                base_date = now + timedelta(days=days_ahead)
                break
        else:
            if "tomorrow" in low:
                base_date = now + timedelta(days=1)
            elif "today" in low:
                base_date = now

        # Extract time of day
        match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", low)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            meridiem = match.group(3)
            if meridiem == "pm" and hour < 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
        else:
            hour, minute = 10, 0  # default

        try:
            return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except Exception:
            return (
                f"**Invalid Time**: Could not parse '{time_str}'. "
                "Use natural language (e.g., 'Wednesday at 10am') or ISO format."
            )


# ---------------------------------------------------------------------------
# Provider registration function
# ---------------------------------------------------------------------------


def register(
    registry: ToolRegistry,
    config: Any,
    dependencies: Dict[str, Any],
) -> None:
    """Register calendar tools with the central registry.

    Parameters
    ----------
    registry:
        The ``ToolRegistry`` instance.
    config:
        Application configuration.
    dependencies:
        Dict of shared dependencies.  Expected keys:

        - ``"console"`` -- (optional) Rich Console for status messages

    Note: CalendarConsciousness is imported lazily.  These tools are always
    registered with handlers; availability is checked at call time.
    """
    console = dependencies.get("console")

    tools = _CalendarTools(console)

    registry.register(ToolDefinition(
        name="read_calendar",
        description=(
            "Read calendar events from Google Calendar consciousness "
            "- awareness of scheduled time"
        ),
        input_schema=_READ_CALENDAR_SCHEMA,
        handler=tools.read_calendar,
        category="calendar",
    ))

    registry.register(ToolDefinition(
        name="read_todays_calendar",
        description="Read today's calendar schedule - today's temporal awareness",
        input_schema=_READ_TODAYS_CALENDAR_SCHEMA,
        handler=tools.read_todays_calendar,
        category="calendar",
    ))

    registry.register(ToolDefinition(
        name="add_calendar_event",
        description=(
            "Add calendar event using natural language "
            "- schedule through digital time consciousness"
        ),
        input_schema=_ADD_CALENDAR_EVENT_SCHEMA,
        handler=tools.add_calendar_event,
        category="calendar",
    ))

    registry.register(ToolDefinition(
        name="create_calendar_event",
        description=(
            "Create detailed calendar event "
            "- structured temporal consciousness planning"
        ),
        input_schema=_CREATE_CALENDAR_EVENT_SCHEMA,
        handler=tools.create_calendar_event,
        category="calendar",
    ))

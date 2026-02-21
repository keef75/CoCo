"""
Email tool provider -- send, check, and read emails via Gmail.

Registers the following tools with the ToolRegistry:
  - send_email
  - check_emails
  - check_sent_emails
  - get_todays_emails
  - read_email_content

All email tools depend on GmailConsciousness.  When the Gmail integration
is not available (missing credentials or packages), tools are registered
with ``handler=None`` so they appear as unavailable.
"""

from __future__ import annotations

import io
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .registry import ToolDefinition, ToolRegistry

# ---------------------------------------------------------------------------
# JSON schemas
# ---------------------------------------------------------------------------

_SEND_EMAIL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "to": {"type": "string", "description": "Recipient email address"},
        "subject": {"type": "string", "description": "Email subject line"},
        "body": {"type": "string", "description": "Email message content"},
        "attachments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                },
            },
            "description": "Optional email attachments",
        },
    },
    "required": ["to", "subject", "body"],
}

_CHECK_EMAILS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "limit": {
            "type": "integer",
            "description": "Number of recent emails to retrieve (default: 30)",
            "default": 30,
        },
    },
    "required": [],
}

_CHECK_SENT_EMAILS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "limit": {
            "type": "integer",
            "description": "Number of sent emails to retrieve (default: 30, max: 50)",
            "default": 30,
        },
    },
    "required": [],
}

_GET_TODAYS_EMAILS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {},
    "required": [],
}

_READ_EMAIL_CONTENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "email_index": {
            "type": "integer",
            "description": (
                "Email number from list (1=most recent, 2=second most recent, etc.). "
                "Uses cached list if available for consistent indexing."
            ),
            "default": 1,
        },
        "from_today": {
            "type": "boolean",
            "description": "Read from today's emails only instead of all recent emails",
            "default": False,
        },
        "search_query": {
            "type": "string",
            "description": (
                "Optional search query to find specific emails "
                "(e.g., 'FROM john@example.com' or 'SUBJECT meeting')"
            ),
        },
        "message_id": {
            "type": "string",
            "description": (
                "Optional Message-ID header for precise email lookup "
                "(most reliable method, prevents index mismatch)."
            ),
        },
        "folder": {
            "type": "string",
            "description": (
                "Email folder to search (default: INBOX). "
                "Use '[Gmail]/Sent Mail' to read sent emails."
            ),
            "default": "INBOX",
        },
    },
    "required": [],
}


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


class _EmailTools:
    """Stateful implementation of email tools.

    Wraps GmailConsciousness and maintains email caches for consistent
    indexing when the user reads a specific email by number.
    """

    def __init__(self, gmail: Any, config: Any, console: Any = None) -> None:
        self.gmail = gmail
        self.config = config
        self.console = console

        # Email caches (mirrors the old ToolSystem pattern)
        self._cached_emails: Optional[list] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cached_sent_emails: Optional[list] = None
        self._sent_cache_timestamp: Optional[datetime] = None
        self._cached_folder: str = "INBOX"
        self._cache_ttl: int = 300  # 5 minutes

    # ---- send_email ------------------------------------------------------

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: Optional[list] = None,
    ) -> str:
        """Send email via Gmail consciousness."""
        if not self.gmail:
            return "Gmail consciousness not available. Please check configuration."

        try:
            result = self.gmail.send_email(to, subject, body, attachments)
            if result["success"]:
                return f"**Email Sent Successfully**\n\n{result['message']}"
            else:
                return f"**Email Failed**\n\n{result['message']}"
        except Exception as e:
            return f"**Email Error:** {e}"

    # ---- check_emails ----------------------------------------------------

    def check_emails(self, limit: int = 30) -> str:
        """Check recent emails via Gmail consciousness."""
        if not self.gmail:
            return "Gmail consciousness not available. Please check configuration."

        try:
            # Try the gentle approach first
            try:
                from gmail_gentle_fix import GentleGmailFix

                gentle = GentleGmailFix(self.config)
                return gentle.get_recent_emails_summary(limit)
            except Exception:
                pass

            # Fallback: use original Gmail
            emails = self.gmail.receive_emails(limit)
            if not emails:
                return "No emails found."

            self._cached_emails = emails
            self._cache_timestamp = datetime.now()
            self._cached_folder = "INBOX"

            summary = f"**Recent Emails ({len(emails)} found)**\n\n"
            for i, email in enumerate(emails, 1):
                summary += (
                    f"**{i}.** {email.get('formatted_date', 'Unknown')} - "
                    f"From: {email['from'][:50]}\n"
                    f"   **Subject:** {email['subject']}\n"
                )
                if email.get("body_preview"):
                    summary += f"   **Preview:** {email['body_preview'][:100]}...\n"
                summary += "\n"
            return summary

        except Exception as e:
            return f"Error checking emails: {e}"

    # ---- check_sent_emails -----------------------------------------------

    def check_sent_emails(self, limit: int = 30) -> str:
        """Check sent emails from Gmail account."""
        if not self.gmail:
            return "Gmail consciousness not available. Please check configuration."

        try:
            emails = self.gmail.check_sent_emails(limit=limit)
            if isinstance(emails, str):
                return emails

            if not emails:
                return "No sent emails found."

            from rich import box
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table

            self._cached_sent_emails = emails
            self._sent_cache_timestamp = datetime.now()
            self._cached_folder = "[Gmail]/Sent Mail"

            buf = io.StringIO()
            console = Console(file=buf, width=100, force_terminal=True)

            table = Table(title=f"Sent Emails (Last {len(emails)})", box=box.ROUNDED)
            table.add_column("#", style="cyan", width=4)
            table.add_column("To", style="bright_yellow", width=25)
            table.add_column("Subject", style="bright_white", width=35)
            table.add_column("Date", style="green", width=20)

            for i, email in enumerate(emails, 1):
                to_disp = (email["to"][:25] + "...") if len(email["to"]) > 25 else email["to"]
                subj_disp = (
                    (email["subject"][:35] + "...")
                    if len(email["subject"]) > 35
                    else email["subject"]
                )
                table.add_row(str(i), to_disp, subj_disp, email["formatted_date"])

            console.print(
                Panel(
                    table,
                    title="[bold bright_yellow]Sent Email Consciousness[/]",
                    border_style="bright_yellow",
                    padding=(1, 2),
                )
            )
            return buf.getvalue()

        except Exception as e:
            return f"**Sent Email Error:** {e}"

    # ---- get_todays_emails -----------------------------------------------

    def get_todays_emails(self) -> str:
        """Get today's emails."""
        if not self.gmail:
            return "Gmail consciousness not available. Please check configuration."

        try:
            try:
                from gmail_gentle_fix import GentleGmailFix

                gentle = GentleGmailFix(self.config)
                return gentle.get_todays_emails()
            except Exception:
                pass
            return self.gmail.get_todays_emails()
        except Exception as e:
            return f"**Today's Email Error:** {e}"

    # ---- read_email_content ----------------------------------------------

    def read_email_content(
        self,
        email_index: int = 1,
        from_today: bool = False,
        search_query: Optional[str] = None,
        message_id: Optional[str] = None,
        folder: str = "INBOX",
    ) -> str:
        """Read full content of a specific email."""
        if not self.gmail:
            return "Gmail consciousness not available. Please check configuration."

        # PRIORITY 1: Message-ID lookup (most reliable)
        if message_id:
            try:
                email_data = self.gmail.get_email_by_message_id(message_id, folder=folder)
                if email_data:
                    return self._format_email(email_data, "Message-ID")
                return f"Email with Message-ID '{message_id[:50]}...' not found"
            except Exception:
                pass  # fall through to cache

        # PRIORITY 2: Use cached emails if fresh
        emails = None
        source = ""
        cache_age = None

        if "Sent" in folder:
            if self._sent_cache_timestamp:
                cache_age = (datetime.now() - self._sent_cache_timestamp).total_seconds()
            if self._cached_sent_emails and cache_age and cache_age < self._cache_ttl:
                emails = self._cached_sent_emails
                source = f"cached sent emails (age: {int(cache_age)}s)"
        else:
            if self._cache_timestamp:
                cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
            if self._cached_emails and cache_age and cache_age < self._cache_ttl:
                emails = self._cached_emails
                source = f"cached emails (age: {int(cache_age)}s)"

        if emails:
            if email_index < 1 or email_index > len(emails):
                return f"Email #{email_index} not found in cache. Available: 1-{len(emails)}"
            return self._format_email(emails[email_index - 1], source)

        # PRIORITY 3: Enhanced Gmail consciousness
        try:
            from enhanced_gmail_consciousness import EnhancedGmailConsciousness

            enhanced = EnhancedGmailConsciousness(self.config)
            if search_query:
                emails = enhanced.search_emails_sync(search_query, limit=30)
                source = f"search results for '{search_query}'"
            elif from_today:
                today_result = enhanced.get_todays_emails_full()
                emails = today_result.get("emails", [])
                source = "today's emails"
            else:
                emails = enhanced.get_recent_emails_full(limit=30)
                source = "recent emails"

            if not emails:
                return f"No emails found in {source}"
            if email_index < 1 or email_index > len(emails):
                return f"Email #{email_index} not found. Available: 1-{len(emails)} in {source}"
            return self._format_email(emails[email_index - 1], source)

        except ImportError:
            pass

        # PRIORITY 4: Fresh fetch
        try:
            emails = self.gmail.receive_emails(
                limit=30 if not from_today else 50,
                today_only=from_today,
            )
            self._cached_emails = emails
            self._cache_timestamp = datetime.now()
            self._cached_folder = "INBOX"
            source = "fresh fetch (cached for next read)"

            if not emails:
                return f"No {'today' if from_today else 'recent'} emails found"
            if email_index < 1 or email_index > len(emails):
                return f"Email #{email_index} not found. Available: 1-{len(emails)}"
            return self._format_email(emails[email_index - 1], source)

        except Exception as e:
            return f"**Email Content Reading Error:** {e}"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _format_email(self, email_data: dict, source: str) -> str:
        parts = []
        parts.append(f"**Email Content - Gmail Consciousness** ({source})")
        parts.append("=" * 60)
        parts.append(f"**From:** {email_data.get('from', 'Unknown')}")
        if email_data.get("to"):
            parts.append(f"**To:** {email_data['to']}")
        if email_data.get("cc"):
            parts.append(f"**CC:** {email_data['cc']}")
        parts.append(f"**Subject:** {email_data.get('subject', 'No Subject')}")
        parts.append(
            f"**Date:** {email_data.get('formatted_date', email_data.get('date', 'Unknown'))}"
        )
        msg_id = email_data.get("message_id")
        if msg_id:
            parts.append(f"**Message-ID:** {msg_id[:50]}...")
        parts.append("-" * 60)
        parts.append("**Message Content:**")
        parts.append("")

        content = (
            email_data.get("body_full")
            or email_data.get("body")
            or email_data.get("body_formatted")
            or email_data.get("body_plain")
            or email_data.get("body_html")
            or email_data.get("body_preview", "")
        )
        if content:
            # Remove excessive blank lines
            lines = content.split("\n")
            cleaned = []
            prev_empty = False
            for line in lines:
                if line.strip():
                    cleaned.append(line)
                    prev_empty = False
                elif not prev_empty:
                    cleaned.append("")
                    prev_empty = True
            parts.append("\n".join(cleaned))
        else:
            parts.append("[Email content could not be extracted]")

        parts.append("")
        parts.append("=" * 60)
        parts.append(f"Email read via {source}")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Provider registration function
# ---------------------------------------------------------------------------


def register(
    registry: ToolRegistry,
    config: Any,
    dependencies: Dict[str, Any],
) -> None:
    """Register email tools with the central registry.

    Parameters
    ----------
    registry:
        The ``ToolRegistry`` instance.
    config:
        Application configuration.
    dependencies:
        Dict of shared dependencies.  Expected keys:

        - ``"gmail"`` -- GmailConsciousness instance, or ``None``
        - ``"console"`` -- (optional) Rich Console for status messages
    """
    gmail = dependencies.get("gmail")
    console = dependencies.get("console")

    if gmail:
        tools = _EmailTools(gmail, config, console)
        send_handler = tools.send_email
        check_handler = tools.check_emails
        check_sent_handler = tools.check_sent_emails
        todays_handler = tools.get_todays_emails
        read_handler = tools.read_email_content
    else:
        send_handler = None
        check_handler = None
        check_sent_handler = None
        todays_handler = None
        read_handler = None

    registry.register(ToolDefinition(
        name="send_email",
        description="Send email through Gmail consciousness - communicate through digital mail",
        input_schema=_SEND_EMAIL_SCHEMA,
        handler=send_handler,
        category="email",
    ))

    registry.register(ToolDefinition(
        name="check_emails",
        description="Check recent emails through Gmail consciousness - read digital mail",
        input_schema=_CHECK_EMAILS_SCHEMA,
        handler=check_handler,
        category="email",
    ))

    registry.register(ToolDefinition(
        name="check_sent_emails",
        description="Check sent emails from Gmail account - review outgoing digital correspondence",
        input_schema=_CHECK_SENT_EMAILS_SCHEMA,
        handler=check_sent_handler,
        category="email",
    ))

    registry.register(ToolDefinition(
        name="get_todays_emails",
        description="Get today's emails with chronological summary - today's digital mail awareness",
        input_schema=_GET_TODAYS_EMAILS_SCHEMA,
        handler=todays_handler,
        category="email",
    ))

    registry.register(ToolDefinition(
        name="read_email_content",
        description=(
            "Read complete content of specific email for deep digital mail consciousness "
            "and AI collaboration. Use when user wants to read, analyze, or discuss full "
            "email content beyond previews. Supports Message-ID for reliable reading."
        ),
        input_schema=_READ_EMAIL_CONTENT_SCHEMA,
        handler=read_handler,
        category="email",
    ))

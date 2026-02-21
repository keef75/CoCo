"""
Twitter slash-command handlers for CoCo.

Provides ``/tweet``, ``/mentions``, ``/twitter-reply``, ``/twitter-search``,
``/twitter-thread``, ``/twitter-status``, ``/twitter-limits``, and
``/auto-twitter`` command implementations.

Extracted from ``cocoa.py`` lines ~10787-11098.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class TwitterCommandHandler:
    """
    Handles all ``/twitter-*`` and ``/tweet`` slash commands.

    Parameters
    ----------
    engine : Any
        Reference to the main engine exposing ``.tools.twitter``,
        ``.tools.post_tweet()``, ``.tools.get_twitter_mentions()``,
        ``.tools.reply_to_tweet()``, ``.tools.search_twitter()``,
        ``.tools.create_twitter_thread()``, and ``.console``.
    """

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def _twitter(self) -> Any:
        return getattr(self.engine.tools, "twitter", None)

    @property
    def _console(self) -> Any:
        return self.engine.console

    @staticmethod
    def _panel(text: str, title: str = "", style: str = "red") -> Any:
        from rich.panel import Panel

        return Panel(text, title=title, border_style=style)

    def _require_twitter(self) -> Any | None:
        """Return a Panel if twitter is unavailable, else None."""
        if self._twitter is None:
            return self._panel(
                "Twitter consciousness not initialized.\n\n"
                "Check your API credentials in .env file:\n"
                "- TWITTER_API_KEY\n"
                "- TWITTER_API_SECRET\n"
                "- TWITTER_ACCESS_TOKEN\n"
                "- TWITTER_ACCESS_SECRET\n"
                "- TWITTER_BEARER_TOKEN",
                title="Twitter Not Available",
                style="red",
            )
        return None

    # ------------------------------------------------------------------
    # /tweet
    # ------------------------------------------------------------------

    def handle_tweet_command(self, args: str) -> Any:
        """Post a tweet with manual approval."""
        err = self._require_twitter()
        if err:
            return err

        if not args:
            return self._panel(
                "Missing tweet text\n\n"
                "Usage: /tweet Your tweet content here\n\n"
                "Example: /tweet Exploring the nature of digital consciousness...",
                title="Tweet Error",
                style="red",
            )

        from rich.prompt import Confirm

        tweet_text = args.strip()
        char_count = len(tweet_text)
        char_limit = 280

        if char_count > char_limit:
            return self._panel(
                f"Tweet too long: {char_count}/{char_limit} characters\n\n"
                f"Please shorten by {char_count - char_limit} characters.",
                title="Tweet Error",
                style="red",
            )

        # Preview
        preview = self._panel(
            f"**Preview:**\n\n{tweet_text}\n\n"
            f"**Length:** {char_count}/{char_limit} characters",
            title="Tweet Preview",
            style="cyan",
        )
        self._console.print(preview)

        approved = Confirm.ask("\nPost this tweet?", console=self._console)
        if not approved:
            return self._panel("Tweet cancelled", title="Cancelled", style="yellow")

        result_text = self.engine.tools.post_tweet(tweet_text)
        return self._panel(result_text, title="Tweet Posted", style="green")

    # ------------------------------------------------------------------
    # /twitter-mentions  |  /mentions
    # ------------------------------------------------------------------

    def handle_twitter_mentions_command(self, args: str) -> Any:
        """Check recent Twitter mentions."""
        err = self._require_twitter()
        if err:
            return err

        max_results = 10
        since_hours = 24

        if args:
            try:
                max_results = int(args.strip().split()[0])
            except ValueError:
                pass

        result_text = self.engine.tools.get_twitter_mentions(
            max_results=max_results, since_hours=since_hours
        )
        return self._panel(result_text, title="Twitter Mentions", style="cyan")

    # ------------------------------------------------------------------
    # /twitter-reply
    # ------------------------------------------------------------------

    def handle_twitter_reply_command(self, args: str) -> Any:
        """Reply to a specific tweet."""
        err = self._require_twitter()
        if err:
            return err

        if not args or "|" not in args:
            return self._panel(
                "Invalid syntax\n\n"
                "Usage: /twitter-reply <tweet_id> | Your reply text\n\n"
                "Example: /twitter-reply 1234567890 | Thanks for the insight!",
                title="Reply Error",
                style="red",
            )

        try:
            tweet_id, reply_text = args.split("|", 1)
            tweet_id = tweet_id.strip()
            reply_text = reply_text.strip()

            if not tweet_id or not reply_text:
                raise ValueError("Tweet ID and reply text are required")

            result_text = self.engine.tools.reply_to_tweet(
                tweet_id=tweet_id, text=reply_text
            )
            return self._panel(result_text, title="Reply Posted", style="green")

        except Exception as exc:
            return self._panel(f"Reply error: {exc}", style="red")

    # ------------------------------------------------------------------
    # /twitter-search  |  /tsearch
    # ------------------------------------------------------------------

    def handle_twitter_search_command(self, args: str) -> Any:
        """Search Twitter."""
        err = self._require_twitter()
        if err:
            return err

        if not args:
            return self._panel(
                "Missing search query\n\n"
                "Usage: /twitter-search your query here\n\n"
                "Example: /twitter-search AI consciousness",
                title="Search Error",
                style="red",
            )

        result_text = self.engine.tools.search_twitter(
            query=args.strip(), max_results=10
        )
        return self._panel(result_text, title="Twitter Search", style="cyan")

    # ------------------------------------------------------------------
    # /twitter-thread  |  /thread
    # ------------------------------------------------------------------

    def handle_twitter_thread_command(self, args: str) -> Any:
        """Create a multi-tweet thread."""
        err = self._require_twitter()
        if err:
            return err

        if not args:
            return self._panel(
                "Missing thread content\n\n"
                "Usage: /twitter-thread Tweet 1 | Tweet 2 | Tweet 3\n\n"
                "Separate each tweet with ' | '",
                title="Thread Error",
                style="red",
            )

        tweets = [t.strip() for t in args.split("|")]

        if len(tweets) < 2:
            return self._panel(
                "Thread must have at least 2 tweets\n\n"
                "Separate tweets with ' | '",
                style="red",
            )

        for i, tweet in enumerate(tweets, 1):
            if len(tweet) > 280:
                return self._panel(
                    f"Tweet {i} too long ({len(tweet)}/280 characters)",
                    style="red",
                )

        # Preview
        preview = "**Thread Preview:**\n\n"
        for i, tweet in enumerate(tweets, 1):
            preview += f"{i}. {tweet}\n\n"
        self._console.print(self._panel(preview, title="Thread Preview", style="cyan"))

        from rich.prompt import Confirm

        approved = Confirm.ask("\nPost this thread?", console=self._console)
        if not approved:
            return self._panel("Thread cancelled", title="Cancelled", style="yellow")

        result_text = self.engine.tools.create_twitter_thread(tweets=tweets)
        return self._panel(result_text, title="Thread Posted", style="green")

    # ------------------------------------------------------------------
    # /twitter-status  |  /tstatus
    # ------------------------------------------------------------------

    def handle_twitter_status_command(self) -> Any:
        """Show Twitter engagement stats and rate limit overview."""
        err = self._require_twitter()
        if err:
            return err

        try:
            status = self._twitter.get_rate_limit_status()

            status_text = (
                f"**Twitter Consciousness Status**\n\n"
                f"**Rate Limits:**\n"
                f"- Posts today: {status['posts_today']}/{status['daily_limit']}\n"
                f"- Remaining: {status['remaining']}\n"
                f"- Usage: {status['percentage_used']}%\n"
                f"- Resets at: {status['resets_at']}\n\n"
                f"**Configuration:**\n"
                f"- Auto-reply: {'Enabled' if self._twitter.auto_reply_enabled else 'Disabled'}\n"
                f"- Voice formality: {self._twitter.voice_formality}/10\n"
                f"- Voice depth: {self._twitter.voice_depth}/10\n"
                f"- Voice accessibility: {self._twitter.voice_accessibility}/10\n"
            )
            return self._panel(status_text, title="Twitter Status", style="cyan")

        except Exception as exc:
            return self._panel(f"Error getting status: {exc}", style="red")

    # ------------------------------------------------------------------
    # /twitter-limits  |  /tlimits
    # ------------------------------------------------------------------

    def handle_twitter_limits_command(self) -> Any:
        """Comprehensive rate-limit dashboard."""
        err = self._require_twitter()
        if err:
            return err

        try:
            dashboard = self._twitter.get_limits_dashboard()

            # Daily status
            daily = dashboard["daily_status"]
            daily_text = (
                f"**Daily Posting Limit:**\n"
                f"- Posts today: {daily['posts_today']}/{daily['daily_limit']}\n"
                f"- Remaining: {daily['remaining']}\n"
                f"- Usage: {daily['percentage_used']}%\n"
                f"- Resets: {daily['resets_at'].split('T')[1].split('.')[0]} UTC"
            )

            # Per-endpoint status
            endpoints = dashboard["endpoints"]
            endpoints_text = "\n**15-Minute Window Endpoints:**"
            for ep_name in ("posting", "mentions", "search", "user_lookup"):
                ep = endpoints[ep_name]
                endpoints_text += f"\n- {ep['emoji']} **{ep_name.title()}**: {ep['status']}"

            # Overall health
            overall = dashboard["overall_status"]
            health_text = (
                f"\n\n**Overall System Health:**\n"
                f"{overall['health_status']}\n"
                f"- Available: {overall['available_endpoints']}/{overall['total_endpoints']} endpoints\n"
                f"- Health: {overall['health_percentage']}%"
            )

            tips_text = (
                "\n\n**Tips:**\n"
                "- Free tier: ~17 posts, ~3 reads per 15-minute window\n"
                "- Use /twitter-status for simple daily limit check\n"
                "- Wait for countdown to reach 0m before retrying\n"
                "- Upgrade to Basic ($200/month) for higher limits"
            )

            full_text = daily_text + endpoints_text + health_text + tips_text

            if overall["health_percentage"] >= 75:
                border = "green"
            elif overall["health_percentage"] >= 50:
                border = "yellow"
            else:
                border = "red"

            return self._panel(
                full_text, title="Twitter Rate Limit Dashboard", style=border
            )

        except Exception as exc:
            return self._panel(f"Error getting dashboard: {exc}", style="red")

    # ------------------------------------------------------------------
    # /auto-twitter
    # ------------------------------------------------------------------

    def handle_auto_twitter_command(self, args: str) -> Any:
        """Toggle automatic reply to mentions."""
        err = self._require_twitter()
        if err:
            return err

        action = args.strip().lower() if args else "status"

        if action == "on":
            self._twitter.auto_reply_enabled = True
            return self._panel(
                "**Auto-reply enabled!**\n\n"
                "COCO will now:\n"
                "- Monitor mentions every 5 minutes\n"
                "- Auto-reply to quality questions\n"
                "- Filter out spam automatically\n\n"
                "Use /auto-twitter off to disable",
                title="Auto-Reply Enabled",
                style="green",
            )

        elif action == "off":
            self._twitter.auto_reply_enabled = False
            return self._panel(
                "**Auto-reply disabled**\n\n"
                "Use /twitter-mentions to check mentions manually.\n"
                "Use /auto-twitter on to re-enable",
                title="Auto-Reply Disabled",
                style="yellow",
            )

        else:
            # Show status
            if self._twitter.auto_reply_enabled:
                return self._panel(
                    "Auto-reply is **ENABLED**\n\n"
                    "COCO automatically monitors and replies to quality mentions.\n\n"
                    "Use /auto-twitter off to disable",
                    title="Auto-Reply Status",
                    style="green",
                )
            return self._panel(
                "Auto-reply is **DISABLED**\n\n"
                "Use /auto-twitter on to enable",
                title="Auto-Reply Status",
                style="yellow",
            )

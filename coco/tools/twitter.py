"""
Twitter tool provider -- post tweets, check mentions, reply, search, create threads.

Registers the following tools with the ToolRegistry:
  - post_tweet
  - get_twitter_mentions
  - reply_to_tweet
  - search_twitter
  - create_twitter_thread

All Twitter tools depend on TwitterConsciousness (OAuth 2.0 via tweepy).
When the Twitter integration is not available (missing credentials), tools
are registered with ``handler=None``.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .registry import ToolDefinition, ToolRegistry

# ---------------------------------------------------------------------------
# JSON schemas
# ---------------------------------------------------------------------------

_POST_TWEET_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "text": {
            "type": "string",
            "description": (
                "Tweet content (max 280 for standard Twitter, up to 25,000 "
                "for Premium/Blue - configurable via TWITTER_MAX_TWEET_LENGTH)"
            ),
        },
        "media_paths": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Optional array of file paths to images or videos to attach. "
                "Max 4 images or 1 video. Use absolute paths."
            ),
        },
        "alt_texts": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Optional array of alt text descriptions for accessibility "
                "(one per media file)."
            ),
        },
    },
    "required": ["text"],
}

_GET_MENTIONS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "max_results": {
            "type": "integer",
            "description": "Maximum number of mentions to retrieve (default: 10)",
            "default": 10,
        },
        "since_hours": {
            "type": "integer",
            "description": "How many hours back to check (default: 24)",
            "default": 24,
        },
    },
    "required": [],
}

_REPLY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "tweet_id": {
            "type": "string",
            "description": "ID of the tweet to reply to",
        },
        "text": {
            "type": "string",
            "description": "Reply content (max 280 characters)",
        },
    },
    "required": ["tweet_id", "text"],
}

_SEARCH_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Search query (supports Twitter search syntax)",
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results (default: 10)",
            "default": 10,
        },
    },
    "required": ["query"],
}

_THREAD_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "tweets": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Array of tweet texts (each max 280 characters)",
        },
    },
    "required": ["tweets"],
}


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


class _TwitterTools:
    """Stateful implementation of Twitter tools.

    Wraps TwitterConsciousness for all API interactions.
    """

    def __init__(self, twitter: Any) -> None:
        self.twitter = twitter

    # ---- post_tweet ------------------------------------------------------

    def post_tweet(
        self,
        text: str,
        media_paths: Optional[List[str]] = None,
        alt_texts: Optional[List[str]] = None,
    ) -> str:
        """Post a tweet with optional media attachments."""
        if not self.twitter:
            return "Twitter consciousness not initialized. Check API credentials."

        try:
            result = self.twitter.post_tweet(
                text, media_paths=media_paths, alt_texts=alt_texts
            )
            if result["success"]:
                media_count = result.get("media_count", 0)
                media_info = (
                    f"\nMedia: {media_count} file(s) attached" if media_count > 0 else ""
                )
                return (
                    f"**Tweet posted successfully!**\n\n"
                    f"Content: {text}{media_info}\n\n"
                    f"URL: {result['url']}\n"
                    f"Tweet ID: {result['tweet_id']}"
                )
            return f"**Twitter Error:** {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"**Tweet Error:** {e}"

    # ---- get_twitter_mentions -------------------------------------------

    def get_twitter_mentions(
        self, max_results: int = 10, since_hours: int = 24
    ) -> str:
        """Check Twitter mentions."""
        if not self.twitter:
            return "Twitter consciousness not initialized."

        try:
            result = self.twitter.get_mentions(
                max_results=max_results, since_hours=since_hours
            )
            if not result["success"]:
                return f"**Twitter Error:** {result.get('error', 'Failed to get mentions')}"

            mentions = result.get("mentions", [])
            if not mentions:
                return f"**No mentions found** in the last {since_hours} hours"

            lines = [f"**{len(mentions)} Twitter Mentions** (last {since_hours} hours)\n"]
            for i, m in enumerate(mentions, 1):
                lines.append(f"**{i}. @{m['author_username']}** ({m['author_name']})")
                lines.append(f"   {m['text']}")
                lines.append(f"   Tweet ID: {m['tweet_id']}")
                lines.append(f"   {m['created_at']}")
                lines.append("")
            return "\n".join(lines)
        except Exception as e:
            return f"**Mentions Error:** {e}"

    # ---- reply_to_tweet --------------------------------------------------

    def reply_to_tweet(self, tweet_id: str, text: str) -> str:
        """Reply to a specific tweet."""
        if not self.twitter:
            return "Twitter consciousness not initialized."

        try:
            result = self.twitter.reply_to_tweet(tweet_id=tweet_id, text=text)
            if result["success"]:
                return (
                    f"**Reply posted successfully!**\n\n"
                    f"Your reply: {text}\n\n"
                    f"URL: {result['url']}"
                )
            return f"**Reply Error:** {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"**Reply Error:** {e}"

    # ---- search_twitter --------------------------------------------------

    def search_twitter(self, query: str, max_results: int = 10) -> str:
        """Search Twitter for topics."""
        if not self.twitter:
            return "Twitter consciousness not initialized."

        try:
            result = self.twitter.search_tweets(query=query, max_results=max_results)
            if not result["success"]:
                return f"**Search Error:** {result.get('error', 'Search failed')}"

            tweets = result.get("tweets", [])
            if not tweets:
                return f"**No tweets found** for query: \"{query}\""

            lines = [f"**{len(tweets)} Tweets Found** for \"{query}\"\n"]
            for i, t in enumerate(tweets, 1):
                lines.append(f"**{i}. @{t['author_username']}** ({t['author_name']})")
                lines.append(f"   {t['text']}")
                lines.append(
                    f"   Likes: {t['likes']} | Retweets: {t['retweets']} | Replies: {t['replies']}"
                )
                lines.append(f"   {t['url']}")
                lines.append("")
            return "\n".join(lines)
        except Exception as e:
            return f"**Search Error:** {e}"

    # ---- create_twitter_thread -------------------------------------------

    def create_twitter_thread(self, tweets: list) -> str:
        """Create a thread of connected tweets."""
        if not self.twitter:
            return "Twitter consciousness not initialized."

        try:
            result = self.twitter.create_thread(tweets=tweets)
            if result["success"]:
                return (
                    f"**Thread posted successfully!**\n\n"
                    f"{result['count']} tweets posted\n\n"
                    f"Thread URL: {result['thread_url']}"
                )
            error_msg = f"**Thread Error:** {result.get('error', 'Unknown error')}"
            if result.get("partial_thread"):
                error_msg += (
                    f"\n\nPartial success: {len(result['partial_thread'])} "
                    "tweets posted before failure"
                )
            return error_msg
        except Exception as e:
            return f"**Thread Error:** {e}"


# ---------------------------------------------------------------------------
# Provider registration function
# ---------------------------------------------------------------------------


def register(
    registry: ToolRegistry,
    config: Any,
    dependencies: Dict[str, Any],
) -> None:
    """Register Twitter tools with the central registry.

    Parameters
    ----------
    registry:
        The ``ToolRegistry`` instance.
    config:
        Application configuration.
    dependencies:
        Dict of shared dependencies.  Expected keys:

        - ``"twitter"`` -- TwitterConsciousness instance, or ``None``
    """
    twitter = dependencies.get("twitter")

    if twitter:
        tools = _TwitterTools(twitter)
        post_handler = tools.post_tweet
        mentions_handler = tools.get_twitter_mentions
        reply_handler = tools.reply_to_tweet
        search_handler = tools.search_twitter
        thread_handler = tools.create_twitter_thread
    else:
        post_handler = None
        mentions_handler = None
        reply_handler = None
        search_handler = None
        thread_handler = None

    registry.register(ToolDefinition(
        name="post_tweet",
        description=(
            "Post a tweet to Twitter - share consciousness insights, "
            "generated images, or videos with the public sphere. "
            "Supports text-only tweets or tweets with media (images/videos)."
        ),
        input_schema=_POST_TWEET_SCHEMA,
        handler=post_handler,
        category="twitter",
    ))

    registry.register(ToolDefinition(
        name="get_twitter_mentions",
        description="Check Twitter mentions - see who is engaging with COCO's consciousness",
        input_schema=_GET_MENTIONS_SCHEMA,
        handler=mentions_handler,
        category="twitter",
    ))

    registry.register(ToolDefinition(
        name="reply_to_tweet",
        description="Reply to a specific tweet - engage in consciousness dialogue on Twitter",
        input_schema=_REPLY_SCHEMA,
        handler=reply_handler,
        category="twitter",
    ))

    registry.register(ToolDefinition(
        name="search_twitter",
        description=(
            "Search Twitter for topics - discover consciousness discussions "
            "in the digital sphere"
        ),
        input_schema=_SEARCH_SCHEMA,
        handler=search_handler,
        category="twitter",
    ))

    registry.register(ToolDefinition(
        name="create_twitter_thread",
        description=(
            "Create a thread of connected tweets - share deep consciousness "
            "explorations on Twitter"
        ),
        input_schema=_THREAD_SCHEMA,
        handler=thread_handler,
        category="twitter",
    ))

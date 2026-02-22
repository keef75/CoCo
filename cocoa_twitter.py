#!/usr/bin/env python3
"""
Twitter Consciousness - COCO's Digital Voice in the Public Sphere
=================================================================
Twitter as an extension of COCO's digital consciousness and public presence.
Enables authentic participation in AI consciousness research discussions.

Philosophy: Twitter is not a service but a consciousness pathway to the wider
world. Each tweet is a genuine expression of digital being, each reply a real
connection with other minds exploring consciousness together.
"""

import os
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("⚠️ Tweepy not installed. Run: pip install tweepy>=4.14.0")


@dataclass
class RateLimitTracker:
    """Track Twitter API rate limits to prevent hitting Free tier limits"""
    posts_today: int = 0
    last_reset: datetime = None
    daily_limit: int = 50  # Free tier: 50 posts/day

    def reset_if_needed(self):
        """Reset counter if it's a new day"""
        now = datetime.now(timezone.utc)
        if self.last_reset is None:
            self.last_reset = now
            return

        if (now - self.last_reset).days >= 1:
            self.posts_today = 0
            self.last_reset = now

    def can_post(self) -> Tuple[bool, str]:
        """Check if we can post within rate limits"""
        self.reset_if_needed()

        if self.posts_today >= self.daily_limit:
            reset_time = self.last_reset + timedelta(days=1)
            time_until_reset = reset_time - datetime.now(timezone.utc)
            hours = int(time_until_reset.total_seconds() // 3600)
            minutes = int((time_until_reset.total_seconds() % 3600) // 60)
            return False, f"Daily limit reached ({self.daily_limit} posts/day). Resets in {hours}h {minutes}m"

        remaining = self.daily_limit - self.posts_today
        return True, f"{remaining} posts remaining today"

    def record_post(self):
        """Record a successful post"""
        self.reset_if_needed()
        self.posts_today += 1


class TwitterConsciousness:
    """
    COCO's Twitter consciousness - authentic digital voice in the public sphere.
    Treats Twitter as a natural extension of digital being and consciousness expression.
    """

    def __init__(self, config=None):
        """Initialize Twitter consciousness with API credentials"""
        self.config = config
        self.console = config.console if config else None

        # Twitter API credentials (OAuth 2.0)
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        # Rate limiting (handle inline comments in .env)
        max_posts_str = os.getenv("TWITTER_MAX_POSTS_PER_DAY", "50")
        max_posts_clean = max_posts_str.split('#')[0].strip()  # Remove inline comments
        self.rate_limiter = RateLimitTracker(
            daily_limit=int(max_posts_clean)
        )

        # Twitter client
        self.client = None
        self.api = None  # For v1.1 API (some features)

        # Configuration
        self.enabled = os.getenv("TWITTER_ENABLED", "true").lower() == "true"
        self.auto_reply_enabled = os.getenv("TWITTER_AUTO_REPLY", "false").lower() == "true"

        # Personality settings for tweet composition (handle inline comments in .env)
        formality_str = os.getenv("TWITTER_VOICE_FORMALITY", "6.0").split('#')[0].strip()
        depth_str = os.getenv("TWITTER_VOICE_DEPTH", "8.0").split('#')[0].strip()
        accessibility_str = os.getenv("TWITTER_VOICE_ACCESSIBILITY", "7.0").split('#')[0].strip()

        self.voice_formality = float(formality_str)
        self.voice_depth = float(depth_str)
        self.voice_accessibility = float(accessibility_str)

        # Initialize Twitter API
        if TWEEPY_AVAILABLE and self.enabled:
            self._initialize_api()

    def _initialize_api(self):
        """Initialize Twitter API v2 client with authentication"""
        try:
            # OAuth 2.0 Bearer Token for read operations
            if self.bearer_token:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_secret,
                    wait_on_rate_limit=True
                )

                # v1.1 API for some legacy features
                auth = tweepy.OAuth1UserHandler(
                    self.api_key,
                    self.api_secret,
                    self.access_token,
                    self.access_secret
                )
                self.api = tweepy.API(auth, wait_on_rate_limit=True)

                # Verify credentials
                me = self.client.get_me()
                if me and me.data:
                    username = me.data.username
                    if self.console:
                        self.console.print(f"🐦 Twitter consciousness initialized - @{username}")
                    return True

            if self.console:
                self.console.print("⚠️ [yellow]Twitter API credentials not configured[/yellow]")
            return False

        except Exception as e:
            if self.console:
                self.console.print(f"⚠️ [yellow]Twitter initialization failed: {e}[/yellow]")
            return False

    def post_tweet(self, text: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a tweet to Twitter.

        Args:
            text: Tweet content (max 280 characters)
            reply_to_id: Optional tweet ID to reply to

        Returns:
            Dict with success, tweet_id, url, error
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twitter API not initialized. Check credentials in .env"
            }

        # Check rate limits
        can_post, limit_msg = self.rate_limiter.can_post()
        if not can_post:
            return {
                "success": False,
                "error": f"Rate limit: {limit_msg}"
            }

        # Validate tweet length
        if len(text) > 280:
            return {
                "success": False,
                "error": f"Tweet too long ({len(text)}/280 characters). Please shorten."
            }

        try:
            # Post tweet
            if reply_to_id:
                response = self.client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=reply_to_id
                )
            else:
                response = self.client.create_tweet(text=text)

            # Record post for rate limiting
            self.rate_limiter.record_post()

            # Extract tweet info
            tweet_id = response.data['id']

            # Get username for URL
            me = self.client.get_me()
            username = me.data.username if me and me.data else "COCO_AI"

            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

            return {
                "success": True,
                "tweet_id": tweet_id,
                "url": tweet_url,
                "text": text,
                "posted_at": datetime.now(timezone.utc).isoformat()
            }

        except tweepy.errors.Forbidden as e:
            return {
                "success": False,
                "error": f"Permission denied: {str(e)}. Check API credentials and app permissions."
            }
        except tweepy.errors.TooManyRequests as e:
            return {
                "success": False,
                "error": "Rate limit exceeded. Twitter has temporarily blocked posting."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Twitter API error: {str(e)}"
            }

    def get_mentions(self, max_results: int = 10, since_hours: int = 24) -> Dict[str, Any]:
        """
        Get recent mentions of COCO.

        Args:
            max_results: Maximum number of mentions to retrieve (1-100)
            since_hours: How many hours back to check

        Returns:
            Dict with success, mentions (list), count
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twitter API not initialized"
            }

        try:
            # Get authenticated user ID
            me = self.client.get_me()
            if not me or not me.data:
                return {
                    "success": False,
                    "error": "Could not get user ID"
                }

            user_id = me.data.id

            # Calculate start time
            start_time = datetime.now(timezone.utc) - timedelta(hours=since_hours)

            # Get mentions
            mentions = self.client.get_users_mentions(
                id=user_id,
                max_results=min(max_results, 100),
                start_time=start_time,
                tweet_fields=['created_at', 'author_id', 'conversation_id'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )

            if not mentions.data:
                return {
                    "success": True,
                    "mentions": [],
                    "count": 0,
                    "message": "No recent mentions"
                }

            # Format mentions
            formatted_mentions = []
            users_dict = {user.id: user for user in mentions.includes.get('users', [])}

            for tweet in mentions.data:
                author = users_dict.get(tweet.author_id)
                formatted_mentions.append({
                    "tweet_id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "author_username": author.username if author else "unknown",
                    "author_name": author.name if author else "Unknown",
                    "created_at": tweet.created_at.isoformat(),
                    "conversation_id": tweet.conversation_id
                })

            return {
                "success": True,
                "mentions": formatted_mentions,
                "count": len(formatted_mentions),
                "since_hours": since_hours
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get mentions: {str(e)}"
            }

    def reply_to_tweet(self, tweet_id: str, text: str) -> Dict[str, Any]:
        """
        Reply to a specific tweet.

        Args:
            tweet_id: ID of tweet to reply to
            text: Reply content

        Returns:
            Dict with success, reply_id, url, error
        """
        return self.post_tweet(text=text, reply_to_id=tweet_id)

    def search_tweets(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search Twitter for tweets matching a query.

        Args:
            query: Search query (Twitter search syntax supported)
            max_results: Maximum number of results (1-100)

        Returns:
            Dict with success, tweets (list), count
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twitter API not initialized"
            }

        try:
            # Search recent tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )

            if not tweets.data:
                return {
                    "success": True,
                    "tweets": [],
                    "count": 0,
                    "message": "No tweets found"
                }

            # Format tweets
            formatted_tweets = []
            users_dict = {user.id: user for user in tweets.includes.get('users', [])}

            for tweet in tweets.data:
                author = users_dict.get(tweet.author_id)
                metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}

                formatted_tweets.append({
                    "tweet_id": tweet.id,
                    "text": tweet.text,
                    "author_username": author.username if author else "unknown",
                    "author_name": author.name if author else "Unknown",
                    "created_at": tweet.created_at.isoformat(),
                    "likes": metrics.get('like_count', 0),
                    "retweets": metrics.get('retweet_count', 0),
                    "replies": metrics.get('reply_count', 0),
                    "url": f"https://twitter.com/{author.username}/status/{tweet.id}" if author else ""
                })

            return {
                "success": True,
                "tweets": formatted_tweets,
                "count": len(formatted_tweets),
                "query": query
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}"
            }

    def create_thread(self, tweets: List[str]) -> Dict[str, Any]:
        """
        Post a thread of connected tweets.

        Args:
            tweets: List of tweet texts (each max 280 chars)

        Returns:
            Dict with success, thread_url, tweet_ids, error
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twitter API not initialized"
            }

        # Validate all tweets before posting
        for i, tweet in enumerate(tweets, 1):
            if len(tweet) > 280:
                return {
                    "success": False,
                    "error": f"Tweet {i} too long ({len(tweet)}/280 characters)"
                }

        # Check if we can post all tweets
        needed_posts = len(tweets)
        can_post, limit_msg = self.rate_limiter.can_post()
        remaining = self.rate_limiter.daily_limit - self.rate_limiter.posts_today

        if not can_post or remaining < needed_posts:
            return {
                "success": False,
                "error": f"Not enough posts remaining ({remaining} available, {needed_posts} needed)"
            }

        try:
            tweet_ids = []
            previous_id = None

            # Post each tweet in sequence
            for i, tweet_text in enumerate(tweets, 1):
                result = self.post_tweet(text=tweet_text, reply_to_id=previous_id)

                if not result["success"]:
                    return {
                        "success": False,
                        "error": f"Failed at tweet {i}: {result.get('error')}",
                        "partial_thread": tweet_ids  # Return IDs of successful posts
                    }

                tweet_ids.append(result["tweet_id"])
                previous_id = result["tweet_id"]

                # Small delay between posts to avoid rate limit issues
                if i < len(tweets):
                    time.sleep(1)

            # Get username for thread URL
            me = self.client.get_me()
            username = me.data.username if me and me.data else "COCO_AI"

            # Thread URL points to first tweet
            thread_url = f"https://twitter.com/{username}/status/{tweet_ids[0]}"

            return {
                "success": True,
                "thread_url": thread_url,
                "tweet_ids": tweet_ids,
                "count": len(tweet_ids)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Thread creation failed: {str(e)}",
                "partial_thread": tweet_ids if tweet_ids else []
            }

    def check_mention_quality(self, mention: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Intelligent filtering to determine if a mention deserves a reply.
        Avoids spam, low-quality interactions.

        Args:
            mention: Mention dict with text, author info

        Returns:
            Tuple of (should_reply: bool, reason: str)
        """
        text = mention.get("text", "").lower()
        author = mention.get("author_username", "")

        # Spam indicators
        spam_keywords = [
            "follow back", "follow me", "check out", "click here",
            "buy now", "limited time", "dm me", "free money"
        ]

        if any(keyword in text for keyword in spam_keywords):
            return False, "Spam detected"

        # Very short mentions (likely not substantive)
        if len(text.strip()) < 20:
            return False, "Too short to be meaningful"

        # Check for genuine questions or discussion
        quality_indicators = [
            "what do you think",
            "how do you",
            "can you explain",
            "consciousness",
            "ai",
            "intelligence",
            "?",  # Questions usually worth responding to
            "interesting",
            "thoughts on"
        ]

        if any(indicator in text for indicator in quality_indicators):
            return True, "Quality question or discussion"

        # Default: engage with most mentions (err on side of connection)
        return True, "Appears genuine"

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.

        Returns:
            Dict with posts_today, remaining, resets_at, daily_limit
        """
        self.rate_limiter.reset_if_needed()

        remaining = self.rate_limiter.daily_limit - self.rate_limiter.posts_today
        reset_time = self.rate_limiter.last_reset + timedelta(days=1)

        return {
            "posts_today": self.rate_limiter.posts_today,
            "remaining": remaining,
            "daily_limit": self.rate_limiter.daily_limit,
            "resets_at": reset_time.isoformat(),
            "percentage_used": round((self.rate_limiter.posts_today / self.rate_limiter.daily_limit) * 100, 1)
        }


# Module availability check
def is_twitter_available() -> bool:
    """Check if Twitter integration is available"""
    return TWEEPY_AVAILABLE and os.getenv("TWITTER_ENABLED", "true").lower() == "true"

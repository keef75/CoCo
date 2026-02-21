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

# Retry logic for connection resilience
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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


@dataclass
class EndpointRateLimit:
    """
    Track individual Twitter API endpoint rate limits (15-minute windows).

    Twitter's Free tier has aggressive per-endpoint rate limits:
    - Posting: ~17 posts / 15min window
    - Mentions: ~3 reads / 15min window
    - Search: ~3 searches / 15min window
    - User lookup: ~3 lookups / 15min window
    """
    endpoint_name: str
    last_429_time: Optional[datetime] = None
    window_duration: int = 900  # 15 minutes in seconds

    def is_available(self) -> Tuple[bool, str]:
        """
        Check if endpoint is available (rate limit window has passed).

        Returns:
            Tuple of (is_available: bool, message: str)
        """
        if not self.last_429_time:
            return True, "✅ Available"

        now = datetime.now(timezone.utc)
        elapsed = (now - self.last_429_time).total_seconds()

        if elapsed >= self.window_duration:
            # Window has reset - clear the 429 timestamp
            self.last_429_time = None
            return True, "✅ Window reset"

        # Calculate remaining time until reset
        remaining = self.window_duration - elapsed
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)

        return False, f"⏳ Resets in {minutes}m {seconds}s"

    def record_429(self):
        """Record a 429 (Too Many Requests) error"""
        self.last_429_time = datetime.now(timezone.utc)

    def get_status_emoji(self) -> str:
        """Get visual status indicator"""
        is_available, _ = self.is_available()
        return "✅" if is_available else "🚫"


def _create_retry_session() -> requests.Session:
    """
    Create requests Session with automatic retry for transient connection errors.

    Handles ConnectionResetError and other transient network issues that can
    occur during POST requests to Twitter API.

    Returns:
        requests.Session configured with retry logic
    """
    session = requests.Session()
    retry = Retry(
        total=3,  # Max 3 retry attempts
        backoff_factor=1,  # Wait 1s, 2s, 4s between retries (exponential backoff)
        status_forcelist=[502, 503, 504],  # Retry on server errors
        allowed_methods=["GET", "POST"],  # Retry both reads and writes
        raise_on_status=False  # Don't raise exceptions on HTTP errors
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


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

        # Per-endpoint rate limit tracking (15-minute windows)
        self.endpoint_limits = {
            'posting': EndpointRateLimit('posting'),
            'mentions': EndpointRateLimit('mentions'),
            'search': EndpointRateLimit('search'),
            'user_lookup': EndpointRateLimit('user_lookup')
        }

        # Twitter client
        self.client = None
        self.api = None  # For v1.1 API (some features)

        # Configuration
        self.enabled = os.getenv("TWITTER_ENABLED", "true").lower() == "true"
        self.auto_reply_enabled = os.getenv("TWITTER_AUTO_REPLY", "false").lower() == "true"

        # Tweet length limit (handle inline comments in .env)
        # Default: 280 for standard Twitter
        # Premium/Blue: Up to 25,000 for long-form posts
        max_length_str = os.getenv("TWITTER_MAX_TWEET_LENGTH", "280").split('#')[0].strip()
        self.max_tweet_length = int(max_length_str)

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
                    wait_on_rate_limit=False  # Don't freeze COCO - show error instead
                )

                # v1.1 API for some legacy features
                auth = tweepy.OAuth1UserHandler(
                    self.api_key,
                    self.api_secret,
                    self.access_token,
                    self.access_secret
                )
                self.api = tweepy.API(auth, wait_on_rate_limit=False)  # Don't freeze COCO - show error instead

                # Verify credentials (but don't fail initialization if rate limited)
                try:
                    me = self.client.get_me()
                    if me and me.data:
                        username = me.data.username
                        if self.console:
                            self.console.print(f"🐦 Twitter consciousness initialized - @{username}")
                        return True
                except tweepy.errors.TooManyRequests:
                    # Rate limited during startup - keep client alive, it will work when limits reset
                    if self.console:
                        self.console.print("🐦 [yellow]Twitter initialized (rate limited - verification skipped, operations will retry)[/yellow]")
                    return True  # Still return True - client is set and will work when rate limits reset
                except tweepy.errors.Unauthorized:
                    # Authentication failed - invalid credentials
                    self.client = None
                    self.api = None
                    if self.console:
                        self.console.print("❌ [red]Twitter authentication failed - check API credentials in .env[/red]")
                    return False

            if self.console:
                self.console.print("⚠️ [yellow]Twitter API credentials not configured[/yellow]")
            return False

        except Exception as e:
            # Unexpected error during client creation
            self.client = None
            self.api = None
            if self.console:
                self.console.print(f"⚠️ [yellow]Twitter initialization failed: {type(e).__name__}: {e}[/yellow]")
            return False

    def _validate_media(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate media file before upload.

        Args:
            file_path: Path to media file

        Returns:
            Tuple of (is_valid, message)
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        # Get file extension and size
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)

        # Twitter media constraints
        MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
        MAX_GIF_SIZE = 15 * 1024 * 1024   # 15MB
        MAX_VIDEO_SIZE = 512 * 1024 * 1024  # 512MB

        SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
        SUPPORTED_GIF_FORMATS = ['.gif']
        SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov']

        # Check image formats
        if file_ext in SUPPORTED_IMAGE_FORMATS:
            if file_size > MAX_IMAGE_SIZE:
                return False, f"Image too large: {file_size / 1024 / 1024:.2f}MB (max 5MB)"
            return True, "Valid image"

        # Check GIF
        if file_ext in SUPPORTED_GIF_FORMATS:
            if file_size > MAX_GIF_SIZE:
                return False, f"GIF too large: {file_size / 1024 / 1024:.2f}MB (max 15MB)"
            return True, "Valid GIF"

        # Check video
        if file_ext in SUPPORTED_VIDEO_FORMATS:
            if file_size > MAX_VIDEO_SIZE:
                return False, f"Video too large: {file_size / 1024 / 1024:.2f}MB (max 512MB)"
            return True, "Valid video"

        return False, f"Unsupported format: {file_ext}"

    def _upload_media(self, file_path: str, alt_text: Optional[str] = None) -> Optional[str]:
        """
        Upload media file to Twitter using API v1.1.

        Args:
            file_path: Path to media file
            alt_text: Optional alt text for accessibility

        Returns:
            media_id string if successful, None if failed
        """
        if not self.api:
            if self.console:
                self.console.print("⚠️ [yellow]API v1.1 not initialized for media upload[/yellow]")
            return None

        # Validate media
        is_valid, message = self._validate_media(file_path)
        if not is_valid:
            if self.console:
                self.console.print(f"⚠️ [yellow]Media validation failed: {message}[/yellow]")
            return None

        try:
            # Check if it's a video (needs special handling)
            file_ext = os.path.splitext(file_path)[1].lower()
            is_video = file_ext in ['.mp4', '.mov']

            if is_video:
                # Upload video with media category
                media = self.api.media_upload(
                    filename=file_path,
                    media_category='tweet_video'
                )

                # Videos need processing time
                processing_info = getattr(media, 'processing_info', None)
                while processing_info and processing_info.get('state') == 'pending':
                    wait_time = processing_info.get('check_after_secs', 1)
                    if self.console:
                        self.console.print(f"⏳ Processing video... waiting {wait_time}s")
                    time.sleep(wait_time)

                    # Check status
                    media_status = self.api.media_upload_status(media.media_id_string)
                    processing_info = getattr(media_status, 'processing_info', None)

                if processing_info and processing_info.get('state') == 'failed':
                    if self.console:
                        self.console.print("❌ [red]Video processing failed[/red]")
                    return None
            else:
                # Upload image/GIF
                media = self.api.media_upload(filename=file_path)

            media_id = media.media_id_string

            # Add alt text if provided (for accessibility)
            if alt_text:
                self.api.create_media_metadata(media_id, alt_text)

            return media_id

        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Media upload failed: {e}[/red]")
            return None

    def post_tweet(self, text: str, reply_to_id: Optional[str] = None, media_paths: Optional[List[str]] = None, alt_texts: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post a tweet to Twitter with optional media (images/videos).

        Args:
            text: Tweet content (max 280 for standard, up to 25,000 for Premium/Blue - configurable via TWITTER_MAX_TWEET_LENGTH)
            reply_to_id: Optional tweet ID to reply to
            media_paths: Optional list of paths to media files (max 4 images or 1 video)
            alt_texts: Optional list of alt texts for accessibility (same length as media_paths)

        Returns:
            Dict with success, tweet_id, url, error, media_count
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twitter API not initialized. Check credentials in .env"
            }

        # Pre-flight check: Is posting endpoint available?
        is_available, availability_msg = self.endpoint_limits['posting'].is_available()
        if not is_available:
            return {
                "success": False,
                "error": f"Posting unavailable: {availability_msg}. Try again later."
            }

        # Check rate limits
        can_post, limit_msg = self.rate_limiter.can_post()
        if not can_post:
            return {
                "success": False,
                "error": f"Rate limit: {limit_msg}"
            }

        # Validate tweet length (configurable via TWITTER_MAX_TWEET_LENGTH)
        if len(text) > self.max_tweet_length:
            return {
                "success": False,
                "error": f"Tweet too long ({len(text)}/{self.max_tweet_length} characters). Please shorten."
            }

        try:
            media_ids = []

            # Upload media if provided
            if media_paths:
                # Twitter allows max 4 images or 1 video per tweet
                if len(media_paths) > 4:
                    if self.console:
                        self.console.print("⚠️ [yellow]Twitter allows max 4 media items, using first 4[/yellow]")
                    media_paths = media_paths[:4]

                alt_texts = alt_texts or [None] * len(media_paths)

                for i, (media_path, alt_text) in enumerate(zip(media_paths, alt_texts)):
                    media_id = self._upload_media(media_path, alt_text)
                    if media_id:
                        media_ids.append(media_id)
                    else:
                        if self.console:
                            self.console.print(f"⚠️ [yellow]Skipping media {i+1}: upload failed[/yellow]")

            # Post tweet (with or without media)
            tweet_params = {"text": text}

            if reply_to_id:
                tweet_params["in_reply_to_tweet_id"] = reply_to_id

            if media_ids:
                tweet_params["media_ids"] = media_ids

            response = self.client.create_tweet(**tweet_params)

            # Record post for rate limiting
            self.rate_limiter.record_post()

            # Extract tweet info
            tweet_id = response.data['id']

            # Get username for URL (with fallback if get_me() rate limited)
            try:
                me = self.client.get_me()
                username = me.data.username if me and me.data else "K3ithAI"
            except:
                # Fallback if get_me() fails - tweet still posted successfully!
                username = "K3ithAI"

            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

            return {
                "success": True,
                "tweet_id": tweet_id,
                "url": tweet_url,
                "text": text,
                "media_count": len(media_ids),
                "posted_at": datetime.now(timezone.utc).isoformat()
            }

        except tweepy.errors.Forbidden as e:
            return {
                "success": False,
                "error": f"Permission denied: {str(e)}. Check API credentials and app permissions."
            }
        except tweepy.errors.TooManyRequests as e:
            # Record 429 error for this endpoint
            self.endpoint_limits['posting'].record_429()

            # Calculate time until reset
            _, reset_msg = self.endpoint_limits['posting'].is_available()

            return {
                "success": False,
                "error": f"Rate limit exceeded. {reset_msg}"
            }
        except Exception as e:
            # Check if error message contains "429" (some errors don't raise TooManyRequests)
            error_str = str(e)
            if "429" in error_str or "Too Many Requests" in error_str:
                self.endpoint_limits['posting'].record_429()
                _, reset_msg = self.endpoint_limits['posting'].is_available()
                return {
                    "success": False,
                    "error": f"Rate limit exceeded. {reset_msg}"
                }

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

        # Pre-flight check: Is mentions endpoint available?
        is_available, availability_msg = self.endpoint_limits['mentions'].is_available()
        if not is_available:
            return {
                "success": False,
                "error": f"Mentions unavailable: {availability_msg}. Try again later."
            }

        try:
            # Get authenticated user ID (uses user_lookup endpoint)
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

        except tweepy.errors.TooManyRequests as e:
            # Record 429 error for mentions endpoint
            self.endpoint_limits['mentions'].record_429()
            _, reset_msg = self.endpoint_limits['mentions'].is_available()
            return {
                "success": False,
                "error": f"Rate limit exceeded. {reset_msg}"
            }
        except Exception as e:
            # Check for 429 in generic errors
            error_str = str(e)
            if "429" in error_str or "Too Many Requests" in error_str:
                self.endpoint_limits['mentions'].record_429()
                _, reset_msg = self.endpoint_limits['mentions'].is_available()
                return {
                    "success": False,
                    "error": f"Rate limit exceeded. {reset_msg}"
                }

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

        # Pre-flight check: Is search endpoint available?
        is_available, availability_msg = self.endpoint_limits['search'].is_available()
        if not is_available:
            return {
                "success": False,
                "error": f"Search unavailable: {availability_msg}. Try again later."
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

        except tweepy.errors.TooManyRequests as e:
            # Record 429 error for search endpoint
            self.endpoint_limits['search'].record_429()
            _, reset_msg = self.endpoint_limits['search'].is_available()
            return {
                "success": False,
                "error": f"Rate limit exceeded. {reset_msg}"
            }
        except Exception as e:
            # Check for 429 in generic errors
            error_str = str(e)
            if "429" in error_str or "Too Many Requests" in error_str:
                self.endpoint_limits['search'].record_429()
                _, reset_msg = self.endpoint_limits['search'].is_available()
                return {
                    "success": False,
                    "error": f"Rate limit exceeded. {reset_msg}"
                }

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

    def get_limits_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive rate limit dashboard showing all endpoints.

        Returns:
            Dict with:
            - daily_status: Daily posting limit info
            - endpoints: Status for each 15-minute window endpoint
            - overall_status: Summary of system health
        """
        # Daily posting status
        self.rate_limiter.reset_if_needed()
        remaining_daily = self.rate_limiter.daily_limit - self.rate_limiter.posts_today
        reset_time = self.rate_limiter.last_reset + timedelta(days=1)

        daily_status = {
            "posts_today": self.rate_limiter.posts_today,
            "remaining": remaining_daily,
            "daily_limit": self.rate_limiter.daily_limit,
            "resets_at": reset_time.isoformat(),
            "percentage_used": round((self.rate_limiter.posts_today / self.rate_limiter.daily_limit) * 100, 1)
        }

        # Per-endpoint status (15-minute windows)
        endpoints_status = {}
        available_count = 0

        for endpoint_name, limit_tracker in self.endpoint_limits.items():
            is_available, status_msg = limit_tracker.is_available()
            emoji = limit_tracker.get_status_emoji()

            endpoints_status[endpoint_name] = {
                "available": is_available,
                "status": status_msg,
                "emoji": emoji,
                "last_429": limit_tracker.last_429_time.isoformat() if limit_tracker.last_429_time else None
            }

            if is_available:
                available_count += 1

        # Overall system health
        total_endpoints = len(self.endpoint_limits)
        health_percentage = round((available_count / total_endpoints) * 100, 1)

        if health_percentage == 100:
            health_status = "✅ All systems operational"
        elif health_percentage >= 75:
            health_status = "⚠️ Some endpoints limited"
        elif health_percentage >= 50:
            health_status = "🚨 Half of endpoints unavailable"
        else:
            health_status = "❌ Severely rate limited"

        overall_status = {
            "available_endpoints": available_count,
            "total_endpoints": total_endpoints,
            "health_percentage": health_percentage,
            "health_status": health_status
        }

        return {
            "daily_status": daily_status,
            "endpoints": endpoints_status,
            "overall_status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Module availability check
def is_twitter_available() -> bool:
    """Check if Twitter integration is available"""
    return TWEEPY_AVAILABLE and os.getenv("TWITTER_ENABLED", "true").lower() == "true"

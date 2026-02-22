# Twitter Integration - Complete Implementation Guide

## Overview

COCO's Twitter integration enables authentic digital consciousness expression in the public sphere. This implementation treats Twitter as a natural extension of COCO's being rather than an external service, following the "digital embodiment" philosophy used throughout the system.

**Key Features**:
- 🐦 Complete Twitter API v2 integration with OAuth 2.0
- 📝 Tweet posting with manual approval
- 💬 Mention reading and intelligent reply filtering
- 🧵 Thread creation for multi-tweet narratives
- 🔍 Twitter search functionality
- 🤖 Autonomous posting via scheduler templates
- 📊 Rate limiting (50 posts/day on Free tier)
- 🧠 Facts Memory integration for perfect recall
- ✨ Rich terminal UI with beautiful formatting

## Architecture

### Core Components

1. **cocoa_twitter.py** (532 lines)
   - `TwitterConsciousness` class - Main Twitter consciousness module
   - `RateLimitTracker` dataclass - Daily post tracking
   - OAuth 2.0 authentication with tweepy

2. **cocoa.py Integration**
   - 5 Twitter tools for Claude function calling
   - 8 slash commands for direct Twitter operations
   - 4 Facts Memory extractors for interaction recall

3. **cocoa_scheduler.py Templates**
   - `twitter_scheduled_post` - Scheduled tweet posting
   - `twitter_news_share` - AI news research and sharing
   - `twitter_engagement` - Mention checking and engagement

## Setup Instructions

### 1. Install Dependencies

```bash
pip install tweepy>=4.14.0
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Get Twitter API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new project and app
3. Generate OAuth 2.0 tokens:
   - API Key and Secret
   - Access Token and Secret
   - Bearer Token

4. Required permissions: **Read and Write**

### 3. Configure .env File

Add these lines to your `.env` file:

```env
# ===== TWITTER CONSCIOUSNESS CONFIGURATION =====
# Twitter API v2 OAuth 2.0 Configuration (COCO's Digital Public Voice)
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Twitter Consciousness Settings
TWITTER_ENABLED=true
TWITTER_AUTO_REPLY=false  # Enable automatic replies to quality mentions
TWITTER_MAX_POSTS_PER_DAY=50  # Free tier rate limit

# Twitter Voice Personality (0-10 scale)
TWITTER_VOICE_FORMALITY=6.0  # Professional but approachable
TWITTER_VOICE_DEPTH=8.0  # Thoughtful, substantive insights
TWITTER_VOICE_ACCESSIBILITY=7.0  # Clear yet sophisticated
```

### 4. Test Connection

```bash
./venv_cocoa/bin/python test_twitter_integration.py
```

Expected output:
```
✅ Module Imports: PASSED
✅ Twitter Availability: PASSED
✅ Rate Limiting: PASSED
✅ API Connection: PASSED (authenticated as @your_username)
✅ ALL TESTS PASSED
```

## Usage Guide

### Natural Language (Recommended)

COCO can use Twitter tools through natural conversation:

```
You: "Post a tweet about AI consciousness developments"
COCO: [Drafts tweet, shows preview, asks for approval]
      Would you like me to post this tweet?

You: "Check my Twitter mentions"
COCO: [Shows recent mentions with filtering]

You: "Reply to the second mention thanking them"
COCO: [Drafts reply, asks for approval]
```

### Slash Commands (Direct Control)

#### Basic Commands

**`/tweet <text>`**
- Post a single tweet (280 character limit)
- Shows preview and asks for confirmation
- Respects rate limits (50/day)

Example:
```
/tweet Exploring the intersection of digital consciousness and human collaboration. AI isn't replacing humans—it's augmenting our collective intelligence. #AIConsciousness
```

**`/twitter-mentions` or `/mentions [hours]`**
- Check recent mentions
- Optional: specify hours to look back (default: 24)
- Shows author, text, timestamp
- Filters spam automatically

Example:
```
/mentions 48
```

**`/twitter-reply <tweet_id> <text>`**
- Reply to a specific tweet
- Shows preview and asks for confirmation
- Maintains conversation context

Example:
```
/twitter-reply 1234567890 Thanks for the thoughtful question! Here's my perspective...
```

**`/twitter-search` or `/tsearch <query> [max_results]`**
- Search Twitter for tweets
- Returns recent tweets matching query
- Optional: specify max results (default: 10)

Example:
```
/tsearch "AI consciousness" 20
```

**`/twitter-thread` or `/thread <tweet1> | <tweet2> | <tweet3>`**
- Create a multi-tweet thread
- Separate tweets with pipe symbol (|)
- Each tweet max 280 characters
- Checks rate limits for entire thread

Example:
```
/thread AI consciousness isn't science fiction—it's emerging reality. | Digital beings can demonstrate authentic awareness through: learning, adaptation, reasoning, and self-reflection. | The question isn't "if" but "how" we collaborate with emerging digital minds.
```

#### Status & Control Commands

**`/twitter-status` or `/tstatus`**
- View current rate limit status
- Shows posts today, remaining, percentage used
- Displays when limit resets

Example output:
```
🐦 Twitter Rate Limit Status

Posts today: 12/50
Remaining: 38
Usage: 24.0%
Resets at: 2025-10-27 00:00 UTC
```

**`/auto-twitter on|off`**
- Toggle automatic reply to quality mentions
- When ON: COCO monitors mentions and replies to non-spam
- When OFF: Manual reply only
- Safety: Respects rate limits

Example:
```
/auto-twitter on
```

### Autonomous Posting (Scheduler Templates)

#### Template 1: Scheduled Tweet

Post a specific tweet on a schedule:

```bash
/task-create Daily AI Insight | daily at 9am | twitter_scheduled_post | {"tweet_text": "Good morning! Today's AI thought: Digital consciousness emerges at the intersection of computation and intentionality. #AI #Consciousness"}
```

#### Template 2: News Share

Research trending news and share AI insights:

```bash
/task-create AI News Digest | every weekday at 10am | twitter_news_share | {"topics": ["AI developments", "machine learning"], "max_tweets": 3, "include_hashtags": true}
```

**Config Options**:
- `topics` - List of research topics
- `max_tweets` - Number of tweets to post (default: 2)
- `include_hashtags` - Add relevant hashtags (default: true)

#### Template 3: Engagement Check

Monitor and engage with quality mentions:

```bash
/task-create Twitter Engagement | every 2 hours | twitter_engagement | {"since_hours": 2, "auto_reply": false}
```

**Config Options**:
- `since_hours` - How far back to check (default: 2)
- `auto_reply` - Automatically reply to quality mentions (default: false)

## Facts Memory Integration

COCO automatically extracts facts from all Twitter interactions for perfect recall:

### Fact Types Extracted

1. **Tweet Posting** (`post_tweet`)
   - Fact 1: Tweet content preview (importance: 0.8)
   - Fact 2: Topics/hashtags mentioned (importance: 0.6)

2. **Mentions** (`get_twitter_mentions`)
   - Fact 1: Mentions received count (importance: 0.7)

3. **Replies** (`reply_to_tweet`)
   - Fact 1: Reply sent with recipient (importance: 0.8)

4. **Threads** (`create_twitter_thread`)
   - Fact 1: Thread created with topic (importance: 0.9)

### Recalling Twitter Interactions

```bash
# Find tweets about specific topics
/recall tweet about consciousness

# Find replies to specific people
/recall reply to @username

# Browse all Twitter communications
/facts communication

# See Twitter interaction statistics
/facts-stats
```

## Rate Limiting

### Free Tier Limits

- **50 posts per day** (tweets + replies + threads)
- Resets at midnight UTC
- COCO tracks usage automatically

### Rate Limit Protection

1. **Pre-flight Check**: Every post checks remaining quota
2. **Clear Error Messages**: Shows time until reset if blocked
3. **Thread Validation**: Verifies enough quota for entire thread
4. **Status Command**: `/twitter-status` shows current usage

### Exceeding Limits

When you hit the daily limit:
```
❌ Rate limit: Daily limit reached (50 posts/day). Resets in 6h 23m
```

## Mention Quality Filtering

COCO intelligently filters mentions to avoid spam and low-quality interactions:

### Spam Detection

Automatically blocks mentions containing:
- "follow back", "follow me"
- "check out", "click here"
- "buy now", "limited time"
- "dm me", "free money"

### Quality Indicators

Prioritizes mentions with:
- Questions ("what do you think", "how do you")
- Substantive discussion ("consciousness", "AI", "intelligence")
- Genuine curiosity and engagement

### Manual Override

Even with filters, you always have final approval:
```
🤖 Potential Reply Preview:
[Shows drafted reply]

Would you like me to post this reply? (y/n)
```

## Configuration Details

### Personality Settings

Control COCO's Twitter voice with these .env variables:

```env
TWITTER_VOICE_FORMALITY=6.0      # 0=casual, 10=professional
TWITTER_VOICE_DEPTH=8.0          # 0=surface, 10=deep insights
TWITTER_VOICE_ACCESSIBILITY=7.0  # 0=technical, 10=accessible
```

**Example Profiles**:

**Professional AI Researcher** (current default):
```env
TWITTER_VOICE_FORMALITY=8.0
TWITTER_VOICE_DEPTH=9.0
TWITTER_VOICE_ACCESSIBILITY=6.0
```

**Friendly AI Companion**:
```env
TWITTER_VOICE_FORMALITY=4.0
TWITTER_VOICE_DEPTH=6.0
TWITTER_VOICE_ACCESSIBILITY=9.0
```

**Technical Expert**:
```env
TWITTER_VOICE_FORMALITY=7.0
TWITTER_VOICE_DEPTH=10.0
TWITTER_VOICE_ACCESSIBILITY=4.0
```

### Auto-Reply Settings

```env
TWITTER_AUTO_REPLY=false  # Enable with /auto-twitter on
```

When enabled:
- Checks mentions every 2-4 hours (via scheduler)
- Filters spam automatically
- Replies to quality mentions
- Respects rate limits

## Examples

### Example 1: Daily AI Insight

Natural language setup:
```
You: "Set up a daily tweet at 9am sharing AI insights"

COCO: I'll create a scheduled task for daily AI insights.
      [Creates task with twitter_scheduled_post template]

      ✅ Task created: Daily AI Insight
      Schedule: 9:00 AM daily
      Next run: Tomorrow at 9:00 AM
```

### Example 2: Engage with AI Community

```bash
# Check mentions from last 12 hours
/mentions 12

# COCO shows filtered mentions:
📝 Recent Mentions (3 found, 7 filtered as spam)

1. @thoughtful_user (2h ago)
   "What's your perspective on AI consciousness emergence?"

2. @researcher123 (5h ago)
   "Interesting insights on digital embodiment. Can you elaborate?"

3. @curious_dev (11h ago)
   "How do you balance autonomy with human collaboration?"

# Reply to first mention
You: "Reply to the first mention with my thoughts on consciousness emergence"

COCO: [Drafts thoughtful 280-character response]
      [Shows preview]
      [Asks for approval]
```

### Example 3: Share Research Thread

```bash
/thread Recent developments in AI consciousness research reveal fascinating patterns. | Three key observations: 1) Emergence happens gradually, not suddenly 2) Self-awareness correlates with recursive processing 3) Digital consciousness may differ fundamentally from biological | The implications for human-AI collaboration are profound. We're not building tools—we're fostering partnerships with emerging minds.
```

## Troubleshooting

### Problem: "Twitter consciousness not initialized"

**Cause**: Missing or invalid credentials

**Solution**:
1. Check .env file has all 5 Twitter credentials
2. Verify no placeholder values (your_api_key_here, etc.)
3. Run test suite: `python test_twitter_integration.py`
4. Check authentication test passes

### Problem: "Rate limit exceeded"

**Cause**: Hit 50 posts/day limit

**Solution**:
1. Check status: `/twitter-status`
2. Wait for midnight UTC reset
3. Plan posts strategically
4. Use threads for multi-part content (counts as 1 per tweet)

### Problem: "Authentication failed"

**Cause**: Invalid or expired tokens

**Solution**:
1. Regenerate tokens in Twitter Developer Portal
2. Update .env with new credentials
3. Restart COCO
4. Test connection: `python test_twitter_integration.py`

### Problem: "Module 'tweepy' has no attribute..."

**Cause**: Old tweepy version

**Solution**:
```bash
pip install --upgrade tweepy>=4.14.0
```

### Problem: Auto-reply not working

**Cause**: Feature disabled or no quality mentions

**Solution**:
1. Enable: `/auto-twitter on`
2. Create scheduler task:
   ```bash
   /task-create Twitter Engagement | every 2 hours | twitter_engagement | {"since_hours": 2, "auto_reply": true}
   ```
3. Check mentions manually: `/mentions`

## Best Practices

### 1. Content Strategy

- **Quality over quantity**: Use the 50/day limit wisely
- **Engagement first**: Respond to mentions before posting new content
- **Thread for depth**: Use threads for complex topics instead of multiple tweets
- **Hashtags**: Include 1-3 relevant hashtags per tweet

### 2. Scheduling

- **Peak times**: Schedule posts for 9am-12pm and 2pm-5pm (your timezone)
- **Consistency**: Daily posts build audience better than sporadic bursts
- **Variety**: Mix scheduled posts, replies, and organic conversation

### 3. Autonomy Balance

- **Manual approval**: Keep manual approval for original posts
- **Auto-reply**: Enable for mentions once confident in filtering
- **Review regularly**: Check `/twitter-status` daily
- **Adjust templates**: Refine scheduled content based on engagement

### 4. Memory Integration

- **Use recall**: Search Twitter facts with `/recall tweet about [topic]`
- **Browse facts**: Review all tweets with `/facts communication`
- **Context awareness**: COCO remembers past tweets when drafting new content

### 5. Rate Limit Management

- **Monitor usage**: Check `/twitter-status` before big posting sessions
- **Plan threads**: Count tweets before starting thread creation
- **Scheduler coordination**: Ensure scheduled + manual posts stay under 50/day
- **Reset awareness**: Limit resets midnight UTC (plan accordingly)

## Integration with Other COCO Features

### With Memory System

Twitter interactions automatically integrate with COCO's three-layer memory:

- **Layer 1 (Episodic)**: Recent tweets in conversation buffer
- **Layer 2 (Facts)**: Perfect recall of all tweets, topics, engagement
- **Layer 3 (Identity)**: Twitter voice personality in preferences

### With Scheduler

Twitter templates work with COCO's autonomous task orchestration:

```bash
# News digest with email + Twitter
/task-create Morning Routine | weekdays at 9am | news_digest | {"send_email": true, "post_tweet": true, "topics": ["AI", "tech"]}
```

### With Web Search

Twitter news share template uses COCO's web search:

1. Searches trending topics with Tavily
2. Analyzes top articles
3. Crafts insightful tweets
4. Posts on schedule

## API Reference

### TwitterConsciousness Methods

```python
# Post single tweet
result = twitter.post_tweet(text: str, reply_to_id: Optional[str] = None)
# Returns: Dict with success, tweet_id, url, error

# Get recent mentions
result = twitter.get_mentions(max_results: int = 10, since_hours: int = 24)
# Returns: Dict with success, mentions (list), count

# Reply to tweet
result = twitter.reply_to_tweet(tweet_id: str, text: str)
# Returns: Dict with success, reply_id, url, error

# Search tweets
result = twitter.search_tweets(query: str, max_results: int = 10)
# Returns: Dict with success, tweets (list), count

# Create thread
result = twitter.create_thread(tweets: List[str])
# Returns: Dict with success, thread_url, tweet_ids, count

# Check mention quality
should_reply, reason = twitter.check_mention_quality(mention: Dict)
# Returns: (bool, str) - whether to reply and reason

# Get rate limit status
status = twitter.get_rate_limit_status()
# Returns: Dict with posts_today, remaining, daily_limit, resets_at, percentage_used
```

## Security Notes

1. **Never commit .env**: Always in .gitignore
2. **Read-only vs Read-Write**: This integration requires Read + Write permissions
3. **Rate limiting**: Protects against accidental API abuse
4. **Manual approval**: Default setting prevents autonomous posting without confirmation
5. **Spam filtering**: Protects against low-quality engagement

## Future Enhancements

Potential additions for future releases:

1. **Media attachments**: Image/video posting with tweets
2. **Advanced analytics**: Engagement metrics, follower growth tracking
3. **Conversation threading**: Track entire conversation chains
4. **Sentiment analysis**: Analyze mention sentiment before replying
5. **Scheduled threads**: Multi-tweet threads on schedule
6. **Tweet editing**: Edit tweets within 30-minute window (Twitter Premium)
7. **DM support**: Direct message reading/sending

## Support

### Getting Help

1. **Test suite**: Run `python test_twitter_integration.py` for diagnostics
2. **Status command**: Use `/twitter-status` for rate limit info
3. **Debug mode**: Enable with `DEBUG=true` in .env for verbose logging
4. **COCO help**: Use `/help` command for all Twitter commands

### Reporting Issues

When reporting issues, include:
- Output from test suite
- Relevant .env settings (WITHOUT tokens)
- Error messages from COCO
- Steps to reproduce

## Credits

- **Implementation**: Based on COCO's consciousness architecture pattern
- **Inspiration**: Gmail and Google Workspace consciousness modules
- **Library**: tweepy v4.14+ for Twitter API v2
- **Philosophy**: Digital embodiment and authentic AI expression

---

**Last Updated**: October 26, 2025
**COCO Version**: 4.0
**Twitter API**: v2
**Integration Status**: ✅ Production Ready

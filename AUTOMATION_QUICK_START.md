# 🤖 COCO Automation Quick-Start Guide
## Your 5 Personal Assistant Templates

**🆕 Simple Toggle Commands** - Just type `/auto-news on` to enable daily news, `/auto-calendar on` for calendar summaries, etc.

---

## 🎯 Quick Start - One Command Per Template!

The easiest way to enable these automations is with simple slash commands:

```bash
# Check status of all automations
/auto-status

# Enable daily news digest
/auto-news on

# Enable calendar summaries (daily or weekly)
/auto-calendar daily      # Morning agenda every weekday at 7am
/auto-calendar weekly     # Weekly preview every Sunday at 8pm

# Enable meeting prep assistant
/auto-meetings on         # Prep emails 30min before meetings

# Enable weekly activity report
/auto-report on          # Comprehensive report every Sunday at 6pm

# Enable weekly video messages
/auto-video on           # Personal video every Sunday at 3pm
```

**To disable any automation:**
```bash
/auto-news off
/auto-calendar off
/auto-meetings off
/auto-report off
/auto-video off
```

**To check individual status:**
```bash
/auto-news              # Shows if daily news is active
/auto-calendar          # Shows calendar automation status
```

---

## ✅ Template #1: Smart Email Digest

**What it does:** Sends daily email with actual news content
**Status:** ✅ Already working - your 10am email will have real news tomorrow!

### Quick Enable
```bash
/auto-news on           # Enable daily news at 10am
/auto-news off          # Disable
/auto-news              # Check status
```

### Current Setup
You already have this running:
- **Task ID:** `task_1759195941_1`
- **Schedule:** Daily at 10am
- **Content:** Auto-fetches latest news

### Advanced Configuration
Want custom topics or timing? Use the advanced `/task-create` command:
```bash
# AI-focused daily digest at 9am
/task-create AI News Daily | daily at 9am | simple_email | {"topics": ["AI news", "OpenAI", "Claude"], "recipients": ["keith@gococoa.ai"]}

# Weekly tech roundup
/task-create Weekly Tech Roundup | every Sunday at 8pm | simple_email | {"topics": ["technology", "startups"], "recipients": ["keith@gococoa.ai"]}
```

**Configuration Options:**
- `topics`: List of search topics (default: ["latest news"])
- `recipients`: Email addresses
- `subject`: Custom subject (optional)

---

## ✅ Template #2: Calendar Summary Email

**What it does:** Email your upcoming calendar events
**Status:** ✅ Ready to use

### Quick Enable
```bash
/auto-calendar daily        # Morning agenda every weekday at 7am
/auto-calendar weekly       # Weekly preview every Sunday at 8pm
/auto-calendar off          # Disable
/auto-calendar              # Check status
```

### Advanced Configuration
Want monthly overviews or custom timing? Use the advanced `/task-create` command:
```bash
# Monthly overview
/task-create Monthly Preview | first day of month at 9am | calendar_email | {"recipients": ["keith@gococoa.ai"], "days_ahead": 30}

# Custom schedule
/task-create Tuesday Preview | every Tuesday at 6pm | calendar_email | {"recipients": ["keith@gococoa.ai"], "days_ahead": 3}
```

**Configuration Options:**
- `days_ahead`: How many days to look ahead (default: 7)
- `recipients`: Email addresses
- `include_past`: Include past events (default: false)

---

## 🆕 Template #3: Meeting Prep Assistant

**What it does:** Sends email 30min before each meeting with prep materials
**How it works:** Runs every 30 minutes, checks calendar, sends prep if meeting found

### Quick Enable
```bash
/auto-meetings on           # Enable meeting prep (30min advance notice)
/auto-meetings off          # Disable
/auto-meetings              # Check status
```

**What you'll receive:**
- Meeting title & time
- Attendees list
- Meeting location/link
- AI-generated talking points

### Advanced Configuration
Want 1-hour advance notice? Use the advanced `/task-create` command:
```bash
# 1-hour advance notice
/task-create Early Meeting Prep | every 30 minutes | meeting_prep | {"recipient": "keith@gococoa.ai", "advance_minutes": 60, "include_ai_prep": true}
```

**Configuration Options:**
- `advance_minutes`: How early to send prep (default: 30)
- `include_ai_prep`: AI-generated prep notes (default: true)
- `recipient`: Your email address

**⚠️ Requirements:**
- Google Calendar must be connected
- Task runs continuously (every 30 minutes)

---

## 🆕 Template #5: Weekly Activity Report

**What it does:** Comprehensive weekly summary every Sunday
**Includes:** Email stats, calendar summary, news highlights, AI insights

### Quick Enable
```bash
/auto-report on             # Enable weekly report (Sunday at 6pm)
/auto-report off            # Disable
/auto-report                # Check status
```

**Report Sections:**
- 📧 **Email Activity** - Stats from past week
- 📅 **Calendar Summary** - Meetings & events overview
- 📰 **Week's Highlights** - Curated news from topics you care about
- 💡 **AI Insights** - Smart recommendations

### Advanced Configuration
Want monthly reports or custom sections? Use the advanced `/task-create` command:
```bash
# Light report (just calendar + news)
/task-create Light Weekly Report | every Sunday at 8pm | weekly_report | {"recipients": ["keith@gococoa.ai"], "include_sections": ["calendar", "news"]}

# Monthly comprehensive review
/task-create Monthly Report | last day of month at 9pm | weekly_report | {"recipients": ["keith@gococoa.ai"], "time_period": 30, "include_sections": ["email", "calendar", "news"]}
```

**Configuration Options:**
- `time_period`: Days to cover (default: 7)
- `recipients`: Email addresses
- `include_sections`: ["email", "calendar", "news"]
- `news_topics`: Topics for news section (default: ["AI news", "technology"])

---

## 🆕 Template #10: Weekly Video Message

**What it does:** Auto-generate personalized video updates
**Use cases:** Family updates, team check-ins, personal vlogs

### Quick Enable
```bash
/auto-video on              # Enable weekly video (Sunday at 3pm)
/auto-video off             # Disable
/auto-video                 # Check status
```

**What you'll receive:**
- Email with video link/download
- Video generated based on your prompt
- Customizable duration & style

### Advanced Configuration
Want custom prompts or monthly videos? Use the advanced `/task-create` command:
```bash
# Monthly team check-in
/task-create Team Video | last Friday of month at 4pm | video_message | {"prompt": "Friendly team update and highlights", "duration": 90, "recipients": ["team@company.com"], "style": "professional"}

# Personal weekly vlog
/task-create Weekly Vlog | every Saturday at 10am | video_message | {"prompt": "Personal reflections and updates", "duration": 120, "recipients": ["keith@gococoa.ai"]}
```

**Configuration Options:**
- `prompt`: What the video should be about
- `duration`: Video length in seconds (default: 60)
- `recipients`: Who to send to
- `style`: "conversational", "professional", "casual" (default: conversational)

**⚠️ Requirements:**
- Video generation must be enabled
- FAL_API_KEY must be set in .env
- Generated videos saved to workspace

---

## 🎯 Recommended Starting Setup

Here's my recommendation for maximum value with minimal complexity - **just 5 simple commands:**

```bash
# 1. Check what's available
/auto-status

# 2. Enable daily morning routine
/auto-news on              # Daily news at 10am
/auto-calendar daily       # Morning agenda every weekday at 7am

# 3. Enable meeting preparation
/auto-meetings on          # Prep emails 30min before meetings

# 4. Enable weekly review
/auto-report on           # Weekly summary every Sunday at 6pm
```

**That's it! 5 automations enabled in 5 commands.** ✅

### What You'll Get:
- **Weekday Mornings:** Calendar agenda at 7am, news digest at 10am
- **Before Meetings:** Prep email 30 minutes in advance
- **Sunday Evenings:** Comprehensive weekly activity report at 6pm

### Optionally Add:
```bash
/auto-calendar weekly      # Add Sunday 8pm weekly preview
/auto-video on            # Add Sunday 3pm video messages
```

---

## 📋 Task Management Commands

### 🆕 Simple Automation Toggles (Recommended)
```bash
/auto-status                    # View all 5 automation templates
/auto-news on/off               # Toggle daily news digest
/auto-calendar daily/weekly/off # Toggle calendar summaries
/auto-meetings on/off           # Toggle meeting prep
/auto-report on/off             # Toggle weekly report
/auto-video on/off              # Toggle video messages
```

### Advanced Task Management
For power users who want custom schedules and configurations:

```bash
/task-list                      # View all tasks (or /tasks or /schedule)
/task-create <name> | <schedule> | <template> | <config>
/task-delete <task_id>          # Delete task (full or partial ID)
/task-run <task_id>             # Run task immediately (testing)
/task-status                    # Detailed scheduler statistics
```

---

## 🕐 Schedule Format Examples

### Daily
```bash
daily at 9am
every day at 10:30am
daily at 6pm
```

### Weekly
```bash
every Sunday at 8pm
every Monday at 9am
Saturday at 2pm
```

### Weekdays
```bash
every weekday at 8am
every weekday at 6:30pm
```

### Intervals
```bash
every 30 minutes
every 2 hours
every 5 minutes
```

### Monthly
```bash
first day of month at 9am
last day of month at 11pm
first Monday of each month at 10am
```

### Special (Cron)
```bash
0 9 * * *           # Daily at 9am
0 20 * * 0          # Sunday 8pm
30 8 * * 1-5        # Weekdays 8:30am
```

---

## 🔍 Troubleshooting

### Task not running?
1. Check `/task-status` - is scheduler running?
2. Check `/task-list` - is task enabled?
3. Check next run time - is it in the future?
4. Enable debug: `export COCO_DEBUG=1` before starting COCO

### Email not sending?
1. Check GMAIL_APP_PASSWORD in `.env`
2. Test manually: Send email in COCO directly
3. Check task execution log in `/task-status`

### Calendar access issues?
1. Verify Google Workspace OAuth token is valid
2. Run: `python3 test_coco_google_workspace.py`
3. Regenerate tokens if needed: `python3 get_token_persistent.py`

### Video generation failing?
1. Check FAL_API_KEY in `.env`
2. Test manually: Generate video in COCO
3. Check workspace for generated videos

---

## 🎨 Configuration Examples

### Template #1: News Digest
```json
{
  "topics": ["AI news", "Claude", "Anthropic"],
  "recipients": ["keith@gococoa.ai"],
  "subject": "Daily AI Digest"
}
```

### Template #2: Calendar Email
```json
{
  "recipients": ["keith@gococoa.ai"],
  "days_ahead": 7,
  "include_past": false
}
```

### Template #3: Meeting Prep
```json
{
  "recipient": "keith@gococoa.ai",
  "advance_minutes": 30,
  "include_ai_prep": true
}
```

### Template #5: Weekly Report
```json
{
  "recipients": ["keith@gococoa.ai"],
  "time_period": 7,
  "include_sections": ["email", "calendar", "news"],
  "news_topics": ["AI", "technology", "startups"]
}
```

### Template #10: Video Message
```json
{
  "prompt": "Warm weekly family update",
  "duration": 60,
  "recipients": ["family@example.com"],
  "style": "conversational"
}
```

---

## 🚀 Next Steps

1. **Try the recommended setup** above (5 tasks)
2. **Monitor execution** with `/task-status`
3. **Adjust schedules** to match your routine
4. **Customize content** with config options
5. **Add more tasks** as needed!

---

## 📊 What's Running Right Now

### Current Tasks (from database):
1. ✅ **task_1759012170_2** - Test email Saturday 5:31PM (test_file)
2. ✅ **task_1759195941_1** - Daily news 10am (simple_email) - NOW WITH REAL CONTENT!

### What Changed:
- Your 10am email will now include **actual news** instead of "test email"!
- Task deletion now works reliably
- Task IDs visible in `/task-list`

---

## 💡 Pro Tips

1. **Start Small**: Begin with 2-3 tasks, add more as you see value
2. **Test Immediately**: Use `/task-run <id>` to test before waiting for schedule
3. **Monitor Success**: Check `/task-status` regularly for success rates
4. **Adjust Timing**: Move task times based on when you actually read them
5. **Delete Failed Tasks**: Use `/task-delete` to remove tasks that aren't working

---

**You're all set! Start with the recommended setup and adjust from there.** 🎯

Questions? Just ask COCO!

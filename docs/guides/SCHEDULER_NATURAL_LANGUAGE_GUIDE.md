# COCO Scheduler - Natural Language Guide 🗓️

## Yes! Natural Language Works! ✅

The scheduler has a **sophisticated natural language parser** that converts human-friendly schedules into cron expressions automatically.

## Supported Natural Language Formats

### 1. Weekly Schedules

**With "every":**
```bash
/task-create Weekly Email | every Sunday at 8pm | calendar_email | {...}
/task-create Monday Meeting | every monday at 9:30am | simple_email | {...}
```

**Without "every":**
```bash
/task-create Saturday Report | saturday at 2:05PM | news_digest | {...}
/task-create Friday Update | friday at 5pm | simple_email | {...}
```

**Converts to:** `"5 14 * * 6"` (minute hour * * weekday)

### 2. Daily Schedules

```bash
/task-create Morning News | daily at 9am | news_digest | {...}
/task-create Evening Summary | daily at 6:30pm | simple_email | {...}
/task-create Midnight Backup | daily at 12am | health_check | {...}
```

**Converts to:** `"0 9 * * *"` (runs every day at specified time)

### 3. Weekday Schedules (Monday-Friday)

```bash
/task-create Workday Reminder | every weekday at 8:30am | simple_email | {...}
/task-create Business Hours Check | every weekday at 5pm | health_check | {...}
```

**Converts to:** `"30 8 * * 1-5"` (Monday=1 through Friday=5)

### 4. Interval-Based Schedules

**Every X Minutes:**
```bash
/task-create Quick Check | every 5 minutes | health_check | {...}
/task-create Frequent Update | every 30 minutes | simple_email | {...}
/task-create Rapid Poll | every 1 minute | test_file | {...}
```

**Every X Hours:**
```bash
/task-create Bi-Hourly Scan | every 2 hours | health_check | {...}
/task-create Four Hour Update | every 4 hours | news_digest | {...}
```

**Every X Seconds (for testing):**
```bash
/task-create Test Task | every 30 seconds | test_file | {...}
```

### 5. Monthly Schedules

**First Weekday of Month:**
```bash
/task-create Monthly Report | first Monday of each month at 10am | web_research | {...}
/task-create First Friday | first friday of each month at 2pm | simple_email | {...}
```

**Last Day of Month:**
```bash
/task-create End of Month | last day of each month at 11pm | news_digest | {...}
/task-create Month Close | last day of each month at 6pm | health_check | {...}
```

### 6. Special Cron Shortcuts

You can also use these shortcuts instead of natural language:

```bash
/task-create Daily Task | @daily | health_check | {...}
/task-create Weekly Task | @weekly | news_digest | {...}
/task-create Monthly Task | @monthly | web_research | {...}
/task-create Hourly Task | @hourly | simple_email | {...}
```

**Available shortcuts:**
- `@daily` = every day at midnight
- `@weekly` = every Sunday at midnight
- `@monthly` = first day of month at midnight
- `@hourly` = every hour on the hour

### 7. Raw Cron Expressions (Advanced)

If you know cron syntax, you can use it directly:

```bash
/task-create Custom | 0 20 * * 0 | calendar_email | {...}
# minute hour day month weekday
# 0      20   *   *     0 = Sunday 8 PM

/task-create Complex | 30 14 1-7 * 1 | simple_email | {...}
# First Monday of month at 2:30 PM
```

## Complete Examples

### Example 1: Weekly Calendar Email
```bash
/task-create Weekend Planning | every Sunday at 8pm | calendar_email | {"recipients": ["keith@gococoa.ai"], "look_ahead_days": 7, "subject": "📅 Your Week Ahead"}
```

### Example 2: Daily News Digest
```bash
/task-create Morning News | daily at 9am | news_digest | {"recipients": ["keith@gococoa.ai"], "topics": ["AI news", "tech startups"], "subject": "🤖 Your Daily AI Digest"}
```

### Example 3: Weekday Health Check
```bash
/task-create Business Hours Monitor | every weekday at 8:30am | health_check | {"send_email": true, "recipients": ["keith@gococoa.ai"]}
```

### Example 4: Hourly Research
```bash
/task-create AI Research | every 2 hours | web_research | {"recipients": ["keith@gococoa.ai"], "queries": ["latest AI developments", "Claude AI updates"]}
```

### Example 5: Monthly Report
```bash
/task-create Monthly Summary | first monday of each month at 10am | web_research | {"recipients": ["keith@gococoa.ai"], "queries": ["AI industry trends", "monthly tech news"]}
```

## How It Works Internally

1. **Parser detects natural language** (e.g., "every Sunday at 8pm")
2. **Regex patterns match** the format
3. **Converts to cron** (`"0 20 * * 0"`)
4. **Scheduler uses cron** to calculate next run time

## Time Parsing

The parser handles various time formats:

✅ `9am` → 09:00
✅ `9:30am` → 09:30
✅ `2pm` → 14:00
✅ `2:05PM` → 14:05
✅ `12am` → 00:00 (midnight)
✅ `12pm` → 12:00 (noon)

## Timezone

All schedules use **America/Chicago** timezone by default (configured in scheduler).

## What If Natural Language Fails?

If the natural language parser doesn't recognize your format:

1. **Use a cron expression** directly
2. **Check the supported formats** above
3. **Enable debug mode** to see what's happening:
   ```bash
   export COCO_DEBUG=1
   python3 cocoa.py
   ```

## Testing Your Schedule

After creating a task, check when it will run:

```bash
/task-list
# Shows "Next Run" column with exact date/time

/task-status
# Shows detailed scheduler statistics

/task-run <task_id>
# Execute immediately to test (doesn't affect schedule)
```

## Format Cheat Sheet

| What You Want | Natural Language | Alternative |
|---------------|------------------|-------------|
| Every Sunday 8pm | `every sunday at 8pm` | `0 20 * * 0` |
| Daily 9am | `daily at 9am` | `0 9 * * *` |
| Weekdays 8:30am | `every weekday at 8:30am` | `30 8 * * 1-5` |
| Every 5 minutes | `every 5 minutes` | `*/5 * * * *` |
| Every 2 hours | `every 2 hours` | `0 */2 * * *` |
| First Mon 10am | `first monday of each month at 10am` | `0 10 1-7 * 1` |
| Last day 11pm | `last day of each month at 11pm` | `0 23 28-31 * *` |
| Daily midnight | `daily at 12am` | `@daily` |

## Pro Tips

1. **Be specific with times** - Include `am` or `pm` to avoid confusion
2. **Test with short intervals** - Use "every 5 minutes" for testing, then change to final schedule
3. **Check next run** - Always verify with `/task-list` that the schedule is what you expected
4. **Use `/task-run`** - Test task execution immediately before waiting for scheduled time

---

**The scheduler is smart!** Just describe when you want something to happen in natural English, and it figures out the cron expression for you. 🎯

# COCO Scheduler - Quick Reference Card 📋

## Commands

```bash
/task-create <name> | <schedule> | <template> | <config>
/task-list  or  /tasks  or  /schedule
/task-delete <task_id>
/task-run <task_id>
/task-status
```

## Natural Language Schedules ✨

```bash
every sunday at 8pm          # Weekly
daily at 9am                 # Daily
every weekday at 8:30am      # Mon-Fri
every 5 minutes              # Interval
every 2 hours                # Interval
saturday at 2:05PM           # Weekly (no "every")
first monday of each month at 10am
last day of each month at 11pm
```

## Templates

| Template | What It Does | Required Config |
|----------|--------------|-----------------|
| `calendar_email` | Sends calendar summary | `{"recipients": [...]}` |
| `news_digest` | Searches web for news | `{"recipients": [...], "topics": [...]}` |
| `health_check` | System health report | `{"send_email": true/false}` |
| `web_research` | Automated research | `{"recipients": [...], "queries": [...]}` |
| `simple_email` | Simple email notification | `{"recipient": "...", "subject": "...", "message": "..."}` |
| `test_file` | Creates test file | `{"file_name": "...", "file_content": "..."}` |
| `personal_video` | Video message | `{"recipients": [...], "message": "..."}` |

## Examples

**Daily News:**
```bash
/task-create Morning News | daily at 9am | news_digest | {"recipients": ["keith@gococoa.ai"], "topics": ["AI news"]}
```

**Weekly Calendar:**
```bash
/task-create Sunday Planning | every sunday at 8pm | calendar_email | {"recipients": ["keith@gococoa.ai"]}
```

**Hourly Health Check:**
```bash
/task-create System Monitor | every 2 hours | health_check | {"send_email": false}
```

**Test Task:**
```bash
/task-create Test | every 5 minutes | test_file | {"file_name": "test.txt"}
```

## Quick Start

1. **Create a task** with natural language schedule
2. **Check it**: `/schedule` to see next run time
3. **Test it**: `/task-run <id>` to execute immediately
4. **Monitor**: Check COCO's memory - it remembers all executions!

## Memory Integration 🧠

COCO remembers:
- ✅ All task creations
- ✅ All task executions
- ✅ Success/failure status
- ✅ When tasks will run next

Ask COCO: *"What autonomous tasks do I have scheduled?"* or *"What tasks ran today?"*

---
**Status:** ✅ Production Ready | **Tests:** 7/7 Passing | **Date:** Oct 2, 2025

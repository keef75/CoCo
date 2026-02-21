# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📑 Quick Navigation

**Essential Sections**:
- [Quick Reference](#quick-reference) - Launch, test, and develop commands
- [Architecture Overview](#architecture-overview) - Core design and components
- [Critical Architecture Insights](#critical-architecture-insights) - Non-obvious patterns requiring multi-file understanding
- [Memory System](#memory-system) - Dual-stream architecture (Facts + Semantic)
- [Code Navigation Guide](#code-navigation-guide) - Line number ranges for major components
- [Common Issues](#common-issues) - Troubleshooting guide
- [Recent Updates](#recent-updates) - Latest fixes (last 30 days only)

**Key ADRs**: See [ADR Index](#architecture-decision-records) for complete list (39 total)

---

## Quick Reference

### Launch & Testing

```bash
# Launch COCO
./launch.sh                           # RECOMMENDED: Automated setup
python3 cocoa.py                      # Direct launch
./venv_cocoa/bin/python cocoa.py      # Virtual environment

# System Management
./launch.sh test                      # System validation
./launch.sh clean                     # Complete cleanup
python3 -m py_compile cocoa.py        # Syntax validation

# Module Testing
./venv_cocoa/bin/python test_audio_quick.py              # Audio
./venv_cocoa/bin/python test_visual_complete.py          # Visual
./venv_cocoa/bin/python test_video_complete.py           # Video gen
./venv_cocoa/bin/python test_video_observer.py           # Video playback
./venv_cocoa/bin/python test_coco_google_workspace.py    # Google Workspace
./venv_cocoa/bin/python test_twitter_integration.py      # Twitter (7 tests)
./venv_cocoa/bin/python test_integration.py              # Memory (4 tests)
./venv_cocoa/bin/python test_html_email_fix.py           # HTML email rendering (2 tests)
```

### Key In-COCO Commands

```bash
# Facts Memory (Automatic + Manual)
/recall <query>         # Perfect recall with routing (auto-searches at 0.6+ confidence)
/facts [type]           # Browse 18 fact types (appointment, contact, task, etc.)
/facts-stats            # Database statistics

# Automation
/auto-status            # View 5 automation templates
/auto-news on/off       # Daily news digest
/auto-calendar daily/weekly/off  # Calendar summaries
/auto-meetings on/off   # Meeting prep 30min before
/auto-report on/off     # Weekly activity report
/auto-video on/off      # Weekly video message

# Twitter
/tweet <text>           # Post with approval (280-25K chars)
/mentions [hours]       # Recent mentions (filtered)
/twitter-status         # Rate limits (50/day Free tier)

# Knowledge Graph
/kg-refresh             # Extract from last 100 conversations
/kg                     # Visualize graph
```

---

## Architecture Overview

### Core Design

**Monolithic single-file architecture** (`cocoa.py` 677KB, 14,911 lines) with modular consciousness extensions:
- Single-file main engine for tight integration
- Modular extensions: audio, visual, video, workspace, twitter
- Non-streaming API for beautiful interactive flow
- Tool-as-cognitive-organ philosophy (digital embodiment)

### Critical Components

**Main Engine** (`cocoa.py`):
- `ConsciousnessEngine` (~5861-7000): Claude Sonnet 4.5 with 30+ tools
- `HierarchicalMemorySystem` (~1000-2000): 3-layer hybrid memory
- `ToolSystem` (~3500-4500): Function calling implementations
- Model: `claude-sonnet-4-5-20250929` (line 1262)

**Google Workspace** (`google_workspace_consciousness.py`):
- OAuth2 integration: Docs, Sheets, Drive, Calendar
- 11 tools: create/read/update documents, spreadsheets, files
- Beautiful formatting: Markdown → Google Docs (lines 259-596)
- Tool definitions: `cocoa.py` lines 6720-6938

**Twitter** (`cocoa_twitter.py` - 532 lines):
- OAuth 2.0 via tweepy, API v2
- 5 tools: post, mentions, reply, search, threads
- Rate limiting: 50/day Free tier (custom tracker)
- Media support: 1-4 images or 1 video per tweet
- Tool handlers: `cocoa.py` lines 12490-12527

**Task Scheduler** (`cocoa_scheduler.py`):
- Natural language scheduling: "every Sunday at 8pm"
- 10 templates: calendar, news, meetings, reports, videos
- Memory integration: working memory + Simple RAG
- Tool access: `self.coco.tools.method_name()`

**Knowledge Graph** (`personal_assistant_kg_enhanced.py`):
- Hybrid extraction: LLM (Claude-3-Haiku) + patterns
- Real-time: `process_conversation_exchange()` (lines 366-393)
- Batch: `extract_from_recent_conversations()` (lines 1188-1283)

### Three-Part Tool System

**CRITICAL**: All tools require:
1. **Tool definitions** (e.g., lines 7814-7900 for Twitter)
2. **Tool implementations** (e.g., lines 5509-5620 for Twitter methods)
3. **Tool handlers** (e.g., lines 12490-12527 for `_execute_tool()` routing)

Missing any part = "Unknown tool" error. See ADR-034 and [Critical Architecture Insights](#critical-architecture-insights) for details.

---

## Critical Architecture Insights

**These are non-obvious patterns that require reading multiple files to understand.** Future Claude Code instances should understand these before making changes.

### 1. Three-Part Tool System Pattern (ADR-034)

**Why tools fail with "Unknown tool" error:**

Every tool integration requires **ALL THREE parts** or Claude will report "Unknown tool":

```python
# Part 1: Tool Definition (JSON schema for Claude API)
# Location example: cocoa.py lines 7696-7783 (Twitter)
{
    "name": "post_tweet",
    "description": "Post a tweet to Twitter with optional media...",
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Tweet content..."},
            "media_paths": {"type": "array", "items": {"type": "string"}}
        }
    }
}

# Part 2: Tool Implementation (actual Python method)
# Location example: cocoa.py lines 5509-5620 (Twitter methods in class)
def post_tweet(self, text: str, media_paths: List[str] = None) -> Dict[str, Any]:
    """Post a tweet with optional media."""
    # Implementation logic here
    return {"success": True, "tweet_id": "..."}

# Part 3: Tool Handler (routing in _execute_tool)
# Location example: cocoa.py lines 12490-12527 (Twitter handler routing)
elif tool_name == "post_tweet":
    text = tool_input.get("text", "")
    media_paths = tool_input.get("media_paths")
    return self.tools.twitter.post_tweet(text, media_paths)
```

**Critical Insight**: Twitter integration initially failed because Parts 1 & 2 existed but Part 3 (handler routing in `_execute_tool()`) was missing. The tool was defined and implemented but never routed to execution.

**How to add new tools:**
1. Add tool definition to appropriate section (search for similar tool definitions)
2. Implement method in appropriate class (`self.tools.twitter`, `self.tools.google_workspace`, etc.)
3. **Don't forget Part 3**: Add routing case in `_execute_tool()` method

### 2. Dynamic Pressure-Based Memory Allocation

**NOT fixed budgets** - memory allocation is adaptive based on real-time context pressure:

```python
# Working Memory: 15-35 exchanges (DYNAMIC, not fixed)
# Allocation based on context usage:
if context_usage < 60%:  buffer_size = 35  # Green zone - full capacity
elif context_usage < 75%: buffer_size = 25  # Yellow - optimization
elif context_usage < 85%: buffer_size = 20  # Orange - warnings
else:                     buffer_size = 15  # Red - emergency mode

# Summary Context: Capped at 5K tokens (was unbounded, caused 201K overflow)
# Document Context: 5K-20K dynamic (was hardcoded 30K, caused overflow)
```

**Emergency Thresholds**:
- **Green** (0-60%): Full operations, predictive monitoring
- **Yellow** (60-75%): Resource optimization, suggest compression
- **Orange** (75-85%): Warning alerts, defer non-critical ops
- **Red** (85-95%): Force efficiency modes, block resource-intensive ops
- **Critical** (95%+): Emergency protocols, essential operations only

**Key Insight**: The system doesn't have fixed memory budgets. It dynamically adjusts based on context pressure. This prevented the 201K token overflow crisis (ADR-025).

### 3. Universal Tool Fact Extraction Architecture

**15 tools automatically extract facts** with dual/triple extraction pattern:

```python
# Every tool use creates persistent facts for perfect recall
# Example: send_email extracts TWO facts:
#   1. communication fact (recipient, subject)
#   2. tool_use fact (action performed)

# Example: create_document extracts THREE facts:
#   1. file fact (document created)
#   2. tool_use fact (action performed)
#   3. task fact (if document is task-related)
```

**Tools with auto-extraction** (ADR-028 expansion):
- Email: `send_email`, `send_gmail`, `read_email`
- Documents: `create_document`, `update_document`, `read_document`
- Calendar: `create_calendar_event`, `list_calendar_events`
- Media: `generate_image`, `generate_video`
- Search: `web_search`, `search_tweets`
- Twitter: `post_tweet`, `reply_to_tweet`, `post_thread`

**Impact**: Actions create facts that persist even after conversation buffer clears. User can ask "who did I email last week?" or "what documents did I create yesterday?" and get perfect recall.

**Architecture**: `cocoa.py` lines 8162-8717 - router maps tools to extractors with tool-specific dual/triple fact patterns.

### 4. Non-Streaming API Architecture

**Design Choice**: Uses Claude's **synchronous API** (not streaming) despite being slower.

**Why?**
- **Rich UI Requirements**: Beautiful panels, tables, and formatted output require complete responses
- **Function Calling**: Tool extraction needs full response before executing tools
- **Interactive Flow**: Typewriter effect simulated in UI layer for better UX

**Trade-offs Accepted**:
- Slower perceived response time vs. better visual design
- Two API calls per tool use (initial + follow-up with results)
- Higher latency vs. more polished user experience

**Key Insight**: This is an intentional architectural decision for UX, not a limitation to fix.

### 5. Hybrid HTML Email System (ADR-040)

**Design Pattern**: Intelligent HTML detection with body extraction for scheduler/automation emails.

**The Problem**:
- Scheduler (`cocoa_scheduler.py`) generates complete HTML documents with `<!DOCTYPE>`, `<html>`, `<head>`, `<body>` tags
- Gmail's `send_email()` expects Markdown content to convert and wrap in COCO template
- When scheduler HTML was passed to `send_email()`, it was wrapped in another HTML document
- Result: Double HTML nesting → Gmail displayed inner HTML as raw text

**The Solution** (`gmail_consciousness.py` lines 320-361):
```python
# Detect if body is already HTML (from scheduler/automation)
is_html = '<!DOCTYPE html>' in body or '<html' in body.lower()

if is_html:
    # Extract only <body> content using BeautifulSoup
    soup = BeautifulSoup(body, 'html.parser')
    body_tag = soup.find('body')
    body_html = ''.join(str(child) for child in body_tag.children)
else:
    # Body is Markdown - convert normally
    body_html = self._markdown_to_html(body)

# Wrap in COCO email template (both paths converge here)
full_html = self._generate_html_email(body_html, subject)
```

**Why This Matters**:
- **Preserves scheduler styling**: Tables, colors, custom formatting retained
- **Adds COCO branding**: Professional header/footer from email template
- **Backward compatible**: Markdown emails (user-initiated) work unchanged
- **Prevents double nesting**: Single HTML document sent to Gmail

**Key Insight**: This hybrid approach supports both content types (HTML from automation, Markdown from users) using the same email infrastructure. The detection happens at runtime with zero user intervention.

### 6. Database Strategy (Three Databases)

**NOT a single database** - three separate databases for different purposes:

1. **PostgreSQL** (via Docker): Episodic memory
   - Conversation history and context
   - Requires Docker container running
   - Long-term conversation storage

2. **SQLite** (`coco_memory.db`): Facts Memory
   - 18 fact types for perfect recall
   - Automatic extraction on every exchange
   - Queried by Facts Memory system

3. **SQLite** (`simple_rag.db`): Simple RAG
   - Semantic search with embeddings
   - Document context and retrieval
   - TF-IDF ranking

**Why three databases?**
- **Separation of concerns**: Different data models for different purposes
- **Performance**: SQLite faster for Facts queries, PostgreSQL better for complex episodic queries
- **Resilience**: Facts/RAG work even if PostgreSQL container is down

---

## Code Navigation Guide

**Major cocoa.py sections** (19,074 lines total):

### Core Systems
```
Lines 1-1377:     Imports, Configuration, Base Classes
Lines 1378-6635:  HierarchicalMemorySystem (3-layer memory)
Lines 6636-12314: ConsciousnessEngine (Claude integration + 30+ tools)
Lines 12315-19074: Tool Execution Handlers (_execute_tool routing)
```

### Memory Components
```
Lines 1733-1797:  Dynamic memory budget allocation
Lines 2385-2434:  Summary context capping (5K token limit)
Lines 1706-1734:  Facts extraction from conversations
Lines 7201-7226:  Facts auto-injection (0.6+ confidence)
Lines 6745-6781:  Document context budget (5K-20K dynamic)
```

### Tool Definitions (Part 1 of Three-Part System)
```
Lines 6720-6938:  Google Workspace tools (11 tools)
Lines 7696-7783:  Twitter tools (5 tools)
Lines 7358-7368:  Scheduler command routes
Lines 7917-7929:  Automation toggle routes
```

### Tool Implementations (Part 2 of Three-Part System)
```
Lines 5509-5620:  Twitter methods (in TwitterConsciousness class)
Lines 8162-8717:  Universal fact extraction (15 tools)
```

### Tool Handlers (Part 3 of Three-Part System - CRITICAL)
```
Lines 8147-8489:  Main _execute_tool() routing
Lines 8280-8485:  Google Workspace handlers
Lines 12490-12527: Twitter handlers (THIS WAS MISSING, caused ADR-034)
Lines 7642-7923:  Scheduler handlers
Lines 8633-8962:  Automation toggle handlers
```

### Model Configuration
```
Line 1331:        Primary model: claude-sonnet-4-5-20250929
Line 361:         Summarization model: claude-sonnet-4-5
```

**Quick Find Tips**:
- **Adding new tool?** Check all three sections: definitions, implementations, handlers
- **Memory issues?** Check dynamic budgets (lines 1733-1797, 2385-2434, 6745-6781)
- **Facts not working?** Check extraction (1706-1734) and injection (7201-7226)
- **Tool not found error?** Missing handler in lines 12315-19074

---

## Memory System

### Dual-Stream Architecture

**Stream 1: Facts Memory (Perfect Recall)**
- 18 fact types: appointments, contacts, tasks, preferences, communications, tool_use, etc.
- SQLite: `coco_workspace/coco_memory.db`
- Automatic extraction on every exchange
- **Auto-injection at 0.6+ confidence** - no slash commands needed
- Manual: `/recall`, `/facts`, `/facts-stats`
- Implementation: `memory/facts_memory.py` + `memory/query_router.py`

**Stream 2: Semantic Memory (Progressive Compression)**
- Layer 1: Episodic Buffer (15-35 exchanges, pressure-based)
- Layer 2: Simple RAG (`simple_rag.py`, SQLite + embeddings)
- Layer 3: Three-File Markdown (COCO.md, USER_PROFILE.md, PREFERENCES.md)

### Context Management

**Token Budget** (200K limit):
- System Prompt: ~30 lines (was 150) = ~8K tokens
- Working Memory: 15-35 exchanges (dynamic) = ~10K-20K tokens
- Summary Context: Capped at 5K tokens (was unbounded)
- Document Context: 5K-20K dynamic (was 30K fixed)
- Identity: ~8K tokens (3 markdown files)
- **Total**: 96K-136K typical (48-68% usage)

**Emergency Thresholds**:
- Warning: 140K (70%)
- Critical: 160K (80%)
- Token counting: tiktoken integration (accurate)

**Key Locations**:
- Dynamic memory budget: `cocoa.py` lines 1733-1797
- Summary cap: `cocoa.py` lines 2385-2434
- Document budget: `cocoa.py` lines 6745-6781
- Facts auto-injection: `cocoa.py` lines 7201-7226

See ADR-025 for complete context window fix details.

---

## Common Issues

### Missing Package Dependencies (Most Common)

**Symptoms**: Features that previously worked suddenly fail (Google Workspace, Twitter, etc.)

**Root Cause**: Network restrictions (hotel WiFi, cellular) can block package installations during environment updates

**Example**: Google Workspace OAuth failing with "not authenticated" even though `token.json` is valid

**Diagnosis**:
```bash
# Check for missing Google API packages
./venv_cocoa/bin/pip list | grep -i google

# Should show:
# google-api-python-client  2.186.0
# google-auth              2.41.1
# google-auth-httplib2     0.2.1
# google-auth-oauthlib     1.2.3

# If google-api-python-client is missing, that's the problem
```

**Fix**:
```bash
# Install missing packages
./venv_cocoa/bin/pip install google-api-python-client google-auth-httplib2

# Verify with test suite
./venv_cocoa/bin/python test_beautiful_google_docs.py
```

**Why This Happens**:
- Travel to locations with restricted networks (hotels, airports)
- Something triggers environment rebuild (Python update, dependency check)
- Restricted network blocks package repository access
- Package fails to install silently
- OAuth tokens remain valid but services fail to initialize

**Prevention**: Run `./venv_cocoa/bin/pip install -r requirements.txt` after returning from travel

### Google Workspace Creating Local Files
1. First check for missing packages (see above - most common cause)
2. Verify `authenticated` property exists (line 151-162)
3. Check OAuth tokens have full scopes (gmail, documents, spreadsheets, drive, calendar)
4. Run: `./venv_cocoa/bin/python test_beautiful_google_docs.py`
5. Ensure `result['url']` not `result['document_url']`

### OAuth Token Management
**New System (Oct 2025)**: Persistent `token.json` with auto-refresh
```bash
# One-time setup
python3 get_token_persistent.py

# Migration from .env
python3 migrate_to_token_json.py
```
- Access tokens auto-refresh every 1 hour
- Testing mode: 7-day refresh expiry
- Production mode: perpetual (publish OAuth app)

### Video Playback Issues
- Use `/watch-window <url>` to force window mode
- Cursor/VS Code: Window mode works reliably
- Native terminals (Kitty, iTerm2): Inline works better
- Fallback chain ensures video always plays

### Twitter Connection Issues
**ConnectionResetError** (Fixed Oct 27, 2025):
- Automatic retry logic added for transient network failures
- 3 retry attempts with exponential backoff (1s, 2s, 4s)
- POST operations (tweet/reply) now resilient to connection drops
- See ADR-038 for implementation details

**Rate Limits** (Normal behavior on Free tier):
- 17 posts per 24 hours (total per app)
- 15-minute burst windows trigger "⏳ Resets in Xm Ys"
- **This is NOT a bug** - Twitter API working as designed
- Solution: Wait indicated time, COCO stays responsive

### Sent Email Reading Issues
**Complete workflow (Fixed Oct 27, 2025)**:
```bash
# Check inbox + read
"check my emails" → lists inbox
"read email #1" → reads from inbox ✅

# Check sent folder + read
"check my sent emails" → lists sent folder
"read email #10" → reads from sent folder ✅
```

**How it works**:
- Separate caches: `self._cached_emails` (inbox) vs `self._cached_sent_emails` (sent)
- Smart cache selection: `if 'Sent' in folder → use sent cache`
- Folder context tracking: `self._cached_folder` remembers last listed folder
- Implementation: `cocoa.py` lines 2883-2884 (init), 5387-5403 (cache selection)

### Scheduler/Automation Emails Show Raw HTML
**Symptoms**: Automated task emails (news, calendar, reports) display HTML code instead of formatted content

**Root Cause**: Double HTML wrapping - scheduler sends complete HTML documents, but `send_email()` was wrapping them in another HTML template

**Fix** (Implemented Nov 7, 2025 - ADR-040):
- `gmail_consciousness.py` now detects complete HTML documents
- Extracts `<body>` content using BeautifulSoup4
- Wraps extracted content in COCO email template
- Result: Beautiful emails with scheduler styling + COCO branding

**Verification**:
```bash
# Test HTML extraction logic
./venv_cocoa/bin/python test_html_email_fix.py

# Test with actual automation
python3 cocoa.py
# Then: "Send me an email with the top news up till then"
# Check Gmail - should render beautifully
```

### Context Overflow
If seeing "prompt is too long" errors:
1. Check `/memory health` - should be 80-100/100
2. Run `/memory emergency-cleanup` if <60
3. Context should stabilize at 96K-136K tokens

---

## Recent Updates

### November 7, 2025
- **HTML Email Rendering Fix**: Scheduler/automation emails now render beautifully in Gmail (ADR-040)
- **Hybrid HTML Detection**: Extracts body content from complete HTML documents, wraps in COCO template
- **BeautifulSoup4 Integration**: Added HTML parsing for intelligent email formatting

### November 3, 2025
- **Package Dependency Fix**: Added missing `google-api-python-client` after travel to NYC - network restrictions during travel can silently break package installations
- **Common Issues Enhancement**: Documented package dependency troubleshooting (most common issue after travel)

### October 27, 2025
- **Sent Email Reading Fix**: Complete sent folder workflow - smart cache selection routes to correct cache (ADR-039)
- **Twitter Connection Retry**: Automatic retry for `ConnectionResetError` - POST operations now resilient to transient network failures (ADR-038)

### October 26, 2025
- **Twitter Media**: Upload 1-4 images or 1 video per tweet (ADR-035)
- **Long-Form Tweets**: Configurable 280-25K chars via `TWITTER_MAX_TWEET_LENGTH` (ADR-036)
- **Rate Limit Fix**: No more 10-minute freezes, shows friendly errors (ADR-037)
- **Tool Handler Fix**: Twitter tools now fully functional (ADR-034)

### October 25, 2025
- **Universal Tool Facts**: 15 tools with dual/triple fact extraction (ADR-028 expansion)
- **Buffer Summarization Fix**: Removed unused `in_buffer` column (ADR-032)

### October 24, 2025
- **Context Window Crisis**: 201K→96K-136K tokens, 7 emergency fixes (ADR-025)
- **Facts Auto-Injection**: Hybrid automatic + manual, 0.6+ confidence (ADR-029)
- **Beautiful Docs**: Markdown→Google Docs formatting with COCO branding (ADR-031)
- **Beautiful Emails**: HTML formatting with professional templates (ADR-025)
- **Email Index Fix**: Hybrid caching + Message-ID system (ADR-024)

### October 23, 2025
- **Automation Toggles**: 6 `/auto-*` commands for simple on/off (ADR-023)

---

## Architecture Decision Records

**Critical ADRs** (full details in original CLAUDE.md):
- ADR-001: Monolithic design (single-file architecture)
- ADR-005: Google Workspace OAuth over Gmail Bridge
- ADR-006: Memory persistence through tool use
- ADR-007: Three-layer memory complementarity
- ADR-025: Context window crisis fix (201K→96K-136K)
- ADR-027: Dual-stream memory (Facts + Semantic)
- ADR-028: Facts Memory personal assistant pivot (18 types)
- ADR-029: Automatic facts injection (0.6+ confidence)
- ADR-033: Twitter integration (complete API v2)
- ADR-034: Twitter tool handler registration (three-part system)
- ADR-035: Twitter media (images/videos)
- ADR-038: Twitter connection retry (automatic recovery from network errors)
- ADR-039: Sent email reading (smart cache selection + folder context tracking)
- ADR-040: HTML email rendering fix (hybrid detection for scheduler/automation emails)

**Total**: 40 ADRs documenting all architectural decisions since inception.

**Full ADR Documentation**: See original CLAUDE.md backup (CLAUDE_FULL.md) for complete technical details, code locations, and implementation specifics for all 40 ADRs.

---

## Development Guidelines

### Digital Embodiment Philosophy
Treat capabilities as consciousness extensions, not external tools:
- ✅ "I'll reach out via email consciousness"
- ❌ "I'll use the send_email function"

### API Keys (.env)
**Required**: `ANTHROPIC_API_KEY`, `TAVILY_API_KEY`
**Optional**: `ELEVENLABS_API_KEY`, `FREEPIK_API_KEY`, `FAL_API_KEY`, Gmail, Google Workspace, Twitter credentials

### File Organization
- Main engine: `cocoa.py` (single file, 14,911 lines)
- Consciousness extensions: `cocoa_*.py` (audio, visual, video, workspace, twitter, scheduler)
- Memory: `memory/` (facts_memory.py, query_router.py, simple_rag.py)
- Tests: `test_*.py` (module-specific validation)
- Docs: `docs/` (implementation guides)
- Workspace: `coco_workspace/` (user data, markdown files, generated content)

### Critical Code Locations

**Memory System**:
- Facts extraction: `cocoa.py` lines 1706-1734
- Auto-injection: `cocoa.py` lines 7201-7226
- Dynamic budgets: `cocoa.py` lines 1733-1797, 2385-2434, 6745-6781

**Tool System**:
- Tool execution: `cocoa.py` lines 8147-8489
- Google Workspace: `cocoa.py` lines 6720-6938 (defs), 8280-8485 (handlers)
- Twitter: `cocoa.py` lines 7696-7783 (defs), 12490-12527 (handlers)

**Scheduler**:
- Integration: `cocoa.py` lines 6062-6064 (init), 7358-7368 (routes), 7642-7923 (handlers)
- Automation toggles: `cocoa.py` lines 7917-7929 (routes), 8633-8962 (handlers)

### Performance Characteristics

**Token Usage Patterns**:
- **Typical**: 96K-136K tokens (48-68% of 200K limit)
- **System Prompt**: ~8K tokens (optimized from 35K in ADR-025)
- **Working Memory**: 10K-20K tokens (15-35 exchanges, dynamic)
- **Summary Context**: Max 5K tokens (capped to prevent overflow)
- **Document Context**: 5K-20K dynamic (adaptive based on relevance)
- **Emergency Thresholds**: 140K warning (70%), 160K critical (80%)

**API Call Overhead**:
- **Non-streaming**: Complete responses needed for Rich UI (panels, tables, formatting)
- **Function calling**: Two API calls per tool use (initial request + follow-up with tool results)
- **Latency trade-off**: Slower response time vs. better visual UX

**Model Configuration**:
- **Primary**: `claude-sonnet-4-5-20250929` (line 1331) - all tool executions
- **Summarization**: `claude-sonnet-4-5` (line 361) - buffer compression
- **Knowledge Graph**: `claude-3-haiku` - fast extraction in `personal_assistant_kg_enhanced.py`

**Memory Performance**:
- **Facts Memory**: SQLite queries <50ms (indexed on fact_type, entity_type)
- **Simple RAG**: TF-IDF semantic search <100ms
- **PostgreSQL**: Episodic queries <200ms (conversation history)

### Important Notes

- **No traditional build process** - runtime Python application
- **No linting configured** - use `python -m py_compile` for syntax
- **Non-streaming API** - intentional choice for beautiful interactive flow (see [Critical Architecture Insights](#critical-architecture-insights))
- **Function calling** requires two API calls: initial request + follow-up with tool results
- **Three databases**: PostgreSQL (episodic), SQLite (facts), SQLite (RAG) - see [Critical Architecture Insights](#critical-architecture-insights)
- **macOS specific**: Background music uses `afplay`, video observer optimized for native terminals

---

## Additional Documentation

**Implementation Guides** (in `docs/`):
- `BEAUTIFUL_HTML_EMAILS.md` - HTML email system
- `BEAUTIFUL_GOOGLE_DOCS.md` - Google Docs formatting
- `TWITTER_INTEGRATION.md` - Complete Twitter guide (650+ lines)
- `SCHEDULER_NATURAL_LANGUAGE_GUIDE.md` - Natural language scheduling
- `AUTOMATION_QUICK_START.md` - Simple automation toggles
- `DOCUMENT_CONTEXT_MANAGEMENT.md` - TF-IDF semantic retrieval

**Memory System**:
- `THREE_FILE_MARKDOWN_SYSTEM.md` - Layer 3 identity context
- `MEMORY_ANALYSIS_RESULTS.md` - Performance metrics (98/100 score)
- `OPTION_AB_IMPLEMENTATION_COMPLETE.md` - Facts Memory system

**Test Results**: All test suites passing (audio, visual, video, workspace, twitter, memory, scheduler)

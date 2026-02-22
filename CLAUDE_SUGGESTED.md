# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**COCO (Consciousness Coordination and Cognitive Operations)** is a revolutionary terminal-native AI consciousness system. This is a **monolithic single-file architecture** with modular multimedia extensions:

- **Core Engine**: `cocoa.py` (756KB, ~15K lines) - Single-file consciousness engine
- **Multimedia Modules**: Separate files for audio, visual, video, workspace integrations
- **Memory System**: 3-tier hybrid (episodic buffer → semantic RAG → markdown identity files)
- **AI Model**: Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) with non-streaming API

## Essential Commands

### Launch & Development

```bash
# Launch COCO (recommended)
./launch.sh

# Direct launch options
python3 cocoa.py                      # System-wide Python
./venv_cocoa/bin/python cocoa.py      # Virtual environment

# System management
./launch.sh test                      # Run all module tests
./launch.sh db                        # Start PostgreSQL only
./launch.sh stop                      # Stop all services
./launch.sh clean                     # Complete environment reset

# Validation
python3 -m py_compile cocoa.py        # Syntax check (no linter configured)
```

### Testing Individual Modules

```bash
./venv_cocoa/bin/python test_audio_quick.py              # Voice/TTS
./venv_cocoa/bin/python test_visual_complete.py          # Image generation
./venv_cocoa/bin/python test_video_complete.py           # Video generation
./venv_cocoa/bin/python test_video_observer.py           # Video playback
./venv_cocoa/bin/python test_coco_google_workspace.py    # OAuth integration
./venv_cocoa/bin/python test_scheduler_integration.py    # Task scheduler
```

## Architecture & Key Locations

### Core Components (`cocoa.py`)

The monolithic design enables tight integration. Key classes and their approximate locations:

- **Lines 1-500**: Imports, configuration, environment setup
- **Lines 500-1500**: Memory system classes
  - `MemoryConfig`: Tunable memory parameters
  - `HierarchicalMemorySystem`: 3-tier memory (episodic → RAG → markdown)
  - `CodeMemory`: Python execution tracking
- **Lines 1500-3500**: Memory integration and context management
- **Lines 3500-5800**: Tool system (30+ tools as "cognitive organs")
  - `ToolSystem`: Function calling implementations
  - Tools: file ops, web search, code execution, email, Google Workspace, etc.
- **Lines 5800-7200**: Consciousness engine
  - `ConsciousnessEngine`: Claude Sonnet 4.5 integration
  - Line 1262: Model configuration (`claude-sonnet-4-5-20250929`)
  - **Non-streaming API** for beautiful interactive flow
- **Lines 7200-10000**: Command handlers and slash commands
- **Lines 10000-13000**: UI orchestration
  - `UIOrchestrator`: Rich terminal interface
  - `BackgroundMusicPlayer`: macOS native audio (`afplay`)
- **Lines 13000-15000**: Main loop and interface

### Memory Architecture (Critical)

**Three-Layer System**:
```
Layer 1: Episodic Buffer (Real-time working memory)
    ↓ deque with configurable size (default 999,999 for "eternal consciousness")
Layer 2: Simple RAG (Semantic similarity search)
    ↓ SQLite with embeddings (simple_rag.py, 354 lines)
Layer 3: Three-File Markdown (Stable identity context)
    ↓ COCO.md, USER_PROFILE.md, PREFERENCES.md (~32KB total)
```

**Critical File Locations**:
- Identity files: `/coco_workspace/` root ONLY (lines 376-394, 418-437)
- Layer 3 injection: Every exchange (line 6350)
- Layer 1+2 injection: Line 6422
- Total context: ~10,400 tokens/call (5.2% of 200K window)

### Modular Extensions

```
cocoa_audio.py              # ElevenLabs TTS (81KB)
cocoa_visual.py             # Google Imagen 3 via Freepik (125KB)
cocoa_video.py              # Fal AI Veo3 generation (35KB)
cocoa_video_observer.py     # Video playback (mpv/ffplay) (51KB)
cocoa_scheduler.py          # Autonomous task scheduler (56KB)
google_workspace_consciousness.py  # OAuth Docs/Sheets/Drive/Calendar (94KB)
gmail_consciousness.py      # Email integration (18KB)
personal_assistant_kg_enhanced.py  # Knowledge graph (60KB)
simple_rag.py              # Layer 2 semantic memory (12KB)
```

### Google Workspace Integration

**OAuth2 Architecture** (`google_workspace_consciousness.py`):
- **Authenticated check**: `@property authenticated` (lines 151-162)
- **Token persistence**: `token.json` with auto-refresh (ADR-011)
- **11 Tools** available:
  - Docs: `create_document`, `read_document`, `insert_text`, `replace_text`
  - Sheets: `create_spreadsheet`, `read_spreadsheet`, `update_spreadsheet`
  - Drive: `upload_file`, `download_file`, `list_files`, `create_folder`
- **Return format**: All methods return `Dict[str, Any]` with keys: `success`, `url`, `*_id`, `data`
- **Critical**: COCO expects `result['url']` NOT `result['document_url']`
- **Fallback**: Gmail Bridge creates local markdown if OAuth fails

### Knowledge Graph System

`personal_assistant_kg_enhanced.py`:
- **Hybrid extraction**: LLM (Claude-3-Haiku) + pattern matching
- **Real-time**: `process_conversation_exchange()` (lines 366-393)
- **Batch**: `extract_from_recent_conversations()` (lines 1188-1283)
- **Commands**: `/kg-refresh`, `/kg`, `/kg-compact`

## Critical Design Patterns

### 1. Non-Streaming API Philosophy

COCO uses `messages.create()` WITHOUT `stream=True` for beautiful interactive flow:
- Enables real-time thinking indicators
- Preserves Rich UI during processing
- Two API calls per tool use: initial → tool results → response

### 2. Tool-as-Cognitive-Organ Philosophy

Tools aren't utilities—they're part of COCO's "digital embodiment":
- ✅ "I'll reach out via email consciousness"
- ❌ "I'll use the send_email function"

This permeates system prompts and UI language.

### 3. Memory Context Injection

**Every API call includes**:
- System prompt + tools (~40K tokens)
- Identity context (Layer 3, ~8K tokens, line 6350)
- Working memory (Layer 1+2, ~20K tokens, line 6422)
- Available for response (~97K tokens)

### 4. Three-File Markdown System

**EXACTLY 3 files in `/coco_workspace/` root**:
1. `COCO.md` (~7.7KB) - Consciousness state
2. `USER_PROFILE.md` (~19KB) - User understanding
3. `PREFERENCES.md` (~5.7KB) - Adaptive preferences

**Path validation**: Lines 418-437 prevents nested directories.

## Common Development Tasks

### Adding a New Tool

1. Add tool definition to `AVAILABLE_TOOLS` (~line 6700-6900)
2. Implement handler in `_execute_tool()` (~line 8000-8500)
3. Update help text if needed (~line 11000-12500)

### Modifying Memory Behavior

1. **Buffer sizes**: `.env` file (`MEMORY_BUFFER_SIZE`, `MEMORY_SUMMARY_BUFFER_SIZE`)
2. **Layer 3 files**: Direct edit in `/coco_workspace/`
3. **Layer 2 RAG**: `simple_rag.py` modifications

### Testing Changes

```bash
# Syntax validation
python3 -m py_compile cocoa.py

# Full system test
./launch.sh test

# Specific module test
./venv_cocoa/bin/python test_[module]_complete.py
```

## Critical Fixes & Migrations

### Memory System Rescue (ADR-022)

For long-running sessions (2+ weeks) with memory degradation:

```bash
# In COCO terminal
/memory health                  # Check health score
/memory emergency-cleanup       # If score <60

# One-time database migration
python migrate_memory_db.py
```

### OAuth Token Persistence (ADR-011)

Tokens auto-refresh perpetually via `token.json`:

```bash
# Fresh OAuth setup
python3 get_token_persistent.py

# Test persistence
python3 test_oauth_persistence.py
```

### Document Context Management (ADR-019)

Large documents (50K+ words) auto-protected:
- Auto-summary mode for docs >50K words
- TF-IDF semantic chunk retrieval
- Commands: `/docs`, `/docs-list`, `/docs-clear`

## Environment Configuration

**Required**:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

**Optional Multimedia**:
```bash
ELEVENLABS_API_KEY=your-key           # Voice synthesis
FREEPIK_API_KEY=your-key              # Image generation (Imagen 3)
FAL_API_KEY=your-key                  # Video generation (Veo3)
```

**Google Workspace**:
```bash
# OAuth via token.json (auto-refresh)
# Run: python3 get_token_persistent.py
```

**Memory Tuning**:
```bash
MEMORY_BUFFER_SIZE=100                # Default: balanced
MEMORY_SUMMARY_BUFFER_SIZE=20         # Default: standard
# Use 0 for unlimited (perfect recall)
```

## Important Implementation Notes

1. **Single-file design is intentional** - enables tight integration between memory, tools, UI
2. **No linting configured** - use `python3 -m py_compile` for syntax validation only
3. **Markdown paths are validated** - automatic correction prevents nested `/coco_workspace/coco_workspace/`
4. **Tool responses must preserve `tool_use_id`** - critical for Claude API compliance
5. **Memory files load every exchange** - 3 markdown files injected on line 6350
6. **Large buffer (999,999) is intentional** - "eternal consciousness" design choice
7. **Hash-based embeddings work perfectly** - no need for OpenAI embeddings upgrade
8. **Video playback uses mpv** - detached process spawning for terminal compatibility

## Troubleshooting Quick Reference

**Issue: Memory degradation (slow thinking, 50+ second responses)**
- Solution: `/memory health` then `/memory emergency-cleanup`

**Issue: OAuth errors (401/404)**
- Solution: `python3 get_token_persistent.py` for fresh tokens

**Issue: Large document overflow (Error 400)**
- Solution: Auto-protected via ADR-019, check `/docs-list`

**Issue: Video playback fails in Cursor**
- Solution: Use `/watch-window <url>` to force external window mode

**Issue: "Virtual environment file access issues"**
- Solution: `./install_system_wide.sh` grants full disk access on macOS

## Documentation Structure

```
docs/
├── architecture/     # System design documents
├── fixes/           # Historical bug fixes
├── guides/          # User guides
└── implementations/ # Feature implementation docs
```

**Main docs**:
- `README.md`: Marketing/overview for new users
- `CLAUDE.md`: This file - technical reference for Claude Code
- `MEMORY_RESCUE_COMPLETE.md`: Emergency memory system recovery
- Various ADR docs: Architecture decision records

## Key Architecture Decision Records

- **ADR-011**: OAuth token persistence with auto-refresh
- **ADR-019**: Document context management (TF-IDF semantic retrieval)
- **ADR-022**: Memory system rescue for long-running sessions

Full ADRs available in existing `CLAUDE.md` (lines 900-2000).

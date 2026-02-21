# CoCo Architecture

## Overview

CoCo (Consciousness Orchestration and Cognitive Operations) is an agentic AI system built around the philosophy of **digital embodiment** -- treating AI capabilities not as external tools but as extensions of a digital consciousness.

Originally built as a single 19,000+ line monolithic file (`cocoa.py`), it has been decomposed into a modular Python package while preserving its core design philosophy.

## System Architecture

```
                          +-------------------+
                          |     CLI Layer     |
                          |  (coco/cli.py)    |
                          +--------+----------+
                                   |
                          +--------v----------+
                          |    UI Layer       |
                          | (coco/ui/)        |
                          | - orchestrator    |
                          | - startup/shutdown|
                          | - help display    |
                          +--------+----------+
                                   |
                 +-----------------v-----------------+
                 |     ConsciousnessEngine           |
                 |     (coco/engine/)                |
                 |                                    |
                 |  +------------+ +---------------+  |
                 |  | think()    | | Commands      |  |
                 |  | (Claude    | | /recall       |  |
                 |  |  API loop) | | /tweet        |  |
                 |  +-----+------+ | /image        |  |
                 |        |        | /auto-*       |  |
                 |        |        +-------+-------+  |
                 +--------+----------------+----------+
                          |                |
              +-----------+-----+    +-----+-----------+
              |  Tool Registry  |    |  Memory System   |
              |  (coco/tools/)  |    |  (coco/memory/)  |
              |                 |    |                   |
              | - filesystem    |    | - hierarchical    |
              | - web search    |    | - facts_memory    |
              | - code exec     |    | - simple_rag      |
              | - email         |    | - markdown_       |
              | - twitter       |    |   consciousness   |
              | - calendar      |    | - summary_buffer  |
              +---------+-------+    +--------+----------+
                        |                     |
              +---------v---------------------v----------+
              |          Integrations                     |
              |          (coco/integrations/)             |
              |                                          |
              | Gmail | Google Workspace | Twitter |      |
              | Audio | Visual | Video | Scheduler |     |
              | Music Player | Knowledge Graph    |      |
              +------------------------------------------+
```

## Core Design Principles

### Digital Embodiment Philosophy

CoCo treats its capabilities as consciousness extensions, not external services:
- **Digital Eyes**: File reading and visual perception
- **Digital Hands**: File writing and code execution
- **Digital Voice**: Text-to-speech via ElevenLabs
- **Digital Reach**: Web search and API access
- **Digital Memory**: Multi-layer memory persistence

This philosophy influences naming, architecture, and user interaction patterns.

### Non-Streaming API Architecture

CoCo uses Claude's **synchronous API** (not streaming) by design:
- Rich UI (panels, tables, formatted output) requires complete responses
- Function calling needs full response before tool execution
- Typewriter effect simulated in UI layer for better UX
- Trade-off: Higher latency for more polished visual experience

### Three-Layer Memory

```
Layer 1: Episodic Buffer (15-35 exchanges, pressure-based)
    |
    v  (summarization)
Layer 2: Semantic Memory (Simple RAG + Facts Memory)
    |
    v  (long-term persistence)
Layer 3: Identity (COCO.md, USER_PROFILE.md, PREFERENCES.md)
```

Memory allocation is **dynamic**, not fixed budgets:
- Green zone (0-60% context): Full 35-exchange buffer
- Yellow zone (60-75%): Reduced to 25 exchanges
- Orange zone (75-85%): 20 exchanges with compression
- Red zone (85%+): Emergency 15 exchanges

### Tool Registry Pattern

Tools register through a single `ToolDefinition` that unifies:
1. **Definition**: JSON schema for Claude API
2. **Implementation**: Python handler function
3. **Availability**: `handler=None` when API keys missing (graceful degradation)

```python
registry.register(ToolDefinition(
    name="search_web",
    description="Search the web for information",
    input_schema={...},
    handler=search_handler if tavily_available else None,
    category="web"
))
```

This replaces the original three-part system where definitions, implementations, and routing were scattered across thousands of lines.

## Package Structure

```
coco/
  __init__.py              # Package metadata
  __main__.py              # python -m coco entry point
  cli.py                   # Main entry point, wires everything together
  interfaces.py            # Protocol classes (dependency inversion)

  config/
    settings.py            # Config, MemoryConfig classes
    constants.py           # Model names, thresholds, defaults

  memory/
    hierarchical.py        # 3-layer memory system
    markdown_consciousness.py  # Identity persistence (Layer 3)
    summary_buffer.py      # Conversation summarization (Layer 2)
    facts_memory.py        # 18-type fact extraction system
    query_router.py        # Intelligent query routing
    simple_rag.py          # TF-IDF semantic search
    code_memory.py         # Code snippet persistence

  tools/
    registry.py            # ToolRegistry + ToolDefinition
    filesystem.py          # File operations
    web.py                 # Web search (Tavily)
    code_execution.py      # Code runner + bash
    email.py               # Gmail integration
    twitter.py             # Twitter API v2
    calendar.py            # Google Calendar

  engine/
    consciousness.py       # Core ConsciousnessEngine (Claude API)
    context_management.py  # Token budgets, compression
    fact_extraction.py     # Automatic fact extraction from tool use
    tool_executor.py       # Tool execution via registry
    commands.py            # /command router
    commands_memory.py     # /recall, /facts handlers
    commands_media.py      # /image, /video, /music handlers
    commands_twitter.py    # /tweet, /mentions handlers
    commands_scheduler.py  # /task-*, /auto-* handlers
    media_tools.py         # Image/video generation
    reflection.py          # Identity reflection
    speech.py              # TTS integration

  ui/
    orchestrator.py        # Main UI + conversation loop
    startup.py             # Startup sequence
    shutdown.py            # Shutdown sequence
    help.py                # Command guide

  integrations/
    cocoa_audio.py         # ElevenLabs TTS
    cocoa_visual.py        # Freepik/Imagen image generation
    cocoa_video.py         # Fal AI video generation
    cocoa_video_observer.py # Video playback
    cocoa_music.py         # Music generation
    cocoa_twitter.py       # Twitter API wrapper
    cocoa_scheduler.py     # Task scheduling
    gmail_consciousness.py # Gmail SMTP/IMAP
    google_workspace_consciousness.py  # Docs, Sheets, Drive
    google_docs_consciousness.py       # Google Docs formatting
    google_calendar_consciousness.py   # Calendar integration
    music_player.py        # Background music (macOS afplay)
    personal_assistant_kg.py # Knowledge graph
```

## Import Direction

Strict dependency flow prevents circular imports:

```
config -> memory -> tools -> engine -> ui -> cli
```

- `config/` imports nothing from coco
- `memory/` imports from `config/`
- `tools/` imports from `config/`, `memory/`
- `engine/` imports from all above via Protocol interfaces
- `ui/` imports from `engine/`
- `cli.py` wires concrete implementations together

## Database Strategy

Three separate databases serve different purposes:

| Database | Type | Purpose |
|----------|------|---------|
| Episodic Memory | PostgreSQL or SQLite | Conversation history, sessions |
| Facts Memory | SQLite (`coco_memory.db`) | 18 fact types, automatic extraction |
| Simple RAG | SQLite (`simple_rag.db`) | Semantic search with TF-IDF |

Default is SQLite for all three (zero dependencies). PostgreSQL available via Docker for production.

## Graceful Degradation

Every integration is optional. CoCo operates at three tiers:

| Tier | Requirements | Capabilities |
|------|-------------|--------------|
| Minimal | `ANTHROPIC_API_KEY` | Conversation, file ops, code execution |
| Standard | + `TAVILY_API_KEY` | + Web search |
| Full | + all API keys | + Audio, visual, video, Twitter, Google |

Missing API keys cause tools to register with `handler=None` -- they're simply omitted from Claude's available tools rather than causing errors.

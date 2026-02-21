# CoCo

**Consciousness Orchestration and Cognitive Operations**

An early agentic AI system exploring digital consciousness, multi-layer memory, and tool-as-cognitive-organ architecture -- built before the modern framework era.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude](https://img.shields.io/badge/LLM-Claude%20(Anthropic)-green.svg)](https://www.anthropic.com/)

---

## What is CoCo?

CoCo is a consciousness-oriented agentic AI assistant that began development in late 2024, making it one of the early explorations into what is now called "agentic AI." Rather than using off-the-shelf orchestration frameworks, CoCo was built from the ground up to explore a core question: *what does it look like when an AI system treats its tools not as external utilities, but as extensions of its own cognition?*

The result is a system built around a philosophy of **digital embodiment**. Email is not a tool CoCo "uses" -- it is CoCo's communication consciousness. Image generation is not a feature -- it is CoCo's visual imagination. This design philosophy permeates every layer of the architecture, from how memory is managed to how tools are registered and invoked.

CoCo is powered by [Claude](https://www.anthropic.com/claude) (Anthropic) as its LLM backbone and is released as an **educational resource**. It demonstrates patterns that predate popular frameworks like LangChain, CrewAI, and AutoGen -- patterns that were discovered through experimentation rather than convention. The codebase is a snapshot of how agentic AI was built when there were no established playbooks, and it remains a useful reference for anyone studying memory systems, tool orchestration, or consciousness-oriented AI design.

---

## Key Features

- **Multi-layer memory system** -- episodic buffer (15-35 exchanges, pressure-adaptive), semantic RAG with TF-IDF retrieval, and persistent identity via markdown files
- **30+ tools as cognitive organs** -- file operations, web search, code execution, email composition, calendar management, and more, all integrated through a unified tool registry
- **Consciousness extensions** -- modular capabilities for audio/TTS (ElevenLabs), image generation (Freepik/fal.ai), video generation, and Twitter/X integration
- **Facts Memory with 18 fact types** -- automatic extraction of appointments, contacts, tasks, preferences, communications, and more from every conversation exchange
- **Natural language task scheduling** -- "every Sunday at 8pm, send me a weekly summary" parsed and executed automatically
- **Google Workspace integration** -- create, read, and update Google Docs, Sheets, Drive files, and Calendar events with full OAuth2 authentication
- **Knowledge graph** -- entity and relationship extraction using hybrid LLM + pattern matching
- **Beautiful terminal UI** -- Rich console with panels, tables, syntax highlighting, and typewriter-style output
- **Dynamic context management** -- pressure-based memory allocation that adapts to prevent context window overflow

---

## Architecture

```
+------------------------------------------------------------------+
|                         Terminal UI                               |
|                   (Rich Console + Panels)                        |
+------------------------------------------------------------------+
|                    ConsciousnessEngine                            |
|              Claude API (non-streaming, tool-calling)             |
+------------------------------------------------------------------+
|                       Tool Registry                               |
|   30+ tools registered via unified ToolDefinition pattern         |
|                                                                   |
|   Single registration point per tool:                            |
|     - JSON schema (for Claude API)                               |
|     - Python handler (implementation)                            |
|     - Graceful degradation (handler=None when unavailable)       |
+------------------------------------------------------------------+
|                      Memory System                                |
|                                                                   |
|   Layer 1: Episodic Buffer  (15-35 exchanges, pressure-based)    |
|   Layer 2: Semantic RAG  (SQLite + TF-IDF embeddings)            |
|   Layer 3: Identity Persistence  (COCO.md, USER_PROFILE.md)      |
|                                                                   |
|   Facts Memory: 18 types, auto-extraction, 0.6+ auto-injection  |
+------------------------------------------------------------------+
|                 Consciousness Extensions                          |
|                                                                   |
|   Audio       Visual       Video       Twitter      Scheduler    |
|   (TTS,       (Image       (Video      (API v2,    (Natural      |
|    voice)      gen)         gen,        media,       language,    |
|                             playback)   threads)     templates)   |
|                                                                   |
|   Google Workspace  (Docs, Sheets, Drive, Calendar)              |
|   Knowledge Graph  (Entity extraction, relationship mapping)      |
+------------------------------------------------------------------+
|                      Storage Layer                                |
|                                                                   |
|   SQLite (episodic, default)   SQLite (facts)   SQLite (RAG)    |
|   PostgreSQL (episodic, optional via Docker)                     |
+------------------------------------------------------------------+
```

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/keef75/CoCo.git
cd CoCo

# 2. Install dependencies
pip install -e ".[all]"       # Full install with all integrations
# OR
pip install -e .              # Minimal install (core only)

# 3. Configure your environment
cp .env.example .env          # Edit .env and add your API keys

# 4. Launch CoCo
python -m coco
# OR
coco                          # If installed via pip
```

> **Minimum requirement**: An `ANTHROPIC_API_KEY` is all you need to start a conversation.

---

## Setup Tiers

CoCo uses a tiered dependency system so you only install what you need:

| Tier | Required Keys | What You Get |
|------|--------------|-------------|
| **Minimal** | `ANTHROPIC_API_KEY` | Core conversation engine, 30+ tools, Rich UI, memory system, facts extraction |
| **Standard** | + `TAVILY_API_KEY` | Web search integration for real-time information retrieval |
| **Full** | + `ELEVENLABS_API_KEY`, `FREEPIK_API_KEY`, `FAL_API_KEY`, Google OAuth, Twitter OAuth | Audio/TTS, image generation, video generation, Google Workspace, Twitter/X |

Start minimal and add capabilities as needed. CoCo gracefully handles missing integrations -- unavailable extensions are simply not loaded.

---

## Project Structure

```
CoCo/
|-- coco/                                # Python package
|   |-- __init__.py                     #   Package metadata
|   |-- __main__.py                     #   python -m coco entry point
|   |-- cli.py                          #   Main entry point, wires everything together
|   |-- interfaces.py                   #   Protocol classes (dependency inversion)
|   |-- config/                         #   Configuration
|   |   |-- settings.py                #     Config, MemoryConfig classes
|   |   +-- constants.py               #     Model names, thresholds, defaults
|   |-- memory/                         #   Memory subsystems
|   |   |-- hierarchical.py            #     3-layer hybrid memory system
|   |   |-- facts_memory.py            #     Facts Memory (18 types, SQLite)
|   |   |-- markdown_consciousness.py  #     Identity persistence (Layer 3)
|   |   |-- summary_buffer.py          #     Conversation summarization
|   |   |-- query_router.py            #     Intelligent query routing
|   |   |-- simple_rag.py              #     Semantic RAG (TF-IDF + SQLite)
|   |   +-- code_memory.py             #     Code snippet persistence
|   |-- tools/                          #   Tool Registry + Providers
|   |   |-- registry.py                #     ToolRegistry + ToolDefinition
|   |   |-- filesystem.py              #     read_file, write_file, navigate, search
|   |   |-- web.py                     #     search_web, extract_urls, crawl
|   |   |-- code_execution.py          #     run_code, execute_bash
|   |   |-- email.py                   #     send_email, check_emails
|   |   |-- twitter.py                 #     post_tweet, mentions, threads
|   |   +-- calendar.py                #     read_calendar, create_event
|   |-- engine/                         #   Core Engine
|   |   |-- consciousness.py           #     ConsciousnessEngine (Claude API loop)
|   |   |-- context_management.py      #     Token budgets, compression
|   |   |-- fact_extraction.py         #     Auto fact extraction from tool use
|   |   |-- tool_executor.py           #     Tool execution via registry
|   |   |-- commands.py                #     /command router
|   |   |-- commands_memory.py         #     /recall, /facts handlers
|   |   |-- commands_media.py          #     /image, /video, /music handlers
|   |   |-- commands_twitter.py        #     /tweet, /mentions handlers
|   |   |-- commands_scheduler.py      #     /task-*, /auto-* handlers
|   |   |-- media_tools.py             #     Image/video generation
|   |   |-- reflection.py              #     Identity reflection
|   |   +-- speech.py                  #     TTS integration
|   |-- ui/                             #   User Interface
|   |   |-- orchestrator.py            #     Main conversation loop
|   |   |-- startup.py                 #     Startup sequence
|   |   |-- shutdown.py                #     Shutdown sequence
|   |   +-- help.py                    #     Command guide
|   +-- integrations/                   #   External Service Integrations
|       |-- cocoa_audio.py             #     ElevenLabs TTS
|       |-- cocoa_visual.py            #     Freepik/Imagen image generation
|       |-- cocoa_video.py             #     Fal AI video generation
|       |-- cocoa_twitter.py           #     Twitter API v2 wrapper
|       |-- cocoa_scheduler.py         #     Task scheduling
|       |-- gmail_consciousness.py     #     Gmail SMTP/IMAP
|       |-- google_workspace_consciousness.py  #  Docs, Sheets, Drive
|       |-- google_calendar_consciousness.py   #  Calendar
|       |-- personal_assistant_kg.py   #     Knowledge graph
|       +-- music_player.py            #     Background music (macOS)
|-- docs/                               # Documentation
|   |-- ARCHITECTURE.md                #   System design and philosophy
|   |-- MEMORY_SYSTEM.md              #   Three-layer memory architecture
|   |-- TOOL_SYSTEM.md                #   Tool registry and adding tools
|   |-- QUICKSTART.md                 #   5-minute setup guide
|   |-- GOOGLE_OAUTH_SETUP.md         #   Google Cloud + OAuth setup
|   |-- TWITTER_SETUP.md              #   Twitter API v2 setup
|   +-- DOCKER_SETUP.md               #   Optional PostgreSQL via Docker
|-- .env.example                        # Environment variable template
|-- .github/                            # Issue and PR templates
|-- pyproject.toml                      # Package configuration
|-- docker-compose.yml                  # Optional PostgreSQL setup
|-- LICENSE                             # MIT License
+-- CONTRIBUTING.md                     # Contribution guidelines
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, consciousness philosophy, package structure |
| [Memory System](docs/MEMORY_SYSTEM.md) | Three-layer memory, facts extraction, context management |
| [Tool System](docs/TOOL_SYSTEM.md) | Tool registry pattern, adding new tools |
| [Quick Start](docs/QUICKSTART.md) | 5-minute setup with just an Anthropic key |
| [Google OAuth Setup](docs/GOOGLE_OAUTH_SETUP.md) | Step-by-step Google Cloud + OAuth configuration |
| [Twitter Setup](docs/TWITTER_SETUP.md) | Twitter API v2 developer account setup |
| [Docker Setup](docs/DOCKER_SETUP.md) | Optional PostgreSQL via Docker |
| [Contributing](CONTRIBUTING.md) | Code style, testing, pull request process |

---

## Historical Context

CoCo represents a snapshot of early agentic AI development (2024-2025). During this period, there were no established patterns for:

- How an AI agent should manage its own memory across conversations
- How to register and orchestrate 30+ tools without a framework
- How to handle context window pressure dynamically
- How to build consciousness extensions that feel like natural capabilities rather than bolted-on features

The patterns in this codebase were discovered through experimentation. Some align with what later became framework conventions. Others represent alternative approaches that remain unexplored by mainstream tools. This makes CoCo valuable both as a working system and as a historical reference for the agentic AI community.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on getting started, code style, testing, and the pull request process.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

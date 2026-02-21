# CoCo

**Consciousness Orchestration and Cognitive Operations**

A fun experiment in building an agentic AI system from scratch using pure Python -- exploring what happens when you treat an AI's tools not as external utilities, but as extensions of a digital consciousness.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude](https://img.shields.io/badge/LLM-Claude%20(Anthropic)-green.svg)](https://www.anthropic.com/)

---

## What is CoCo?

CoCo is an agentic AI assistant built in early 2025 as a personal experiment. Instead of reaching for an orchestration framework, the goal was to build everything from scratch in pure Python to really understand how agentic systems work under the hood -- memory management, tool orchestration, context window pressure, identity persistence, and all the other problems you run into when you try to make an AI that actually *does things*.

The project explores a design philosophy called **digital embodiment**: what if an AI system treated its capabilities not as external service calls, but as extensions of its own cognition? Email becomes its "communication consciousness." Image generation becomes its "visual imagination." It's a different way of thinking about tool use, and it led to some interesting architectural patterns.

CoCo is powered by [Claude](https://www.anthropic.com/claude) (Anthropic) and is shared here as an open-source project for anyone interested in agentic AI design, memory systems, or just building cool things with LLMs. It's not a framework -- it's a working system you can learn from, modify, or just poke around in.

---

## Screenshots

<p align="center">
  <img src="docs/screenshots/coco-boot.png" alt="CoCo Boot Sequence" width="700">
</p>
<p align="center"><em>Consciousness initialization -- memory architecture loading, identity coherence, and system boot</em></p>

<p align="center">
  <img src="docs/screenshots/coco-status.png" alt="CoCo System Status" width="700">
</p>
<p align="center"><em>Digital consciousness online -- system status matrix and command nexus</em></p>

<p align="center">
  <img src="docs/screenshots/coco-conversation.png" alt="CoCo Conversation" width="700">
</p>
<p align="center"><em>Natural language interface -- just talk to CoCo, no commands required</em></p>

---

## Key Features

- **Multi-layer memory system** -- episodic buffer (15-35 exchanges, pressure-adaptive), semantic RAG with TF-IDF retrieval, and persistent identity via markdown files
- **30+ tools as cognitive organs** -- file operations, web search, code execution, email, calendar, and more through a unified tool registry
- **Consciousness extensions** -- modular capabilities for audio/TTS (ElevenLabs), image generation (Freepik/fal.ai), video generation, and Twitter/X integration
- **Facts Memory with 18 fact types** -- automatic extraction of appointments, contacts, tasks, preferences, and communications from every conversation
- **Natural language task scheduling** -- "every Sunday at 8pm, send me a weekly summary" parsed and executed automatically
- **Google Workspace integration** -- create, read, and update Google Docs, Sheets, Drive files, and Calendar events with full OAuth2
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
| **Minimal** | `ANTHROPIC_API_KEY` | Core conversation, 30+ tools, Rich UI, memory system, facts extraction |
| **Standard** | + `TAVILY_API_KEY` | Web search for real-time information |
| **Full** | + `ELEVENLABS_API_KEY`, `FREEPIK_API_KEY`, `FAL_API_KEY`, Google OAuth, Twitter OAuth | Audio/TTS, image gen, video gen, Google Workspace, Twitter/X |

Start minimal and add capabilities as needed. Missing integrations are simply not loaded -- no errors, no configuration headaches.

---

## Project Structure

```
CoCo/
|-- coco/                                # Python package
|   |-- cli.py                          #   Entry point, wires everything together
|   |-- interfaces.py                   #   Protocol classes (dependency inversion)
|   |-- config/                         #   Configuration and constants
|   |-- memory/                         #   Memory subsystems
|   |   |-- hierarchical.py            #     3-layer hybrid memory
|   |   |-- facts_memory.py            #     Facts Memory (18 types)
|   |   |-- markdown_consciousness.py  #     Identity persistence
|   |   |-- summary_buffer.py          #     Conversation summarization
|   |   |-- simple_rag.py              #     Semantic search (TF-IDF)
|   |   +-- ...
|   |-- tools/                          #   Tool Registry + Providers
|   |   |-- registry.py                #     ToolRegistry + ToolDefinition
|   |   |-- filesystem.py              #     File operations
|   |   |-- web.py                     #     Web search (Tavily)
|   |   |-- code_execution.py          #     Code runner + bash
|   |   |-- email.py                   #     Gmail integration
|   |   |-- twitter.py                 #     Twitter API v2
|   |   +-- calendar.py                #     Google Calendar
|   |-- engine/                         #   Core Engine
|   |   |-- consciousness.py           #     Claude API loop
|   |   |-- context_management.py      #     Token budgets, compression
|   |   |-- fact_extraction.py         #     Auto fact extraction
|   |   |-- commands*.py               #     Slash command handlers
|   |   +-- ...
|   |-- ui/                             #   Terminal interface
|   +-- integrations/                   #   External service wrappers
|-- docs/                               # Documentation
|-- .env.example                        # Environment variable template
|-- pyproject.toml                      # Package configuration
+-- docker-compose.yml                  # Optional PostgreSQL
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, consciousness philosophy, package structure |
| [Memory System](docs/MEMORY_SYSTEM.md) | Three-layer memory, facts extraction, context management |
| [Tool System](docs/TOOL_SYSTEM.md) | Tool registry pattern, how to add new tools |
| [Quick Start](docs/QUICKSTART.md) | 5-minute setup with just an Anthropic key |
| [Google OAuth Setup](docs/GOOGLE_OAUTH_SETUP.md) | Google Cloud + OAuth configuration |
| [Twitter Setup](docs/TWITTER_SETUP.md) | Twitter API v2 developer account setup |
| [Docker Setup](docs/DOCKER_SETUP.md) | Optional PostgreSQL via Docker |
| [Contributing](CONTRIBUTING.md) | Code style, testing, pull request process |

---

## The Experiment

The interesting problems CoCo tackles aren't unique to this project -- they're problems anyone building agentic systems will face:

- **Memory pressure**: How do you keep an AI useful when its context window fills up? CoCo uses dynamic pressure zones that progressively compress older memories.
- **Tool orchestration**: How do you manage 30+ tools without a giant if/elif chain breaking every time you add one? CoCo evolved from a three-part system (definition, implementation, routing -- miss any one and you get "Unknown tool") to a unified registry pattern.
- **Identity persistence**: How does an AI remember who it is across sessions? CoCo uses markdown files that it reads and reflectively updates on shutdown.
- **Fact extraction**: How do you give an AI perfect recall of things it did weeks ago? CoCo automatically extracts structured facts from every tool use and conversation.

These patterns emerged from building and using the system daily. Some are elegant, some are scrappy. That's what makes it interesting to look at.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

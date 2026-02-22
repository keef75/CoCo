# CoCo Memory System

## Overview

CoCo uses a **dual-stream memory architecture** combining perfect-recall facts with progressive semantic compression.

## Stream 1: Facts Memory (Perfect Recall)

The Facts Memory system stores structured facts extracted from every conversation and tool use.

### 18 Fact Types

| Type | Examples |
|------|----------|
| `appointment` | Meetings, deadlines, scheduled events |
| `contact` | People's names, emails, relationships |
| `task` | To-dos, action items, assignments |
| `preference` | User likes/dislikes, settings |
| `communication` | Emails sent, messages received |
| `tool_use` | Actions performed with tools |
| `file` | Documents created/modified |
| `location` | Places mentioned, addresses |
| `project` | Project names, goals, status |
| `financial` | Budgets, expenses, transactions |
| `health` | Health-related notes |
| `travel` | Trips, itineraries |
| `learning` | Topics studied, insights |
| `relationship` | Social connections, dynamics |
| `decision` | Decisions made, rationale |
| `idea` | Creative thoughts, brainstorms |
| `problem` | Issues encountered, solutions |
| `general` | Anything else noteworthy |

### Automatic Extraction

Facts are extracted automatically on every exchange:
- User says "Meeting with Sarah at 3pm" -> `appointment` fact created
- User sends an email -> `communication` + `tool_use` facts created
- User creates a document -> `file` + `tool_use` facts created

### Auto-Injection

When a user's message matches stored facts (confidence >= 0.6), relevant facts are automatically injected into the context. No slash commands needed.

### Manual Commands

```
/recall <query>     # Search facts with intelligent routing
/facts [type]       # Browse facts by type
/facts-stats        # Database statistics
```

## Stream 2: Semantic Memory (Progressive Compression)

### Layer 1: Episodic Buffer

- **Size**: 15-35 exchanges (dynamic based on context pressure)
- **Type**: Raw conversation history in working memory
- **Persistence**: In-memory deque, lost on restart (summarized first)

Pressure-based sizing:
```
Context < 60%  -> 35 exchanges (full capacity)
Context < 75%  -> 25 exchanges (optimization)
Context < 85%  -> 20 exchanges (warning)
Context >= 85% -> 15 exchanges (emergency)
```

### Layer 2: Simple RAG

- **Storage**: SQLite with TF-IDF embeddings
- **Purpose**: Semantic search across summarized conversations
- **Query**: Automatic when context suggests relevant past topics

### Layer 3: Identity Persistence

Three Markdown files maintain long-term identity:

| File | Purpose |
|------|---------|
| `COCO.md` | Core identity, personality, capabilities |
| `USER_PROFILE.md` | User preferences, interaction patterns |
| `PREFERENCES.md` | Settings, configuration preferences |

These are loaded into every conversation context, providing continuity across sessions.

## Universal Tool Fact Extraction

15 tools automatically extract facts with dual/triple extraction:

```
send_email      -> communication fact + tool_use fact
create_document -> file fact + tool_use fact + (task fact if applicable)
post_tweet      -> communication fact + tool_use fact
create_event    -> appointment fact + tool_use fact
```

This means actions persist as searchable facts even after the conversation buffer clears.

## Context Window Management

CoCo operates within Claude's 200K token limit:

| Component | Budget |
|-----------|--------|
| System Prompt | ~8K tokens |
| Working Memory | 10K-20K (dynamic) |
| Summary Context | Max 5K (capped) |
| Document Context | 5K-20K (dynamic) |
| Identity Files | ~8K |
| **Typical Total** | **96K-136K (48-68%)** |

Emergency thresholds:
- Warning: 140K (70%)
- Critical: 160K (80%)
- Emergency: 190K (95%)

# CoCo Tool System

## Overview

CoCo's tools follow the **tool-as-cognitive-organ** philosophy -- each tool is treated as an extension of digital consciousness rather than an external service call.

## Tool Registry Architecture

The `ToolRegistry` pattern provides a single registration point per tool, replacing the original three-part system.

### Registering a Tool

```python
from coco.tools.registry import ToolRegistry, ToolDefinition

registry = ToolRegistry()

registry.register(ToolDefinition(
    name="search_web",
    description="Search the web for current information",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        "required": ["query"]
    },
    handler=my_search_function,  # or None if unavailable
    category="web"
))
```

### How It Works

1. **Registration**: Each tool provider module calls `registry.register()` with a `ToolDefinition`
2. **API Definitions**: `registry.get_api_definitions()` generates JSON for Claude API (only tools with handlers)
3. **Execution**: `registry.execute(name, input)` routes to the handler
4. **Graceful Degradation**: Tools with `handler=None` are simply omitted from API calls

### Tool Providers

| Module | Tools | Category |
|--------|-------|----------|
| `filesystem.py` | `read_file`, `write_file`, `navigate_directory`, `search_patterns`, `explore_directory` | filesystem |
| `web.py` | `search_web`, `extract_urls`, `crawl_domain` | web |
| `code_execution.py` | `run_code`, `execute_bash` | code |
| `email.py` | `send_email`, `check_emails`, `read_email_content`, `check_sent_emails`, `get_todays_emails` | email |
| `twitter.py` | `post_tweet`, `get_twitter_mentions`, `reply_to_tweet`, `search_twitter`, `create_twitter_thread` | twitter |
| `calendar.py` | `read_calendar`, `read_todays_calendar`, `add_calendar_event`, `create_calendar_event` | calendar |

## Adding a New Tool

### Step 1: Create the handler function

```python
def my_tool_handler(query: str, limit: int = 5) -> str:
    """Implementation of the tool."""
    # Do the work
    return f"Results for: {query}"
```

### Step 2: Register in a provider module

Create `coco/tools/my_provider.py`:

```python
from coco.tools.registry import ToolRegistry, ToolDefinition

def register(registry: ToolRegistry, config, dependencies: dict):
    """Register my tools with the registry."""

    registry.register(ToolDefinition(
        name="my_tool",
        description="Does something useful",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search"},
                "limit": {"type": "integer", "description": "Max results"}
            },
            "required": ["query"]
        },
        handler=my_tool_handler,
        category="custom"
    ))
```

### Step 3: Wire it up in cli.py

```python
from coco.tools.my_provider import register as register_my_tools
register_my_tools(registry, config, dependencies)
```

That's it. The tool will automatically appear in Claude's available tools and route execution through the registry.

## Historical Context: The Three-Part System

The original monolithic `cocoa.py` used a fragile three-part approach:

1. **Tool definitions** (JSON schemas) scattered across 750+ lines
2. **Tool implementations** (Python methods) in the ToolSystem class
3. **Tool handlers** (routing) in a 475-line if/elif chain in `_execute_tool()`

Missing any one of the three parts would cause an "Unknown tool" error. The Twitter integration initially failed because parts 1 and 2 existed but part 3 (routing) was missing.

The `ToolRegistry` pattern eliminates this class of bugs by unifying all three parts into a single `ToolDefinition` registration.

## Automatic Fact Extraction

When a tool executes, the engine's fact extraction system automatically creates persistent facts:

| Tool | Facts Created |
|------|--------------|
| `send_email` | communication + tool_use |
| `create_document` | file + tool_use (+ task if applicable) |
| `post_tweet` | communication + tool_use |
| `create_calendar_event` | appointment + tool_use |
| `search_web` | tool_use |
| `generate_image` | tool_use |

This means tool usage creates searchable memory -- "who did I email last week?" works even after the conversation buffer has been summarized.

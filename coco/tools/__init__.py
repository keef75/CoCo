"""
CoCo tools -- unified tool registry, definitions, and provider modules.

The ``ToolRegistry`` replaces the old three-part tool system where every tool
required a JSON schema definition, a method implementation, and a handler
entry in a 475-line if/elif chain.  Now each tool is registered in one place.

Provider modules
----------------
Each provider module exposes a ``register(registry, config, dependencies)``
function that registers its tools:

- ``filesystem``      -- read_file, write_file, navigate_directory, search_patterns, explore_directory
- ``web``             -- search_web, extract_urls, crawl_domain
- ``code_execution``  -- run_code, execute_bash
- ``email``           -- send_email, check_emails, check_sent_emails, get_todays_emails, read_email_content
- ``twitter``         -- post_tweet, get_twitter_mentions, reply_to_tweet, search_twitter, create_twitter_thread
- ``calendar``        -- read_calendar, read_todays_calendar, add_calendar_event, create_calendar_event

Quick start
-----------
::

    from coco.tools.registry import ToolRegistry, ToolDefinition
    from coco.tools import filesystem, web, code_execution, email, twitter, calendar

    registry = ToolRegistry()
    deps = {"workspace": Path("coco_workspace"), "deployment_dir": Path(".")}

    filesystem.register(registry, config, deps)
    web.register(registry, config, deps)
    code_execution.register(registry, config, deps)
    email.register(registry, config, {**deps, "gmail": gmail_instance})
    twitter.register(registry, config, {"twitter": twitter_instance})
    calendar.register(registry, config, {})

    # Get API definitions for Claude
    tool_defs = registry.get_api_definitions()

    # Execute a tool call
    result = registry.execute("read_file", {"path": "README.md"})
"""

from .registry import ToolDefinition, ToolRegistry

__all__ = [
    "ToolDefinition",
    "ToolRegistry",
]

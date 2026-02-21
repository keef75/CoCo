"""
Central tool registry that replaces CoCo's three-part tool system.

The old architecture required three separate, scattered pieces per tool:
  1. JSON schema definition (for the Claude API)
  2. Implementation method (in ToolSystem)
  3. Handler routing (in a 475-line if/elif chain inside _execute_tool)

ToolRegistry unifies all three into a single registration point.

A tool provider module calls ``registry.register(ToolDefinition(...))`` once,
supplying the schema *and* the handler callable.  The registry then:
  - exposes ``get_api_definitions()`` for the Claude API (only tools whose
    handler is not None)
  - routes ``execute(name, input)`` to the correct handler
  - tracks which tools are available vs. unavailable (missing API key, etc.)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ToolDefinition:
    """Single registration point for a tool -- unifies definition, implementation, and handler.

    Parameters
    ----------
    name:
        Unique tool name (e.g. ``"read_file"``).
    description:
        Human-readable description sent to the Claude API.
    input_schema:
        JSON Schema ``dict`` describing accepted parameters.
    handler:
        Callable that executes the tool.  If ``None`` the tool is treated as
        *unavailable* (e.g. missing API key) and will **not** appear in the
        API definitions list.
    category:
        Logical grouping used for introspection and logging.
    """

    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None
    category: str = "general"


class ToolRegistry:
    """Central registry that replaces the three-part tool system.

    Implements the ``ToolRegistryProtocol`` from ``coco.interfaces``.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool.

        If *handler* is ``None`` the tool is recorded but excluded from
        ``get_api_definitions()`` and will return a friendly error from
        ``execute()``.
        """
        self._tools[tool.name] = tool

    # ------------------------------------------------------------------
    # API surface
    # ------------------------------------------------------------------

    def get_api_definitions(self) -> List[Dict[str, Any]]:
        """Return JSON tool definitions for the Claude API.

        Only tools whose handler is not ``None`` are included -- this
        prevents Claude from trying to call tools that cannot run.
        """
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in self._tools.values()
            if t.handler is not None
        ]

    def execute(self, name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool by *name*.

        Raises ``KeyError`` when the tool was never registered.
        Returns a user-friendly message when the tool exists but has no
        handler (i.e. it is unavailable due to missing configuration).
        """
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")

        tool = self._tools[name]

        if tool.handler is None:
            return f"Tool '{name}' is not available (missing configuration)"

        return tool.handler(**tool_input)

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def list_tools(self) -> List[str]:
        """Return names of **all** registered tools (available or not)."""
        return list(self._tools.keys())

    def available_tools(self) -> List[str]:
        """Return names of tools that have a working handler."""
        return [name for name, t in self._tools.items() if t.handler is not None]

    def unavailable_tools(self) -> List[str]:
        """Return names of tools registered without a handler."""
        return [name for name, t in self._tools.items() if t.handler is None]

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Look up a single tool by name, or ``None`` if not registered."""
        return self._tools.get(name)

    def get_tools_by_category(self, category: str) -> List[ToolDefinition]:
        """Return all tools belonging to *category*."""
        return [t for t in self._tools.values() if t.category == category]

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __repr__(self) -> str:
        available = len(self.available_tools())
        total = len(self._tools)
        return f"<ToolRegistry {available}/{total} tools available>"

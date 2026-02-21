"""
Simplified tool executor using the ToolRegistry.

Replaces the old 475-line if/elif chain in ``cocoa.py._execute_tool()``
(lines ~12486-12960) with a clean dispatch through the central registry.

Responsibilities
----------------
* Route tool calls through ``ToolRegistry.execute()``
* Trigger fact extraction after successful tool execution
* Format results consistently (always return a ``str``)
* Handle errors with user-friendly messages and structured logging
"""

from __future__ import annotations

import json
import logging
import traceback
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Maximum length for a tool result before it gets truncated.
# Prevents context-window overflow when a tool returns huge output.
_MAX_RESULT_LENGTH = 50_000

# Truncation suffix appended when a result is clipped.
_TRUNCATION_NOTICE = (
    "\n\n[Result truncated -- original output exceeded "
    f"{_MAX_RESULT_LENGTH:,} characters]"
)


class ToolExecutor:
    """Executes tools via the registry, replacing the old if/elif chain.

    Parameters
    ----------
    registry:
        A ``ToolRegistry`` instance that owns all tool definitions and
        handlers.
    engine:
        Optional reference to the engine (or any object that exposes
        ``extract_facts_from_tool_use(tool_name, tool_input, result)``).
        When provided, every successful execution triggers fact extraction
        so that actions persist even after the conversation buffer clears.
    console:
        Optional Rich console for user-facing status messages.  When
        ``None`` messages are logged instead.
    """

    def __init__(
        self,
        registry: Any,
        engine: Any = None,
        console: Any = None,
    ) -> None:
        self.registry = registry
        self.engine = engine
        self.console = console

    # ------------------------------------------------------------------
    # Primary entry point
    # ------------------------------------------------------------------

    def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool by name and return a string result.

        The method performs four steps:

        1. **Dispatch** the call through the registry.
        2. **Format** the raw return value into a string.
        3. **Extract facts** (if an engine with fact extraction is wired up).
        4. **Truncate** the result if it exceeds the safety limit.

        Returns
        -------
        str
            Always a string -- either the tool's output, a friendly error
            message, or a formatted JSON representation.
        """
        logger.debug("Executing tool: %s", tool_name)

        try:
            raw_result = self.registry.execute(tool_name, tool_input)
        except KeyError:
            msg = f"Unknown tool: {tool_name}"
            logger.warning(msg)
            return msg
        except TypeError as exc:
            # Common when the handler signature doesn't match tool_input keys.
            msg = (
                f"Tool parameter error ({tool_name}): {exc}\n"
                f"Received keys: {list(tool_input.keys())}"
            )
            logger.error(msg)
            return msg
        except Exception as exc:
            msg = f"Tool execution error ({tool_name}): {exc}"
            logger.error(msg, exc_info=True)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(traceback.format_exc())
            return msg

        # ---- Format ----
        result_str = self._format_result(raw_result)

        # ---- Fact extraction ----
        self._try_fact_extraction(tool_name, tool_input, result_str)

        # ---- Truncate if needed ----
        if len(result_str) > _MAX_RESULT_LENGTH:
            logger.info(
                "Truncating %s result from %d to %d chars",
                tool_name,
                len(result_str),
                _MAX_RESULT_LENGTH,
            )
            result_str = result_str[:_MAX_RESULT_LENGTH] + _TRUNCATION_NOTICE

        return result_str

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def available_tools(self):
        """Return names of tools that have a working handler."""
        return self.registry.available_tools()

    def list_tools(self):
        """Return names of all registered tools."""
        return self.registry.list_tools()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_result(raw: Any) -> str:
        """Coerce a tool's raw return value into a string.

        * ``str`` -- returned as-is.
        * ``dict`` / ``list`` -- serialised as indented JSON.
        * ``None`` -- returns a confirmation message.
        * Everything else -- ``str(raw)``.
        """
        if isinstance(raw, str):
            return raw

        if raw is None:
            return "Tool executed successfully (no output)."

        if isinstance(raw, (dict, list)):
            try:
                return json.dumps(raw, indent=2, default=str, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(raw)

        return str(raw)

    def _try_fact_extraction(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        result: str,
    ) -> None:
        """Trigger fact extraction on the engine if available.

        Fact extraction failure NEVER breaks tool execution -- we catch
        all exceptions and log them at WARNING level.
        """
        if self.engine is None:
            return

        extractor = getattr(self.engine, "extract_facts_from_tool_use", None)
        if extractor is None:
            return

        try:
            extractor(tool_name, tool_input, result)
        except Exception as exc:
            logger.warning(
                "Fact extraction failed for %s: %s", tool_name, exc
            )

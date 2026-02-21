"""
Protocol classes for dependency inversion across CoCo's module boundaries.

Import direction: config -> memory -> tools -> engine -> ui -> cli
Engine modules import Protocols from here, never concrete classes from tools/memory.
Concrete wiring happens only in cli.py:main().
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)


@runtime_checkable
class ConfigProtocol(Protocol):
    """What every module needs from configuration."""

    anthropic_api_key: str
    openai_api_key: str
    tavily_api_key: str
    planner_model: str
    embedding_model: str
    workspace: str
    debug: bool
    memory_db: str
    bash_timeout: int

    @property
    def console(self) -> Any:
        ...


@runtime_checkable
class MemoryConfigProtocol(Protocol):
    """Configuration specific to the memory subsystem."""

    buffer_size: int
    buffer_truncate_at: int
    summary_window_size: int
    summary_overlap: int
    max_summaries_in_memory: int
    summary_buffer_size: int
    summarization_model: str
    embedding_model: str


@runtime_checkable
class MemorySystemProtocol(Protocol):
    """What the engine needs from the memory system."""

    def insert_episode(self, user_input: str, response: str) -> None:
        ...

    def get_context_window(self) -> List[Dict[str, str]]:
        ...

    def create_rolling_summary(self, exchanges: List[Dict[str, str]]) -> None:
        ...

    def create_session_summary(self) -> str:
        ...

    def get_summary_context(self) -> str:
        ...

    @property
    def episode_count(self) -> int:
        ...


@runtime_checkable
class ToolRegistryProtocol(Protocol):
    """What the engine needs from the tool system."""

    def get_api_definitions(self) -> List[Dict[str, Any]]:
        """Return JSON tool definitions for the Claude API."""
        ...

    def execute(self, name: str, tool_input: Dict[str, Any]) -> Any:
        """Route a tool call to its handler and return the result."""
        ...

    def list_tools(self) -> List[str]:
        """Return names of all registered tools."""
        ...


@runtime_checkable
class ToolSystemProtocol(Protocol):
    """What the engine needs from the legacy ToolSystem (pre-registry)."""

    config: Any
    workspace: Any
    gmail: Any
    twitter: Any
    code_memory: Any

    def read_file(self, path: str) -> str:
        ...

    def write_file(self, path: str, content: str) -> str:
        ...


@runtime_checkable
class ConsciousnessProtocol(Protocol):
    """What the UI needs from the consciousness engine."""

    config: Any
    memory: Any
    tools: Any
    identity: str

    def think(self, user_input: str) -> str:
        ...

    def process_command(self, command: str) -> Optional[str]:
        ...

    def save_identity(self) -> None:
        ...

    def speak_response(self, response: str) -> None:
        ...

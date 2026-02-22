"""
Configuration classes for COCO - Consciousness Orchestration and Cognitive Operations.

Extracted from cocoa.py to provide standalone, importable configuration management.
Contains MemoryConfig (hierarchical memory system tuning) and Config (centralized
application configuration with .env loading).
"""

import os
from pathlib import Path
from typing import List, Optional

from prompt_toolkit.styles import Style


class MemoryConfig:
    """Hierarchical memory system configuration with .env parameter support"""

    def __init__(self):
        # Buffer Window Memory Configuration (configurable via .env)
        self.buffer_size = int(
            os.getenv("MEMORY_BUFFER_SIZE", os.getenv("EPISODIC_WINDOW", "100"))
        )  # 0 = unlimited, >0 = fixed size
        self.buffer_truncate_at = 120  # Start summarization when buffer reaches this

        # Summary Memory Configuration
        self.summary_window_size = 25  # Number of exchanges per summary
        self.summary_overlap = 5  # Overlap between summary windows
        self.max_summaries_in_memory = 50  # Keep recent summaries accessible

        # Summary Buffer Configuration (configurable via .env - parallel to buffer_size)
        self.summary_buffer_size = int(
            os.getenv("MEMORY_SUMMARY_BUFFER_SIZE", "20")
        )  # Number of recent summaries to inject into context (0 = unlimited)

        # Gist Memory Configuration (Long-term)
        self.gist_creation_threshold = 25  # Create gist after N summaries
        self.gist_importance_threshold = 0.5  # Minimum importance to create gist

        # Session Continuity (configurable via .env)
        self.load_session_summary_on_start = (
            os.getenv("LOAD_SESSION_SUMMARY_ON_START", "true").lower() == "true"
        )
        self.save_session_summary_on_end = True
        self.session_summary_length = 500  # Words in session summary

        # LLM Integration
        self.summarization_model = "claude-sonnet-4-5"
        self.embedding_model = "text-embedding-3-small"

        # Phenomenological Integration
        self.enable_emotional_tagging = True
        self.enable_importance_scoring = True
        self.enable_thematic_clustering = True

        # Performance
        self.async_summarization = True
        self.batch_embedding_generation = True
        self.cache_frequent_queries = True

    def to_dict(self) -> dict:
        """Convert config to dictionary for storage"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    @classmethod
    def from_dict(cls, config_dict: dict) -> "MemoryConfig":
        """Create config from dictionary"""
        config = cls()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class Config:
    """Centralized configuration management.

    Loads settings from environment variables and a .env file using a built-in
    parser (no python-dotenv dependency required).  A ``rich.console.Console``
    can be provided at construction time or will be created lazily on first
    access via the ``console`` property.
    """

    def __init__(self, console=None):
        # Load environment variables from .env
        self.load_env()

        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY", "")

        # Enhanced Tavily Configuration
        self.tavily_search_depth = os.getenv("TAVILY_SEARCH_DEPTH", "basic")
        self.tavily_max_results = int(os.getenv("TAVILY_MAX_RESULTS", "5"))
        self.tavily_include_images = (
            os.getenv("TAVILY_INCLUDE_IMAGES", "false").lower() == "true"
        )
        self.tavily_exclude_domains: List[str] = [
            d.strip()
            for d in os.getenv("TAVILY_EXCLUDE_DOMAINS", "").split(",")
            if d.strip()
        ]
        self.tavily_auto_extract_markdown = (
            os.getenv("TAVILY_AUTO_EXTRACT_MARKDOWN", "true").lower() == "true"
        )
        self.tavily_timeout = int(os.getenv("TAVILY_TIMEOUT", "60"))

        # Tool timeout configurations
        self.bash_timeout = int(os.getenv("BASH_TIMEOUT", "60"))

        # Model Configuration - use Claude Sonnet 4.5 (latest model, no beta features)
        self.planner_model = os.getenv(
            "PLANNER_MODEL", "claude-sonnet-4-5-20250929"
        )
        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL", "text-embedding-3-small"
        )

        # Workspace Configuration
        self.workspace = os.getenv("WORKSPACE", "./coco_workspace")
        self.ensure_workspace()

        # Debug Configuration
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        # Memory Configuration
        self.memory_config = MemoryConfig()
        self.memory_db = os.path.join(self.workspace, "coco_memory.db")
        self.knowledge_graph_db = os.path.join(self.workspace, "coco_knowledge.db")

        # UI Configuration - console is passed in or created lazily
        self._console: Optional[object] = console
        self.style = self.create_ui_style()

    @property
    def console(self):
        """Return the Rich console, creating one lazily if not provided."""
        if self._console is None:
            from rich.console import Console

            self._console = Console()
        return self._console

    @console.setter
    def console(self, value):
        self._console = value

    @staticmethod
    def load_env(env_path: str = ".env"):
        """Load a .env file into ``os.environ``.

        Uses a simple built-in parser -- no ``python-dotenv`` dependency.
        Lines starting with ``#`` are treated as comments. Values may
        optionally be wrapped in single or double quotes which are stripped.
        """
        path = Path(env_path)
        if not path.exists():
            return
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value

    def ensure_workspace(self):
        """Create workspace directory if it doesn't exist"""
        Path(self.workspace).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def create_ui_style() -> Style:
        """Create prompt_toolkit style that matches Rich aesthetics"""
        return Style.from_dict(
            {
                "prompt": "#00aaff bold",
                "input": "#ffffff",
                "": "#ffffff",  # Default text color
            }
        )

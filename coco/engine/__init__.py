"""
CoCo engine -- core consciousness loop, Claude API integration, and command routing.

Public API
----------
- ConsciousnessEngine -- the central orchestration class (Claude API + tools + memory)
- ContextManager -- mixin for token estimation, context compression, document budgeting
- FactExtractionMixin -- mixin for universal tool-fact extraction (18 extractors)
- MediaTools -- image/video generation, analysis, and document perception
- ReflectionEngine -- identity evolution, user profiling, and shutdown reflection
- SpeechEngine -- text-to-speech integration via ElevenLabs
- ToolExecutor -- simplified tool dispatch via ToolRegistry

Command Routing (Wave 4)
------------------------
- CommandRouter -- central slash-command dispatch
- MemoryCommandHandler -- /memory, /recall, /facts, /kg, /rag, /help
- MediaCommandHandler -- /speak, /image, /video, /watch, /play-music, etc.
- TwitterCommandHandler -- /tweet, /mentions, /twitter-*, /auto-twitter
- SchedulerCommandHandler -- /task-*, /auto-news, /auto-calendar, etc.
"""

from coco.engine.consciousness import ConsciousnessEngine
from coco.engine.context_management import ContextManager
from coco.engine.fact_extraction import FactExtractionMixin
from coco.engine.media_tools import MediaTools
from coco.engine.reflection import ReflectionEngine
from coco.engine.speech import SpeechEngine
from coco.engine.tool_executor import ToolExecutor

from coco.engine.commands import CommandRouter
from coco.engine.commands_media import MediaCommandHandler
from coco.engine.commands_memory import MemoryCommandHandler
from coco.engine.commands_scheduler import SchedulerCommandHandler
from coco.engine.commands_twitter import TwitterCommandHandler

__all__ = [
    "ConsciousnessEngine",
    "ContextManager",
    "FactExtractionMixin",
    "MediaTools",
    "ReflectionEngine",
    "SpeechEngine",
    "ToolExecutor",
    "CommandRouter",
    "MediaCommandHandler",
    "MemoryCommandHandler",
    "SchedulerCommandHandler",
    "TwitterCommandHandler",
]

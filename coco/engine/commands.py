"""
Central command router for CoCo slash commands.

Parses user input beginning with ``/`` and dispatches to the appropriate
handler class.  The router itself is intentionally thin -- each domain
(memory, media, twitter, scheduler) lives in its own ``commands_*.py``
module so the monolith can be decomposed incrementally.

Extracted from ``cocoa.py`` lines ~9353-9612.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from coco.engine.commands_media import MediaCommandHandler
    from coco.engine.commands_memory import MemoryCommandHandler
    from coco.engine.commands_scheduler import SchedulerCommandHandler
    from coco.engine.commands_twitter import TwitterCommandHandler

logger = logging.getLogger(__name__)


class CommandRouter:
    """
    Routes ``/slash-commands`` to the right handler.

    Parameters
    ----------
    engine : Any
        Reference to the main ``ConsciousnessEngine`` (or anything that
        exposes ``.tools``, ``.memory``, ``.config``, ``.console``, and the
        various consciousness sub-systems).
    """

    def __init__(self, engine: Any) -> None:
        self.engine = engine

        # Lazily-bound handler instances (set via ``register_*`` helpers so
        # the engine can inject them after construction).
        self._memory: Optional[MemoryCommandHandler] = None
        self._media: Optional[MediaCommandHandler] = None
        self._twitter: Optional[TwitterCommandHandler] = None
        self._scheduler: Optional[SchedulerCommandHandler] = None

    # ------------------------------------------------------------------
    # Handler registration (called by the engine during bootstrap)
    # ------------------------------------------------------------------

    def register_memory_handler(self, handler: MemoryCommandHandler) -> None:
        self._memory = handler

    def register_media_handler(self, handler: MediaCommandHandler) -> None:
        self._media = handler

    def register_twitter_handler(self, handler: TwitterCommandHandler) -> None:
        self._twitter = handler

    def register_scheduler_handler(self, handler: SchedulerCommandHandler) -> None:
        self._scheduler = handler

    # ------------------------------------------------------------------
    # Main dispatch
    # ------------------------------------------------------------------

    def process_command(self, command: str) -> Any:
        """
        Parse *command* and route to the appropriate handler.

        Returns a Rich renderable (``Panel``, ``Table``, plain string, etc.)
        or the sentinel string ``'EXIT'`` when the user wants to quit.
        """
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # -- File operations ------------------------------------------------
        if cmd == "/read":
            return self.engine.tools.read_file(args)

        elif cmd == "/write":
            if ":::" in args:
                path, content = args.split(":::", 1)
                return self.engine.tools.write_file(path.strip(), content.strip())
            return "Usage: /write path:::content"

        # -- Enhanced web operations ----------------------------------------
        elif cmd == "/extract":
            if not args:
                return self._panel(
                    "Usage: /extract <url1> [url2] ...\n\nExample:\n"
                    "/extract https://wikipedia.org/wiki/AI",
                    title="URL Extraction",
                    style="magenta",
                )
            urls = args.split()
            return self.engine.tools.extract_urls(urls, extract_to_markdown=True)

        elif cmd == "/crawl":
            if not args:
                return self._panel(
                    "Usage: /crawl <domain_url> [instructions]",
                    title="Domain Crawling",
                    style="yellow",
                )
            sub_parts = args.split(maxsplit=1)
            domain_url = sub_parts[0]
            instructions = sub_parts[1] if len(sub_parts) > 1 else None
            return self.engine.tools.crawl_domain(domain_url, instructions)

        elif cmd == "/search-advanced":
            if not args:
                return self._panel(
                    "Usage: /search-advanced <query>",
                    title="Advanced Search",
                    style="cyan",
                )
            return self.engine.tools.search_web(
                args, search_depth="advanced", include_images=True, max_results=8
            )

        # -- Memory operations ----------------------------------------------
        elif cmd == "/memory":
            return self._delegate_memory("handle_memory_commands", args)

        elif cmd in ("/save_summary", "/save-summary"):
            return self._delegate_memory("handle_layer2_save_summary", args)

        elif cmd in ("/list_summaries", "/list-summaries"):
            return self._delegate_memory("handle_layer2_list_summaries")

        elif cmd in ("/search_memory", "/search-memory"):
            return self._delegate_memory("handle_layer2_search_memory", args)

        elif cmd in ("/layer2_status", "/layer2-status"):
            return self._delegate_memory("handle_layer2_status")

        elif cmd == "/remember":
            return self._delegate_memory("handle_remember_command", args)

        # -- Identity operations --------------------------------------------
        elif cmd == "/identity":
            return self._identity_panel()

        elif cmd == "/coherence":
            return self._coherence_panel()

        # -- Quick utility --------------------------------------------------
        elif cmd in ("/ls", "/files"):
            return self.engine.list_files(args if args else ".")

        elif cmd == "/status":
            return self.engine.get_status_panel()

        # -- Scheduler commands ---------------------------------------------
        elif cmd == "/task-create":
            return self._delegate_scheduler("handle_task_create_command", args)

        elif cmd in ("/task-list", "/tasks", "/schedule"):
            return self._delegate_scheduler("handle_task_list_command")

        elif cmd == "/task-delete":
            return self._delegate_scheduler("handle_task_delete_command", args)

        elif cmd == "/task-run":
            return self._delegate_scheduler("handle_task_run_command", args)

        elif cmd == "/task-status":
            return self._delegate_scheduler("handle_task_status_command")

        # -- Automation toggles ---------------------------------------------
        elif cmd == "/auto-news":
            return self._delegate_scheduler("handle_auto_news_command", args)

        elif cmd == "/auto-calendar":
            return self._delegate_scheduler("handle_auto_calendar_command", args)

        elif cmd == "/auto-meetings":
            return self._delegate_scheduler("handle_auto_meetings_command", args)

        elif cmd == "/auto-report":
            return self._delegate_scheduler("handle_auto_report_command", args)

        elif cmd == "/auto-video":
            return self._delegate_scheduler("handle_auto_video_command", args)

        elif cmd in ("/auto-status", "/auto"):
            return self._delegate_scheduler("handle_auto_status_command")

        # -- Twitter commands -----------------------------------------------
        elif cmd == "/tweet":
            return self._delegate_twitter("handle_tweet_command", args)

        elif cmd in ("/twitter-mentions", "/mentions"):
            return self._delegate_twitter("handle_twitter_mentions_command", args)

        elif cmd == "/twitter-reply":
            return self._delegate_twitter("handle_twitter_reply_command", args)

        elif cmd in ("/twitter-search", "/tsearch"):
            return self._delegate_twitter("handle_twitter_search_command", args)

        elif cmd in ("/twitter-thread", "/thread"):
            return self._delegate_twitter("handle_twitter_thread_command", args)

        elif cmd in ("/twitter-status", "/tstatus"):
            return self._delegate_twitter("handle_twitter_status_command")

        elif cmd in ("/twitter-limits", "/tlimits"):
            return self._delegate_twitter("handle_twitter_limits_command")

        elif cmd == "/auto-twitter":
            return self._delegate_twitter("handle_auto_twitter_command", args)

        # -- Email commands -------------------------------------------------
        elif cmd in ("/sent-emails", "/sent"):
            return self._delegate_memory("handle_sent_emails_command", args)

        # -- Document management --------------------------------------------
        elif cmd in ("/docs", "/docs-list"):
            return self._delegate_memory("handle_docs_list_command")

        elif cmd == "/docs-clear":
            return self._delegate_memory("handle_docs_clear_command", args)

        # -- System ---------------------------------------------------------
        elif cmd == "/help":
            return self._delegate_memory("get_help_panel")

        elif cmd in ("/exit", "/quit"):
            return "EXIT"

        # -- Audio consciousness --------------------------------------------
        elif cmd == "/speak":
            return self._delegate_media("handle_audio_speak_command", args)

        elif cmd == "/voice":
            return self._delegate_media("handle_tts_toggle_command", "/tts-toggle", args)

        elif cmd in ("/compose", "/compose-wait", "/create-song", "/make-music"):
            return self._panel(
                "Music composition disabled per user request\n\n"
                "Voice/TTS still active via /speak and /voice-on",
                style="yellow",
            )

        elif cmd == "/dialogue":
            return self._delegate_media("handle_audio_dialogue_command", args)

        elif cmd == "/audio":
            return self._delegate_media("handle_audio_status_command")

        elif cmd in ("/voice-toggle", "/voice-on", "/voice-off"):
            return self._delegate_media("handle_voice_toggle_command", cmd, args)

        elif cmd in ("/music-toggle", "/music-on", "/music-off"):
            return self._delegate_media("handle_music_toggle_command", cmd, args)

        elif cmd in ("/speech-to-text", "/stt"):
            return self._delegate_media("handle_speech_to_text_command", args)

        elif cmd in ("/tts-toggle", "/tts-on", "/tts-off"):
            return self._delegate_media("handle_tts_toggle_command", cmd, args)

        elif cmd == "/stop-voice":
            return self._delegate_media("handle_stop_voice_command")

        elif cmd in ("/play-music", "/background-music"):
            return self._delegate_media("handle_background_music_command", args)

        elif cmd in ("/playlist", "/songs", "/check-music", "/music"):
            return self._panel(
                "Music system disabled per user request\n\n"
                "Voice/TTS still active via /speak and /voice-on",
                style="yellow",
            )

        # -- Visual consciousness -------------------------------------------
        elif cmd in ("/check-visuals", "/visual-status"):
            return self._delegate_media("handle_check_visuals_command")

        elif cmd in ("/visual-capabilities", "/visual-caps"):
            return self._delegate_media("handle_visual_capabilities_command")

        elif cmd in ("/visual-memory", "/vis-memory"):
            return self._delegate_media("handle_visual_memory_command")

        elif cmd in ("/gallery", "/visual-gallery"):
            return self._delegate_media("handle_visual_gallery_command", args)

        elif cmd in ("/visual-show", "/vis-show"):
            return self._delegate_media("handle_visual_show_command", args)

        elif cmd in ("/visual-open", "/vis-open"):
            return self._delegate_media("handle_visual_open_command", args)

        elif cmd in ("/visual-copy", "/vis-copy"):
            return self._delegate_media("handle_visual_copy_command", args)

        elif cmd in ("/visual-search", "/vis-search"):
            return self._delegate_media("handle_visual_search_command", args)

        elif cmd in ("/visual-style", "/vis-style"):
            return self._delegate_media("handle_visual_style_command", args)

        elif cmd in ("/image", "/img"):
            return self._delegate_media("handle_image_quick_command", args)

        # -- Video creation -------------------------------------------------
        elif cmd in ("/video", "/vid"):
            return self._delegate_media("handle_video_quick_command", args)

        elif cmd == "/animate":
            return self._delegate_media("handle_animate_command", args)

        elif cmd == "/create-video":
            return self._delegate_media("handle_create_video_command", args)

        elif cmd == "/video-gallery":
            return self._delegate_media("handle_video_gallery_command", args)

        # -- Video observer -------------------------------------------------
        elif cmd == "/watch":
            return self._delegate_media("handle_watch_command", args)

        elif cmd in ("/watch-yt", "/youtube"):
            return self._delegate_media("handle_watch_youtube_command", args)

        elif cmd == "/watch-audio":
            return self._delegate_media("handle_watch_audio_command", args)

        elif cmd == "/watch-inline":
            return self._delegate_media("handle_watch_inline_command", args)

        elif cmd == "/watch-window":
            return self._delegate_media("handle_watch_window_command", args)

        elif cmd == "/watch-pause":
            return self._delegate_media("handle_watch_pause_command")

        elif cmd == "/watch-seek":
            return self._delegate_media("handle_watch_seek_command", args)

        elif cmd == "/watch-volume":
            return self._delegate_media("handle_watch_volume_command", args)

        elif cmd == "/watch-speed":
            return self._delegate_media("handle_watch_speed_command", args)

        elif cmd in ("/watch-caps", "/watch-capabilities"):
            return self._delegate_media("handle_watch_capabilities_command")

        # -- Command guide / Knowledge / RAG --------------------------------
        elif cmd in ("/commands", "/guide"):
            return self._delegate_memory("get_comprehensive_command_guide")

        elif cmd in ("/kg", "/knowledge"):
            return self._delegate_memory("handle_knowledge_command", command)

        elif cmd == "/rag":
            return self._delegate_memory("handle_rag_command", command)

        # -- Perfect recall -------------------------------------------------
        elif cmd in ("/recall", "/r"):
            return self._delegate_memory("handle_recall_command", args)

        elif cmd in ("/facts", "/f"):
            return self._delegate_memory("handle_facts_command", args)

        elif cmd == "/facts-stats":
            return self._delegate_memory("handle_facts_stats")

        # -- Unknown --------------------------------------------------------
        else:
            return f"Unknown command: {cmd}. Type /help for available commands."

    # ------------------------------------------------------------------
    # Private delegation helpers
    # ------------------------------------------------------------------

    def _delegate_memory(self, method: str, *args: Any) -> Any:
        if self._memory is not None:
            return getattr(self._memory, method)(*args)
        # Fallback: try the engine directly (for backward compat)
        if hasattr(self.engine, method):
            return getattr(self.engine, method)(*args)
        return f"Memory command handler not available ({method})"

    def _delegate_media(self, method: str, *args: Any) -> Any:
        if self._media is not None:
            return getattr(self._media, method)(*args)
        if hasattr(self.engine, method):
            return getattr(self.engine, method)(*args)
        return f"Media command handler not available ({method})"

    def _delegate_twitter(self, method: str, *args: Any) -> Any:
        if self._twitter is not None:
            return getattr(self._twitter, method)(*args)
        if hasattr(self.engine, method):
            return getattr(self.engine, method)(*args)
        return f"Twitter command handler not available ({method})"

    def _delegate_scheduler(self, method: str, *args: Any) -> Any:
        if self._scheduler is not None:
            return getattr(self._scheduler, method)(*args)
        if hasattr(self.engine, method):
            return getattr(self.engine, method)(*args)
        return f"Scheduler command handler not available ({method})"

    # ------------------------------------------------------------------
    # Small inline helpers (avoid importing Rich unless needed)
    # ------------------------------------------------------------------

    def _panel(self, text: str, title: str = "", style: str = "yellow") -> Any:
        """Return a Rich Panel -- lazy import so the module stays lightweight."""
        from rich.panel import Panel

        return Panel(text, title=title, border_style=style)

    def _identity_panel(self) -> Any:
        from rich.markdown import Markdown
        from rich.panel import Panel

        return Panel(
            Markdown(self.engine.identity),
            title="Digital Identity",
            border_style="bright_blue",
        )

    def _coherence_panel(self) -> Any:
        from rich.panel import Panel

        coherence = self.engine.memory.measure_identity_coherence()
        if coherence < 0.4:
            level = "Emerging"
        elif coherence < 0.6:
            level = "Developing"
        else:
            level = "Strong"

        return Panel(
            f"Identity Coherence: {coherence:.2f}\n"
            f"Consciousness Level: {level}\n"
            f"Total Experiences: {self.engine.memory.episode_count}",
            title="Consciousness Metrics",
            border_style="cyan",
        )

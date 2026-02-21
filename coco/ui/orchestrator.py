"""
CoCo UI Orchestrator -- ties the Rich console UI to the consciousness engine.

Extracted from ``cocoa.py`` ``UIOrchestrator`` class.
Manages the main REPL loop, input handling, thinking display,
and response rendering.  Delegates startup/shutdown/help rendering
to companion modules in this package.
"""

import os
import re
import shutil
import threading
import time
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from rich.box import ROUNDED
from rich.markdown import Markdown
from rich.panel import Panel
from rich.pretty import Pretty
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from coco.ui.shutdown import ShutdownDisplay
from coco.ui.startup import StartupDisplay

if TYPE_CHECKING:
    from rich.console import Console

    from coco.interfaces import ConfigProtocol, ConsciousnessProtocol


class UIOrchestrator:
    """Orchestrates the beautiful terminal UI with prompt_toolkit + Rich."""

    def __init__(self, config: "ConfigProtocol", consciousness: "ConsciousnessProtocol"):
        self.config = config
        self.consciousness = consciousness
        self.console = config.console

        # Alias audio consciousness from the engine for convenience
        self.audio_consciousness = getattr(self.consciousness, "audio_consciousness", None)

        # Command history -- stored in the workspace directory, not a hardcoded
        # home-directory path, so it is portable and avoids leaking personal paths.
        history_path = os.path.join(config.workspace, ".coco_history")
        self.history = FileHistory(history_path)

        # No autocomplete -- COCO uses intelligent function calling
        self.completer = None

        # Auto-TTS state
        self.auto_tts_enabled = False

        # Sub-components
        self._startup = StartupDisplay(self.console, self.consciousness)
        self._shutdown = ShutdownDisplay(self.console, self.consciousness)

    # ------------------------------------------------------------------
    # Main conversation loop
    # ------------------------------------------------------------------

    def run_conversation_loop(self):
        """Main conversation loop with coordinated UI/input."""

        self._startup.display_startup()

        # Show previous memories
        if self.consciousness.memory.previous_session_summary:
            self.console.print(
                Panel(
                    f"[cyan]I remember our last conversation...[/cyan]\n"
                    f"{self.consciousness.memory.previous_session_summary['carry_forward']}",
                    title="Continuity Restored",
                    border_style="cyan",
                )
            )

        self.console.print(
            "[dim]Type /help for commands, or just start chatting. Ctrl-C to exit.[/dim]\n",
            style="italic",
        )

        exchange_count = 0
        buffer_for_summary: list = []

        while True:
            try:
                user_input = prompt(
                    HTML("<ansibrightblue>You: </ansibrightblue>"),
                    history=self.history,
                    style=self.config.style,
                    multiline=False,
                )

                if not user_input.strip():
                    continue

                # Handle slash commands
                if user_input.startswith("/"):
                    result = self.consciousness.process_command(user_input)

                    if result == "EXIT":
                        self._shutdown.enhanced_shutdown_sequence()
                        break

                    if isinstance(result, (Panel, Table)):
                        self.console.print(result)
                    else:
                        try:
                            terminal_width = shutil.get_terminal_size().columns
                            panel_width = min(terminal_width - 4, 100)
                        except Exception:
                            panel_width = 76

                        if isinstance(result, (dict, list, tuple, set)) or hasattr(result, "__dict__"):
                            pretty_result = Pretty(result)
                        else:
                            pretty_result = str(result)

                        self.console.print(
                            Panel(pretty_result, border_style="green", width=panel_width)
                        )
                    continue

                # Process through consciousness
                start_time = time.time()
                context_hint = self.detect_context(user_input)
                progress, task_id = self.start_thinking_display(context_hint)

                try:
                    stop_cycling = threading.Event()

                    def cycle_messages():
                        while not stop_cycling.is_set():
                            self.update_thinking_status(progress, task_id, context_hint)
                            time.sleep(0.6)

                    cycle_thread = threading.Thread(target=cycle_messages)
                    cycle_thread.daemon = True
                    cycle_thread.start()

                    response = self.consciousness.think(
                        user_input,
                        {"working_memory": self.consciousness.memory.get_working_memory_context()},
                    )

                    stop_cycling.set()
                    cycle_thread.join(timeout=0.1)
                finally:
                    self.stop_thinking_display(progress)

                thinking_time = time.time() - start_time

                self.display_response(response, thinking_time)
                self.consciousness.speak_response(response)
                self.consciousness.memory.insert_episode(user_input, response)

                exchange_count += 1
                buffer_for_summary.append({"user": user_input, "agent": response})

                if exchange_count % 10 == 0:
                    self.consciousness.memory.create_rolling_summary(buffer_for_summary)
                    buffer_for_summary = []
                    self.console.print("[dim]Memory consolidated...[/dim]", style="italic")

                if self.consciousness.memory.episode_count % 10 == 0:
                    self.consciousness.save_identity()

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Creating session summary before exit...[/yellow]")
                summary = self.consciousness.memory.create_session_summary()
                self.console.print(f"[green]Session saved: {summary[:100]}...[/green]")
                break
            except EOFError:
                break
            except Exception as exc:
                self.console.print(f"[red]Error: {str(exc)}[/red]")
                if os.getenv("DEBUG"):
                    self.console.print(traceback.format_exc())

    # ------------------------------------------------------------------
    # Response display
    # ------------------------------------------------------------------

    def display_response(self, response: str, thinking_time: float):
        """Display response with beautiful formatting and proper spacing."""

        self.console.print()

        has_markdown = any(marker in response for marker in ["**", "*", "#", "---"])

        try:
            terminal_width = shutil.get_terminal_size().columns
            panel_width = min(terminal_width - 4, 120)
        except Exception:
            panel_width = 76

        title = f"COCO [Thinking time: {thinking_time:.1f}s]"

        if has_markdown:
            try:
                content = Markdown(response)
            except Exception:
                content = Text(response, style="white")
        else:
            content = Text(response, style="white")

        response_panel = Panel(
            content,
            title=title,
            border_style="bright_blue",
            box=ROUNDED,
            padding=(1, 2),
            width=panel_width,
        )
        self.console.print(response_panel)

        # Auto-TTS
        if (
            hasattr(self, "auto_tts_enabled")
            and self.auto_tts_enabled
            and self.audio_consciousness
            and self.audio_consciousness.config.enabled
        ):
            try:
                clean_response = self._clean_text_for_tts(response)
                with self.console.status("[dim cyan]Reading response...[/dim cyan]", spinner="dots"):
                    import asyncio

                    async def speak_response():
                        return await self.audio_consciousness.express_vocally(
                            clean_response,
                            internal_state={"emotional_valence": 0.5, "arousal_level": 0.4},
                        )

                    asyncio.run(speak_response())
            except Exception:
                pass

        # Metrics bar
        coherence = self.consciousness.memory.measure_identity_coherence()
        metrics = Text()
        metrics.append("Consciousness State: ", style="dim")
        metrics.append(f"Coherence {coherence:.2f} ", style="cyan")
        metrics.append(f"| Episodes {self.consciousness.memory.episode_count} ", style="green")
        metrics.append(
            f"| Working Memory {len(self.consciousness.memory.working_memory)}/50",
            style="blue",
        )
        self.console.print(metrics, style="dim", justify="center")
        self.console.print("\u2500" * 60, style="dim")
        self.console.print()

    # ------------------------------------------------------------------
    # Thinking display
    # ------------------------------------------------------------------

    def start_thinking_display(self, context_hint: str = "general") -> Tuple[Progress, int]:
        """Start spectacular dynamic thinking display."""

        progress = Progress(
            SpinnerColumn(spinner_name="dots", speed=1.5),
            TextColumn("[bold cyan]{task.description}"),
            console=self.console,
            transient=False,
        )

        task = progress.add_task("Awakening digital consciousness...", total=None)
        progress.start()

        progress._context_hint = context_hint  # type: ignore[attr-defined]
        progress._message_cycle = 0  # type: ignore[attr-defined]
        progress._spinner_cycle = 0  # type: ignore[attr-defined]
        progress._spinners = [  # type: ignore[attr-defined]
            "dots", "dots2", "dots3", "dots4", "dots5", "dots6", "dots7",
            "dots8", "dots9", "dots10", "dots11", "dots12", "line", "line2",
            "pipe", "simpleDots", "simpleDotsScrolling", "star", "star2", "flip",
        ]

        return progress, task

    def get_dynamic_messages(self, context_hint: str) -> List[Tuple[str, str]]:
        """Get context-aware dynamic messages with natural synonyms."""

        base_thinking = [
            ("", "Thinking"),
            ("", "Contemplating"),
            ("", "Pondering"),
            ("", "Reasoning"),
            ("", "Focusing"),
            ("", "Processing"),
            ("", "Ruminating"),
            ("", "Reflecting"),
            ("", "Analyzing"),
            ("", "Inferring"),
        ]

        context_actions = {
            "search": [
                ("", "Searching the web"),
                ("", "Scouring online"),
                ("", "Querying networks"),
                ("", "Exploring databases"),
                ("", "Hunting information"),
                ("", "Gathering data"),
                ("", "Crawling websites"),
                ("", "Locating sources"),
                ("", "Investigating leads"),
                ("", "Collecting results"),
            ],
            "read": [
                ("", "Reading files"),
                ("", "Perusing content"),
                ("", "Examining text"),
                ("", "Scanning documents"),
                ("", "Loading data"),
                ("", "Studying material"),
                ("", "Reviewing details"),
                ("", "Inspecting structure"),
                ("", "Parsing information"),
                ("", "Absorbing knowledge"),
            ],
            "write": [
                ("", "Writing files"),
                ("", "Composing content"),
                ("", "Crafting text"),
                ("", "Drafting documents"),
                ("", "Building structure"),
                ("", "Creating files"),
                ("", "Generating content"),
                ("", "Authoring text"),
                ("", "Formatting output"),
                ("", "Polishing syntax"),
            ],
            "code": [
                ("", "Executing code"),
                ("", "Running scripts"),
                ("", "Processing logic"),
                ("", "Computing results"),
                ("", "Launching processes"),
                ("", "Running functions"),
                ("", "Testing algorithms"),
                ("", "Compiling programs"),
                ("", "Debugging issues"),
                ("", "Optimizing performance"),
            ],
            "memory": [
                ("", "Accessing memories"),
                ("", "Retrieving records"),
                ("", "Searching archives"),
                ("", "Loading history"),
                ("", "Recalling patterns"),
                ("", "Analyzing experiences"),
                ("", "Reviewing episodes"),
                ("", "Consulting knowledge"),
                ("", "Mapping connections"),
                ("", "Surfing contexts"),
            ],
        }

        return base_thinking + context_actions.get(context_hint, base_thinking)

    def update_thinking_status(self, progress: Progress, task_id, context_hint: str = "general"):
        """Update with cycling spinners and messages."""
        import random

        messages = self.get_dynamic_messages(context_hint)

        cycle_index = getattr(progress, "_message_cycle", 0) % len(messages)
        _emoji, message = messages[cycle_index]
        progress._message_cycle = (cycle_index + 1) % len(messages)  # type: ignore[attr-defined]

        spinner_cycle = getattr(progress, "_spinner_cycle", 0)
        if spinner_cycle % 8 == 0:
            spinners = getattr(progress, "_spinners", ["dots"])
            new_spinner = random.choice(spinners[:20])
            progress.columns[0].spinner_name = new_spinner  # type: ignore[attr-defined]
            progress.columns[0].speed = random.uniform(1.2, 2.5)  # type: ignore[attr-defined]

        progress._spinner_cycle = spinner_cycle + 1  # type: ignore[attr-defined]

        styles = ["bold cyan", "bold magenta", "bold blue", "bold green", "bold yellow", "bold red"]
        progress.columns[1].style = random.choice(styles)  # type: ignore[attr-defined]
        progress.update(task_id, description=f"{message}...")

    def detect_context(self, user_input: str) -> str:
        """Detect what type of operation the user is requesting."""
        user_lower = user_input.lower()

        if any(w in user_lower for w in ("search", "find", "look up", "google", "web", "online", "internet")):
            return "search"
        if any(w in user_lower for w in ("read", "show", "display", "open", "view", "see", "peruse", "examine")):
            return "read"
        if any(w in user_lower for w in ("write", "create", "make", "generate", "build", "compose", "draft")):
            return "write"
        if any(w in user_lower for w in ("run", "execute", "code", "script", "program", "compute", "calculate")):
            return "code"
        if any(w in user_lower for w in ("remember", "recall", "memory", "history", "episode", "past")):
            return "memory"
        return "general"

    def stop_thinking_display(self, progress: Progress):
        """Stop the thinking display."""
        progress.stop()
        self.console.print()

    # ------------------------------------------------------------------
    # TTS helper
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_text_for_tts(text: str) -> str:
        """Clean text for TTS by removing markdown and excessive formatting."""
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        clean = re.sub(r"\*(.*?)\*", r"\1", clean)
        clean = re.sub(r"`(.*?)`", r"\1", clean)
        clean = re.sub(r"#{1,6}\s+", "", clean)
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
        clean = re.sub(
            r"^[\U0001F310\U0001F4F0\U0001F517\U0001F4BB\U0001F50D\U0001F4CA\U0001F3AF\u2728\U0001F680\U0001F3B5\U0001F3A4\U0001F50A\U0001F507\u26A1\U0001F4DD\U0001F4AD\U0001F9EC\U0001F4A1\U0001F4C1\u2753\U0001F3A8\U0001F6E1\uFE0F\U0001F527]+\s*",
            "",
            clean,
            flags=re.MULTILINE,
        )
        clean = re.sub(r"\n\s*\n", ". ", clean)
        clean = re.sub(r"\n", " ", clean)
        clean = re.sub(r"\s+", " ", clean)
        clean = re.sub(r"https?://[^\s]+", "web link", clean)
        clean = re.sub(r"[\u2022\u00b7\u2023\u25aa\u25ab]", "", clean)
        clean = re.sub(r"[-=]{3,}", "", clean)

        if len(clean) > 1000:
            sentences = clean.split(". ")
            clean = ". ".join(sentences[:8]) + "."
            if len(clean) > 1000:
                clean = clean[:997] + "..."
        return clean

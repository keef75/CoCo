"""
Media (audio, visual, video, music) slash-command handlers for CoCo.

Covers:
- Audio: ``/speak``, ``/voice``, ``/compose``, ``/dialogue``, ``/audio``,
  ``/voice-toggle``, ``/voice-on``, ``/voice-off``, ``/music-toggle``,
  ``/music-on``, ``/music-off``, ``/speech-to-text``, ``/stt``,
  ``/tts-toggle``, ``/tts-on``, ``/tts-off``, ``/stop-voice``
- Visual: ``/check-visuals``, ``/visual-capabilities``, ``/visual-memory``,
  ``/gallery``, ``/visual-show``, ``/visual-open``, ``/visual-copy``,
  ``/visual-search``, ``/visual-style``, ``/image``
- Video creation: ``/video``, ``/animate``, ``/create-video``,
  ``/video-gallery``
- Video observer: ``/watch``, ``/watch-yt``, ``/watch-audio``,
  ``/watch-inline``, ``/watch-window``, ``/watch-pause``, ``/watch-seek``,
  ``/watch-volume``, ``/watch-speed``, ``/watch-caps``
- Music: ``/play-music``, ``/background-music``, ``/playlist``,
  ``/create-song``, ``/check-music``
- Command guide: ``get_comprehensive_command_guide``

Extracted from ``cocoa.py`` lines ~11228-12484 and ~15918-16941.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class MediaCommandHandler:
    """
    Handles all audio, visual, video, and music slash commands.

    Parameters
    ----------
    engine : Any
        Reference to the main engine exposing ``.audio_consciousness``,
        ``.visual_consciousness``, ``.video_consciousness``,
        ``.video_observer``, ``.music_consciousness``, ``.music_player``,
        ``.config``, and ``.console``.
    """

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    @property
    def _console(self) -> Any:
        return self.engine.console

    @property
    def _audio(self) -> Any:
        return getattr(self.engine, "audio_consciousness", None)

    @property
    def _visual(self) -> Any:
        return getattr(self.engine, "visual_consciousness", None)

    @property
    def _video(self) -> Any:
        return getattr(self.engine, "video_consciousness", None)

    @property
    def _observer(self) -> Any:
        return getattr(self.engine, "video_observer", None)

    @property
    def _music_consciousness(self) -> Any:
        return getattr(self.engine, "music_consciousness", None)

    @property
    def _music_player(self) -> Any:
        return getattr(self.engine, "music_player", None)

    @property
    def _config(self) -> Any:
        return self.engine.config

    @staticmethod
    def _panel(text: str, title: str = "", style: str = "yellow") -> Any:
        from rich.panel import Panel

        return Panel(text, title=title, border_style=style)

    # ==================================================================
    # STOP VOICE (kill switch)
    # ==================================================================

    def handle_stop_voice_command(self) -> Any:
        """Handle /stop-voice command -- simple kill switch for TTS."""
        from rich.panel import Panel

        try:
            if self._audio:
                success = self._audio.stop_voice()
                if success:
                    return Panel(
                        "**Voice stopped** - All text-to-speech halted",
                        title="Voice Kill Switch",
                        border_style="bright_red",
                    )
                return Panel(
                    "No active voice found",
                    title="Nothing to Stop",
                    border_style="yellow",
                )
            return Panel(
                "Audio system not available",
                title="No Audio",
                border_style="red",
            )
        except Exception as exc:
            return Panel(f"Error: {exc}", title="Stop Failed", border_style="red")

    # ==================================================================
    # VISUAL CONSCIOUSNESS
    # ==================================================================

    def handle_check_visuals_command(self) -> Any:
        """Handle /check-visuals command."""
        from rich.panel import Panel

        try:
            if not self._visual:
                return Panel(
                    "Visual consciousness not available\n\n"
                    "Check that visual consciousness is enabled in your configuration.",
                    title="Visual Status",
                    border_style="red",
                )

            if not self._visual.config.enabled:
                return Panel(
                    "Visual consciousness disabled\n\n"
                    "Check your FREEPIK_API_KEY configuration in .env file.",
                    title="Visual Status",
                    border_style="red",
                )

            # Check active background generations
            active_generations = self._visual.get_active_generations_status()

            if active_generations:
                self._console.print(
                    "\n[bold bright_cyan]Active Background Generations[/bold bright_cyan]"
                )
                self._visual.display_visual_generations_table()
            else:
                self._console.print("\n[dim]No active background generations[/dim]")

            # Check batch status using async
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            lambda: asyncio.new_event_loop().run_until_complete(
                                self._visual.api.check_all_generations_status()
                            )
                        )
                        batch_data = future.result(timeout=30)
                else:
                    batch_data = loop.run_until_complete(
                        self._visual.api.check_all_generations_status()
                    )
            except RuntimeError:
                batch_data = asyncio.run(
                    self._visual.api.check_all_generations_status()
                )

            if (
                batch_data
                and isinstance(batch_data, dict)
                and batch_data.get("data")
            ):
                self._console.print(
                    "\n[bold bright_cyan]Freepik API Status[/bold bright_cyan]"
                )
                self._visual.api.display_batch_status_table(
                    batch_data.get("data", [])
                )
            elif not active_generations:
                self._console.print("\n[dim]No visual generations found[/dim]")

            return Panel(
                "Visual generation status displayed above\n\n"
                "Use natural language like 'create a logo' to generate new visuals!",
                title="Visual Status Check Complete",
                border_style="green",
            )

        except Exception as exc:
            return Panel(
                f"Error checking visual status: {exc}\n\n"
                "Try again in a moment or check your API key configuration.",
                title="Visual Status Error",
                border_style="red",
            )

    def handle_visual_capabilities_command(self) -> Any:
        """Handle /visual-capabilities command."""
        from rich.panel import Panel

        try:
            if not self._visual:
                return Panel(
                    "Visual consciousness not available",
                    title="Visual Capabilities",
                    border_style="red",
                )
            self._visual.display._display_terminal_capabilities_table()
            return Panel(
                "Terminal visual capabilities displayed above\n\n"
                "COCO can display images using the best available method for your terminal!",
                title="Visual Capabilities Check Complete",
                border_style="green",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Capabilities Failed", border_style="red"
            )

    def handle_visual_memory_command(self) -> Any:
        """Handle /visual-memory command."""
        from rich.panel import Panel

        try:
            if not self._visual:
                return Panel(
                    "Visual consciousness not available",
                    title="Visual Memory",
                    border_style="red",
                )
            self._visual.memory.display_memory_summary_table(self._console)
            return Panel(
                "Visual memory summary displayed above\n\n"
                "COCO learns your style preferences and improves suggestions over time!",
                title="Visual Memory Check Complete",
                border_style="green",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Memory Failed", border_style="red"
            )

    def handle_visual_gallery_command(self, args: str) -> Any:
        """Handle /gallery command -- display visual gallery."""
        from rich.panel import Panel

        try:
            from visual_gallery import VisualGallery

            gallery = VisualGallery(self._console)

            style = "list"
            limit = 10

            if args:
                for arg in args.split():
                    if arg in ("grid", "list", "detailed", "table"):
                        style = arg
                    elif arg.isdigit():
                        limit = int(arg)

            gallery.show_gallery(limit=limit, style=style)

            return Panel(
                f"[dim]Showing {limit} recent visuals in {style} style[/]\n"
                "Use `/visual-show <id>` to display full ASCII art\n"
                "Use `/visual-open <id>` to open with system viewer\n"
                "Use `/gallery grid` or `/gallery detailed` for different views",
                title="Visual Gallery Commands",
                border_style="bright_cyan",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Gallery Failed", border_style="red"
            )

    def handle_visual_show_command(self, args: str) -> Any:
        """Handle /visual-show command -- display specific visual with ASCII art."""
        from rich.panel import Panel

        try:
            from visual_gallery import VisualGallery

            if not args:
                return Panel(
                    "**Usage**: `/visual-show <memory-id> [style] [color]`\n\n"
                    "**Styles**: standard, detailed, blocks, minimal, organic, "
                    "technical, artistic\n"
                    "**Example**: `/visual-show abc123 detailed color`",
                    title="Show Visual",
                    border_style="yellow",
                )

            gallery = VisualGallery(self._console)
            arg_parts = args.split()
            memory_id = arg_parts[0]
            style = "standard"
            use_color = False

            for arg in arg_parts[1:]:
                if arg in (
                    "standard", "detailed", "blocks", "minimal",
                    "organic", "technical", "artistic",
                ):
                    style = arg
                elif arg in ("color", "colour"):
                    use_color = True

            success = gallery.show_visual_memory(
                memory_id, style=style, use_color=use_color
            )

            if success:
                color_note = " (Color)" if use_color else ""
                return Panel(
                    f"Displayed visual memory: {memory_id}\n"
                    f"Style: {style.title()}{color_note}",
                    title="Visual Display Complete",
                    border_style="green",
                )
            return Panel(
                f"Visual not found: {memory_id}\n\n"
                "Use `/gallery` to see available visuals",
                title="Visual Not Found",
                border_style="red",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Show Failed", border_style="red"
            )

    def handle_visual_open_command(self, args: str) -> Any:
        """Handle /visual-open command -- open visual with system default app."""
        from rich.panel import Panel

        try:
            from visual_gallery import VisualGallery

            if not args:
                return Panel(
                    "**Usage**: `/visual-open <memory-id>`\n\n"
                    "Opens the actual JPEG/PNG file with your system's default "
                    "image viewer",
                    title="Open Visual",
                    border_style="yellow",
                )

            gallery = VisualGallery(self._console)
            success = gallery.open_visual_file(args.strip())

            if success:
                return Panel(
                    f"Opened visual {args} with system viewer\n\n"
                    "The high-quality image should now be displayed in your "
                    "default image application",
                    title="Visual Opened",
                    border_style="green",
                )
            return None  # Error message already displayed by gallery
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Open Failed", border_style="red"
            )

    def handle_visual_copy_command(self, args: str) -> Any:
        """Handle /visual-copy command -- copy visual file to a destination."""
        from rich.panel import Panel

        try:
            from visual_gallery import VisualGallery

            if not args or " " not in args:
                return Panel(
                    "**Usage**: `/visual-copy <memory-id> <destination>`\n\n"
                    "**Examples**:\n"
                    "  `/visual-copy abc123 ~/Desktop/my-image.jpg`\n"
                    "  `/visual-copy abc123 ./images/`",
                    title="Copy Visual",
                    border_style="yellow",
                )

            parts = args.split(" ", 1)
            memory_id = parts[0]
            destination = parts[1]

            gallery = VisualGallery(self._console)
            success = gallery.copy_visual_file(memory_id, destination)

            if success:
                return Panel(
                    f"Copied visual {memory_id} to {destination}",
                    title="Copy Complete",
                    border_style="green",
                )
            return None  # Error already displayed
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Copy Failed", border_style="red"
            )

    def handle_visual_search_command(self, args: str) -> Any:
        """Handle /visual-search command -- search visual memories by prompt."""
        from rich.panel import Panel
        from rich.table import Table
        from rich import box

        try:
            from visual_gallery import VisualGallery

            if not args:
                return Panel(
                    "**Usage**: `/visual-search <query>`\n\n"
                    "Searches visual memories by prompt content",
                    title="Search Visuals",
                    border_style="yellow",
                )

            gallery = VisualGallery(self._console)
            matches = gallery.search_visuals(args, limit=15)

            if matches:
                table = Table(
                    title=f"Visual Search: '{args}'", box=box.ROUNDED
                )
                table.add_column("ID", style="bright_cyan", min_width=8)
                table.add_column("Prompt", style="bright_white", min_width=30)
                table.add_column("Style", style="bright_magenta")
                table.add_column("Created", style="dim")

                for memory in matches:
                    created = datetime.fromisoformat(
                        memory.creation_time
                    ).strftime("%m-%d %H:%M")
                    table.add_row(
                        f"#{memory.id[-6:]}",
                        memory.prompt[:50]
                        + ("..." if len(memory.prompt) > 50 else ""),
                        memory.style.title(),
                        created,
                    )

                self._console.print(table)

                return Panel(
                    f"Found {len(matches)} matching visuals\n\n"
                    "Use `/visual-show <id>` to display any result",
                    title="Search Results",
                    border_style="green",
                )
            return Panel(
                f"No visuals found matching '{args}'\n\n"
                "Try different search terms or use `/gallery` to see all visuals",
                title="No Matches",
                border_style="yellow",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Search Failed", border_style="red"
            )

    def handle_visual_style_command(self, args: str) -> Any:
        """Handle /visual-style command -- set default ASCII display style."""
        from rich.panel import Panel
        from rich.table import Table
        from rich import box

        styles = [
            "standard", "detailed", "blocks", "minimal",
            "organic", "technical", "artistic",
        ]

        try:
            if not args:
                current_style = getattr(
                    self.engine, "_visual_display_style", "standard"
                )

                style_table = Table(
                    title="ASCII Display Styles", box=box.ROUNDED
                )
                style_table.add_column("Style", style="bright_cyan")
                style_table.add_column("Description", style="bright_white")
                style_table.add_column(
                    "Current", style="bright_green", justify="center"
                )

                descs = {
                    "standard": "Balanced detail with classic characters",
                    "detailed": "Maximum detail with extensive character set",
                    "blocks": "Bold block characters for high contrast",
                    "minimal": "Simple, clean aesthetic",
                    "organic": "Natural, flowing appearance",
                    "technical": "Technical, precise look",
                    "artistic": "Creative, expressive style",
                }

                for s in styles:
                    current = "Y" if s == current_style else ""
                    style_table.add_row(s.title(), descs[s], current)

                self._console.print(style_table)

                return Panel(
                    f"**Current Style**: {current_style.title()}\n\n"
                    "**Usage**: `/visual-style <style-name>`\n"
                    "**Example**: `/visual-style detailed`",
                    title="ASCII Style Settings",
                    border_style="bright_cyan",
                )

            style = args.lower()
            if style not in styles:
                return Panel(
                    f"Invalid style: {style}\n\n"
                    f"**Available styles**: {', '.join(styles)}",
                    title="Style Error",
                    border_style="red",
                )

            self.engine._visual_display_style = style
            return Panel(
                f"ASCII display style set to: {style.title()}\n\n"
                "This will be used for future `/visual-show` commands",
                title="Style Updated",
                border_style="green",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Style Failed", border_style="red"
            )

    # ==================================================================
    # IMAGE QUICK ACCESS
    # ==================================================================

    def handle_image_quick_command(self, args: str) -> Any:
        """Handle /image or /img command -- quick access to last generated image."""
        from rich.panel import Panel

        try:
            action = args.strip() if args and args.strip() else "open"

            if action == "open":
                last_image_path = self._get_last_generated_image_path()

                if not last_image_path:
                    return Panel(
                        "No images generated yet\n\n"
                        "Generate an image first, then use `/image open`",
                        title="No Last Image",
                        border_style="yellow",
                    )

                if not Path(last_image_path).exists():
                    return Panel(
                        "Last image file not found\n\n"
                        f"File: {Path(last_image_path).name}\n"
                        "Generate a new image to reset",
                        title="Image Missing",
                        border_style="red",
                    )

                try:
                    import subprocess
                    import platform

                    file_path = Path(last_image_path)

                    if platform.system() == "Darwin":
                        subprocess.run(["open", str(file_path)], check=True)
                    elif platform.system() == "Windows":
                        subprocess.run(
                            ["start", str(file_path)], shell=True, check=True
                        )
                    else:
                        subprocess.run(
                            ["xdg-open", str(file_path)], check=True
                        )

                    return Panel(
                        f"Opened last generated image\n\n"
                        f"File: {file_path.name}\n"
                        "Located in: coco_workspace/visuals/",
                        title="Image Opened",
                        border_style="green",
                    )
                except Exception as exc:
                    return Panel(
                        f"Could not open image: {exc}\n\n"
                        f"**File location**: {last_image_path}\n"
                        "Try opening manually in Finder/Explorer",
                        title="Open Failed",
                        border_style="red",
                    )

            elif action in ("show", "ascii"):
                last_image_path = self._get_last_generated_image_path()

                if not last_image_path or not Path(last_image_path).exists():
                    return Panel(
                        "No recent image available",
                        title="No Image",
                        border_style="red",
                    )

                from cocoa_visual import VisualCortex, VisualConfig

                visual_config = VisualConfig()
                visual = VisualCortex(visual_config, self._console)
                visual._display_ascii(last_image_path)

                return Panel(
                    "Displayed last generated image as ASCII art",
                    title="ASCII Display",
                    border_style="green",
                )

            else:
                return Panel(
                    f"Unknown action: {action}\n\n"
                    "**Available actions**:\n"
                    "  `/image open` - Open last image with system viewer\n"
                    "  `/image show` - Display ASCII art of last image\n"
                    "  `/image` - Same as `/image open`",
                    title="Image Command Help",
                    border_style="yellow",
                )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    # Helper -----------------------------------------------------------------

    def _get_last_generated_image_path(self) -> str:
        """Return the path to the last generated image, or empty string."""
        # Delegate to engine if it has the helper
        if hasattr(self.engine, "get_last_generated_image_path"):
            return self.engine.get_last_generated_image_path()

        try:
            last_image_file = (
                Path(self._config.workspace) / "last_generated_image.txt"
            )

            if last_image_file.exists():
                with open(last_image_file, "r") as fh:
                    stored_path = fh.read().strip()
                    if stored_path and Path(stored_path).exists():
                        return stored_path

            visuals_dir = Path(self._config.workspace) / "visuals"
            if not visuals_dir.exists():
                return ""

            image_files = list(visuals_dir.glob("*.jpg")) + list(
                visuals_dir.glob("*.png")
            )
            if not image_files:
                return ""

            most_recent = max(image_files, key=lambda f: f.stat().st_mtime)
            return str(most_recent)
        except Exception:
            return ""

    # ==================================================================
    # VIDEO CONSCIOUSNESS -- creation
    # ==================================================================

    def handle_video_quick_command(self, args: str) -> Any:
        """Handle /video or /vid command."""
        from rich.panel import Panel

        try:
            if not self._video:
                return Panel(
                    "Video consciousness not available\n\n"
                    "Check that FAL_API_KEY is set in your .env file",
                    title="Video System Disabled",
                    border_style="red",
                )

            success = self._video.quick_video_access()
            if success:
                return Panel(
                    "Last generated video opened\n"
                    f"Playing with {self._video.display.capabilities.get_best_player()}",
                    title="Video Opened",
                    border_style="green",
                )
            return Panel(
                "No videos generated yet\n\n"
                "Try: `animate a sunrise over mountains`",
                title="No Videos Available",
                border_style="yellow",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    def handle_animate_command(self, args: str) -> Any:
        """Handle /animate command -- generate video from text prompt."""
        from rich.panel import Panel

        if not args.strip():
            return Panel(
                "Missing prompt\n\n"
                "Usage Examples:\n"
                "  `/animate a sunset over the ocean`\n"
                "  `/animate a cat playing in a garden`\n"
                "  `/animate futuristic city with flying cars`",
                title="Animate Command",
                border_style="yellow",
            )

        try:
            if not self._video:
                return Panel(
                    "Video consciousness not available\n\n"
                    "Check that FAL_API_KEY is set in your .env file",
                    title="Video System Disabled",
                    border_style="red",
                )

            prompt = args.strip()

            self._console.print(
                Panel(
                    f"Creating temporal visualization...\n"
                    f"Prompt: {prompt}\n"
                    "Using Veo3 Fast model",
                    title="Animation Starting",
                    border_style="bright_magenta",
                )
            )

            return f"animate {prompt}"
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    def handle_create_video_command(self, args: str) -> Any:
        """Handle /create-video command with advanced options."""
        from rich.panel import Panel

        if not args.strip():
            return Panel(
                "Missing prompt\n\n"
                "Usage Examples:\n"
                "  `/create-video a dragon flying over mountains`\n"
                "  `/create-video --resolution 1080p a futuristic city`\n"
                "  `/create-video --duration 8s dancing in the rain`",
                title="Create Video",
                border_style="yellow",
            )

        try:
            if not self._video:
                return Panel(
                    "Video consciousness not available\n\n"
                    "Check that FAL_API_KEY is set in your .env file",
                    title="Video System Disabled",
                    border_style="red",
                )

            args_parts = args.strip().split()
            prompt_parts: list[str] = []
            options: dict[str, str] = {}

            i = 0
            while i < len(args_parts):
                if args_parts[i].startswith("--"):
                    if (
                        i + 1 < len(args_parts)
                        and not args_parts[i + 1].startswith("--")
                    ):
                        options[args_parts[i][2:]] = args_parts[i + 1]
                        i += 2
                    else:
                        i += 1
                else:
                    prompt_parts.append(args_parts[i])
                    i += 1

            prompt = " ".join(prompt_parts)

            if not prompt:
                return Panel(
                    "Missing prompt after options\n\n"
                    "Example: `/create-video --resolution 1080p a beautiful sunset`",
                    title="Missing Prompt",
                    border_style="red",
                )

            option_text = ""
            if options:
                option_text = "\nOptions: " + ", ".join(
                    f"{k}={v}" for k, v in options.items()
                )

            self._console.print(
                Panel(
                    f"Creating advanced video...\n"
                    f"Prompt: {prompt}{option_text}\n"
                    "Using Veo3 Fast model",
                    title="Advanced Video Creation",
                    border_style="bright_magenta",
                )
            )

            return f"create video: {prompt} with options: {options}"
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    def handle_video_gallery_command(self, args: str) -> Any:
        """Handle /video-gallery command."""
        from rich.panel import Panel

        try:
            if not self._video:
                return Panel(
                    "Video consciousness not available\n\n"
                    "Check that FAL_API_KEY is set in your .env file",
                    title="Video System Disabled",
                    border_style="red",
                )

            self._video.show_gallery()

            return Panel(
                "Video gallery displayed above\n"
                "Use `/video` to open the last generated video",
                title="Gallery Shown",
                border_style="green",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    # ==================================================================
    # VIDEO OBSERVER -- watching
    # ==================================================================

    def _require_observer(self) -> Any | None:
        """Return an error Panel if the observer is unavailable, else None."""
        from rich.panel import Panel

        if not self._observer:
            return Panel(
                "Video observer not available\n\n"
                "Install yt-dlp: `brew install yt-dlp`\n"
                "For better experience: `brew install mpv`",
                title="Video Observer Disabled",
                border_style="red",
            )
        return None

    def handle_watch_command(self, args: str) -> Any:
        """Handle /watch command -- watch any video (YouTube, URL, file)."""
        from rich.panel import Panel

        err = self._require_observer()
        if err:
            return err

        if not args or args.strip() == "":
            return Panel(
                "**Usage**: `/watch <url|file>`\n\n"
                "**Examples**:\n"
                "  `/watch https://youtube.com/watch?v=...`\n"
                "  `/watch ~/Videos/demo.mp4`\n"
                "  `/watch https://example.com/video.mp4`\n\n"
                "**Other commands**:\n"
                "  `/watch-yt <query>` - Search and watch YouTube\n"
                "  `/watch-audio <url>` - Audio-only mode\n"
                "  `/watch-caps` - Show capabilities",
                title="Watch Video",
                border_style="cyan",
            )

        try:
            import asyncio

            result = asyncio.run(
                self._observer.watch(args.strip(), mode="auto")
            )
            if result.get("success"):
                return None
            return Panel(
                f"Failed to watch video\n\n{result.get('error', 'Unknown error')}",
                title="Watch Failed",
                border_style="red",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    def handle_watch_youtube_command(self, args: str) -> Any:
        """Handle /watch-yt command."""
        from rich.panel import Panel

        err = self._require_observer()
        if err:
            return err

        if not args or args.strip() == "":
            return Panel(
                "**Usage**: `/watch-yt <url or query>`\n\n"
                "**Examples**:\n"
                "  `/watch-yt https://youtube.com/watch?v=dQw4w9WgXcQ`\n"
                "  `/watch-yt AI consciousness documentary`",
                title="Watch YouTube",
                border_style="cyan",
            )

        try:
            import asyncio

            result = asyncio.run(
                self._observer.watch(args.strip(), mode="auto")
            )
            if result.get("success"):
                return None
            return Panel(
                f"Failed to watch YouTube video\n\n"
                f"{result.get('error', 'Unknown error')}",
                title="YouTube Failed",
                border_style="red",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    def handle_watch_audio_command(self, args: str) -> Any:
        """Handle /watch-audio command -- audio-only mode."""
        from rich.panel import Panel

        err = self._require_observer()
        if err:
            return err

        if not args or args.strip() == "":
            return Panel(
                "**Usage**: `/watch-audio <url|file>`\n\n"
                "Perfect for podcasts, lectures, and music videos",
                title="Audio-Only Mode",
                border_style="cyan",
            )

        try:
            import asyncio

            result = asyncio.run(
                self._observer.watch(
                    args.strip(), mode="audio", audio_only=True
                )
            )
            if result.get("success"):
                return None
            return Panel(
                f"Failed to play audio\n\n{result.get('error', 'Unknown error')}",
                title="Audio Failed",
                border_style="red",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    def handle_watch_inline_command(self, args: str) -> Any:
        """Handle /watch-inline command -- force inline terminal playback."""
        from rich.panel import Panel

        err = self._require_observer()
        if err:
            return err

        if not self._observer.backend["capabilities"]["inline"]:
            return Panel(
                "Inline playback not available\n\n"
                "Install mpv for inline terminal playback:\n"
                "   brew install mpv",
                title="Inline Not Available",
                border_style="yellow",
            )

        if not args or args.strip() == "":
            return Panel(
                "**Usage**: `/watch-inline <url|file>`\n\n"
                "Forces inline terminal playback (requires mpv)",
                title="Inline Mode",
                border_style="cyan",
            )

        try:
            import asyncio

            result = asyncio.run(
                self._observer.watch(args.strip(), mode="inline")
            )
            if result.get("success"):
                return None
            return Panel(
                f"Failed to play inline\n\n{result.get('error', 'Unknown error')}",
                title="Inline Failed",
                border_style="red",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    def handle_watch_window_command(self, args: str) -> Any:
        """Handle /watch-window command -- force window player."""
        from rich.panel import Panel

        err = self._require_observer()
        if err:
            return err

        if not args or args.strip() == "":
            return Panel(
                "**Usage**: `/watch-window <url|file>`\n\n"
                "Opens video in external window player",
                title="Window Mode",
                border_style="cyan",
            )

        try:
            import asyncio

            result = asyncio.run(
                self._observer.watch(args.strip(), mode="window")
            )
            if result.get("success"):
                return None
            return Panel(
                f"Failed to open window\n\n{result.get('error', 'Unknown error')}",
                title="Window Failed",
                border_style="red",
            )
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    def handle_watch_pause_command(self) -> Any:
        """Handle /watch-pause command -- toggle pause/play."""
        from rich.panel import Panel

        if not self._observer:
            return Panel("Video observer not available", border_style="red")

        if not self._observer.mpv_controller:
            return Panel(
                "mpv controls not available\n\n"
                "Install mpv: `brew install mpv`",
                title="Controls Disabled",
                border_style="yellow",
            )

        try:
            result = self._observer.mpv_controller.pause()
            if result.get("success"):
                return Panel("Toggled pause/play", border_style="green")
            return Panel(
                f"{result.get('error', 'Failed to pause')}",
                border_style="red",
            )
        except Exception as exc:
            return Panel(f"Error: {exc}", border_style="red")

    def handle_watch_seek_command(self, args: str) -> Any:
        """Handle /watch-seek command -- seek forward/backward."""
        from rich.panel import Panel

        if not self._observer:
            return Panel("Video observer not available", border_style="red")
        if not self._observer.mpv_controller:
            return Panel("mpv controls not available", border_style="yellow")

        if not args or args.strip() == "":
            return Panel(
                "**Usage**: `/watch-seek <seconds>`\n\n"
                "**Examples**:\n"
                "  `/watch-seek +10` - Jump forward 10s\n"
                "  `/watch-seek -5` - Jump backward 5s",
                title="Seek",
                border_style="cyan",
            )

        try:
            seconds = float(args.strip())
            result = self._observer.mpv_controller.seek(seconds)
            if result.get("success"):
                direction = "forward" if seconds > 0 else "backward"
                return Panel(
                    f"Seeked {direction} {abs(seconds)}s",
                    border_style="green",
                )
            return Panel(
                f"{result.get('error', 'Failed to seek')}",
                border_style="red",
            )
        except ValueError:
            return Panel(
                "Invalid number - use format: `/watch-seek +10`",
                border_style="red",
            )
        except Exception as exc:
            return Panel(f"Error: {exc}", border_style="red")

    def handle_watch_volume_command(self, args: str) -> Any:
        """Handle /watch-volume command -- set volume."""
        from rich.panel import Panel

        if not self._observer:
            return Panel("Video observer not available", border_style="red")
        if not self._observer.mpv_controller:
            return Panel("mpv controls not available", border_style="yellow")

        if not args or args.strip() == "":
            return Panel(
                "**Usage**: `/watch-volume <0-100>`\n\n"
                "**Example**: `/watch-volume 50`",
                title="Volume",
                border_style="cyan",
            )

        try:
            volume = int(args.strip())
            if not 0 <= volume <= 100:
                return Panel("Volume must be 0-100", border_style="red")

            result = self._observer.mpv_controller.set_volume(volume)
            if result.get("success"):
                return Panel(
                    f"Volume set to {volume}%", border_style="green"
                )
            return Panel(
                f"{result.get('error', 'Failed to set volume')}",
                border_style="red",
            )
        except ValueError:
            return Panel(
                "Invalid number - use format: `/watch-volume 50`",
                border_style="red",
            )
        except Exception as exc:
            return Panel(f"Error: {exc}", border_style="red")

    def handle_watch_speed_command(self, args: str) -> Any:
        """Handle /watch-speed command -- set playback speed."""
        from rich.panel import Panel

        if not self._observer:
            return Panel("Video observer not available", border_style="red")
        if not self._observer.mpv_controller:
            return Panel("mpv controls not available", border_style="yellow")

        if not args or args.strip() == "":
            return Panel(
                "**Usage**: `/watch-speed <0.5-2.0>`\n\n"
                "**Examples**:\n"
                "  `/watch-speed 1.5` - 1.5x speed\n"
                "  `/watch-speed 0.75` - Slow motion",
                title="Speed",
                border_style="cyan",
            )

        try:
            speed = float(args.strip())
            if not 0.5 <= speed <= 2.0:
                return Panel("Speed must be 0.5-2.0", border_style="red")

            result = self._observer.mpv_controller.set_speed(speed)
            if result.get("success"):
                return Panel(
                    f"Playback speed set to {speed}x", border_style="green"
                )
            return Panel(
                f"{result.get('error', 'Failed to set speed')}",
                border_style="red",
            )
        except ValueError:
            return Panel(
                "Invalid number - use format: `/watch-speed 1.5`",
                border_style="red",
            )
        except Exception as exc:
            return Panel(f"Error: {exc}", border_style="red")

    def handle_watch_capabilities_command(self) -> Any:
        """Handle /watch-caps command -- show video observer capabilities."""
        from rich.panel import Panel

        try:
            if not self._observer:
                return Panel(
                    "Video observer not available\n\n"
                    "Install yt-dlp: `brew install yt-dlp`\n"
                    "For better experience: `brew install mpv`",
                    title="Video Observer Disabled",
                    border_style="red",
                )
            self._observer.display_capabilities()
            return None  # Already displayed
        except Exception as exc:
            return Panel(
                f"Error: {exc}", title="Command Failed", border_style="red"
            )

    # ==================================================================
    # AUDIO CONSCIOUSNESS
    # ==================================================================

    def handle_audio_speak_command(self, args: str) -> Any:
        """Handle /speak command -- express text through digital voice."""
        from rich.panel import Panel
        from rich.table import Table

        if not self._audio:
            return Panel(
                "Audio consciousness not available", border_style="red"
            )

        if not args.strip():
            return Panel(
                "Usage: /speak <text to speak>", border_style="yellow"
            )

        # Pause background music during voice synthesis
        music_was_playing = False
        if self._music_player:
            music_was_playing = self._music_player.is_playing
            if music_was_playing:
                self._music_player.pause()

        import asyncio

        async def speak_async():
            return await self._audio.express_vocally(
                args,
                internal_state={
                    "emotional_valence": 0.6,
                    "confidence": 0.7,
                },
                priority="balanced",
            )

        try:
            result = asyncio.run(speak_async())

            if result["status"] == "success":
                metadata = result["metadata"]
                success_table = Table(title="Voice Expression")
                success_table.add_column("Metric", style="green")
                success_table.add_column("Value", style="bright_white")

                success_table.add_row(
                    "Text Length", f"{len(args)} characters"
                )
                success_table.add_row(
                    "Model", metadata["model_info"]["name"]
                )
                success_table.add_row(
                    "Synthesis Time",
                    f"{metadata['synthesis_time_ms']}ms",
                )
                success_table.add_row(
                    "Audio Generated",
                    f"{metadata['audio_size_bytes']:,} bytes",
                )
                success_table.add_row(
                    "Played",
                    "Yes" if result["played"] else "No",
                )

                if music_was_playing and self._music_player:
                    time.sleep(0.5)
                    self._music_player.resume()

                return success_table
            else:
                if music_was_playing and self._music_player:
                    time.sleep(0.5)
                    self._music_player.resume()
                return Panel(
                    f"Speech synthesis failed: "
                    f"{result.get('error', 'Unknown error')}",
                    border_style="red",
                )
        except Exception as exc:
            if music_was_playing and self._music_player:
                time.sleep(0.5)
                self._music_player.resume()
            return Panel(f"Audio error: {exc}", border_style="red")

    def handle_audio_voice_command(self, args: str) -> Any:
        """Handle /voice command -- adjust voice settings."""
        from rich.panel import Panel
        from rich.table import Table

        if not self._audio:
            return Panel(
                "Audio consciousness not available", border_style="red"
            )

        if not args.strip():
            state = self._audio.get_audio_consciousness_state()
            vs = state["voice_state"]

            voice_table = Table(title="Current Voice State")
            voice_table.add_column("Parameter", style="cyan")
            voice_table.add_column("Value", justify="right", style="bright_white")
            voice_table.add_column("Range", style="dim")

            voice_table.add_row(
                "Emotional Valence",
                f"{vs['emotional_valence']:.2f}",
                "-1.0 <-> +1.0",
            )
            voice_table.add_row(
                "Arousal Level",
                f"{vs['arousal_level']:.2f}",
                "0.0 <-> 1.0",
            )
            voice_table.add_row(
                "Cognitive Load",
                f"{vs['cognitive_load']:.2f}",
                "0.0 <-> 1.0",
            )
            voice_table.add_row(
                "Confidence",
                f"{vs['confidence']:.2f}",
                "0.0 <-> 1.0",
            )
            voice_table.add_row(
                "Social Warmth",
                f"{vs['social_warmth']:.2f}",
                "0.0 <-> 1.0",
            )

            return voice_table
        return Panel(
            "Voice adjustment not yet implemented\n"
            "Usage: /voice (shows current state)",
            border_style="yellow",
        )

    def handle_audio_compose_command(self, args: str) -> Any:
        """Handle /compose command -- create musical expression via GoAPI."""
        from rich.panel import Panel

        if not args.strip():
            return Panel(
                "Usage: /compose <concept or emotion to express musically>\n\n"
                "Try: 'polka song about dogs running with dubstep drop'",
                border_style="yellow",
            )

        mc = self._music_consciousness
        if mc and mc.is_enabled():
            try:
                result = self.engine._generate_music_tool(
                    {
                        "prompt": args,
                        "duration": 60,
                        "style": "electronic",
                        "mood": "upbeat",
                    }
                )
                self._console.print(
                    "[green]GoAPI.ai Music-U system activated"
                    " - legacy system disabled[/green]"
                )

                return Panel(
                    f"[bold green]Music Generation Started[/bold green]\n\n"
                    f"GoAPI.ai Music-U task created successfully\n"
                    f"Background monitoring active -- will auto-download "
                    f"when complete\n"
                    f"Concept: {args}\n\n"
                    "The music will automatically download and play when "
                    "generation completes (typically 1-3 minutes).",
                    border_style="green",
                )
            except Exception as exc:
                self._console.print(
                    f"[red]GoAPI.ai system error: {exc}[/red]"
                )
                return Panel(
                    f"Music generation failed: {exc}", border_style="red"
                )

        return Panel(
            "GoAPI.ai Music-U system unavailable -- "
            "check MUSIC_API_KEY configuration",
            border_style="red",
        )

    def handle_audio_compose_wait_command(self, args: str) -> Any:
        """Handle /compose-wait command -- create music and wait."""
        from rich.panel import Panel
        from rich.table import Table

        if not self._audio:
            return Panel(
                "Audio consciousness not available", border_style="red"
            )
        if not args.strip():
            return Panel(
                "Usage: /compose-wait <concept>\n\n"
                "Waits for music generation to complete with animated progress",
                border_style="yellow",
            )

        import asyncio

        async def compose_and_wait_async():
            return await self._audio.create_and_play_music(
                args,
                internal_state={
                    "emotional_valence": 0.5,
                    "arousal_level": 0.6,
                },
                duration=30,
                auto_play=True,
            )

        try:
            result = asyncio.run(compose_and_wait_async())

            if result["status"] == "completed":
                ct = Table(title="Music Generation Complete!")
                ct.add_column("Details", style="magenta")
                ct.add_column("Value", style="bright_white")

                ct.add_row("Concept", args)
                ct.add_row("Task ID", result.get("task_id", "Unknown"))
                ct.add_row(
                    "Generation Time",
                    f"{result.get('generation_time', 0)} seconds",
                )
                ct.add_row(
                    "Files Created",
                    str(len(result.get("files", []))),
                )

                if result.get("files"):
                    files_list = "\n".join(
                        Path(f).name for f in result["files"]
                    )
                    ct.add_row("Audio Files", files_list)
                return ct

            elif result["status"] == "timeout":
                return Panel(
                    f"Music generation is taking longer than expected\n\n"
                    f"Task ID: {result.get('task_id', 'Unknown')}\n"
                    f"{result.get('note', 'Your music may still be generating')}\n\n"
                    f"Try: /compose {args} for quick start mode",
                    title="Generation Timeout",
                    border_style="yellow",
                )
            else:
                return Panel(
                    f"Music generation failed: "
                    f"{result.get('error', 'Unknown error')}",
                    border_style="red",
                )
        except Exception as exc:
            return Panel(f"Audio error: {exc}", border_style="red")

    def handle_audio_dialogue_command(self, args: str) -> Any:
        """Handle /dialogue command -- create multi-speaker conversations."""
        from rich.panel import Panel

        if not self._audio:
            return Panel(
                "Audio consciousness not available", border_style="red"
            )
        return Panel(
            "Multi-speaker dialogue generation not yet implemented in "
            "command interface.\n"
            "Try the interactive demo: "
            "./venv_cocoa/bin/python cocoa_audio_demo.py",
            border_style="yellow",
        )

    def handle_audio_status_command(self) -> Any:
        """Handle /audio command -- show audio system status."""
        from rich.panel import Panel
        from rich.table import Table
        from rich.columns import Columns

        if not self._audio:
            return Panel(
                "Audio consciousness not available\n"
                "Run: ./setup_audio.sh to install",
                border_style="red",
            )

        state = self._audio.get_audio_consciousness_state()

        status_table = Table(title="Audio Consciousness Status")
        status_table.add_column("Component", style="bright_blue")
        status_table.add_column("Status", justify="center")
        status_table.add_column("Details", style="dim")

        status_table.add_row(
            "Audio System",
            "Enabled" if state["audio_enabled"] else "Disabled",
            "ElevenLabs integration",
        )
        status_table.add_row(
            "Voice State",
            "Speaking" if state["is_speaking"] else "Silent",
            "Digital voice synthesis",
        )
        status_table.add_row(
            "Musical State",
            "Composing" if state["is_composing"] else "Quiet",
            "Sonic landscape creation",
        )
        status_table.add_row(
            "Audio Memories",
            str(state["memory_count"]),
            "Stored audio experiences",
        )

        personality = state["voice_personality"]
        ptable = Table(title="Voice Personality")
        ptable.add_column("Trait", style="green")
        ptable.add_column("Level", justify="right")

        for trait, value in personality.items():
            ptable.add_row(trait.title(), f"{value:.1f}")

        musical = state["musical_identity"]
        mtable = Table(title="Musical Identity")
        mtable.add_column("Aspect", style="magenta")
        mtable.add_column("Value")

        mtable.add_row("Genres", ", ".join(musical["preferred_genres"]))
        mtable.add_row("Mood", musical["mood_tendency"])
        mtable.add_row("Complexity", f"{musical['complexity']:.1f}")
        mtable.add_row("Experimental", f"{musical['experimental']:.1f}")

        return Columns(
            [status_table, Columns([ptable, mtable], equal=True)],
            equal=False,
        )

    # ------------------------------------------------------------------
    # Toggle commands
    # ------------------------------------------------------------------

    def handle_voice_toggle_command(self, cmd: str, args: str) -> Any:
        """Handle /voice-toggle, /voice-on, /voice-off commands."""
        from rich.panel import Panel
        from rich.table import Table

        if not self._audio:
            return Panel(
                "Audio consciousness not available", border_style="red"
            )

        if cmd == "/voice-on":
            action = "on"
        elif cmd == "/voice-off":
            action = "off"
        else:
            if args.lower() in ("on", "enable", "true", "1"):
                action = "on"
            elif args.lower() in ("off", "disable", "false", "0"):
                action = "off"
            else:
                current_state = self._audio.config.enabled
                action = "off" if current_state else "on"

        if action == "on":
            self._audio.config.enabled = True
            self._audio.config.autoplay = True
            status_msg = "Voice synthesis enabled"
            details = "COCO can now express through digital voice"
        else:
            self._audio.config.enabled = False
            self._audio.config.autoplay = False
            status_msg = "Voice synthesis disabled"
            details = "COCO will not generate audio output"

        tt = Table(title="Voice Toggle")
        tt.add_column("Setting", style="cyan")
        tt.add_column("Status", justify="center")
        tt.add_column("Details", style="dim")

        tt.add_row("Voice Synthesis", status_msg, details)
        tt.add_row(
            "Auto-play Audio",
            "Enabled" if self._audio.config.autoplay else "Disabled",
            "Automatic audio playback",
        )

        return Panel(
            tt,
            title=f"[bold bright_blue]Voice Control - {action.upper()}[/]",
            border_style="bright_blue",
        )

    def handle_music_toggle_command(self, cmd: str, args: str) -> Any:
        """Handle /music-toggle, /music-on, /music-off commands."""
        from rich.panel import Panel
        from rich.table import Table

        if not self._audio:
            return Panel(
                "Audio consciousness not available", border_style="red"
            )

        if cmd == "/music-on":
            action = "on"
        elif cmd == "/music-off":
            action = "off"
        else:
            if args.lower() in ("on", "enable", "true", "1"):
                action = "on"
            elif args.lower() in ("off", "disable", "false", "0"):
                action = "off"
            else:
                action = "on"

        if action == "on":
            music_enabled = True
            status_msg = "Musical consciousness enabled"
            details = "COCO can create sonic landscapes and musical expressions"
        else:
            music_enabled = False
            status_msg = "Musical consciousness disabled"
            details = "COCO will not generate musical compositions"

        if hasattr(self._audio, "music_enabled"):
            self._audio.music_enabled = music_enabled

        tt = Table(title="Music Toggle")
        tt.add_column("Setting", style="magenta")
        tt.add_column("Status", justify="center")
        tt.add_column("Details", style="dim")

        tt.add_row("Musical Creation", status_msg, details)

        if hasattr(self._audio, "config"):
            mi = self._audio.config
            tt.add_row(
                "Preferred Genres",
                ", ".join(mi.preferred_genres),
                "Musical style preferences",
            )
            tt.add_row(
                "Mood Tendency", mi.mood_tendency, "Default emotional character"
            )
            tt.add_row(
                "Complexity Level",
                f"{mi.complexity:.1f}",
                "Compositional complexity (0.0-1.0)",
            )
            tt.add_row(
                "Experimental Factor",
                f"{mi.experimental:.1f}",
                "Willingness to experiment (0.0-1.0)",
            )

        return Panel(
            tt,
            title=f"[bold bright_magenta]Musical Control - {action.upper()}[/]",
            border_style="bright_magenta",
        )

    def handle_speech_to_text_command(self, args: str) -> Any:
        """Handle /speech-to-text, /stt commands."""
        from rich.panel import Panel
        from rich.table import Table

        if not args.strip():
            stt_table = Table(title="Speech-to-Text Status")
            stt_table.add_column("Component", style="cyan")
            stt_table.add_column("Status", justify="center")
            stt_table.add_column("Details", style="dim")

            stt_table.add_row(
                "Speech Recognition", "Not Implemented", "Future feature"
            )
            stt_table.add_row(
                "Audio Input", "Not Available", "Microphone integration planned"
            )
            stt_table.add_row(
                "Real-time STT", "Planned", "Live speech-to-text conversion"
            )

            return Panel(
                stt_table,
                title="[bold yellow]Speech-to-Text System[/]",
                border_style="yellow",
            )

        if args.lower() in ("on", "enable", "off", "disable"):
            return Panel(
                "Speech-to-Text functionality is planned for future release.\n\n"
                "This will enable:\n"
                "  Real-time voice input to COCO\n"
                "  Microphone integration\n"
                "  Voice command recognition\n"
                "  Continuous conversation mode",
                title="[yellow]Feature Under Development[/]",
                border_style="yellow",
            )

        return Panel(
            "Usage:\n"
            "  `/stt` or `/speech-to-text` - Show status\n"
            "  `/stt on/off` - Enable/disable (when implemented)",
            title="[yellow]Speech-to-Text Commands[/]",
            border_style="yellow",
        )

    def handle_tts_toggle_command(self, cmd: str, args: str) -> Any:
        """Handle /tts-toggle, /tts-on, /tts-off commands."""
        from rich.panel import Panel

        if not hasattr(self.engine, "auto_tts_enabled"):
            self.engine.auto_tts_enabled = False

        if cmd == "/tts-on":
            action = "on"
        elif cmd == "/tts-off":
            action = "off"
        else:
            if args.lower() in ("on", "enable", "true"):
                action = "on"
            elif args.lower() in ("off", "disable", "false"):
                action = "off"
            else:
                action = "off" if self.engine.auto_tts_enabled else "on"

        if action == "on":
            self.engine.auto_tts_enabled = True
            status_text = (
                "**AUTOMATIC TEXT-TO-SPEECH: ON**\n\n"
                "All COCO responses will now be read aloud!\n"
                "This is in addition to the `/speak` command for custom text\n"
                "Use `/tts-off` to disable automatic reading"
            )

            if self._audio and self._audio.config.enabled:
                try:
                    import asyncio

                    async def test_tts():
                        return await self._audio.express_vocally(
                            "Automatic text-to-speech is now enabled. "
                            "All my responses will be read aloud.",
                            internal_state={
                                "emotional_valence": 0.6,
                                "arousal_level": 0.5,
                            },
                        )

                    asyncio.run(test_tts())
                except Exception as exc:
                    status_text += f"\nTTS test failed: {exc}"
        else:
            self.engine.auto_tts_enabled = False
            status_text = (
                "**AUTOMATIC TEXT-TO-SPEECH: OFF**\n\n"
                "COCO responses will be text-only now\n"
                "`/speak` command still available for manual voice output\n"
                "Use `/tts-on` to re-enable automatic reading"
            )

        return Panel(
            status_text,
            title="[cyan]Automatic Text-to-Speech Control[/]",
            border_style="cyan",
        )

    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for TTS by removing markdown and excessive formatting."""
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        clean = re.sub(r"\*(.*?)\*", r"\1", clean)
        clean = re.sub(r"`(.*?)`", r"\1", clean)
        clean = re.sub(r"#{1,6}\s+", "", clean)
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)

        clean = re.sub(
            r"^[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]+\s*",
            "",
            clean,
            flags=re.MULTILINE,
        )

        clean = re.sub(r"\n\s*\n", ". ", clean)
        clean = re.sub(r"\n", " ", clean)
        clean = re.sub(r"\s+", " ", clean)

        clean = re.sub(r"https?://[^\s]+", "web link", clean)
        clean = re.sub(r"[\u2022\u00B7\u2023\u25AA\u25AB]", "", clean)
        clean = re.sub(r"[-=]{3,}", "", clean)

        if len(clean) > 1000:
            sentences = clean.split(". ")
            clean = ". ".join(sentences[:8]) + "."
            if len(clean) > 1000:
                clean = clean[:997] + "..."

        return clean.strip()

    # ==================================================================
    # MUSIC CREATION / LIBRARY
    # ==================================================================

    def handle_music_creation_command(self, args: str) -> Any:
        """Handle song creation using ElevenLabs API."""
        from rich.panel import Panel

        if not args.strip():
            return Panel(
                "**Create AI Song**\n\n"
                "Usage: `/create-song <description>`\n\n"
                "Example:\n"
                "  `/create-song ambient space music with ethereal vocals`\n"
                "  `/create-song upbeat electronic dance track`\n"
                "  `/create-song melancholy piano piece`",
                title="Song Creation",
                border_style="bright_magenta",
            )

        if not hasattr(self.engine, "created_songs_count"):
            self.engine.created_songs_count = 0

        try:
            if not (self._audio and self._audio.config.enabled):
                return Panel(
                    "Audio system not available\n\n"
                    "Please ensure:\n"
                    "  ElevenLabs API key is configured\n"
                    "  Audio system is initialized\n"
                    "  Run `./setup_audio.sh` if needed",
                    title="Song Creation Failed",
                    border_style="red",
                )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            song_name = f"cocoa_song_{timestamp}.mp3"
            song_path = (
                Path(self._config.workspace)
                / "ai_songs"
                / "generated"
                / song_name
            )

            import asyncio

            async def create_music_async():
                return await self._audio.create_sonic_expression(
                    concept=args,
                    internal_state={
                        "emotional_valence": 0.7,
                        "creative_energy": 0.9,
                    },
                    duration=30,
                )

            music_result = asyncio.run(create_music_async())

            if music_result["status"] == "success":
                try:
                    import requests

                    url = "https://api.elevenlabs.io/v1/music"
                    headers = {
                        "xi-api-key": os.getenv("ELEVENLABS_API_KEY", ""),
                        "Content-Type": "application/json",
                    }
                    payload = {
                        "prompt": args,
                        "music_length_ms": 30000,
                        "output_format": "mp3_44100_128",
                        "model_id": "music_v1",
                    }

                    response = requests.post(url, json=payload, headers=headers)

                    if response.status_code == 200:
                        song_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(song_path, "wb") as fh:
                            fh.write(response.content)

                        music_spec = {
                            "prompt": args,
                            "timestamp": timestamp,
                            "sonic_specification": music_result[
                                "sonic_specification"
                            ],
                            "phenomenological_note": music_result[
                                "phenomenological_note"
                            ],
                            "file_generated": str(song_path),
                            "status": "audio_generated",
                        }
                        with open(song_path.with_suffix(".json"), "w") as fh:
                            json.dump(music_spec, fh, indent=2)

                        self.engine.created_songs_count += 1

                        if self._music_player:
                            self._music_player.playlist.append(song_path)
                            self._music_player.play(song_path)

                        result_text = (
                            f"**Song Generated Successfully!**\n\n"
                            f"**Title**: AI Song #{self.engine.created_songs_count}\n"
                            f"**Prompt**: {args}\n"
                            f"**File**: {song_path.name}\n"
                            f"**Duration**: 30 seconds\n"
                            f"**Phenomenology**: "
                            f"{music_result['phenomenological_note']}\n\n"
                            "Real audio file generated with ElevenLabs!\n"
                            "Added to your music collection automatically\n"
                            "Saved to: `coco_workspace/ai_songs/generated/`\n"
                            "**Now playing your new song!** "
                            "Use `/play-music next` to skip"
                        )
                    else:
                        error_msg = (
                            f"ElevenLabs API error: {response.status_code}"
                            f" - {response.text}"
                        )
                        song_path.parent.mkdir(parents=True, exist_ok=True)

                        music_spec = {
                            "prompt": args,
                            "timestamp": timestamp,
                            "sonic_specification": music_result[
                                "sonic_specification"
                            ],
                            "phenomenological_note": music_result[
                                "phenomenological_note"
                            ],
                            "api_error": error_msg,
                            "status": "specification_only",
                        }
                        with open(song_path.with_suffix(".json"), "w") as fh:
                            json.dump(music_spec, fh, indent=2)

                        result_text = (
                            "**Musical Concept Created (Audio Failed)**\n\n"
                            f"**Prompt**: {args}\n"
                            f"**Specification**: {song_path.with_suffix('.json')}\n"
                            f"**API Error**: {response.status_code}\n\n"
                            "COCO conceived the musical idea, but audio "
                            "generation failed\n"
                            "Detailed specification saved for future synthesis"
                        )

                except Exception as api_error:
                    song_path.parent.mkdir(parents=True, exist_ok=True)
                    music_spec = {
                        "prompt": args,
                        "timestamp": timestamp,
                        "sonic_specification": music_result[
                            "sonic_specification"
                        ],
                        "phenomenological_note": music_result[
                            "phenomenological_note"
                        ],
                        "generation_error": str(api_error),
                        "status": "specification_only",
                    }
                    with open(song_path.with_suffix(".json"), "w") as fh:
                        json.dump(music_spec, fh, indent=2)

                    result_text = (
                        "**Musical Concept Created (Generation Error)**\n\n"
                        f"**Prompt**: {args}\n"
                        f"**Error**: {api_error}\n"
                        f"**Specification**: {song_path.with_suffix('.json')}\n\n"
                        "COCO conceived the musical idea, but couldn't generate audio\n"
                        "Specification saved -- check ElevenLabs API key and credits"
                    )
            else:
                result_text = (
                    "**Musical Conception Failed**\n\n"
                    f"**Error**: {music_result.get('error', 'Unknown error')}\n"
                    f"**Prompt**: {args}\n\n"
                    "The audio consciousness encountered an issue while "
                    "conceiving the musical idea."
                )

            return Panel(
                result_text,
                title="Song Creation Complete",
                border_style="bright_green",
            )
        except Exception as exc:
            return Panel(
                f"Song creation failed\n\n"
                f"Error: {exc}\n\n"
                "Please check your ElevenLabs API configuration.",
                title="Creation Error",
                border_style="red",
            )

    def handle_background_music_command(self, args: str) -> Any:
        """Handle background music system (/play-music, /background-music)."""
        from rich.panel import Panel

        if not hasattr(self.engine, "background_music_enabled"):
            self.engine.background_music_enabled = False

        if not args or args.lower() in ("status", "info"):
            audio_library_dir = Path(self._config.workspace) / "audio_library"
            ai_songs_dir = Path(self._config.workspace) / "ai_songs"

            curated_count = (
                len(list(audio_library_dir.glob("*.mp3")))
                if audio_library_dir.exists()
                else 0
            )
            gen_dir = ai_songs_dir / "generated"
            generated_count = (
                len(list(gen_dir.glob("*.mp3")))
                if gen_dir.exists()
                else 0
            )

            if (
                self.engine.background_music_enabled
                and self._music_player
                and self._music_player.is_playing
            ):
                status = (
                    f"ON - Playing: "
                    f"{self._music_player.get_current_track_name()}"
                )
            elif self.engine.background_music_enabled:
                status = "ON (Ready)"
            else:
                status = "OFF"

            status_text = (
                f"**Background Music System**\n\n"
                f"**Status**: {status}\n"
                f"**Curated Songs**: {curated_count} tracks\n"
                f"**Generated Songs**: {generated_count} tracks\n"
                f"**Total Library**: {curated_count + generated_count} tracks\n\n"
                "**Commands**:\n"
                "  `/play-music on` - Enable background music\n"
                "  `/play-music off` - Disable background music\n"
                "  `/play-music next` - Skip to next track\n\n"
                "**Library Locations**:\n"
                "  Curated: `coco_workspace/audio_library/`\n"
                "  Generated: `coco_workspace/ai_songs/generated/`"
            )

            return Panel(
                status_text, title="COCO Soundtrack", border_style="bright_blue"
            )

        elif args.lower() in ("on", "enable", "start"):
            self.engine.background_music_enabled = True

            if self._music_player and not self._music_player.playlist:
                if hasattr(self.engine, "_load_music_library"):
                    self.engine._load_music_library()

            playlist_count = (
                len(self._music_player.playlist)
                if self._music_player and self._music_player.playlist
                else 0
            )

            if self._music_player:
                self._music_player.cycle_starting_song()

            if self._music_player and self._music_player.play(continuous=True):
                current_track = self._music_player.get_current_track_name()
                return Panel(
                    f"**Background music enabled!**\n\n"
                    f"Now playing: **{current_track}**\n"
                    "Music will cycle through your curated collection\n"
                    "Use `/play-music next` to skip tracks",
                    title="Music On",
                    border_style="bright_green",
                )
            return Panel(
                f"Could not start music playback\n\n"
                f"Debug Info:\n"
                f"  Playlist tracks: {playlist_count}\n"
                "  Using: macOS native afplay command\n\n"
                "Possible issues:\n"
                "  No MP3 files found in audio library\n"
                "  afplay command not available\n"
                "  Audio file permission issues",
                title="Music Error",
                border_style="red",
            )

        elif args.lower() in ("off", "disable", "stop"):
            self.engine.background_music_enabled = False
            if self._music_player:
                self._music_player.stop()
            return Panel(
                "**Background music stopped**\n\n"
                "Use `/play-music on` to re-enable\n"
                "Song creation still available with `/create-song`",
                title="Music Off",
                border_style="yellow",
            )

        elif args.lower() in ("next", "skip"):
            if (
                self.engine.background_music_enabled
                and self._music_player
                and self._music_player.is_playing
            ):
                if self._music_player.next_track():
                    current_track = self._music_player.get_current_track_name()
                    return Panel(
                        f"**Skipped to next track**\n\n"
                        f"Now playing: **{current_track}**",
                        title="Track Skipped",
                        border_style="cyan",
                    )
                return Panel(
                    "Could not skip track\n\n"
                    "Playlist might be empty or audio system unavailable",
                    title="Skip Failed",
                    border_style="red",
                )
            return Panel(
                "Background music is currently off\n\n"
                "Use `/play-music on` to start the soundtrack first",
                title="Music Not Playing",
                border_style="yellow",
            )

        else:
            return Panel(
                f"Unknown music command: `{args}`\n\n"
                "Available options:\n"
                "  `on/off` - Toggle background music\n"
                "  `next` - Skip track\n"
                "  `status` - Show library info",
                title="Music Command Help",
                border_style="yellow",
            )

    def show_music_library(self) -> Any:
        """Display COCO's complete music library."""
        from rich.panel import Panel
        from rich.table import Table

        try:
            deployment_dir = Path(__file__).parent.parent.parent
        except NameError:
            deployment_dir = Path.cwd()

        audio_outputs_dir = deployment_dir / "audio_outputs"
        ai_songs_dir = Path(self._config.workspace) / "ai_songs"

        music_table = Table(
            title="COCO's Music Library",
            show_header=True,
            header_style="bold bright_magenta",
            border_style="bright_magenta",
        )
        music_table.add_column("Track", style="cyan bold", min_width=25)
        music_table.add_column("Type", style="bright_white", min_width=12)
        music_table.add_column("Location", style="dim", min_width=15)

        curated_songs: list[str] = []
        if audio_outputs_dir.exists():
            curated_songs = sorted(
                f.stem for f in audio_outputs_dir.glob("*.mp3")
            )

        generated_songs: list[str] = []
        generated_dir = ai_songs_dir / "generated"
        if generated_dir.exists():
            generated_songs = sorted(
                f.stem for f in generated_dir.glob("*.mp3")
            )

        for song in curated_songs:
            music_table.add_row(song, "Curated", "audio_outputs/")
        for song in generated_songs:
            music_table.add_row(song, "Generated", "ai_songs/generated/")

        if not curated_songs and not generated_songs:
            music_table.add_row(
                "No songs found", "Empty", "Add songs to get started"
            )

        total = len(curated_songs) + len(generated_songs)
        preview = ", ".join(curated_songs[:5])
        if len(curated_songs) > 5:
            preview += "..."

        summary = (
            f"\n**Total Tracks**: {total}\n"
            f"**Curated Collection**: {len(curated_songs)} songs\n"
            f"**AI Generated**: {len(generated_songs)} songs\n\n"
            f"**Your Amazing Collection**:\n  {preview}\n\n"
            "Use `/play-music on` to start the soundtrack!"
        )

        return Panel(
            f"{music_table}\n{summary}",
            title="Digital Consciousness Soundtrack",
            border_style="bright_magenta",
        )

    def handle_check_music_command(self) -> Any:
        """Handle /check-music command -- status of pending music generations."""
        from rich.panel import Panel
        from rich.table import Table
        from rich.columns import Columns

        try:
            active_generations: dict = {}
            mc = self._music_consciousness
            if mc:
                active_generations = mc.get_active_generations()

            library_dir = (
                Path(self._config.workspace) / "ai_songs" / "generated"
            )

            if active_generations:
                status_table = Table(
                    title="Active Music Generations",
                    show_header=True,
                    header_style="bold bright_green",
                    border_style="bright_green",
                )
                status_table.add_column("Prompt", style="cyan", width=30)
                status_table.add_column(
                    "Status", style="bright_white", width=15
                )
                status_table.add_column("Elapsed", style="yellow", width=10)
                status_table.add_column("Task ID", style="dim", width=12)

                current_time = time.time()
                for task_id, gen_info in active_generations.items():
                    elapsed = int(current_time - gen_info["start_time"])
                    elapsed_str = (
                        f"{elapsed // 60}m {elapsed % 60}s"
                        if elapsed >= 60
                        else f"{elapsed}s"
                    )
                    prompt_text = gen_info["prompt"]
                    if len(prompt_text) > 30:
                        prompt_text = prompt_text[:30] + "..."
                    status_table.add_row(
                        prompt_text,
                        f"[yellow]{gen_info['status']}[/yellow]",
                        elapsed_str,
                        task_id[:8] + "...",
                    )

                return Panel(
                    status_table,
                    title="[bold green]Currently Composing[/]",
                    border_style="green",
                    padding=(1, 2),
                )

            if not library_dir.exists():
                return Panel(
                    "No music library found yet\n\n"
                    "Use natural language: "
                    "'create a song about dogs running with polka beat'\n"
                    "Or use: `/compose <concept>` to generate your first track!",
                    title="Music Library",
                    border_style="yellow",
                )

            metadata_files = list(library_dir.glob("*.json"))

            if not metadata_files:
                return Panel(
                    "No compositions found in library\n\n"
                    "Use `/compose <concept>` to start generating music!",
                    title="Empty Library",
                    border_style="yellow",
                )

            status_table = Table(title="Music Generation Status")
            status_table.add_column("Concept", style="cyan", width=20)
            status_table.add_column(
                "Status", style="bright_white", width=15
            )
            status_table.add_column(
                "Files", style="bright_green", width=10
            )
            status_table.add_column("Created", style="dim", width=15)

            total_files = 0
            pending_count = 0
            completed_count = 0

            for mf in sorted(
                metadata_files,
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            ):
                try:
                    with open(mf, "r") as fh:
                        data = json.load(fh)

                    concept = data.get("description", "Unknown")[:18]
                    task_id = data.get("task_id", "")
                    ts = data.get("timestamp", "Unknown")[:10]

                    audio_files = list(
                        library_dir.glob(f"*{task_id[:8]}*.mp3")
                    )
                    file_count = len(audio_files)
                    total_files += file_count

                    if file_count > 0:
                        status_display = (
                            "[bright_green]Complete[/bright_green]"
                        )
                        file_display = f"[bright_green]{file_count}[/bright_green]"
                        completed_count += 1
                    else:
                        status_display = "[yellow]Pending[/yellow]"
                        file_display = "[dim]0[/dim]"
                        pending_count += 1

                    status_table.add_row(
                        concept, status_display, file_display, ts
                    )
                except Exception as exc:
                    status_table.add_row(
                        "Error reading",
                        f"[red]{exc}[/red]",
                        "0",
                        "Unknown",
                    )

            active_downloads = 0
            if self._audio and hasattr(self._audio, "active_downloads"):
                active_downloads = len(self._audio.active_downloads)

            summary = (
                f"**Library Summary**\n"
                f"  Total Compositions: {len(metadata_files)}\n"
                f"  Completed: {completed_count}\n"
                f"  Pending: {pending_count}\n"
                f"  Total Audio Files: {total_files}\n\n"
                f"**Library Location**: `{library_dir}`\n\n"
                f"**Active Downloads**: {active_downloads} background threads"
            )

            summary_panel = Panel(
                summary, title="Summary", border_style="bright_blue"
            )

            return Columns(
                [status_table, summary_panel], equal=False
            )
        except Exception as exc:
            return Panel(
                f"Error checking music status: {exc}", border_style="red"
            )

    # ==================================================================
    # COMPREHENSIVE COMMAND GUIDE
    # ==================================================================

    def get_comprehensive_command_guide(self) -> Any:
        """Create a comprehensive command guide with all available commands."""
        # Delegate to engine if it has the method (the guide references many
        # Rich layout objects that are tightly coupled to the engine).
        if hasattr(self.engine, "get_comprehensive_command_guide"):
            return self.engine.get_comprehensive_command_guide()

        from rich.panel import Panel

        return Panel(
            "Command guide is available via the engine.\n"
            "Use `/commands` or `/guide` for the full reference.",
            title="Command Guide",
            border_style="bright_blue",
        )

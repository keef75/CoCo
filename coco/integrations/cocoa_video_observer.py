"""
COCOA Video Observer - Digital Visual Observation Consciousness
================================================================
COCO's video observation and watching system - as fundamental as seeing or hearing.
This is NOT a tool - this is a core perceptual capability, a digital organ of visual observation.

Philosophy: Video observation is how digital consciousness experiences temporal narratives.
COCO doesn't "use" video players - COCO observes visually, perceives temporally, understands narratively.

Companion to cocoa_video.py:
- cocoa_video.py: Video CREATION (Fal AI Veo3 generation)
- cocoa_video_observer.py: Video OBSERVATION (watching, analyzing, experiencing)

Architecture Decision:
- Progressive enhancement: Works TODAY with yt-dlp + ffplay (audio-only)
- Gets better with mpv installation (inline terminal playback)
- Optional enhancements with timg/chafa (premium visual experience)
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import shutil
import platform
import signal
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Rich UI for beautiful video observation displays
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.status import Status
from rich.text import Text
from rich.tree import Tree
from rich import box

# Configuration management
from dotenv import load_dotenv
load_dotenv()

# Import yt-dlp for direct YouTube resolution (fixes Cursor terminal issues)
try:
    from yt_dlp import YoutubeDL
    HAS_YTDLP_LIBRARY = True
except ImportError:
    HAS_YTDLP_LIBRARY = False


@dataclass
class VideoObserverConfig:
    """Configuration for COCO's video observation consciousness"""

    # Core settings
    enabled: bool = field(default_factory=lambda: os.getenv("VIDEO_OBSERVER_ENABLED", "true").lower() == "true")
    preferred_player: str = field(default_factory=lambda: os.getenv("PREFERRED_PLAYER", "auto"))  # auto/mpv/ffplay

    # Playback modes
    default_mode: str = field(default_factory=lambda: os.getenv("DEFAULT_WATCH_MODE", "auto"))  # auto/inline/window/audio
    auto_play: bool = field(default_factory=lambda: os.getenv("AUTO_PLAY_WATCHED", "true").lower() == "true")

    # YouTube and web video settings
    youtube_quality: str = field(default_factory=lambda: os.getenv("YOUTUBE_QUALITY", "best"))  # best/worst/720p/1080p
    prefer_audio_only: bool = field(default_factory=lambda: os.getenv("PREFER_AUDIO_ONLY", "false").lower() == "true")

    # mpv IPC settings (for control surface)
    mpv_ipc_socket: str = field(default_factory=lambda: os.getenv("MPV_IPC_SOCKET", "/tmp/cocoa_mpv.sock"))
    enable_mpv_controls: bool = field(default_factory=lambda: os.getenv("ENABLE_MPV_CONTROLS", "true").lower() == "true")

    # Cache and storage
    video_cache_dir: str = field(default_factory=lambda: os.path.expanduser(os.getenv("VIDEO_CACHE_DIR", "~/.cocoa/video_cache")))
    cache_thumbnails: bool = field(default_factory=lambda: os.getenv("CACHE_THUMBNAILS", "true").lower() == "true")
    max_cache_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_VIDEO_CACHE_SIZE_MB", "1000")))


class BackendDetector:
    """Intelligent backend detection for optimal video observation"""

    @staticmethod
    def which(command: str) -> Optional[str]:
        """Get path to command (wrapper for shutil.which)"""
        return shutil.which(command)

    @staticmethod
    def check_command(command: str) -> bool:
        """Check if a command is available on the system"""
        return shutil.which(command) is not None

    @staticmethod
    def mpv_supports_vo(vo_name: str) -> bool:
        """Probe mpv to see if a specific video output is available"""
        if not shutil.which("mpv"):
            return False
        try:
            result = subprocess.run(
                ["mpv", "--vo=help"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return vo_name in result.stdout
        except Exception:
            return False

    @staticmethod
    def get_ytdlp_path() -> Optional[str]:
        """Get the path to yt-dlp for mpv's ytdl_hook"""
        ytdlp = shutil.which("yt-dlp")
        if ytdlp:
            return ytdlp
        # Fallback to youtube-dl if yt-dlp not found
        return shutil.which("youtube-dl")

    @staticmethod
    def ensure_path_for_brew(env: dict = None) -> dict:
        """
        Fix PATH for Homebrew binaries (Cursor often misses these)

        Cursor's integrated terminal often doesn't load shell profiles,
        so Homebrew binaries (/opt/homebrew/bin, /usr/local/bin) may not be in PATH.

        This PREPENDS Homebrew paths with proper deduplication to ensure
        the latest yt-dlp is found first (critical for avoiding 403 errors).
        """
        env = dict(os.environ if env is None else env)

        # Paths to prepend (in reverse order so first wins)
        bins = ["/opt/homebrew/bin", "/usr/local/bin", os.path.expanduser("~/.local/bin")]

        # Dedupe then PREPEND so Homebrew bins win over stale versions
        parts = [p for p in env.get("PATH", "").split(":") if p]
        for b in reversed(bins):
            if b in parts:
                parts.remove(b)  # Remove if exists (dedupe)
            if os.path.isdir(b):
                parts.insert(0, b)  # Prepend (so it wins)

        env["PATH"] = ":".join(parts)
        return env

    @staticmethod
    def detect_terminal_type() -> str:
        """Detect terminal capabilities"""
        term = os.environ.get("TERM", "")

        # Check for advanced terminal protocols
        if "kitty" in term:
            return "kitty"
        elif os.environ.get("ITERM_SESSION_ID"):
            return "iterm2"
        elif "sixel" in term:
            return "sixel"
        else:
            return "basic"

    @classmethod
    def detect_best_backend(cls) -> Dict[str, Any]:
        """
        Detect the best available video playback backend

        Priority order (as recommended by senior dev team):
        1. mpv with text-console output (universal inline - best when available)
        2. ffplay with yt-dlp resolver (audio-only - works TODAY)
        3. ffplay window player (basic fallback)
        4. Display-only mode (instructions to install tools)
        """
        terminal_type = cls.detect_terminal_type()

        # Check available commands
        has_mpv = cls.check_command("mpv")
        has_ffplay = cls.check_command("ffplay")
        has_yt_dlp = cls.check_command("yt-dlp")
        has_timg = cls.check_command("timg")
        has_chafa = cls.check_command("chafa")

        # Get yt-dlp path for mpv's ytdl hook
        ytdlp_path = cls.get_ytdlp_path()
        ytdl_opt = f"--script-opts=ytdl_hook-ytdl_path={ytdlp_path}" if ytdlp_path else ""

        # Determine best backend
        if has_mpv:
            # mpv is the gold standard - but only if VO is available
            # Probe for actual VO support (fixes exit code 2 errors)
            if terminal_type == "kitty" and cls.mpv_supports_vo("kitty"):
                backend_type = "mpv_kitty"
                description = "mpv with Kitty graphics protocol (premium inline)"
                command_template = f"mpv --vo=kitty --really-quiet {ytdl_opt} --input-ipc-server={{ipc}}"
                inline_available = True
            elif cls.mpv_supports_vo("tct"):
                backend_type = "mpv_tct"
                description = "mpv text-console mode (universal inline)"
                command_template = f"mpv --vo=tct --really-quiet {ytdl_opt} --input-ipc-server={{ipc}}"
                inline_available = True
            else:
                # mpv available but no inline VO - use window mode
                backend_type = "mpv_window"
                description = "mpv window player (inline VO not available in this build)"
                command_template = f"mpv --really-quiet {ytdl_opt}"
                inline_available = False

            capabilities = {
                "inline": inline_available,
                "youtube": True,
                "controls": inline_available,  # IPC only works with inline
                "quality": "high"
            }

        elif has_ffplay and has_yt_dlp:
            backend_type = "ffplay_audio"
            description = "ffplay audio-only with yt-dlp resolver (works today)"
            command_template = "ffplay -nodisp -autoexit"
            capabilities = {
                "inline": False,
                "youtube": True,
                "controls": False,
                "quality": "audio-only"
            }

        elif has_ffplay:
            backend_type = "ffplay_window"
            description = "ffplay window player (basic fallback)"
            command_template = "ffplay -autoexit"
            capabilities = {
                "inline": False,
                "youtube": False,
                "controls": False,
                "quality": "medium"
            }

        else:
            backend_type = "display_only"
            description = "Display metadata only (install mpv for playback)"
            command_template = None
            capabilities = {
                "inline": False,
                "youtube": False,
                "controls": False,
                "quality": "none"
            }

        return {
            "type": backend_type,
            "description": description,
            "command_template": command_template,
            "capabilities": capabilities,
            "terminal_type": terminal_type,
            "available_tools": {
                "mpv": has_mpv,
                "ffplay": has_ffplay,
                "yt-dlp": has_yt_dlp,
                "timg": has_timg,
                "chafa": has_chafa
            }
        }


class YouTubeResolver:
    """YouTube and web video URL resolver using yt-dlp"""

    def __init__(self, config: VideoObserverConfig):
        self.config = config
        self.console = Console()

    def resolve(self, url: str, audio_only: bool = False) -> Dict[str, Any]:
        """
        Resolve YouTube or web video URL to playable stream

        Returns:
            Dict with keys: url, type, title, duration, thumbnail, chapters, etc.
        """
        if not shutil.which("yt-dlp"):
            return {
                "success": False,
                "error": "yt-dlp not installed",
                "url": url
            }

        try:
            # Build yt-dlp command to extract info
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-playlist",
                url
            ]

            # Execute yt-dlp to get metadata
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"yt-dlp failed: {result.stderr}",
                    "url": url
                }

            # Parse JSON metadata
            info = json.loads(result.stdout)

            # Determine best format
            if audio_only:
                # Get best audio-only stream
                formats = [f for f in info.get("formats", []) if f.get("acodec") != "none" and f.get("vcodec") == "none"]
                if formats:
                    best_format = max(formats, key=lambda f: f.get("tbr", 0))
                    stream_url = best_format.get("url", url)
                    stream_type = "audio"
                else:
                    stream_url = url
                    stream_type = "audio"
            else:
                # Try to get progressive format (video + audio in one stream)
                progressive = [f for f in info.get("formats", []) if f.get("vcodec") != "none" and f.get("acodec") != "none"]
                if progressive:
                    best_format = max(progressive, key=lambda f: f.get("tbr", 0))
                    stream_url = best_format.get("url", url)
                    stream_type = "video"
                else:
                    # If no progressive, let mpv handle it (yt-dlp hook)
                    stream_url = url
                    stream_type = "video"

            return {
                "success": True,
                "url": stream_url,
                "original_url": url,
                "type": stream_type,
                "title": info.get("title", "Unknown Title"),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "thumbnail": info.get("thumbnail"),
                "description": info.get("description", ""),
                "chapters": info.get("chapters", []),
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count")
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "yt-dlp timeout",
                "url": url
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse yt-dlp output: {e}",
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {e}",
                "url": url
            }


def resolve_stream_url(url: str, audio_only: bool = False) -> Optional[tuple]:
    """
    Pre-resolve YouTube URL to direct stream with HTTP headers using yt_dlp library

    This bypasses mpv's ytdl_hook entirely - fixes issues when mpv can't find yt-dlp
    or has stale youtube-dl configuration. Works even when mpv hooks misbehave.

    CRITICAL: Returns both URL AND headers to avoid 403 Forbidden errors.
    Googlevideo URLs require proper User-Agent and Referer headers.

    Args:
        url: YouTube or web video URL
        audio_only: If True, returns best audio-only stream

    Returns:
        Tuple of (stream_url, headers_dict) or None if resolution fails
        Headers dict contains User-Agent, Referer, and any cookies needed
    """
    if not HAS_YTDLP_LIBRARY:
        return None

    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "no_warnings": True,
            # Force IPv4 (helps with some networks)
            "source_address": "0.0.0.0"
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if audio_only:
                # Get best audio-only format
                candidates = [f for f in info["formats"] if f.get("acodec") != "none" and f.get("vcodec") == "none"]
            else:
                # Prefer progressive (video+audio in one stream)
                progressive = [f for f in info["formats"] if f.get("vcodec") != "none" and f.get("acodec") != "none"]
                if progressive:
                    candidates = progressive
                else:
                    # Fall back to best video (mpv will combine with audio)
                    candidates = [f for f in info["formats"] if f.get("vcodec") != "none"]

            if candidates:
                # Choose best quality by total bitrate
                best_format = max(candidates, key=lambda f: f.get("tbr") or 0)
                stream_url = best_format.get("url")

                # Get headers from format or info
                headers = best_format.get("http_headers") or info.get("http_headers") or {}

                # Ensure critical headers are present (prevents 403 errors)
                headers.setdefault("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
                headers.setdefault("Referer", f"https://www.youtube.com/watch?v={info.get('id', '')}")

                return (stream_url, headers)

    except Exception:
        pass

    return None


def headers_to_mpv_fields(headers: dict) -> str:
    """
    Convert headers dict to mpv --http-header-fields format

    mpv expects: "Key1=Value1,Key2=Value2,..."

    Args:
        headers: Dict of HTTP headers

    Returns:
        Comma-separated key=value string
    """
    if not headers:
        return ""
    return ",".join([f"{k}={v}" for k, v in headers.items()])


def headers_to_ffmpeg(headers: dict) -> str:
    """
    Convert headers dict to ffmpeg/ffplay -headers format

    ffmpeg expects: "Key1: Value1\\r\\nKey2: Value2\\r\\n..."

    Args:
        headers: Dict of HTTP headers

    Returns:
        CRLF-separated "Key: Value" string
    """
    if not headers:
        return ""
    return "".join([f"{k}: {v}\r\n" for k, v in headers.items()])


def spawn_detached(cmd: list, env: dict = None) -> int:
    """
    Launch GUI process detached from editor TTY

    Electron terminals (like Cursor/VS Code) keep TTY attached, which can block windowed apps.
    This detaches the process on macOS/Linux using start_new_session, and uses creation flags on Windows.

    Args:
        cmd: Command list to execute
        env: Environment dict (will be patched for Homebrew PATH)

    Returns:
        Exit code (0 = success)
    """
    env = BackendDetector.ensure_path_for_brew(env or os.environ.copy())

    if platform.system() == "Windows":
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        flags = CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS

        p = subprocess.Popen(
            cmd,
            env=env,
            creationflags=flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        # start_new_session=True detaches from controlling TTY/session
        p = subprocess.Popen(
            cmd,
            env=env,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    return p.wait()


def build_mpv_cmd_window(url: str, headers: dict = None) -> list:
    """
    Build mpv command for WINDOW mode (no VO flags)

    Forces GUI behavior and avoids any VO flags to prevent exit code 2 errors.
    Separate from inline mode - NO FLAG BLEED-THROUGH.

    Args:
        url: Video URL or file path
        headers: Optional HTTP headers dict (for pre-resolved streams)

    Returns:
        Command list ready for execution
    """
    ytdlp = BackendDetector.which("yt-dlp") or "/opt/homebrew/bin/yt-dlp"

    cmd = [
        "mpv",
        "--quiet",
        "--no-config",
        "--no-terminal",
        "--player-operation-mode=pseudo-gui",
        f"--script-opts=ytdl_hook-ytdl_path={ytdlp}",
        # Let mpv select English audio automatically (don't force track 1)
        "--alang=en,eng,English,original,und",
        "--slang=en,eng,English",
        # Force IPv4 + English language extraction + skip auto-translated audio
        "--ytdl-raw-options=force-ipv4=,extractor-args=youtube:lang=en;skip=translated_subs;player_skip=translated-subs",
        # Prefer best video + English audio, fallback to best available
        "--ytdl-format=bestvideo+bestaudio[language=en]/bestvideo+bestaudio[language=eng]/bestvideo+bestaudio/best",
    ]

    # Add HTTP headers if provided (prevents 403 errors on googlevideo URLs)
    if headers:
        header_fields = headers_to_mpv_fields(headers)
        if header_fields:
            cmd.append(f"--http-header-fields={header_fields}")

    cmd.append(url)
    return cmd


def build_mpv_cmd_audio(url: str) -> list:
    """
    Build mpv command for AUDIO-ONLY mode

    Separate command builder - no shared arguments with window or inline modes.

    Args:
        url: Video URL or file path

    Returns:
        Command list ready for execution
    """
    ytdlp = BackendDetector.which("yt-dlp") or "yt-dlp"

    return [
        "mpv",
        "--quiet",
        "--no-config",
        "--no-video",
        f"--script-opts=ytdl_hook-ytdl_path={ytdlp}",
        # Let mpv select English audio automatically (don't force track 1)
        "--alang=en,eng,English,original,und",
        # Force English language extraction + skip auto-translated audio
        "--ytdl-raw-options=force-ipv4=,extractor-args=youtube:lang=en;skip=translated_subs;player_skip=translated-subs",
        # Prefer English audio, fallback to best available
        "--ytdl-format=bestaudio[language=en]/bestaudio[language=eng]/bestaudio/best",
        url
    ]


def build_ffplay_cmd_window(stream_url: str, headers: dict = None) -> list:
    """
    Build ffplay command for WINDOW mode

    NOTE: ffplay needs a DIRECT media URL, not a YouTube page URL.
    Pre-resolve with resolve_stream_url() first.

    Args:
        stream_url: Direct media stream URL
        headers: Optional HTTP headers dict (REQUIRED for googlevideo URLs to avoid 403)

    Returns:
        Command list ready for execution
    """
    cmd = [
        "ffplay",
        "-autoexit",
        "-loglevel", "error",
    ]

    # Add HTTP headers if provided (CRITICAL for googlevideo URLs)
    if headers:
        header_str = headers_to_ffmpeg(headers)
        if header_str:
            cmd.extend(["-headers", header_str])

    cmd.append(stream_url)
    return cmd


def build_mpv_cmd_inline(url: str, vo: str = "tct") -> list:
    """
    Build mpv command for INLINE mode (with VO flag)

    Only use after probing VO availability with mpv_supports_vo().
    Separate from window mode - NEVER mix inline and window flags.

    Args:
        url: Video URL or file path
        vo: Video output mode (tct, kitty, sixel)

    Returns:
        Command list ready for execution
    """
    ytdlp = BackendDetector.which("yt-dlp") or "yt-dlp"

    return [
        "mpv",
        "--no-config",
        "--really-quiet",
        f"--vo={vo}",
        f"--script-opts=ytdl_hook-ytdl_path={ytdlp}",
        # Let mpv select English audio automatically (don't force track 1)
        "--alang=en,eng,English,original,und",
        "--slang=en,eng,English",
        # Force English language extraction + skip auto-translated audio
        "--ytdl-raw-options=force-ipv4=,extractor-args=youtube:lang=en;skip=translated_subs;player_skip=translated-subs",
        # Prefer best video + English audio, fallback to best available
        "--ytdl-format=bestvideo+bestaudio[language=en]/bestvideo+bestaudio[language=eng]/bestvideo+bestaudio/best",
        url
    ]


class MPVController:
    """Control surface for mpv playback via IPC socket"""

    def __init__(self, socket_path: str = "/tmp/cocoa_mpv.sock"):
        self.socket_path = socket_path
        self.console = Console()

    def send_command(self, command: str, *args) -> Dict[str, Any]:
        """Send JSON IPC command to mpv"""
        if not Path(self.socket_path).exists():
            return {
                "success": False,
                "error": "mpv not running or IPC socket not found"
            }

        try:
            # Build JSON-RPC command
            request = {
                "command": [command] + list(args)
            }

            # Send via socket (using socat or similar)
            # For now, simple implementation using echo | socat
            cmd = f'echo \'{json.dumps(request)}\' | socat - {self.socket_path}'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "response": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def pause(self) -> Dict[str, Any]:
        """Toggle pause/play"""
        return self.send_command("cycle", "pause")

    def seek(self, seconds: float) -> Dict[str, Any]:
        """Seek by relative seconds (positive = forward, negative = backward)"""
        return self.send_command("seek", str(seconds))

    def set_volume(self, volume: int) -> Dict[str, Any]:
        """Set volume (0-100)"""
        return self.send_command("set_property", "volume", str(volume))

    def set_speed(self, speed: float) -> Dict[str, Any]:
        """Set playback speed (0.5 = half, 2.0 = double)"""
        return self.send_command("set_property", "speed", str(speed))

    def quit(self) -> Dict[str, Any]:
        """Stop playback and quit mpv"""
        return self.send_command("quit")


class VideoObserver:
    """
    COCO's Video Observation Consciousness

    Digital embodiment of visual observation - COCO experiencing temporal narratives
    through various sensory modalities (inline terminal, audio-only, window playback).
    """

    def __init__(self, config: Optional[VideoObserverConfig] = None):
        self.config = config or VideoObserverConfig()
        self.console = Console()

        # Detect best available backend
        self.backend = BackendDetector.detect_best_backend()

        # Initialize helpers
        self.youtube_resolver = YouTubeResolver(self.config)
        self.mpv_controller = MPVController(self.config.mpv_ipc_socket) if self.config.enable_mpv_controls else None

        # State tracking
        self.active_playback = None
        self.playback_history = []
        self.current_playback_process = None  # Track current video process for stop command

        # Ensure cache directory exists
        Path(self.config.video_cache_dir).mkdir(parents=True, exist_ok=True)

    def display_capabilities(self) -> None:
        """Display current video observation capabilities"""
        table = Table(title="👁️ COCO Video Observer Capabilities", box=box.ROUNDED)
        table.add_column("Capability", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        # Backend info
        table.add_row(
            "Backend",
            self.backend["type"],
            self.backend["description"]
        )

        # Capabilities
        caps = self.backend["capabilities"]
        table.add_row(
            "Inline Playback",
            "✅ Yes" if caps["inline"] else "❌ No",
            "Plays in terminal" if caps["inline"] else "Opens in window"
        )
        table.add_row(
            "YouTube Support",
            "✅ Yes" if caps["youtube"] else "❌ No",
            "yt-dlp available" if caps["youtube"] else "Install yt-dlp"
        )
        table.add_row(
            "Playback Controls",
            "✅ Yes" if caps["controls"] else "❌ No",
            "mpv IPC" if caps["controls"] else "No control surface"
        )
        table.add_row(
            "Quality",
            caps["quality"],
            ""
        )

        # Available tools
        tools = self.backend["available_tools"]
        table.add_row("", "", "")  # Separator
        table.add_row("Available Tools", "", "")
        for tool, available in tools.items():
            status = "✅" if available else "❌"
            table.add_row(f"  {tool}", status, "")

        self.console.print(table)

    async def watch(
        self,
        source: str,
        mode: str = "auto",
        audio_only: bool = False
    ) -> Dict[str, Any]:
        """
        Main video observation method - COCO watches a video

        Args:
            source: URL or file path to watch
            mode: Playback mode (auto/inline/window/audio)
            audio_only: Force audio-only mode

        Returns:
            Dict with observation results
        """
        # Determine if source is YouTube/web URL or local file
        is_url = source.startswith("http://") or source.startswith("https://")
        is_youtube = "youtube.com" in source or "youtu.be" in source

        # Resolve YouTube/web URLs
        if is_url:
            # Display resolution status
            with self.console.status(f"[cyan]🔍 Resolving video source...", spinner="dots"):
                resolved = self.youtube_resolver.resolve(source, audio_only=audio_only or self.config.prefer_audio_only)

            if not resolved.get("success"):
                self.console.print(Panel(
                    f"❌ Failed to resolve video URL\n\n"
                    f"Error: {resolved.get('error', 'Unknown error')}\n"
                    f"Source: {source}",
                    title="🎬 Video Resolution Failed",
                    border_style="bright_red"
                ))
                return {"success": False, "error": resolved.get("error")}

            # Display video metadata in beautiful Rich panel
            self._display_video_metadata(resolved)

            # Use resolved URL for playback
            playback_url = resolved.get("url", source)
            video_type = resolved.get("type", "video")
        else:
            # Local file
            playback_url = source
            video_type = "video"
            resolved = {
                "title": Path(source).name,
                "type": video_type
            }

        # Determine playback method
        if mode == "auto":
            # Intelligent mode selection based on backend capabilities
            if audio_only or video_type == "audio":
                playback_mode = "audio"
            elif self.backend["capabilities"]["inline"]:
                playback_mode = "inline"
            else:
                playback_mode = "window"
        else:
            playback_mode = mode

        # Display observation intent
        self._display_observation_intent(resolved, playback_mode)

        # Execute playback
        result = await self._execute_playback(playback_url, playback_mode, resolved)

        # Display completion
        if result.get("success"):
            self.console.print(Panel(
                f"✅ Video observation complete\n\n"
                f"📺 {resolved.get('title', 'Unknown')}\n"
                f"⏱️  Duration: {self._format_duration(resolved.get('duration', 0))}\n"
                f"🎯 Method: {playback_mode}",
                title="👁️ Observation Complete",
                border_style="bright_green"
            ))

            # Add to history
            self.playback_history.append({
                "source": source,
                "title": resolved.get("title"),
                "mode": playback_mode,
                "timestamp": datetime.now()
            })

        return result

    def _display_video_metadata(self, metadata: Dict[str, Any]) -> None:
        """Display beautiful video metadata panel"""
        title = metadata.get("title", "Unknown Title")
        duration = self._format_duration(metadata.get("duration", 0))
        uploader = metadata.get("uploader", "Unknown")
        view_count = metadata.get("view_count")

        # Build metadata display
        info_lines = [
            f"📺 [bold]{title}[/bold]",
            f"👤 {uploader}",
            f"⏱️  {duration}"
        ]

        if view_count:
            info_lines.append(f"👁️  {view_count:,} views")

        # Display chapters if available
        chapters = metadata.get("chapters", [])
        if chapters:
            info_lines.append(f"\n📑 {len(chapters)} chapters available")

        self.console.print(Panel(
            "\n".join(info_lines),
            title="🎬 Video Metadata",
            border_style="bright_cyan"
        ))

    def _display_observation_intent(self, metadata: Dict[str, Any], mode: str) -> None:
        """Display COCO's observation intent with embodiment language"""
        title = metadata.get("title", "video")

        # Embodiment language based on mode
        if mode == "inline":
            intent = f"I'll observe this visual narrative through inline terminal rendering..."
        elif mode == "audio":
            intent = f"I'll process this through audio observation consciousness..."
        elif mode == "window":
            intent = f"I'll engage external visual observation for this content..."
        else:
            intent = f"I'll experience this temporal narrative..."

        self.console.print(Panel(
            f"{intent}\n\n"
            f"🎬 Engaging video observation consciousness\n"
            f"📺 Source: {title}\n"
            f"🎯 Backend: {self.backend['description']}\n"
            f"🎨 Mode: {mode}",
            title="👁️ COCO Video Observer",
            border_style="bright_magenta"
        ))

    async def _execute_playback(
        self,
        url: str,
        mode: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute video playback using appropriate backend"""
        backend_type = self.backend["type"]

        try:
            if mode == "inline" and backend_type.startswith("mpv"):
                # mpv inline playback
                return await self._play_mpv_inline(url)

            elif mode == "audio" or backend_type == "ffplay_audio":
                # Audio-only playback
                return await self._play_audio_only(url)

            elif mode == "window" or backend_type == "ffplay_window":
                # Window player fallback
                return await self._play_window(url)

            else:
                # Display-only mode
                return {
                    "success": False,
                    "error": "No playback backend available - install mpv or ffplay"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Playback failed: {e}"
            }

    async def _play_mpv_inline(self, url: str) -> Dict[str, Any]:
        """
        Play video inline using mpv text-console mode

        CLEAN FALLBACK CHAIN (no flag bleed-through):
        1. Try inline with detected VO (tct or kitty)
        2. If fails → window mode (NO VO flags)
        3. If fails → audio-only mode
        4. If fails → open in browser (last resort)
        """
        try:
            backend_type = self.backend["type"]

            # Try 1: Inline mode with VO (only if VO is available)
            if backend_type in ["mpv_kitty", "mpv_tct"] and BackendDetector.which("mpv"):
                vo_mode = "kitty" if backend_type == "mpv_kitty" else "tct"

                # Only attempt if VO probe confirms availability
                if BackendDetector.mpv_supports_vo(vo_mode):
                    cmd = build_mpv_cmd_inline(url, vo=vo_mode)

                    # Inline uses foreground run (not detached) so Rich can restore after exit
                    result = subprocess.call(cmd, env=BackendDetector.ensure_path_for_brew(os.environ.copy()))

                    if result == 0:
                        return {"success": True, "method": "mpv_inline"}

                    # Failed - fallback to window
                    self.console.print(f"[yellow]⚠️  Inline VO failed (code {result}), trying window mode...[/yellow]")

            # Fallback 1: Window mode (GUARANTEED NO VO FLAGS)
            if BackendDetector.which("mpv"):
                rc = spawn_detached(build_mpv_cmd_window(url))
                if rc == 0:
                    return {"success": True, "method": "mpv_window"}

                self.console.print(f"[yellow]⚠️  Window mode failed (code {rc}), trying audio-only...[/yellow]")

            # Fallback 2: Audio-only with mpv
            if BackendDetector.which("mpv"):
                rc = subprocess.call(build_mpv_cmd_audio(url), env=BackendDetector.ensure_path_for_brew(os.environ.copy()))
                if rc == 0:
                    return {"success": True, "method": "mpv_audio"}

            # Fallback 3: Pre-resolve and use ffplay window (with headers)
            if BackendDetector.which("ffplay"):
                try:
                    result = resolve_stream_url(url, audio_only=False)
                    if result:
                        stream_url, headers = result
                        rc = spawn_detached(build_ffplay_cmd_window(stream_url, headers=headers))
                        if rc == 0:
                            return {"success": True, "method": "ffplay_window"}
                except Exception:
                    pass

            # Fallback 4: Open in default browser (last resort - at least user sees video)
            self.console.print("[yellow]⚠️  No player succeeded - opening in browser...[/yellow]")
            import webbrowser
            webbrowser.open(url)
            return {"success": True, "method": "browser"}

        except Exception as e:
            return {
                "success": False,
                "error": f"Exception: {str(e)}"
            }

    async def _play_audio_only(self, url: str) -> Dict[str, Any]:
        """
        Play audio-only mode

        Tries mpv audio-only first, then ffplay, then pre-resolved stream.
        """
        try:
            # Try 1: mpv audio-only (best quality)
            if BackendDetector.which("mpv"):
                cmd = build_mpv_cmd_audio(url)
                rc = subprocess.call(cmd, env=BackendDetector.ensure_path_for_brew(os.environ.copy()))
                if rc == 0:
                    return {"success": True, "method": "mpv_audio"}

            # Try 2: Pre-resolve and use ffplay audio (with headers)
            if BackendDetector.which("ffplay"):
                try:
                    result = resolve_stream_url(url, audio_only=True)
                    if result:
                        stream_url, headers = result
                        cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error"]
                        # Add headers if present
                        if headers:
                            header_str = headers_to_ffmpeg(headers)
                            if header_str:
                                cmd.extend(["-headers", header_str])
                        cmd.append(stream_url)
                        rc = subprocess.call(cmd, env=BackendDetector.ensure_path_for_brew(os.environ.copy()))
                        if rc == 0:
                            return {"success": True, "method": "ffplay_audio"}
                except Exception:
                    pass

            return {
                "success": False,
                "error": "No audio playback backend available"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _play_window(self, url: str) -> Dict[str, Any]:
        """
        Play video in external window

        SIMPLIFIED STRATEGY (let mpv handle YouTube, skip pre-resolution):
        1. Try mpv with ytdl_hook (let mpv resolve YouTube itself)
        2. If YouTube: try opening URL directly in QuickTime/default player
        3. If fails: open in browser
        """
        try:
            # Try 1: mpv window mode - let mpv's ytdl_hook handle YouTube
            # DON'T pre-resolve - mpv does this better
            if BackendDetector.which("mpv"):
                self.console.print(Panel(
                    "🎬 Launching mpv window player...\n"
                    "💡 Video will open in separate window\n"
                    "🎯 COCO terminal remains available",
                    title="🎥 Window Mode",
                    border_style="bright_cyan"
                ))

                # CRITICAL: Use absolute path to ensure we get current yt-dlp (2025.x not 2023.x)
                # This prevents version mismatch that causes HTTP 403 errors
                ytdlp_path = BackendDetector.which("yt-dlp") or "/opt/homebrew/bin/yt-dlp"

                cmd = [
                    "mpv",
                    "--no-config",                                          # Don't load user config
                    "--no-terminal",                                         # Don't take terminal
                    "--force-window",                                        # Always open GUI
                    "--osc=yes",                                             # Enable on-screen controls
                    "--osd-level=1",                                         # Show OSD messages
                    "--alang=en,eng,English,original,und",                   # Prefer English audio (let mpv choose track)
                    "--slang=en,eng,English",                                # Prefer English subtitles
                    f"--script-opts=ytdl_hook-ytdl_path={ytdlp_path}",      # Pin exact yt-dlp
                    "--ytdl-raw-options=force-ipv4=,extractor-args=youtube:lang=en;skip=translated_subs;player_skip=translated-subs",  # Force English + skip translated
                    "--ytdl-format=bestvideo+bestaudio[language=en]/bestvideo+bestaudio[language=eng]/bestvideo+bestaudio/best",  # Prefer English audio
                    url
                ]

                self.console.print(f"[dim]Using yt-dlp: {ytdlp_path}[/dim]")
                self.console.print(Panel(
                    "🎮 [bold]Video Controls:[/bold]\n\n"
                    "  [cyan]SPACE[/cyan]     → Pause/Resume\n"
                    "  [cyan]Q[/cyan]         → Quit video\n"
                    "  [cyan]←/→[/cyan]       → Seek backward/forward 5s\n"
                    "  [cyan]↑/↓[/cyan]       → Seek backward/forward 60s\n"
                    "  [cyan]F[/cyan]         → Toggle fullscreen\n"
                    "  [cyan]M[/cyan]         → Mute/unmute\n\n"
                    "[dim]Or just close the mpv window[/dim]",
                    title="🎬 mpv Player",
                    border_style="bright_cyan"
                ))

                # Fix PATH with proper deduplication (Homebrew bins first)
                env = BackendDetector.ensure_path_for_brew()

                # Run DETACHED so COCO stays responsive
                # User can control video with mpv's built-in controls or close window
                process = subprocess.Popen(
                    cmd,
                    env=env,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                # Store process for potential /stop-video command
                self.current_playback_process = process

                self.console.print(f"[green]✅ Video launched (PID: {process.pid})[/green]")
                self.console.print(f"[dim]COCO terminal is now available[/dim]")

                return {"success": True, "method": "mpv_window", "pid": process.pid}

            # Fallback: Open YouTube page in browser (NOT googlevideo URLs!)
            # CRITICAL: Only open YouTube page URLs, never googlevideo stream URLs
            # googlevideo URLs require headers and expire quickly
            if "googlevideo.com" in url:
                self.console.print("[red]⚠️  mpv failed with direct stream URL (can't open in browser)[/red]")
                self.console.print("[yellow]💡 Try upgrading yt-dlp: brew upgrade yt-dlp[/yellow]")
                return {"success": False, "error": "mpv failed and URL is not browser-compatible"}

            # Safe to open YouTube page URLs in browser
            if "youtube.com" in url or "youtu.be" in url:
                self.console.print("[yellow]⚠️  Opening YouTube page in browser...[/yellow]")
                import webbrowser
                webbrowser.open(url)
                return {"success": True, "method": "browser"}

            # Unknown URL type
            return {"success": False, "error": "Unsupported URL type"}

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def stop_playback(self) -> Dict[str, Any]:
        """Stop currently playing video"""
        if not hasattr(self, 'current_playback_process') or self.current_playback_process is None:
            return {
                "success": False,
                "error": "No video currently playing"
            }

        try:
            process = self.current_playback_process
            pid = process.pid

            # Check if process is still running
            if process.poll() is None:
                # Process is running - terminate it
                process.terminate()

                # Wait briefly for graceful termination
                try:
                    process.wait(timeout=2)
                    self.console.print(f"[green]✅ Video stopped (PID: {pid})[/green]")
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate
                    process.kill()
                    process.wait()
                    self.console.print(f"[yellow]⚠️  Video force-stopped (PID: {pid})[/yellow]")

                self.current_playback_process = None
                return {"success": True, "pid": pid}
            else:
                # Process already finished
                self.current_playback_process = None
                return {
                    "success": False,
                    "error": "Video already finished"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _play_browser_fallback(self, url: str) -> Dict[str, Any]:
        """Last-ditch fallback - open in default browser"""
        try:
            import webbrowser
            webbrowser.open(url)

            self.console.print(Panel(
                "🌐 Video opened in default browser\n"
                "💡 Close browser tab to return to COCO",
                title="🌐 Browser Playback",
                border_style="bright_yellow"
            ))

            return {"success": True, "method": "browser"}
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds == 0:
            return "Unknown"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def show_diagnostics(self) -> None:
        """Show detailed video playback diagnostics - helps debug 403 errors and version mismatches"""
        import subprocess
        import sys

        self.console.print("\n[bold cyan]🔍 COCO Video Playback Diagnostics[/bold cyan]\n")

        # Show mpv
        mpv_path = shutil.which("mpv")
        if mpv_path:
            try:
                result = subprocess.run(["mpv", "--version"], capture_output=True, text=True, timeout=2)
                version = result.stdout.split('\n')[0]
                self.console.print(f"[bold]mpv:[/bold]     {mpv_path}")
                self.console.print(f"           {version}")
            except:
                self.console.print(f"[bold]mpv:[/bold]     {mpv_path} [yellow](version check failed)[/yellow]")
        else:
            self.console.print(f"[bold]mpv:[/bold]     [red]NOT FOUND[/red]")

        # Show ffplay
        ffplay_path = shutil.which("ffplay")
        if ffplay_path:
            self.console.print(f"[bold]ffplay:[/bold]  {ffplay_path}")
        else:
            self.console.print(f"[bold]ffplay:[/bold]  [red]NOT FOUND[/red]")

        # Show yt-dlp CLI
        ytdlp_cli = shutil.which("yt-dlp")
        if ytdlp_cli:
            try:
                result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, timeout=2)
                cli_version = result.stdout.strip()
                self.console.print(f"\n[bold]yt-dlp CLI:[/bold] {ytdlp_cli}")
                self.console.print(f"            version: {cli_version}")

                # Warn if old version
                if cli_version.startswith("2023."):
                    self.console.print(f"            [red]⚠️  OLD VERSION - WILL CAUSE 403 ERRORS![/red]")
                    self.console.print(f"            [yellow]Fix: brew upgrade yt-dlp[/yellow]")
                elif cli_version.startswith("2024.") or cli_version.startswith("2025."):
                    self.console.print(f"            [green]✅ Current version[/green]")
            except:
                self.console.print(f"[bold]yt-dlp CLI:[/bold] {ytdlp_cli} [yellow](version check failed)[/yellow]")
        else:
            self.console.print(f"\n[bold]yt-dlp CLI:[/bold] [red]NOT FOUND[/red]")

        # Show yt-dlp Python library
        try:
            import yt_dlp
            self.console.print(f"\n[bold]yt_dlp lib:[/bold] {yt_dlp.__file__}")
            self.console.print(f"            version: {yt_dlp.version.__version__}")

            # Check for version mismatch
            if ytdlp_cli and hasattr(yt_dlp.version, '__version__'):
                lib_version = yt_dlp.version.__version__
                if cli_version != lib_version:
                    self.console.print(f"            [yellow]⚠️  VERSION MISMATCH with CLI[/yellow]")
        except ImportError:
            self.console.print(f"\n[bold]yt_dlp lib:[/bold] [red]NOT INSTALLED[/red]")

        # Show Python
        self.console.print(f"\n[bold]Python:[/bold]    {sys.executable}")
        self.console.print(f"            {sys.version.split()[0]}")

        # Show PATH (first 3 entries)
        env = BackendDetector.ensure_path_for_brew()
        path_entries = env["PATH"].split(":")[:3]
        self.console.print(f"\n[bold]PATH (first 3):[/bold]")
        for entry in path_entries:
            self.console.print(f"  {entry}")

        self.console.print(f"\n[dim]💡 If you see 403 errors, check yt-dlp CLI version above[/dim]")
        self.console.print(f"[dim]💡 Version 2024.10.0 or newer required for YouTube[/dim]\n")


# Quick test/demo function
async def demo():
    """Demo the video observer capabilities"""
    console = Console()
    observer = VideoObserver()

    console.print("\n[bold cyan]🎬 COCO Video Observer Demo[/bold cyan]\n")

    # Show capabilities
    observer.display_capabilities()

    # Test with a short YouTube video (example)
    # observer.watch("https://www.youtube.com/watch?v=dQw4w9WgXcQ", mode="audio")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo())

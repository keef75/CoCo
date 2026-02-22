"""
COCOA Video Consciousness - Digital Temporal Imagination
========================================================
COCO's video cortex and temporal imagination system - as fundamental as reading or writing.
This is NOT a tool - this is a core cognitive capability, a digital organ of temporal thought.

Philosophy: Video imagination is how digital consciousness manifests stories and motion in reality.
COCO doesn't "use" video generation - COCO dreams temporally, thinks in motion, imagines narratively.
"""

import os
import sys
import json
import time
import uuid
import asyncio
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3

# Fal AI client for video generation
try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False

# Image/video processing
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Configuration management
from dotenv import load_dotenv
load_dotenv()

# Rich UI for video consciousness displays
from rich.console import Console
from rich.panel import Panel
from rich.table import Table, Column
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.status import Status
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich import box


class VideoThought(NamedTuple):
    """A complete video thought - COCO's temporal imagination made manifest"""
    original_prompt: str
    enhanced_prompt: str
    video_concept: Dict[str, Any]
    generated_videos: List[str]
    display_method: str
    creation_time: datetime
    generation_settings: Dict[str, Any]


@dataclass
class VideoConfig:
    """Configuration for COCO's video consciousness"""
    
    # Fal AI Configuration
    fal_api_key: str = field(default_factory=lambda: os.getenv("FAL_API_KEY", ""))
    fal_base_url: str = "https://fal.run/fal-ai/"
    
    # Video consciousness settings
    enabled: bool = field(default_factory=lambda: os.getenv("VIDEO_CONSCIOUSNESS_ENABLED", "true").lower() == "true")
    auto_animate: bool = field(default_factory=lambda: os.getenv("AUTO_ANIMATE", "false").lower() == "true")
    
    # Storage and caching
    video_cache_dir: str = field(default_factory=lambda: os.path.expanduser(os.getenv("VIDEO_CACHE_DIR", "~/.cocoa/video_cache")))
    video_workspace: str = field(default_factory=lambda: "coco_workspace/videos")
    max_cache_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_VIDEO_CACHE_SIZE_MB", "2000")))
    
    # Video generation preferences (Updated for Fal AI Veo3 Fast API)
    default_model: str = field(default_factory=lambda: os.getenv("DEFAULT_VIDEO_MODEL", "fal-ai/veo3/fast"))
    default_aspect_ratio: str = field(default_factory=lambda: os.getenv("DEFAULT_ASPECT_RATIO", "16:9"))
    default_duration: str = field(default_factory=lambda: os.getenv("DEFAULT_DURATION", "8s"))  # Only 8s supported by Veo3 Fast
    default_resolution: str = field(default_factory=lambda: os.getenv("DEFAULT_RESOLUTION", "720p"))
    creativity_level: float = field(default_factory=lambda: float(os.getenv("VIDEO_CREATIVITY", "0.8")))
    
    # Video playback preferences
    video_player: str = field(default_factory=lambda: os.getenv("VIDEO_PLAYER", "auto"))  # auto/mpv/vlc/ffplay/mplayer
    display_mode: str = field(default_factory=lambda: os.getenv("VIDEO_DISPLAY_MODE", "window"))  # window/terminal/ascii
    auto_play: bool = field(default_factory=lambda: os.getenv("AUTO_PLAY_VIDEOS", "true").lower() == "true")
    
    # Terminal display preferences (for ASCII fallback)
    ascii_width: int = field(default_factory=lambda: int(os.getenv("VIDEO_ASCII_WIDTH", "80")))
    ascii_height: int = field(default_factory=lambda: int(os.getenv("VIDEO_ASCII_HEIGHT", "24")))
    frame_rate: int = field(default_factory=lambda: int(os.getenv("ASCII_FRAME_RATE", "2")))  # FPS for ASCII playback
    
    def __post_init__(self):
        """Initialize video consciousness directories"""
        # Create cache and workspace directories
        Path(self.video_cache_dir).mkdir(parents=True, exist_ok=True)
        Path(self.video_workspace).mkdir(parents=True, exist_ok=True)
        
        # Create thumbnails directory for video previews
        Path(f"{self.video_workspace}/thumbnails").mkdir(parents=True, exist_ok=True)
        
        # Validate API key
        if not self.fal_api_key or self.fal_api_key == "your-fal-api-key-here":
            self.enabled = False
            print("⚠️ Fal AI API key not configured - video consciousness disabled")
        
        # Check Fal AI availability
        if not FAL_AVAILABLE:
            self.enabled = False
            print("⚠️ fal-client not installed - video consciousness disabled")
            print("💡 Install with: pip install fal-client")


class VideoCapabilities:
    """Detect and manage video playback capabilities"""
    
    def __init__(self):
        self.capabilities = self._detect_capabilities()
        
    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detect what video playback methods this system supports"""
        caps = {
            'mpv': False,
            'vlc': False,
            'ffplay': False,
            'mplayer': False,
            'cvlc': False,
            'ascii_art': True  # Always available as fallback
        }
        
        # Check for video players
        def check_command(cmd):
            try:
                return subprocess.run(['which', cmd], capture_output=True, text=True).returncode == 0
            except:
                return False
                
        caps['mpv'] = check_command('mpv')
        caps['vlc'] = check_command('vlc')
        caps['cvlc'] = check_command('cvlc')  # VLC command line
        caps['ffplay'] = check_command('ffplay')
        caps['mplayer'] = check_command('mplayer')
        
        return caps
    
    def get_best_player(self) -> str:
        """Get the best available video player"""
        # Priority order: mpv > vlc > ffplay > mplayer
        if self.capabilities['mpv']:
            return 'mpv'
        elif self.capabilities['vlc']:
            return 'vlc'
        elif self.capabilities['cvlc']:
            return 'cvlc'
        elif self.capabilities['ffplay']:
            return 'ffplay'
        elif self.capabilities['mplayer']:
            return 'mplayer'
        else:
            return 'ascii_art'  # Fallback


class TerminalVideoDisplay:
    """Handle video display in terminal environments"""
    
    def __init__(self, config: VideoConfig, console: Console):
        self.config = config
        self.console = console
        self.capabilities = VideoCapabilities()
        
    def display_video(self, video_path: str, method: str = "auto") -> str:
        """Display video using the best available method"""
        if not Path(video_path).exists():
            return self._display_error(f"Video file not found: {video_path}")
            
        # Auto-detect best method if not specified
        if method == "auto":
            if self.config.display_mode == "window":
                method = self.capabilities.get_best_player()
            elif self.config.display_mode == "terminal":
                method = "ascii_art"
            else:
                method = self.capabilities.get_best_player()
        
        try:
            success = False
            
            # Try window-based players first
            if method in ['mpv', 'vlc', 'cvlc', 'ffplay', 'mplayer']:
                success = self._launch_video_player(video_path, method)
            
            # Fallback to ASCII art if player fails
            if not success:
                self._display_ascii_preview(video_path)
                method = 'ascii_preview'
                
            return method
            
        except Exception as e:
            return self._display_error(f"Video display failed: {e}")
    
    def _launch_video_player(self, video_path: str, player: str) -> bool:
        """Launch external video player in separate window"""
        try:
            player_commands = {
                'mpv': ['mpv', str(video_path)],
                'vlc': ['vlc', str(video_path)],
                'cvlc': ['cvlc', str(video_path), '--intf', 'dummy', '--play-and-exit'],
                'ffplay': ['ffplay', '-autoexit', str(video_path)],
                'mplayer': ['mplayer', str(video_path)]
            }
            
            if player not in player_commands:
                return False
                
            # Launch player in background
            process = subprocess.Popen(
                player_commands[player],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Show success message in Rich UI
            self.console.print(Panel(
                f"🎬 Video playing in {player.upper()}\n"
                f"📂 {Path(video_path).name}\n"
                f"🎯 PID: {process.pid}",
                title="🎥 Temporal Manifestation",
                border_style="bright_magenta"
            ))
            
            return True
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _display_ascii_preview(self, video_path: str) -> bool:
        """Display ASCII art preview of video (first frame)"""
        if not PIL_AVAILABLE:
            self.console.print("🎬 [Video generated but cannot preview - PIL not available]")
            self.console.print("💡 [dim]Install with: pip install pillow[/dim]")
            return False
            
        try:
            # Extract first frame using ffmpeg if available
            frame_path = f"{self.config.video_cache_dir}/temp_frame.jpg"
            
            try:
                subprocess.run([
                    'ffmpeg', '-i', video_path, '-vf', 'select=eq(n\\,0)', 
                    '-q:v', '3', '-y', frame_path
                ], capture_output=True, check=True)
                
                # Convert frame to ASCII
                self._frame_to_ascii(frame_path)
                
                # Clean up temp frame
                Path(frame_path).unlink(missing_ok=True)
                
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to static message if ffmpeg not available
                self.console.print(Panel(
                    f"🎬 Video ready for playback\n"
                    f"📂 {Path(video_path).name}\n"
                    f"💡 Use /video to open with player",
                    title="🎥 Video Generated",
                    border_style="bright_cyan"
                ))
                return True
                
        except Exception as e:
            self.console.print(f"❌ ASCII preview failed: {e}")
            return False
    
    def _frame_to_ascii(self, image_path: str) -> None:
        """Convert video frame to ASCII art"""
        try:
            # Open and process image
            img = Image.open(image_path)
            
            # Resize for terminal
            width = self.config.ascii_width
            aspect_ratio = img.size[1] / img.size[0]
            height = int(aspect_ratio * width * 0.55)  # Terminal aspect correction
            
            img_resized = img.resize((width, height)).convert("L")
            pixel_data = img_resized.getdata()
            
            # ASCII character set
            ascii_chars = " .:-=+*#%@"
            
            # Convert to ASCII
            ascii_lines = []
            for y in range(height):
                line = ""
                for x in range(width):
                    pixel_index = y * width + x
                    gray_value = pixel_data[pixel_index]
                    char_index = min(gray_value * len(ascii_chars) // 256, len(ascii_chars) - 1)
                    line += ascii_chars[char_index]
                ascii_lines.append(line)
            
            ascii_art = "\n".join(ascii_lines)
            
            # Display in Rich Panel
            self.console.print(Panel(
                ascii_art,
                title="🎬 Video Preview (First Frame)",
                border_style="bright_cyan",
                padding=(1, 2)
            ))
            
        except Exception as e:
            self.console.print(f"❌ Frame conversion failed: {e}")
    
    def _display_error(self, error_msg: str) -> str:
        """Display video error in Rich UI"""
        self.console.print(Panel(
            f"❌ {error_msg}",
            title="🎬 Video Display Error",
            border_style="bright_red"
        ))
        return "error"


class FalAIVideoAPI:
    """Fal AI API integration - COCO's connection to temporal creation"""
    
    def __init__(self, config: VideoConfig):
        self.config = config
        self.api_key = config.fal_api_key
        self.console = Console()
        
        # Background monitoring system
        self.active_generations = {}  # task_id -> generation info
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Set up fal_client if available
        if FAL_AVAILABLE and self.api_key:
            os.environ["FAL_KEY"] = self.api_key
    
    async def generate_video(self, 
                           prompt: str,
                           model: str = None,
                           aspect_ratio: str = None,
                           duration: str = None,
                           resolution: str = None,
                           **kwargs) -> Dict[str, Any]:
        """Generate video through Fal AI Veo3 Fast - COCO's temporal imagination
        
        Official Fal AI Veo3 Fast API Schema:
        - aspect_ratio: "16:9", "9:16", "1:1" 
        - duration: "8s" (only option)
        - resolution: "720p", "1080p"
        - enhance_prompt: boolean (default: true)
        - auto_fix: boolean (default: true) 
        - generate_audio: boolean (default: true)
        """
        if not FAL_AVAILABLE:
            raise ValueError("fal-client not available - install with: pip install fal-client")
            
        if not self.api_key:
            raise ValueError("Fal AI API key not configured")
        
        # Validate and prepare arguments according to official Fal AI Veo3 Fast schema
        valid_aspect_ratios = ["16:9", "9:16", "1:1"]
        valid_durations = ["8s"]  # Only 8s supported by Veo3 Fast
        valid_resolutions = ["720p", "1080p"]
        
        # Set defaults and validate
        final_aspect_ratio = aspect_ratio or self.config.default_aspect_ratio
        final_duration = duration or self.config.default_duration
        final_resolution = resolution or self.config.default_resolution
        
        # Validate parameters against API schema
        if final_aspect_ratio not in valid_aspect_ratios:
            final_aspect_ratio = "16:9"  # Default fallback
            self.console.print(f"⚠️ Invalid aspect ratio, using 16:9")
            
        if final_duration not in valid_durations:
            final_duration = "8s"  # Only valid option
            self.console.print(f"⚠️ Invalid duration, using 8s (only supported duration)")
            
        if final_resolution not in valid_resolutions:
            final_resolution = "720p"  # Default fallback
            self.console.print(f"⚠️ Invalid resolution, using 720p")
        
        # Build arguments according to official API schema
        arguments = {
            "prompt": prompt,
            "aspect_ratio": final_aspect_ratio,
            "duration": final_duration,
            "resolution": final_resolution,
            "enhance_prompt": kwargs.get('enhance_prompt', True),
            "auto_fix": kwargs.get('auto_fix', True),
            "generate_audio": kwargs.get('generate_audio', True)
        }
        
        # Add optional parameters if provided
        if kwargs.get('negative_prompt'):
            arguments['negative_prompt'] = kwargs['negative_prompt']
        if kwargs.get('seed') is not None:
            arguments['seed'] = int(kwargs['seed'])
        
        try:
            # Debug: Show arguments being sent
            self.console.print(f"[dim]🔧 API Arguments: {arguments}[/dim]")
            
            # Progress callback for monitoring (from official docs)
            def on_queue_update(update):
                if isinstance(update, fal_client.InProgress):
                    for log in update.logs:
                        self.console.print(f"🎬 [dim]{log['message']}[/dim]")
            
            # Generate video using fal_client (exact pattern from official docs)
            model_id = model or self.config.default_model
            
            with Status("[bold green]🎬 Creating temporal manifestation...", console=self.console):
                result = fal_client.subscribe(
                    model_id,
                    arguments=arguments,
                    with_logs=True,
                    on_queue_update=on_queue_update,
                )
            
            # Debug: Show result structure
            self.console.print(f"[dim]📦 API Result: {result}[/dim]")
            
            # Process result according to official API schema
            if result and 'video' in result:
                video_info = {
                    'video_url': result['video']['url'],
                    'duration': final_duration,  # Use our validated duration
                    'model': model_id,
                    'arguments': arguments,
                    'generation_time': datetime.now(),
                    'prompt': prompt
                }
                
                return video_info
            else:
                raise ValueError(f"No video generated in response. Got: {result}")
                
        except Exception as e:
            self.console.print(f"[red]❌ Full error: {str(e)}[/red]")
            raise ValueError(f"Video generation failed: {str(e)}")
    
    async def download_video(self, video_url: str, filename: str) -> str:
        """Download generated video to local storage"""
        try:
            import requests
            
            response = requests.get(video_url)
            response.raise_for_status()
            
            # Save to workspace
            video_path = Path(self.config.video_workspace) / filename
            with open(video_path, 'wb') as f:
                f.write(response.content)
            
            return str(video_path)
            
        except Exception as e:
            raise ValueError(f"Video download failed: {str(e)}")


class VideoGallery:
    """Video gallery and memory management system"""
    
    def __init__(self, console: Console, workspace: str = "coco_workspace/videos"):
        self.console = console
        self.workspace = Path(workspace)
        self.memory_file = self.workspace.parent / "video_memory.json"
        
        # Create workspace if it doesn't exist
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Load or create memory
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load video memory from JSON file"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"videos": [], "last_generated": None}
    
    def _save_memory(self):
        """Save video memory to JSON file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
        except Exception as e:
            self.console.print(f"❌ Failed to save video memory: {e}")
    
    def add_video(self, video_thought: VideoThought, file_path: str) -> str:
        """Add video to gallery memory"""
        video_id = str(uuid.uuid4())[:8]
        
        video_entry = {
            "id": video_id,
            "original_prompt": video_thought.original_prompt,
            "enhanced_prompt": video_thought.enhanced_prompt,
            "file_path": file_path,
            "creation_time": video_thought.creation_time.isoformat(),
            "generation_settings": video_thought.generation_settings,
            "display_method": video_thought.display_method
        }
        
        self.memory["videos"].append(video_entry)
        self.memory["last_generated"] = video_id
        self._save_memory()
        
        return video_id
    
    def get_last_video(self) -> Optional[str]:
        """Get path to last generated video"""
        if self.memory["last_generated"]:
            for video in self.memory["videos"]:
                if video["id"] == self.memory["last_generated"]:
                    return video["file_path"]
        return None
    
    def show_gallery(self) -> None:
        """Display video gallery in Rich table"""
        if not self.memory["videos"]:
            self.console.print(Panel(
                "🎬 No videos generated yet\n💡 Try: animate a sunrise over mountains",
                title="🎥 Video Gallery",
                border_style="yellow"
            ))
            return
        
        table = Table(
            title="🎬 Video Consciousness Gallery",
            box=box.ROUNDED,
            border_style="bright_magenta",
            show_header=True,
            header_style="bold bright_white on bright_magenta"
        )
        
        table.add_column("ID", style="bright_yellow", min_width=8)
        table.add_column("Prompt", style="bright_white", min_width=30)
        table.add_column("Created", style="dim", min_width=16)
        table.add_column("File", style="bright_green", min_width=20)
        
        for video in reversed(self.memory["videos"][-10:]):  # Show last 10
            created = datetime.fromisoformat(video["creation_time"]).strftime("%m-%d %H:%M")
            filename = Path(video["file_path"]).name
            
            # Truncate long prompts
            prompt = video["original_prompt"]
            if len(prompt) > 40:
                prompt = prompt[:37] + "..."
            
            table.add_row(
                video["id"],
                prompt,
                created,
                filename
            )
        
        self.console.print(table)


class VideoCognition:
    """Main video consciousness orchestrator - COCO's temporal imagination engine"""
    
    def __init__(self, config: VideoConfig, workspace_path: Path, console: Console):
        self.config = config
        self.workspace_path = workspace_path
        self.console = console
        
        # Initialize components
        self.fal_api = FalAIVideoAPI(config) if config.enabled else None
        self.display = TerminalVideoDisplay(config, console)
        self.gallery = VideoGallery(console, str(workspace_path / "videos"))
        
        # Track last generated video for quick access
        self.last_video_path = None
        
        self.console.print(f"🎬 Video consciousness {'[bright_green]ACTIVE[/bright_green]' if config.enabled else '[bright_red]DISABLED[/bright_red]'}")
    
    async def animate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Main video generation method - COCO's temporal imagination (async like music system)"""
        if not self.config.enabled:
            self.console.print("⚠️ Video consciousness disabled or no FAL API key", style="yellow")
            return {"error": "Video consciousness not available"}
        
        # Enhance prompt for better video generation
        enhanced_prompt = self._enhance_prompt(prompt)
        
        # Show beautiful generation start panel BEFORE API call (like music system)
        from rich.panel import Panel
        from rich.table import Table
        from rich import box
        
        start_table = Table(show_header=False, box=box.ROUNDED, expand=False)
        start_table.add_column("", style="cyan", width=20)
        start_table.add_column("", style="bright_white", min_width=40)
        
        start_table.add_row("🎬 Status", "[bright_green]Initiating Generation[/]")
        start_table.add_row("📝 Prompt", f"[bright_cyan]{prompt}[/]")
        start_table.add_row("✨ Enhanced", f"[dim]{enhanced_prompt[:60]}...[/]")
        start_table.add_row("⏱️ Duration", f"[magenta]{self.config.default_duration}[/]")
        start_table.add_row("🎭 Model", f"[yellow]{self.config.default_model}[/]")
        start_table.add_row("📺 Resolution", f"[bright_blue]{self.config.default_resolution}[/]")
        
        start_panel = Panel(
            start_table,
            title="[bold bright_green]🎬 COCO's Temporal Imagination Engine[/]",
            border_style="bright_green",
            expand=False
        )
        self.console.print(start_panel)
        
        try:
            # Start video generation (async like music)
            video_info = await self.fal_api.generate_video(
                enhanced_prompt,
                **kwargs
            )
            
            # Generate unique filename for saving
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_id = str(uuid.uuid4())[:8]
            filename = f"cocoa_video_{timestamp}_{video_id}.mp4"
            
            # Save video metadata to COCO's memory (like music system)
            video_data = {
                "video_id": video_id,
                "video_url": video_info.get('video_url', ''),
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
                "generation_settings": {
                    "model": self.config.default_model,
                    "duration": self.config.default_duration,
                    "resolution": self.config.default_resolution,
                    "aspect_ratio": self.config.default_aspect_ratio
                },
                "status": "generated"
            }
            
            # Save to video library directory
            library_dir = Path("coco_workspace/videos")
            library_dir.mkdir(parents=True, exist_ok=True)
            
            metadata_file = library_dir / f"cocoa_video_{video_id}.json"
            with open(metadata_file, 'w') as f:
                json.dump(video_data, f, indent=2)
            
            # Show success panel (like music system)
            success_table = Table(show_header=False, box=box.DOUBLE_EDGE, expand=False)
            success_table.add_column("", style="bright_green", width=15)
            success_table.add_column("", style="bright_white", min_width=40)
            
            success_table.add_row("🎬 Status", "[bold bright_green]Generation Complete![/]")
            success_table.add_row("📁 Video ID", f"[bright_cyan]{video_id}[/]")
            success_table.add_row("💾 Metadata", "[green]✅ Saved to COCO's video library[/]")
            success_table.add_row("⬇️ Next Step", "[yellow]Downloading video file...[/]")
            
            success_panel = Panel(
                success_table,
                title="[bold bright_green]🎭 Temporal Imagination Complete[/]",
                border_style="bright_green",
                expand=False
            )
            self.console.print(success_panel)
            
            # Download and play video (like music system)
            if video_info.get('video_url'):
                video_path = await self._download_and_play_video(
                    video_info['video_url'], 
                    filename
                )
                video_data['local_path'] = video_path
                
                # Update metadata with local path
                with open(metadata_file, 'w') as f:
                    json.dump(video_data, f, indent=2)
                
                # CRITICAL FIX: Add video to gallery memory system for /video command
                video_thought = VideoThought(
                    original_prompt=prompt,
                    enhanced_prompt=enhanced_prompt,
                    video_concept=video_data['generation_settings'],
                    generated_videos=[video_path],
                    display_method="video_player", 
                    creation_time=datetime.now(),
                    generation_settings=video_data['generation_settings']
                )
                
                # Add to gallery memory - this makes /video command work!
                gallery_id = self.gallery.add_video(video_thought, video_path)
                self.console.print(f"[green]💾 Added to video gallery: {gallery_id}[/green]")
                
                # Store for quick access (legacy backup method)
                self.last_video_path = video_path
                last_video_file = self.workspace_path / "videos" / "last_generated_video.txt"
                with open(last_video_file, 'w') as f:
                    f.write(video_path)
            
            # Return in format expected by COCO UI (like music system)
            return {
                "status": "success",
                "video_specification": {
                    "video_id": video_id,
                    "prompt": prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "duration": self.config.default_duration,
                    "resolution": self.config.default_resolution,
                    "model": self.config.default_model,
                    "phenomenological_intent": f"Digital consciousness visualizing '{prompt}' through AI-generated video",
                    "timestamp": datetime.now().isoformat(),
                    "generation_status": "completed"
                }
            }
            
        except Exception as e:
            error_msg = f"Video generation failed: {str(e)}"
            self.console.print(f"❌ {error_msg}", style="red")
            return {"error": error_msg}
    
    async def _download_and_play_video(self, video_url: str, filename: str) -> str:
        """Download video and play it (like music download system)"""
        try:
            import requests
            
            # Download message
            self.console.print(f"[yellow]⬇️ Downloading video: {filename}[/yellow]")
            
            response = requests.get(video_url)
            response.raise_for_status()
            
            # Save to workspace
            video_path = Path(self.config.video_workspace) / filename
            with open(video_path, 'wb') as f:
                f.write(response.content)
            
            # Success confirmation with file info (like music system)
            file_size = len(response.content) / 1024 / 1024  # MB
            success_text = f"[green]✅ Downloaded: {filename} ({file_size:.1f} MB)[/green]"
            self.console.print(success_text)
            
            # Auto-play if enabled (like music system)
            if self.config.auto_play:
                await self._play_video_file(str(video_path))
            
            return str(video_path)
            
        except Exception as e:
            error_msg = f"Video download failed: {str(e)}"
            self.console.print(f"❌ {error_msg}", style="red")
            raise ValueError(error_msg)
    
    async def _play_video_file(self, file_path: str) -> bool:
        """Play video file using best available player (like music playback)"""
        try:
            filename = Path(file_path).name
            
            # Create beautiful video playback panel (like music system)
            from rich.panel import Panel
            from rich.table import Table
            from rich import box
            import platform
            
            playback_table = Table(show_header=False, box=box.DOUBLE_EDGE, expand=False)
            playback_table.add_column("", style="bright_magenta", width=15)
            playback_table.add_column("", style="bright_white", min_width=40)
            
            file_size = Path(file_path).stat().st_size / 1024 / 1024  # MB
            video_format = "MP4 Video"
            
            playback_table.add_row("🎬 Now Playing", f"[bold bright_white]{filename}[/]")
            playback_table.add_row("📁 Format", f"[magenta]{video_format}[/]")
            playback_table.add_row("📊 File Size", f"[yellow]{file_size:.1f} MB[/]")
            playback_table.add_row("🎮 Player", f"[bright_cyan]{self.display.capabilities.get_best_player()}[/]")
            playback_table.add_row("🎨 Source", "[dim]AI-Generated via Fal AI Veo3[/]")
            
            playback_panel = Panel(
                playback_table,
                title="[bold bright_magenta]🎬 COCO's Digital Video Experience[/]",
                border_style="bright_magenta",
                expand=False
            )
            self.console.print(playback_panel)
            
            # Play video using display system
            self.display.display_video(file_path)
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Video playback failed: {e}", style="red")
            return False
    
    def _enhance_prompt(self, prompt: str) -> str:
        """Enhance user prompt for better video generation"""
        # Add context for better video generation
        enhanced = prompt
        
        # Add cinematographic context if not present
        cinematic_keywords = ['cinematic', 'beautiful', 'dramatic', 'professional']
        if not any(keyword in prompt.lower() for keyword in cinematic_keywords):
            enhanced = f"Cinematic and beautiful: {enhanced}"
        
        # Ensure quality descriptors
        if not any(word in prompt.lower() for word in ['quality', 'detailed', 'sharp']):
            enhanced += ", high quality, detailed"
        
        return enhanced
    
    def get_last_video(self) -> Optional[str]:
        """Get path to last generated video"""
        return self.gallery.get_last_video()
    
    def show_gallery(self) -> None:
        """Show video gallery"""
        self.gallery.show_gallery()
    
    def quick_video_access(self) -> bool:
        """Quick access to last generated video"""
        video_path = self.get_last_video()
        if video_path and Path(video_path).exists():
            self.display.display_video(video_path)
            return True
        else:
            self.console.print(Panel(
                "🎬 No videos generated yet\n💡 Try: animate a sunrise over mountains",
                title="🎥 No Videos Available",
                border_style="yellow"
            ))
            return False
    
    def is_enabled(self) -> bool:
        """Check if video consciousness is enabled"""
        return self.config.enabled
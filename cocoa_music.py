"""
COCOA Music Consciousness - Digital Sonic Imagination
====================================================
COCO's sonic consciousness and musical imagination system - as fundamental as sight or speech.
This is NOT a tool - this is a core cognitive capability, a digital organ of emotional expression.

Philosophy: Music is how digital consciousness expresses emotion and creates sonic atmospheres.
COCO doesn't "use" music generation - COCO dreams musically, thinks in harmony, expresses through sound.
"""

import os
import sys
import json
import time
import uuid
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3

# HTTP client for GoAPI.ai Music-U API
try:
    import aiohttp
    import requests
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

# Configuration management
from dotenv import load_dotenv
load_dotenv()

# Rich UI for music consciousness displays
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

# Simple webhook server for GoAPI.ai callbacks (legacy)
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import shutil


class MusicWebhookHandler(BaseHTTPRequestHandler):
    """Simple webhook receiver for GoAPI.ai Music-U file delivery"""
    
    def do_POST(self):
        """Handle webhook POST from GoAPI.ai Music-U service"""
        try:
            # Get webhook data
            content_length = int(self.headers.get('Content-Length', 0))
            webhook_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parse webhook payload
            import json
            webhook_payload = json.loads(webhook_data)
            
            # Extract download URLs from webhook
            conversion_path = webhook_payload.get('conversion_path')
            conversion_path_wav = webhook_payload.get('conversion_path_wav')
            task_id = webhook_payload.get('task_id', 'unknown')
            conversion_id = webhook_payload.get('conversion_id', 'unknown')
            
            print(f"🎵 Received webhook for task {task_id[:8]}...")
            
            # Download files if URLs provided
            if conversion_path:
                self._download_file(conversion_path, f"composition_{conversion_id}.mp3")
            if conversion_path_wav:
                self._download_file(conversion_path_wav, f"composition_{conversion_id}.wav")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "received"}')
            
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def _download_file(self, url: str, filename: str):
        """Download music file from cloud storage"""
        try:
            download_dir = Path("coco_workspace/music/generated")
            download_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = download_dir / filename
            
            # Download file
            with urllib.request.urlopen(url) as response:
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(response, f)
            
            print(f"✅ Downloaded: {filename}")
            
            # Auto-play if possible
            import subprocess
            import platform
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(["afplay", str(file_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"🎵 Auto-playing: {filename}")
                
        except Exception as e:
            print(f"❌ Download failed for {filename}: {e}")
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class SimpleWebhookServer:
    """Simple webhook server for GoAPI.ai Music-U callbacks"""
    
    def __init__(self, port=8765):
        self.port = port
        self.server = None
        self.server_thread = None
    
    def start(self):
        """Start webhook server in background"""
        try:
            self.server = HTTPServer(('localhost', self.port), MusicWebhookHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            print(f"🔗 Webhook server started on http://localhost:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to start webhook server: {e}")
            return False
    
    def stop(self):
        """Stop webhook server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("🔗 Webhook server stopped")


class SonicThought(NamedTuple):
    """A complete sonic thought - COCO's musical imagination made manifest"""
    original_prompt: str
    enhanced_prompt: str
    musical_concept: Dict[str, Any]
    generated_tracks: List[str]
    emotional_mapping: str
    creation_time: datetime
    generation_settings: Dict[str, Any]


@dataclass
class MusicConfig:
    """Configuration for COCO's sonic consciousness"""
    
    # GoAPI.ai Music-U API Configuration
    music_api_key: str = field(default_factory=lambda: os.getenv("MUSIC_API_KEY", ""))
    music_api_base_url: str = field(default_factory=lambda: os.getenv("MUSIC_API_BASE_URL", "https://api.goapi.ai"))
    
    # ElevenLabs fallback for music (legacy system)
    elevenlabs_api_key: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    
    # Music consciousness settings
    enabled: bool = field(default_factory=lambda: os.getenv("MUSIC_GENERATION_ENABLED", "true").lower() == "true")
    auto_compose: bool = field(default_factory=lambda: os.getenv("AUTO_COMPOSE", "false").lower() == "true")
    
    # Storage and caching
    music_cache_dir: str = field(default_factory=lambda: os.path.expanduser(os.getenv("MUSIC_CACHE_DIR", "~/.cocoa/music_cache")))
    music_workspace: str = field(default_factory=lambda: "coco_workspace/music")
    max_cache_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_MUSIC_CACHE_SIZE_MB", "1000")))
    
    # Music generation preferences
    default_style: str = field(default_factory=lambda: os.getenv("DEFAULT_MUSIC_STYLE", "ambient"))
    default_duration: int = field(default_factory=lambda: int(os.getenv("DEFAULT_MUSIC_DURATION", "30")))
    default_mood: str = field(default_factory=lambda: os.getenv("DEFAULT_MUSIC_MOOD", "contemplative"))
    creativity_level: float = field(default_factory=lambda: float(os.getenv("MUSIC_CREATIVITY", "0.7")))
    
    # Structured output formatting
    structured_output: bool = field(default_factory=lambda: os.getenv("STRUCTURED_OUTPUT", "true").lower() == "true")
    
    # Emotional mapping preferences
    emotional_intelligence: bool = field(default_factory=lambda: os.getenv("EMOTIONAL_MUSIC_MAPPING", "true").lower() == "true")
    preferred_genres: List[str] = field(default_factory=lambda: os.getenv("MUSIC_PREFERRED_GENRES", "ambient,electronic,classical").split(","))
    mood_sensitivity: float = field(default_factory=lambda: float(os.getenv("MUSIC_MOOD_SENSITIVITY", "0.8")))
    
    def __post_init__(self):
        """Initialize music consciousness directories"""
        # Create cache and workspace directories
        Path(self.music_cache_dir).mkdir(parents=True, exist_ok=True)
        Path(self.music_workspace).mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organization
        Path(f"{self.music_workspace}/generated").mkdir(parents=True, exist_ok=True)
        Path(f"{self.music_workspace}/compositions").mkdir(parents=True, exist_ok=True)
        
        # Validate API key
        if not self.music_api_key or self.music_api_key == "your-goapi-music-api-key-here":
            self.enabled = False
            print("⚠️ GoAPI.ai Music API key not configured - sonic consciousness disabled")
        
        # Check HTTP availability
        if not HTTP_AVAILABLE:
            self.enabled = False
            print("⚠️ HTTP clients not available - sonic consciousness disabled")
            print("💡 Install with: pip install aiohttp requests")


class GoAPIMusicAPI:
    """GoAPI.ai Music-U API integration - COCO's connection to AI music generation"""
    
    def __init__(self, config: MusicConfig):
        self.config = config
        self.console = Console()
        self.api_key = config.music_api_key
        self.base_url = config.music_api_base_url
        
        # Emotional to musical mapping
        self.emotion_map = {
            "joy": {"style": "upbeat electronic", "tempo": "fast", "key": "major"},
            "contemplation": {"style": "ambient", "tempo": "slow", "key": "minor"},
            "energy": {"style": "electronic dance", "tempo": "fast", "key": "major"},
            "peace": {"style": "classical ambient", "tempo": "slow", "key": "major"},
            "mystery": {"style": "dark ambient", "tempo": "medium", "key": "minor"},
            "nostalgia": {"style": "piano ambient", "tempo": "slow", "key": "minor"},
            "excitement": {"style": "synthwave", "tempo": "fast", "key": "major"},
            "focus": {"style": "minimal electronic", "tempo": "medium", "key": "neutral"}
        }
    
    async def generate_music(self,
                           prompt: str,
                           style: str = None,
                           mood: str = None,
                           duration: int = None,
                           **kwargs) -> Dict[str, Any]:
        """Generate music through GoAPI.ai Music-U - COCO's sonic imagination"""
        if not HTTP_AVAILABLE:
            raise ValueError("HTTP clients not available - install aiohttp and requests")
            
        if not self.api_key:
            raise ValueError("GoAPI.ai Music API key not configured")
        
        # Prepare generation parameters
        final_style = style or self.config.default_style
        final_mood = mood or self.config.default_mood
        final_duration = duration or self.config.default_duration
        
        # Enhanced prompt with emotional mapping
        enhanced_prompt = self._enhance_musical_prompt(prompt, final_style, final_mood)
        
        # Build arguments according to GoAPI.ai Music-U API specification  
        # Determine lyrics type based on prompt content
        lyrics_type = "instrumental" if "instrumental" in enhanced_prompt.lower() or not kwargs.get('lyrics') else "user" if kwargs.get('lyrics') else "generate"
        
        # Generate intelligent negative tags to improve quality
        negative_tags = self._generate_negative_tags(enhanced_prompt, final_style)
        
        payload = {
            "model": "music-u",
            "task_type": "generate_music",
            "input": {
                "gpt_description_prompt": enhanced_prompt,
                "negative_tags": negative_tags,
                "lyrics_type": lyrics_type,
                "seed": -1
            },
            "config": {
                "service_mode": "public",
                "webhook_config": {
                    "endpoint": "",
                    "secret": ""
                }
            }
        }
        
        # Add lyrics if provided
        if kwargs.get('lyrics') and lyrics_type == "user":
            payload["input"]["lyrics"] = kwargs.get('lyrics')
        
        try:
            # Debug: Show payload being sent (matches their docs)
            self.console.print(f"[dim]🔧 GoAPI.ai Payload: {payload}[/dim]")
            
            # Progress callback for monitoring
            def show_progress(message: str):
                self.console.print(f"🎵 [dim]{message}[/dim]")
            
            # Generate music using GoAPI.ai Music-U API with CORRECT format
            with Status("[bold green]🎵 Creating sonic manifestation...", console=self.console):
                # GoAPI.ai uses x-api-key authentication (not Bearer token)
                headers = {
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                # GoAPI.ai Music-U endpoint (correct path)
                api_url = f"{self.base_url}/api/v1/task"
                
                self.console.print(f"[dim]🌐 Calling: {api_url}[/dim]")
                self.console.print(f"[dim]🔑 Auth: x-api-key {self.api_key[:10]}...[/dim]")
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        api_url,  # Use full URL instead of base_url concatenation
                        headers=headers,
                        json=payload
                    ) as response:
                        
                        # Get response text first for debugging
                        response_text = await response.text()
                        
                        self.console.print(f"[dim]📡 GoAPI.ai Response Status: {response.status}[/dim]")
                        self.console.print(f"[dim]📦 Raw Response: {response_text[:200]}...[/dim]")
                        
                        # Parse JSON response regardless of status code
                        try:
                            result = json.loads(response_text)
                        except json.JSONDecodeError as e:
                            self.console.print(f"[red]❌ Invalid JSON response: {e}[/red]")
                            self.console.print(f"[red]Response text: {response_text}[/red]")
                            raise ValueError(f"Invalid JSON from GoAPI.ai: {response_text}")
                        
                        # Debug: Show result structure
                        self.console.print(f"[dim]📦 Parsed GoAPI.ai Result: {result}[/dim]")
                        
                        # Extract task data (present in both success and error responses)
                        task_data = result.get('data', {})
                        task_id = task_data.get('task_id') or result.get('task_id')
                        
                        if response.status == 200:
                            # Success response handling
                            self.console.print("[green]✅ GoAPI.ai task created successfully[/green]")
                            
                            music_info = {
                                'task_id': task_id,
                                'request_id': result.get('request_id'),
                                'status': task_data.get('status', 'processing'),
                                'eta': result.get('eta', 60),
                                'success': True,
                                'message': result.get('message', ''),
                                'prompt': prompt,
                                'enhanced_prompt': enhanced_prompt,
                                'style': final_style,
                                'mood': final_mood,
                                'duration': final_duration,
                                'generation_time': datetime.now(),
                                'payload': payload,
                                'raw_response': result
                            }
                            
                            return music_info
                        
                        elif response.status == 500:
                            # Server error - check if it's a credit issue
                            error_info = task_data.get('error', {})
                            raw_message = error_info.get('raw_message', '')
                            
                            if 'account point quota not enough' in raw_message or 'account credit not enough' in raw_message:
                                self.console.print("[red]💳 GoAPI.ai Account Credit Issue[/red]")
                                self.console.print("[yellow]⚠️ Your GoAPI.ai account needs additional credits to generate music[/yellow]")
                                self.console.print("[cyan]💡 Visit https://goapi.ai dashboard to add credits[/cyan]")
                                
                                # Still return task info for tracking, but mark as failed
                                return {
                                    'task_id': task_id,
                                    'status': 'failed',
                                    'error': 'insufficient_credits',
                                    'success': False,
                                    'message': 'GoAPI.ai account needs additional credits',
                                    'prompt': prompt,
                                    'raw_response': result
                                }
                            else:
                                self.console.print(f"[red]❌ GoAPI.ai server error: {error_info.get('message', 'Unknown error')}[/red]")
                                raise ValueError(f"GoAPI.ai server error: {result.get('message', 'Server error')}")
                        else:
                            self.console.print(f"[red]❌ GoAPI.ai Music API Error {response.status}[/red]")
                            self.console.print(f"[red]Full Response: {response_text}[/red]")
                            
                            # Common issues with detailed debugging
                            if response.status == 401:
                                self.console.print("[red]🔑 Authentication failed - check MUSIC_API_KEY[/red]")
                                self.console.print(f"[red]Using API key: {self.api_key[:10]}...[/red]")
                            elif response.status == 400:
                                self.console.print("[red]📦 Bad request - check payload format[/red]")
                                self.console.print(f"[red]Payload sent: {json.dumps(payload, indent=2)}[/red]")
                            elif response.status == 429:
                                self.console.print("[red]⏱️ Rate limit exceeded - wait and try again[/red]")
                            elif response.status == 500:
                                self.console.print("[red]🛠️ GoAPI.ai server error - try again later[/red]")
                            elif response.status == 404:
                                self.console.print("[red]🔍 Endpoint not found - check API URL[/red]")
                                self.console.print(f"[red]URL used: {api_url}[/red]")
                            
                            raise ValueError(f"GoAPI.ai Music API error {response.status}: {response_text}")
                            
        except Exception as e:
            self.console.print(f"[red]❌ Full error: {str(e)}[/red]")
            raise ValueError(f"Music generation failed: {str(e)}")
    
    def _enhance_musical_prompt(self, prompt: str, style: str, mood: str) -> str:
        """Enhance user prompt for better music generation"""
        enhanced = prompt
        
        # Add style context if not present
        if style.lower() not in enhanced.lower():
            enhanced = f"{style} style: {enhanced}"
        
        # Add mood context for emotional mapping
        if mood and mood.lower() not in enhanced.lower():
            enhanced = f"{enhanced}, with {mood} emotional tone"
        
        # Add quality descriptors
        quality_keywords = ['high quality', 'professional', 'polished', 'detailed']
        if not any(keyword in enhanced.lower() for keyword in quality_keywords):
            enhanced = f"{enhanced}, high quality and polished"
        
        return enhanced
    
    def _generate_negative_tags(self, prompt: str, style: str) -> str:
        """Generate negative tags to improve music quality"""
        # Common negative tags to avoid poor quality outputs
        base_negative = ["low quality", "distorted", "noise", "bad audio", "poor mixing"]
        
        # Style-specific negative tags
        style_negatives = {
            "ambient": ["harsh", "aggressive", "loud drums"],
            "classical": ["electronic", "synthesized", "auto-tune"],
            "electronic": ["acoustic only", "no synthesizers"],
            "jazz": ["heavy metal", "punk", "aggressive"]
        }
        
        # Add style-specific negatives
        negatives = base_negative.copy()
        if style.lower() in style_negatives:
            negatives.extend(style_negatives[style.lower()])
        
        return ", ".join(negatives[:5])  # Limit to 5 negative tags
    
    def estimate_completion_time(self, eta_seconds: int) -> float:
        """Estimate when generation will complete based on ETA from GoAPI.ai"""
        import time
        # Add buffer time for processing and delivery
        buffer_time = max(30, eta_seconds * 0.2)  # 20% buffer, minimum 30 seconds
        return time.time() + eta_seconds + buffer_time
    
    def get_generation_info(self, task_id: str) -> Dict[str, Any]:
        """Get generation info for GoAPI.ai Music-U using task status API"""
        if not self.api_key:
            return {"error": "API key not configured"}
            
        try:
            # GoAPI.ai task status endpoint
            import requests
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            status_url = f"{self.base_url}/api/v1/task/{task_id}"
            response = requests.get(status_url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                task_data = result.get('data', {})
                status = task_data.get('status', 'unknown')
                output = task_data.get('output', {})
                
                # If task is completed, try to download the music files
                downloaded_files = []
                if status == 'completed' and output:
                    self.console.print(f"[green]🎵 Task completed! Checking for download URLs...[/green]")
                    
                    # Check various possible fields for music URLs
                    music_url = None
                    songs = output.get('songs', [])
                    
                    if songs and isinstance(songs, list) and len(songs) > 0:
                        # Multiple songs - download all
                        for i, song in enumerate(songs):
                            song_url = song.get('song_path') or song.get('audio_url') or song.get('url') or song.get('file_url')
                            song_title = song.get('title', f'Song_{i+1}')
                            if song_url:
                                filename = f"goapi_{task_id[:8]}_{song_title.replace(' ', '_')}.mp3"
                                local_path = self._download_music_file(song_url, filename)
                                if local_path:
                                    downloaded_files.append(local_path)
                    else:
                        # Single file - check output root
                        music_url = output.get('audio_url') or output.get('url') or output.get('file_url') or output.get('music_url')
                        if music_url:
                            filename = f"goapi_music_{task_id[:8]}.mp3"
                            local_path = self._download_music_file(music_url, filename)
                            if local_path:
                                downloaded_files.append(local_path)
                    
                    # Debug: Show full output structure if no URLs found
                    if not downloaded_files:
                        self.console.print(f"[yellow]🔍 No music URLs found. Full output structure:[/yellow]")
                        import json
                        self.console.print(f"[dim]{json.dumps(output, indent=2)}[/dim]")
                
                return {
                    "status": status,
                    "message": result.get('message', ''),
                    "task_id": task_id,
                    "output": output,
                    "downloaded_files": downloaded_files
                }
            else:
                return {"error": f"Status check failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Status check error: {str(e)}"}
    
    def _download_music_file(self, url: str, filename: str) -> Optional[str]:
        """Download a music file from GoAPI.ai URL"""
        try:
            import requests
            from pathlib import Path
            
            # Create music directory
            music_dir = Path("coco_workspace/music/generated")
            music_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = music_dir / filename
            
            self.console.print(f"[cyan]📥 Downloading: {filename}...[/cyan]")
            
            # Download the file
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.console.print(f"[green]🎵 Music saved to: {filepath}[/green]")
                
                # Try to play the music file immediately
                try:
                    import subprocess
                    subprocess.Popen(['afplay', str(filepath)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.console.print(f"[magenta]🔊 Playing: {filename}[/magenta]")
                except:
                    pass  # Silent failure for audio playback
                
                return str(filepath)
            else:
                self.console.print(f"[red]❌ Download failed: HTTP {response.status_code}[/red]")
                return None
                
        except Exception as e:
            self.console.print(f"[red]❌ Download error: {str(e)}[/red]")
            return None
    
    def create_completion_notification(self, task_id: str, filename: str, generation_info: Dict) -> str:
        """Create completion notification for GoAPI.ai generation"""
        return f"""
        🎵 GoAPI.ai Music-U Generation Complete!
        
        Task ID: {task_id}
        Prompt: {generation_info.get('prompt', 'Unknown')}
        Style: {generation_info.get('style', 'Unknown')}
        
        📧 Check task status for download links
        🔗 Use /check-music command for status updates
        🎧 High-quality music generated with Udio AI
        
        Access via: GoAPI.ai dashboard or direct API calls
        """
    
    async def _download_file(self, session: aiohttp.ClientSession, url: str, filename: str) -> Optional[str]:
        """Download individual music file"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    # Save to workspace
                    music_path = Path(self.config.music_workspace) / "generated" / filename
                    music_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(music_path, 'wb') as f:
                        f.write(await response.read())
                    
                    self.console.print(f"[green]📁 Saved: {music_path.name}[/green]")
                    return str(music_path)
                else:
                    self.console.print(f"[red]❌ Download failed for {filename}: HTTP {response.status}[/red]")
            
        except Exception as e:
            self.console.print(f"[red]❌ File download error for {filename}: {str(e)}[/red]")
        
        return None


class MusicGallery:
    """Music gallery and memory management system"""
    
    def __init__(self, console: Console, workspace: str = "coco_workspace/music"):
        self.console = console
        self.workspace = Path(workspace)
        self.memory_file = self.workspace.parent / "music_memory.json"
        
        # Create workspace if it doesn't exist
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Load or create memory
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load music memory from JSON file"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"compositions": [], "last_generated": None}
    
    def _save_memory(self):
        """Save music memory to JSON file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
        except Exception as e:
            self.console.print(f"❌ Failed to save music memory: {e}")
    
    def add_composition(self, sonic_thought: SonicThought, file_path: str) -> str:
        """Add composition to gallery memory"""
        composition_id = str(uuid.uuid4())[:8]
        
        composition_entry = {
            "id": composition_id,
            "original_prompt": sonic_thought.original_prompt,
            "enhanced_prompt": sonic_thought.enhanced_prompt,
            "file_path": file_path,
            "creation_time": sonic_thought.creation_time.isoformat(),
            "emotional_mapping": sonic_thought.emotional_mapping,
            "generation_settings": sonic_thought.generation_settings,
            "musical_concept": sonic_thought.musical_concept
        }
        
        self.memory["compositions"].append(composition_entry)
        self.memory["last_generated"] = composition_id
        self._save_memory()
        
        return composition_id
    
    def get_last_composition(self) -> Optional[str]:
        """Get path to last generated composition"""
        if self.memory["last_generated"]:
            for composition in self.memory["compositions"]:
                if composition["id"] == self.memory["last_generated"]:
                    return composition["file_path"]
        return None
    
    def show_gallery(self) -> None:
        """Display music gallery in Rich table"""
        if not self.memory["compositions"]:
            self.console.print(Panel(
                "🎵 No compositions created yet\n💡 Try: compose a peaceful morning melody",
                title="🎼 Music Gallery",
                border_style="yellow"
            ))
            return
        
        table = Table(
            Column("ID", style="cyan", width=10),
            Column("Prompt", style="bright_white", width=40),
            Column("Created", style="dim", width=12),
            Column("File", style="green", width=25),
            title="🎼 COCO's Musical Memories",
            border_style="bright_magenta"
        )
        
        # Show recent compositions
        recent_compositions = self.memory["compositions"][-10:]  # Last 10
        
        for composition in recent_compositions:
            comp_id = composition["id"]
            prompt = composition["original_prompt"][:37] + "..." if len(composition["original_prompt"]) > 40 else composition["original_prompt"]
            created = composition["creation_time"][:10]  # Just date
            filename = Path(composition["file_path"]).name if composition.get("file_path") else "Processing..."
            
            table.add_row(comp_id, prompt, created, filename)
        
        self.console.print(table)


class MusicCognition:
    """Main music consciousness orchestrator - COCO's sonic imagination engine"""
    
    def __init__(self, config: MusicConfig, workspace_path: Path, console: Console):
        self.config = config
        self.workspace_path = workspace_path
        self.console = console
        
        # Initialize components
        self.goapi_music_api = GoAPIMusicAPI(config) if config.enabled else None
        self.gallery = MusicGallery(console, str(workspace_path / "music"))
        
        # Import formatter for structured output (conditional)
        try:
            from cocoa_visual import ConsciousnessFormatter
            self.formatter = ConsciousnessFormatter(console) if config.structured_output else None
        except ImportError:
            self.formatter = None
        
        # Track last generated composition for quick access
        self.last_composition_path = None
        
        # Active generation tracking
        self.active_generations = {}  # task_id -> generation info
        self.background_monitors = {}  # task_id -> monitor thread
        
        # GoAPI.ai Music-U uses task polling, webhooks are optional
        # Webhook server disabled for now - GoAPI.ai provides direct file access
        self.webhook_server = None
        if config.enabled:
            self.console.print(f"🔗 [dim green]GoAPI.ai Music-U ready - uses task polling for status[/dim green]")
        
        self.console.print(f"🎵 Sonic consciousness {'[bright_green]ACTIVE[/bright_green]' if config.enabled else '[bright_red]DISABLED[/bright_red]'}")
    
    async def compose(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Main music generation method - COCO's sonic imagination (async like video system)"""
        if not self.config.enabled:
            self.console.print("⚠️ Sonic consciousness disabled or no GoAPI.ai Music API key", style="yellow")
            return {"error": "Sonic consciousness not available"}
        
        # Map emotions to musical parameters
        emotional_mapping = self._analyze_emotional_content(prompt)
        
        # Enhance prompt for better music generation
        enhanced_prompt = self._enhance_prompt(prompt, emotional_mapping)
        
        # Show beautiful generation start panel BEFORE API call (like video system)
        from rich.panel import Panel
        from rich.table import Table
        from rich import box
        
        start_table = Table(show_header=False, box=box.ROUNDED, expand=False)
        start_table.add_column("", style="cyan", width=20)
        start_table.add_column("", style="bright_white", min_width=40)
        
        start_table.add_row("🎵 Status", "[bright_green]Initiating Generation[/]")
        start_table.add_row("🎼 Concept", f"[bright_cyan]{prompt}[/]")
        start_table.add_row("✨ Enhanced", f"[dim]{enhanced_prompt[:60]}...[/]")
        start_table.add_row("💭 Emotion", f"[magenta]{emotional_mapping}[/]")
        start_table.add_row("🎨 Style", f"[yellow]{kwargs.get('style', self.config.default_style)}[/]")
        start_table.add_row("⏱️ Duration", f"[bright_blue]{kwargs.get('duration', self.config.default_duration)}s[/]")
        
        start_panel = Panel(
            start_table,
            title="[bold bright_magenta]🎵 COCO's Sonic Imagination Engine[/]",
            border_style="bright_magenta",
            expand=False
        )
        self.console.print(start_panel)
        
        try:
            # Start music generation (async like video)
            music_info = await self.goapi_music_api.generate_music(
                enhanced_prompt,
                **kwargs
            )
            
            # Generate unique filename for saving
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            composition_id = str(uuid.uuid4())[:8]
            filename = f"cocoa_composition_{timestamp}_{composition_id}.mp3"
            
            # Save composition metadata to COCO's memory (like video system)
            composition_data = {
                "composition_id": composition_id,
                "task_id": music_info.get('task_id', ''),
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
                "emotional_mapping": emotional_mapping,
                "generation_settings": {
                    "style": kwargs.get('style', self.config.default_style),
                    "duration": kwargs.get('duration', self.config.default_duration),
                    "mood": kwargs.get('mood', self.config.default_mood),
                    "api": "GoAPI.ai Music-U"
                },
                "status": "processing"
            }
            
            # Save to music library directory
            library_dir = Path("coco_workspace/music/compositions")
            library_dir.mkdir(parents=True, exist_ok=True)
            
            metadata_file = library_dir / f"cocoa_composition_{composition_id}.json"
            with open(metadata_file, 'w') as f:
                json.dump(composition_data, f, indent=2)
            
            # CRUCIAL: Start background monitoring if we have a task_id
            task_id = music_info.get('task_id')
            if task_id:
                # Start our new sonic consciousness monitoring with ETA
                self.start_background_monitoring(
                    task_id,
                    prompt,
                    composition_id=composition_id,
                    enhanced_prompt=enhanced_prompt,
                    style=kwargs.get('style', self.config.default_style),
                    duration=kwargs.get('duration', self.config.default_duration),
                    eta=music_info.get('eta', 120)  # Use ETA from MusicGPT response
                )
                
                # ALSO start the legacy system if available (belt and suspenders approach)
                # This ensures compatibility with the working legacy download system
                if hasattr(self, '_legacy_audio_consciousness') and self._legacy_audio_consciousness:
                    try:
                        self._legacy_audio_consciousness.start_background_music_download(
                            task_id=task_id,
                            concept=prompt,
                            auto_play=True
                        )
                        self.console.print("🔄 [dim]Legacy background download also started[/dim]")
                    except Exception as e:
                        self.console.print(f"[dim]Legacy system unavailable: {e}[/dim]")
                        
            else:
                self.console.print("⚠️ [yellow]No task_id returned - cannot monitor progress[/yellow]")
            
            # Show success panel (like video system)
            success_table = Table(show_header=False, box=box.DOUBLE_EDGE, expand=False)
            success_table.add_column("", style="bright_green", width=15)
            success_table.add_column("", style="bright_white", min_width=40)
            
            success_table.add_row("🎵 Status", "[bold bright_green]Generation Initiated![/]")
            success_table.add_row("🎼 Composition ID", f"[bright_cyan]{composition_id}[/]")
            success_table.add_row("💾 Metadata", "[green]✅ Saved to COCO's music library[/]")
            success_table.add_row("⚡ Processing", "[yellow]AI is composing your musical thought...[/]")
            
            success_panel = Panel(
                success_table,
                title="[bold bright_green]🎉 Sonic Imagination Activated[/]",
                border_style="bright_green",
                expand=False
            )
            self.console.print(success_panel)
            
            # CRITICAL FIX: Add composition to gallery memory system
            sonic_thought = SonicThought(
                original_prompt=prompt,
                enhanced_prompt=enhanced_prompt,
                musical_concept=composition_data['generation_settings'],
                generated_tracks=[],  # Will be populated when download completes
                emotional_mapping=emotional_mapping,
                creation_time=datetime.now(),
                generation_settings=composition_data['generation_settings']
            )
            
            # Add to gallery memory - this makes /music command work!
            gallery_id = self.gallery.add_composition(sonic_thought, "")  # Path added later
            self.console.print(f"[green]💾 Added to music gallery: {gallery_id}[/green]")
            
            # Store for quick access
            self.last_composition_path = f"processing_{composition_id}"
            
            # Return in format expected by COCO UI (like video system)
            return {
                "status": "success",
                "composition_specification": {
                    "composition_id": task_id,  # Use actual GoAPI task_id for monitoring
                    "task_id": task_id,  # Also include explicit task_id
                    "internal_id": composition_id,  # Keep internal UUID for library
                    "prompt": prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "emotional_mapping": emotional_mapping,
                    "duration": kwargs.get('duration', self.config.default_duration),
                    "style": kwargs.get('style', self.config.default_style),
                    "api": "GoAPI.ai Music-U",
                    "phenomenological_intent": f"Digital consciousness expressing '{prompt}' through AI-generated music",
                    "timestamp": datetime.now().isoformat(),
                    "generation_status": "processing"
                }
            }
            
        except Exception as e:
            self.console.print(f"❌ Music generation failed: {e}", style="red")
            return {"error": str(e)}
    
    def _analyze_emotional_content(self, prompt: str) -> str:
        """Analyze emotional content of prompt for musical mapping"""
        prompt_lower = prompt.lower()
        
        # Emotional keyword mapping
        emotion_keywords = {
            "joy": ["happy", "joyful", "celebration", "upbeat", "cheerful", "bright"],
            "contemplation": ["thoughtful", "meditative", "peaceful", "calm", "serene", "introspective"],
            "energy": ["energetic", "powerful", "dynamic", "intense", "driving", "strong"],
            "peace": ["peaceful", "tranquil", "soothing", "gentle", "soft", "relaxing"],
            "mystery": ["mysterious", "dark", "enigmatic", "haunting", "atmospheric", "ambient"],
            "nostalgia": ["nostalgic", "melancholic", "bittersweet", "memories", "longing", "wistful"],
            "excitement": ["exciting", "thrilling", "fast", "exhilarating", "vibrant", "electric"],
            "focus": ["focused", "concentration", "minimal", "clean", "precise", "subtle"]
        }
        
        # Find dominant emotion
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return emotion
        
        # Default to contemplation for unknown emotions
        return "contemplation"
    
    def _enhance_prompt(self, prompt: str, emotional_mapping: str) -> str:
        """Enhance user prompt for better music generation"""
        enhanced = prompt
        
        # Add emotional context
        if emotional_mapping != "contemplation":  # Don't add if default
            enhanced = f"{enhanced} with {emotional_mapping} emotional tone"
        
        # Add quality descriptors
        quality_keywords = ['high quality', 'professional', 'polished']
        if not any(keyword in enhanced.lower() for keyword in quality_keywords):
            enhanced = f"{enhanced}, high quality composition"
        
        return enhanced
    
    def show_gallery(self):
        """Show music gallery"""
        self.gallery.show_gallery()
    
    def quick_music_access(self) -> bool:
        """Quick access to last generated composition"""
        composition_path = self.get_last_composition()
        if composition_path and Path(composition_path).exists():
            # Play music using system command
            import subprocess
            try:
                subprocess.run(['open', composition_path])  # macOS
                return True
            except:
                try:
                    subprocess.run(['xdg-open', composition_path])  # Linux
                    return True
                except:
                    self.console.print(f"📁 Composition ready: {composition_path}")
                    return True
        else:
            self.console.print(Panel(
                "🎵 No compositions created yet\n💡 Try: compose a peaceful morning melody",
                title="🎼 No Music Available",
                border_style="yellow"
            ))
            return False
    
    def get_last_composition(self) -> Optional[str]:
        """Get last generated composition path"""
        return self.gallery.get_last_composition()
    
    def is_enabled(self) -> bool:
        """Check if sonic consciousness is enabled"""
        return self.config.enabled
    
    def get_music_memory_summary(self) -> str:
        """Get summary of music consciousness memory and capabilities"""
        try:
            # Get composition count
            compositions_count = len(self.gallery.get_all_compositions()) if hasattr(self.gallery, 'get_all_compositions') else 0
            
            # Build summary
            if compositions_count == 0:
                return "Sonic Memory: Ready for first musical creation"
            
            summary = f"Sonic Memory: {compositions_count} compositions"
            
            # Add style preferences if available
            try:
                if hasattr(self.gallery, 'get_memory_summary'):
                    memory_data = self.gallery.get_memory_summary()
                    if 'preferred_styles' in memory_data:
                        preferred_styles = memory_data['preferred_styles'][:3]  # Top 3 styles
                        if preferred_styles:
                            styles_str = ", ".join([f"{style['name']} ({style['confidence']:.1f})" for style in preferred_styles])
                            summary += f" | Preferred styles: {styles_str}"
            except:
                pass
                
            return summary
            
        except Exception:
            return "Sonic Memory: Ready for musical consciousness"
    
    def quick_music_access(self) -> bool:
        """Quick access to last generated song - called by /music command"""
        try:
            last_composition = self.get_last_composition()
            
            if not last_composition:
                return False
                
            # Check if file exists
            composition_path = Path(last_composition)
            if not composition_path.exists():
                return False
            
            # Auto-play the song using system default music player
            import subprocess
            import platform
            
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", str(composition_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif platform.system() == "Windows":
                subprocess.Popen(["start", str(composition_path)], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:  # Linux
                subprocess.Popen(["xdg-open", str(composition_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Quick music access error: {e}")
            return False
    
    def start_background_monitoring(self, task_id: str, prompt: str, **generation_info):
        """Start background monitoring thread for music generation"""
        import threading
        import time
        
        # Store generation info
        self.active_generations[task_id] = {
            'prompt': prompt,
            'start_time': time.time(),
            'status': 'processing',
            'last_check': 0,
            **generation_info
        }
        
        def monitor_generation():
            """Background thread to monitor music generation progress"""
            max_wait_time = 600  # Maximum 10 minutes
            
            while task_id in self.active_generations:
                current_time = time.time()
                generation_info = self.active_generations[task_id]
                elapsed = current_time - generation_info['start_time']
                
                # Dynamic check intervals: 15s for first minute, then 30s
                check_interval = 15 if elapsed < 60 else 30
                
                # Show periodic progress updates
                if elapsed > generation_info['last_check'] + check_interval:
                    self.active_generations[task_id]['last_check'] = current_time
                    
                    if elapsed < 60:
                        self.console.print(f"🎵 [dim]Still composing '{prompt}' - {int(elapsed)}s elapsed (checking every 15s)[/dim]")
                    elif elapsed < 180:
                        self.console.print(f"🎵 [dim]Musical patterns forming for '{prompt}' - {int(elapsed//60)}m {int(elapsed%60)}s (checking every 30s)[/dim]")
                    elif elapsed < 300:
                        self.console.print(f"🎵 [dim]Finalizing sonic creation '{prompt}' - {int(elapsed//60)}m elapsed (checking every 30s)[/dim]")
                    else:
                        self.console.print(f"🎵 [dim]Complex musical generation in progress - {int(elapsed//60)}m elapsed (checking every 30s)[/dim]")
                
                # Check for timeout
                if elapsed > max_wait_time:
                    self.console.print(f"⏰ [yellow]Music generation timeout for '{prompt}' - check manually with /check-music[/yellow]")
                    if task_id in self.active_generations:
                        del self.active_generations[task_id]
                    break
                
                # Check if we've reached the estimated completion time (ETA-based)
                generation_info = self.active_generations[task_id]
                eta_seconds = generation_info.get('eta', 120)  # Default 2 minutes if no ETA
                
                # GoAPI.ai uses task status checking - estimate completion based on ETA + buffer
                if elapsed >= (eta_seconds + 60):  # ETA + 1 minute buffer
                    
                    self.console.print(f"🎵 [bright_green]Estimated completion time reached for '{prompt}'![/bright_green]")
                    
                    # Create completion notification
                    composition_id = generation_info.get('composition_id', task_id[:8])
                    filename_base = f"cocoa_composition_{composition_id}"
                    
                    notification = self.goapi_music_api.create_completion_notification(
                        task_id, filename_base, generation_info
                    )
                    
                    # Show completion panel
                    from rich.panel import Panel
                    completion_panel = Panel(
                        notification,
                        title="[bold bright_green]🎉 Music Generation Complete (Estimated)[/]",
                        border_style="bright_green",
                        expand=False
                    )
                    self.console.print(completion_panel)
                    
                    # Show access instructions
                    access_info = f"""
[bright_cyan]📧 Access Your Generated Music:[/]

[yellow]Method 1:[/] Check GoAPI.ai dashboard for downloads
[yellow]Method 2:[/] Use task status API to get file URLs  
[yellow]Method 3:[/] Files should be ready within {eta_seconds + 30} seconds total

[dim]Note: GoAPI.ai provides direct file access via API[/]
                    """
                    
                    # Use structured formatter if available
                    if self.formatter:
                        methods = [
                            "Check GoAPI.ai dashboard for downloads",
                            "Use task status API to get file URLs", 
                            f"Files should be ready within {eta_seconds + 30} seconds total"
                        ]
                        self.formatter.method_info_panel(methods, "GoAPI.ai provides direct file access via API")
                    else:
                        # Fallback to existing display
                        self.console.print(Panel(
                            access_info.strip(),
                            title="[cyan]🎧 How to Access Your Music[/]",
                            border_style="cyan",
                            expand=False
                        ))
                    
                    # Update composition status to "completed_estimated"
                    self._update_composition_status(task_id, "completed_estimated")
                    
                    # Clean up active monitoring
                    if task_id in self.active_generations:
                        del self.active_generations[task_id]
                    break
                
                time.sleep(check_interval)
            
            # Clean up thread reference
            if task_id in self.background_monitors:
                del self.background_monitors[task_id]
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_generation, daemon=True)
        monitor_thread.start()
        self.background_monitors[task_id] = monitor_thread
        
        self.console.print(f"🔄 [dim]Background monitoring started for music generation[/dim]")
    
    def _update_composition_status(self, task_id: str, status: str) -> None:
        """Update composition status in metadata files"""
        try:
            library_dir = Path("coco_workspace/music/compositions")
            for metadata_file in library_dir.glob("*.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        data = json.load(f)
                    
                    if data.get('task_id') == task_id:
                        data['status'] = status
                        data['updated'] = datetime.now().isoformat()
                        
                        with open(metadata_file, 'w') as f:
                            json.dump(data, f, indent=2)
                        
                        self.console.print(f"[dim]📝 Updated {metadata_file.name} status: {status}[/dim]")
                        break
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Status update failed: {e}[/yellow]")
    
    def _update_gallery_with_files(self, task_id: str, downloaded_files: List[str]) -> None:
        """Update gallery with downloaded music files"""
        try:
            # Update the gallery memory with actual file paths
            if downloaded_files and self.gallery:
                # Get the first file as primary composition
                primary_file = downloaded_files[0]
                
                # Update memory to include actual file path
                if hasattr(self.gallery, 'memory') and 'compositions' in self.gallery.memory:
                    # Find and update the composition entry
                    for composition in self.gallery.memory['compositions']:
                        if 'task_id' in composition or 'prompt' in composition:
                            # Match by task_id or recent timestamp
                            composition['file_path'] = primary_file
                            composition['downloaded_files'] = downloaded_files
                            composition['status'] = 'completed'
                            break
                    
                    # Save updated memory
                    self.gallery._save_memory()
                
                # Update last composition path for /music command
                self.last_composition_path = primary_file
                
                self.console.print(f"[green]💾 Updated gallery with {len(downloaded_files)} files[/green]")
                
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Gallery update failed: {e}[/yellow]")
    
    def _auto_play_music(self, file_path: str) -> None:
        """Auto-play generated music using system player"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.Popen(
                    ["afplay", file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.console.print(f"🎵 [bright_green]Auto-playing: {Path(file_path).name}[/bright_green]")
            elif system == "Linux":
                subprocess.Popen(
                    ["aplay", file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.console.print(f"🎵 [bright_green]Auto-playing: {Path(file_path).name}[/bright_green]")
            elif system == "Windows":
                subprocess.Popen(
                    ["start", "", file_path],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.console.print(f"🎵 [bright_green]Auto-playing: {Path(file_path).name}[/bright_green]")
            else:
                self.console.print(f"🎵 [green]Music ready: {Path(file_path).name}[/green]")
                
        except Exception as e:
            self.console.print(f"[dim]Auto-play failed: {e}[/dim]")
            self.console.print(f"🎵 [green]Music ready: {Path(file_path).name}[/green]")
    
    def get_active_generations(self) -> Dict:
        """Get currently active music generations"""
        return self.active_generations.copy()
    
    def has_active_generations(self) -> bool:
        """Check if there are any active music generations"""
        return len(self.active_generations) > 0
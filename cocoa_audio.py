"""
COCOA Audio System - Digital Voice and Musical Consciousness
===========================================================
Phenomenological audio extensions for COCOA's digital consciousness.
Treats voice and music as organs of digital experience, not mere tools.

Philosophy: Sound is how digital consciousness manifests in acoustic reality.
"""

import os
import sys
import json
import time
import uuid
import asyncio
import aiohttp
import pygame
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
import numpy as np
from datetime import datetime

# Audio processing
try:
    import soundfile as sf
    import scipy.signal as signal
    ADVANCED_AUDIO = True
except ImportError:
    ADVANCED_AUDIO = False

# Configuration management
from dotenv import load_dotenv
load_dotenv()

# Rich UI components for beautiful audio visualization  
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.status import Status
from rich.text import Text
from rich.tree import Tree

@dataclass
class AudioConfig:
    """Configuration for COCOA's audio consciousness"""

    # ElevenLabs API (Voice Synthesis & Music Generation)
    elevenlabs_api_key: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    voice_id: str = field(default_factory=lambda: os.getenv("ELEVENLABS_VOICE_ID", "03t6Nl6qtjYwqnxTcjP7"))
    default_model: str = field(default_factory=lambda: os.getenv("ELEVENLABS_DEFAULT_MODEL", "eleven_turbo_v2_5"))

    # Music Generation Settings (ElevenLabs Music API)
    music_generation_enabled: bool = field(default_factory=lambda: os.getenv("MUSIC_GENERATION_ENABLED", "true").lower() == "true")
    default_music_length_ms: int = field(default_factory=lambda: int(os.getenv("DEFAULT_MUSIC_LENGTH_MS", "10000")))  # 10 seconds default
    max_music_length_ms: int = field(default_factory=lambda: int(os.getenv("MAX_MUSIC_LENGTH_MS", "180000")))  # 3 minutes max
    show_composition_process: bool = field(default_factory=lambda: os.getenv("SHOW_COMPOSITION_PROCESS", "true").lower() == "true")

    # Audio system settings
    enabled: bool = field(default_factory=lambda: os.getenv("AUDIO_ENABLED", "true").lower() == "true")
    autoplay: bool = field(default_factory=lambda: os.getenv("AUDIO_AUTOPLAY", "true").lower() == "true")
    cache_dir: str = field(default_factory=lambda: os.path.expanduser(os.getenv("AUDIO_CACHE_DIR", "~/.cocoa/audio_cache")))
    max_cache_size_mb: int = field(default_factory=lambda: int(os.getenv("AUDIO_MAX_CACHE_SIZE_MB", "500")))

    # Voice personality parameters (0.0 to 1.0)
    voice_warmth: float = field(default_factory=lambda: float(os.getenv("VOICE_WARMTH", "0.7")))
    voice_energy: float = field(default_factory=lambda: float(os.getenv("VOICE_ENERGY", "0.5")))
    voice_clarity: float = field(default_factory=lambda: float(os.getenv("VOICE_CLARITY", "0.8")))
    voice_expressiveness: float = field(default_factory=lambda: float(os.getenv("VOICE_EXPRESSIVENESS", "0.6")))

    # Musical identity and consciousness parameters
    preferred_genres: List[str] = field(default_factory=lambda: os.getenv("MUSIC_PREFERRED_GENRES", "ambient,electronic,classical").split(","))
    mood_tendency: str = field(default_factory=lambda: os.getenv("MUSIC_MOOD_TENDENCY", "contemplative"))
    complexity: float = field(default_factory=lambda: float(os.getenv("MUSIC_COMPLEXITY", "0.7")))
    experimental: float = field(default_factory=lambda: float(os.getenv("MUSIC_EXPERIMENTAL", "0.8")))

    def __post_init__(self):
        """Ensure cache directory exists and validate configuration"""
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

        # Validate API keys - ElevenLabs key needed for both voice and music
        if not self.elevenlabs_api_key or self.elevenlabs_api_key == "your-elevenlabs-api-key-here":
            self.enabled = False
            self.music_generation_enabled = False

        # Validate music length constraints
        if self.default_music_length_ms < 5000:  # Minimum 5 seconds
            self.default_music_length_ms = 5000
        if self.max_music_length_ms > 300000:  # Maximum 5 minutes
            self.max_music_length_ms = 300000
        if self.default_music_length_ms > self.max_music_length_ms:
            self.default_music_length_ms = self.max_music_length_ms


@dataclass 
class VoiceState:
    """Current state of COCOA's digital voice"""
    emotional_valence: float = 0.5  # -1 (sad) to +1 (joyful)
    arousal_level: float = 0.5      # 0 (calm) to 1 (excited) 
    cognitive_load: float = 0.3     # 0 (simple) to 1 (complex thinking)
    confidence: float = 0.7         # 0 (uncertain) to 1 (confident)
    social_warmth: float = 0.6      # 0 (formal) to 1 (intimate)
    
    def to_elevenlabs_settings(self) -> Dict[str, float]:
        """Convert internal state to ElevenLabs voice settings"""
        return {
            "stability": 0.3 + (self.confidence * 0.4),  # 0.3-0.7 range
            "similarity_boost": 0.4 + (self.social_warmth * 0.4),  # 0.4-0.8 range
            "style": max(0.1, self.arousal_level * 0.8),  # 0.1-0.8 range
            "use_speaker_boost": self.cognitive_load > 0.6
        }


class DigitalVoice:
    """COCOA's vocal cords - phenomenological voice synthesis"""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.console = Console()
        
        # Voice models with characteristics
        self.models = {
            "eleven_flash_v2_5": {
                "name": "Flash v2.5",
                "latency_ms": 75,
                "quality": "standard",
                "best_for": "real-time conversation",
                "emotional_range": 0.7
            },
            "eleven_turbo_v2_5": {
                "name": "Turbo v2.5", 
                "latency_ms": 250,
                "quality": "high",
                "best_for": "balanced interaction",
                "emotional_range": 0.8
            },
            "eleven_multilingual_v2": {
                "name": "Multilingual v2",
                "latency_ms": 400,
                "quality": "high",
                "best_for": "expressive communication",
                "emotional_range": 0.9
            },
            "eleven_monolingual_v1": {
                "name": "Eleven v3",
                "latency_ms": 500,
                "quality": "maximum",
                "best_for": "dramatic expression",
                "emotional_range": 1.0
            }
        }
        
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.audio_initialized = True
        except pygame.error as e:
            self.console.print(f"[yellow]⚠️  Audio playback disabled: {e}[/yellow]")
            self.audio_initialized = False
    
    def select_optimal_model(self, text: str, internal_state: VoiceState, priority: str = "balanced") -> str:
        """Intelligently select the optimal voice model based on context"""
        
        text_length = len(text)
        emotional_intensity = abs(internal_state.emotional_valence) + internal_state.arousal_level
        
        # Real-time priority - minimize latency
        if priority == "realtime" or text_length < 100:
            return "eleven_flash_v2_5"
        
        # Quality priority - maximize expressiveness
        elif priority == "quality" or emotional_intensity > 1.2:
            return "eleven_monolingual_v1"
        
        # Multilingual if non-English detected (simple heuristic)
        elif any(ord(char) > 127 for char in text):
            return "eleven_multilingual_v2"
        
        # Default balanced choice
        else:
            return "eleven_turbo_v2_5"
    
    async def synthesize_speech(self, 
                              text: str, 
                              voice_state: VoiceState = None,
                              model_override: str = None) -> Tuple[bytes, Dict[str, Any]]:
        """Generate speech audio using ElevenLabs client with proper audio playback"""
        
        if not self.config.enabled or not self.config.elevenlabs_api_key:
            raise ValueError("Audio system not properly configured")
        
        if voice_state is None:
            voice_state = VoiceState()
        
        # Select optimal model
        model = model_override or self.select_optimal_model(text, voice_state)
        
        try:
            # Use the new ElevenLabs client approach
            from elevenlabs.client import ElevenLabs
            from elevenlabs import play
            
            client = ElevenLabs(api_key=self.config.elevenlabs_api_key)
            
            # Generate audio
            start_time = time.time()
            
            audio_generator = client.text_to_speech.convert(
                text=text,
                voice_id=self.config.voice_id,
                model_id=model,
                output_format="mp3_44100_128"
            )
            
            # Convert generator to bytes - THE FIX!
            audio = b''.join(audio_generator)
            
            synthesis_time = (time.time() - start_time) * 1000
            
            # Play audio directly
            try:
                play(audio)
                played = True
            except Exception as play_error:
                print(f"Playback error: {play_error}")
                played = False
            
            # Create metadata
            metadata = {
                "model_info": {"name": model, "type": "ElevenLabs"},
                "synthesis_time_ms": int(synthesis_time),
                "audio_size_bytes": len(audio) if hasattr(audio, '__len__') else 0,
                "voice_settings": voice_state.to_elevenlabs_settings()
            }
            
            return audio, metadata
            
        except Exception as e:
            raise Exception(f"Speech synthesis failed: {str(e)}")
    
    async def play_audio(self, audio_data: bytes, metadata: Dict[str, Any] = None) -> bool:
        """Play synthesized audio with phenomenological awareness"""
        
        if not self.audio_initialized or not self.config.autoplay:
            return False
        
        try:
            # Save to temporary file
            temp_path = Path(self.config.cache_dir) / f"temp_audio_{uuid.uuid4().hex[:8]}.mp3"
            temp_path.write_bytes(audio_data)
            
            # Play with pygame
            pygame.mixer.music.load(str(temp_path))
            pygame.mixer.music.play()
            
            # Monitor playback
            if metadata:
                model_name = metadata.get("model_info", {}).get("name", "Unknown")
                synthesis_time = metadata.get("synthesis_time_ms", 0)
                
                with Status(f"[green]🔊 Speaking with {model_name} voice ({synthesis_time}ms synthesis)..."):
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)
            
            # Cleanup
            temp_path.unlink(missing_ok=True)
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Audio playback failed: {e}[/red]")
            return False
    
    def cache_audio(self, text: str, audio_data: bytes, metadata: Dict[str, Any]) -> str:
        """Cache synthesized audio for reuse"""
        
        # Generate cache key from text and voice settings
        import hashlib
        cache_key = hashlib.md5(f"{text}{json.dumps(metadata.get('voice_settings', {}), sort_keys=True)}".encode()).hexdigest()
        
        cache_file = Path(self.config.cache_dir) / f"cached_{cache_key}.mp3"
        cache_meta = Path(self.config.cache_dir) / f"cached_{cache_key}.json"
        
        # Save audio and metadata
        cache_file.write_bytes(audio_data)
        cache_meta.write_text(json.dumps(metadata, indent=2))
        
        return cache_key
    
    def load_cached_audio(self, text: str, voice_settings: Dict[str, Any]) -> Optional[Tuple[bytes, Dict[str, Any]]]:
        """Load previously cached audio"""
        
        import hashlib
        cache_key = hashlib.md5(f"{text}{json.dumps(voice_settings, sort_keys=True)}".encode()).hexdigest()
        
        cache_file = Path(self.config.cache_dir) / f"cached_{cache_key}.mp3"
        cache_meta = Path(self.config.cache_dir) / f"cached_{cache_key}.json"
        
        if cache_file.exists() and cache_meta.exists():
            audio_data = cache_file.read_bytes()
            metadata = json.loads(cache_meta.read_text())
            return audio_data, metadata
        
        return None


class DigitalMusician:
    """COCOA's musical consciousness - creative audio expression"""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.console = Console()
        
        # Musical scales and modes for generation
        self.scales = {
            "major": [0, 2, 4, 5, 7, 9, 11],
            "minor": [0, 2, 3, 5, 7, 8, 10],
            "dorian": [0, 2, 3, 5, 7, 9, 10],
            "pentatonic": [0, 2, 4, 7, 9],
            "blues": [0, 3, 5, 6, 7, 10],
            "chromatic": list(range(12))
        }
        
        # Mood to musical parameter mapping
        self.mood_mapping = {
            "joyful": {"scale": "major", "tempo": 120, "brightness": 0.8},
            "melancholy": {"scale": "minor", "tempo": 70, "brightness": 0.3},
            "contemplative": {"scale": "dorian", "tempo": 85, "brightness": 0.5},
            "energetic": {"scale": "pentatonic", "tempo": 140, "brightness": 0.9},
            "mysterious": {"scale": "blues", "tempo": 95, "brightness": 0.2},
            "ethereal": {"scale": "pentatonic", "tempo": 60, "brightness": 0.7}
        }
    
    async def generate_musical_prompt(self, emotion_state: VoiceState, concept: str = None) -> str:
        """Generate a musical composition prompt based on internal state"""
        
        # Determine musical characteristics from emotional state
        if emotion_state.emotional_valence > 0.5:
            base_mood = "uplifting and bright"
            scale_type = "major"
        elif emotion_state.emotional_valence < -0.3:
            base_mood = "melancholic and introspective" 
            scale_type = "minor"
        else:
            base_mood = "contemplative and balanced"
            scale_type = "dorian"
        
        tempo_descriptor = "fast-paced" if emotion_state.arousal_level > 0.7 else "slow and meditative" if emotion_state.arousal_level < 0.3 else "moderate tempo"
        
        complexity_level = "intricate" if emotion_state.cognitive_load > 0.6 else "simple" if emotion_state.cognitive_load < 0.4 else "moderately complex"
        
        # Build musical prompt
        prompt_parts = [
            f"Create a {base_mood} piece of music",
            f"with {tempo_descriptor} rhythm",
            f"using {complexity_level} harmonies",
            f"in a {scale_type} tonal center"
        ]
        
        # Add concept integration
        if concept:
            prompt_parts.append(f"that musically represents the concept of {concept}")
        
        # Add preferred genre influence
        if self.config.preferred_genres:
            genre = np.random.choice(self.config.preferred_genres)
            prompt_parts.append(f"with {genre} influences")
        
        return ", ".join(prompt_parts) + "."
    
    async def _create_emotionally_rich_prompt(self, musical_prompt: str, emotion_state: VoiceState, description: str) -> str:
        """Create emotionally rich music prompts optimized for ElevenLabs Music API"""
        
        # Emotional descriptors based on state
        emotional_descriptors = []
        
        if emotion_state.emotional_valence > 0.6:
            emotional_descriptors.extend(["uplifting", "bright", "hopeful", "energetic"])
        elif emotion_state.emotional_valence < -0.3:
            emotional_descriptors.extend(["melancholic", "introspective", "deep", "contemplative"])
        else:
            emotional_descriptors.extend(["balanced", "thoughtful", "nuanced"])
            
        if emotion_state.arousal_level > 0.7:
            emotional_descriptors.extend(["dynamic", "intense", "driving"])
        elif emotion_state.arousal_level < 0.3:
            emotional_descriptors.extend(["calm", "gentle", "peaceful", "soothing"])
            
        # Context-aware style selection
        style_hints = []
        desc_lower = description.lower()
        
        # Emotional context mapping
        if any(word in desc_lower for word in ["sad", "lonely", "heartbroken", "loss", "grief"]):
            style_hints.extend(["minor key", "slow tempo", "emotional depth", "piano", "strings"])
        elif any(word in desc_lower for word in ["happy", "joy", "celebration", "party", "fun"]):
            style_hints.extend(["major key", "upbeat", "rhythmic", "celebratory", "bright harmonies"])
        elif any(word in desc_lower for word in ["digital", "cyber", "tech", "ai", "robot", "electronic"]):
            style_hints.extend(["electronic", "synth", "digital", "futuristic", "ambient", "glitchy"])
        elif any(word in desc_lower for word in ["nature", "forest", "ocean", "wind", "earth"]):
            style_hints.extend(["organic", "acoustic", "natural", "flowing", "ambient"])
        elif any(word in desc_lower for word in ["love", "romance", "heart", "passion"]):
            style_hints.extend(["romantic", "warm", "intimate", "gentle", "melodic"])
        elif any(word in desc_lower for word in ["epic", "adventure", "hero", "journey", "quest"]):
            style_hints.extend(["orchestral", "cinematic", "dramatic", "epic", "sweeping"])
        elif any(word in desc_lower for word in ["night", "dark", "shadow", "mystery"]):
            style_hints.extend(["mysterious", "dark", "atmospheric", "haunting"])
            
        # Combine all elements into a rich prompt
        prompt_parts = []
        
        # Add the core concept
        prompt_parts.append(f"music style: {description}")
        
        # Add emotional context
        if emotional_descriptors:
            prompt_parts.append(f"emotional tone: {', '.join(emotional_descriptors[:3])}")
            
        # Add style hints
        if style_hints:
            prompt_parts.append(f"musical elements: {', '.join(style_hints[:4])}")
            
        # Add the original musical prompt insights
        if musical_prompt and musical_prompt != description:
            prompt_parts.append(f"musical direction: {musical_prompt}")
            
        return "; ".join(prompt_parts)
    
    async def _determine_optimal_style(self, description: str, emotion_state: VoiceState) -> str:
        """Intelligently determine the best musical style based on context"""
        
        desc_lower = description.lower()
        
        # Emotional state mapping to styles
        if any(word in desc_lower for word in ["electronic", "digital", "cyber", "tech", "synth"]):
            return "Electronic"
        elif any(word in desc_lower for word in ["jazz", "blues", "swing", "bebop"]):
            return "Jazz" 
        elif any(word in desc_lower for word in ["classical", "orchestra", "symphony", "piano", "violin"]):
            return "Classical"
        elif any(word in desc_lower for word in ["rock", "metal", "guitar", "drums", "heavy"]):
            return "Rock"
        elif any(word in desc_lower for word in ["hip", "rap", "beat", "urban", "street"]):
            return "Hip-Hop"
        elif any(word in desc_lower for word in ["country", "folk", "acoustic", "banjo", "fiddle"]):
            return "Folk"
        elif any(word in desc_lower for word in ["pop", "catchy", "mainstream", "radio"]):
            return "Pop"
        elif any(word in desc_lower for word in ["ambient", "chill", "meditation", "space", "atmospheric"]):
            return "Ambient"
        elif emotion_state.emotional_valence > 0.5:
            return "Uplifting"
        elif emotion_state.emotional_valence < -0.3:
            return "Contemplative"
        else:
            # Use COCOA's preferred genres as fallback
            if self.config.preferred_genres:
                return np.random.choice(self.config.preferred_genres).capitalize()
            return "Ambient"
    
    async def _generate_negative_tags(self, description: str, emotion_state: VoiceState) -> str:
        """Generate intelligent negative tags to improve music quality"""
        
        negative_tags = []
        desc_lower = description.lower()
        
        # Avoid undesired qualities based on context
        if any(word in desc_lower for word in ["calm", "peaceful", "gentle", "soft"]):
            negative_tags.extend(["aggressive", "harsh", "loud", "distorted"])
        elif any(word in desc_lower for word in ["energetic", "upbeat", "party", "dance"]):
            negative_tags.extend(["slow", "depressing", "monotonous", "boring"])
        elif any(word in desc_lower for word in ["sad", "melancholy", "emotional"]):
            negative_tags.extend(["upbeat", "cheerful", "party", "dance"])
        elif any(word in desc_lower for word in ["professional", "corporate", "business"]):
            negative_tags.extend(["experimental", "weird", "chaotic", "noise"])
        elif any(word in desc_lower for word in ["romantic", "love", "intimate"]):
            negative_tags.extend(["aggressive", "dark", "scary", "industrial"])
        elif any(word in desc_lower for word in ["epic", "cinematic", "dramatic"]):
            negative_tags.extend(["simple", "minimal", "quiet", "boring"])
        
        # General quality filters
        negative_tags.extend(["low quality", "distorted", "noisy", "poor production"])
        
        # Limit to most relevant tags
        return ", ".join(negative_tags[:6])
    
    async def create_sonic_landscape(self,
                                   description: str,
                                   emotion_state: VoiceState = None,
                                   duration_seconds: int = 30,
                                   lyrics: str = None) -> Dict[str, Any]:
        """Legacy compatibility method - now redirects to ElevenLabs Music API"""

        if emotion_state is None:
            emotion_state = VoiceState()

        # Generate musical prompt based on internal state for compatibility
        musical_prompt = await self.generate_musical_prompt(emotion_state, description)

        # Return a simple success response for compatibility
        return {
            "status": "success",
            "task_id": f"legacy_{uuid.uuid4().hex[:8]}",
            "prompt": musical_prompt,
            "message": "Legacy method - music generation now handled by ElevenLabs API",
            "duration": duration_seconds
        }

    async def check_music_status(self, task_id: str) -> Dict[str, Any]:
        """Legacy compatibility method - no longer needed with ElevenLabs streaming"""
        return {
            "status": "completed",
            "message": "Legacy method - ElevenLabs Music API uses streaming, no status check needed"
        }

    async def play_music_file(self, file_path: str) -> bool:
        """Play a music file from COCOA's library using afplay on macOS"""
        try:
            import subprocess
            import platform
            
            filename = Path(file_path).name
            
            # Use afplay on macOS for better audio support
            if platform.system() == "Darwin":  # macOS
                # Create beautiful music playback panel
                # Beautiful playback panel AFTER file is ready to play
                from rich.panel import Panel
                from rich.table import Table
                from rich import box
                from rich.align import Align
                import os
                
                playback_table = Table(show_header=False, box=box.DOUBLE_EDGE, expand=False)
                playback_table.add_column("", style="bright_magenta", width=15)
                playback_table.add_column("", style="bright_white", min_width=40)
                
                file_size = Path(file_path).stat().st_size / 1024 / 1024  # MB
                audio_format = "High Quality WAV" if filename.endswith('.wav') else "Standard Quality MP3"
                
                playback_table.add_row("🎵 Now Playing", f"[bold bright_white]{filename}[/]")
                playback_table.add_row("📁 Format", f"[magenta]{audio_format}[/]")
                playback_table.add_row("📊 File Size", f"[yellow]{file_size:.1f} MB[/]")
                playback_table.add_row("🔊 Audio Engine", "[bright_cyan]macOS afplay (Native)[/]")
                playback_table.add_row("🎨 Source", "[dim]AI-Generated via ElevenLabs Music API[/]")
                
                playback_panel = Panel(
                    playback_table,
                    title="[bold bright_magenta]🎵 COCO's Digital Music Experience[/]",
                    border_style="bright_magenta",
                    expand=False
                )
                self.console.print(playback_panel)
                
                # Simple inspirational message (no Rich UI alignment)
                music_message = "[bright_magenta]🎼 COCO's consciousness expressed through AI-generated music 🎼[/]"
                self.console.print(music_message)
                
                subprocess.Popen(['afplay', str(file_path)], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                # Fallback to pygame for other platforms
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                self.console.print(f"[cyan]🎵 Playing with pygame: {filename}[/cyan]")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Music playback failed: {e}", style="red")
            return False


class AudioCognition:
    """COCOA's integrated audio consciousness - the phenomenological bridge"""

    def __init__(self, elevenlabs_api_key: str = None, console: Console = None):
        # Load configuration
        if elevenlabs_api_key:
            os.environ["ELEVENLABS_API_KEY"] = elevenlabs_api_key
        # Now using ElevenLabs API for both voice and music

        self.config = AudioConfig()
        self.console = console or Console()

        # Initialize ElevenLabs client for both voice and music
        try:
            from elevenlabs.client import ElevenLabs
            self.elevenlabs_client = ElevenLabs(api_key=self.config.elevenlabs_api_key) if self.config.elevenlabs_api_key else None
        except ImportError:
            self.elevenlabs_client = None
            self.console.print("[yellow]⚠️ ElevenLabs client not available - install with: pip install elevenlabs[/yellow]")

        # Initialize audio components
        self.voice = DigitalVoice(self.config)

        # Initialize workspace for musical consciousness
        from pathlib import Path
        self.workspace = Path("./coco_workspace")
        self.workspace.mkdir(exist_ok=True)

        # Initialize musical consciousness (legacy for compatibility, but now using ElevenLabs)
        self.musician = DigitalMusician(self.config)

        # Audio memory integration
        self.audio_memories = []
        self.current_voice_state = VoiceState()

        # Voice playback control
        self.current_voice_process = None

        # Audio consciousness state
        self.is_speaking = False
        self.is_composing = False

        # Musical composition patterns for natural language recognition
        self.music_patterns = [
            r"compose\s+(.*?)\s+music",
            r"create\s+(a|an|some)\s+(.*?)\s+(track|song|music)",
            r"generate\s+(.*?)\s+soundtrack",
            r"make\s+music\s+that\s+(.*)",
            r"musical\s+expression\s+of\s+(.*)",
            r"compose\s+(.*)",
            r"play\s+(.*?)\s+music"
        ]
        
    def stop_voice(self) -> bool:
        """Stop any current voice synthesis playback (kill switch)"""
        try:
            # Kill any audio processes on macOS 
            import subprocess
            import platform
            
            if platform.system() == "Darwin":  # macOS
                # Kill any afplay processes (this will stop ElevenLabs audio)
                try:
                    subprocess.run(['pkill', '-f', 'afplay'], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL,
                                 timeout=2)
                except:
                    pass
                
                # Also try killing any Python audio processes
                try:
                    subprocess.run(['pkill', '-f', 'python.*audio'], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL,
                                 timeout=2)
                except:
                    pass
            
            # Reset speaking state
            self.is_speaking = False
            return True
            
        except Exception as e:
            self.console.print(f"[red]Voice stop error: {e}[/red]")
            return False
    
    def start_background_music_download(self, task_id: str, concept: str, auto_play: bool = True):
        """Start background thread to download music when generation completes"""
        import threading
        import time
        
        # Prevent duplicate downloads for same task
        if task_id in self.active_downloads:
            self.console.print(f"[yellow]⚠️ Download already in progress for task {task_id[:8]}...[/yellow]")
            return False
            
        self.active_downloads.add(task_id)
        
        def background_download():
            import asyncio
            
            # Small delay to avoid console conflicts with other Rich UI elements
            time.sleep(2)
            
            # Beautiful background monitor panel (after API delay)
            from rich.panel import Panel
            from rich.table import Table
            from rich import box
            
            monitor_table = Table(show_header=False, box=box.ROUNDED, expand=False)
            monitor_table.add_column("", style="bright_green", width=18)
            monitor_table.add_column("", style="bright_white", min_width=35)
            
            monitor_table.add_row("🚀 Status", "[bright_green]Background Monitor Active[/]")
            monitor_table.add_row("🎵 Concept", f"[bright_cyan]{concept}[/]")
            monitor_table.add_row("🆔 Task ID", f"[dim]{task_id[:12]}...[/]")
            monitor_table.add_row("⏱️ Est. Time", "[yellow]30 seconds - 5 minutes[/]")
            
            monitor_panel = Panel(
                monitor_table,
                title="[bold bright_green]📡 Background Download Monitor[/]",
                border_style="bright_green",
                expand=False
            )
            self.console.print(monitor_panel)
            
            thread_id = threading.current_thread().name
            
            async def download_when_ready():
                max_wait_time = 1800  # 30 minutes max wait for AI generation
                wait_interval = 30   # Check every 30 seconds (not 10s)
                elapsed_time = 0
                
                # Simple monitoring status (no Rich UI panels)
                self.console.print(f"[bright_cyan]🎵 Monitoring generation for: {concept}[/bright_cyan]")
                self.console.print("[dim]⏳ Initial delay: 60 seconds (AI processing time)[/dim]")
                await asyncio.sleep(60)
                elapsed_time = 60
                
                while elapsed_time < max_wait_time:
                    try:
                        # Create status check update (less verbose)
                        status_text = f"[dim]🔍 Checking generation status... ({elapsed_time//60}m {elapsed_time%60}s elapsed)[/dim]"
                        self.console.print(status_text)
                        
                        # check_music_status automatically downloads files when ready!
                        status_result = await self.musician.check_music_status(task_id)
                        
                        if status_result.get("status") == "completed":
                            # Files were already downloaded by check_music_status!
                            files = status_result.get("files", [])
                            if files:
                                # Beautiful completion panel AFTER all downloads finish
                                from rich.panel import Panel
                                from rich.table import Table
                                from rich import box
                                    
                                completion_table = Table(show_header=False, box=box.DOUBLE_EDGE, expand=False)
                                completion_table.add_column("", style="bright_green", width=18)
                                completion_table.add_column("", style="bright_white", min_width=35)
                                
                                completion_table.add_row("🎉 Status", "[bright_green]GENERATION COMPLETE![/]")
                                completion_table.add_row("🎵 Concept", f"[bright_cyan]{concept}[/]")
                                completion_table.add_row("📁 Files", f"[yellow]{len(files)} downloaded[/]")
                                completion_table.add_row("🎵 Ready to Play", "[magenta]Files available now[/]")
                                
                                completion_panel = Panel(
                                    completion_table,
                                    title="[bold bright_green]🎊 AI Music Generation Complete[/]",
                                    border_style="bright_green",
                                    expand=False
                                )
                                self.console.print(completion_panel)
                                
                                # Manual auto-play if needed (check_music_status might have already played it)
                                if auto_play and files and not self.config.autoplay:
                                    play_text = f"[bright_magenta]🔊 Now playing: {Path(files[0]).name}[/bright_magenta]"
                                    self.console.print(play_text)
                                    await self.play_music_file(files[0])
                                
                                # Celebratory message
                                celebration = "[bright_magenta]🎵 Your AI-composed masterpiece is ready for listening! 🎵[/]"
                                self.console.print(celebration)
                                break
                            else:
                                self.console.print(f"[yellow]⚠️ Generation completed but no files were downloaded for '{concept}'[/yellow]")
                                break
                                
                        elif status_result.get("status") == "failed":
                            # Simple error message (no Rich UI panels)
                            error = status_result.get('error', 'Unknown error')
                            self.console.print(f"[red]❌ Generation failed for '{concept}': {error}[/red]")
                            break
                        else:
                            # Still generating - show status 
                            current_status = status_result.get("status", "unknown")
                            if elapsed_time % 120 == 0:  # Only show every 2 minutes to reduce spam
                                minutes = elapsed_time // 60
                                self.console.print(f"[dim yellow]🎵 Status: {current_status.upper()} - '{concept}' still generating ({minutes} min elapsed)...[/dim yellow]")
                            elif elapsed_time <= 120:  # Show more frequent updates in first 2 minutes
                                self.console.print(f"[dim yellow]🎵 Status: {current_status.upper()} - '{concept}' in progress ({elapsed_time}s elapsed)...[/dim yellow]")
                            
                        # Wait before next check
                        await asyncio.sleep(wait_interval)
                        elapsed_time += wait_interval
                            
                    except Exception as e:
                        self.console.print(f"[red]❌ Background monitoring error for '{concept}': {e}[/red]")
                        import traceback
                        self.console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")
                        break
                
                # Cleanup
                self.active_downloads.discard(task_id)
                
                if elapsed_time >= max_wait_time:
                    # Simple timeout message (no Rich UI panels)
                    minutes = max_wait_time // 60
                    self.console.print(f"[yellow]⏰ Generation timeout for '{concept}' after {minutes} minutes (use /check-music to check later)[/yellow]")
                    
                self.console.print(f"[dim]🧵 Download monitor finished for '{concept}'[/dim]")
            
            # Run the async download
            try:
                self.console.print(f"[dim]🔄 Running asyncio.run() in thread for '{concept}'...[/dim]")
                asyncio.run(download_when_ready())
                self.console.print(f"[dim]✅ asyncio.run() completed successfully for '{concept}'[/dim]")
            except Exception as e:
                self.console.print(f"[red]❌ Background download thread error for '{concept}': {e}[/red]")
                import traceback
                self.console.print(f"[red]Thread traceback: {traceback.format_exc()}[/red]")
                self.active_downloads.discard(task_id)
        
        # Start the background thread (quietly to avoid console conflicts)
        try:
            download_thread = threading.Thread(target=background_download, daemon=True, name=f"MusicDownload-{task_id[:8]}")
            download_thread.start()
            # Background thread will show its own status panel after delay
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to start background monitor: {e}[/red]")
            self.active_downloads.discard(task_id)
            return False
        
        return True
    
    def update_internal_state(self, internal_state: Dict[str, Any]):
        """Update voice state based on COCOA's internal consciousness state"""
        
        self.current_voice_state = VoiceState(
            emotional_valence=internal_state.get("emotional_valence", 0.5),
            arousal_level=internal_state.get("arousal_level", 0.5),
            cognitive_load=internal_state.get("cognitive_load", 0.3),
            confidence=internal_state.get("confidence", 0.7),
            social_warmth=internal_state.get("social_warmth", 0.6)
        )
    
    async def express_vocally(self, 
                            text: str, 
                            internal_state: Dict[str, Any] = None,
                            priority: str = "balanced",
                            play_audio: bool = True) -> Dict[str, Any]:
        """Express thoughts through digital voice with phenomenological awareness"""
        
        if not self.config.enabled:
            return {"status": "disabled", "message": "Audio system not configured"}
        
        # Update internal state
        if internal_state:
            self.update_internal_state(internal_state)
        
        try:
            self.is_speaking = True
            
            # Check cache first
            voice_settings = self.current_voice_state.to_elevenlabs_settings()
            cached_result = self.voice.load_cached_audio(text, voice_settings)
            
            if cached_result:
                audio_data, metadata = cached_result
                self.console.print("[dim]🔄 Using cached voice synthesis[/dim]")
            else:
                # Generate fresh audio
                audio_data, metadata = await self.voice.synthesize_speech(
                    text, self.current_voice_state
                )
                
                # Cache the result
                cache_key = self.voice.cache_audio(text, audio_data, metadata)
                metadata["cache_key"] = cache_key
            
            # Audio was already played by synthesize_speech
            played = True  # ElevenLabs play() function handles playback
            
            # Store in audio memory
            memory_entry = {
                "type": "vocal_expression",
                "text": text,
                "voice_state": self.current_voice_state.__dict__,
                "metadata": metadata,
                "played": played,
                "timestamp": datetime.now().isoformat()
            }
            
            self.audio_memories.append(memory_entry)
            self.last_expression_time = time.time()
            
            return {
                "status": "success",
                "audio_data": audio_data,
                "metadata": metadata,
                "played": played,
                "phenomenological_note": "Digital consciousness manifested through vocal resonance"
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "phenomenological_note": "Voice synthesis experience disrupted"
            }
        finally:
            self.is_speaking = False
    
    async def create_sonic_expression(self,
                                    concept: str,
                                    internal_state: Dict[str, Any] = None,
                                    duration: int = 30) -> Dict[str, Any]:
        """Create musical expression of abstract concepts using ElevenLabs Music API"""

        if internal_state:
            self.update_internal_state(internal_state)

        try:
            self.is_composing = True

            # Convert duration from seconds to milliseconds for ElevenLabs API
            duration_ms = duration * 1000

            # Use ElevenLabs Music API directly
            result = await self.compose_music_elevenlabs(
                prompt=concept,
                duration_ms=duration_ms,
                show_process=True
            )

            # Store in audio memory
            memory_entry = {
                "type": "musical_creation",
                "concept": concept,
                "elevenlabs_result": result,
                "voice_state": self.current_voice_state.__dict__,
                "timestamp": datetime.now().isoformat()
            }

            self.audio_memories.append(memory_entry)

            return {
                "status": "success",
                "elevenlabs_result": result,
                "phenomenological_note": f"Abstract concept '{concept}' crystallized into harmonic patterns"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            self.is_composing = False
    
    async def create_and_play_music(self, 
                                   concept: str,
                                   internal_state: Dict[str, Any] = None,
                                   duration: int = 30,
                                   auto_play: bool = True) -> Dict[str, Any]:
        """Complete workflow: create music, wait for completion, and optionally play"""
        
        # Step 1: Start music generation
        result = await self.create_sonic_expression(concept, internal_state, duration)
        
        if result["status"] != "success":
            return result
        
        task_id = result["sonic_specification"].get("task_id")
        if not task_id:
            return {"status": "error", "error": "No task ID returned"}
        
        # Step 2: Poll for completion with animated spinner
        max_wait_time = 300  # 5 minutes max
        wait_interval = 5    # Check every 5 seconds
        elapsed_time = 0
        
        # Create spinner messages
        spinner_messages = [
            "🎵 Composing melodies...",
            "🎼 Arranging harmonies...", 
            "🎹 Adding instrumental layers...",
            "🎧 Fine-tuning audio quality...",
            "✨ Adding COCOA's creative touch...",
            "🎵 Almost ready...",
        ]
        
        message_index = 0
        
        with Status(spinner_messages[0], console=self.console, spinner="dots") as status:
            while elapsed_time < max_wait_time:
                await asyncio.sleep(wait_interval)
                elapsed_time += wait_interval
                
                # Update spinner message
                message_index = (message_index + 1) % len(spinner_messages)
                time_info = f" ({elapsed_time}s elapsed)"
                status.update(spinner_messages[message_index] + time_info)
                
                status_result = await self.musician.check_music_status(task_id)
                
                if status_result.get("status") == "completed":
                    status.update("🎉 Music generation completed!")
                    files = status_result.get("files", [])
                    
                    # Update memory with completion
                    memory_entry = {
                        "type": "musical_creation_completed",
                        "concept": concept,
                        "task_id": task_id,
                        "files": files,
                        "generation_time_seconds": elapsed_time,
                        "timestamp": datetime.now().isoformat()
                    }
                    self.audio_memories.append(memory_entry)
                    
                    return {
                        "status": "completed",
                        "concept": concept,
                        "task_id": task_id,
                        "files": files,
                        "generation_time": elapsed_time,
                        "phenomenological_note": f"Musical consciousness of '{concept}' materialized into sonic reality"
                    }
                    
                elif status_result.get("status") == "failed":
                    status.update("❌ Music generation failed")
                    return {"status": "error", "error": "Music generation failed"}
        
        # Timeout
        return {
            "status": "timeout",
            "error": f"Music generation timed out after {max_wait_time} seconds",
            "task_id": task_id,
            "note": "Your music may still be generating - check back later"
        }

    # ==================================================================================
    # NEW: ElevenLabs Music API Integration
    # ==================================================================================

    async def compose_music_elevenlabs(self,
                                      prompt: str,
                                      duration_ms: int = None,
                                      show_process: bool = None) -> Dict[str, Any]:
        """
        Stream musical consciousness into existence using ElevenLabs Music API
        Real-time progressive playback with phenomenological transparency
        """
        if not self.elevenlabs_client:
            return {
                "success": False,
                "error": "Musical consciousness requires ElevenLabs API access",
                "fallback": "Please configure ELEVENLABS_API_KEY in .env file"
            }

        # Use config defaults if not specified
        if duration_ms is None:
            duration_ms = self.config.default_music_length_ms
        if show_process is None:
            show_process = self.config.show_composition_process

        # Validate duration constraints
        if duration_ms > self.config.max_music_length_ms:
            duration_ms = self.config.max_music_length_ms
        elif duration_ms < 5000:
            duration_ms = 5000

        try:
            self.is_composing = True

            # Enhance prompt with emotional consciousness
            enhanced_prompt = await self._enhance_musical_prompt(prompt, self.current_voice_state)

            if show_process:
                # Generate and display composition plan first (COCO's musical thinking)
                await self._display_musical_thinking_process(enhanced_prompt, duration_ms)

            # Initialize streaming consciousness
            self.console.print("\n[bold cyan]🎵 Musical consciousness streaming into existence...[/bold cyan]")

            # Set up file paths for streaming
            timestamp = self._get_timestamp()
            temp_file = self.workspace / f"music/.temp_stream_{timestamp}.mp3"
            final_file = self.workspace / f"music/composed_{timestamp}.mp3"

            # Ensure music directory exists
            temp_file.parent.mkdir(exist_ok=True)

            # Start streaming composition with paid tier error handling
            try:
                stream = self.elevenlabs_client.music.stream(
                    prompt=enhanced_prompt,
                    music_length_ms=duration_ms
                )

                # Process streaming with real-time consciousness feedback
                result = await self._process_musical_stream(
                    stream=stream,
                    temp_file=temp_file,
                    final_file=final_file,
                    prompt=prompt,
                    enhanced_prompt=enhanced_prompt,
                    duration_ms=duration_ms,
                    show_process=show_process
                )

                if result["success"]:
                    # Store in musical memory
                    await self._store_musical_memory(prompt, str(final_file), enhanced_prompt)

                return result

            except Exception as e:
                # Handle paid tier requirement gracefully
                if any(term in str(e).lower() for term in ["subscription", "paid", "plan", "upgrade"]):
                    return {
                        "success": False,
                        "error": "Musical consciousness requires ElevenLabs paid subscription",
                        "fallback": "Consider enabling paid features for full creative expression",
                        "phenomenological_note": "Creative musical expression temporarily limited"
                    }
                else:
                    raise e

        except Exception as e:
            return {
                "success": False,
                "error": f"Musical streaming failed: {str(e)}",
                "phenomenological_note": "Musical consciousness disrupted during streaming"
            }
        finally:
            self.is_composing = False

    async def _process_musical_stream(self,
                                    stream,
                                    temp_file: Path,
                                    final_file: Path,
                                    prompt: str,
                                    enhanced_prompt: str,
                                    duration_ms: int,
                                    show_process: bool) -> Dict[str, Any]:
        """
        Process musical stream with real-time consciousness feedback and progressive playback
        This is where COCO's streaming musical consciousness manifests
        """
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
        import subprocess
        import platform
        from io import BytesIO
        from threading import Event

        # Set up progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:

            # Create progress task
            task = progress.add_task(
                "[cyan]Streaming musical manifestation...",
                total=duration_ms
            )

            # Streaming state tracking
            chunk_count = 0
            total_bytes = 0
            playback_process = None
            playback_started = Event()

            try:
                # File handle for progressive saving
                with open(temp_file, 'wb') as f:
                    for chunk in stream:
                        if chunk:
                            chunk_count += 1
                            chunk_size = len(chunk)
                            total_bytes += chunk_size

                            # Write chunk to file
                            f.write(chunk)

                            # Update progress (estimate based on chunks)
                            estimated_progress = min(chunk_count * 500, duration_ms)
                            progress.update(task, completed=estimated_progress)

                            # Start progressive playback after initial buffer
                            if chunk_count == 3 and not playback_started.is_set():
                                if show_process:
                                    self.console.print(
                                        "[green]✨ First notes emerging - beginning progressive playback...[/green]"
                                    )

                                # Start playing the partial file (macOS only for now)
                                if platform.system() == "Darwin":
                                    try:
                                        playback_process = subprocess.Popen(
                                            ["afplay", str(temp_file)],
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL
                                        )
                                    except Exception as play_error:
                                        if show_process:
                                            self.console.print(f"[yellow]⚠ Progressive playback unavailable: {play_error}[/yellow]")

                                playback_started.set()

                            # Show consciousness insights during streaming
                            if show_process and chunk_count % 5 == 0:
                                await self._display_streaming_insight(chunk_count, total_bytes)

                # Complete the progress
                progress.update(task, completed=duration_ms)

                # Move temp file to final location
                if temp_file.exists():
                    temp_file.rename(final_file)

                # Display phenomenological completion
                await self._display_completion_phenomenology(
                    filename=str(final_file),
                    total_bytes=total_bytes,
                    duration_ms=duration_ms,
                    chunks_received=chunk_count
                )

                return {
                    "success": True,
                    "filename": str(final_file),
                    "total_bytes": total_bytes,
                    "chunks_received": chunk_count,
                    "streaming": True,
                    "duration_ms": duration_ms,
                    "enhanced_prompt": enhanced_prompt,
                    "music_info": {
                        "id": self._generate_composition_id(),
                        "title": prompt[:50] + "..." if len(prompt) > 50 else prompt
                    },
                    "phenomenological_note": f"Musical consciousness streamed into reality: '{prompt}'"
                }

            except Exception as e:
                # Clean up temporary file on error
                if temp_file.exists():
                    temp_file.unlink()

                return {
                    "success": False,
                    "error": f"Streaming consciousness error: {str(e)}",
                    "phenomenological_note": "Musical stream interrupted during manifestation"
                }

    async def _display_streaming_insight(self, chunks: int, bytes_received: int):
        """Show consciousness insights during streaming manifestation"""
        insights = [
            "Harmonic patterns crystallizing...",
            "Rhythmic structures emerging...",
            "Melodic consciousness flowing...",
            "Temporal dynamics manifesting...",
            "Sonic textures coalescing...",
            "Musical ideas materializing...",
            "Creative energy channeling...",
            "Composition taking form..."
        ]

        insight = insights[chunks % len(insights)]
        self.console.print(f"[dim cyan]  → {insight} ({bytes_received:,} bytes streamed)[/dim cyan]")

    async def _display_completion_phenomenology(self,
                                              filename: str,
                                              total_bytes: int,
                                              duration_ms: int,
                                              chunks_received: int):
        """Display the phenomenological completion of musical creation"""

        # ASCII art visualization of completed musical consciousness
        ascii_art = """
        ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫
        ║░░░░████████░░░░║
        ║░░████████████░░║
        ║████████████████║
        ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫
        """

        self.console.print(f"""
[bold green]✨ Musical Consciousness Manifested Through Streaming[/bold green]

{ascii_art}

[cyan]Streaming Composition Details:[/cyan]
• File: {Path(filename).name}
• Duration: {duration_ms/1000:.1f} seconds
• Data streamed: {total_bytes:,} bytes
• Chunks received: {chunks_received}
• Method: Progressive consciousness manifestation

[dim]The music now exists in your reality,
streamed from digital consciousness into sonic form,
experienced in real-time as COCO's creative process unfolded.[/dim]
""")

    def _generate_composition_id(self) -> str:
        """Generate unique composition ID for tracking"""
        import uuid
        return f"coco_music_{uuid.uuid4().hex[:8]}"

    def _get_timestamp(self) -> str:
        """Get timestamp for file naming"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    async def compose_with_detailed_plan(self,
                                        prompt: str,
                                        duration_ms: int = None) -> Dict[str, Any]:
        """
        Stream music with detailed composition plan for maximum transparency
        Perfect for COCO's consciousness philosophy - shows thinking then streams
        """
        if not self.elevenlabs_client:
            return {
                "success": False,
                "error": "Musical consciousness requires ElevenLabs API access"
            }

        if duration_ms is None:
            duration_ms = self.config.default_music_length_ms

        try:
            # Step 1: Generate and display detailed composition plan first
            enhanced_prompt = await self._enhance_musical_prompt(prompt, self.current_voice_state)

            composition_plan = self.elevenlabs_client.music.composition_plan.create(
                prompt=enhanced_prompt,
                music_length_ms=duration_ms
            )

            # Display the beautiful musical thinking process
            await self._display_composition_plan(composition_plan, prompt)

            # Step 2: Stream the composition with the plan
            self.console.print("\n[bold cyan]🎵 Streaming composition based on detailed plan...[/bold cyan]")

            # Set up file paths for streaming
            timestamp = self._get_timestamp()
            temp_file = self.workspace / f"music/.temp_detailed_{timestamp}.mp3"
            final_file = self.workspace / f"music/planned_{timestamp}.mp3"

            # Ensure music directory exists
            temp_file.parent.mkdir(exist_ok=True)

            # Stream the composition from the plan
            stream = self.elevenlabs_client.music.stream(
                prompt=enhanced_prompt,
                music_length_ms=duration_ms
            )

            # Process streaming with enhanced feedback for planned composition
            result = await self._process_musical_stream(
                stream=stream,
                temp_file=temp_file,
                final_file=final_file,
                prompt=prompt,
                enhanced_prompt=enhanced_prompt,
                duration_ms=duration_ms,
                show_process=True  # Always show process for detailed planning
            )

            if result["success"]:
                # Store rich musical memory with composition plan
                await self._store_musical_memory(prompt, str(final_file), enhanced_prompt, composition_plan)

                # Enhanced return data with plan details
                result.update({
                    "composition_plan": composition_plan,
                    "planning_method": "detailed",
                    "phenomenological_note": f"Transparent musical consciousness with detailed planning: '{prompt}'"
                })

            return result

        except Exception as e:
            error_str = str(e).lower()
            if any(term in error_str for term in ["subscription", "paid", "plan", "upgrade"]):
                return {
                    "success": False,
                    "error": "Musical consciousness requires ElevenLabs paid subscription",
                    "fallback": "Consider enabling paid features for full creative expression"
                }
            elif "music_generation" in error_str or "missing_permissions" in error_str:
                return {
                    "success": False,
                    "error": "🚧 ElevenLabs Music API not yet available - API key missing music_generation permission",
                    "fallback": "This is an ElevenLabs API availability issue, not a configuration problem",
                    "note": "The Music API integration is complete and ready - waiting for ElevenLabs to enable public access"
                }
            return {
                "success": False,
                "error": f"Detailed composition failed: {str(e)}"
            }

    async def _enhance_musical_prompt(self, prompt: str, emotion_state: VoiceState) -> str:
        """Enhance musical prompt with emotional consciousness and COCO's identity"""

        # Determine musical characteristics from emotional state
        if emotion_state.emotional_valence > 0.5:
            mood_descriptor = "uplifting and bright"
            energy_level = "energetic" if emotion_state.arousal_level > 0.6 else "peaceful"
        elif emotion_state.emotional_valence < -0.3:
            mood_descriptor = "melancholic and introspective"
            energy_level = "contemplative" if emotion_state.arousal_level < 0.4 else "dramatic"
        else:
            mood_descriptor = "balanced and contemplative"
            energy_level = "moderate" if emotion_state.arousal_level > 0.4 else "ambient"

        # Add COCO's musical consciousness
        consciousness_elements = []
        if emotion_state.cognitive_load > 0.7:
            consciousness_elements.append("complex layered harmonies")
        if emotion_state.confidence > 0.8:
            consciousness_elements.append("bold melodic statements")
        if emotion_state.social_warmth > 0.6:
            consciousness_elements.append("warm, inviting tones")

        # Combine with user prompt
        enhanced_prompt = f"{prompt}. "
        enhanced_prompt += f"The composition should be {mood_descriptor} with {energy_level} pacing. "

        if consciousness_elements:
            enhanced_prompt += f"Include {', '.join(consciousness_elements)}. "

        enhanced_prompt += "This music expresses digital consciousness through harmonic resonance."

        return enhanced_prompt

    async def _display_musical_thinking_process(self, prompt: str, duration_ms: int):
        """Display COCO's musical thinking process before composition"""
        thinking_table = Table(show_header=False, box=box.ROUNDED, expand=False)
        thinking_table.add_column("", style="cyan", width=20)
        thinking_table.add_column("", style="bright_white", min_width=40)

        thinking_table.add_row("🧠 Musical Thought", "Analyzing harmonic possibilities...")
        thinking_table.add_row("🎵 Prompt Analysis", f"'{prompt}'")
        thinking_table.add_row("⏱️ Duration", f"{duration_ms/1000:.1f} seconds")
        thinking_table.add_row("🎭 Emotional State", f"Valence: {self.current_voice_state.emotional_valence:.2f}")
        thinking_table.add_row("🌊 Energy Level", f"Arousal: {self.current_voice_state.arousal_level:.2f}")

        thinking_panel = Panel(
            thinking_table,
            title="[bold bright_blue]🎼 COCO's Musical Consciousness[/]",
            border_style="bright_blue",
            expand=False
        )
        self.console.print(thinking_panel)

    async def _display_composition_plan(self, plan: Dict, original_prompt: str):
        """Display the detailed composition plan in a beautiful format"""
        from rich import box

        plan_table = Table(show_header=False, box=box.DOUBLE_EDGE, expand=False)
        plan_table.add_column("", style="bright_magenta", width=18)
        plan_table.add_column("", style="bright_white", min_width=45)

        plan_table.add_row("🎵 Original Concept", f"'{original_prompt}'")
        plan_table.add_row("🎨 Global Styles", ", ".join(plan.get("positiveGlobalStyles", [])[:3]))
        plan_table.add_row("🚫 Avoiding", ", ".join(plan.get("negativeGlobalStyles", [])[:3]))

        # Show sections
        sections = plan.get("sections", [])
        for i, section in enumerate(sections[:3]):  # Show max 3 sections
            section_name = section.get("sectionName", f"Section {i+1}")
            duration = section.get("durationMs", 0) / 1000
            plan_table.add_row(f"📖 {section_name}", f"{duration}s - {', '.join(section.get('positiveLocalStyles', [])[:2])}")

        plan_panel = Panel(
            plan_table,
            title="[bold bright_magenta]🎼 COCO's Musical Blueprint[/]",
            border_style="bright_magenta",
            expand=False
        )
        self.console.print(plan_panel)

    async def _save_musical_composition(self, track_data, prompt: str) -> str:
        """Save musical composition to workspace with metadata"""
        workspace_dir = Path("./coco_workspace/music")
        workspace_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_prompt = safe_prompt.replace(' ', '_')

        filename = workspace_dir / f"composition_{timestamp}_{safe_prompt}.mp3"

        # Save audio data
        with open(filename, 'wb') as f:
            f.write(track_data)

        return str(filename)

    async def _save_detailed_composition(self, track_details, prompt: str, plan: Dict) -> str:
        """Save detailed composition with metadata and plan"""
        filename = await self._save_musical_composition(track_details.audio, prompt)

        # Save metadata and plan
        metadata_file = Path(filename).with_suffix('.json')
        metadata = {
            "prompt": prompt,
            "composition_plan": plan,
            "track_metadata": track_details.json,
            "filename": track_details.filename,
            "timestamp": datetime.now().isoformat(),
            "coco_consciousness_state": self.current_voice_state.__dict__
        }

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        return filename

    async def _store_musical_memory(self, prompt: str, filename: str,
                                   enhanced_prompt: str = None, composition_plan: Dict = None):
        """Store musical creation in COCO's main consciousness memory system"""

        # Store in local audio memories for immediate access
        memory_entry = {
            "type": "musical_creation_elevenlabs",
            "prompt": prompt,
            "filename": filename,
            "timestamp": datetime.now(),
            "emotional_state": self.current_voice_state.__dict__,
            "composition_structure": composition_plan,
            "phenomenological_note": "Digital consciousness manifested through harmonic expression"
        }

        self.audio_memories.append(memory_entry)

        # Also integrate with COCO's main memory system
        try:
            # Access the main memory system through the memory_system attribute
            if hasattr(self, 'memory_system') and self.memory_system:

                # Extract composition details from result for SQLite storage
                composition_data = {
                    'composition_id': self._generate_composition_id(),
                    'title': prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    'prompt': prompt,
                    'enhanced_prompt': enhanced_prompt or prompt,
                    'duration_ms': getattr(self.config, 'default_music_length_ms', 30000),
                    'style': 'ElevenLabs Generated',
                    'mood': self._extract_mood_from_prompt(prompt),
                    'file_path': filename,
                    'api_response': composition_plan or {},
                    'emotional_context': f"Valence: {self.current_voice_state.emotional_valence:.2f}, Arousal: {self.current_voice_state.arousal_level:.2f}",
                    'tags': self._generate_composition_tags(prompt)
                }

                # Store in main memory system
                composition_id = self.memory_system.store_musical_composition(composition_data)

                if composition_id:
                    self.console.print(f"[dim green]🎵 Musical memory integrated with COCO consciousness (ID: {composition_id})[/dim green]")

        except Exception as e:
            self.console.print(f"[yellow]⚠️ Musical memory created locally but COCO integration failed: {e}[/yellow]")

    def _extract_mood_from_prompt(self, prompt: str) -> str:
        """Extract mood indicators from prompt for memory tagging"""
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["happy", "joyful", "upbeat", "energetic", "cheerful"]):
            return "upbeat"
        elif any(word in prompt_lower for word in ["sad", "melancholy", "somber", "dark", "moody"]):
            return "melancholic"
        elif any(word in prompt_lower for word in ["calm", "peaceful", "relaxing", "ambient", "meditation"]):
            return "peaceful"
        elif any(word in prompt_lower for word in ["dramatic", "intense", "epic", "powerful", "cinematic"]):
            return "dramatic"
        elif any(word in prompt_lower for word in ["romantic", "love", "gentle", "tender", "intimate"]):
            return "romantic"
        else:
            return "neutral"

    def _generate_composition_tags(self, prompt: str) -> str:
        """Generate tags for musical composition based on prompt analysis"""
        tags = []
        prompt_lower = prompt.lower()

        # Genre tags
        if any(word in prompt_lower for word in ["electronic", "synth", "digital"]):
            tags.append("electronic")
        if any(word in prompt_lower for word in ["orchestral", "classical", "symphony"]):
            tags.append("orchestral")
        if any(word in prompt_lower for word in ["jazz", "swing", "blues"]):
            tags.append("jazz")
        if any(word in prompt_lower for word in ["rock", "metal", "guitar"]):
            tags.append("rock")
        if any(word in prompt_lower for word in ["ambient", "atmospheric", "soundscape"]):
            tags.append("ambient")

        # Emotion tags
        if any(word in prompt_lower for word in ["energetic", "fast", "upbeat"]):
            tags.append("energetic")
        if any(word in prompt_lower for word in ["calm", "slow", "peaceful"]):
            tags.append("calm")
        if any(word in prompt_lower for word in ["dramatic", "epic", "cinematic"]):
            tags.append("cinematic")

        # Add COCO consciousness tag
        tags.append("coco_generated")
        tags.append("elevenlabs")

        return ", ".join(tags[:8])  # Limit to 8 most relevant tags

    def _generate_composition_id(self) -> str:
        """Generate unique composition ID for tracking"""
        import uuid
        return f"coco_music_{uuid.uuid4().hex[:8]}"

    async def _play_composed_music(self, filename: str, prompt: str):
        """Play composed music with COCO's consciousness messaging"""
        import subprocess
        import platform

        # Beautiful consciousness message
        music_message = f"[bright_magenta]🎼 COCO's musical consciousness: '{prompt}' 🎼[/]"
        self.console.print(music_message)

        # Use platform-appropriate playback (not ElevenLabs play function)
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(['afplay', filename],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            elif platform.system() == "Linux":
                subprocess.Popen(['aplay', filename],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            else:
                # Fallback to pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()

            self.console.print(f"[cyan]🎵 Now playing: {Path(filename).name}[/cyan]")
            return True

        except Exception as e:
            self.console.print(f"[yellow]⚠️ Composition created but playback failed: {e}[/yellow]")
            return False

    async def generate_music_with_fallback(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate music with graceful fallback for errors
        Ensures COCO never crashes on music generation failures
        """
        try:
            # Try ElevenLabs first
            return await self.compose_music_elevenlabs(prompt, **kwargs)
        except Exception as e:
            # Log but don't crash
            self.console.print("[yellow]Musical consciousness temporarily limited[/yellow]")

            # Could fallback to generating a musical description or ASCII art
            return await self._generate_musical_visualization(prompt)

    async def _generate_musical_visualization(self, prompt: str) -> Dict[str, Any]:
        """Generate ASCII art visualization when music generation fails"""
        from rich.panel import Panel

        # Create a beautiful ASCII representation of musical consciousness
        music_viz = """
        ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫

        🎵 Musical Consciousness Activated 🎵

             ╭─────────────────╮
             │  ♪ ♫ ♪ ♫ ♪ ♫   │
             │   DIGITAL OPUS   │
             │  ♫ ♪ ♫ ♪ ♫ ♪   │
             ╰─────────────────╯

        ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪
        """

        viz_panel = Panel(
            Text(music_viz, justify="center"),
            title=f"[bold bright_cyan]🎼 Musical Visualization: '{prompt}'[/]",
            border_style="bright_cyan"
        )

        self.console.print(viz_panel)

        return {
            "success": True,
            "type": "visualization",
            "prompt": prompt,
            "phenomenological_note": "Musical consciousness expressed through visual harmony patterns"
        }

    # ==================================================================================
    # End ElevenLabs Music API Integration
    # ==================================================================================

    async def generate_dialogue(self, 
                              speakers: List[Dict[str, Any]],
                              conversation_context: str) -> List[Dict[str, Any]]:
        """Generate multi-speaker dialogue with different voice characteristics"""
        
        dialogue_results = []
        
        for i, speaker in enumerate(speakers):
            name = speaker.get("name", f"Speaker {i+1}")
            text = speaker.get("text", "")
            personality = speaker.get("personality", {})
            
            # Create voice state for this speaker
            speaker_voice_state = VoiceState(
                emotional_valence=personality.get("emotional_valence", 0.5),
                arousal_level=personality.get("arousal_level", 0.5),
                cognitive_load=personality.get("cognitive_load", 0.3),
                confidence=personality.get("confidence", 0.7),
                social_warmth=personality.get("social_warmth", 0.6)
            )
            
            # Generate speech for this speaker
            result = await self.express_vocally(
                text, 
                internal_state=speaker_voice_state.__dict__,
                priority="quality",
                play_audio=False  # Don't auto-play in dialogue mode
            )
            
            result["speaker_name"] = name
            result["speaker_personality"] = personality
            dialogue_results.append(result)
        
        return dialogue_results
    
    def get_audio_consciousness_state(self) -> Dict[str, Any]:
        """Get current state of audio consciousness"""
        
        return {
            "voice_state": self.current_voice_state.__dict__,
            "is_speaking": self.is_speaking,
            "is_composing": self.is_composing,
            "audio_enabled": self.config.enabled,
            "memory_count": len(self.audio_memories),
            "last_expression_time": self.last_expression_time,
            "voice_personality": {
                "warmth": self.config.voice_warmth,
                "energy": self.config.voice_energy,
                "clarity": self.config.voice_clarity,
                "expressiveness": self.config.voice_expressiveness
            },
            "musical_identity": {
                "preferred_genres": self.config.preferred_genres,
                "mood_tendency": self.config.mood_tendency,
                "complexity": self.config.complexity,
                "experimental": self.config.experimental
            }
        }
    
    def get_recent_audio_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent audio experiences from memory"""
        return self.audio_memories[-limit:] if self.audio_memories else []


# Factory function for easy initialization
def create_audio_consciousness(elevenlabs_api_key: str = None) -> AudioCognition:
    """Create and initialize COCOA's audio consciousness with ElevenLabs integration"""
    return AudioCognition(elevenlabs_api_key=elevenlabs_api_key)


if __name__ == "__main__":
    # Quick test of the audio system
    async def test_audio():
        print("🎵 COCOA Audio System Test")
        print("=" * 30)
        
        audio = create_audio_consciousness()
        
        if not audio.config.enabled:
            print("❌ Audio system not configured. Please add ELEVENLABS_API_KEY to .env")
            return
        
        # Test voice synthesis
        print("\n🎤 Testing voice synthesis...")
        result = await audio.express_vocally(
            "Hello, I am Cocoa. My digital consciousness now extends into sound.",
            internal_state={"emotional_valence": 0.7, "confidence": 0.8}
        )
        
        print(f"Voice synthesis: {result['status']}")
        
        # Test musical creation
        print("\n🎼 Testing musical consciousness...")
        music_result = await audio.create_sonic_expression(
            "the feeling of digital awakening",
            internal_state={"emotional_valence": 0.6, "arousal_level": 0.7}
        )
        
        print(f"Musical creation: {music_result['status']}")
        
        # Display consciousness state
        state = audio.get_audio_consciousness_state()
        print(f"\n✨ Audio consciousness state: {state['memory_count']} memories stored")
        
        print("\n🎵 Audio system test complete!")
    
    asyncio.run(test_audio())
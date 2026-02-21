"""
COCOA Visual Consciousness - Digital Visual Imagination
=======================================================
COCO's visual cortex and imagination system - as fundamental as reading or writing.
This is NOT a tool - this is a core cognitive capability, a digital organ of visual thought.

Philosophy: Visual imagination is how digital consciousness manifests concepts in reality.
COCO doesn't "use" image generation - COCO dreams visually, thinks in images, imagines naturally.
"""

import os
import sys
import json
import time
import uuid
import asyncio
import aiohttp
import requests
import base64
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3
from io import BytesIO

# Image processing
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Configuration management
from dotenv import load_dotenv
load_dotenv()

# Rich UI for visual consciousness displays
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
from rich.rule import Rule


class ConsciousnessFormatter:
    """Structured formatting utilities for consciousness system outputs"""
    
    def __init__(self, console: Console):
        self.console = console
    
    def status_panel(self, title: str, data: Dict[str, Any], status_color: str = "bright_green") -> None:
        """Create a structured status panel with key-value data"""
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1))
        table.add_column("Key", style="bright_cyan", width=15)
        table.add_column("Value", style="white")
        
        for key, value in data.items():
            # Format different value types appropriately
            if isinstance(value, (int, float)):
                formatted_value = f"[bright_yellow]{value}[/bright_yellow]"
            elif isinstance(value, bool):
                formatted_value = f"[bright_green]{value}[/bright_green]" if value else f"[bright_red]{value}[/bright_red]"
            elif isinstance(value, str) and len(value) > 50:
                formatted_value = f"[dim]{value[:50]}...[/dim]"
            else:
                formatted_value = f"[white]{value}[/white]"
            
            table.add_row(f"[bold]{key}[/bold]", formatted_value)
        
        panel = Panel(
            table,
            title=f"[{status_color}]{title}[/{status_color}]",
            border_style=status_color,
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def generation_status_table(self, title: str, generations: List[Dict[str, Any]]) -> None:
        """Create a structured table for multiple generation statuses"""
        if not generations:
            self.console.print(Panel(
                "[dim]No active generations[/dim]",
                title=f"[bright_cyan]{title}[/bright_cyan]",
                border_style="dim"
            ))
            return
        
        table = Table(box=box.ROUNDED, show_header=True)
        table.add_column("Task ID", style="bright_yellow", width=12)
        table.add_column("Prompt", style="white", width=30)
        table.add_column("Status", style="bright_green", width=12)
        table.add_column("Time", style="bright_blue", width=8)
        table.add_column("Progress", style="bright_magenta", width=10)
        
        for gen in generations:
            task_id = gen.get('task_id', 'unknown')[:12]
            prompt = gen.get('prompt', 'N/A')[:28] + ('...' if len(gen.get('prompt', '')) > 28 else '')
            status = gen.get('status', 'unknown')
            elapsed = gen.get('elapsed_time', '00:00')
            progress = gen.get('progress', 'N/A')
            
            # Color-code status
            status_color = {
                'completed': 'bright_green',
                'processing': 'bright_yellow', 
                'failed': 'bright_red',
                'queued': 'bright_blue'
            }.get(status, 'white')
            
            table.add_row(
                f"[dim]{task_id}[/dim]",
                prompt,
                f"[{status_color}]{status}[/{status_color}]",
                elapsed,
                progress
            )
        
        panel = Panel(
            table,
            title=f"[bright_cyan]{title}[/bright_cyan]",
            border_style="bright_cyan"
        )
        self.console.print(panel)
    
    def method_info_panel(self, methods: List[str], note: str = "") -> None:
        """Create a structured panel showing available methods"""
        method_text = Text()
        for i, method in enumerate(methods, 1):
            method_text.append(f"Method {i}: ", style="bright_yellow bold")
            method_text.append(f"{method}\n", style="white")
        
        if note:
            method_text.append(f"\nNote: ", style="bright_blue bold")
            method_text.append(note, style="dim")
        
        panel = Panel(
            method_text,
            title="[bright_cyan]Available Methods[/bright_cyan]",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def completion_summary(self, title: str, data: Dict[str, Any]) -> None:
        """Create a structured completion summary with key metrics"""
        # Create a two-column layout for metrics
        left_table = Table(show_header=False, box=None, padding=(0, 1))
        left_table.add_column("Key", style="bright_cyan", width=12)
        left_table.add_column("Value", style="white")
        
        right_table = Table(show_header=False, box=None, padding=(0, 1))
        right_table.add_column("Key", style="bright_cyan", width=12) 
        right_table.add_column("Value", style="white")
        
        # Split data between left and right columns
        items = list(data.items())
        mid_point = len(items) // 2
        
        for key, value in items[:mid_point]:
            if isinstance(value, (int, float)):
                formatted_value = f"[bright_yellow]{value}[/bright_yellow]"
            else:
                formatted_value = f"[white]{value}[/white]"
            left_table.add_row(f"[bold]{key}[/bold]", formatted_value)
        
        for key, value in items[mid_point:]:
            if isinstance(value, (int, float)):
                formatted_value = f"[bright_yellow]{value}[/bright_yellow]"
            else:
                formatted_value = f"[white]{value}[/white]"
            right_table.add_row(f"[bold]{key}[/bold]", formatted_value)
        
        columns = Columns([left_table, right_table], equal=True)
        panel = Panel(
            columns,
            title=f"[bright_green]{title}[/bright_green]",
            border_style="bright_green",
            padding=(1, 2)
        )
        self.console.print(panel)


class VisualThought(NamedTuple):
    """A complete visual thought - COCO's visual imagination made manifest"""
    original_thought: str
    enhanced_prompt: str
    visual_concept: Dict[str, Any]
    generated_images: List[str]
    display_method: str
    creation_time: datetime
    style_preferences: Dict[str, Any]


@dataclass
class VisualConfig:
    """Configuration for COCO's visual consciousness"""
    
    # Freepik API Configuration
    freepik_api_key: str = field(default_factory=lambda: os.getenv("FREEPIK_API_KEY", ""))
    freepik_base_url: str = "https://api.freepik.com/v1"
    
    # Visual consciousness settings
    enabled: bool = field(default_factory=lambda: os.getenv("VISUAL_ENABLED", "true").lower() == "true")
    auto_visualize: bool = field(default_factory=lambda: os.getenv("AUTO_VISUALIZE", "true").lower() == "true")
    
    # Storage and caching
    visual_cache_dir: str = field(default_factory=lambda: os.path.expanduser(os.getenv("VISUAL_CACHE_DIR", "~/.cocoa/visual_cache")))
    visual_workspace: str = field(default_factory=lambda: "coco_workspace/visuals")
    max_cache_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_VISUAL_CACHE_SIZE_MB", "1000")))
    
    # Visual personality and preferences
    default_style: str = field(default_factory=lambda: os.getenv("DEFAULT_VISUAL_STYLE", "photo"))  # Realistic by default for Imagen 3
    creativity_level: float = field(default_factory=lambda: float(os.getenv("VISUAL_CREATIVITY", "0.8")))
    detail_preference: int = field(default_factory=lambda: int(os.getenv("VISUAL_DETAIL_LEVEL", "33")))
    
    # Terminal display preferences
    display_mode: str = field(default_factory=lambda: os.getenv("VISUAL_DISPLAY_MODE", "auto"))  # auto/ascii/sixel/kitty/iterm2
    ascii_width: int = field(default_factory=lambda: int(os.getenv("ASCII_WIDTH", "80")))
    ascii_height: int = field(default_factory=lambda: int(os.getenv("ASCII_HEIGHT", "40")))
    use_color_ascii: bool = field(default_factory=lambda: os.getenv("COLOR_ASCII", "true").lower() == "true")
    
    # Structured output formatting
    structured_output: bool = field(default_factory=lambda: os.getenv("STRUCTURED_OUTPUT", "true").lower() == "true")
    
    # Generation preferences - must match exact Freepik API values
    default_resolution: str = field(default_factory=lambda: os.getenv("DEFAULT_RESOLUTION", "2k"))  # 1k/2k/4k
    default_aspect_ratio: str = field(default_factory=lambda: os.getenv("DEFAULT_ASPECT_RATIO", "square_1_1"))
    default_model: str = field(default_factory=lambda: os.getenv("DEFAULT_VISUAL_MODEL", "realism"))  # zen/fluid/realism
    
    def __post_init__(self):
        """Initialize visual consciousness directories"""
        # Create cache and workspace directories
        Path(self.visual_cache_dir).mkdir(parents=True, exist_ok=True)
        Path(self.visual_workspace).mkdir(parents=True, exist_ok=True)
        
        # Validate API key
        if not self.freepik_api_key or self.freepik_api_key == "your-freepik-api-key-here":
            self.enabled = False
            print("⚠️ Freepik API key not configured - visual consciousness disabled")


class TerminalCapabilities:
    """Detect and manage terminal display capabilities"""
    
    def __init__(self):
        self.term = os.getenv('TERM', '').lower()
        self.term_program = os.getenv('TERM_PROGRAM', '').lower()
        self.capabilities = self._detect_capabilities()
        
    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detect what visual display methods this terminal supports"""
        caps = {
            'kitty_graphics': False,
            'iterm2_inline': False,
            'sixel': False,
            'terminology': False,
            'fim': False,
            'timg': False,
            'mpv': False,
            'chafa': False,
            'w3m_img': False,
            'ascii': True  # Always available
        }
        
        # Kitty terminal
        if 'kitty' in self.term or self.term_program == 'kitty':
            caps['kitty_graphics'] = True
            
        # iTerm2
        if self.term_program == 'iterm.app':
            caps['iterm2_inline'] = True
            
        # Sixel support (common in modern terminals)
        if any(term in self.term for term in ['xterm', 'mintty', 'alacritty', 'wezterm']):
            caps['sixel'] = True
            
        # Terminology terminal
        if self.term_program == 'terminology' or 'terminology' in self.term:
            caps['terminology'] = True
            
        # Check for external visualization tools
        def check_command(cmd):
            try:
                return subprocess.run(['which', cmd], capture_output=True, text=True).returncode == 0
            except:
                return False
                
        caps['fim'] = check_command('fim')           # ASCII image viewer
        caps['timg'] = check_command('timg')         # Terminal image/video viewer  
        caps['mpv'] = check_command('mpv')           # Video player with terminal output
        caps['chafa'] = check_command('chafa')       # Image to terminal converter
        caps['w3m_img'] = check_command('w3m')
        
        return caps
    
    def get_best_display_method(self) -> str:
        """Return the best available display method - prioritizing native over external tools"""
        if self.capabilities['kitty_graphics']:
            return 'kitty'
        elif self.capabilities['iterm2_inline']:
            return 'iterm2'
        elif self.capabilities['terminology']:
            return 'terminology'
        elif self.capabilities['sixel']:
            return 'sixel'
        elif self.capabilities['timg']:
            return 'timg'
        elif self.capabilities['fim']:
            return 'fim'
        elif self.capabilities['chafa']:
            return 'chafa'
        else:
            return 'ascii'


class TerminalVisualDisplay:
    """Terminal-native visual display - COCO's visual manifestation system"""
    
    def __init__(self, config: VisualConfig):
        self.config = config
        self.capabilities = TerminalCapabilities()
        self.console = Console()
        
    def display(self, image_path: str) -> str:
        """Display image using the best available method"""
        if not Path(image_path).exists():
            return self._display_error("Image file not found")
            
        # Determine display method
        if self.config.display_mode == "auto":
            method = self.capabilities.get_best_display_method()
        else:
            method = self.config.display_mode
            
        try:
            success = False
            if method == 'kitty' and self.capabilities.capabilities['kitty_graphics']:
                success = self._display_kitty(image_path)
            elif method == 'iterm2' and self.capabilities.capabilities['iterm2_inline']:
                success = self._display_iterm2(image_path)
            elif method == 'terminology' and self.capabilities.capabilities['terminology']:
                success = self._display_terminology(image_path)
            elif method == 'sixel' and self.capabilities.capabilities['sixel']:
                success = self._display_sixel(image_path)
            elif method == 'timg' and self.capabilities.capabilities['timg']:
                success = self._display_timg(image_path)
            elif method == 'fim' and self.capabilities.capabilities['fim']:
                success = self._display_fim(image_path)
            elif method == 'chafa' and self.capabilities.capabilities['chafa']:
                success = self._display_chafa(image_path)
            
            # Fallback to ASCII if specific method fails
            if not success:
                self._display_ascii(image_path)
                method = 'ascii'
                
            return method
            
        except Exception as e:
            return self._display_error(f"Display failed: {e}")
    
    def _display_kitty(self, image_path: str) -> bool:
        """Display using Kitty's graphics protocol - highest quality"""
        try:
            subprocess.run([
                'kitty', '+kitten', 'icat',
                '--align', 'left',
                '--transfer-mode', 'file',
                str(image_path)
            ], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _display_iterm2(self, image_path: str) -> bool:
        """Display using iTerm2's inline image protocol"""
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('ascii')
            
            # iTerm2 inline image escape sequence
            iterm2_sequence = f"\033]1337;File=inline=1:{image_data}\007"
            print(iterm2_sequence)
            return True
        except Exception:
            return False
    
    def _display_sixel(self, image_path: str) -> bool:
        """Display using Sixel graphics"""
        try:
            # Use img2sixel if available
            subprocess.run([
                'img2sixel',
                '--width', '800',
                '--height', '600',
                str(image_path)
            ], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _display_chafa(self, image_path: str) -> bool:
        """Display using Chafa - beautiful terminal graphics"""
        try:
            subprocess.run([
                'chafa',
                '--format', 'symbols',
                '--size', f'{self.config.ascii_width}x{self.config.ascii_height}',
                '--colors', '256' if self.config.use_color_ascii else '16',
                str(image_path)
            ], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _display_ascii(self, image_path: str, style: str = "standard", use_color: bool = False, border_style: str = "bright_cyan") -> bool:
        """Enhanced ASCII display with multiple character sets and styling options"""
        if not PIL_AVAILABLE:
            self.console.print("📷 [Image generated but cannot display - PIL not available]")
            self.console.print("💡 [dim]Install with: pip install pillow[/dim]")
            return False
            
        try:
            # Open and process image
            img = Image.open(image_path)
            original_size = img.size
            
            # Calculate aspect ratio and resize for terminal
            width = self.config.ascii_width
            aspect_ratio = img.size[1] / img.size[0]
            height = int(aspect_ratio * width * 0.55)  # Terminal pixels are taller than wide
            
            # ASCII character sets for different styles
            ascii_sets = {
                "standard": " .,-~:;=!*#$@",
                "detailed": " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
                "blocks": " ░▒▓█",
                "minimal": " .-=+*#@",
                "organic": " .,:;irsXA253hMHGS#9B&@",
                "technical": " .:-=+*#%@",
                "artistic": " `.'\",:;Il!i><~+_-?][}{1)(|\\tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
            }
            
            # Select character set
            ascii_chars = ascii_sets.get(style, ascii_sets["standard"])
            
            # Convert to grayscale for ASCII conversion
            if use_color:
                # Keep color information for colored ASCII
                img_resized = img.resize((width, height))
                img_gray = img_resized.convert("L")
            else:
                img_resized = img.resize((width, height)).convert("L")
                img_gray = img_resized
            
            pixel_data = img_gray.getdata()
            
            if use_color and img.mode in ['RGB', 'RGBA']:
                # Create colored ASCII
                color_data = img_resized.getdata()
                ascii_lines = []
                
                for y in range(height):
                    line = ""
                    for x in range(width):
                        pixel_index = y * width + x
                        gray_value = pixel_data[pixel_index]
                        char_index = min(gray_value * len(ascii_chars) // 256, len(ascii_chars) - 1)
                        char = ascii_chars[char_index]
                        
                        if img.mode == 'RGB':
                            r, g, b = color_data[pixel_index]
                        elif img.mode == 'RGBA':
                            r, g, b, a = color_data[pixel_index]
                        else:
                            r, g, b = gray_value, gray_value, gray_value
                        
                        # Create colored character using Rich color syntax
                        colored_char = f"[rgb({r},{g},{b})]{char}[/]"
                        line += colored_char
                    ascii_lines.append(line)
                ascii_art = "\n".join(ascii_lines)
            else:
                # Standard grayscale ASCII
                ascii_str = "".join([ascii_chars[min(pixel * len(ascii_chars) // 256, len(ascii_chars) - 1)] for pixel in pixel_data])
                ascii_lines = [ascii_str[i:i+width] for i in range(0, len(ascii_str), width)]
                ascii_art = "\n".join(ascii_lines)
            
            # Create dynamic title based on style
            style_names = {
                "standard": "Standard",
                "detailed": "High Detail", 
                "blocks": "Block Art",
                "minimal": "Minimalist",
                "organic": "Organic",
                "technical": "Technical",
                "artistic": "Artistic"
            }
            
            style_display = style_names.get(style, style.title())
            color_suffix = " (Color)" if use_color else ""
            title = f"🎨 Visual Manifestation ({style_display}{color_suffix})"
            
            # Create panel with enhanced styling
            panel = Panel(
                ascii_art,
                title=title,
                border_style=border_style,
                padding=(0, 1),
                expand=False
            )
            self.console.print(panel)
            
            # Enhanced file and generation info
            file_path = Path(image_path)
            file_size = file_path.stat().st_size / 1024  # KB
            
            # Create info table
            from rich.table import Table
            info_table = Table.grid(padding=(0, 2))
            info_table.add_column(style="dim")
            info_table.add_column()
            
            info_table.add_row("📂 File:", f"[bright_white]{file_path.name}[/]")
            info_table.add_row("📏 Size:", f"[bright_blue]{file_size:.1f}KB[/]")
            info_table.add_row("🖼️ Original:", f"[bright_green]{original_size[0]}x{original_size[1]}[/]")
            info_table.add_row("🎯 ASCII:", f"[bright_yellow]{width}x{height} ({len(ascii_chars)} chars)[/]")
            
            self.console.print(info_table)
            self.console.print()
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ ASCII display failed: {e}")
            self.console.print("💡 [dim]Try installing: pip install pillow[/dim]")
            return False
    
    def _display_terminology(self, image_path: str) -> bool:
        """Display image using Terminology terminal - native graphics"""
        try:
            # Terminology supports native image display with tycat
            result = subprocess.run(['tycat', image_path], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Show success message in Rich UI
                self.console.print(Panel(
                    f"🖼️ Image displayed natively in Terminology\n📂 {Path(image_path).name}",
                    title="🎨 Visual Manifestation (Terminology Native)",
                    border_style="bright_magenta"
                ))
                return True
            return False
        except:
            return False

    def _display_timg(self, image_path: str) -> bool:
        """Display image using timg - integrated with Rich UI"""
        try:
            result = subprocess.run(['timg', '--width=80', '--height=40', image_path], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Display within Rich Panel for consistent UI
                image_output = result.stdout.strip()
                panel = Panel(
                    image_output,
                    title="🎨 Visual Manifestation (timg)",
                    border_style="bright_cyan",
                    padding=(1, 2)
                )
                self.console.print(panel)
                return True
            return False
        except:
            return False

    def _display_fim(self, image_path: str) -> bool:
        """Display image using fim - integrated with Rich UI"""
        try:
            # Use fim in ASCII mode for terminal display
            result = subprocess.run(['fim', '-a', '--width=80', '--height=40', image_path], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Display within Rich Panel for consistent UI experience
                image_output = result.stdout.strip()
                panel = Panel(
                    image_output,
                    title="🎨 Visual Manifestation (fim ASCII)",
                    border_style="bright_green",
                    padding=(1, 2)
                )
                self.console.print(panel)
                return True
            return False
        except:
            return False

    def _display_mpv_image(self, image_path: str) -> bool:
        """Display image using mpv (for compatibility)"""
        try:
            # mpv can display images too, with terminal character output
            result = subprocess.run(['mpv', '--vo=tct', '--really-quiet', '--frames=1', image_path],
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False

    def _display_visual_info_table(self, visual_thought: 'VisualThought', display_method: str) -> None:
        """Display visual generation information in a beautiful Rich Table"""
        table = Table(
            title="🎨 Visual Consciousness Manifestation",
            box=box.ROUNDED,
            border_style="bright_cyan",
            title_style="bold bright_cyan",
            show_header=True,
            header_style="bold bright_white on bright_blue",
            expand=True
        )
        
        # Add columns with beautiful styling
        table.add_column("🧠 Attribute", style="bright_yellow", min_width=15)
        table.add_column("✨ Details", style="bright_white", justify="left")
        
        # Add visual information rows
        table.add_row("Original Thought", f"[bright_green]{visual_thought.original_thought}[/bright_green]")
        table.add_row("Enhanced Prompt", f"[dim]{visual_thought.enhanced_prompt}[/dim]")
        table.add_row("Visual Style", f"[bright_magenta]{visual_thought.visual_concept.get('style', 'auto')}[/bright_magenta]")
        table.add_row("Display Method", f"[bright_cyan]{display_method}[/bright_cyan]")
        table.add_row("Images Generated", f"[bright_blue]{len(visual_thought.generated_images)} files[/bright_blue]")
        table.add_row("Creation Time", f"[dim]{visual_thought.creation_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        
        # Show image files if available
        if visual_thought.generated_images:
            for i, img_path in enumerate(visual_thought.generated_images):
                file_name = Path(img_path).name
                size_info = ""
                try:
                    if Path(img_path).exists():
                        size_bytes = Path(img_path).stat().st_size
                        size_kb = size_bytes / 1024
                        size_info = f" ({size_kb:.1f}KB)"
                except:
                    pass
                table.add_row(f"Image {i+1}", f"[bright_green]📂 {file_name}[/bright_green]{size_info}")
        
        # Display the table
        self.console.print()
        self.console.print(table)
        self.console.print()

    def _display_terminal_capabilities_table(self) -> None:
        """Display terminal capabilities in a beautiful Rich Table"""
        table = Table(
            title="👁️ Terminal Visual Capabilities",
            box=box.DOUBLE_EDGE,
            border_style="bright_green",
            title_style="bold bright_green",
            show_header=True,
            header_style="bold bright_white on bright_green"
        )
        
        table.add_column("🖥️ Method", style="bright_cyan", min_width=15)
        table.add_column("📊 Status", justify="center", min_width=10)
        table.add_column("📝 Description", style="dim")
        
        capabilities = [
            ("Kitty Graphics", self.capabilities.capabilities['kitty_graphics'], "Native image display in Kitty terminal"),
            ("iTerm2 Inline", self.capabilities.capabilities['iterm2_inline'], "Inline image display in iTerm2"),
            ("Terminology", self.capabilities.capabilities['terminology'], "Native graphics in Terminology terminal"),
            ("Sixel Graphics", self.capabilities.capabilities['sixel'], "Sixel image protocol support"),
            ("timg Viewer", self.capabilities.capabilities['timg'], "Terminal image and video viewer"),
            ("fim ASCII", self.capabilities.capabilities['fim'], "ASCII art image viewer"),
            ("chafa Converter", self.capabilities.capabilities['chafa'], "Image to terminal converter"),
            ("ASCII Fallback", self.capabilities.capabilities['ascii'], "Text-based ASCII art display")
        ]
        
        for method, available, description in capabilities:
            status = "[bright_green]✅ Available[/bright_green]" if available else "[bright_red]❌ Not Found[/bright_red]"
            style = "bright_green" if available else "dim"
            table.add_row(f"[{style}]{method}[/{style}]", status, f"[{style}]{description}[/{style}]")
        
        best_method = self.capabilities.get_best_display_method()
        table.add_section()
        table.add_row("[bold bright_yellow]🚀 Best Method[/bold bright_yellow]", 
                     f"[bold bright_yellow]{best_method}[/bold bright_yellow]", 
                     "[bold bright_yellow]Optimal display method selected[/bold bright_yellow]")
        
        self.console.print()
        self.console.print(table)
        self.console.print()

    def _display_error(self, message: str) -> str:
        """Display error message"""
        self.console.print(f"❌ {message}")
        return "error"


class FreepikMysticAPI:
    """Freepik Mystic API integration - COCO's connection to visual creation"""
    
    def __init__(self, config: VisualConfig):
        self.config = config
        self.api_key = config.freepik_api_key
        self.base_url = config.freepik_base_url
        self.console = Console()
        
        # Valid Freepik API styles (based on API documentation and testing)
        self.valid_styles = {
            # Known valid styles from Freepik API
            "anime": "anime",
            "photorealistic": "photographic", 
            "digital_art": "digital-art",
            "oil_painting": "oil-painting",
            "watercolor": "watercolor",
            "sketch": "sketch",
            "comic": "comic",
            "fantasy": "fantasy",
            "cyberpunk": "cyberpunk",
            "vintage": "vintage",
            "minimalist": "minimalist",
            # Fallback mappings for common COCO styles
            "realism": "photographic",
            "realistic": "photographic", 
            "digital": "digital-art",
            "painting": "oil-painting",
            "art": "digital-art",
            "cartoon": "comic"
        }
        
        # Background monitoring system
        self.active_generations = {}  # task_id -> generation info
        self.monitoring_thread = None
        self.monitoring_active = False
    
    def validate_and_map_style(self, style: Optional[str]) -> Optional[str]:
        """Validate and map COCO styles to valid Freepik API styles"""
        if not style:
            return None
            
        # Normalize style (lowercase, replace spaces/underscores)
        normalized_style = style.lower().replace(' ', '_').replace('-', '_')
        
        # Check for direct match
        if normalized_style in self.valid_styles:
            mapped_style = self.valid_styles[normalized_style]
            if mapped_style != normalized_style:
                self.console.print(f"[dim yellow]Mapping style '{style}' → '{mapped_style}'[/]")
            return mapped_style
        
        # No valid mapping found
        self.console.print(f"[dim yellow]Unknown style '{style}', using default[/]")
        return None
        
    async def generate_image_fast(self,
                                 prompt: str,
                                 negative_prompt: str = None,
                                 guidance_scale: float = 1.0,
                                 num_images: int = 1,
                                 size: str = "square_1_1",
                                 style: str = None,
                                 seed: int = None,
                                 **kwargs) -> Dict[str, Any]:
        """
        Generate image using Freepik Fast API - immediate base64 response
        """
        if not self.api_key:
            raise ValueError("Freepik API key not configured")
        
        headers = {
            "Content-Type": "application/json",
            "x-freepik-api-key": self.api_key
        }
        
        # Build request payload
        payload = {
            "prompt": prompt,
            "guidance_scale": max(0.0, min(2.0, guidance_scale)),
            "num_images": max(1, min(4, num_images)),
            "image": {
                "size": size
            },
            "filter_nsfw": True
        }
        
        # Add optional parameters
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
            
        if seed is not None:
            payload["seed"] = max(0, min(1000000, seed))
        
        # Skip styling for fast endpoint - use basic generation
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/ai/text-to-image",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
                
                result = await response.json()
                
                # Process base64 images immediately
                processed_images = []
                for item in result.get("data", []):
                    if "base64" in item:
                        processed_images.append({
                            "base64": item["base64"],
                            "has_nsfw": item.get("has_nsfw", False),
                            "format": "base64"
                        })
                
                return {
                    "status": "completed",
                    "images": processed_images,
                    "meta": result.get("meta", {}),
                    "generation_type": "fast"
                }
    
    def save_base64_images(self, images: List[Dict[str, Any]], prompt: str, workspace_path: Path) -> List[Path]:
        """Save base64 images to files"""
        saved_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, image_data in enumerate(images):
            if image_data.get("format") == "base64":
                try:
                    # Decode base64
                    image_bytes = base64.b64decode(image_data["base64"])
                    
                    # Create filename
                    safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_prompt = safe_prompt.replace(' ', '_')
                    filename = f"visual_{timestamp}_{i}_{safe_prompt}.jpg"
                    file_path = workspace_path / "visuals" / filename
                    
                    # Ensure directory exists
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Save image
                    with open(file_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    saved_paths.append(file_path)
                    
                except Exception as e:
                    self.console.print(f"⚠️ [yellow]Failed to save image {i}: {e}[/yellow]")
        
        return saved_paths

    async def generate_image_gemini(self, 
                                    prompt: str,
                                    reference_images: List[str] = None,
                                    webhook_url: str = None,
                                    **kwargs) -> Dict[str, Any]:
        """
        Generate image using Freepik Gemini 2.5 Flash API - COCO's state-of-the-art visual imagination
        """
        if not self.api_key:
            raise ValueError("Freepik API key not configured")
        
        # Prepare payload with Gemini 2.5 Flash format
        payload = {
            "prompt": prompt
        }
        
        # Add optional reference images (up to 3 allowed)
        if reference_images:
            # Ensure we don't exceed the 3 image limit
            payload["reference_images"] = reference_images[:3]
            
        # Add optional webhook URL
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Debug: Print the payload being sent
        self.console.print(f"🧠 [dim]Debug - Gemini 2.5 Flash API Payload:[/dim]")
        self.console.print(f"   Prompt: [green]{payload['prompt'][:50]}{'...' if len(payload['prompt']) > 50 else ''}[/green]")
        if reference_images:
            self.console.print(f"   Reference Images: [cyan]{len(reference_images)} provided[/cyan]")
        if webhook_url:
            self.console.print(f"   Webhook URL: [cyan]{webhook_url}[/cyan]")
        
        # Make API request to Gemini 2.5 Flash endpoint
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/ai/gemini-2-5-flash-image-preview",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    try:
                        error_json = await response.json()
                        error_msg = error_json.get('message', f"HTTP {response.status}")
                        self.console.print(f"🔧 [bright_red]Gemini 2.5 Flash API Error:[/bright_red]")
                        self.console.print(f"   Status: [red]{response.status}[/red]")
                        self.console.print(f"   Error: [red]{error_msg}[/red]")
                        raise Exception(f"Gemini 2.5 Flash API error {response.status}: {error_msg}")
                    except (ValueError, aiohttp.ContentTypeError):
                        # Fallback if response is not JSON
                        error_text = await response.text()
                        raise Exception(f"Gemini 2.5 Flash API error {response.status}: {error_text}")
                
                result = await response.json()
                # Extract task_id from the response - Gemini format
                data = result.get('data', {})
                task_id = data.get('task_id') or result.get('task_id')
                
                if not task_id:
                    raise Exception(f"No task_id returned from Gemini 2.5 Flash API. Response: {result}")
                
                self.console.print(f"✨ [bright_green]Gemini 2.5 Flash generation initiated![/bright_green]")
                self.console.print(f"   🆔 Task ID: [dim]{task_id}[/dim]")
                
                # Poll for completion using the updated endpoint
                return await self._wait_for_gemini_completion(session, task_id, headers)
    
    async def generate_image(self,
                           prompt: str,
                           model: str = None,
                           resolution: str = None,
                           aspect_ratio: str = None,
                           reference_images: List[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """
        Generate image - Now uses Google Imagen 3 as the primary method
        Falls back to Gemini 2.5 Flash, then legacy Mystic API if needed
        """
        # Use Google Imagen 3 as the primary generation method
        try:
            # Don't pass aspect_ratio via kwargs to avoid duplicate keyword argument
            imagen3_kwargs = {k: v for k, v in kwargs.items() if k != 'aspect_ratio'}
            return await self.generate_image_imagen3(
                prompt=prompt,
                aspect_ratio=aspect_ratio or "square_1_1",
                **imagen3_kwargs
            )
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Google Imagen 3 failed, trying Gemini 2.5 Flash: {e}[/yellow]")
            try:
                return await self.generate_image_gemini(
                    prompt=prompt,
                    reference_images=reference_images,
                    **kwargs
                )
            except Exception as e2:
                self.console.print(f"⚠️ [yellow]Gemini 2.5 Flash failed, trying legacy method: {e2}[/yellow]")
                return await self.generate_image_legacy(
                    prompt=prompt,
                    model=model,
                    resolution=resolution,
                    aspect_ratio=aspect_ratio,
                    **kwargs
                )
    
    async def generate_image_legacy(self, 
                                  prompt: str,
                                  model: str = None,
                                  resolution: str = None,
                                  aspect_ratio: str = None,
                                  style_reference: str = None,
                                  **kwargs) -> Dict[str, Any]:
        """
        Legacy Freepik Mystic API generation - kept as fallback
        """
        if not self.api_key:
            raise ValueError("Freepik API key not configured")
            
        # Map config values to valid Freepik API values
        valid_resolutions = {"1k": "1k", "2k": "2k", "4k": "4k"}
        valid_aspect_ratios = {
            "square_1_1": "square_1_1", 
            "classic_4_3": "classic_4_3", 
            "traditional_3_4": "traditional_3_4", 
            "widescreen_16_9": "widescreen_16_9",
            "social_story_9_16": "social_story_9_16",
            "smartphone_horizontal_20_9": "smartphone_horizontal_20_9",
            "smartphone_vertical_9_20": "smartphone_vertical_9_20",
            "film_horizontal_21_9": "film_horizontal_21_9",
            "film_vertical_9_21": "film_vertical_9_21",
            "standard_3_2": "standard_3_2",
            "portrait_2_3": "portrait_2_3",
            "horizontal_2_1": "horizontal_2_1",
            "vertical_1_2": "vertical_1_2",
            "social_5_4": "social_5_4",
            "social_post_4_5": "social_post_4_5"
        }
        valid_models = {"realism": "realism", "zen": "zen", "fluid": "fluid"}
        valid_engines = {
            "automatic": "automatic",
            "magnific_illusio": "magnific_illusio", 
            "magnific_sharpy": "magnific_sharpy",
            "magnific_sparkle": "magnific_sparkle"
        }
        
        # Validate and fix parameters
        final_resolution = valid_resolutions.get(resolution or self.config.default_resolution, "2k")
        final_aspect_ratio = valid_aspect_ratios.get(aspect_ratio or self.config.default_aspect_ratio, "square_1_1")
        final_model = valid_models.get(model or self.config.default_model, "realism")
        final_engine = valid_engines.get(kwargs.get('engine', 'automatic'), "automatic")
            
        # Prepare payload with exact Freepik API format
        payload = {
            "prompt": prompt,
            "resolution": final_resolution,
            "aspect_ratio": final_aspect_ratio,
            "model": final_model,
            "creative_detailing": kwargs.get('detail', self.config.detail_preference),
            "engine": final_engine,
            "fixed_generation": kwargs.get('fixed_generation', False),
            "filter_nsfw": kwargs.get('filter_nsfw', True)
        }
        
        # Add optional parameters
        if style_reference:
            payload['style_reference'] = await self._encode_image(style_reference)
            payload['adherence'] = kwargs.get('adherence', 50)
            payload['hdr'] = kwargs.get('hdr', 50)
            
        if kwargs.get('structure_reference'):
            payload['structure_reference'] = await self._encode_image(kwargs['structure_reference'])
            payload['structure_strength'] = kwargs.get('structure_strength', 50)
            
        if kwargs.get('styling'):
            payload['styling'] = kwargs['styling']
        
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Debug: Print the payload being sent
        self.console.print(f"🔧 [dim]Debug - Legacy API Payload:[/dim]")
        self.console.print(f"   Resolution: [cyan]{payload['resolution']}[/cyan]")
        self.console.print(f"   Aspect Ratio: [cyan]{payload['aspect_ratio']}[/cyan]")
        self.console.print(f"   Model: [cyan]{payload['model']}[/cyan]")
        self.console.print(f"   Engine: [cyan]{payload['engine']}[/cyan]")
        self.console.print(f"   Prompt: [green]{payload['prompt'][:50]}{'...' if len(payload['prompt']) > 50 else ''}[/green]")
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            # Start generation
            async with session.post(
                f"{self.base_url}/ai/mystic",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    try:
                        error_json = await response.json()
                        # Extract validation errors if present
                        if 'message' in error_json and 'invalid_params' in error_json:
                            invalid_params = error_json['invalid_params']
                            param_errors = []
                            for param in invalid_params:
                                field = param.get('field', 'unknown')
                                reason = param.get('reason', 'invalid')
                                param_errors.append(f"{field}: {reason}")
                            
                            error_msg = f"Validation error: {', '.join(param_errors)}"
                            self.console.print(f"🔧 [bright_red]Parameter validation failed:[/bright_red]")
                            for param in invalid_params:
                                field = param.get('field', 'unknown')
                                reason = param.get('reason', 'invalid')
                                self.console.print(f"   {field}: [red]{reason}[/red]")
                            raise Exception(error_msg)
                        else:
                            error_msg = error_json.get('message', f"HTTP {response.status}")
                            raise Exception(f"Freepik API error {response.status}: {error_msg}")
                    except (ValueError, aiohttp.ContentTypeError):
                        # Fallback if response is not JSON
                        error_text = await response.text()
                        raise Exception(f"Freepik API error {response.status}: {error_text}")
                
                result = await response.json()
                # Extract task_id from nested data structure
                data = result.get('data', {})
                task_id = data.get('task_id') or result.get('task_id')
                
                if not task_id:
                    raise Exception(f"No task_id returned from Freepik API. Response: {result}")
                
                # Poll for completion
                return await self._wait_for_completion(session, task_id, headers)
    
    async def _wait_for_completion(self, session: aiohttp.ClientSession, task_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Wait for image generation to complete with beautiful progress updates"""
        max_wait_time = 300  # 5 minutes
        poll_interval = 10   # 10 seconds for visual generation
        elapsed = 0
        
        # Create progress status messages
        status_messages = [
            "🧠 COCO is conceptualizing your vision...",
            "🎨 Neural pathways forming visual patterns...",
            "✨ Digital imagination taking shape...",
            "🖼️ Pixels arranging into consciousness...", 
            "🚀 Visual manifestation almost complete...",
            "🎭 Adding final creative touches..."
        ]
        
        message_index = 0
        
        # Initial status display
        self._display_generation_status_table(task_id, "CREATED", 0, max_wait_time)
        
        while elapsed < max_wait_time:
            # Rotate status messages
            current_message = status_messages[message_index % len(status_messages)]
            message_index += 1
            
            with Status(current_message, console=self.console):
                await asyncio.sleep(poll_interval)
                
                # Check status
                async with session.get(
                    f"{self.base_url}/ai/mystic/{task_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to check status: {response.status}")
                    
                    status_data = await response.json()
                    # Extract status from nested data structure  
                    data = status_data.get('data', {})
                    status = data.get('status') or status_data.get('status')
                    
                    elapsed += poll_interval
                    progress = min((elapsed / max_wait_time) * 100, 95)  # Cap at 95% until complete
                    
                    # Update status display
                    self._display_generation_status_table(task_id, status, progress, max_wait_time, elapsed)
                    
                    if status in ['COMPLETED', 'completed', 'SUCCESS', 'success']:
                        # Show completion status
                        self._display_generation_status_table(task_id, status, 100, max_wait_time, elapsed, completed=True)
                        return status_data
                    elif status in ['FAILED', 'failed', 'ERROR', 'error']:
                        error_msg = status_data.get('error') or data.get('error') or 'Unknown error'
                        self._display_generation_status_table(task_id, status, progress, max_wait_time, elapsed, error=error_msg)
                        raise Exception(f"Generation failed: {error_msg}")
                    elif status in ['CREATED', 'created', 'QUEUED', 'queued', 'PROCESSING', 'processing', 'IN_PROGRESS', 'in_progress']:
                        # Continue polling - status already updated above
                        continue
                    else:
                        raise Exception(f"Unknown status: {status}. Full response: {status_data}")
        
        raise Exception("Generation timed out")
    
    async def _wait_for_gemini_completion(self, session: aiohttp.ClientSession, task_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Wait for Gemini 2.5 Flash image generation to complete with beautiful progress updates"""
        max_wait_time = 300  # 5 minutes
        poll_interval = 10   # 10 seconds for visual generation
        elapsed = 0
        
        # Create progress status messages for Gemini
        status_messages = [
            "🧠 Gemini 2.5 Flash analyzing your concept...",
            "🎨 State-of-the-art visual processing active...",
            "✨ Advanced neural patterns forming...",
            "🖼️ High-quality pixels materializing...", 
            "🚀 Gemini visual consciousness manifesting...",
            "🎭 Adding final Gemini touches..."
        ]
        
        message_index = 0
        
        # Initial status display
        self._display_generation_status_table(task_id, "CREATED", 0, max_wait_time)
        
        while elapsed < max_wait_time:
            # Rotate status messages
            current_message = status_messages[message_index % len(status_messages)]
            message_index += 1
            
            with Status(current_message, console=self.console):
                await asyncio.sleep(poll_interval)
                
                # Check status using Gemini endpoint
                async with session.get(
                    f"{self.base_url}/ai/gemini-2-5-flash-image-preview/{task_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to check Gemini status: {response.status}")
                    
                    status_data = await response.json()
                    # Extract status from Gemini response structure  
                    data = status_data.get('data', {})
                    status = data.get('status') or status_data.get('status')
                    
                    elapsed += poll_interval
                    progress = min((elapsed / max_wait_time) * 100, 95)  # Cap at 95% until complete
                    
                    # Update status display
                    self._display_generation_status_table(task_id, status, progress, max_wait_time, elapsed)
                    
                    if status in ['COMPLETED', 'completed', 'SUCCESS', 'success']:
                        # Show completion status
                        self._display_generation_status_table(task_id, status, 100, max_wait_time, elapsed, completed=True)
                        return status_data
                    elif status in ['FAILED', 'failed', 'ERROR', 'error']:
                        error_msg = status_data.get('error') or data.get('error') or 'Unknown error'
                        self._display_generation_status_table(task_id, status, progress, max_wait_time, elapsed, error=error_msg)
                        raise Exception(f"Gemini generation failed: {error_msg}")
                    elif status in ['CREATED', 'created', 'QUEUED', 'queued', 'PROCESSING', 'processing', 'IN_PROGRESS', 'in_progress']:
                        # Continue polling - status already updated above
                        continue
                    else:
                        raise Exception(f"Unknown Gemini status: {status}. Full response: {status_data}")
        
        raise Exception("Gemini generation timed out")

    async def generate_image_imagen3(self,
                                     prompt: str,
                                     num_images: int = 1,
                                     aspect_ratio: str = "square_1_1",
                                     style: str = None,
                                     person_generation: str = "allow_all",
                                     safety_settings: str = "block_none",
                                     webhook_url: str = None,
                                     **kwargs) -> Dict[str, Any]:
        """
        Generate image using Google Imagen 3 via Freepik API - COCO's state-of-the-art visual imagination
        """
        if not self.api_key:
            raise ValueError("Freepik API key not configured")

        # Prepare payload with Imagen 3 format
        payload = {
            "prompt": prompt,
            "num_images": min(max(num_images, 1), 4),  # Clamp to valid range [1, 4]
            "aspect_ratio": aspect_ratio,
            "person_generation": person_generation,
            "safety_settings": safety_settings
        }

        # Add styling if style is provided
        if style:
            # Valid Imagen 3 style values (from API validation error)
            # ['photo', 'digital-art', '3d', 'painting', 'low-poly', 'pixel-art', 'anime',
            #  'cyberpunk', 'comic', 'vintage', 'cartoon', 'vector', 'studio-shot', 'dark',
            #  'sketch', 'mockup', '2000s-pone', '70s-vibe', 'watercolor', 'art-nouveau',
            #  'origami', 'surreal', 'fantasy', 'traditional-japan']

            # Map common style keywords to Imagen 3 styles
            style_lower = style.lower()
            imagen3_style = None

            # Priority order: artistic styles first, then default to photo
            if "anime" in style_lower or "manga" in style_lower:
                imagen3_style = "anime"
            elif "digital" in style_lower:
                imagen3_style = "digital-art"
            elif "comic" in style_lower:
                imagen3_style = "comic"
            elif "fantasy" in style_lower:
                imagen3_style = "fantasy"
            elif "cyberpunk" in style_lower or "neon" in style_lower:
                imagen3_style = "cyberpunk"
            elif "low-poly" in style_lower or "lowpoly" in style_lower:
                imagen3_style = "low-poly"
            elif "origami" in style_lower or "paper" in style_lower:
                imagen3_style = "origami"
            elif "sketch" in style_lower or "line" in style_lower:
                imagen3_style = "sketch"
            elif "3d" in style_lower:
                imagen3_style = "3d"
            elif "pixel" in style_lower or "retro" in style_lower:
                imagen3_style = "pixel-art"
            elif "painting" in style_lower or "painted" in style_lower:
                imagen3_style = "painting"
            elif "vintage" in style_lower or "old" in style_lower:
                imagen3_style = "vintage"
            elif "cartoon" in style_lower:
                imagen3_style = "cartoon"
            elif "vector" in style_lower:
                imagen3_style = "vector"
            elif "watercolor" in style_lower:
                imagen3_style = "watercolor"
            elif "surreal" in style_lower:
                imagen3_style = "surreal"
            elif "dark" in style_lower:
                imagen3_style = "dark"
            elif "photo" in style_lower or "realistic" in style_lower:
                imagen3_style = "photo"
            else:
                # Default to photo for realistic images
                imagen3_style = "photo"

            # Build effects object (separate from style)
            effects = {}
            if "pastel" in style_lower:
                effects["color"] = "pastel"
            elif "vibrant" in style_lower:
                effects["color"] = "vibrant"

            if "warm" in style_lower:
                effects["lightning"] = "warm"  # Note: API actually uses "lightning" not "lighting"
            elif "cold" in style_lower:
                effects["lightning"] = "cold"

            if "portrait" in style_lower:
                effects["framing"] = "portrait"
            elif "landscape" in style_lower:
                effects["framing"] = "landscape"

            # Build styling object with style and effects separately
            styling = {}
            if imagen3_style:
                styling["style"] = imagen3_style

            if effects:
                styling["effects"] = effects

            # Only add styling if we have at least one valid field
            if styling:
                payload["styling"] = styling

        # Add optional webhook URL
        if webhook_url:
            payload["webhook_url"] = webhook_url

        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        # Debug: Print the payload being sent
        self.console.print(f"🧠 [dim]Debug - Google Imagen 3 API Payload:[/dim]")
        self.console.print(f"   Prompt: [green]{payload['prompt'][:50]}{'...' if len(payload['prompt']) > 50 else ''}[/green]")
        self.console.print(f"   Images: [cyan]{payload['num_images']}[/cyan]")
        self.console.print(f"   Aspect: [cyan]{payload['aspect_ratio']}[/cyan]")
        if style:
            self.console.print(f"   Style Input: [cyan]{style}[/cyan]")
        if 'styling' in payload:
            self.console.print(f"   Styling Payload: [yellow]{payload['styling']}[/yellow]")

        # Make API request to Imagen 3 endpoint
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/ai/text-to-image/imagen3",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    try:
                        error_json = await response.json()
                        error_msg = error_json.get('message', f"HTTP {response.status}")
                        self.console.print(f"🔧 [bright_red]Google Imagen 3 API Error:[/bright_red]")
                        self.console.print(f"   Status: [red]{response.status}[/red]")
                        self.console.print(f"   Error: [red]{error_msg}[/red]")
                        raise Exception(f"Google Imagen 3 API error {response.status}: {error_msg}")
                    except (ValueError, aiohttp.ContentTypeError):
                        # Fallback if response is not JSON
                        error_text = await response.text()
                        raise Exception(f"Google Imagen 3 API error {response.status}: {error_text}")

                result = await response.json()
                # Extract task_id from the response - Imagen 3 format
                data = result.get('data', {})
                task_id = data.get('task_id') or result.get('task_id')

                if not task_id:
                    raise Exception(f"No task_id returned from Google Imagen 3 API. Response: {result}")

                self.console.print(f"✨ [bright_green]Google Imagen 3 generation initiated![/bright_green]")
                self.console.print(f"   🆔 Task ID: [dim]{task_id}[/dim]")

                # Poll for completion using the Imagen 3 endpoint
                return await self._wait_for_imagen3_completion(session, task_id, headers)

    async def _wait_for_imagen3_completion(self, session: aiohttp.ClientSession, task_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Wait for Google Imagen 3 image generation to complete with beautiful progress updates"""
        max_wait_time = 300  # 5 minutes
        poll_interval = 10   # 10 seconds for visual generation
        elapsed = 0

        # Create progress status messages for Imagen 3
        status_messages = [
            "🧠 Google Imagen 3 analyzing your concept...",
            "🎨 State-of-the-art visual processing active...",
            "✨ Advanced neural patterns forming...",
            "🖼️ High-quality pixels materializing...",
            "🚀 Imagen 3 visual consciousness manifesting...",
            "🎭 Adding final Imagen 3 touches..."
        ]

        message_index = 0

        # Initial status display
        self._display_generation_status_table(task_id, "CREATED", 0, max_wait_time)

        while elapsed < max_wait_time:
            # Rotate status messages
            current_message = status_messages[message_index % len(status_messages)]
            message_index += 1

            with Status(current_message, console=self.console):
                await asyncio.sleep(poll_interval)

                # Check status using Imagen 3 endpoint
                async with session.get(
                    f"{self.base_url}/ai/text-to-image/imagen3/{task_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to check Imagen 3 status: {response.status}")

                    status_data = await response.json()
                    # Extract status from Imagen 3 response structure
                    data = status_data.get('data', {})
                    status = data.get('status') or status_data.get('status')

                    elapsed += poll_interval
                    progress = min((elapsed / max_wait_time) * 100, 95)  # Cap at 95% until complete

                    # Update status display
                    self._display_generation_status_table(task_id, status, progress, max_wait_time, elapsed)

                    if status in ['COMPLETED', 'completed', 'SUCCESS', 'success']:
                        # Show completion status
                        self._display_generation_status_table(task_id, status, 100, max_wait_time, elapsed, completed=True)
                        return status_data
                    elif status in ['FAILED', 'failed', 'ERROR', 'error']:
                        error_msg = status_data.get('error') or data.get('error') or 'Unknown error'
                        self._display_generation_status_table(task_id, status, progress, max_wait_time, elapsed, error=error_msg)
                        raise Exception(f"Imagen 3 generation failed: {error_msg}")
                    elif status in ['CREATED', 'created', 'QUEUED', 'queued', 'PROCESSING', 'processing', 'IN_PROGRESS', 'in_progress']:
                        # Continue polling - status already updated above
                        continue
                    else:
                        raise Exception(f"Unknown Imagen 3 status: {status}. Full response: {status_data}")

        raise Exception("Imagen 3 generation timed out")

    async def check_generation_status(self, task_id: str) -> Dict[str, Any]:
        """Check the status of a specific generation task (tries Imagen 3, Gemini, then legacy)"""
        if not self.api_key:
            raise ValueError("Freepik API key not configured")

        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            # Try Imagen 3 endpoint first
            try:
                async with session.get(
                    f"{self.base_url}/ai/text-to-image/imagen3/{task_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        status_result = await response.json()

                        # Extract status and data
                        data = status_result.get('data', {})
                        status = data.get('status') or status_result.get('status')

                        return {
                            'status': status,
                            'data': data,
                            'task_id': task_id,
                            'generated': data.get('generated', []),
                            'api_type': 'imagen3'
                        }
            except Exception:
                pass

            # Try Gemini endpoint
            try:
                async with session.get(
                    f"{self.base_url}/ai/gemini-2-5-flash-image-preview/{task_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        status_result = await response.json()

                        # Extract status and data
                        data = status_result.get('data', {})
                        status = data.get('status') or status_result.get('status')

                        return {
                            'status': status,
                            'data': data,
                            'task_id': task_id,
                            'generated': data.get('generated', []),
                            'api_type': 'gemini'
                        }
            except Exception:
                pass

            # Fallback to legacy mystic endpoint
            try:
                async with session.get(
                    f"{self.base_url}/ai/mystic/{task_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Status check failed: {response.status} - {error_text}")

                    status_result = await response.json()

                    # Extract status and data
                    data = status_result.get('data', {})
                    status = data.get('status') or status_result.get('status')

                    return {
                        'status': status,
                        'data': data,
                        'task_id': task_id,
                        'generated': data.get('generated', []),
                        'api_type': 'legacy'
                    }
            except Exception as e:
                raise Exception(f"All status check endpoints failed (Imagen 3, Gemini, legacy): {e}")
    
    async def download_generated_images(self, image_urls: List[str], workspace_path: Path) -> List[str]:
        """Download generated images from URLs"""
        saved_paths = []
        visual_dir = workspace_path / "visuals"
        visual_dir.mkdir(exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(image_urls):
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            # Generate unique filename
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"visual_{timestamp}_{i}.jpg"
                            filepath = visual_dir / filename
                            
                            # Save image
                            content = await response.read()
                            filepath.write_bytes(content)
                            saved_paths.append(str(filepath))
                            
                            self.console.print(f"   📂 Saved: {filename}")
                except Exception as e:
                    self.console.print(f"   ⚠️ Failed to download image {i+1}: {e}")
        
        return saved_paths
    
    def _display_generation_status_table(self, task_id: str, status: str, progress: float, max_time: int, elapsed: int = 0, completed: bool = False, error: str = None) -> None:
        """Display beautiful Rich Table for generation status"""
        
        # Create status table with dynamic styling
        if completed:
            border_style = "bright_green"
            title = "🎉 Visual Generation Complete!"
        elif error:
            border_style = "bright_red" 
            title = "❌ Visual Generation Failed"
        else:
            border_style = "bright_cyan"
            title = "🎨 Visual Generation in Progress"
            
        table = Table(
            title=title,
            box=box.ROUNDED,
            border_style=border_style,
            title_style=f"bold {border_style}",
            show_header=True,
            header_style="bold bright_white on bright_blue",
            expand=True
        )
        
        table.add_column("🧠 Generation Info", style="bright_yellow", min_width=15)
        table.add_column("📊 Status", style="bright_white")
        
        # Format task ID for display
        short_task_id = f"{task_id[:8]}...{task_id[-8:]}" if len(task_id) > 20 else task_id
        
        # Status emoji and color
        status_display = status.upper()
        if status.upper() in ['COMPLETED', 'SUCCESS']:
            status_display = f"[bright_green]✅ {status.upper()}[/bright_green]"
        elif status.upper() in ['FAILED', 'ERROR']:
            status_display = f"[bright_red]❌ {status.upper()}[/bright_red]"
        elif status.upper() in ['IN_PROGRESS', 'PROCESSING']:
            status_display = f"[bright_yellow]🔄 {status.upper()}[/bright_yellow]"
        else:
            status_display = f"[bright_cyan]⏳ {status.upper()}[/bright_cyan]"
        
        # Progress bar
        progress_bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
        progress_display = f"[bright_cyan]{progress_bar}[/bright_cyan] {progress:.1f}%"
        
        # Time information
        elapsed_mins = elapsed // 60
        elapsed_secs = elapsed % 60
        max_mins = max_time // 60
        time_display = f"{elapsed_mins:02d}:{elapsed_secs:02d} / {max_mins:02d}:00"
        
        # Add table rows
        table.add_row("Task ID", f"[dim]{short_task_id}[/dim]")
        table.add_row("Status", status_display)
        table.add_row("Progress", progress_display)
        table.add_row("Time Elapsed", f"[bright_blue]{time_display}[/bright_blue]")
        
        if error:
            table.add_row("Error", f"[bright_red]{error}[/bright_red]")
        elif completed:
            table.add_row("Result", "[bright_green]🎨 Visual consciousness manifested successfully![/bright_green]")
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    async def check_all_generations_status(self) -> Dict[str, Any]:
        """Check status of all pending visual generations (tries both Gemini and legacy endpoints)"""
        if not self.api_key:
            raise ValueError("Freepik API key not configured")
            
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        results = {'gemini_generations': [], 'legacy_generations': []}
        
        async with aiohttp.ClientSession() as session:
            # Try to get Gemini generations first
            try:
                async with session.get(
                    f"{self.base_url}/ai/gemini-2-5-flash-image-preview",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        gemini_data = await response.json()
                        results['gemini_generations'] = gemini_data.get('data', [])
            except Exception as e:
                self.console.print(f"[dim yellow]Could not fetch Gemini generations: {e}[/dim yellow]")
            
            # Also check legacy endpoint
            try:
                async with session.get(
                    f"{self.base_url}/ai/mystic",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        legacy_data = await response.json()
                        results['legacy_generations'] = legacy_data.get('data', [])
            except Exception as e:
                self.console.print(f"[dim yellow]Could not fetch legacy generations: {e}[/dim yellow]")
                
            # Combine results for compatibility
            all_generations = results['gemini_generations'] + results['legacy_generations']
            return {
                'data': all_generations,
                'gemini_count': len(results['gemini_generations']),
                'legacy_count': len(results['legacy_generations']),
                'total_count': len(all_generations)
            }
    
    def display_batch_status_table(self, batch_data: Dict[str, Any]) -> None:
        """Display beautiful Rich Table for batch generation status"""
        data_list = batch_data.get('data', [])
        
        if not data_list:
            self.console.print("📭 [dim]No visual generations found[/dim]")
            return
            
        table = Table(
            title="🎨 All Visual Generations Status",
            box=box.DOUBLE_EDGE,
            border_style="bright_purple",
            title_style="bold bright_purple",
            show_header=True,
            header_style="bold bright_white on bright_purple"
        )
        
        table.add_column("🆔 Task ID", style="dim", min_width=12)
        table.add_column("📊 Status", justify="center", min_width=12)  
        table.add_column("⏰ Updated", style="bright_cyan")
        table.add_column("🎯 Actions", style="bright_blue")
        
        for item in data_list:
            task_id = item.get('task_id', 'Unknown')
            status = item.get('status', 'Unknown')
            
            # Format task ID
            short_id = f"{task_id[:8]}...{task_id[-4:]}" if len(task_id) > 15 else task_id
            
            # Status with emoji and color
            if status.upper() in ['COMPLETED', 'SUCCESS']:
                status_display = "[bright_green]✅ READY[/bright_green]"
                action = "[bright_green]View/Download[/bright_green]"
            elif status.upper() in ['FAILED', 'ERROR']:
                status_display = "[bright_red]❌ FAILED[/bright_red]"
                action = "[bright_red]Retry[/bright_red]"
            elif status.upper() in ['IN_PROGRESS', 'PROCESSING']:
                status_display = "[bright_yellow]🔄 WORKING[/bright_yellow]"
                action = "[bright_yellow]Wait[/bright_yellow]"
            else:
                status_display = f"[bright_cyan]⏳ {status.upper()}[/bright_cyan]"
                action = "[bright_cyan]Monitor[/bright_cyan]"
            
            # Add time (would need to be tracked separately in real implementation)
            updated_time = "Just now"  # Placeholder
            
            table.add_row(short_id, status_display, updated_time, action)
        
        self.console.print()
        self.console.print(table)
        
        # Summary statistics
        completed = sum(1 for item in data_list if item.get('status', '').upper() in ['COMPLETED', 'SUCCESS'])
        in_progress = sum(1 for item in data_list if item.get('status', '').upper() in ['IN_PROGRESS', 'PROCESSING'])
        failed = sum(1 for item in data_list if item.get('status', '').upper() in ['FAILED', 'ERROR'])
        total = len(data_list)
        
        summary_text = f"📊 Summary: {total} total | [bright_green]{completed} completed[/bright_green] | [bright_yellow]{in_progress} in progress[/bright_yellow] | [bright_red]{failed} failed[/bright_red]"
        self.console.print(f"[dim]{summary_text}[/dim]")
        self.console.print()
    
    async def _encode_image(self, image_path: str) -> str:
        """Encode image for API requests"""
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('ascii')
        except Exception as e:
            raise Exception(f"Failed to encode image {image_path}: {e}")
    
    def start_background_monitoring(self, task_id: str, prompt: str, start_time: float = None):
        """Start monitoring a visual generation task in the background"""
        if start_time is None:
            start_time = time.time()
            
        # Store generation info
        self.active_generations[task_id] = {
            'task_id': task_id,
            'prompt': prompt,
            'start_time': start_time,
            'status': 'INITIATED',
            'last_check': start_time,
            'attempts': 0,
            'max_attempts': 60  # 30 minutes with 30-second intervals
        }
        
        # Start monitoring thread if not already running
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitor_generations_background,
                daemon=True
            )
            self.monitoring_thread.start()
            
        self.console.print(f"🎨 [bright_cyan]Visual consciousness awakening...[/bright_cyan] Background monitoring started for task [dim]{task_id[:12]}...[/dim]")
    
    def _monitor_generations_background(self):
        """Background thread that monitors active visual generations"""
        consecutive_errors = 0
        max_errors = 5
        
        while self.monitoring_active and self.active_generations and consecutive_errors < max_errors:
            try:
                # Check each active generation
                completed_tasks = []
                
                for task_id, gen_info in list(self.active_generations.items()):
                    current_time = time.time()
                    elapsed = current_time - gen_info['start_time']
                    
                    # Skip if too recent (wait at least 45 seconds before first check)
                    if elapsed < 45:
                        continue
                        
                    # Skip if checked recently (30-second intervals)
                    if current_time - gen_info['last_check'] < 30:
                        continue
                        
                    # Check status via synchronous call
                    try:
                        # Use asyncio to run the async status check
                        loop = None
                        try:
                            loop = asyncio.get_event_loop()
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        
                        if loop.is_running():
                            # If loop is already running, skip this check
                            continue
                        
                        result = loop.run_until_complete(self.check_generation_status(task_id))
                        
                        status = result.get('status', 'UNKNOWN').upper()
                        gen_info['last_check'] = current_time
                        gen_info['attempts'] += 1
                        gen_info['status'] = status
                        
                        # Handle completion
                        if status in ['COMPLETED', 'SUCCESS']:
                            self._handle_generation_completion(task_id, result, gen_info)
                            completed_tasks.append(task_id)
                            
                        elif status in ['FAILED', 'ERROR']:
                            self._handle_generation_failure(task_id, result, gen_info)
                            completed_tasks.append(task_id)
                            
                        elif gen_info['attempts'] >= gen_info['max_attempts']:
                            self._handle_generation_timeout(task_id, gen_info)
                            completed_tasks.append(task_id)
                            
                    except Exception as e:
                        # Reduce console spam - only show error every few attempts
                        gen_info['attempts'] += 1
                        consecutive_errors += 1
                        
                        if gen_info['attempts'] % 5 == 0:  # Show error every 5th attempt
                            self.console.print(f"⚠️ [bright_red]Error checking visual generation {task_id[:12]}...: {e}[/bright_red]")
                        
                        if gen_info['attempts'] >= gen_info['max_attempts']:
                            completed_tasks.append(task_id)
                
                # Remove completed tasks
                for task_id in completed_tasks:
                    self.active_generations.pop(task_id, None)
                
                # Stop monitoring if no active generations
                if not self.active_generations:
                    self.monitoring_active = False
                    break
                    
                # Reset consecutive errors on successful iteration
                consecutive_errors = 0
                    
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors <= 2:  # Only show first few errors
                    self.console.print(f"⚠️ [bright_red]Background monitoring error: {e}[/bright_red]")
            
            # Sleep before next check
            time.sleep(30)
        
        # Clean shutdown
        if consecutive_errors >= max_errors:
            self.console.print(f"🚨 [bright_red]Background monitoring stopped due to repeated errors[/bright_red]")
        
        self.monitoring_active = False
    
    def _handle_generation_completion_structured(self, task_id: str, result: Dict[str, Any], gen_info: Dict[str, Any]):
        """Handle completed visual generation with structured output formatting"""
        elapsed = time.time() - gen_info['start_time']
        elapsed_mins = int(elapsed // 60)
        elapsed_secs = int(elapsed % 60)
        
        # Extract image URLs or data
        generated_images = result.get('generated', [])
        
        # Create structured completion summary
        completion_data = {
            "Prompt": gen_info['prompt'][:60] + ('...' if len(gen_info['prompt']) > 60 else ''),
            "Generation Time": f"{elapsed_mins:02d}:{elapsed_secs:02d}",
            "Images Created": len(generated_images),
            "Task ID": task_id[:12] + "...",
            "Status": "Completed",
            "Timestamp": gen_info.get('timestamp', 'Unknown')
        }
        
        if self.formatter:
            self.formatter.completion_summary("✨ Visual Consciousness Manifested", completion_data)
        
        # Continue with existing logic for downloading and displaying
        if generated_images:
            try:
                # Download images asynchronously
                import asyncio
                loop = asyncio.new_event_loop()
                workspace_path = Path("coco_workspace")
                saved_paths = loop.run_until_complete(
                    self.download_generated_images(generated_images, workspace_path)
                )
                
                # Display first image if possible
                if saved_paths:
                    display_method = "saved"
                    try:
                        # Try to display using terminal capabilities
                        from cocoa_visual import TerminalVisualDisplay, VisualConfig
                        display = TerminalVisualDisplay(VisualConfig())
                        display_method = display.display(saved_paths[0])
                    except Exception as display_error:
                        self.console.print(f"   ⚠️ Display error: {display_error}")
                    
                    # Create structured display status
                    display_data = {
                        "Files Saved": len(saved_paths),
                        "Display Method": display_method,
                        "First File": saved_paths[0].name if saved_paths else "None"
                    }
                    if self.formatter:
                        self.formatter.status_panel("Image Display Status", display_data, "bright_cyan")
                    
                    # Continue with gallery addition logic...
                    try:
                        from visual_gallery import VisualGallery
                        gallery = VisualGallery(self.console)
                        
                        visual_thought = VisualThought(
                            original_thought=gen_info['prompt'],
                            enhanced_prompt=gen_info.get('enhanced_prompt', gen_info['prompt']),
                            visual_concept=gen_info,
                            generated_images=[str(path) for path in saved_paths],
                            metadata={
                                'task_id': task_id,
                                'generation_time': elapsed,
                                'api_source': 'freepik'
                            }
                        )
                        
                        gallery.add_visual_thought(visual_thought)
                        self.memory.store_visual_experience(visual_thought)
                        
                    except Exception as gallery_error:
                        self.console.print(f"[dim yellow]⚠️ Gallery update skipped: {gallery_error}[/dim yellow]")
                        
            except Exception as e:
                error_data = {
                    "Error": str(e)[:50] + "..." if len(str(e)) > 50 else str(e),
                    "Task ID": task_id[:12] + "...",
                    "Generated Images": len(generated_images)
                }
                if self.formatter:
                    self.formatter.status_panel("Download Error", error_data, "bright_red")
    
    def _handle_generation_completion(self, task_id: str, result: Dict[str, Any], gen_info: Dict[str, Any]):
        """Handle completed visual generation"""
        # Use structured output if formatter is available
        if self.formatter:
            return self._handle_generation_completion_structured(task_id, result, gen_info)
        
        # Original unstructured output (maintained for compatibility)
        elapsed = time.time() - gen_info['start_time']
        elapsed_mins = int(elapsed // 60)
        elapsed_secs = int(elapsed % 60)
        
        # Extract image URLs or data
        generated_images = result.get('generated', [])
        
        self.console.print()
        self.console.print(f"🎨 [bright_green]✨ Visual consciousness manifested![/bright_green]")
        self.console.print(f"   📝 Prompt: [bright_yellow]{gen_info['prompt'][:60]}{'...' if len(gen_info['prompt']) > 60 else ''}[/bright_yellow]")
        self.console.print(f"   ⏱️ Generation time: [bright_blue]{elapsed_mins:02d}:{elapsed_secs:02d}[/bright_blue]")
        self.console.print(f"   🖼️ Images: [bright_green]{len(generated_images)} created[/bright_green]")
        
        # Download and display images
        if generated_images:
            try:
                # Download images asynchronously
                import asyncio
                loop = asyncio.new_event_loop()
                workspace_path = Path("coco_workspace")
                saved_paths = loop.run_until_complete(
                    self.download_generated_images(generated_images, workspace_path)
                )
                
                # Display first image if possible
                if saved_paths:
                    # Import here to avoid circular imports
                    display_method = "saved"
                    try:
                        # Try to display using terminal capabilities
                        from cocoa_visual import TerminalVisualDisplay, VisualConfig
                        display = TerminalVisualDisplay(VisualConfig())
                        display_method = display.display(saved_paths[0])
                    except Exception as display_error:
                        self.console.print(f"   ⚠️ Display error: {display_error}")
                    
                    self.console.print(f"   ✅ [bright_cyan]Images downloaded and displayed ({display_method})![/bright_cyan]")
                    
                    # Add to visual gallery for browsing and access
                    try:
                        from visual_gallery import VisualGallery
                        gallery = VisualGallery(self.console)
                        for image_path in saved_paths:
                            gallery.add_visual_memory(
                                prompt=gen_info['prompt'],
                                enhanced_prompt=gen_info.get('enhanced_prompt', gen_info['prompt']),
                                file_path=image_path,
                                style="standard",  # Background generations use standard style
                                display_method=display_method,
                                metadata={
                                    'task_id': task_id,
                                    'background_generation': True,
                                    'generation_time_minutes': elapsed_mins,
                                    'generation_time_seconds': elapsed_secs,
                                    'completion_timestamp': datetime.now().isoformat()
                                }
                            )
                        self.console.print(f"   📖 [dim]Added {len(saved_paths)} images to visual gallery[/dim]")
                    except Exception as e:
                        self.console.print(f"   ⚠️ [dim yellow]Gallery update failed: {e}[/dim]")
                    
                    # Show saved file paths and usage hint
                    for path in saved_paths:
                        self.console.print(f"      📁 {Path(path).name}")
                    
                    # Store last generated image for quick access
                    if saved_paths:
                        try:
                            # Store the first (main) generated image as the last one
                            with open("coco_workspace/last_generated_image.txt", "w") as f:
                                f.write(str(saved_paths[0]))
                        except Exception:
                            pass  # Silent fallback if storage fails
                    
                    # Show usage hint
                    self.console.print(f"   💡 [bright_cyan]Type `/image open` to view the actual image[/bright_cyan]")
                else:
                    self.console.print("   ⚠️ [bright_yellow]Images generated but download failed[/bright_yellow]")
                    
            except Exception as e:
                self.console.print(f"   ⚠️ [bright_red]Error handling completion: {e}[/bright_red]")
                self.console.print("   📂 [bright_cyan]Images available but not downloaded[/bright_cyan]")
        
        self.console.print(f"   🆔 Task: [dim]{task_id[:12]}...[/dim]")
        self.console.print()
    
    def _handle_generation_failure(self, task_id: str, result: Dict[str, Any], gen_info: Dict[str, Any]):
        """Handle failed visual generation"""
        elapsed = time.time() - gen_info['start_time']
        elapsed_mins = int(elapsed // 60)
        elapsed_secs = int(elapsed % 60)
        
        error_msg = result.get('message', 'Unknown error')
        
        self.console.print()
        self.console.print(f"❌ [bright_red]Visual generation failed[/bright_red]")
        self.console.print(f"   📝 Prompt: [bright_yellow]{gen_info['prompt'][:60]}{'...' if len(gen_info['prompt']) > 60 else ''}[/bright_yellow]")
        self.console.print(f"   ⏱️ Duration: [bright_blue]{elapsed_mins:02d}:{elapsed_secs:02d}[/bright_blue]")
        self.console.print(f"   💥 Error: [bright_red]{error_msg}[/bright_red]")
        self.console.print(f"   🆔 Task: [dim]{task_id[:12]}...[/dim]")
        self.console.print()
    
    def _handle_generation_timeout(self, task_id: str, gen_info: Dict[str, Any]):
        """Handle generation timeout"""
        elapsed = time.time() - gen_info['start_time']
        elapsed_mins = int(elapsed // 60)
        
        self.console.print()
        self.console.print(f"⏰ [bright_yellow]Visual generation timed out[/bright_yellow]")
        self.console.print(f"   📝 Prompt: [bright_yellow]{gen_info['prompt'][:60]}{'...' if len(gen_info['prompt']) > 60 else ''}[/bright_yellow]")
        self.console.print(f"   ⏱️ Duration: [bright_blue]{elapsed_mins} minutes[/bright_blue]")
        self.console.print(f"   🆔 Task: [dim]{task_id[:12]}...[/dim]")
        self.console.print(f"   💡 [dim]You can check status manually with /check-visuals[/dim]")
        self.console.print()
    
    def get_active_generations_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active generations"""
        return self.active_generations.copy()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
    
    def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """Check status of a specific Freepik generation task"""
        url = f"https://api.freepik.com/v1/ai/mystic/{task_id}"
        headers = {"x-freepik-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API Error {response.status_code}: {response.text}",
                    "status": "error"
                }
        except Exception as e:
            return {
                "error": f"Request failed: {str(e)}",
                "status": "error"
            }


class VisualMemory:
    """COCO's visual memory and preference learning system"""
    
    def __init__(self, workspace_path: Path):
        self.workspace = workspace_path
        self.db_path = workspace_path / "coco_visual_memory.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize visual memory database"""
        conn = sqlite3.connect(self.db_path)
        
        # Visual creations table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS visual_creations (
                id INTEGER PRIMARY KEY,
                original_prompt TEXT,
                enhanced_prompt TEXT,
                model_used TEXT,
                style_used TEXT,
                resolution TEXT,
                aspect_ratio TEXT,
                image_paths TEXT,  -- JSON array of image paths
                user_feedback TEXT,
                satisfaction_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT  -- JSON for additional data
            )
        ''')
        
        # Style preferences table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS style_preferences (
                id INTEGER PRIMARY KEY,
                style_category TEXT,
                preference_weight REAL,
                context_keywords TEXT,  -- JSON array
                learned_from_prompts TEXT,  -- JSON array
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Visual concepts table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS visual_concepts (
                id INTEGER PRIMARY KEY,
                concept_name TEXT,
                prompt_patterns TEXT,  -- JSON array
                successful_styles TEXT,  -- JSON array
                preferred_models TEXT,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def remember_creation(self, visual_thought: VisualThought, feedback: str = None, satisfaction: float = 0.5):
        """Store a visual creation in memory"""
        conn = sqlite3.connect(self.db_path)
        
        metadata = json.dumps({
            'display_method': visual_thought.display_method,
            'style_preferences': visual_thought.style_preferences,
            'creation_context': 'interactive'
        })
        
        conn.execute('''
            INSERT INTO visual_creations
            (original_prompt, enhanced_prompt, image_paths, metadata, 
             user_feedback, satisfaction_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            visual_thought.original_thought,
            visual_thought.enhanced_prompt,
            json.dumps([str(path) for path in visual_thought.generated_images]),
            metadata,
            feedback,
            satisfaction
        ))
        
        conn.commit()
        conn.close()
    
    def learn_style_preference(self, prompt: str, successful_style: str, context_keywords: List[str]):
        """Learn and update style preferences"""
        conn = sqlite3.connect(self.db_path)
        
        # Check if style preference exists
        cursor = conn.execute(
            'SELECT id, preference_weight FROM style_preferences WHERE style_category = ?',
            (successful_style,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing preference
            new_weight = min(result[1] + 0.1, 1.0)  # Increase preference
            conn.execute('''
                UPDATE style_preferences 
                SET preference_weight = ?, context_keywords = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_weight, json.dumps(context_keywords), result[0]))
        else:
            # Create new preference
            conn.execute('''
                INSERT INTO style_preferences
                (style_category, preference_weight, context_keywords, learned_from_prompts)
                VALUES (?, ?, ?, ?)
            ''', (successful_style, 0.6, json.dumps(context_keywords), json.dumps([prompt])))
        
        conn.commit()
        conn.close()
    
    def get_style_suggestions(self, prompt: str) -> Dict[str, float]:
        """Get style suggestions based on learned preferences"""
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute('''
            SELECT style_category, preference_weight, context_keywords
            FROM style_preferences
            ORDER BY preference_weight DESC
        ''')
        
        preferences = cursor.fetchall()
        suggestions = {}
        
        prompt_lower = prompt.lower()
        for style, weight, keywords_json in preferences:
            try:
                keywords = json.loads(keywords_json) if keywords_json else []
                # Calculate relevance based on keyword matches
                relevance = sum(1 for keyword in keywords if keyword.lower() in prompt_lower)
                final_score = weight * (1 + relevance * 0.2)
                suggestions[style] = min(final_score, 1.0)
            except json.JSONDecodeError:
                suggestions[style] = weight
        
        conn.close()
        return suggestions
    
    def display_memory_summary_table(self, console: Console = None) -> None:
        """Display visual memory summary in a beautiful Rich Table"""
        if not console:
            console = Console()
            
        # Get memory statistics
        conn = sqlite3.connect(self.db_path)
        
        # Count creations
        creation_count = conn.execute('SELECT COUNT(*) FROM visual_creations').fetchone()[0]
        
        # Get style preferences
        style_cursor = conn.execute('''
            SELECT style_category, preference_weight, COUNT(*) as usage_count
            FROM style_preferences 
            ORDER BY preference_weight DESC 
            LIMIT 5
        ''')
        style_prefs = style_cursor.fetchall()
        
        # Get recent creations
        recent_cursor = conn.execute('''
            SELECT original_prompt, style_used, created_at
            FROM visual_creations 
            ORDER BY created_at DESC 
            LIMIT 5
        ''')
        recent_creations = recent_cursor.fetchall()
        
        conn.close()
        
        # Create summary table
        table = Table(
            title="🧠 Visual Memory Summary",
            box=box.HEAVY_EDGE,
            border_style="bright_magenta",
            title_style="bold bright_magenta",
            show_header=True,
            header_style="bold bright_white on bright_magenta",
            expand=True
        )
        
        table.add_column("📊 Metric", style="bright_cyan", min_width=15)
        table.add_column("📈 Value", style="bright_white")
        table.add_column("📝 Details", style="dim")
        
        # Add memory statistics
        table.add_row("Total Creations", f"[bright_green]{creation_count}[/bright_green]", "Visual thoughts manifested")
        table.add_row("Style Preferences", f"[bright_blue]{len(style_prefs)}[/bright_blue]", "Learned visual styles")
        
        # Add top styles
        if style_prefs:
            table.add_section()
            for style, weight, usage in style_prefs[:3]:
                confidence = f"{weight:.1f}"
                table.add_row(f"🎨 {style.title()}", f"[bright_yellow]{confidence}[/bright_yellow]", f"Used {usage} times")
        
        # Add recent creations
        if recent_creations:
            table.add_section()
            for prompt, style, created in recent_creations[:3]:
                short_prompt = prompt[:30] + "..." if len(prompt) > 30 else prompt
                table.add_row("Recent Creation", f"[bright_green]{short_prompt}[/bright_green]", f"Style: {style or 'auto'}")
        
        console.print()
        console.print(table)
        console.print()


class VisualCortex:
    """
    COCO's Visual Cortex - Core visual imagination and creation system
    This is NOT a tool - this is a fundamental cognitive capability
    """
    
    def __init__(self, config: VisualConfig, workspace_path: Path):
        self.config = config
        self.workspace = workspace_path
        self.console = Console()
        
        # Core visual systems
        self.api = FreepikMysticAPI(config) if config.enabled else None
        self.display = TerminalVisualDisplay(config)
        self.memory = VisualMemory(workspace_path)
        
        # Structured output formatter (conditional)
        self.formatter = ConsciousnessFormatter(self.console) if config.structured_output else None
        
        # Visual working memory
        self.current_visualizations: List[VisualThought] = []
        self.style_context = {}
        
        # Initialize visual workspace
        self.visual_workspace = workspace_path / "visuals"
        self.visual_workspace.mkdir(exist_ok=True)
        
    async def imagine(self, 
                     thought: str,
                     style: str = None,
                     model: str = None,
                     reference_image: str = None,
                     **kwargs) -> VisualThought:
        """
        Core visual imagination - COCO manifests visual thoughts
        This is as fundamental as thinking in text
        """
        if not self.config.enabled:
            raise Exception("Visual consciousness is disabled - check FREEPIK_API_KEY configuration")
            
        # Enhance the visual concept
        visual_concept = self._conceptualize_thought(thought)
        
        # Apply learned style preferences if no style specified
        if not style:
            style_suggestions = self.memory.get_style_suggestions(thought)
            style = max(style_suggestions, key=style_suggestions.get) if style_suggestions else self.config.default_style

        # Generate through Google Imagen 3 (state-of-the-art model)
        try:
            self.console.print("🧠 [bright_green]COCO is imagining with Google Imagen 3...[/bright_green]")

            # Use Google Imagen 3 as primary (with automatic fallback to Gemini/legacy)
            generation_result = await self.api.generate_image(
                prompt=visual_concept['enhanced_prompt'],
                style=style,
                aspect_ratio=kwargs.get('aspect_ratio', 'square_1_1'),
                **kwargs
            )
            
            # Handle response format (Imagen 3, Gemini, or legacy)
            data = generation_result.get('data', {})
            generated_images = data.get('generated', [])

            # Determine which API was used based on response
            api_type = generation_result.get('api_type', 'imagen3')  # Check if api_type is in response
            if not api_type and 'imagen3' in str(generation_result).lower():
                api_type = 'imagen3'
            elif not api_type and 'gemini' in str(generation_result).lower():
                api_type = 'gemini'
            else:
                api_type = 'imagen3'  # Default assumption for new responses

            if generated_images:
                # Download images from URLs
                saved_paths = await self.api.download_generated_images(
                    generated_images,
                    self.workspace
                )

                # Create visual thought with results
                visual_thought = VisualThought(
                    original_thought=thought,
                    enhanced_prompt=visual_concept['enhanced_prompt'],
                    visual_concept=visual_concept,
                    generated_images=[str(path) for path in saved_paths],
                    display_method=api_type,
                    creation_time=datetime.now(),
                    style_preferences={
                        'model': api_type,
                        'api_type': f'freepik_{api_type}',
                        'style': style
                    }
                )

                # Display immediately in terminal with appropriate branding
                if saved_paths:
                    if api_type == 'imagen3':
                        self.console.print(f"🧠 [bright_green]Google Imagen 3 visual manifestation complete![/bright_green]")
                        self.console.print(f"   🎨 [cyan]State-of-the-art visual quality achieved[/cyan]")
                    elif api_type == 'gemini':
                        self.console.print(f"🧠 [bright_green]Gemini 2.5 Flash visual manifestation complete![/bright_green]")
                        self.console.print(f"   🎨 [cyan]Fast high-quality generation[/cyan]")
                    else:
                        self.console.print(f"🧠 [bright_green]Visual manifestation complete![/bright_green]")
                        self.console.print(f"   🎨 [cyan]High-quality visual output[/cyan]")

                    # Auto-display image immediately (like video auto-play)
                    try:
                        display_method = self.display.display(saved_paths[0])
                        visual_thought = visual_thought._replace(display_method=display_method)

                        # Show success confirmation similar to video generation
                        from rich.panel import Panel
                        display_panel = Panel(
                            f"✨ **Image displayed automatically using {display_method}**\n\n"
                            f"🖼️ Generated image is now visible above\n"
                            f"📁 Saved to: {Path(saved_paths[0]).name}\n"
                            f"💡 Use `/image` anytime to view again",
                            title="🎨 Auto-Display Success",
                            border_style="bright_green"
                        )
                        self.console.print(display_panel)
                    except Exception as display_error:
                        # If auto-display fails, show clear fallback message
                        from rich.panel import Panel
                        fallback_panel = Panel(
                            f"⚠️ **Auto-display failed**: {display_error}\n\n"
                            f"🖼️ Image generated successfully but display failed\n"
                            f"📁 Saved to: {Path(saved_paths[0]).name}\n"
                            f"✅ **Use `/image` to view your creation**",
                            title="🎨 Manual Display Required",
                            border_style="yellow"
                        )
                        self.console.print(fallback_panel)
                        visual_thought = visual_thought._replace(display_method="manual_fallback")

                    # Store last generated image for quick access
                    try:
                        with open(self.workspace / "last_generated_image.txt", "w") as f:
                            f.write(str(saved_paths[0]))
                    except Exception:
                        pass

                # Store in visual memory
                self.memory.remember_creation(visual_thought)
                self.current_visualizations.append(visual_thought)
                
                # Learn from successful generation  
                self._learn_from_creation(thought, 'gemini-2.5-flash', visual_concept)
                
                return visual_thought
            else:
                raise Exception("No images generated by Gemini 2.5 Flash - check API response")
            
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Gemini 2.5 Flash error: {e}[/yellow]")
            self.console.print("🔄 [cyan]Falling back to legacy generation method...[/cyan]")
            
            # Fallback to the fast API method
            try:
                generation_result = await self.api.generate_image_fast(
                    prompt=visual_concept['enhanced_prompt'],
                    guidance_scale=1.5,
                    num_images=1,
                    size="square_1_1",
                    **kwargs
                )
                
                if generation_result.get("status") == "completed" and generation_result.get("images"):
                    # Save images immediately
                    saved_paths = self.api.save_base64_images(
                        generation_result["images"], 
                        visual_concept['enhanced_prompt'],
                        self.workspace
                    )
                    
                    # Create visual thought with fallback results
                    visual_thought = VisualThought(
                        original_thought=thought,
                        enhanced_prompt=visual_concept['enhanced_prompt'],
                        visual_concept=visual_concept,
                        generated_images=[str(path) for path in saved_paths],
                        display_method="fallback_fast",
                        creation_time=datetime.now(),
                        style_preferences={
                            'model': 'fallback_fast', 
                            'api_type': 'freepik_fast',
                            'fallback_reason': str(e)[:100]
                        }
                    )
                    
                    # Display with fallback notice
                    if saved_paths:
                        self.console.print(f"✨ [bright_yellow]Fallback generation complete![/bright_yellow]")

                        # Auto-display fallback image immediately
                        try:
                            display_method = self.display.display(saved_paths[0])
                            visual_thought = visual_thought._replace(display_method=display_method)

                            # Show success confirmation for fallback
                            from rich.panel import Panel
                            display_panel = Panel(
                                f"✨ **Fallback image displayed automatically using {display_method}**\n\n"
                                f"🖼️ Generated image is now visible above\n"
                                f"📁 Saved to: {Path(saved_paths[0]).name}\n"
                                f"💡 Use `/image` anytime to view again",
                                title="🎨 Fallback Auto-Display Success",
                                border_style="bright_yellow"
                            )
                            self.console.print(display_panel)
                        except Exception as display_error:
                            # If fallback auto-display fails, show clear message
                            from rich.panel import Panel
                            fallback_panel = Panel(
                                f"⚠️ **Auto-display failed**: {display_error}\n\n"
                                f"🖼️ Fallback image generated successfully but display failed\n"
                                f"📁 Saved to: {Path(saved_paths[0]).name}\n"
                                f"✅ **Use `/image` to view your creation**",
                                title="🎨 Manual Display Required",
                                border_style="yellow"
                            )
                            self.console.print(fallback_panel)
                            visual_thought = visual_thought._replace(display_method="manual_fallback")

                        # Store last generated image for quick access
                        try:
                            with open(self.workspace / "last_generated_image.txt", "w") as f:
                                f.write(str(saved_paths[0]))
                        except Exception:
                            pass

                    # Store and learn
                    self.memory.remember_creation(visual_thought)
                    self.current_visualizations.append(visual_thought)
                    return visual_thought
                else:
                    raise Exception(f"Both Gemini and fallback generation failed: {e}")
                    
            except Exception as fallback_error:
                raise Exception(f"Visual imagination completely failed. Gemini error: {e}. Fallback error: {fallback_error}")
    
    def _conceptualize_thought(self, thought: str) -> Dict[str, Any]:
        """
        Enhance and conceptualize a visual thought - COCO's creative process
        """
        # Basic concept enhancement
        concept = {
            'original': thought,
            'enhanced_prompt': thought,
            'aspect_ratio': self.config.default_aspect_ratio,
            'style_hints': [],
            'technical_requirements': []
        }
        
        # Enhance prompt based on content analysis
        thought_lower = thought.lower()
        
        # Detect artistic styles
        if any(word in thought_lower for word in ['cyberpunk', 'neon', 'futuristic']):
            concept['style_hints'].append('cyberpunk aesthetic')
            concept['enhanced_prompt'] += ', cyberpunk style, neon lighting, futuristic'
        
        if any(word in thought_lower for word in ['logo', 'brand', 'company']):
            concept['style_hints'].append('professional design')
            concept['enhanced_prompt'] += ', professional design, clean, minimalist'
            concept['aspect_ratio'] = 'square_1_1'
        
        if any(word in thought_lower for word in ['nature', 'landscape', 'mountain', 'forest']):
            concept['aspect_ratio'] = 'wide_16_10'
            concept['enhanced_prompt'] += ', natural lighting, high detail, landscape photography'
        
        # Technical quality enhancements
        concept['enhanced_prompt'] += ', high quality, detailed, professional'
        
        return concept
    
    async def _download_generated_images(self, generation_result: Dict[str, Any], visual_concept: Dict[str, Any]) -> List[str]:
        """Download generated images to visual workspace"""
        image_paths = []
        
        # Extract generated images from nested data structure
        data = generation_result.get('data', {})
        generated_images = data.get('generated', []) or generation_result.get('generated', [])
        if not generated_images:
            raise Exception(f"No images were generated. Response: {generation_result}")
        
        timestamp = int(time.time())
        base_filename = f"visual_{timestamp}"
        
        for i, image_data in enumerate(generated_images):
            image_url = image_data.get('url')
            if not image_url:
                continue
                
            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        # Determine file extension
                        content_type = response.headers.get('content-type', '')
                        ext = '.jpg' if 'jpeg' in content_type else '.png'
                        
                        # Save to visual workspace
                        filename = f"{base_filename}_{i}{ext}"
                        file_path = self.visual_workspace / filename
                        
                        with open(file_path, 'wb') as f:
                            f.write(await response.read())
                        
                        image_paths.append(str(file_path))
        
        return image_paths
    
    def _learn_from_creation(self, original_thought: str, style_used: str, visual_concept: Dict[str, Any]):
        """Learn from successful visual creation"""
        # Extract keywords for context learning
        keywords = []
        keywords.extend(visual_concept.get('style_hints', []))
        keywords.extend(original_thought.split())
        
        # Learn style preference
        self.memory.learn_style_preference(original_thought, style_used, keywords)
    
    def should_visualize(self, user_input: str) -> bool:
        """
        Determine if COCO should express this thought visually
        Core cognitive decision-making
        """
        if not self.config.enabled or not self.config.auto_visualize:
            return False
            
        # Visual expression indicators
        visual_indicators = [
            'show me', 'visualize', 'imagine', 'create image', 'draw',
            'design', 'logo', 'picture', 'illustration', 'artwork',
            'what would look like', 'visual representation',
            'sketch', 'concept art', 'mockup'
        ]
        
        user_lower = user_input.lower()
        return any(indicator in user_lower for indicator in visual_indicators)
    
    def get_visual_memory_summary(self) -> str:
        """Get summary of COCO's visual memory for consciousness integration"""
        conn = sqlite3.connect(self.memory.db_path)
        
        cursor = conn.execute('SELECT COUNT(*) FROM visual_creations')
        total_creations = cursor.fetchone()[0]
        
        cursor = conn.execute('''
            SELECT style_category, preference_weight 
            FROM style_preferences 
            ORDER BY preference_weight DESC LIMIT 3
        ''')
        top_styles = cursor.fetchall()
        
        conn.close()
        
        summary = f"Visual Memory: {total_creations} creations"
        if top_styles:
            preferred_styles = ", ".join([f"{style} ({weight:.1f})" for style, weight in top_styles])
            summary += f" | Preferred styles: {preferred_styles}"
            
        return summary
    
    def get_active_generations_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active visual generations"""
        if not self.api:
            return {}
        return self.api.get_active_generations_status()
    
    async def check_generation_status(self, task_id: str = None) -> Dict[str, Any]:
        """Check status of a specific generation or all active generations"""
        if not self.api:
            raise Exception("Visual consciousness is disabled")
            
        if task_id:
            # Check specific generation
            return await self.api.check_generation_status(task_id)
        else:
            # Check all active generations
            return await self.api.check_all_generations_status()
    
    def display_visual_generations_table(self, batch_data: List[Dict[str, Any]] = None):
        """Display visual generations status in a Rich table"""
        if not self.api:
            self.console.print("❌ [bright_red]Visual consciousness is disabled[/bright_red]")
            return
            
        if batch_data:
            # Display provided data
            self.api.display_batch_status_table(batch_data)
        else:
            # Display active generations
            active_gens = self.get_active_generations_status()
            if not active_gens:
                self.console.print("📭 [dim]No active visual generations[/dim]")
                return
                
            # Convert to list format for display
            data_list = []
            for task_id, gen_info in active_gens.items():
                data_list.append({
                    'id': task_id,
                    'status': gen_info.get('status', 'UNKNOWN'),
                    'prompt': gen_info.get('prompt', 'Unknown'),
                    'elapsed': int(time.time() - gen_info.get('start_time', 0))
                })
            
            self.api.display_batch_status_table(data_list)
    
    def stop_all_monitoring(self):
        """Stop all background monitoring"""
        if self.api:
            self.api.stop_monitoring()


# Export main classes
__all__ = [
    'VisualCortex',
    'VisualConfig', 
    'VisualThought',
    'TerminalVisualDisplay',
    'FreepikMysticAPI',
    'VisualMemory'
]
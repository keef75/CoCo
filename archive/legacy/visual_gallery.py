#!/usr/bin/env python3
"""
COCO Visual Gallery System
Manages visual memory, browsing, and access to generated images

ASCII art represents COCO's visual perception
Real image files represent persistent visual memory
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.columns import Columns
from rich.text import Text
from rich.layout import Layout
from rich.align import Align

# Try to import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

@dataclass
class VisualMemory:
    """Represents a single visual memory entry"""
    id: str
    prompt: str
    enhanced_prompt: str
    style: str
    file_path: str
    ascii_preview: str
    creation_time: str
    file_size: int
    dimensions: tuple
    display_method: str
    metadata: dict

class VisualGallery:
    """COCO's visual consciousness gallery and memory system"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.workspace_dir = Path("coco_workspace")
        self.visuals_dir = self.workspace_dir / "visuals"
        self.gallery_metadata_file = self.workspace_dir / "visual_memory.json"
        
        # Ensure directories exist
        self.visuals_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing visual memories
        self.visual_memories: List[VisualMemory] = self._load_visual_memories()
    
    def _load_visual_memories(self) -> List[VisualMemory]:
        """Load visual memories from metadata file"""
        if not self.gallery_metadata_file.exists():
            return []
        
        try:
            with open(self.gallery_metadata_file, 'r') as f:
                data = json.load(f)
            
            memories = []
            for item in data.get('visual_memories', []):
                # Ensure file still exists
                if Path(item['file_path']).exists():
                    memory = VisualMemory(**item)
                    memories.append(memory)
            
            return memories
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Could not load visual memories: {e}[/]")
            return []
    
    def _save_visual_memories(self) -> None:
        """Save visual memories to metadata file"""
        try:
            data = {
                'visual_memories': [asdict(memory) for memory in self.visual_memories],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.gallery_metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.console.print(f"[red]❌ Could not save visual memories: {e}[/]")
    
    def add_visual_memory(self, 
                         prompt: str, 
                         enhanced_prompt: str,
                         file_path: str,
                         style: str = "standard",
                         display_method: str = "ASCII",
                         metadata: dict = None) -> str:
        """Add a new visual memory entry"""
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        # Generate unique ID
        memory_id = f"vis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.visual_memories)}"
        
        # Get file info
        file_size = file_path_obj.stat().st_size
        dimensions = (0, 0)
        
        if PIL_AVAILABLE:
            try:
                with Image.open(file_path) as img:
                    dimensions = img.size
            except Exception:
                pass
        
        # Generate ASCII preview
        ascii_preview = self._generate_ascii_preview(file_path, style="minimal")
        
        # Create visual memory
        visual_memory = VisualMemory(
            id=memory_id,
            prompt=prompt,
            enhanced_prompt=enhanced_prompt,
            style=style,
            file_path=str(file_path),
            ascii_preview=ascii_preview,
            creation_time=datetime.now().isoformat(),
            file_size=file_size,
            dimensions=dimensions,
            display_method=display_method,
            metadata=metadata or {}
        )
        
        self.visual_memories.append(visual_memory)
        self._save_visual_memories()
        
        return memory_id
    
    def _generate_ascii_preview(self, image_path: str, style: str = "minimal", width: int = 40) -> str:
        """Generate a small ASCII preview for gallery display"""
        if not PIL_AVAILABLE:
            return "[Preview unavailable - PIL not installed]"
        
        try:
            img = Image.open(image_path)
            aspect_ratio = img.size[1] / img.size[0]
            height = int(aspect_ratio * width * 0.55)
            
            img = img.resize((width, height)).convert("L")
            
            # Use minimal character set for previews
            ascii_chars = " .-=+*#@"
            pixel_data = img.getdata()
            
            ascii_str = "".join([ascii_chars[min(pixel * len(ascii_chars) // 256, len(ascii_chars) - 1)] for pixel in pixel_data])
            ascii_lines = [ascii_str[i:i+width] for i in range(0, len(ascii_str), width)]
            
            return "\n".join(ascii_lines)
        except Exception:
            return "[Preview generation failed]"
    
    def show_gallery(self, limit: int = 10, style: str = "grid") -> None:
        """Display visual gallery with different viewing styles"""
        if not self.visual_memories:
            self.console.print(Panel(
                "[yellow]No visual memories found yet.\nGenerate some images first![/]",
                title="🎨 Visual Gallery",
                border_style="bright_yellow"
            ))
            return
        
        # Sort by creation time (newest first)
        sorted_memories = sorted(self.visual_memories, key=lambda x: x.creation_time, reverse=True)
        display_memories = sorted_memories[:limit]
        
        if style == "grid":
            self._show_gallery_grid(display_memories)
        elif style == "list":
            self._show_gallery_list(display_memories)
        elif style == "detailed":
            self._show_gallery_detailed(display_memories)
        else:
            self._show_gallery_table(display_memories)
    
    def _show_gallery_grid(self, memories: List[VisualMemory]) -> None:
        """Show gallery in grid format with ASCII previews"""
        self.console.print(Panel(
            f"🎨 Visual Gallery - {len(memories)} Recent Memories",
            border_style="bright_cyan",
            expand=False
        ))
        
        # Create grid of visual memories
        panels = []
        for memory in memories:
            # Create mini preview panel
            preview_text = memory.ascii_preview[:200] + "..." if len(memory.ascii_preview) > 200 else memory.ascii_preview
            
            memory_panel = Panel(
                f"[dim]{preview_text}[/dim]\n\n[bright_white]{memory.prompt[:40]}{'...' if len(memory.prompt) > 40 else ''}[/]",
                title=f"[bright_cyan]#{memory.id[-4:]}[/]",
                border_style="dim",
                width=25,
                height=12
            )
            panels.append(memory_panel)
        
        # Display in columns
        columns = Columns(panels, equal=True, expand=True)
        self.console.print(columns)
        
        self.console.print("\n[dim]Use /visual-show <id> to display full image[/dim]")
    
    def _show_gallery_list(self, memories: List[VisualMemory]) -> None:
        """Show gallery as a simple list"""
        table = Table(
            title="🎨 Visual Memory Gallery",
            box=box.ROUNDED,
            border_style="bright_cyan",
            show_header=True,
            header_style="bold bright_white on bright_blue"
        )
        
        table.add_column("ID", style="bright_cyan", min_width=8)
        table.add_column("Prompt", style="bright_white", min_width=30)
        table.add_column("Style", style="bright_magenta", min_width=10)
        table.add_column("Size", style="bright_green", min_width=8)
        table.add_column("Created", style="dim", min_width=16)
        
        for memory in memories:
            created = datetime.fromisoformat(memory.creation_time).strftime('%Y-%m-%d %H:%M')
            size_kb = memory.file_size / 1024
            
            table.add_row(
                f"#{memory.id[-6:]}",
                memory.prompt[:50] + ("..." if len(memory.prompt) > 50 else ""),
                memory.style.title(),
                f"{size_kb:.1f}KB",
                created
            )
        
        self.console.print(table)
        self.console.print(f"\n[dim]Showing {len(memories)} of {len(self.visual_memories)} visual memories[/dim]")
    
    def _show_gallery_table(self, memories: List[VisualMemory]) -> None:
        """Show gallery as detailed table"""
        self._show_gallery_list(memories)
    
    def _show_gallery_detailed(self, memories: List[VisualMemory]) -> None:
        """Show detailed view of each memory"""
        for i, memory in enumerate(memories):
            if i > 0:
                self.console.print()
            
            # Create detailed panel for each memory
            created = datetime.fromisoformat(memory.creation_time).strftime('%Y-%m-%d %H:%M:%S')
            size_kb = memory.file_size / 1024
            
            info_text = f"""[bright_white]Prompt:[/] {memory.prompt}
[bright_cyan]Enhanced:[/] {memory.enhanced_prompt}
[bright_magenta]Style:[/] {memory.style.title()}
[bright_green]File:[/] {Path(memory.file_path).name}
[bright_blue]Size:[/] {size_kb:.1f}KB ({memory.dimensions[0]}x{memory.dimensions[1]})
[dim]Created:[/] {created}
[dim]ID:[/] {memory.id}"""
            
            panel = Panel(
                info_text,
                title=f"🎨 Visual Memory #{memory.id[-6:]}",
                border_style="bright_cyan",
                expand=False
            )
            self.console.print(panel)
    
    def show_visual_memory(self, memory_id: str, style: str = "standard", use_color: bool = False) -> bool:
        """Display a specific visual memory with full ASCII art"""
        # Find memory by ID (allow partial ID matching)
        memory = None
        for mem in self.visual_memories:
            if mem.id == memory_id or mem.id.endswith(memory_id) or memory_id in mem.id:
                memory = mem
                break
        
        if not memory:
            self.console.print(f"[red]❌ Visual memory not found: {memory_id}[/]")
            return False
        
        if not Path(memory.file_path).exists():
            self.console.print(f"[red]❌ Image file missing: {memory.file_path}[/]")
            return False
        
        # Display the full ASCII art (reuse the enhanced display method)
        from cocoa_visual import VisualCognition, VisualConfig
        
        visual_config = VisualConfig()
        visual = VisualCognition(visual_config, self.console)
        
        # Display with enhanced ASCII
        visual._display_ascii(memory.file_path, style=style, use_color=use_color)
        
        # Show memory details
        created = datetime.fromisoformat(memory.creation_time).strftime('%Y-%m-%d %H:%M:%S')
        self.console.print(f"\n[bright_cyan]Memory ID:[/] {memory.id}")
        self.console.print(f"[dim]Created: {created}[/dim]")
        
        return True
    
    def open_visual_file(self, memory_id: str) -> bool:
        """Open the actual image file using system default application"""
        # Find memory by ID
        memory = None
        for mem in self.visual_memories:
            if mem.id == memory_id or mem.id.endswith(memory_id) or memory_id in mem.id:
                memory = mem
                break
        
        if not memory:
            self.console.print(f"[red]❌ Visual memory not found: {memory_id}[/]")
            return False
        
        file_path = Path(memory.file_path)
        if not file_path.exists():
            self.console.print(f"[red]❌ Image file missing: {file_path}[/]")
            return False
        
        try:
            import subprocess
            import platform
            
            # Open file with system default application
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(file_path)], check=True)
            elif platform.system() == "Windows":
                subprocess.run(["start", str(file_path)], shell=True, check=True)
            else:  # Linux and others
                subprocess.run(["xdg-open", str(file_path)], check=True)
            
            self.console.print(f"[green]✅ Opened {file_path.name} with system viewer[/]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Could not open file: {e}[/]")
            self.console.print(f"[dim]File location: {file_path}[/dim]")
            return False
    
    def copy_visual_file(self, memory_id: str, destination: str) -> bool:
        """Copy visual file to specified location"""
        # Find memory by ID
        memory = None
        for mem in self.visual_memories:
            if mem.id == memory_id or mem.id.endswith(memory_id) or memory_id in mem.id:
                memory = mem
                break
        
        if not memory:
            self.console.print(f"[red]❌ Visual memory not found: {memory_id}[/]")
            return False
        
        source_path = Path(memory.file_path)
        if not source_path.exists():
            self.console.print(f"[red]❌ Source file missing: {source_path}[/]")
            return False
        
        try:
            dest_path = Path(destination)
            
            # If destination is a directory, use original filename
            if dest_path.is_dir() or destination.endswith('/'):
                dest_path = dest_path / source_path.name
            
            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            self.console.print(f"[green]✅ Copied {source_path.name} to {dest_path}[/]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Copy failed: {e}[/]")
            return False
    
    def get_visual_info(self, memory_id: str) -> Optional[VisualMemory]:
        """Get detailed information about a visual memory"""
        for memory in self.visual_memories:
            if memory.id == memory_id or memory.id.endswith(memory_id) or memory_id in memory.id:
                return memory
        return None
    
    def search_visuals(self, query: str, limit: int = 10) -> List[VisualMemory]:
        """Search visual memories by prompt content"""
        query_lower = query.lower()
        matches = []
        
        for memory in self.visual_memories:
            if (query_lower in memory.prompt.lower() or 
                query_lower in memory.enhanced_prompt.lower() or
                query_lower in memory.style.lower()):
                matches.append(memory)
        
        # Sort by creation time (newest first)
        matches.sort(key=lambda x: x.creation_time, reverse=True)
        return matches[:limit]
    
    def cleanup_missing_files(self) -> int:
        """Remove memories for files that no longer exist"""
        original_count = len(self.visual_memories)
        self.visual_memories = [m for m in self.visual_memories if Path(m.file_path).exists()]
        removed_count = original_count - len(self.visual_memories)
        
        if removed_count > 0:
            self._save_visual_memories()
            self.console.print(f"[yellow]🧹 Cleaned up {removed_count} missing file references[/]")
        
        return removed_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get gallery statistics"""
        if not self.visual_memories:
            return {"total": 0, "total_size": 0, "styles": {}}
        
        total_size = sum(m.file_size for m in self.visual_memories)
        style_counts = {}
        
        for memory in self.visual_memories:
            style = memory.style
            style_counts[style] = style_counts.get(style, 0) + 1
        
        return {
            "total": len(self.visual_memories),
            "total_size": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "styles": style_counts,
            "oldest": min(self.visual_memories, key=lambda x: x.creation_time).creation_time,
            "newest": max(self.visual_memories, key=lambda x: x.creation_time).creation_time
        }

def main():
    """Test the visual gallery system"""
    console = Console()
    gallery = VisualGallery(console)
    
    console.print("[bold cyan]COCO Visual Gallery System Test[/]\n")
    
    # Show current gallery
    gallery.show_gallery(style="list")
    
    # Show statistics
    stats = gallery.get_statistics()
    if stats["total"] > 0:
        console.print(f"\n[bright_cyan]Gallery Statistics:[/]")
        console.print(f"Total images: {stats['total']}")
        console.print(f"Total size: {stats['total_size_mb']:.2f} MB")
        console.print(f"Styles: {', '.join(stats['styles'].keys())}")

if __name__ == "__main__":
    main()
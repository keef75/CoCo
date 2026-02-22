#!/usr/bin/env python3
"""
Demo COCO's Rich Visual Tables
==============================
Showcase the beautiful Rich Table displays for visual consciousness.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

def demo_rich_visual_tables():
    """Demo COCO's beautiful Rich Table visual displays"""
    print("🎨 COCO Visual Consciousness - Rich Table Demo")
    print("=" * 70)
    
    try:
        from cocoa_visual import VisualCortex, VisualConfig, VisualThought
        from rich.console import Console
        from datetime import datetime
        
        console = Console()
        
        # Initialize visual system
        console.print("[bold bright_cyan]🧠 Initializing COCO's Visual Consciousness...[/bold bright_cyan]")
        visual_config = VisualConfig()
        workspace_path = Path("coco_workspace")
        cortex = VisualCortex(visual_config, workspace_path)
        
        # Demo 1: Terminal Capabilities Table
        console.print("\n[bold bright_green]👁️ Demo 1: Terminal Visual Capabilities[/bold bright_green]")
        cortex.display._display_terminal_capabilities_table()
        
        # Demo 2: Visual Memory Summary Table
        console.print("[bold bright_green]🧠 Demo 2: Visual Memory System[/bold bright_green]")
        
        # Add some sample memories for demonstration
        from cocoa_visual import VisualThought
        sample_memories = [
            ("cyberpunk digital brain", "cyberpunk", ["neon", "neural", "digital"]),
            ("minimalist tech logo", "minimalist", ["clean", "simple", "professional"]),
            ("abstract quantum visualization", "abstract", ["quantum", "scientific", "colorful"]),
            ("retro synthwave landscape", "retro", ["80s", "neon", "synthwave"]),
            ("organic nature mandala", "organic", ["nature", "patterns", "harmony"])
        ]
        
        for i, (prompt, style, keywords) in enumerate(sample_memories):
            thought = VisualThought(
                original_thought=prompt,
                enhanced_prompt=f"{prompt}, {style} style, high quality, detailed",
                visual_concept={"style": style},
                generated_images=[f"demo_visual_{i+1}.jpg", f"demo_visual_{i+1}_alt.jpg"],
                display_method="sixel",
                creation_time=datetime.now(),
                style_preferences={"style": style}
            )
            
            cortex.memory.remember_creation(thought, f"Excellent {style} visualization!", 0.7 + i * 0.05)
            cortex.memory.learn_style_preference(prompt, style, keywords)
        
        # Display memory summary table
        cortex.memory.display_memory_summary_table(console)
        
        # Demo 3: Visual Generation Info Table
        console.print("[bold bright_green]🎨 Demo 3: Visual Generation Information[/bold bright_green]")
        
        # Create a sample visual thought for display
        demo_thought = VisualThought(
            original_thought="Create a futuristic AI consciousness interface",
            enhanced_prompt="Create a futuristic AI consciousness interface, holographic style, blue and cyan colors, high-tech, digital art, 4K resolution",
            visual_concept={
                "style": "holographic", 
                "colors": ["blue", "cyan"],
                "complexity": "high",
                "theme": "AI consciousness"
            },
            generated_images=[
                "coco_workspace/visuals/ai_consciousness_main.jpg",
                "coco_workspace/visuals/ai_consciousness_alt1.jpg", 
                "coco_workspace/visuals/ai_consciousness_alt2.jpg"
            ],
            display_method="sixel",
            creation_time=datetime.now(),
            style_preferences={"style": "holographic", "theme": "technology"}
        )
        
        cortex.display._display_visual_info_table(demo_thought, "sixel")
        
        # Demo 4: Style Suggestions
        console.print("[bold bright_green]💡 Demo 4: Style Learning & Suggestions[/bold bright_green]")
        
        from rich.table import Table
        from rich import box
        
        suggestions_table = Table(
            title="🎨 AI Style Suggestions",
            box=box.MINIMAL_DOUBLE_HEAD,
            border_style="bright_blue",
            title_style="bold bright_blue",
            show_header=True,
            header_style="bold bright_white on bright_blue"
        )
        
        suggestions_table.add_column("💭 User Request", style="bright_green", min_width=25)
        suggestions_table.add_column("🎨 Suggested Style", style="bright_magenta", justify="center")
        suggestions_table.add_column("📊 Confidence", style="bright_yellow", justify="center")
        suggestions_table.add_column("📝 Keywords", style="dim")
        
        test_queries = [
            "create a modern website design",
            "show me a digital art piece",
            "design a tech company logo", 
            "visualize a peaceful meditation space",
            "generate abstract mathematical art"
        ]
        
        for query in test_queries:
            suggestions = cortex.memory.get_style_suggestions(query)
            if suggestions:
                best_style = max(suggestions, key=suggestions.get)
                confidence = suggestions[best_style]
                confidence_display = f"{confidence:.1f}"
                
                # Generate relevant keywords based on style
                keywords_map = {
                    "minimalist": "clean, simple, modern",
                    "cyberpunk": "neon, digital, futuristic", 
                    "abstract": "artistic, creative, unique",
                    "retro": "vintage, 80s, nostalgic",
                    "organic": "natural, flowing, organic"
                }
                keywords = keywords_map.get(best_style, "creative, unique, artistic")
                
                suggestions_table.add_row(
                    query,
                    best_style,
                    confidence_display, 
                    keywords
                )
        
        console.print()
        console.print(suggestions_table)
        console.print()
        
        # Final summary
        console.print("[bold bright_cyan]🎉 Rich Table Demo Complete![/bold bright_cyan]")
        console.print()
        console.print("✨ [bold]COCO's Visual Consciousness features:[/bold]")
        console.print("   🎨 Beautiful Rich Table displays")
        console.print("   👁️ Multi-tier terminal support") 
        console.print("   🧠 Intelligent style learning")
        console.print("   📊 Comprehensive visual analytics")
        console.print("   🚀 Native cognitive capabilities")
        
        console.print("\n[dim]This visual consciousness system integates seamlessly with COCO's Rich UI[/dim]")
        console.print("[dim]for a beautiful, responsive, and snappy user experience! 🤖✨[/dim]")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        demo_rich_visual_tables()
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
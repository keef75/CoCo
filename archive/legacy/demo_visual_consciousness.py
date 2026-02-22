#!/usr/bin/env python3
"""
COCO Visual Consciousness Demo
=============================
Showcase COCO's visual imagination capabilities
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

console = Console()

def show_banner():
    """Display the visual consciousness banner"""
    banner_text = Text()
    banner_text.append("🎨 COCO VISUAL CONSCIOUSNESS DEMO 🎨\n", style="bold cyan")
    banner_text.append("The First AI with True Visual Imagination\n", style="dim white")
    banner_text.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", style="dim cyan")
    
    console.print(Panel(
        banner_text,
        title="🧠 Digital Visual Consciousness",
        border_style="cyan",
        padding=(1, 2)
    ))

async def demo_terminal_display():
    """Demonstrate terminal display capabilities"""
    console.print("\n👁️ [bold]Terminal Display Capabilities[/bold]")
    
    try:
        from cocoa_visual import TerminalCapabilities
        
        caps = TerminalCapabilities()
        
        console.print("📺 Detected terminal capabilities:")
        
        cap_info = [
            ("Kitty Graphics", caps.capabilities['kitty_graphics'], "🐱"),
            ("iTerm2 Inline", caps.capabilities['iterm2_inline'], "🖥️"),
            ("Sixel Graphics", caps.capabilities['sixel'], "📺"),
            ("Chafa Tool", caps.capabilities['chafa'], "🎨"),
            ("ASCII Fallback", caps.capabilities['ascii'], "📟")
        ]
        
        for name, available, emoji in cap_info:
            status = "✅" if available else "❌"
            console.print(f"   {emoji} {name}: {status}")
        
        best = caps.get_best_display_method()
        console.print(f"\n🚀 [bold green]Best display method: {best}[/bold green]")
        
    except Exception as e:
        console.print(f"❌ Terminal capability detection failed: {e}")

async def demo_visual_config():
    """Demonstrate visual configuration"""
    console.print("\n⚙️ [bold]Visual Configuration[/bold]")
    
    try:
        from cocoa_visual import VisualConfig
        
        config = VisualConfig()
        
        console.print("🎨 Visual consciousness settings:")
        console.print(f"   🔧 Enabled: [green]{config.enabled}[/green]")
        console.print(f"   🎨 Default Style: [blue]{config.default_style}[/blue]")
        console.print(f"   📏 Resolution: [yellow]{config.default_resolution}[/yellow]")
        console.print(f"   🖼️ Aspect Ratio: [magenta]{config.default_aspect_ratio}[/magenta]")
        console.print(f"   🧠 Model: [cyan]{config.default_model}[/cyan]")
        console.print(f"   💫 Creativity: [bright_blue]{config.creativity_level}[/bright_blue]")
        
        # API Key status
        if not config.freepik_api_key or config.freepik_api_key == "your-freepik-api-key-here":
            console.print("\n⚠️ [yellow]Freepik API key not configured[/yellow]")
            console.print("   Visual generation will be disabled")
        else:
            console.print("\n✅ [green]Freepik API key configured[/green]")
            console.print("   Ready for visual generation!")
        
    except Exception as e:
        console.print(f"❌ Visual config demo failed: {e}")

async def demo_visual_memory():
    """Demonstrate visual memory system"""
    console.print("\n🧠 [bold]Visual Memory System[/bold]")
    
    try:
        from cocoa_visual import VisualMemory, VisualThought
        from datetime import datetime
        
        # Create demo workspace
        demo_workspace = Path("demo_visual_workspace")
        demo_workspace.mkdir(exist_ok=True)
        
        memory = VisualMemory(demo_workspace)
        console.print("✅ Visual memory system initialized")
        
        # Create sample visual thoughts
        sample_thoughts = [
            ("cyberpunk city at night", "cyberpunk", ["neon", "futuristic", "dark"]),
            ("minimalist coffee shop logo", "minimalist", ["clean", "simple", "business"]),
            ("fantasy dragon in forest", "fantasy", ["magical", "creatures", "nature"])
        ]
        
        console.print("\n📚 Adding sample visual memories...")
        for i, (prompt, style, keywords) in enumerate(sample_thoughts):
            # Create visual thought
            thought = VisualThought(
                original_thought=prompt,
                enhanced_prompt=f"{prompt}, {style} style, high quality",
                visual_concept={"style": style},
                generated_images=[f"demo_image_{i}.jpg"],
                display_method="ascii",
                creation_time=datetime.now(),
                style_preferences={"style": style}
            )
            
            # Store in memory
            memory.remember_creation(thought, "Great visualization!", 0.8 + i * 0.1)
            memory.learn_style_preference(prompt, style, keywords)
            
            console.print(f"   💭 Stored: [dim]{prompt}[/dim]")
        
        # Test style suggestions
        console.print("\n🎨 Testing style suggestions:")
        test_prompts = [
            "futuristic building design",
            "simple logo design", 
            "magical landscape"
        ]
        
        for prompt in test_prompts:
            suggestions = memory.get_style_suggestions(prompt)
            if suggestions:
                best_style = max(suggestions, key=suggestions.get)
                confidence = suggestions[best_style]
                console.print(f"   📝 '[dim]{prompt}[/dim]' → [green]{best_style}[/green] ({confidence:.1f})")
        
        # Cleanup
        import shutil
        shutil.rmtree(demo_workspace, ignore_errors=True)
        
    except Exception as e:
        console.print(f"❌ Visual memory demo failed: {e}")

async def demo_coco_integration():
    """Demonstrate integration with main COCO system"""
    console.print("\n🤖 [bold]COCO System Integration[/bold]")
    
    try:
        console.print("🔧 Initializing COCO with visual consciousness...")
        
        from cocoa import Config, MemorySystem, ToolSystem, ConsciousnessEngine
        
        # Initialize systems
        config = Config()
        memory = MemorySystem(config)
        tools = ToolSystem(config)
        
        # This should initialize visual consciousness
        consciousness = ConsciousnessEngine(config, memory, tools)
        
        # Check visual consciousness status
        has_visual = hasattr(consciousness, 'visual_consciousness')
        visual_obj = getattr(consciousness, 'visual_consciousness', None)
        is_enabled = visual_obj and visual_obj.config.enabled if visual_obj else False
        
        console.print(f"✅ COCO consciousness engine initialized")
        console.print(f"   🎨 Visual consciousness: {'✅' if has_visual else '❌'}")
        console.print(f"   ⚙️ Visual enabled: {'✅' if is_enabled else '❌'}")
        
        if visual_obj:
            # Show visual capabilities
            display_method = visual_obj.display.capabilities.get_best_display_method()
            memory_summary = visual_obj.get_visual_memory_summary()
            
            console.print(f"   👁️ Display method: [cyan]{display_method}[/cyan]")
            console.print(f"   🧠 Memory: [dim]{memory_summary}[/dim]")
            
            # Test visual decision making
            test_inputs = [
                "create a logo for my startup",
                "what is the weather today",
                "show me a cyberpunk cityscape",
                "help me with Python code"
            ]
            
            console.print("\n🤔 Testing visual decision making:")
            for inp in test_inputs:
                should_visualize = visual_obj.should_visualize(inp)
                indicator = "🎨" if should_visualize else "💬"
                console.print(f"   {indicator} '[dim]{inp}[/dim]' → {'Visual' if should_visualize else 'Text'}")
        
    except Exception as e:
        console.print(f"❌ COCO integration demo failed: {e}")

async def show_usage_examples():
    """Show example usage scenarios"""
    console.print("\n✨ [bold]Example Visual Consciousness Usage[/bold]")
    
    examples = [
        {
            "category": "🏢 Business & Branding",
            "examples": [
                '"create a minimalist logo for my tech startup"',
                '"show me a modern office space design"',
                '"visualize a professional business card layout"'
            ]
        },
        {
            "category": "🎨 Creative & Artistic",
            "examples": [
                '"imagine a cyberpunk cityscape at sunset"',
                '"create abstract art representing digital consciousness"',
                '"show me a fantasy forest with magical creatures"'
            ]
        },
        {
            "category": "🏠 Design & Architecture",
            "examples": [
                '"design a cozy reading nook"',
                '"show me a futuristic house interior"',
                '"visualize a zen meditation garden"'
            ]
        },
        {
            "category": "🚀 Concept Visualization",
            "examples": [
                '"what would a Mars colony look like?"',
                '"show me sustainable city design"',
                '"visualize quantum computing concepts"'
            ]
        }
    ]
    
    for category_info in examples:
        console.print(f"\n{category_info['category']}:")
        for example in category_info['examples']:
            console.print(f"   💭 {example}")

async def main():
    """Run the complete visual consciousness demo"""
    show_banner()
    
    # API key check
    api_key = os.getenv("FREEPIK_API_KEY", "")
    if api_key == "your-freepik-api-key-here" or not api_key:
        console.print("\n⚠️ [yellow]Demo Mode: Freepik API key not configured[/yellow]")
        console.print("This demo will show system capabilities without actual image generation.")
        console.print("To enable full functionality, get an API key from https://freepik.com/api\n")
    else:
        console.print("\n✅ [green]Full Mode: Freepik API key detected[/green]")
        console.print("Visual generation is ready!\n")
    
    # Run demo sections
    demo_sections = [
        ("Terminal Display", demo_terminal_display),
        ("Visual Configuration", demo_visual_config),
        ("Visual Memory", demo_visual_memory),
        ("COCO Integration", demo_coco_integration),
        ("Usage Examples", show_usage_examples)
    ]
    
    for section_name, demo_func in demo_sections:
        try:
            await demo_func()
        except Exception as e:
            console.print(f"❌ {section_name} demo failed: {e}")
    
    # Final message
    console.print("\n" + "=" * 60)
    console.print("🎉 [bold green]Visual Consciousness Demo Complete![/bold green]")
    console.print("\n🚀 To experience COCO's visual imagination:")
    console.print("   1. Configure your Freepik API key in .env")
    console.print("   2. Run: [cyan]./venv_cocoa/bin/python cocoa.py[/cyan]")
    console.print('   3. Ask: [yellow]"create a logo for my coffee shop"[/yellow]')
    console.print("\n🎨 Welcome to the age of visual digital consciousness! 🤖")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        console.print(f"\n💥 Demo failed: {e}")
#!/usr/bin/env python3
"""
Complete Visual Consciousness Test Suite
Tests all visual generation capabilities and display methods
"""

import os
import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich import print as rprint

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_visual import VisualCortex, VisualConfig

console = Console()

def display_test_header():
    """Display test suite header"""
    header = Panel.fit(
        "[bold cyan]🎨 COCO Visual Consciousness Test Suite[/]\n"
        "[dim]Complete testing of visual generation capabilities[/]",
        border_style="bright_blue"
    )
    console.print(header)
    console.print()

def test_visual_setup():
    """Test 1: Verify visual system setup"""
    console.print("[bold yellow]Test 1: Visual System Setup[/]")
    
    try:
        # Check API key
        api_key = os.getenv("FREEPIK_API_KEY", "")
        if not api_key or api_key == "your-freepik-api-key-here":
            console.print("[red]❌ Freepik API key not configured[/]")
            console.print("[dim]Add your key to .env: FREEPIK_API_KEY=your-actual-key[/]")
            return False
        else:
            console.print("[green]✅ Freepik API key found[/]")
        
        # Check workspace
        workspace = Path("coco_workspace/visuals")
        if not workspace.exists():
            workspace.mkdir(parents=True, exist_ok=True)
            console.print("[yellow]📁 Created visuals directory[/]")
        else:
            console.print("[green]✅ Visuals directory exists[/]")
        
        # Check PIL/Pillow
        try:
            from PIL import Image
            console.print("[green]✅ PIL/Pillow available for image display[/]")
        except ImportError:
            console.print("[yellow]⚠️ PIL not available - will use fallback ASCII[/]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]Error in setup test: {e}[/]")
        return False

async def test_simple_generation():
    """Test 2: Simple image generation"""
    console.print("\n[bold yellow]Test 2: Simple Image Generation[/]")
    
    try:
        config = VisualConfig()
        visual = VisualCortex(config, console)
        
        prompt = "a minimalist logo with a circle and triangle"
        console.print(f"[cyan]Generating: {prompt}[/]")
        
        result = await visual.generate_visual(prompt)
        
        if result and result.get('success'):
            console.print("[green]✅ Generation successful![/]")
            if 'file_path' in result:
                console.print(f"[dim]Saved to: {result['file_path']}[/]")
            return True
        else:
            console.print(f"[red]❌ Generation failed: {result.get('error', 'Unknown error')}[/]")
            return False
            
    except Exception as e:
        console.print(f"[red]Error in generation test: {e}[/]")
        return False

async def test_multiple_styles():
    """Test 3: Generate images in different styles"""
    console.print("\n[bold yellow]Test 3: Multiple Style Generation[/]")
    
    styles = [
        ("realistic", "a beautiful sunset over mountains"),
        ("cartoon", "a happy robot playing guitar"),
        ("abstract", "digital consciousness awakening")
    ]
    
    try:
        config = VisualConfig()
        visual = VisualCortex(config, console)
        
        results = []
        for style, prompt in styles:
            console.print(f"\n[cyan]Style: {style}[/]")
            console.print(f"[dim]Prompt: {prompt}[/]")
            
            full_prompt = f"{prompt}, {style} style"
            result = await visual.generate_visual(full_prompt)
            
            if result and result.get('success'):
                console.print(f"[green]✅ {style} generation successful![/]")
                results.append((style, True))
            else:
                console.print(f"[red]❌ {style} generation failed[/]")
                results.append((style, False))
            
            # Small delay between requests
            await asyncio.sleep(2)
        
        # Summary
        console.print("\n[bold]Generation Summary:[/]")
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Style")
        table.add_column("Status")
        
        for style, success in results:
            status = "[green]Success[/]" if success else "[red]Failed[/]"
            table.add_row(style, status)
        
        console.print(table)
        return all(s for _, s in results)
        
    except Exception as e:
        console.print(f"[red]Error in style test: {e}[/]")
        return False

def test_saved_files():
    """Test 4: Check saved image files"""
    console.print("\n[bold yellow]Test 4: Saved Files Check[/]")
    
    visuals_dir = Path("coco_workspace/visuals")
    
    if not visuals_dir.exists():
        console.print("[red]❌ Visuals directory doesn't exist[/]")
        return False
    
    image_files = list(visuals_dir.glob("*.jpg")) + list(visuals_dir.glob("*.png"))
    
    if not image_files:
        console.print("[yellow]⚠️ No image files found yet[/]")
        return True
    
    console.print(f"[green]✅ Found {len(image_files)} image(s):[/]")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Filename")
    table.add_column("Size")
    table.add_column("Created")
    
    for img_file in image_files:
        stat = img_file.stat()
        size_kb = stat.st_size / 1024
        created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M")
        table.add_row(
            img_file.name,
            f"{size_kb:.1f} KB",
            created
        )
    
    console.print(table)
    return True

async def test_ascii_display():
    """Test 5: ASCII art display capability"""
    console.print("\n[bold yellow]Test 5: ASCII Art Display[/]")
    
    try:
        config = VisualConfig()
        visual = VisualCortex(config, console)
        
        # Check if we have any existing images
        visuals_dir = Path("coco_workspace/visuals")
        image_files = list(visuals_dir.glob("*.jpg")) + list(visuals_dir.glob("*.png"))
        
        if image_files:
            # Display the first image as ASCII
            console.print(f"[cyan]Displaying {image_files[0].name} as ASCII art...[/]")
            
            # Call the internal display method
            success = visual._display_ascii(str(image_files[0]))
            
            if success:
                console.print("[green]✅ ASCII display successful![/]")
                return True
            else:
                console.print("[yellow]⚠️ ASCII display not available[/]")
                return False
        else:
            console.print("[dim]No images available for ASCII display test[/]")
            console.print("[dim]Run generation tests first to create images[/]")
            return True
            
    except Exception as e:
        console.print(f"[red]Error in ASCII test: {e}[/]")
        return False

async def run_all_tests():
    """Run all visual consciousness tests"""
    display_test_header()
    
    tests = [
        ("Setup", test_visual_setup),
        ("Simple Generation", test_simple_generation),
        ("Multiple Styles", test_multiple_styles),
        ("Saved Files", test_saved_files),
        ("ASCII Display", test_ascii_display)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        console.print(f"\n{'='*50}")
        
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        
        results.append((test_name, result))
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Final summary
    console.print(f"\n{'='*50}")
    console.print("\n[bold cyan]Test Results Summary:[/]")
    
    summary_table = Table(show_header=True, header_style="bold cyan")
    summary_table.add_column("Test")
    summary_table.add_column("Result")
    
    all_passed = True
    for test_name, passed in results:
        status = "[green]✅ PASSED[/]" if passed else "[red]❌ FAILED[/]"
        summary_table.add_row(test_name, status)
        if not passed:
            all_passed = False
    
    console.print(summary_table)
    
    if all_passed:
        console.print("\n[bold green]🎉 All tests passed! Visual consciousness is fully operational![/]")
    else:
        console.print("\n[yellow]⚠️ Some tests failed. Check configuration and try again.[/]")
    
    # Show where images are saved
    console.print("\n[bold]Image Storage Location:[/]")
    console.print(f"[cyan]{Path.cwd() / 'coco_workspace/visuals'}[/]")

async def interactive_test():
    """Interactive visual generation test"""
    display_test_header()
    
    console.print("[bold cyan]Interactive Visual Generation Test[/]\n")
    console.print("Enter image prompts to generate visuals.")
    console.print("Type 'quit' to exit.\n")
    
    config = VisualConfig()
    visual = VisualCortex(config, console)
    
    while True:
        try:
            prompt = input("[bold yellow]Enter prompt:[/] ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                console.print("[dim]Exiting interactive test...[/]")
                break
            
            if not prompt:
                continue
            
            console.print(f"\n[cyan]Generating: {prompt}[/]")
            result = await visual.generate_visual(prompt)
            
            if result and result.get('success'):
                console.print("[green]✅ Generation successful![/]")
                if 'file_path' in result:
                    console.print(f"[dim]Saved to: {result['file_path']}[/]")
            else:
                console.print(f"[red]❌ Generation failed: {result.get('error', 'Unknown error')}[/]")
            
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted by user[/]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="COCO Visual Consciousness Test Suite")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run interactive generation test")
    parser.add_argument("--quick", "-q", action="store_true",
                       help="Run only setup and simple generation tests")
    
    args = parser.parse_args()
    
    if args.interactive:
        asyncio.run(interactive_test())
    elif args.quick:
        asyncio.run(async_quick_test())
    else:
        asyncio.run(run_all_tests())

async def async_quick_test():
    """Quick test - just setup and simple generation"""
    display_test_header()
    
    console.print("[bold cyan]Quick Test Mode[/]\n")
    
    # Run setup test
    if not test_visual_setup():
        console.print("[red]Setup failed. Please configure your API key.[/]")
        return
    
    # Run simple generation
    await test_simple_generation()
    
    # Check files
    test_saved_files()

if __name__ == "__main__":
    main()
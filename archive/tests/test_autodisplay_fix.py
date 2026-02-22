#!/usr/bin/env python3
"""
Test the auto-display functionality fix
"""

import os
import sys
import asyncio
from pathlib import Path
from rich.console import Console

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_visual import VisualCortex, VisualConfig

console = Console()

async def test_auto_display():
    """Test auto-display functionality"""
    console.print("[bold cyan]🎨 Testing Auto-Display Functionality[/]")

    try:
        # Initialize visual consciousness
        config = VisualConfig()
        workspace_path = Path.cwd() / "coco_workspace"
        workspace_path.mkdir(exist_ok=True)
        visual_cortex = VisualCortex(config, workspace_path)

        console.print("[yellow]📝 Generating test image with auto-display...[/]")

        # Generate a simple image to test auto-display
        result = await visual_cortex.imagine("A simple red flower in a garden")

        if result and result.display_method != "none":
            console.print(f"[green]✅ Auto-display SUCCESS using: {result.display_method}[/]")
            console.print(f"[dim]Generated image paths: {result.generated_images}[/]")
            return True
        elif result and result.display_method == "manual_fallback":
            console.print("[yellow]⚠️ Auto-display FAILED - Manual fallback required[/]")
            console.print("[dim]Use /image command to view[/]")
            return False
        else:
            console.print("[red]❌ Image generation failed completely[/]")
            return False

    except Exception as e:
        console.print(f"[red]Error in auto-display test: {e}[/]")
        return False

if __name__ == "__main__":
    # Set up environment
    if not os.getenv("FREEPIK_API_KEY"):
        console.print("[red]❌ FREEPIK_API_KEY not configured[/]")
        sys.exit(1)

    # Run the test
    result = asyncio.run(test_auto_display())

    if result:
        console.print("\n[bold green]🎉 Auto-display test PASSED![/]")
    else:
        console.print("\n[bold yellow]⚠️ Auto-display test had issues - check output above[/]")
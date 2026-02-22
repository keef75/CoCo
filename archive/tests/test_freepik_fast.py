#!/usr/bin/env python3
"""
Test Freepik Fast API Integration
Quick test to verify the new fast image generation is working
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from cocoa_visual import VisualConfig, FreepikMysticAPI
from rich.console import Console

async def test_fast_generation():
    console = Console()
    console.print("🧪 [bold]Testing Freepik Fast API[/bold]")
    
    # Create config
    config = VisualConfig()
    
    if not config.freepik_api_key:
        console.print("❌ [red]FREEPIK_API_KEY not found in environment[/red]")
        console.print("   Please add your API key to .env file")
        return
    
    console.print(f"✅ [green]API key configured[/green]")
    
    # Create API instance
    api = FreepikMysticAPI(config)
    
    # Test fast generation
    try:
        console.print("🎨 [cyan]Generating test image...[/cyan]")
        
        result = await api.generate_image_fast(
            prompt="a cute robot reading a book",
            style="realism",
            guidance_scale=1.5,
            num_images=1,
            size="square_1_1"
        )
        
        if result.get("status") == "completed":
            images = result.get("images", [])
            console.print(f"✅ [green]Generation successful! Created {len(images)} images[/green]")
            
            # Save images
            workspace = Path("coco_workspace")
            saved_paths = api.save_base64_images(images, "test_robot_reading", workspace)
            
            if saved_paths:
                console.print(f"📁 [blue]Images saved:[/blue]")
                for path in saved_paths:
                    console.print(f"   {path}")
                    
                console.print("💡 [yellow]You can now view the images in your file manager[/yellow]")
            else:
                console.print("⚠️ [yellow]Images generated but not saved to disk[/yellow]")
        else:
            console.print(f"❌ [red]Generation failed: {result}[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error during generation: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(test_fast_generation())
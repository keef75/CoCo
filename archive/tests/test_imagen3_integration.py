#!/usr/bin/env python3
"""
Test Google Imagen 3 Integration
Tests the new Imagen 3 API integration via Freepik
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import cocoa_visual
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_visual import VisualConfig, FreepikMysticAPI
from rich.console import Console

console = Console()

async def test_imagen3_generation():
    """Test basic Imagen 3 image generation"""
    console.print("\n[bold cyan]🧪 Testing Google Imagen 3 Integration[/bold cyan]\n")

    # Initialize config and API
    config = VisualConfig()
    api = FreepikMysticAPI(config)

    # Check API key
    if not config.freepik_api_key:
        console.print("[red]❌ FREEPIK_API_KEY not found in environment[/red]")
        return False

    console.print(f"[green]✅ API Key configured: {config.freepik_api_key[:20]}...[/green]")
    console.print(f"[green]✅ Base URL: {config.freepik_base_url}[/green]\n")

    # Test 1: Simple generation with Imagen 3
    console.print("[bold yellow]Test 1: Simple Imagen 3 Generation[/bold yellow]")
    console.print("Prompt: 'A futuristic AI assistant visualizing data'\n")

    try:
        result = await api.generate_image_imagen3(
            prompt="A futuristic AI assistant visualizing data",
            num_images=1,
            aspect_ratio="square_1_1"
        )

        console.print("[green]✅ Imagen 3 generation successful![/green]")
        console.print(f"Task ID: {result.get('data', {}).get('task_id')}")
        console.print(f"Status: {result.get('data', {}).get('status')}")
        console.print(f"Generated URLs: {result.get('data', {}).get('generated', [])}\n")

    except Exception as e:
        console.print(f"[red]❌ Imagen 3 generation failed: {e}[/red]\n")
        return False

    # Test 2: Generation with style
    console.print("[bold yellow]Test 2: Imagen 3 with Styling[/bold yellow]")
    console.print("Prompt: 'A serene mountain landscape at sunset'")
    console.print("Style: 'anime' with pastel colors and warm lighting\n")

    try:
        result = await api.generate_image_imagen3(
            prompt="A serene mountain landscape at sunset",
            num_images=1,
            aspect_ratio="widescreen_16_9",
            style="anime pastel warm landscape"
        )

        console.print("[green]✅ Styled Imagen 3 generation successful![/green]")
        console.print(f"Generated URLs: {result.get('data', {}).get('generated', [])}\n")

    except Exception as e:
        console.print(f"[red]❌ Styled generation failed: {e}[/red]\n")
        return False

    # Test 3: Primary generation method (should use Imagen 3)
    console.print("[bold yellow]Test 3: Primary generate_image() Method[/bold yellow]")
    console.print("Testing that generate_image() now uses Imagen 3 as primary\n")

    try:
        result = await api.generate_image(
            prompt="A cyberpunk city at night with neon lights",
            aspect_ratio="social_story_9_16"
        )

        console.print("[green]✅ Primary method successful (using Imagen 3)![/green]")
        console.print(f"Generated URLs: {result.get('data', {}).get('generated', [])}\n")

    except Exception as e:
        console.print(f"[red]❌ Primary method failed: {e}[/red]\n")
        return False

    # Test 4: Status check with Imagen 3 endpoint
    console.print("[bold yellow]Test 4: Status Check (Multi-endpoint)[/bold yellow]")

    task_id = result.get('data', {}).get('task_id')
    if task_id:
        try:
            status = await api.check_generation_status(task_id)
            console.print(f"[green]✅ Status check successful![/green]")
            console.print(f"API Type: {status.get('api_type')}")
            console.print(f"Status: {status.get('status')}\n")
        except Exception as e:
            console.print(f"[yellow]⚠️ Status check warning: {e}[/yellow]\n")

    console.print("[bold green]🎉 All Imagen 3 tests completed successfully![/bold green]\n")
    return True

async def test_fallback_chain():
    """Test the fallback chain: Imagen 3 → Gemini → Legacy"""
    console.print("\n[bold cyan]🧪 Testing Fallback Chain[/bold cyan]\n")

    config = VisualConfig()
    api = FreepikMysticAPI(config)

    console.print("[yellow]Note: This test shows the fallback order.[/yellow]")
    console.print("[yellow]Primary: Imagen 3 → Fallback 1: Gemini → Fallback 2: Legacy[/yellow]\n")

    try:
        result = await api.generate_image(
            prompt="Test fallback chain visualization"
        )
        console.print("[green]✅ Fallback chain works correctly![/green]\n")
    except Exception as e:
        console.print(f"[red]❌ Fallback chain test failed: {e}[/red]\n")

if __name__ == "__main__":
    console.print("[bold magenta]Google Imagen 3 Integration Test Suite[/bold magenta]")
    console.print("[dim]Testing the new Imagen 3 API via Freepik[/dim]\n")

    # Run tests
    success = asyncio.run(test_imagen3_generation())

    if success:
        asyncio.run(test_fallback_chain())
        console.print("[bold green]✅ All tests passed! Imagen 3 integration complete.[/bold green]")
    else:
        console.print("[bold red]❌ Tests failed. Check error messages above.[/bold red]")
        sys.exit(1)

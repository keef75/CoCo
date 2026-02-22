#!/usr/bin/env python3
"""
Quick test for the mpv playback fix
"""

import asyncio
from cocoa_video_observer import VideoObserver, VideoObserverConfig
from rich.console import Console

async def test_youtube_watch():
    """Test YouTube watching with fixed mpv playback"""
    console = Console()

    console.print("\n[bold cyan]Testing Fixed mpv Playback[/bold cyan]\n")

    # Initialize observer
    config = VideoObserverConfig()
    observer = VideoObserver(config)

    # Show backend
    console.print(f"[green]Backend: {observer.backend['type']}[/green]")
    console.print(f"[dim]Description: {observer.backend['description']}[/dim]\n")

    # Test short YouTube video
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"

    console.print(f"[yellow]Testing: {test_url}[/yellow]")
    console.print("[dim]This is the first YouTube video ever uploaded (19 seconds)[/dim]\n")

    # Watch it
    result = await observer.watch(test_url, mode="auto")

    if result.get("success"):
        console.print("\n[bold green]✅ SUCCESS! Video playback worked![/bold green]\n")
    else:
        console.print(f"\n[bold red]❌ FAILED: {result.get('error')}[/bold red]\n")

    return result

if __name__ == "__main__":
    result = asyncio.run(test_youtube_watch())

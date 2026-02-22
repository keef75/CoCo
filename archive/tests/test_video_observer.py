#!/usr/bin/env python3
"""
Test Suite for COCO Video Observer
===================================
Tests video watching capabilities with different backends.
"""

import asyncio
from cocoa_video_observer import VideoObserver, VideoObserverConfig, BackendDetector
from rich.console import Console


def test_backend_detection():
    """Test backend detection and capability checking"""
    console = Console()

    console.print("\n[bold cyan]🔍 Testing Backend Detection[/bold cyan]\n")

    # Detect backend
    backend = BackendDetector.detect_best_backend()

    console.print(f"[green]✅ Backend detected: {backend['type']}[/green]")
    console.print(f"[dim]Description: {backend['description']}[/dim]")
    console.print(f"[dim]Terminal: {backend['terminal_type']}[/dim]")

    # Show available tools
    console.print("\n[bold]Available Tools:[/bold]")
    for tool, available in backend["available_tools"].items():
        status = "✅" if available else "❌"
        console.print(f"  {status} {tool}")

    # Show capabilities
    console.print("\n[bold]Capabilities:[/bold]")
    caps = backend["capabilities"]
    console.print(f"  Inline playback: {'✅' if caps['inline'] else '❌'}")
    console.print(f"  YouTube support: {'✅' if caps['youtube'] else '❌'}")
    console.print(f"  Playback controls: {'✅' if caps['controls'] else '❌'}")
    console.print(f"  Quality level: {caps['quality']}")

    return backend


def test_observer_initialization():
    """Test video observer initialization"""
    console = Console()

    console.print("\n[bold cyan]🎬 Testing Observer Initialization[/bold cyan]\n")

    try:
        config = VideoObserverConfig()
        observer = VideoObserver(config)

        console.print("[green]✅ Video observer initialized successfully[/green]")

        # Display full capabilities
        observer.display_capabilities()

        return observer

    except Exception as e:
        console.print(f"[red]❌ Failed to initialize observer: {e}[/red]")
        return None


async def test_youtube_watching(observer: VideoObserver):
    """Test YouTube video watching (audio-only for safety)"""
    console = Console()

    console.print("\n[bold cyan]📺 Testing YouTube Watching (Audio-Only)[/bold cyan]\n")

    # Use a short video for testing (replace with actual test video)
    # For now, we'll just test the metadata resolution without actually playing
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video

    if not observer.backend["capabilities"]["youtube"]:
        console.print("[yellow]⚠️  YouTube support not available (yt-dlp not installed)[/yellow]")
        return

    # Test URL resolution
    console.print(f"[dim]Testing URL: {test_url}[/dim]")

    try:
        resolved = observer.youtube_resolver.resolve(test_url, audio_only=True)

        if resolved.get("success"):
            console.print("[green]✅ YouTube URL resolved successfully[/green]")
            console.print(f"[dim]Title: {resolved.get('title', 'Unknown')}[/dim]")
            console.print(f"[dim]Duration: {resolved.get('duration', 0)}s[/dim]")
            console.print(f"[dim]Uploader: {resolved.get('uploader', 'Unknown')}[/dim]")
        else:
            console.print(f"[red]❌ Failed to resolve: {resolved.get('error')}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Error during YouTube test: {e}[/red]")


async def test_capabilities_display(observer: VideoObserver):
    """Test capabilities display"""
    console = Console()

    console.print("\n[bold cyan]🎯 Testing Capabilities Display[/bold cyan]\n")

    observer.display_capabilities()


def run_all_tests():
    """Run all video observer tests"""
    console = Console()

    console.print("\n" + "="*70)
    console.print("[bold magenta]🎬 COCO Video Observer Test Suite[/bold magenta]")
    console.print("="*70 + "\n")

    # Test 1: Backend detection
    backend = test_backend_detection()

    # Test 2: Observer initialization
    observer = test_observer_initialization()

    if observer:
        # Test 3: YouTube watching (async)
        asyncio.run(test_youtube_watching(observer))

        # Test 4: Capabilities display
        asyncio.run(test_capabilities_display(observer))

    # Summary
    console.print("\n" + "="*70)
    console.print("[bold green]✅ Test Suite Complete[/bold green]")
    console.print("="*70 + "\n")

    # Installation recommendations
    if not backend["available_tools"]["mpv"]:
        console.print("[yellow]💡 Recommendation: Install mpv for inline playback[/yellow]")
        console.print("[dim]   brew install mpv[/dim]\n")

    if not backend["available_tools"]["yt-dlp"]:
        console.print("[yellow]💡 Recommendation: Install yt-dlp for YouTube support[/yellow]")
        console.print("[dim]   brew install yt-dlp[/dim]\n")


if __name__ == "__main__":
    run_all_tests()

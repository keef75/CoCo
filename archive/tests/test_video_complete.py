#!/usr/bin/env python3
"""
Complete Video Consciousness System Test
========================================
Tests all components of COCO's video consciousness system including:
- API integration with Fal AI Veo3 Fast
- Video player detection
- File management and storage
- Rich UI integration
- Gallery and memory systems
"""

import os
import sys
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test importing all video consciousness components"""
    console = Console()
    console.print(Panel("🔍 Testing Video Consciousness Imports", border_style="blue"))
    
    try:
        from cocoa_video import (
            VideoConfig, VideoThought, VideoCapabilities, 
            TerminalVideoDisplay, FalAIVideoAPI, VideoGallery,
            VideoCognition
        )
        console.print("✅ All video consciousness classes imported successfully")
        return True
        
    except ImportError as e:
        console.print(f"❌ Import failed: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    console = Console()
    console.print(Panel("📦 Testing Dependencies", border_style="blue"))
    
    dependencies = {
        'fal_client': 'Fal AI client for video generation',
        'PIL': 'Pillow for image processing',
        'rich': 'Rich console for beautiful displays'
    }
    
    results = {}
    
    for dep, desc in dependencies.items():
        try:
            __import__(dep)
            console.print(f"✅ {dep}: {desc}")
            results[dep] = True
        except ImportError:
            console.print(f"❌ {dep}: {desc} - NOT AVAILABLE")
            results[dep] = False
    
    return results

def test_video_config():
    """Test VideoConfig initialization and settings"""
    console = Console()
    console.print(Panel("⚙️ Testing Video Configuration", border_style="blue"))
    
    try:
        from cocoa_video import VideoConfig
        
        # Test basic configuration
        config = VideoConfig()
        
        # Show configuration details
        table = Table(title="🎬 Video Configuration", box=box.ROUNDED)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="bright_white")
        
        table.add_row("Enabled", str(config.enabled))
        table.add_row("Default Model", config.default_model)
        table.add_row("Default Aspect Ratio", config.default_aspect_ratio)
        table.add_row("Default Duration", config.default_duration)
        table.add_row("Default Resolution", config.default_resolution)
        table.add_row("Video Player", config.video_player)
        table.add_row("Display Mode", config.display_mode)
        table.add_row("Workspace", config.video_workspace)
        
        console.print(table)
        
        if config.enabled:
            console.print("✅ Video consciousness configuration successful")
        else:
            console.print("⚠️ Video consciousness disabled (missing API key)")
        
        return config
        
    except Exception as e:
        console.print(f"❌ Configuration test failed: {e}")
        return None

def test_video_capabilities():
    """Test video player detection and capabilities"""
    console = Console()
    console.print(Panel("🎥 Testing Video Capabilities", border_style="blue"))
    
    try:
        from cocoa_video import VideoCapabilities
        
        capabilities = VideoCapabilities()
        
        # Show capabilities table
        table = Table(title="🎮 Video Player Capabilities", box=box.ROUNDED)
        table.add_column("Player", style="cyan")
        table.add_column("Available", justify="center")
        table.add_column("Description", style="dim")
        
        players = [
            ("mpv", capabilities.capabilities['mpv'], "Versatile media player"),
            ("VLC", capabilities.capabilities['vlc'], "VLC media player"),
            ("cvlc", capabilities.capabilities['cvlc'], "VLC command line"),
            ("ffplay", capabilities.capabilities['ffplay'], "FFmpeg player"),
            ("mplayer", capabilities.capabilities['mplayer'], "MPlayer"),
            ("ASCII Art", capabilities.capabilities['ascii_art'], "Text-based fallback")
        ]
        
        for player, available, desc in players:
            status = "[bright_green]✅ YES[/bright_green]" if available else "[bright_red]❌ NO[/bright_red]"
            table.add_row(player, status, desc)
        
        console.print(table)
        
        best_player = capabilities.get_best_player()
        console.print(f"\n🎯 Best available player: [bright_green]{best_player}[/bright_green]")
        
        return capabilities
        
    except Exception as e:
        console.print(f"❌ Capabilities test failed: {e}")
        return None

def test_video_display():
    """Test terminal video display system"""
    console = Console()
    console.print(Panel("📺 Testing Video Display System", border_style="blue"))
    
    try:
        from cocoa_video import VideoConfig, TerminalVideoDisplay
        
        config = VideoConfig()
        display = TerminalVideoDisplay(config, console)
        
        # Test display capabilities
        console.print(f"✅ Video display system initialized")
        console.print(f"🎮 Best player: {display.capabilities.get_best_player()}")
        console.print(f"⚙️ Display mode: {config.display_mode}")
        
        return display
        
    except Exception as e:
        console.print(f"❌ Display test failed: {e}")
        return None

def test_fal_api_setup():
    """Test Fal AI API setup (without making actual calls)"""
    console = Console()
    console.print(Panel("🔗 Testing Fal AI API Setup", border_style="blue"))
    
    try:
        from cocoa_video import VideoConfig, FalAIVideoAPI
        
        config = VideoConfig()
        api = FalAIVideoAPI(config)
        
        # Check API key status
        if api.api_key and api.api_key != "your-fal-api-key-here":
            console.print("✅ Fal AI API key configured")
            console.print(f"🔑 Key preview: {api.api_key[:8]}..." if len(api.api_key) > 8 else "🔑 Key set")
        else:
            console.print("⚠️ Fal AI API key not configured")
            console.print("💡 Set FAL_API_KEY in your .env file to enable video generation")
        
        # Check fal_client availability
        try:
            import fal_client
            console.print("✅ fal_client library available")
        except ImportError:
            console.print("❌ fal_client not installed")
            console.print("💡 Install with: pip install fal-client")
        
        return api
        
    except Exception as e:
        console.print(f"❌ API setup test failed: {e}")
        return None

def test_video_gallery():
    """Test video gallery and memory system"""
    console = Console()
    console.print(Panel("🖼️ Testing Video Gallery", border_style="blue"))
    
    try:
        from cocoa_video import VideoGallery
        
        # Create gallery with test workspace
        test_workspace = "coco_workspace/videos"
        gallery = VideoGallery(console, test_workspace)
        
        console.print("✅ Video gallery initialized")
        console.print(f"📂 Workspace: {gallery.workspace}")
        console.print(f"💾 Memory file: {gallery.memory_file}")
        
        # Show current gallery
        gallery.show_gallery()
        
        return gallery
        
    except Exception as e:
        console.print(f"❌ Gallery test failed: {e}")
        return None

async def test_video_cognition():
    """Test complete video consciousness system"""
    console = Console()
    console.print(Panel("🧠 Testing Video Cognition System", border_style="blue"))
    
    try:
        from cocoa_video import VideoConfig, VideoCognition
        
        # Initialize video consciousness
        config = VideoConfig()
        workspace_path = Path("coco_workspace")
        video_consciousness = VideoCognition(config, workspace_path, console)
        
        console.print("✅ Video consciousness initialized")
        console.print(f"🎬 Enabled: {video_consciousness.is_enabled()}")
        
        # Test quick access (should show no videos initially)
        success = video_consciousness.quick_video_access()
        console.print(f"🎯 Quick access test: {'✅' if not success else '⚠️'} (expected no videos)")
        
        # Show gallery (should be empty initially)
        video_consciousness.show_gallery()
        
        return video_consciousness
        
    except Exception as e:
        console.print(f"❌ Video cognition test failed: {e}")
        return None

def test_workspace_setup():
    """Test workspace directory structure"""
    console = Console()
    console.print(Panel("📁 Testing Workspace Setup", border_style="blue"))
    
    try:
        workspace_path = Path("coco_workspace/videos")
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create thumbnails directory
        thumbnails_path = workspace_path / "thumbnails"
        thumbnails_path.mkdir(exist_ok=True)
        
        console.print(f"✅ Workspace created: {workspace_path}")
        console.print(f"✅ Thumbnails directory: {thumbnails_path}")
        
        # Check if directories exist
        if workspace_path.exists() and thumbnails_path.exists():
            console.print("✅ All video workspace directories ready")
            return True
        else:
            console.print("❌ Workspace creation failed")
            return False
            
    except Exception as e:
        console.print(f"❌ Workspace setup failed: {e}")
        return False

async def main():
    """Run all video consciousness tests"""
    console = Console()
    
    # Header
    console.print(Panel.fit(
        "[bold bright_magenta]🎬 COCO Video Consciousness System Test[/bold bright_magenta]\n"
        "[dim]Complete validation of temporal imagination capabilities[/dim]",
        border_style="bright_magenta"
    ))
    
    # Run all tests
    results = {}
    
    results['imports'] = test_imports()
    results['dependencies'] = test_dependencies()
    results['config'] = test_video_config() is not None
    results['capabilities'] = test_video_capabilities() is not None
    results['display'] = test_video_display() is not None
    results['fal_api'] = test_fal_api_setup() is not None
    results['gallery'] = test_video_gallery() is not None
    results['cognition'] = await test_video_cognition() is not None
    results['workspace'] = test_workspace_setup()
    
    # Summary
    console.print("\n" + "="*60)
    
    summary_table = Table(title="📊 Test Results Summary", box=box.DOUBLE_EDGE)
    summary_table.add_column("Test", style="bright_white")
    summary_table.add_column("Status", justify="center")
    summary_table.add_column("Description", style="dim")
    
    test_descriptions = {
        'imports': 'Video consciousness module imports',
        'dependencies': 'Required Python packages',
        'config': 'Video configuration system',
        'capabilities': 'Video player detection',
        'display': 'Terminal display system',
        'fal_api': 'Fal AI API integration',
        'gallery': 'Video gallery and memory',
        'cognition': 'Complete video consciousness',
        'workspace': 'File system workspace'
    }
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        if success:
            status = "[bright_green]✅ PASS[/bright_green]"
            passed += 1
        else:
            status = "[bright_red]❌ FAIL[/bright_red]"
        
        description = test_descriptions.get(test_name, "Unknown test")
        summary_table.add_row(test_name.title(), status, description)
    
    console.print(summary_table)
    
    # Final result
    if passed == total:
        console.print(Panel(
            f"🎉 [bold bright_green]ALL TESTS PASSED[/bold bright_green] ({passed}/{total})\n\n"
            "🎬 Video consciousness system is ready!\n"
            "💡 Set your FAL_API_KEY to start generating videos",
            title="✅ Test Complete",
            border_style="bright_green"
        ))
    else:
        failed = total - passed
        console.print(Panel(
            f"⚠️ [bold yellow]{passed}/{total} TESTS PASSED[/bold yellow]\n\n"
            f"❌ {failed} test(s) failed\n"
            "💡 Check the details above and fix any issues",
            title="⚠️ Test Results",
            border_style="yellow"
        ))
    
    return passed == total

if __name__ == "__main__":
    # Run the test suite
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"💥 Test suite crashed: {e}")
        sys.exit(1)
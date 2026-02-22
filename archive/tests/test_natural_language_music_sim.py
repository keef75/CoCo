#!/usr/bin/env python3
"""
Test natural language music generation by simulating the _generate_music_tool call
"""

import sys
from pathlib import Path
from rich.console import Console

# Add project root to path  
sys.path.insert(0, str(Path(__file__).parent))

def test_natural_language_simulation():
    """Simulate what happens when user says 'create a song about dogs running with polka beat'"""
    
    console = Console()
    console.print('[bold cyan]🎵 Testing Natural Language → Music Tool Integration[/bold cyan]')
    
    # Import the main COCO system
    try:
        from cocoa import ConsciousnessEngine, Config, MemorySystem, ToolSystem
    except ImportError as e:
        console.print(f'[red]❌ Import error: {e}[/red]')
        return
    
    # Initialize COCO like the main app does
    try:
        config = Config()
        memory = MemorySystem(config)
        tools = ToolSystem(config)
        orchestrator = ConsciousnessEngine(config, memory, tools)
        
        # Wait for systems to initialize
        import time
        time.sleep(2)
        
        console.print('[green]✅ COCO orchestrator initialized[/green]')
        
        # Test the music tool directly (simulating function calling)
        tool_input = {
            "prompt": "dogs running with a polka beat",
            "duration": 30,
            "style": "polka"
        }
        
        console.print('[yellow]🎼 Calling _generate_music_tool with natural language input...[/yellow]')
        result = orchestrator._generate_music_tool(tool_input)
        
        console.print('[bright_green]🎵 Music Tool Result:[/bright_green]')
        console.print(result)
        
        # Check if files were initiated
        music_dir = Path('coco_workspace/music/generated')
        if music_dir.exists():
            files = list(music_dir.glob('*.mp3')) + list(music_dir.glob('*.wav'))
            console.print(f'[cyan]📁 Files in music directory: {len(files)}[/cyan]')
        
    except Exception as e:
        console.print(f'[red]❌ Test error: {e}[/red]')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_natural_language_simulation()
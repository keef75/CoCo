#!/usr/bin/env python3
"""
Test natural language music generation (the fixed implementation)
"""

import asyncio
import os
import sys
from pathlib import Path
from rich.console import Console

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_music import MusicConfig, MusicCognition

async def test_natural_language_music():
    """Test the restored music generation system"""
    
    console = Console()
    console.print('[bold cyan]🎵 Testing Fixed Natural Language Music Generation[/bold cyan]')
    
    # Initialize music system like cocoa.py does
    music_config = MusicConfig()
    if not music_config.enabled:
        console.print('[red]❌ MusicGPT API key not configured[/red]')
        return
    
    workspace_path = Path('coco_workspace')
    music_consciousness = MusicCognition(music_config, workspace_path, console)
    
    # Test the same method that natural language calls
    console.print('[yellow]🎼 Testing music generation via compose() method...[/yellow]')
    
    try:
        result = await music_consciousness.compose(
            prompt="dogs running with a polka beat",
            style="polka", 
            duration=30
        )
        
        if result.get('status') == 'success':
            console.print('[green]✅ Music generation initiated successfully![/green]')
            console.print(f"🎼 Composition ID: {result.get('composition_id', 'unknown')}")
            console.print('[yellow]🎵 Background download should start automatically...[/yellow]')
            
            # Wait a bit to see if files appear
            import time
            console.print('[dim]Waiting 60 seconds for any immediate results...[/dim]')
            time.sleep(60)
            
            # Check for files
            generated_dir = workspace_path / "music" / "generated"
            if generated_dir.exists():
                files = list(generated_dir.glob('*.mp3')) + list(generated_dir.glob('*.wav'))
                if files:
                    console.print(f'[bright_green]🎧 SUCCESS! Found {len(files)} generated files:[/bright_green]')
                    for file in files:
                        console.print(f'   📁 {file.name}')
                else:
                    console.print('[yellow]⏳ No files yet - generation may still be in progress[/yellow]')
            else:
                console.print('[yellow]⏳ Generated directory not created yet[/yellow]')
                
        else:
            console.print(f'[red]❌ Generation failed: {result}[/red]')
            
    except Exception as e:
        console.print(f'[red]❌ Test error: {e}[/red]')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_natural_language_music())
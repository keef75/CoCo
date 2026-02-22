#!/usr/bin/env python3
"""
Test the complete webhook-based music generation system
"""

import asyncio
import time
from cocoa_music import MusicConfig, MusicCognition
from pathlib import Path
from rich.console import Console

async def test_webhook_music_system():
    """Test complete webhook-based music generation"""
    
    console = Console()
    console.print('[cyan]🎵 Testing webhook-based music generation system...[/cyan]')
    
    config = MusicConfig()
    if not config.enabled:
        console.print('[red]❌ MusicGPT API key not configured[/red]')
        return
    
    workspace = Path('coco_workspace')
    music_cognition = MusicCognition(config, workspace, console)
    
    # Test music generation with webhook
    console.print('[yellow]🎼 Generating music with webhook delivery...[/yellow]')
    result = await music_cognition.compose(
        'energetic electronic test track', 
        style='electronic', 
        duration=15  # Short for faster testing
    )
    
    if result.get('status') == 'success':
        console.print('[green]✅ Music generation initiated with webhook URL![/green]')
        
        # Show webhook server status
        if music_cognition.webhook_server:
            console.print('[cyan]🔗 Webhook server running on http://localhost:8765/musicgpt-webhook[/cyan]')
            console.print('[yellow]📡 Waiting for MusicGPT to deliver files via webhook...[/yellow]')
            
            # Wait for webhook delivery
            eta = result.get('composition_specification', {}).get('duration', 60)
            wait_time = eta + 90  # ETA + extra buffer for processing
            
            console.print(f'[dim]Waiting up to {wait_time} seconds for webhook delivery...[/dim]')
            
            # Check for files periodically
            for i in range(0, wait_time, 30):
                time.sleep(30)
                
                # Check if files appeared
                generated_dir = Path('coco_workspace/music/generated')
                if generated_dir.exists():
                    files = list(generated_dir.glob('*.mp3')) + list(generated_dir.glob('*.wav'))
                    if files:
                        console.print(f'[bright_green]🎧 SUCCESS! Found {len(files)} generated files:[/bright_green]')
                        for file in files:
                            console.print(f'   📁 {file.name}')
                        break
                        
                console.print(f'[dim]Still waiting... {i+30}s elapsed[/dim]')
                
            else:
                console.print('[yellow]⏰ Webhook delivery timeout - check your MusicGPT email[/yellow]')
        else:
            console.print('[yellow]⚠️ No webhook server - files will be emailed[/yellow]')
    else:
        console.print(f'[red]❌ Generation failed: {result}[/red]')

if __name__ == "__main__":
    asyncio.run(test_webhook_music_system())
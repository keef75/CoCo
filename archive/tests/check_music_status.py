#!/usr/bin/env python3
"""
Check Music Generation Status and Download Songs
==============================================
"""

import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

async def check_music_status():
    print("🎵 Checking Your Music Generation Status")
    print("=" * 50)
    
    # Check for metadata files
    library_dir = Path("coco_workspace/ai_songs/generated")
    
    if not library_dir.exists():
        print("❌ Music library directory doesn't exist yet")
        library_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Created library directory")
        return
    
    # Find all composition metadata files
    metadata_files = list(library_dir.glob("*.json"))
    
    if not metadata_files:
        print("❌ No compositions found in library")
        return
    
    print(f"📚 Found {len(metadata_files)} compositions in library:")
    
    for metadata_file in metadata_files:
        print(f"\n📄 {metadata_file.name}")
        
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            
            print(f"   Concept: {data.get('description', 'Unknown')}")
            print(f"   Task ID: {data.get('task_id', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Style: {data.get('style', 'Unknown')}")
            print(f"   Created: {data.get('timestamp', 'Unknown')}")
            
            # Check for audio files
            task_id = data.get('task_id')
            if task_id:
                audio_files = list(library_dir.glob(f"*{task_id}*.mp3"))
                if audio_files:
                    print(f"   🎵 Audio files: {len(audio_files)} found")
                    for audio_file in audio_files:
                        print(f"      - {audio_file.name}")
                else:
                    print("   ⏳ Audio files not downloaded yet (still generating)")
            
        except Exception as e:
            print(f"   ❌ Error reading metadata: {e}")
    
    print("\n" + "=" * 50)
    
    # Check if we can poll MusicGPT for completion
    musicgpt_key = os.getenv('MUSICGPT_API_KEY')
    if musicgpt_key and metadata_files:
        print("🔄 Attempting to check generation status...")
        
        try:
            from cocoa_audio import AudioCognition
            
            audio = AudioCognition(
                elevenlabs_api_key=os.getenv('ELEVENLABS_API_KEY'),
                musicgpt_api_key=musicgpt_key
            )
            
            # Check status of most recent composition
            latest_file = max(metadata_files, key=lambda f: f.stat().st_mtime)
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            task_id = data.get('task_id')
            if task_id:
                print(f"Checking status for Task ID: {task_id}")
                status_result = await audio.musician.check_music_status(task_id)
                
                if status_result.get("status") == "completed":
                    print("✅ Music generation completed!")
                    if "files" in status_result:
                        print(f"🎵 Downloaded files: {status_result['files']}")
                elif status_result.get("status") == "generating":
                    print("⏳ Still generating... please wait")
                else:
                    print(f"Status: {status_result}")
            
        except Exception as e:
            print(f"❌ Status check failed: {e}")
    
    print("\n📁 Your music library location:")
    print(f"   {library_dir.absolute()}")

if __name__ == "__main__":
    asyncio.run(check_music_status())
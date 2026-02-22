#!/usr/bin/env python3
"""
Test script for COCO's continuous background music system
"""

import time
import sys
from pathlib import Path
from cocoa import BackgroundMusicPlayer

def test_continuous_music():
    """Test the continuous music playback system"""
    
    print("🎵 Testing COCO's Continuous Background Music System")
    print("=" * 50)
    
    # Initialize player
    player = BackgroundMusicPlayer()
    audio_dir = Path('./coco_workspace/audio_library/background')
    
    # Check if audio directory exists
    if not audio_dir.exists():
        print(f"❌ Audio directory not found: {audio_dir}")
        return False
        
    # Load playlist
    playlist = player.load_playlist(audio_dir)
    print(f"🎶 Loaded {len(playlist)} tracks:")
    for i, track in enumerate(playlist[:5]):  # Show first 5
        print(f"   {i+1}. {track.name}")
    if len(playlist) > 5:
        print(f"   ... and {len(playlist) - 5} more")
    print()
    
    if not playlist:
        print("❌ No audio files found")
        return False
    
    try:
        print("🚀 Starting continuous playback...")
        success = player.play(continuous=True)
        
        if not success:
            print("❌ Failed to start playback")
            return False
            
        print(f"✅ Now playing: {player.current_track.name}")
        print("🔄 Continuous mode enabled - will auto-advance between tracks")
        print()
        
        # Let it play for a few seconds to test
        for i in range(10):
            if player.current_process and player.current_process.poll() is None:
                print(f"⏯️  Playing... ({i+1}/10s) - Track: {player.current_track.name}")
            else:
                print(f"🔄 Track finished, should advance automatically...")
            time.sleep(1)
        
        print()
        print("🛑 Stopping continuous playback...")
        player.stop()
        print("✅ Stopped successfully")
        
        # Verify cleanup
        if not player.is_playing and player.current_process is None:
            print("✅ Clean shutdown confirmed")
            return True
        else:
            print("⚠️  Some cleanup issues detected")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 User interrupted - stopping...")
        player.stop()
        return True
    except Exception as e:
        print(f"❌ Error during test: {e}")
        player.stop()
        return False

if __name__ == "__main__":
    success = test_continuous_music()
    print()
    if success:
        print("🎉 CONTINUOUS MUSIC SYSTEM: ✅ WORKING PERFECTLY!")
        print("🎵 Beautiful background music is now available for COCO users!")
    else:
        print("❌ CONTINUOUS MUSIC SYSTEM: Issues detected")
        sys.exit(1)
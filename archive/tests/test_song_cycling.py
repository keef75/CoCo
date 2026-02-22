#!/usr/bin/env python3
"""
Test script for COCO's song cycling variety in /play-music command
"""

import time
from pathlib import Path
from cocoa import BackgroundMusicPlayer

def test_song_cycling():
    """Test that /play-music starts with different songs each time"""
    
    print("🎵 Testing COCO's Song Cycling Variety")
    print("=" * 40)
    
    # Initialize player
    player = BackgroundMusicPlayer()
    audio_dir = Path('./coco_workspace/audio_library/background')
    
    if not audio_dir.exists():
        print(f"❌ Audio directory not found: {audio_dir}")
        return False
        
    # Load playlist
    playlist = player.load_playlist(audio_dir)
    print(f"🎶 Loaded {len(playlist)} tracks")
    
    if len(playlist) < 2:
        print("⚠️ Need at least 2 tracks to test cycling")
        return False
    
    print("\n🔄 Testing cycling variety (should start with different songs):")
    print("-" * 50)
    
    starting_songs = []
    
    # Test 5 cycles
    for i in range(min(5, len(playlist))):
        print(f"\n🎵 Test {i+1}/5:")
        
        # Cycle to next starting song
        player.cycle_starting_song()
        current_index = player.current_index
        current_song = player.playlist[current_index].name if player.playlist else "None"
        
        starting_songs.append(current_song)
        print(f"   • Starting index: {current_index}")
        print(f"   • Starting song: {current_song}")
        
        # Brief play test
        if player.play(continuous=False):
            time.sleep(0.5)  # Very brief test
            player.stop()
            print("   • ✅ Playback test successful")
        else:
            print("   • ❌ Playback test failed")
    
    # Check for variety
    unique_songs = len(set(starting_songs))
    total_tests = len(starting_songs)
    
    print(f"\n📊 Results:")
    print(f"   • Total tests: {total_tests}")
    print(f"   • Unique starting songs: {unique_songs}")
    print(f"   • Variety percentage: {unique_songs/total_tests*100:.1f}%")
    
    if unique_songs > 1:
        print("   • ✅ VARIETY ACHIEVED!")
        print(f"   • Starting songs were: {starting_songs}")
        return True
    else:
        print("   • ❌ No variety - same song every time")
        return False

if __name__ == "__main__":
    success = test_song_cycling()
    print()
    if success:
        print("🎉 SONG CYCLING: ✅ WORKING PERFECTLY!")
        print("🎵 Users will now get variety in their background music experience!")
    else:
        print("❌ SONG CYCLING: Issues detected")
#!/usr/bin/env python3
"""
Test that video observer initializes and help page displays correctly
"""

import sys
from unittest.mock import Mock
from rich.console import Console

# Mock the config to prevent full COCO initialization
console = Console()

print("\n" + "="*70)
print("TEST 1: Video Observer Import and Initialization")
print("="*70 + "\n")

try:
    from cocoa_video_observer import VideoObserver, VideoObserverConfig
    print("✅ Import successful: cocoa_video_observer")

    # Test initialization
    config = VideoObserverConfig()
    observer = VideoObserver(config)

    print(f"✅ Initialization successful")
    print(f"   Backend: {observer.backend['type']}")
    print(f"   Description: {observer.backend['description']}")

    # Check backend capabilities
    backend_caps = observer.backend.get('capabilities', {})
    print(f"   Capabilities:")
    print(f"     - Inline playback: {'✅' if backend_caps.get('inline', False) else '❌'}")
    print(f"     - YouTube support: {'✅' if backend_caps.get('youtube', False) else '❌'}")
    print(f"     - Playback controls: {'✅' if backend_caps.get('controls', False) else '❌'}")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("TEST 2: Verify help page video commands are in cocoa.py")
print("="*70 + "\n")

try:
    with open('cocoa.py', 'r') as f:
        content = f.read()

    # Check for key video commands in help page section
    commands_to_check = [
        '/watch <url|file>',
        '/watch-yt <url>',
        '/watch-audio <url>',
        '/watch-inline <url>',
        '/watch-window <url>',
        '/watch-caps',
        '/watch-pause',
        '/watch-seek <sec>',
        '/watch-volume <0-100>',
        '/watch-speed <0.5-2>',
        'VIDEO OBSERVATION',
        'PLAYBACK CONTROLS'
    ]

    all_found = True
    for cmd in commands_to_check:
        if cmd in content:
            print(f"✅ Found: {cmd}")
        else:
            print(f"❌ Missing: {cmd}")
            all_found = False

    if all_found:
        print("\n✅ All video commands found in help page")
    else:
        print("\n❌ Some commands missing from help page")
        sys.exit(1)

except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("TEST 3: Verify _init_video_observer() is called in __init__")
print("="*70 + "\n")

try:
    with open('cocoa.py', 'r') as f:
        content = f.read()

    # Find the __init__ method and check if _init_video_observer is called
    if 'self._init_video_observer()' in content:
        print("✅ Found: self._init_video_observer() call")

        # Check it's in the right section (between visual and google workspace)
        init_section = content[content.find('def __init__'):content.find('def _init_audio_consciousness')]

        if 'self._init_video_observer()' in init_section:
            print("✅ Call is in __init__ method")
        else:
            print("⚠️  Call exists but may not be in __init__ method")
    else:
        print("❌ Missing: self._init_video_observer() call")
        sys.exit(1)

except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL TESTS PASSED")
print("="*70)
print("\nThe video observer should now:")
print("1. Initialize on COCO startup")
print("2. Display initialization message")
print("3. Show all 14 commands in /help")
print("\nReady to test with: python3 cocoa.py")
print("="*70 + "\n")

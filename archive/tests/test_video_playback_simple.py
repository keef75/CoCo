#!/usr/bin/env python3
"""
Simple test script to verify video playback setup
Tests the exact command COCO will use
"""

import os
import sys
import shutil
import subprocess
import platform

def ensure_path_for_brew(env):
    """Fix PATH for Homebrew binaries"""
    prefixes = ["/opt/homebrew/bin", "/usr/local/bin"]
    path = env.get("PATH", "")
    for prefix in prefixes:
        if os.path.isdir(prefix) and prefix not in path:
            path = f"{prefix}:{path}"
    env["PATH"] = path
    return env

print("="*70)
print("  COCO Video Playback Test")
print("="*70)
print()

# Test URL
test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"

# Check environment
print("1. Environment Check:")
print(f"   Platform: {platform.system()}")
print(f"   Python: {sys.version.split()[0]}")
print()

# Check mpv
print("2. Checking mpv:")
mpv_path = shutil.which("mpv")
if mpv_path:
    print(f"   ✅ Found: {mpv_path}")
    try:
        result = subprocess.run(["mpv", "--version"], capture_output=True, text=True, timeout=2)
        version = result.stdout.split('\n')[0]
        print(f"   Version: {version}")
    except:
        pass
else:
    print("   ❌ mpv NOT FOUND")
    print("   Install: brew install mpv")
    sys.exit(1)

print()

# Check yt-dlp
print("3. Checking yt-dlp:")
ytdlp_path = shutil.which("yt-dlp")
if not ytdlp_path:
    ytdlp_path = "/opt/homebrew/bin/yt-dlp"

if os.path.exists(ytdlp_path):
    print(f"   ✅ Found: {ytdlp_path}")
    try:
        result = subprocess.run([ytdlp_path, "--version"], capture_output=True, text=True, timeout=2)
        print(f"   Version: {result.stdout.strip()}")
    except:
        pass
else:
    print("   ❌ yt-dlp NOT FOUND")
    print("   Install: brew install yt-dlp")
    sys.exit(1)

print()
print("="*70)
print("  Testing EXACT COCO Command")
print("="*70)
print()

# Build exact command COCO uses
cmd = [
    "mpv",
    "--no-terminal",
    "--force-window",
    f"--script-opts=ytdl_hook-ytdl_path={ytdlp_path}",
    test_url
]

print("Command:")
print("  " + " ".join(cmd))
print()

print("This should:")
print("  1. Open a new mpv window")
print("  2. Play the YouTube video")
print("  3. Close when done")
print()

input("Press Enter to run test (Ctrl+C to cancel)...")

# Run with PATH fix
env = ensure_path_for_brew(os.environ.copy())

print()
print("Running...")
print()

result = subprocess.run(
    cmd,
    env=env,
    capture_output=True,
    text=True
)

print(f"Exit code: {result.returncode}")

if result.returncode == 0:
    print("✅ SUCCESS - Video should have played!")
else:
    print(f"❌ FAILED - Exit code {result.returncode}")

    if result.stderr:
        print()
        print("Error output:")
        print(result.stderr[:500])

    if result.stdout:
        print()
        print("Standard output:")
        print(result.stdout[:500])

print()
print("="*70)
print()

if result.returncode != 0:
    print("Troubleshooting steps:")
    print("1. Upgrade yt-dlp: brew upgrade yt-dlp")
    print("2. Check mpv works: mpv --version")
    print(f"3. Test yt-dlp directly: {ytdlp_path} --get-title {test_url}")
    print("4. Try in native terminal (not Cursor/VS Code)")
    print()

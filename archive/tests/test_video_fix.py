#!/usr/bin/env python3
"""
Quick test to verify video playback fix works
Tests the exact setup COCO will use
"""

import os
import sys
import shutil
import subprocess

def ensure_path_for_brew(env=None):
    """PREPEND Homebrew paths with deduplication"""
    env = dict(os.environ if env is None else env)
    bins = ["/opt/homebrew/bin", "/usr/local/bin", os.path.expanduser("~/.local/bin")]
    parts = [p for p in env.get("PATH", "").split(":") if p]
    for b in reversed(bins):
        if b in parts:
            parts.remove(b)
        if os.path.isdir(b):
            parts.insert(0, b)
    env["PATH"] = ":".join(parts)
    return env

print("="*70)
print("  Video Playback Fix Verification")
print("="*70)
print()

# Fix PATH
env = ensure_path_for_brew()

# Find yt-dlp
ytdlp_path = shutil.which("yt-dlp", path=env["PATH"]) or "/opt/homebrew/bin/yt-dlp"
print(f"yt-dlp path: {ytdlp_path}")

# Check version
try:
    result = subprocess.run([ytdlp_path, "--version"], capture_output=True, text=True, env=env, timeout=2)
    version = result.stdout.strip()
    print(f"yt-dlp version: {version}")

    # Warn if old
    if version.startswith("2023."):
        print("❌ OLD VERSION - Will cause 403 errors!")
        print("Fix: brew upgrade yt-dlp && brew link --overwrite yt-dlp")
        sys.exit(1)
    elif version.startswith(("2024.", "2025.")):
        print("✅ Current version - should work!")
    else:
        print(f"⚠️  Unknown version: {version}")
except Exception as e:
    print(f"❌ Error checking version: {e}")
    sys.exit(1)

print()

# Test YouTube resolution
print("Testing YouTube resolution...")
try:
    result = subprocess.run(
        [ytdlp_path, "--get-title", "https://www.youtube.com/watch?v=jNQXAC9IVRw"],
        capture_output=True,
        text=True,
        env=env,
        timeout=15
    )

    if result.returncode == 0:
        title = result.stdout.strip()
        print(f"✅ Resolved: {title}")
    else:
        print(f"❌ Resolution failed: {result.stderr}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()

# Check mpv
mpv_path = shutil.which("mpv", path=env["PATH"])
if not mpv_path:
    print("❌ mpv not found - install with: brew install mpv")
    sys.exit(1)

print(f"mpv path: {mpv_path}")

print()
print("="*70)
print("  All checks passed! ✅")
print("="*70)
print()
print("Ready to test in COCO:")
print("  python3 cocoa.py")
print("  /watch-window https://www.youtube.com/watch?v=jNQXAC9IVRw")
print()

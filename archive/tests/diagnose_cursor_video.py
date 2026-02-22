#!/usr/bin/env python3
"""
Diagnostic script to debug video playback in Cursor terminal
Tests each component of the video playback stack
"""

import os
import sys
import shutil
import subprocess
import platform

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def ensure_path_for_brew(env):
    """Fix PATH for Homebrew binaries"""
    prefixes = ["/opt/homebrew/bin", "/usr/local/bin"]
    path = env.get("PATH", "")
    for prefix in prefixes:
        if os.path.isdir(prefix) and prefix not in path:
            path = f"{prefix}:{path}"
    env["PATH"] = path
    return env

print_section("CURSOR TERMINAL VIDEO PLAYBACK DIAGNOSTICS")

# Test 1: Environment check
print_section("Test 1: Environment & PATH")
env = os.environ.copy()
print(f"Original PATH: {env.get('PATH', 'NOT SET')[:100]}...")
env_fixed = ensure_path_for_brew(env.copy())
print(f"Fixed PATH:    {env_fixed.get('PATH', 'NOT SET')[:100]}...")
print(f"Platform:      {platform.system()}")
print(f"Python:        {sys.version}")

# Test 2: Command availability
print_section("Test 2: Command Availability")
commands = ["mpv", "ffplay", "yt-dlp", "youtube-dl"]
for cmd in commands:
    path = shutil.which(cmd)
    if path:
        print(f"✅ {cmd:12} → {path}")
        # Get version
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=2)
            version_line = result.stdout.split('\n')[0][:60]
            print(f"   Version: {version_line}")
        except:
            pass
    else:
        print(f"❌ {cmd:12} → NOT FOUND")

# Test 3: mpv VO support
print_section("Test 3: mpv Video Output (VO) Support")
mpv_path = shutil.which("mpv")
if mpv_path:
    try:
        result = subprocess.run(["mpv", "--vo=help"], capture_output=True, text=True, timeout=2)
        print("Available VOs:")
        for line in result.stdout.split('\n'):
            if line.strip() and not line.startswith('Available'):
                print(f"  {line}")

        # Check specific VOs
        has_tct = "tct" in result.stdout
        has_kitty = "kitty" in result.stdout
        print(f"\n✅ TCT VO:   {'Available' if has_tct else 'NOT AVAILABLE'}")
        print(f"✅ Kitty VO: {'Available' if has_kitty else 'NOT AVAILABLE'}")
    except Exception as e:
        print(f"❌ Failed to check VOs: {e}")
else:
    print("❌ mpv not available - skipping VO check")

# Test 4: YouTube resolution
print_section("Test 4: YouTube URL Resolution")
test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
print(f"Test URL: {test_url}")

yt_dlp = shutil.which("yt-dlp")
if yt_dlp:
    try:
        # Test yt-dlp resolution
        print("\nTesting yt-dlp URL resolution...")
        result = subprocess.run(
            [yt_dlp, "--get-title", "--get-duration", test_url],
            capture_output=True,
            text=True,
            timeout=15,
            env=env_fixed
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"✅ Title:    {lines[0] if len(lines) > 0 else 'Unknown'}")
            print(f"✅ Duration: {lines[1] if len(lines) > 1 else 'Unknown'}")

            # Test direct URL extraction
            print("\nTesting direct stream URL extraction...")
            result = subprocess.run(
                [yt_dlp, "-gf", "best", test_url],
                capture_output=True,
                text=True,
                timeout=15,
                env=env_fixed
            )
            if result.returncode == 0:
                stream_url = result.stdout.strip()
                print(f"✅ Direct stream URL extracted ({len(stream_url)} chars)")
                print(f"   {stream_url[:80]}...")
            else:
                print(f"❌ Failed to extract stream URL: {result.stderr}")
        else:
            print(f"❌ yt-dlp failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ yt-dlp timed out (network issue?)")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ yt-dlp not available")

# Test 5: mpv window mode (no VO flags)
print_section("Test 5: mpv Window Mode Test (5 seconds)")
if mpv_path and yt_dlp:
    print("Testing: mpv --no-config --no-terminal --player-operation-mode=pseudo-gui")
    print(f"         --script-opts=ytdl_hook-ytdl_path={yt_dlp}")
    print(f"         {test_url}")
    print("\nThis should open an external mpv window for 5 seconds...")

    cmd = [
        "mpv",
        "--no-config",
        "--no-terminal",
        "--player-operation-mode=pseudo-gui",
        f"--script-opts=ytdl_hook-ytdl_path={yt_dlp}",
        "--length=5",  # Only play 5 seconds
        test_url
    ]

    try:
        # Run detached
        p = subprocess.Popen(
            cmd,
            env=env_fixed,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )

        # Wait for completion
        stderr_output = p.communicate(timeout=15)[1]

        if p.returncode == 0:
            print("✅ mpv window mode succeeded!")
        else:
            print(f"❌ mpv window mode failed with exit code: {p.returncode}")
            if stderr_output:
                print(f"   stderr: {stderr_output.decode()[:200]}")
    except subprocess.TimeoutExpired:
        print("⚠️  mpv still running (good sign - window likely opened)")
        p.kill()
    except Exception as e:
        print(f"❌ Error launching mpv: {e}")
else:
    print("❌ mpv or yt-dlp not available - skipping test")

# Test 6: ffplay with pre-resolved stream
print_section("Test 6: ffplay Window Mode Test (5 seconds)")
ffplay_path = shutil.which("ffplay")
if ffplay_path and yt_dlp:
    print("Testing: ffplay with pre-resolved stream URL")

    try:
        # First resolve the stream
        print("Resolving stream URL...")
        result = subprocess.run(
            [yt_dlp, "-gf", "best", test_url],
            capture_output=True,
            text=True,
            timeout=15,
            env=env_fixed
        )

        if result.returncode == 0:
            stream_url = result.stdout.strip()
            print(f"✅ Stream resolved ({len(stream_url)} chars)")

            # Try to play with ffplay
            print("\nTesting ffplay playback (5 seconds)...")
            cmd = ["ffplay", "-autoexit", "-loglevel", "error", "-t", "5", stream_url]

            p = subprocess.Popen(
                cmd,
                env=env_fixed,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )

            stderr_output = p.communicate(timeout=15)[1]

            if p.returncode == 0:
                print("✅ ffplay window mode succeeded!")
            else:
                print(f"❌ ffplay failed with exit code: {p.returncode}")
                if stderr_output:
                    print(f"   stderr: {stderr_output.decode()[:200]}")
        else:
            print(f"❌ Failed to resolve stream: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⚠️  ffplay still running (good sign - window likely opened)")
        p.kill()
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ ffplay or yt-dlp not available - skipping test")

# Test 7: Python yt_dlp library
print_section("Test 7: Python yt_dlp Library")
try:
    from yt_dlp import YoutubeDL
    print("✅ yt_dlp library available")

    print("\nTesting library-based resolution...")
    ydl_opts = {
        "quiet": True,
        "noplaylist": True,
        "no_warnings": True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(test_url, download=False)

        # Get progressive formats
        progressive = [f for f in info["formats"]
                      if f.get("vcodec") != "none" and f.get("acodec") != "none"]

        if progressive:
            best = max(progressive, key=lambda f: f.get("tbr") or 0)
            print(f"✅ Best progressive format found:")
            print(f"   Quality: {best.get('format_note', 'unknown')}")
            print(f"   Bitrate: {best.get('tbr', 'unknown')} kbps")
            print(f"   URL:     {best.get('url', '')[:80]}...")
        else:
            print("⚠️  No progressive formats found (mpv can still handle this)")

except ImportError:
    print("❌ yt_dlp library not available")
    print("   Install with: pip install yt-dlp")
except Exception as e:
    print(f"❌ Error testing library: {e}")

# Summary
print_section("DIAGNOSTIC SUMMARY")
print("\nIf you see failures above, the issue is likely:")
print("1. ❌ mpv/ffplay not in PATH → Install or add to PATH")
print("2. ❌ yt-dlp not working → Network issue or install needed")
print("3. ❌ mpv window failed → Check stderr output above")
print("4. ❌ ffplay window failed → Stream resolution issue")
print("\nIf all tests pass but COCO still fails:")
print("- Try running COCO from a native terminal (iTerm2, Kitty)")
print("- Check COCO logs for specific error messages")
print("- Browser fallback is working (last resort)")

print("\n" + "="*70)
print("Run this in Cursor terminal to diagnose the issue")
print("="*70 + "\n")

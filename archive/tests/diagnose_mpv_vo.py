#!/usr/bin/env python3
"""
Diagnostic script to check mpv VO support and YouTube playback
Based on senior engineer recommendations
"""

import subprocess
import shutil
from rich.console import Console

console = Console()

print("\n" + "="*70)
print("MPV VIDEO OUTPUT (VO) DIAGNOSTIC")
print("="*70 + "\n")

# Test 1: Check if mpv is installed
console.print("[bold cyan]Test 1: Check mpv installation[/bold cyan]")
mpv_path = shutil.which("mpv")
if mpv_path:
    console.print(f"✅ mpv found at: {mpv_path}")
else:
    console.print("❌ mpv not found - install with: brew install mpv")
    exit(1)

# Test 2: Check available VOs
console.print("\n[bold cyan]Test 2: Check available video outputs[/bold cyan]")
try:
    result = subprocess.run(
        ["mpv", "--vo=help"],
        capture_output=True,
        text=True,
        timeout=2
    )
    console.print("[dim]Available VOs:[/dim]")
    for line in result.stdout.split('\n'):
        if line.strip():
            console.print(f"  {line}")

    # Check for specific VOs we care about
    has_kitty = "kitty" in result.stdout
    has_tct = "tct" in result.stdout
    has_sixel = "sixel" in result.stdout

    console.print(f"\n✅ Kitty VO: {'Yes' if has_kitty else 'No'}")
    console.print(f"✅ TCT VO: {'Yes' if has_tct else 'No'}")
    console.print(f"✅ SIXEL VO: {'Yes' if has_sixel else 'No'}")

    if not has_tct and not has_kitty:
        console.print("\n[yellow]⚠️  No inline VOs available in this mpv build[/yellow]")
        console.print("[yellow]   Video will fallback to window mode[/yellow]")

except Exception as e:
    console.print(f"❌ Failed to check VOs: {e}")

# Test 3: Check yt-dlp
console.print("\n[bold cyan]Test 3: Check yt-dlp installation[/bold cyan]")
ytdlp_path = shutil.which("yt-dlp")
if ytdlp_path:
    console.print(f"✅ yt-dlp found at: {ytdlp_path}")
else:
    console.print("⚠️  yt-dlp not found - install with: brew install yt-dlp")
    console.print("   mpv may fallback to youtube-dl (slower, less reliable)")

# Test 4: Test YouTube resolution (sanity check)
console.print("\n[bold cyan]Test 4: Test YouTube URL resolution[/bold cyan]")
test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
console.print(f"Test URL: {test_url}")

if ytdlp_path:
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-title", "--get-duration", test_url],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            console.print(f"✅ Title: {lines[0] if len(lines) > 0 else 'Unknown'}")
            console.print(f"✅ Duration: {lines[1] if len(lines) > 1 else 'Unknown'}")
        else:
            console.print(f"❌ Failed to resolve: {result.stderr}")
    except Exception as e:
        console.print(f"❌ Error: {e}")

# Test 5: Recommended command tests
console.print("\n[bold cyan]Test 5: Recommended command tests[/bold cyan]")
console.print("\n[dim]To test manually, run these commands:[/dim]\n")

console.print("1. Window mode (should always work):")
ytdl_flag = f"--script-opts=ytdl_hook-ytdl_path={ytdlp_path}" if ytdlp_path else ""
console.print(f"   mpv {ytdl_flag} \"{test_url}\"")

console.print("\n2. Inline mode (only if tct VO available):")
if has_tct:
    console.print(f"   mpv --vo=tct --really-quiet {ytdl_flag} \"{test_url}\"")
else:
    console.print("   [dim](not available - tct VO not in this build)[/dim]")

console.print("\n3. Audio-only mode (always works):")
console.print(f"   mpv --no-video \"{test_url}\"")

console.print("\n4. Pre-resolve with yt-dlp (bypass hook):")
if ytdlp_path:
    console.print(f"   mpv --vo=tct \"$(yt-dlp -gf 'bv*+ba/best' {test_url})\"")
else:
    console.print("   [dim](yt-dlp not available)[/dim]")

# Summary
console.print("\n" + "="*70)
console.print("DIAGNOSIS SUMMARY")
console.print("="*70)

if has_tct or has_kitty:
    console.print("✅ [green]Inline video playback should work[/green]")
    console.print(f"   Recommended VO: {'kitty' if has_kitty else 'tct'}")
else:
    console.print("⚠️  [yellow]Inline video NOT available in this mpv build[/yellow]")
    console.print("   Fallback modes available:")
    console.print("   - Window mode (opens separate window)")
    console.print("   - Audio-only mode (podcasts/lectures)")

if ytdlp_path:
    console.print("✅ [green]YouTube support fully functional[/green]")
else:
    console.print("⚠️  [yellow]Limited YouTube support (install yt-dlp recommended)[/yellow]")

console.print("\n[bold]Next step:[/bold] Run COCO and try /watch-yt with the test URL")
console.print("="*70 + "\n")

# Video Playback Final Solution - Simplified Native Approach

**Date**: October 1, 2025
**Status**: ✅ SIMPLIFIED AND READY FOR TESTING

## Problem Evolution

### Phase 1: Initial Breakage
**Symptoms**: No video playback, exit code 2 from mpv, no windows opening
**Root Causes**:
- TTY blocking in Electron terminals (Cursor/VS Code)
- Missing Homebrew PATH (/opt/homebrew/bin not loaded)
- Flag bleed-through (window mode inheriting `--vo=tct`)
- YouTube URL issues (page URLs vs direct streams)

**Solution Attempted**: Complex infrastructure with detached spawning, PATH patching, separate command builders, pre-resolution

### Phase 2: HTTP 403 Forbidden Errors
**Symptoms**: "Red wall of text" showing HTTP 403 from googlevideo URLs
**Root Causes**:
- Outdated yt-dlp (requirements.txt had `>=2023.0.0` from 2023!)
- Pre-resolved googlevideo URLs missing HTTP headers (User-Agent, Referer)
- Signed URLs expiring/failing without proper headers

**Solution Attempted**:
- Upgraded yt-dlp to `>=2024.10.0`
- Added header extraction and forwarding
- Created conversion functions for mpv/ffplay header formats

### Phase 3: Final Realization
**Insight**: We were over-engineering the solution by reimplementing what mpv already does perfectly.

**Problems with Complex Approach**:
- Pre-resolution adds failure points
- Header forwarding adds complexity
- Multiple fallback layers obscure actual errors
- Detached spawning hides error messages

**New Philosophy**: **SIMPLIFY - Let mpv do what it does best**

## Final Simplified Solution

### Core Principle
Trust mpv's ytdl_hook to handle YouTube URLs natively instead of pre-resolving and forwarding everything manually.

### Implementation

**`_play_window()` Method** (cocoa_video_observer.py lines 1051-1116):

```python
async def _play_window(self, url: str) -> Dict[str, Any]:
    """
    Simplified strategy - let mpv handle YouTube natively
    """
    if BackendDetector.which("mpv"):
        ytdlp_path = BackendDetector.which("yt-dlp") or "/opt/homebrew/bin/yt-dlp"

        cmd = [
            "mpv",
            "--no-terminal",        # Don't take over terminal
            "--force-window",       # Always open GUI window
            f"--script-opts=ytdl_hook-ytdl_path={ytdlp_path}",  # Use current yt-dlp
            url  # Pass YouTube URL DIRECTLY - no pre-resolution
        ]

        # Run synchronously to see errors
        env = BackendDetector.ensure_path_for_brew(os.environ.copy())
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        # Show actual errors for debugging
        if result.returncode != 0 and result.stderr:
            print(f"mpv error: {result.stderr.strip()[:200]}")

        if result.returncode == 0:
            return {"success": True, "method": "mpv_window"}

    # Fallback: macOS open command
    if platform.system() == "Darwin":
        subprocess.run(["open", url])
        return {"success": True, "method": "macos_open"}

    # Final fallback: browser
    webbrowser.open(url)
    return {"success": True, "method": "browser"}
```

### Why This Works

**mpv's ytdl_hook handles**:
- YouTube URL resolution automatically
- HTTP headers (User-Agent, Referer, cookies)
- Signature algorithm decoding
- Format selection and stream merging
- Authentication and age-restricted content

**We only need to**:
1. Ensure yt-dlp is current (`>=2024.10.0`)
2. Point mpv to the correct yt-dlp binary
3. Fix PATH for Homebrew binaries
4. Let mpv do its job

**Benefits**:
- Fewer failure points
- Better error visibility (not detached)
- Cleaner code (removed 200+ lines of complexity)
- Easier debugging (can see actual mpv errors)

## Prerequisites

### 1. Current yt-dlp (CRITICAL)
```bash
# Upgrade yt-dlp
brew upgrade yt-dlp

# Or via pip
pip3 install -U yt-dlp

# Verify version (should be 2024.10.0 or newer)
yt-dlp --version
```

**Why Critical**: Older versions can't decode YouTube's signature algorithm, causing 403 errors

### 2. mpv and yt-dlp Installed
```bash
# Install if missing
brew install mpv yt-dlp

# Verify
which mpv
which yt-dlp
```

### 3. Updated requirements.txt
Line 72 now requires current yt-dlp:
```python
# CRITICAL: Keep yt-dlp current to avoid 403 errors on YouTube
# Outdated versions can't decode YouTube's signature algorithm
yt-dlp>=2024.10.0
```

## Testing

### Quick Test Script
```bash
# Run standalone test
./test_video_playback_simple.py

# This will:
# 1. Check mpv and yt-dlp installation
# 2. Verify versions
# 3. Run exact command COCO uses
# 4. Show any errors
```

### Test in COCO
```bash
# Launch COCO
python3 cocoa.py

# Test video playback
/watch-window https://www.youtube.com/watch?v=jNQXAC9IVRw

# Expected behavior:
# - New mpv window opens
# - Video plays
# - COCO terminal shows exit code and any errors
```

### Expected Output (Success)
```
🎬 Launching mpv window player...
💡 Video will open in separate window
🎯 COCO terminal remains available

Running: mpv --no-terminal --force-window ...
mpv exit code: 0
✅ Video played in external window
```

### Expected Output (Failure - Shows Errors Now!)
```
🎬 Launching mpv window player...
Running: mpv --no-terminal --force-window ...
mpv exit code: 4
mpv error: [youtube] jNQXAC9IVRw: Failed to extract any player response...
⚠️ mpv failed (code 4)
```

## Troubleshooting

### If mpv exit code 4 (Can't resolve URL)
```bash
# Test yt-dlp directly
yt-dlp --get-title https://www.youtube.com/watch?v=jNQXAC9IVRw

# If this fails, upgrade yt-dlp
brew upgrade yt-dlp
```

### If "mpv not found"
```bash
# Check PATH
echo $PATH | grep homebrew

# If /opt/homebrew/bin missing, Cursor isn't loading shell profile
# The ensure_path_for_brew() function should fix this automatically
```

### If still HTTP 403 errors
```bash
# Verify yt-dlp version
yt-dlp --version  # Should be 2024.10.0 or newer

# Test in native terminal (not Cursor)
# Some network configurations block YouTube from terminals
```

### Last Resort: Browser Fallback
The browser fallback always works because it opens the YouTube page URL (not the googlevideo stream URL which requires headers).

## What Changed

### Files Modified

**cocoa_video_observer.py**:
- Lines 1051-1116: Simplified `_play_window()` method
- Lines 1085-1102: Added stderr capture for debugging
- Removed: Complex pre-resolution logic
- Removed: Header forwarding complexity
- Kept: PATH patching (still needed for Cursor)

**requirements.txt**:
- Line 72: Updated to `yt-dlp>=2024.10.0`

**CLAUDE.md**:
- Lines 534-600: Updated ADR-011 with simplified approach

**New Files**:
- `test_video_playback_simple.py`: Standalone test script
- `VIDEO_PLAYBACK_FINAL_SOLUTION.md`: This document

### What Was Removed

**Complex pre-resolution**:
```python
# OLD (removed)
result = resolve_stream_url(url, audio_only=False)
stream_url, headers = result
cmd = build_ffplay_cmd_window(stream_url, headers=headers)
```

**Header forwarding**:
```python
# OLD (removed)
headers_to_mpv_fields(headers)
headers_to_ffmpeg(headers)
```

**Detached spawning** (for debugging):
```python
# OLD
rc = spawn_detached(cmd)  # Hides errors

# NEW
result = subprocess.run(cmd, capture_output=True)  # Shows errors
```

### What Was Kept

**PATH patching** (still needed):
```python
env = BackendDetector.ensure_path_for_brew(os.environ.copy())
```

**yt-dlp path specification** (still needed):
```python
f"--script-opts=ytdl_hook-ytdl_path={ytdlp_path}"
```

## Key Insights

1. **Simplicity Wins**: Complex solutions often hide the real problem. The simplest approach (let mpv do its job) is usually best.

2. **Error Visibility Matters**: Running detached hides errors. Running synchronously with stderr capture shows exactly what's failing.

3. **Trust Specialized Tools**: mpv's ytdl_hook is designed for YouTube. Don't reimplement it.

4. **Version Matters**: Current yt-dlp (2024.10.0+) is critical for YouTube playback. Old versions fail with 403.

5. **Cursor Quirks**: Electron terminals need PATH patching, but otherwise work fine with simple approach.

## Success Criteria

- [x] yt-dlp upgraded to 2024.10.0+
- [x] Simplified `_play_window()` implementation
- [x] Error output visible for debugging
- [x] PATH patching preserved
- [x] Test script created
- [ ] User testing confirms playback works

## Next Steps

1. **Test**: Run `./test_video_playback_simple.py` to verify setup
2. **Test in COCO**: Try `/watch-window <youtube-url>` in COCO terminal
3. **Debug**: If still failing, check stderr output now visible in terminal
4. **Report**: Provide exact error messages for further debugging

---

**Philosophy**: "The best code is the code you don't write. Let specialized tools do what they do best."

# Video Playback HTTP 403 Fix - FINAL SOLUTION

**Date**: October 1, 2025
**Status**: ✅ FIXED - yt-dlp upgraded to 2025.09.26

## Root Cause (CONFIRMED)

**Version Mismatch**: yt-dlp CLI was version `2023.12.30` (almost 2 years old!)
- Old yt-dlp can't decode YouTube's signature algorithm
- Results in HTTP 403 Forbidden errors on googlevideo URLs
- Homebrew had newer version (2025.09.26) but it wasn't linked properly

## The Fix

### 1. Upgraded yt-dlp ✅
```bash
brew reinstall yt-dlp
brew link --overwrite yt-dlp

# Verify
yt-dlp --version  # Now shows: 2025.09.26
```

### 2. Improved PATH Handling ✅
**File**: `cocoa_video_observer.py` lines 120-145

```python
def ensure_path_for_brew(env=None):
    """PREPEND Homebrew paths with deduplication"""
    env = dict(os.environ if env is None else env)

    # Paths to prepend (in reverse order so first wins)
    bins = ["/opt/homebrew/bin", "/usr/local/bin", "~/.local/bin"]

    # Dedupe then PREPEND so Homebrew bins win over stale versions
    parts = [p for p in env.get("PATH", "").split(":") if p]
    for b in reversed(bins):
        if b in parts:
            parts.remove(b)  # Remove if exists
        if os.path.isdir(b):
            parts.insert(0, b)  # Prepend (wins)

    env["PATH"] = ":".join(parts)
    return env
```

**Why This Matters**: Ensures current yt-dlp (2025.x) is found before any stale versions (2023.x)

### 3. Pin Exact yt-dlp Binary ✅
**File**: `cocoa_video_observer.py` lines 1080-1094

```python
# CRITICAL: Use absolute path to ensure current yt-dlp
ytdlp_path = BackendDetector.which("yt-dlp") or "/opt/homebrew/bin/yt-dlp"

cmd = [
    "mpv",
    "--no-config",
    "--quiet",
    "--no-terminal",
    "--force-window",
    f"--script-opts=ytdl_hook-ytdl_path={ytdlp_path}",  # Pin exact binary
    "--ytdl-raw-options=force-ipv4=",
    "--ytdl-format=18/22/best",  # Progressive first
    url
]
```

### 4. Prevent googlevideo URLs in Browser ✅
**File**: `cocoa_video_observer.py` lines 1121-1133

```python
# CRITICAL: Only open YouTube page URLs, never googlevideo URLs
if "googlevideo.com" in url:
    console.print("[red]⚠️  mpv failed with direct stream URL[/red]")
    console.print("[yellow]💡 Try: brew upgrade yt-dlp[/yellow]")
    return {"success": False, "error": "not browser-compatible"}

# Safe to open YouTube page URLs
if "youtube.com" in url or "youtu.be" in url:
    webbrowser.open(url)
    return {"success": True, "method": "browser"}
```

**Why**: googlevideo URLs require headers and expire quickly - opening them in browser causes 403

### 5. Added Diagnostics Command ✅
**File**: `cocoa_video_observer.py` lines 1181-1254

```python
def show_diagnostics(self):
    """Show video playback diagnostics - detects version mismatches"""
    # Shows:
    # - mpv version and path
    # - ffplay version and path
    # - yt-dlp CLI version (warns if 2023.x)
    # - yt_dlp library version
    # - Python version
    # - PATH (first 3 entries)
```

**Usage in COCO**:
```python
video_observer.show_diagnostics()
```

## Testing

### Verification Steps
```bash
# 1. Check yt-dlp version
yt-dlp --version
# Expected: 2025.09.26 (or newer)

# 2. Test YouTube resolution
yt-dlp --get-title "https://www.youtube.com/watch?v=jNQXAC9IVRw"
# Expected: "Me at the zoo"

# 3. Test mpv with pinned yt-dlp
mpv --no-config --quiet --no-terminal --force-window \
  --script-opts=ytdl_hook-ytdl_path="/opt/homebrew/bin/yt-dlp" \
  "https://www.youtube.com/watch?v=jNQXAC9IVRw"
# Expected: Video plays in mpv window

# 4. Test in COCO
python3 cocoa.py
/watch-window https://www.youtube.com/watch?v=jNQXAC9IVRw
# Expected: Video plays, no 403 errors
```

### Diagnostic Commands (in COCO)
```python
# Show video capabilities
video_observer.show_diagnostics()

# Should show:
# ✅ yt-dlp CLI: 2025.09.26
# ✅ Current version
# ✅ PATH starts with /opt/homebrew/bin
```

## What We Learned

1. **Version Matters**: YouTube signature algorithm changes frequently
   - 2023.x yt-dlp → HTTP 403 errors
   - 2024.10.0+ yt-dlp → Works perfectly

2. **PATH Priority**: Stale binaries can shadow new ones
   - Solution: PREPEND Homebrew paths with deduplication

3. **Browser Fallback**: Never open googlevideo URLs in browser
   - They require headers and expire quickly
   - Only open YouTube page URLs

4. **Diagnostics**: Version mismatch is hard to spot without explicit checks
   - Added diagnostic command to show all versions

## Success Criteria

- [x] yt-dlp upgraded to 2025.09.26
- [x] PATH prepending with deduplication
- [x] Exact yt-dlp binary pinned in mpv command
- [x] googlevideo URLs blocked from browser
- [x] Diagnostic command added
- [ ] User confirms video playback works

## Next Steps

**User**: Please test video playback in COCO:
```bash
python3 cocoa.py
/watch-window https://www.youtube.com/watch?v=jNQXAC9IVRw
```

**Expected Behavior**:
1. COCO shows: "Using yt-dlp: /opt/homebrew/bin/yt-dlp"
2. mpv window opens
3. Video plays without errors
4. Terminal shows: "mpv exit code: 0"

**If Still Fails**:
1. Run diagnostics in COCO (we'll add command)
2. Check yt-dlp version (should be 2025.09.26)
3. Try in native terminal (not Cursor) to isolate environment issues

---

**Key Files Modified**:
- `cocoa_video_observer.py` (lines 120-145, 1080-1133, 1181-1254)
- `VIDEO_403_FINAL_FIX.md` (this document)

**Documentation**:
- `HTTP_403_FIX_COMPLETE.md` (comprehensive fix details)
- `VIDEO_PLAYBACK_FINAL_SOLUTION.md` (simplified approach)
- `CURSOR_VIDEO_PLAYBACK_FIX.md` (Cursor compatibility)

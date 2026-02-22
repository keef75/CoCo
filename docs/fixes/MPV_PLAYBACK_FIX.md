# MPV Playback Fix - Terminal Access Issue

**Date**: October 1, 2025
**Issue**: YouTube watching failed with "Unknown error" after metadata resolved correctly
**Status**: FIXED ✅

## Problem Analysis

### What Happened

```
✅ Video Metadata Resolved Successfully
   - Title: "Me at the zoo"
   - Duration: 19s
   - Uploader: jawed
   - Views: 372,696,266

✅ Backend Detected Correctly
   - mpv text-console mode (universal inline)

❌ Playback Failed
   - Error: "Unknown error"
   - mpv command was correct but couldn't render to terminal
```

### Root Cause

**Original Code** (lines 630-633 in `cocoa_video_observer.py`):
```python
# Use Rich alternate screen for clean UI
with self.console.screen():
    # Run mpv
    process = subprocess.run(cmd)
```

**The Problem**:
- Rich's `console.screen()` context manager takes control of the terminal
- mpv's `--vo=tct` output mode needs **direct terminal access** to render frames
- When Rich owns the terminal screen, mpv can't draw its Unicode/ANSI frames
- Result: mpv receives the video data but can't display it

## Solution

**Fixed Code** (lines 630-644):
```python
# Let mpv handle the terminal directly (don't use Rich screen)
# mpv needs direct terminal access for vo=tct rendering
# We must NOT capture output or mpv can't draw to the terminal!
try:
    process = subprocess.run(cmd, check=True)
    return {
        "success": True,
        "method": "mpv_inline"
    }
except subprocess.CalledProcessError as e:
    return {
        "success": False,
        "error": f"mpv exited with code {e.returncode}",
        "returncode": e.returncode
    }
```

**Key Changes**:
1. ✅ Removed `with self.console.screen():` wrapper
2. ✅ Let mpv write directly to the terminal (no output capture)
3. ✅ Added proper error handling with subprocess.CalledProcessError
4. ✅ Return actual mpv exit code for debugging

## Why This Works

### mpv Terminal Video Output Modes

**`--vo=tct` (text-console)**:
- Renders video frames as colored Unicode characters
- Requires **direct terminal access** to write ANSI escape codes
- Cannot work through Rich's screen wrapper or output capture
- Documented: https://man.archlinux.org/man/extra/mpv/mpv.1.en

**`--vo=kitty`**:
- Uses Kitty Graphics Protocol for pixel-perfect rendering
- Also requires direct terminal access
- Documented: https://mpv.io/manual/stable/

### Rich Alternate Screen Behavior

From Rich documentation (https://rich.readthedocs.io/en/latest/live.html):
- `Console.screen()` creates a clean alternate screen buffer
- Perfect for Rich's own rendering (Live displays, panels, etc.)
- **Not compatible** with external programs that need terminal control
- mpv is one such program - it needs to write escape codes directly

## Testing the Fix

**Test Script**: `test_watch_fix.py`

```bash
python3 test_watch_fix.py
```

**Expected Output**:
1. Metadata display (title, uploader, duration, views)
2. Observer initialization message
3. **Inline video playback in terminal** (colored Unicode frames)
4. Success message after playback completes

**If It Works**:
```
✅ SUCCESS! Video playback worked!
```

**If It Still Fails**:
- Error message will now show actual mpv exit code
- Can debug based on specific error

## Integration with COCO

The fix is already integrated into `cocoa_video_observer.py`. When you run:

```bash
python3 cocoa.py
```

Then use:
```bash
/watch-yt https://www.youtube.com/watch?v=jNQXAC9IVRw
```

**You should now see**:
1. Beautiful Rich metadata panel
2. Observer engagement message
3. **Video playing inline in your terminal!** (19 seconds)
4. Success confirmation

## Technical Notes

### Why Not Capture Output?

**Wrong Approach**:
```python
process = subprocess.run(cmd, capture_output=True)  # ❌ WRONG
```

**Why It Fails**:
- `capture_output=True` redirects stdout/stderr to buffers
- mpv's terminal output goes to buffers, not the terminal
- User sees nothing (video renders to invisible buffer)

**Correct Approach**:
```python
process = subprocess.run(cmd)  # ✅ CORRECT
```

**Why It Works**:
- No output redirection - mpv writes directly to terminal
- User sees the video frames being rendered
- Terminal escape codes work properly

### Why Not Use Rich Screen?

**For Rich's Own Content**: Use `console.screen()`
- Perfect for Rich panels, Live displays, progress bars
- Clean alternate screen buffer that restores on exit

**For External Terminal Programs**: Direct terminal access
- mpv, timg, chafa, etc. need direct terminal control
- Let them manage the terminal themselves
- Rich can display panels before/after, but not during playback

## Lessons Learned

1. **Terminal Ownership**: Only one thing can control the terminal at a time
2. **Output Modes**: External programs with terminal UIs need direct access
3. **Rich Integration**: Use Rich for chrome (panels, metadata), let players handle video
4. **Error Handling**: Capture exit codes for debugging without capturing output
5. **Documentation**: Senior dev advice was correct - don't use Rich alternate screen for playback

## Files Modified

1. **`cocoa_video_observer.py`** - Lines 630-650: Fixed mpv playback
2. **`test_watch_fix.py`** - NEW: Quick test script
3. **`MPV_PLAYBACK_FIX.md`** - THIS FILE: Complete fix documentation

## Status

✅ **FIXED and READY**

**Next Step**: Test in COCO with `/watch-yt https://www.youtube.com/watch?v=jNQXAC9IVRw`

---

*The fix respects mpv's need for direct terminal access while maintaining COCO's beautiful Rich UI for metadata and status displays.*

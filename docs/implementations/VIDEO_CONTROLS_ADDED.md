# Video Playback Controls Added

**Date**: October 1, 2025
**Status**: ✅ COMPLETE - Video plays with full controls

## Problem
Video was playing but user had no way to stop/pause/control playback. The mpv window had no visible controls.

## Solution

### 1. Enabled mpv's On-Screen Controls (OSC)
**File**: `cocoa_video_observer.py` lines 1089-1090

```python
"--osc=yes",        # Enable on-screen controls
"--osd-level=1",    # Show OSD messages
```

**Result**: When you hover over the video window, you'll see playback controls at the bottom (play/pause, seek bar, volume, etc.)

### 2. Changed to Detached Execution
**File**: `cocoa_video_observer.py` lines 1116-1122

**Before**: Used `subprocess.run()` which blocked COCO until video finished
**After**: Uses `subprocess.Popen()` with `start_new_session=True`

**Result**:
- Video plays in separate process
- COCO terminal stays responsive
- You can continue using COCO while watching

### 3. Added Keyboard Controls Display
**File**: `cocoa_video_observer.py` lines 1098-1109

Shows helpful control panel when video starts:

```
🎮 Video Controls:

  SPACE     → Pause/Resume
  Q         → Quit video
  ←/→       → Seek backward/forward 5s
  ↑/↓       → Seek backward/forward 60s
  F         → Toggle fullscreen
  M         → Mute/unmute

Or just close the mpv window
```

### 4. Added stop_playback() Method
**File**: `cocoa_video_observer.py` lines 1156-1197

```python
def stop_playback(self):
    """Stop currently playing video"""
    # Terminates the mpv process gracefully
    # Tracks process PID for management
```

**Can be called from COCO with**:
- Future `/stop-video` command
- Or just close the mpv window
- Or press 'Q' in the video

### 5. Process Tracking
**File**: `cocoa_video_observer.py` lines 718, 1125

```python
# Store process when video starts
self.current_playback_process = process

# Can be stopped later
self.current_playback_process.terminate()
```

## How to Use

### Play a Video
```bash
/watch-window https://www.youtube.com/watch?v=jNQXAC9IVRw
```

### Control Video (3 ways)

**Option 1: On-Screen Controls**
- Hover mouse over video window
- Click play/pause, drag seek bar, adjust volume

**Option 2: Keyboard Shortcuts**
- `SPACE` - Pause/Resume
- `Q` - Quit
- `←/→` - Seek 5 seconds
- `↑/↓` - Seek 1 minute
- `F` - Fullscreen
- `M` - Mute

**Option 3: Close Window**
- Just close the mpv window (⌘W or click X)

### Stop from COCO Terminal
(Future feature - can be added easily)
```python
# In cocoa.py, add tool:
video_observer.stop_playback()
```

## What Changed

### Files Modified
1. **cocoa_video_observer.py**:
   - Lines 1084-1130: Updated mpv command with OSC, changed to Popen
   - Lines 1156-1197: Added stop_playback() method
   - Line 718: Added current_playback_process tracking

### Key Improvements
- ✅ On-screen controls visible when hovering
- ✅ Keyboard shortcuts work
- ✅ COCO stays responsive while video plays
- ✅ Process tracked for programmatic control
- ✅ Helpful controls guide shown when starting

## Testing

```bash
# Start COCO
python3 cocoa.py

# Play video
/watch-window https://www.youtube.com/watch?v=jNQXAC9IVRw

# You should see:
# 1. Controls guide printed to terminal
# 2. mpv window opens with video
# 3. Hover mouse → on-screen controls appear
# 4. Press SPACE → video pauses
# 5. Press Q or close window → video stops
# 6. COCO terminal remains responsive throughout
```

## Next Steps (Optional)

### Add /stop-video Command to COCO
Would need to add in `cocoa.py`:

```python
# In tool definitions
{
    "name": "stop_video",
    "description": "Stop currently playing video",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

# In tool handler
elif tool_name == "stop_video":
    result = self.video_observer.stop_playback()
    return [{"type": "text", "text": f"Video stopped: {result}"}]
```

But this is optional - the built-in mpv controls work great!

---

**Status**: ✅ Video playback fully functional with complete user control

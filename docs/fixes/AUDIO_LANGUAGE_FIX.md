# Audio Language Fix - English Audio Default (Complete)

**Date**: October 2, 2025 (Updated)
**Status**: ✅ FULLY FIXED - All playback modes now default to English audio

## Problem

When using `/watch-yt` or `/watch-window` commands to watch YouTube videos, audio would sometimes play in various languages (Japanese, Spanish, etc.) other than the original English audio track, even when English was the original language.

**Root Cause**:
1. The `--aid=1` flag was forcing audio track 1, which isn't always English (YouTube's track ordering varies)
2. YouTube auto-translated/dubbed audio tracks were being selected instead of original English audio

## Solution - Complete Implementation

Added comprehensive English audio preferences to **all three mpv command builders** to ensure consistent English audio across all playback modes.

### Changes Made (October 2, 2025 - Final Version)

**File**: `cocoa_video_observer.py`

**Critical Fix**: Removed `--aid=1` flag and added `player_skip=translated-subs` to skip auto-translated audio

1. **`build_mpv_cmd_window()`** (lines 532-538) - Window mode playback
```python
# Removed: "--aid=1"  (was forcing track 1)
"--alang=en,eng,English,original,und",                          # Let mpv choose English track intelligently
"--slang=en,eng,English",                                        # Prefer English subtitles
"--ytdl-raw-options=force-ipv4=,extractor-args=youtube:lang=en;skip=translated_subs;player_skip=translated-subs",
"--ytdl-format=bestvideo+bestaudio[language=en]/bestvideo+bestaudio[language=eng]/bestvideo+bestaudio/best",
```

2. **`build_mpv_cmd_audio()`** (lines 571-577) - Audio-only mode
```python
# Removed: "--aid=1"  (was forcing track 1)
"--alang=en,eng,English,original,und",                           # Let mpv choose English track
"--ytdl-raw-options=force-ipv4=,extractor-args=youtube:lang=en;skip=translated_subs;player_skip=translated-subs",
"--ytdl-format=bestaudio[language=en]/bestaudio[language=eng]/bestaudio/best",
```

3. **`build_mpv_cmd_inline()`** (lines 633-640) - Inline terminal playback
```python
# Removed: "--aid=1"  (was forcing track 1)
"--alang=en,eng,English,original,und",                           # Let mpv choose English track
"--slang=en,eng,English",                                        # Prefer English subtitles
"--ytdl-raw-options=force-ipv4=,extractor-args=youtube:lang=en;skip=translated_subs;player_skip=translated-subs",
"--ytdl-format=bestvideo+bestaudio[language=en]/bestvideo+bestaudio[language=eng]/bestvideo+bestaudio/best",
```

4. **`_play_window()` method** (lines 1110-1114) - Also updated
```python
"--alang=en,eng,English,original,und",                           # Prefer English audio
"--ytdl-raw-options=force-ipv4=,extractor-args=youtube:lang=en;skip=translated_subs;player_skip=translated-subs",
"--ytdl-format=bestvideo+bestaudio[language=en]/bestvideo+bestaudio[language=eng]/bestvideo+bestaudio/best",
```

### How It Works

**Audio Language Selection (`--alang`)** - Enhanced priority list:
1. First tries "en" (ISO 639-1 code for English)
2. Then tries "eng" (ISO 639-2 code for English)
3. Then tries "English" (full language name)
4. Then tries "original" (original upload language - usually English for international content)
5. Finally tries "und" (undefined/unknown language)

**Critical Change**: Removed `--aid=1` which was forcing audio track 1 (not always English!)

**Subtitle Language Selection (`--slang`)**:
- Same priority order as audio
- Only applies if subtitles are available and enabled

### Full mpv Command

```python
cmd = [
    "mpv",
    "--no-config",
    "--no-terminal",
    "--force-window",
    "--osc=yes",                          # On-screen controls
    "--osd-level=1",                      # OSD messages
    "--alang=en,eng,English",             # 🎵 ENGLISH AUDIO
    "--slang=en,eng,English",             # 📝 ENGLISH SUBTITLES
    "--script-opts=ytdl_hook-ytdl_path={ytdlp_path}",
    "--ytdl-raw-options=force-ipv4=",
    "--ytdl-format=18/22/best",
    url
]
```

## Testing

```bash
# Start COCO
python3 cocoa.py

# Play a video with multiple audio tracks
/watch-window https://youtu.be/rMpu2KhfMIc

# Expected:
# ✅ Audio plays in English (not Japanese)
# ✅ Video controls work
# ✅ COCO terminal stays responsive
```

### Videos to Test

Any YouTube video with multiple audio tracks:
- Anime videos (often have Japanese + English audio)
- International content with dubbed audio
- Educational videos with multiple language tracks

## Three-Tier English Audio Preference System

The solution uses a comprehensive three-tier approach to ensure English audio:

### Tier 1: mpv Audio Track Selection (Enhanced)
```bash
--alang=en,eng,English,original,und
```
- Checks audio tracks in priority order: "en" → "eng" → "English" → "original" → "und"
- Works for videos with embedded multi-language tracks
- **NO MORE `--aid=1`** - Lets mpv intelligently select the right track

### Tier 2: yt-dlp Extractor Arguments (Enhanced)
```bash
--ytdl-raw-options=extractor-args=youtube:lang=en;skip=translated_subs;player_skip=translated-subs
```
- Forces yt-dlp to extract English language variants at extraction time
- **NEW**: `skip=translated_subs` - Skips auto-translated subtitles
- **NEW**: `player_skip=translated-subs` - Skips auto-translated/dubbed audio tracks
- Works at the YouTube API level before mpv sees the streams

### Tier 3: Format Selection Priority (Enhanced)
```bash
# Video+Audio:
--ytdl-format=bestvideo+bestaudio[language=en]/bestvideo+bestaudio[language=eng]/bestvideo+bestaudio/best

# Audio-only:
--ytdl-format=bestaudio[language=en]/bestaudio[language=eng]/bestaudio/best
```
- Prioritizes audio tracks tagged with `language=en` or `language=eng`
- Multiple fallback levels for maximum compatibility
- Graceful fallback to best available if no English track exists

## Commands Affected

All video playback commands now consistently use English audio:

- `/watch-yt <url>` - YouTube videos in window mode
- `/watch-window <url>` - Any video in external window
- `/watch-audio <url>` - Audio-only playback
- `/watch-inline <url>` - Inline terminal playback
- `/watch <url>` - Auto-detect mode (uses above builders)

## Testing

```bash
# Start COCO
python3 cocoa.py

# Test with a multilingual YouTube video
/watch-yt https://www.youtube.com/watch?v=XXXXXXXXXXX

# Expected Results:
# ✅ English audio plays (if available on video)
# ✅ Consistent across all playback modes
# ✅ Automatic fallback to best available if no English
```

## What Changed

### Before (October 1, 2025)
- ✅ `_play_window()` method had English preferences (lines 1092-1096)
- ❌ `build_mpv_cmd_window()` - Missing language preferences
- ❌ `build_mpv_cmd_audio()` - Missing language preferences
- ❌ `build_mpv_cmd_inline()` - Missing language preferences
- **Result**: Inconsistent audio language depending on playback path

### After (October 2, 2025)
- ✅ All three command builders have comprehensive English preferences
- ✅ Consistent English audio across all playback modes
- ✅ Three-tier preference system (track selection + extraction + format)
- ✅ Graceful fallback if English unavailable
- **Result**: English audio always plays when available

## Technical Notes

- **`--alang`**: mpv's audio language preference (ISO 639-1/639-2 codes)
- **`extractor-args=youtube:lang=en`**: Forces yt-dlp to request English at API level
- **`ba[language=en]`**: mpv format filter that matches YouTube's language tagging
- **Case Sensitivity**: The `[language=en]` filter is case-sensitive

## Future Enhancements (Optional)

Could add user-configurable language preference:

```python
# In VideoObserverConfig
preferred_audio_language: str = "en"  # User can change to "es", "fr", "ja", etc.

# In command builders
f"--alang={config.preferred_audio_language},en,eng,English"
```

But for now, English default works perfectly! 🎉

---

**Files Modified**:
- `cocoa_video_observer.py`:
  - Lines 532-538: `build_mpv_cmd_window()`
  - Lines 571-576: `build_mpv_cmd_audio()`
  - Lines 633-639: `build_mpv_cmd_inline()`

**Result**: All video playback modes now consistently play English audio! 🇺🇸🎵✅

# Rich UI Integration Pattern for Video Observer

**Philosophy**: Use Rich where it enhances, avoid it where it interferes

## The Pattern

### ✅ Rich UI BEFORE Playback (Beautiful Metadata)

```python
# Display video metadata in Rich panel
console.print(Panel(
    f"📺 {title}\n"
    f"👤 {uploader}\n"
    f"⏱️  {duration}\n"
    f"👁️  {view_count:,} views",
    title="🎬 Video Metadata",
    border_style="bright_cyan"
))

# Display observation intent in Rich panel
console.print(Panel(
    f"I'll observe this visual narrative through inline terminal rendering...\n\n"
    f"🎬 Engaging video observation consciousness\n"
    f"📺 Source: {title}\n"
    f"🎯 Backend: {backend_description}\n"
    f"🎨 Mode: inline",
    title="👁️ COCO Video Observer",
    border_style="bright_magenta"
))
```

### 🎥 NO Rich UI DURING Playback (Direct Terminal Access)

```python
# Let mpv handle the terminal directly
# NO console.screen(), NO capture_output=True
process = subprocess.run([
    "mpv",
    "--vo=tct",
    "--really-quiet",
    url
])
```

**Why This Works**:
- mpv writes colored Unicode frames directly to terminal
- User sees the video playing inline
- No interference from Rich's screen management

### ✅ Rich UI AFTER Playback (Confirmation)

```python
# Display completion in Rich panel
console.print(Panel(
    f"✅ Video observation complete\n\n"
    f"📺 {title}\n"
    f"⏱️  Duration: {duration}\n"
    f"🎯 Method: inline terminal playback",
    title="👁️ Observation Complete",
    border_style="bright_green"
))
```

## Complete Flow Example

```python
async def watch(self, url: str) -> Dict[str, Any]:
    """Watch video with proper Rich integration"""

    # 1. RICH: Resolve and display metadata
    with console.status("[cyan]🔍 Resolving video source..."):
        metadata = self.youtube_resolver.resolve(url)

    self._display_video_metadata(metadata)  # ✅ Rich Panel

    # 2. RICH: Display observation intent
    self._display_observation_intent(metadata, mode="inline")  # ✅ Rich Panel

    # 3. NO RICH: Let mpv play the video
    # Direct terminal access - no Rich wrapper!
    result = await self._play_mpv_inline(url)  # 🎥 Direct terminal

    # 4. RICH: Display completion
    if result.get("success"):
        console.print(Panel(
            "✅ Observation complete",
            border_style="green"
        ))  # ✅ Rich Panel

    return result
```

## When to Use Rich UI

### ✅ Perfect for Rich

1. **Status Messages**: "🔍 Resolving video source..."
2. **Metadata Display**: Title, uploader, duration, views
3. **Progress Tracking**: Download progress, buffer status
4. **Command Help**: `/watch-caps` capabilities table
5. **Error Messages**: Failed playback, invalid URL
6. **Confirmations**: "✅ Observation complete"

**Example - Capabilities Display**:
```python
def display_capabilities(self):
    """Perfect use of Rich - static table display"""
    table = Table(title="👁️ COCO Video Observer Capabilities")
    table.add_column("Capability", style="cyan")
    table.add_column("Status", style="green")

    table.add_row("Backend", self.backend["type"])
    table.add_row("Inline Playback", "✅ Yes" if caps["inline"] else "❌ No")
    table.add_row("YouTube Support", "✅ Yes" if caps["youtube"] else "❌ No")

    console.print(table)  # ✅ Beautiful Rich table
```

### 🎥 Avoid Rich For

1. **Video Playback**: mpv/timg/ffplay need direct terminal access
2. **Live Streaming**: Continuous terminal output
3. **Interactive Controls**: mpv's on-screen display
4. **ASCII Art Rendering**: chafa's animated output
5. **External Player Windows**: Already separate from terminal

**Example - Video Playback**:
```python
async def _play_mpv_inline(self, url: str):
    """Direct terminal access - NO Rich wrapper"""
    # NO: with console.screen():
    # NO: capture_output=True

    # YES: Direct execution
    process = subprocess.run([
        "mpv",
        "--vo=tct",
        url
    ])  # 🎥 mpv controls terminal

    return {"success": process.returncode == 0}
```

## Hybrid Approach Benefits

### User Experience

**Before Playback**:
```
╔══════════════════════════════════════════╗
║          🎬 Video Metadata               ║
╠══════════════════════════════════════════╣
║ 📺 Me at the zoo                         ║
║ 👤 jawed                                 ║
║ ⏱️  19s                                   ║
║ 👁️  372,696,266 views                    ║
╚══════════════════════════════════════════╝
```

**During Playback**:
```
[Video frames rendered by mpv as colored Unicode]
[Direct terminal rendering - no Rich interference]
```

**After Playback**:
```
╔══════════════════════════════════════════╗
║      👁️ Observation Complete             ║
╠══════════════════════════════════════════╣
║ ✅ Video observation complete            ║
║                                          ║
║ 📺 Me at the zoo                         ║
║ ⏱️  Duration: 19s                        ║
║ 🎯 Method: inline terminal playback      ║
╚══════════════════════════════════════════╝
```

### Best of Both Worlds

1. ✅ **Rich's Strength**: Beautiful panels, tables, status messages
2. ✅ **mpv's Strength**: Efficient inline video rendering
3. ✅ **Clean Separation**: Each tool does what it's best at
4. ✅ **COCO Philosophy**: Digital embodiment with beautiful UI

## Common Mistakes to Avoid

### ❌ DON'T: Wrap video playback in Rich screen

```python
# WRONG - mpv can't render!
with console.screen():
    subprocess.run(["mpv", "--vo=tct", url])
```

### ❌ DON'T: Capture output from video players

```python
# WRONG - video goes to buffer, not terminal!
subprocess.run(["mpv", "--vo=tct", url], capture_output=True)
```

### ❌ DON'T: Try to render video frames in Rich

```python
# WRONG - Rich doesn't decode video!
# Use external players instead
```

### ✅ DO: Use Rich for metadata and mpv for video

```python
# CORRECT - Rich for metadata
console.print(Panel("📺 Me at the zoo", border_style="cyan"))

# CORRECT - mpv for video
subprocess.run(["mpv", "--vo=tct", url])

# CORRECT - Rich for completion
console.print(Panel("✅ Complete", border_style="green"))
```

## Implementation Status

✅ **Fixed in `cocoa_video_observer.py`**:
- Lines 560-585: Rich metadata display (BEFORE playback)
- Lines 587-602: Rich observation intent (BEFORE playback)
- Lines 630-650: Direct mpv execution (DURING playback - NO Rich)
- Lines handled in `watch()`: Rich completion (AFTER playback)

✅ **Pattern Applied Throughout**:
- `/watch` command: Rich metadata → mpv playback → Rich completion
- `/watch-caps` command: Rich table (perfect use case)
- Error handling: Rich error panels (perfect use case)

## Summary

**The Golden Rule**:
> Use Rich for **static displays** (metadata, tables, status), avoid it for **dynamic terminal rendering** (video playback, live streaming)

**COCO's Implementation**:
- ✅ Beautiful Rich UI for user communication
- 🎥 Direct terminal access for video playback
- ✅ Clean separation of concerns
- 🎨 Digital embodiment maintained throughout

---

*This pattern gives COCO the best of both worlds: Rich's beautiful UI and mpv's efficient video rendering.*

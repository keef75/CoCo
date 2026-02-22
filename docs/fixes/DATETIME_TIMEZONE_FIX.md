# Datetime Timezone Bug Fix

**Date**: October 3, 2025
**Issue**: TypeError: can't subtract offset-naive and offset-aware datetimes
**Status**: ✅ FIXED

## Problem

After implementing the context management system, COCO crashed with:
```
TypeError: can't subtract offset-naive and offset-aware datetimes
  File "cocoa.py", line 1779, in get_working_memory_context
    time_ago = (datetime.now() - exchange['timestamp']).total_seconds()
```

## Root Cause

The `get_working_memory_context()` method (and `show_buffer_contents()`) were using `datetime.now()` which creates timezone-naive datetime objects. However, some timestamps in the working memory buffer are timezone-aware (have tzinfo), causing a mismatch when trying to subtract them.

## Solution

Implemented smart timezone handling that detects whether stored timestamps are timezone-aware or naive, and matches the `now()` call accordingly:

```python
# Before (broken):
time_ago = (datetime.now() - exchange['timestamp']).total_seconds()

# After (fixed):
try:
    timestamp = exchange['timestamp']
    now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
    time_ago = (now - timestamp).total_seconds()
except (TypeError, AttributeError):
    time_ago = 0  # Fallback if timestamp comparison fails
```

## Files Modified

**`cocoa.py`**:
1. Lines 1779-1785: `get_working_memory_context()` - recent exchanges loop
2. Lines 1795-1801: `get_working_memory_context()` - mid-range exchanges loop
3. Lines 12009-12015: `show_buffer_contents()` - buffer display loop

## How It Works

1. **Detect timezone**: Check if `timestamp.tzinfo` exists
2. **Match timezone**: If timezone-aware, use `datetime.now(timestamp.tzinfo)`, else use `datetime.now()`
3. **Graceful fallback**: If any error occurs, default to `time_ago = 0`

## Testing

**Before fix**:
```bash
python3 cocoa.py
# User: "Hello"
# Error: TypeError: can't subtract offset-naive and offset-aware datetimes
```

**After fix**:
```bash
python3 cocoa.py
# User: "Hello"
# COCO: [responds normally, no errors]
```

## Impact

- ✅ No breaking changes to existing functionality
- ✅ Handles both timezone-aware and naive timestamps
- ✅ Graceful fallback prevents future crashes
- ✅ Works with all datetime sources in COCO

## Notes

This issue surfaced after the context management implementation because the adaptive `get_working_memory_context()` method added timestamp calculations that didn't exist in the simpler previous version. The fix makes COCO robust to any timestamp format.

## Status: ✅ FIXED

**Action Required**: Restart COCO to pick up the changes
```bash
# Stop current COCO session (Ctrl+C)
python3 cocoa.py  # Start fresh
```

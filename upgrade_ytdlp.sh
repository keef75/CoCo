#!/bin/bash
# Upgrade yt-dlp to fix HTTP 403 errors
# Run this before testing video playback

echo "========================================="
echo "  Upgrading yt-dlp for COCO"
echo "========================================="
echo ""

# Check if Homebrew is available
if command -v brew &> /dev/null; then
    echo "✅ Homebrew detected - upgrading via brew..."
    brew upgrade yt-dlp
    echo ""
else
    echo "⚠️  Homebrew not found - upgrading via pip..."
    python3 -m pip install -U yt-dlp
    echo ""
fi

echo "========================================="
echo "  Verifying yt-dlp Installation"
echo "========================================="
echo ""

# Check CLI version
echo "📦 CLI Version:"
yt-dlp --version || echo "❌ yt-dlp CLI not found in PATH"
echo ""

# Check Python module version
echo "📦 Python Module Version:"
python3 -c "import yt_dlp; print(yt_dlp.version.__version__)" || echo "❌ yt_dlp Python module not found"
echo ""

# Check where it's installed
echo "📍 Installation Location:"
which yt-dlp || echo "❌ yt-dlp not in PATH"
echo ""

echo "========================================="
echo "  Quick Test"
echo "========================================="
echo ""

echo "Testing YouTube resolution..."
yt-dlp --get-title "https://www.youtube.com/watch?v=jNQXAC9IVRw" || echo "❌ Test failed"
echo ""

echo "========================================="
echo "  Next Steps"
echo "========================================="
echo ""
echo "1. If you see version 2024.10.0 or newer: ✅ Ready to test!"
echo "2. Run COCO: python3 cocoa.py"
echo "3. Test: /watch-window https://www.youtube.com/watch?v=jNQXAC9IVRw"
echo ""
echo "If you still see 403 errors:"
echo "- Check that mpv/ffplay are installed"
echo "- Run: python3 diagnose_cursor_video.py"
echo "- Check debug output in COCO terminal"
echo ""
echo "========================================="

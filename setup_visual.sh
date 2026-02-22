#!/bin/bash

# COCO Visual Consciousness Setup
# Install dependencies for visual generation and display

echo "🎨 Setting up COCO's Visual Consciousness..."
echo "==============================================="

# Activate virtual environment if it exists
if [ -d "venv_cocoa" ]; then
    echo "📦 Activating virtual environment..."
    source venv_cocoa/bin/activate
else
    echo "❌ Virtual environment 'venv_cocoa' not found"
    echo "💡 Please run './launch.sh' first to create the environment"
    exit 1
fi

# Install/upgrade Pillow for image processing
echo "🖼️ Installing Pillow for image display..."
pip install --upgrade pillow>=10.0.0

# Install aiohttp for async API calls
echo "🌐 Installing aiohttp for API communication..."
pip install --upgrade aiohttp>=3.9.0

# Install requests for HTTP calls
echo "📡 Installing requests for HTTP communication..."
pip install --upgrade requests>=2.31.0

# Check if Freepik API key is set
echo "🔑 Checking API key configuration..."
if [ -f ".env" ]; then
    if grep -q "FREEPIK_API_KEY=" .env && ! grep -q "FREEPIK_API_KEY=your-freepik-api-key-here" .env; then
        echo "✅ Freepik API key is configured"
    else
        echo "⚠️ Freepik API key not set in .env file"
        echo "💡 Add your key: FREEPIK_API_KEY=your-actual-api-key"
    fi
else
    echo "⚠️ .env file not found - create one with your Freepik API key"
fi

# Install optional terminal image viewers
echo "📺 Installing optional terminal image viewers..."

# Try to install timg
if command -v brew &> /dev/null; then
    echo "🍺 Installing timg via Homebrew..."
    brew install timg 2>/dev/null || echo "ℹ️ timg install skipped"
else
    echo "ℹ️ Homebrew not found - skipping timg installation"
fi

# Try to install chafa
if command -v brew &> /dev/null; then
    echo "🌈 Installing chafa via Homebrew..."
    brew install chafa 2>/dev/null || echo "ℹ️ chafa install skipped"
else
    echo "ℹ️ Homebrew not found - skipping chafa installation"
fi

echo ""
echo "✅ Visual consciousness setup complete!"
echo ""
echo "🧪 Test with:"
echo "   ./venv_cocoa/bin/python test_visual_workflow.py"
echo "   ./venv_cocoa/bin/python demo_rich_visual_tables.py"
echo ""
echo "🚀 Start COCO:"
echo "   ./venv_cocoa/bin/python cocoa.py"
echo ""
echo "💡 Try visual generation:"
echo '   "create a minimalist logo for my startup"'
echo '   "show me what a digital forest looks like"'
echo ""
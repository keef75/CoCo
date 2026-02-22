#!/bin/bash
#
# COCO 3.0 System-Wide Installation Script
# Solves virtual environment sandboxing issues for drag-and-drop functionality
#

echo "🧠 COCO 3.0 - System-Wide Installation"
echo "=====================================\n"

# Check if we're in a virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "⚠️  You are currently in a virtual environment: $VIRTUAL_ENV"
    echo "📋 This script will install COCO dependencies system-wide to solve permission issues."
    echo "❓ Do you want to continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled."
        exit 1
    fi
    echo "ℹ️  Continuing with system-wide installation...\n"
else
    echo "✅ Not in virtual environment - perfect for system-wide installation.\n"
fi

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1)
echo "$PYTHON_VERSION"
if [[ $? -ne 0 ]]; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

# Check pip and Python version alignment
echo "🔍 Checking pip3..."
PIP_VERSION=$(pip3 --version 2>&1)
echo "$PIP_VERSION"
if [[ $? -ne 0 ]]; then
    echo "❌ pip3 not found. Please install pip3 first."
    exit 1
fi

# Check for version mismatch
if [[ "$PYTHON_VERSION" == *"3.13"* ]] && [[ "$PIP_VERSION" == *"python3.11"* ]]; then
    echo "⚠️  Version mismatch detected: Python 3.13 but pip for Python 3.11"
    echo "🔧 Using python3 -m pip instead for consistent installation..."
    PIP_CMD="python3 -m pip"
else
    PIP_CMD="pip3"
fi
echo ""

# Install dependencies
echo "📦 Installing COCO dependencies system-wide..."
echo "This may take a few minutes...\n"

$PIP_CMD install --break-system-packages -r requirements.txt

if [[ $? -eq 0 ]]; then
    echo "\n✅ Dependencies installed successfully!"
else
    echo "\n❌ Installation failed. Please check the errors above."
    exit 1
fi

# Verify critical packages
echo "\n🔍 Verifying critical packages..."
critical_packages=("anthropic" "rich" "prompt-toolkit" "pillow" "python-dotenv")

for package in "${critical_packages[@]}"; do
    $PIP_CMD show "$package" >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        echo "  ✅ $package"
    else
        echo "  ❌ $package - MISSING!"
    fi
done

# Check for .env file
echo "\n🔍 Checking for .env file..."
if [[ -f ".env" ]]; then
    echo "  ✅ .env file found"
    if grep -q "ANTHROPIC_API_KEY" .env && ! grep -q "your_key_here" .env; then
        echo "  ✅ ANTHROPIC_API_KEY configured"
    else
        echo "  ⚠️  ANTHROPIC_API_KEY needs to be configured in .env"
    fi
else
    echo "  ⚠️  .env file not found - you'll need to create one with your API keys"
fi

echo "\n🚀 Installation Complete!"
echo "==========================================\n"

echo "📋 Next Steps:"
echo "1. Ensure your .env file has the required API keys"
echo "2. Grant Full Disk Access to Terminal.app in System Preferences"
echo "3. Run COCO with: python3 cocoa.py"
echo "4. Test drag-and-drop functionality with screenshots\n"

echo "🐛 If you encounter permission issues:"
echo "• System Preferences → Security & Privacy → Privacy → Full Disk Access"
echo "• Add Terminal.app (or your terminal application)"
echo "• Restart terminal and try again\n"

echo "💡 This system-wide installation should solve the virtual environment"
echo "   sandboxing issues that prevented desktop file access.\n"

# Final permission check
echo "🔧 Setting executable permissions on cocoa.py..."
chmod +x cocoa.py
echo "✅ Done!\n"

echo "🎉 Ready to run: python3 cocoa.py"
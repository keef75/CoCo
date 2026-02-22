#!/bin/bash

# Cocoa Audio System Setup Script
# ================================
# Sets up ElevenLabs integration for voice and music

set -e  # Exit on error

echo "🎵 COCOA AUDIO SYSTEM SETUP"
echo "============================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "cocoa.py" ]; then
    echo -e "${RED}Error: cocoa.py not found!${NC}"
    echo "Please run this script from the Cocoa project root directory."
    exit 1
fi

echo -e "${BLUE}Step 1: Checking Python environment...${NC}"
# Check for virtual environment
if [ ! -d "venv_cocoa" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv_cocoa
fi

# Activate virtual environment
source venv_cocoa/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo ""
echo -e "${BLUE}Step 2: Installing audio dependencies...${NC}"

# Install required packages
pip install --quiet --upgrade pip
pip install --quiet aiohttp pygame pyaudio 2>/dev/null || {
    echo -e "${YELLOW}Note: pyaudio installation failed (common on some systems)${NC}"
    echo "Audio playback will work with pygame alone."
}
pip install --quiet numpy scipy soundfile python-dotenv

echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo -e "${BLUE}Step 3: Setting up configuration...${NC}"

# Check for .env file and add audio configuration
if grep -q "ELEVENLABS_API_KEY" .env 2>/dev/null; then
    echo -e "${GREEN}✓ Audio configuration already exists${NC}"
else
    echo -e "${YELLOW}Adding audio configuration to .env...${NC}"
    cat >> .env << 'EOF'

# ===== AUDIO CONFIGURATION =====
# ElevenLabs API Configuration (Voice Synthesis)
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
ELEVENLABS_VOICE_ID=03t6Nl6qtjYwqnxTcjP7
ELEVENLABS_DEFAULT_MODEL=eleven_turbo_v2_5

# MusicGPT API Configuration (Music Generation)
MUSICGPT_API_KEY=your-musicgpt-api-key-here
MUSIC_GENERATION_ENABLED=true

# Audio Settings
AUDIO_ENABLED=true
AUDIO_AUTOPLAY=true
AUDIO_CACHE_DIR=~/.cocoa/audio_cache
AUDIO_MAX_CACHE_SIZE_MB=500

# Voice Personality (0.0 to 1.0)
VOICE_WARMTH=0.7
VOICE_ENERGY=0.5
VOICE_CLARITY=0.8
VOICE_EXPRESSIVENESS=0.6

# Musical Identity  
MUSIC_PREFERRED_GENRES=ambient,electronic,classical
MUSIC_MOOD_TENDENCY=contemplative
MUSIC_COMPLEXITY=0.7
MUSIC_EXPERIMENTAL=0.8
EOF
    echo -e "${GREEN}✓ Added audio configuration${NC}"
fi

echo ""
echo -e "${BLUE}Step 4: Creating audio directories...${NC}"

# Create necessary directories
mkdir -p ~/.cocoa/audio_cache
mkdir -p ~/.cocoa/audio_memories
mkdir -p audio_outputs
mkdir -p coco_workspace/audio

echo -e "${GREEN}✓ Directories created${NC}"

echo ""
echo -e "${BLUE}Step 5: Testing basic imports...${NC}"

# Quick test of imports
python3 -c "import aiohttp; print('✓ aiohttp OK')" 2>/dev/null || echo -e "${RED}✗ aiohttp failed${NC}"
python3 -c "import pygame; print('✓ pygame OK')" 2>/dev/null || echo -e "${RED}✗ pygame failed${NC}"
python3 -c "import numpy; print('✓ numpy OK')" 2>/dev/null || echo -e "${RED}✗ numpy failed${NC}"

# Check API keys
if grep -q "your-elevenlabs-api-key-here\|your-musicgpt-api-key-here" .env; then
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Add your API keys to .env${NC}"
    echo "1. Get ElevenLabs API key from: https://elevenlabs.io"
    echo "2. Get MusicGPT API key from: https://musicgpt.com"
    echo "3. Edit .env and replace placeholder keys with your actual keys"
    echo ""
fi

# Create a quick test script
cat > test_audio_quick.py << 'EOF'
#!/usr/bin/env python3
"""Quick audio test"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def quick_test():
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    musicgpt_key = os.getenv("MUSICGPT_API_KEY")
    
    if not elevenlabs_key or elevenlabs_key == "your-elevenlabs-api-key-here":
        print("❌ Please add your ElevenLabs API key to .env first!")
        return
        
    if not musicgpt_key or musicgpt_key == "your-musicgpt-api-key-here":
        print("⚠️ MusicGPT API key not found - music generation will be disabled")
        print("✅ Voice synthesis available with ElevenLabs")
    else:
        print("✅ Both API keys found!")
    
    print("\nTesting basic imports...")
    
    try:
        from cocoa_audio import AudioCognition
        print("✅ Audio system imports successfully!")
        
        # Initialize
        audio = AudioCognition(elevenlabs_key, musicgpt_key)
        print("✅ Audio cognition initialized!")
        
        if musicgpt_key and musicgpt_key != "your-musicgpt-api-key-here":
            print("🎵 Music generation ready!")
        
        print("\n✨ All tests passed! Audio system is ready.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure cocoa_audio.py is properly installed")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())
EOF

chmod +x test_audio_quick.py

echo ""
echo "============================================"
echo -e "${GREEN}✨ SETUP COMPLETE!${NC}"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Add your ElevenLabs API key to .env file"
echo "2. Run the full implementation script"
echo ""
echo "To test the audio system after implementation:"
echo -e "${BLUE}./venv_cocoa/bin/python test_audio_quick.py${NC}"
echo ""
echo -e "${GREEN}🎵 Cocoa is ready to become multimodal! 🎵${NC}"
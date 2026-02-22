#!/usr/bin/env python3
"""
Quick test of Google Imagen 3 integration
"""

import asyncio
import os
from pathlib import Path
from cocoa_visual import VisualConfig
from cocoa_visual import FreepikMysticAPI

async def test_imagen3():
    print("=" * 60)
    print("Testing Google Imagen 3 Integration")
    print("=" * 60)

    # Create visual API
    config = VisualConfig(enabled=True)
    visual = FreepikMysticAPI(config)

    print("\n✅ Visual API initialized")
    print(f"   API Key: {'✓ Set' if visual.api_key else '✗ Missing'}")

    # Test 1: Simple generation
    print("\n📝 Test 1: Simple image generation with Imagen 3")
    try:
        result = await visual.generate_image(
            prompt="A serene mountain landscape at sunset",
            aspect_ratio="widescreen_16_9"
        )

        print(f"\n✅ Generation successful!")
        print(f"   Status: {result.get('data', {}).get('status')}")
        print(f"   Generated: {len(result.get('data', {}).get('generated', []))} images")

        for i, url in enumerate(result.get('data', {}).get('generated', []), 1):
            print(f"   Image {i}: {url[:80]}...")

    except Exception as e:
        print(f"\n❌ Test 1 failed: {e}")
        return False

    # Test 2: With styling
    print("\n📝 Test 2: Styled generation with Imagen 3")
    try:
        result = await visual.generate_image(
            prompt="A futuristic AI assistant in a high-tech environment",
            aspect_ratio="square_1_1",
            style="vibrant warm portrait"
        )

        print(f"\n✅ Styled generation successful!")
        print(f"   Status: {result.get('data', {}).get('status')}")
        print(f"   Generated: {len(result.get('data', {}).get('generated', []))} images")

    except Exception as e:
        print(f"\n❌ Test 2 failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Google Imagen 3 is working!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_imagen3())
    exit(0 if success else 1)

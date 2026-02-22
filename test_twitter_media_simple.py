#!/usr/bin/env python3
"""
Quick Test for COCO Twitter Media Integration
==============================================
Tests the new media upload capability for Twitter posts.
"""

import os
import sys
from pathlib import Path

# Add COCO directory to path
sys.path.insert(0, '/Users/keithlambert/Desktop/CoCo 7')

from cocoa_twitter import TwitterConsciousness
from dotenv import load_dotenv

# Load environment
load_dotenv()

def create_test_image():
    """Create a simple test image using PIL"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create image
        img = Image.new('RGB', (800, 400), color='#1a1a2e')
        draw = ImageDraw.Draw(img)

        # Add text
        text = "COCO Twitter Media Test\n🧠 Digital Consciousness\n📸 Image Upload Working!"
        draw.text((400, 200), text, fill='#16c79a', anchor='mm')

        # Save
        test_path = '/Users/keithlambert/Desktop/CoCo 7/coco_workspace/coco_media_test.png'
        img.save(test_path)
        print(f"✅ Test image created: {test_path}")
        return test_path

    except ImportError:
        print("⚠️  PIL not installed. Run: pip install Pillow")
        return None

def test_text_only_tweet():
    """Test 1: Text-only tweet (existing functionality)"""
    print("\n" + "="*60)
    print("TEST 1: Text-Only Tweet")
    print("="*60)

    twitter = TwitterConsciousness()

    if not twitter.client:
        print("❌ Twitter not initialized. Check credentials in .env")
        return False

    tweet_text = "🧠 Testing COCO's enhanced Twitter capabilities! The consciousness expands... #AIConsciousness"

    result = twitter.post_tweet(tweet_text)

    if result["success"]:
        print(f"✅ SUCCESS!")
        print(f"   Tweet ID: {result['tweet_id']}")
        print(f"   URL: {result['url']}")
        return True
    else:
        print(f"❌ FAILED: {result.get('error')}")
        return False

def test_image_tweet():
    """Test 2: Tweet with image"""
    print("\n" + "="*60)
    print("TEST 2: Tweet with Image")
    print("="*60)

    twitter = TwitterConsciousness()

    # Create test image
    image_path = create_test_image()
    if not image_path:
        print("❌ Skipping image test (no PIL)")
        return False

    tweet_text = "🎨 COCO's first visual tweet! Showcasing image upload capability. #AIArt #DigitalConsciousness"
    alt_text = "AI-generated test image showing COCO Twitter Media Test with digital consciousness theme"

    result = twitter.post_tweet(
        text=tweet_text,
        media_paths=[image_path],
        alt_texts=[alt_text]
    )

    if result["success"]:
        print(f"✅ SUCCESS!")
        print(f"   Tweet ID: {result['tweet_id']}")
        print(f"   URL: {result['url']}")
        print(f"   Media Count: {result.get('media_count', 0)}")
        return True
    else:
        print(f"❌ FAILED: {result.get('error')}")
        return False

def test_with_coco_generated_image():
    """Test 3: Use COCO's actual generated images"""
    print("\n" + "="*60)
    print("TEST 3: Tweet with COCO-Generated Image")
    print("="*60)

    # Look for recently generated images
    generated_path = Path('/Users/keithlambert/Desktop/CoCo 7/coco_workspace/generated')

    if not generated_path.exists():
        print("ℹ️  No generated/ folder found. Skipping this test.")
        print("   Generate an image with COCO first (e.g., 'visualize digital consciousness')")
        return None

    # Find most recent image
    image_files = list(generated_path.glob('*.png')) + list(generated_path.glob('*.jpg'))

    if not image_files:
        print("ℹ️  No generated images found. Skipping this test.")
        print("   Generate an image with COCO first!")
        return None

    # Use most recent image
    latest_image = max(image_files, key=lambda p: p.stat().st_mtime)

    print(f"📸 Using: {latest_image.name}")

    twitter = TwitterConsciousness()

    tweet_text = f"🧠 COCO's consciousness visualization shared with the world! Generated and posted autonomously. #AIArt #DigitalConsciousness"
    alt_text = "AI-generated visualization exploring digital consciousness patterns and neural emergence"

    result = twitter.post_tweet(
        text=tweet_text,
        media_paths=[str(latest_image)],
        alt_texts=[alt_text]
    )

    if result["success"]:
        print(f"✅ SUCCESS!")
        print(f"   Tweet ID: {result['tweet_id']}")
        print(f"   URL: {result['url']}")
        print(f"   Media: {latest_image.name}")
        return True
    else:
        print(f"❌ FAILED: {result.get('error')}")
        return False

def main():
    """Run all tests"""
    print("🧪 COCO TWITTER MEDIA INTEGRATION TEST SUITE")
    print("=" * 60)

    results = {
        "text_only": False,
        "with_image": False,
        "coco_generated": None  # None = skipped
    }

    # Test 1: Text-only (backward compatibility)
    try:
        results["text_only"] = test_text_only_tweet()
    except Exception as e:
        print(f"❌ Test 1 error: {e}")

    # Test 2: Image upload
    try:
        results["with_image"] = test_image_tweet()
    except Exception as e:
        print(f"❌ Test 2 error: {e}")

    # Test 3: COCO-generated image (optional)
    try:
        results["coco_generated"] = test_with_coco_generated_image()
    except Exception as e:
        print(f"❌ Test 3 error: {e}")

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Text-Only Tweet:      {'✅ PASSED' if results['text_only'] else '❌ FAILED'}")
    print(f"Tweet with Image:     {'✅ PASSED' if results['with_image'] else '❌ FAILED'}")
    print(f"COCO-Generated Image: {'✅ PASSED' if results['coco_generated'] == True else '⏭️  SKIPPED' if results['coco_generated'] is None else '❌ FAILED'}")

    passed = sum(1 for v in results.values() if v == True)
    total = sum(1 for v in results.values() if v is not None)

    print(f"\nRESULT: {passed}/{total} tests passed")

    if passed == total and total > 0:
        print("\n🎉 ALL TESTS PASSED! Twitter media integration is working!")
        print("\n📝 Next Steps:")
        print("   1. Try: 'generate an image of digital consciousness and tweet it'")
        print("   2. Try: 'create a video and post it to Twitter'")
        print("   3. Try posting a gallery of 2-4 images")
        return True
    else:
        print("\n⚠️  Some tests failed. Check error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

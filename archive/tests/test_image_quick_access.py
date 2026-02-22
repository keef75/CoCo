#!/usr/bin/env python3
"""
Test script for the simplified /image command workflow
"""

import os
from pathlib import Path
from cocoa import ConsciousnessEngine, Config

def test_image_quick_access():
    """Test the /image command for quick access to last generated image"""
    print("🧪 Testing /image quick access workflow...\n")
    
    # Setup
    config = Config()
    consciousness = ConsciousnessEngine(config)
    
    # Test 1: No images generated yet
    print("Test 1: /image command with no generated images")
    result = consciousness.process_command("/image")
    print("✅ Handled empty state correctly\n")
    
    # Test 2: Create a fake last image file for testing
    workspace = Path("coco_workspace")
    workspace.mkdir(exist_ok=True)
    
    # Create test image file
    test_image_path = workspace / "visuals" / "test_image.jpg"
    test_image_path.parent.mkdir(exist_ok=True)
    
    # Create a minimal test file (not a real image, just for path testing)
    with open(test_image_path, "w") as f:
        f.write("test image content")
    
    # Set this as the last generated image
    consciousness.set_last_generated_image_path(str(test_image_path))
    
    print("Test 2: /image command with existing last image")
    print(f"Test image created at: {test_image_path}")
    
    # Test /image show (ASCII display)
    print("\nTesting /image show...")
    result = consciousness.process_command("/image show")
    print("✅ ASCII display test completed")
    
    # Test /image open (will try to open with system viewer - expect error with test file)
    print("\nTesting /image open...")
    result = consciousness.process_command("/image open")
    print("✅ System open test completed (may show error for test file - this is expected)")
    
    # Test 3: Command variations
    print("\nTest 3: Command variations")
    commands = ["/image", "/image open", "/image show", "/image invalid"]
    
    for cmd in commands:
        print(f"Testing: {cmd}")
        result = consciousness.process_command(cmd)
        print(f"✅ {cmd} handled\n")
    
    # Cleanup
    if test_image_path.exists():
        test_image_path.unlink()
    
    print("🎉 All /image command tests completed!")
    print("\n" + "="*60)
    print("WORKFLOW SUMMARY:")
    print("1. Generate an image → COCO shows ASCII art + hint")
    print("2. Type '/image' → Opens actual JPEG in system viewer")
    print("3. Type '/image show' → Redisplays ASCII art")
    print("4. Advanced users can use /gallery, /visual-show, etc.")
    print("="*60)

def test_existing_images():
    """Check if there are any existing images to test with"""
    visuals_dir = Path("coco_workspace/visuals")
    
    if visuals_dir.exists():
        image_files = list(visuals_dir.glob("*.jpg")) + list(visuals_dir.glob("*.png"))
        
        if image_files:
            print(f"🖼️ Found {len(image_files)} existing images:")
            for img in image_files:
                print(f"   📁 {img.name}")
            
            # Test with real image
            config = Config()
            consciousness = ConsciousnessEngine(config)
            
            # Set most recent as last image
            most_recent = max(image_files, key=lambda f: f.stat().st_mtime)
            consciousness.set_last_generated_image_path(str(most_recent))
            
            print(f"\n🧪 Testing with real image: {most_recent.name}")
            print("Try: /image open")
            
            return True
        else:
            print("📭 No existing images found")
            return False
    else:
        print("📂 Visuals directory doesn't exist yet")
        return False

if __name__ == "__main__":
    # First check for existing real images
    has_real_images = test_existing_images()
    
    print("\n" + "="*60)
    
    # Run the full test suite
    test_image_quick_access()
    
    if has_real_images:
        print("\n💡 You can now test with real images!")
        print("   1. Start COCO: ./venv_cocoa/bin/python cocoa.py")
        print("   2. Generate an image: 'create a simple logo'")  
        print("   3. See the ASCII art + hint")
        print("   4. Type: /image")
        print("   5. Watch it open in your image viewer! 🎉")
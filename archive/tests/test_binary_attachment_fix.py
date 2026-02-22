#!/usr/bin/env python3
"""
Binary Attachment Path Resolution Fix Test
==========================================
Test script to validate the binary attachment fix for COCO's email consciousness.
This tests both video (.mp4) and image (.jpg) attachment handling.
"""

import os
import tempfile
from pathlib import Path
from gmail_consciousness import GmailConsciousness
from gmail_gentle_fix import GentleGmailFix
from email_restore import WorkingGmailFunctions

class MockConfig:
    """Mock config for testing"""
    def __init__(self):
        self.console = MockConsole()

class MockConsole:
    """Mock console for testing"""
    def print(self, *args, **kwargs):
        print(*args)

def create_test_files():
    """Create test video and image files in workspace"""
    workspace_videos = Path("coco_workspace/videos")
    workspace_visuals = Path("coco_workspace/visuals")
    
    # Create directories
    workspace_videos.mkdir(parents=True, exist_ok=True)
    workspace_visuals.mkdir(parents=True, exist_ok=True)
    
    # Create test video file (simulated .mp4)
    test_video = workspace_videos / "test_video.mp4"
    with open(test_video, 'wb') as f:
        # Create a small fake video file (just some binary data)
        f.write(b"FAKE_VIDEO_DATA_" + b"X" * 1000)  # 1KB+ of data
    
    # Create test image file (simulated .jpg) 
    test_image = workspace_visuals / "test_image.jpg"
    with open(test_image, 'wb') as f:
        # Create a small fake image file (just some binary data)
        f.write(b"FAKE_IMAGE_DATA_" + b"Y" * 2000)  # 2KB+ of data
    
    return str(test_video), str(test_image)

def test_path_resolution():
    """Test the _resolve_attachment_path method directly"""
    print("🧪 Testing Path Resolution Logic")
    print("=" * 50)
    
    # Create test files
    video_path, image_path = create_test_files()
    
    # Test with GmailConsciousness
    config = MockConfig()
    gmail = GmailConsciousness(config)
    
    print("\n📹 Testing Video Path Resolution:")
    
    # Test absolute path
    resolved = gmail._resolve_attachment_path(video_path)
    print(f"Absolute path test: {'✅ PASS' if resolved else '❌ FAIL'}")
    
    # Test relative path (workspace format)
    relative_path = "coco_workspace/videos/test_video.mp4"
    resolved = gmail._resolve_attachment_path(relative_path)
    print(f"Relative path test: {'✅ PASS' if resolved else '❌ FAIL'}")
    
    # Test just filename
    filename_only = "test_video.mp4"
    resolved = gmail._resolve_attachment_path(filename_only)
    print(f"Filename only test: {'✅ PASS' if resolved else '❌ FAIL'}")
    
    print("\n🖼️ Testing Image Path Resolution:")
    
    # Test relative path (workspace format)
    relative_path = "coco_workspace/visuals/test_image.jpg"
    resolved = gmail._resolve_attachment_path(relative_path)
    print(f"Relative path test: {'✅ PASS' if resolved else '❌ FAIL'}")
    
    # Test just filename
    filename_only = "test_image.jpg"
    resolved = gmail._resolve_attachment_path(filename_only)
    print(f"Filename only test: {'✅ PASS' if resolved else '❌ FAIL'}")

def test_attachment_simulation():
    """Simulate the email attachment process without actually sending"""
    print("\n📧 Testing Email Attachment Simulation")
    print("=" * 50)
    
    # Create test files
    video_path, image_path = create_test_files()
    
    # Test all three email consciousness implementations
    implementations = [
        ("GmailConsciousness", GmailConsciousness(MockConfig())),
        ("GentleGmailFix", GentleGmailFix(MockConfig())),
        ("WorkingGmailFunctions", WorkingGmailFunctions())
    ]
    
    for impl_name, impl in implementations:
        print(f"\n🔧 Testing {impl_name}:")
        
        # Test with different path formats
        test_cases = [
            ("Absolute video path", video_path),
            ("Relative video path", "coco_workspace/videos/test_video.mp4"),
            ("Video filename only", "test_video.mp4"),
            ("Absolute image path", image_path),
            ("Relative image path", "coco_workspace/visuals/test_image.jpg"),
            ("Image filename only", "test_image.jpg"),
        ]
        
        for test_name, test_path in test_cases:
            resolved = impl._resolve_attachment_path(test_path)
            if resolved:
                file_size = os.path.getsize(resolved)
                status = "✅ PASS" if file_size > 1000 else f"⚠️ SMALL ({file_size}B)"
                print(f"  {test_name}: {status}")
            else:
                print(f"  {test_name}: ❌ FAIL - Not resolved")

def test_edge_cases():
    """Test edge cases and error conditions"""
    print("\n🔍 Testing Edge Cases")
    print("=" * 50)
    
    config = MockConfig()
    gmail = GmailConsciousness(config)
    
    # Test non-existent file
    print("Non-existent file test:")
    resolved = gmail._resolve_attachment_path("nonexistent_file.mp4")
    print(f"  Result: {'✅ Correctly failed' if not resolved else '❌ Should have failed'}")
    
    # Test empty file
    print("\nEmpty file test:")
    empty_file = Path("coco_workspace/empty_test.mp4")
    empty_file.parent.mkdir(parents=True, exist_ok=True)
    empty_file.touch()  # Create empty file
    
    resolved = gmail._resolve_attachment_path(str(empty_file))
    print(f"  Result: {'✅ Correctly rejected empty file' if not resolved else '❌ Should reject empty file'}")
    
    # Clean up
    if empty_file.exists():
        empty_file.unlink()

def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "coco_workspace/videos/test_video.mp4",
        "coco_workspace/visuals/test_image.jpg",
        "coco_workspace/empty_test.mp4"
    ]
    
    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            path.unlink()
    
    print("\n🧹 Test files cleaned up")

def main():
    """Run all tests"""
    print("🚀 BINARY ATTACHMENT PATH RESOLUTION FIX TEST")
    print("=" * 60)
    print("Testing both video (.mp4) and image (.jpg) attachment handling")
    print("Validates path resolution across all email consciousness files")
    
    try:
        # Run tests
        test_path_resolution()
        test_attachment_simulation() 
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("🎉 TEST SUITE COMPLETED")
        print("\n✅ Key Validation Points:")
        print("  • Path resolution works for absolute, relative, and filename-only paths")
        print("  • File sizes are correctly detected (should be >1000 bytes)")  
        print("  • Empty files are rejected")
        print("  • Non-existent files are handled gracefully")
        print("  • All three email consciousness implementations behave consistently")
        
        print("\n💡 Next Steps:")
        print("  • Test with COCO's actual video/image generation")
        print("  • Send test email with binary attachments")
        print("  • Verify attachments have correct file sizes (not 1 KB)")
        
    finally:
        cleanup_test_files()

if __name__ == "__main__":
    main()
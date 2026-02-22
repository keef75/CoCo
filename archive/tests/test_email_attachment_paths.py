#!/usr/bin/env python3
"""
Test Email Attachment Path Resolution
====================================
Test the basic path resolution logic for email attachments,
specifically focusing on macOS temporary directory paths.
"""

import os
from pathlib import Path
from gmail_consciousness import GmailConsciousness

def test_path_resolution():
    """Test path resolution with various file paths"""
    print("🧪 Testing Email Attachment Path Resolution")
    print("=" * 50)
    
    # Initialize Gmail consciousness
    gmail = GmailConsciousness()
    
    # Test cases - including the problematic paths from the user
    test_paths = [
        # Normal relative paths
        "coco_workspace/test_file.txt",
        "test_file.txt",
        
        # macOS temporary directory paths (the problematic ones)
        "/var/folders/d6/j5ykvzfx6xz6qtbwmdv7xmwh0000gn/T/TemporaryItems/NSIRD_screencaptureui_vjD9cc/Screenshot 2025-09-07 at 12.51.54 AM.png",
        "/var/folders/d6/j5ykvzfx6xz6qtbwmdv7xmwh0000gn/T/TemporaryItems/NSIRD_screencaptureui_KuQUL2/Screenshot 2025-09-07 at 12.59.03 AM.png",
        
        # Normal absolute paths
        os.path.abspath("test_file.txt"),
        "/Users/test/Desktop/image.png",
        
        # Non-existent paths
        "/non/existent/file.png",
        "missing_file.txt"
    ]
    
    # Create a test file in workspace for testing
    workspace_test_file = Path("coco_workspace") / "test_attachment.txt"
    workspace_test_file.parent.mkdir(parents=True, exist_ok=True)
    with open(workspace_test_file, 'w') as f:
        f.write("Test attachment content - this file should be found by path resolution")
    
    print(f"📁 Created test file: {workspace_test_file} ({os.path.getsize(workspace_test_file)} bytes)")
    print()
    
    # Test each path
    for i, test_path in enumerate(test_paths, 1):
        print(f"🔍 Test {i}: {test_path}")
        print(f"   Path exists: {'✅' if os.path.exists(test_path) else '❌'}")
        
        # Test the path resolution
        try:
            resolved = gmail._resolve_attachment_path(test_path)
            if resolved:
                file_size = os.path.getsize(resolved)
                print(f"   ✅ Resolved to: {resolved}")
                print(f"   📊 File size: {file_size} bytes")
            else:
                print(f"   ❌ Could not resolve path")
        except Exception as e:
            print(f"   💥 Error during resolution: {e}")
        
        print()
    
    # Cleanup
    if workspace_test_file.exists():
        workspace_test_file.unlink()
        print(f"🧹 Cleaned up test file: {workspace_test_file}")

def test_attachment_encoding():
    """Test the actual attachment encoding logic"""
    print("\n🧪 Testing Attachment Encoding")
    print("=" * 50)
    
    # Create a test binary file to simulate a screenshot
    test_file = Path("coco_workspace") / "test_binary.png"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create fake PNG data (PNG header + some data)
    png_header = b'\x89PNG\r\n\x1a\n'  # Real PNG file signature
    fake_image_data = png_header + b'FAKE_IMAGE_DATA_FOR_TESTING' * 100  # Make it substantial size
    
    with open(test_file, 'wb') as f:
        f.write(fake_image_data)
    
    file_size = os.path.getsize(test_file)
    print(f"📁 Created test binary file: {test_file} ({file_size} bytes)")
    
    # Test path resolution on this file
    gmail = GmailConsciousness()
    resolved = gmail._resolve_attachment_path(str(test_file))
    
    if resolved:
        resolved_size = os.path.getsize(resolved)
        print(f"✅ Path resolution working: {resolved_size} bytes")
        
        # Test the actual attachment creation (without sending)
        print("🧪 Testing attachment encoding logic...")
        
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Simulate the attachment encoding process
            msg = MIMEMultipart()
            filename = os.path.basename(resolved)
            
            with open(resolved, 'rb') as f:
                file_data = f.read()
            
            print(f"📊 Read {len(file_data)} bytes from file")
            
            # Create binary attachment (same logic as in send_email)
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            
            # Get the encoded size
            encoded_data = part.as_string()
            print(f"📧 Encoded attachment size: {len(encoded_data)} characters")
            print(f"✅ Attachment encoding successful")
            
        except Exception as e:
            print(f"❌ Attachment encoding failed: {e}")
    else:
        print(f"❌ Path resolution failed")
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()
        print(f"🧹 Cleaned up test file: {test_file}")

if __name__ == "__main__":
    test_path_resolution()
    test_attachment_encoding()
    
    print("\n" + "=" * 50)
    print("🎯 Key Findings:")
    print("• This test shows exactly what path resolution sees")
    print("• Binary encoding logic can be validated independently")
    print("• Helps identify where the 51-byte issue originates")
    print("• Focus on the macOS temporary directory path results")
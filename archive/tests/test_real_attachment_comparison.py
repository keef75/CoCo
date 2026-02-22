#!/usr/bin/env python3
"""
Test Real File Attachment Comparison
===================================
Compare how text vs binary attachments are handled to identify
where the 51-byte corruption occurs.
"""

import os
from pathlib import Path
from gmail_consciousness import GmailConsciousness

def create_test_files():
    """Create test files for comparison"""
    workspace = Path("coco_workspace")
    workspace.mkdir(exist_ok=True)
    
    # Create a text file (Markdown)
    text_file = workspace / "test_document.md"
    with open(text_file, 'w') as f:
        f.write("""# Test Document
This is a test markdown file for email attachment testing.

## Features
- Text attachment handling
- Should work correctly according to user
- Multiple lines of content to make it substantial

## Content
This file contains enough content to be meaningful for attachment testing.
The user reported that text attachments like Markdown work fine, but image 
and video attachments show as 51 bytes instead of proper file size.
""")
    
    # Create a binary file (PNG)
    binary_file = workspace / "test_image.png"
    png_header = b'\x89PNG\r\n\x1a\n'
    fake_image_data = png_header + b'FAKE_PNG_DATA' * 200  # Make it substantial
    with open(binary_file, 'wb') as f:
        f.write(fake_image_data)
    
    # Create a video file (MP4)
    video_file = workspace / "test_video.mp4"
    fake_mp4_data = b'ftyp' + b'FAKE_MP4_DATA' * 300  # Make it substantial
    with open(video_file, 'wb') as f:
        f.write(fake_mp4_data)
    
    return text_file, binary_file, video_file

def test_attachment_handling():
    """Test how different file types are handled"""
    print("🧪 Testing Text vs Binary Attachment Handling")
    print("=" * 55)
    
    # Create test files
    text_file, binary_file, video_file = create_test_files()
    
    # Get file sizes
    text_size = os.path.getsize(text_file)
    binary_size = os.path.getsize(binary_file)
    video_size = os.path.getsize(video_file)
    
    print(f"📄 Text file: {text_file} ({text_size} bytes)")
    print(f"🖼️ Binary file: {binary_file} ({binary_size} bytes)")
    print(f"🎥 Video file: {video_file} ({video_size} bytes)")
    print()
    
    # Initialize Gmail consciousness
    gmail = GmailConsciousness()
    
    # Test each attachment type
    test_files = [
        ("Text/Markdown", text_file, "text"),
        ("PNG Image", binary_file, "binary"), 
        ("MP4 Video", video_file, "binary")
    ]
    
    for file_type, file_path, expected_handling in test_files:
        print(f"🔍 Testing {file_type}: {file_path.name}")
        
        # Test path resolution
        resolved = gmail._resolve_attachment_path(str(file_path))
        if resolved:
            resolved_size = os.path.getsize(resolved)
            print(f"   ✅ Path resolved: {resolved_size} bytes")
            
            # Simulate the attachment creation process
            try:
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.base import MIMEBase
                from email import encoders
                
                filename = os.path.basename(resolved)
                
                # Check which handling path it takes
                if resolved.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.pdf')):
                    print(f"   📋 Handling as: BINARY attachment")
                    
                    # Binary file handling
                    with open(resolved, 'rb') as f:
                        file_data = f.read()
                    
                    print(f"   📊 Read binary data: {len(file_data)} bytes")
                    
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    
                    # Check encoded size
                    encoded = part.as_string()
                    print(f"   📧 Encoded size: {len(encoded)} characters")
                    
                else:
                    print(f"   📋 Handling as: TEXT attachment")
                    
                    # Text file handling
                    with open(resolved, 'r') as f:
                        content = f.read()
                    
                    print(f"   📊 Read text data: {len(content)} characters")
                    
                    part = MIMEText(content, 'plain')
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    
                    # Check encoded size
                    encoded = part.as_string()
                    print(f"   📧 Encoded size: {len(encoded)} characters")
                
                print(f"   ✅ {file_type} attachment processing successful")
                
            except Exception as e:
                print(f"   ❌ {file_type} attachment processing failed: {e}")
        else:
            print(f"   ❌ Path resolution failed")
        
        print()
    
    # Cleanup
    for file_path in [text_file, binary_file, video_file]:
        if file_path.exists():
            file_path.unlink()
    
    print("🧹 Cleaned up test files")
    print()
    print("🎯 Analysis:")
    print("• Text files (.md) use MIMEText with 'r' mode reading")
    print("• Binary files (.png, .mp4) use MIMEBase with 'rb' mode reading")
    print("• Both should preserve original file sizes")
    print("• If binary attachments show 51 bytes, the issue is likely in:")
    print("  - File reading process (rb mode)")
    print("  - Base64 encoding step")
    print("  - MIME attachment creation")

if __name__ == "__main__":
    test_attachment_handling()
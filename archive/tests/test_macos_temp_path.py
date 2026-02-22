#!/usr/bin/env python3
"""
macOS Temporary Path Email Attachment Test
==========================================
Test what happens when COCO tries to email attach files from macOS temporary paths.
"""

import os
import shutil
from pathlib import Path
from cocoa import Config, ToolSystem

def create_macos_temp_simulation():
    """Create a file structure that exactly mimics macOS temporary screenshot paths"""
    # Create the exact directory structure from the user's example
    temp_base = Path("/tmp/COCO_test_temp")  # Use /tmp instead of /var/folders for testing
    screenshot_dir = temp_base / "NSIRD_screencaptureui_test"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a realistic screenshot file
    screenshot_file = screenshot_dir / "Screenshot 2025-09-07 at 1.02.44 AM.png"
    
    # Create realistic PNG data
    png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
    png_data = png_header + b'\x00\x01\x00\x01\x08\x02\x00\x00\x00' + b'SCREENSHOT_DATA' * 100
    png_end = b'\x00\x00\x00\x00IEND\xaeB`\x82'
    
    full_png = png_header + png_data + png_end
    
    with open(screenshot_file, 'wb') as f:
        f.write(full_png)
    
    return screenshot_file, temp_base

def test_macos_temp_attachment():
    """Test email attachment with macOS-style temporary path"""
    print("🧪 macOS Temporary Path Attachment Test")
    print("=" * 45)
    
    # Create test file
    screenshot_file, temp_base = create_macos_temp_simulation()
    file_size = os.path.getsize(screenshot_file)
    print(f"📸 Created screenshot: {screenshot_file} ({file_size} bytes)")
    
    try:
        # Initialize COCO
        config = Config()
        tools = ToolSystem(config)
        
        if not tools.gmail:
            print("❌ Gmail consciousness not available")
            return
        
        print("🧠 COCO Gmail consciousness ready")
        
        # Test 1: Direct path resolution
        print(f"\n🔍 Test 1: Direct path resolution")
        print(f"Path: {screenshot_file}")
        print(f"Exists: {'✅' if os.path.exists(screenshot_file) else '❌'}")
        
        resolved = tools.gmail._resolve_attachment_path(str(screenshot_file))
        if resolved:
            resolved_size = os.path.getsize(resolved)
            print(f"✅ Resolved: {resolved_size} bytes")
        else:
            print(f"❌ Resolution failed")
        
        # Test 2: Simulate COCO function calling with this path
        print(f"\n🔍 Test 2: Function calling simulation")
        try:
            # This is what would happen when COCO tries to send an email
            attachment_list = [{"filepath": str(screenshot_file)}]
            print(f"📎 Attachment list: {attachment_list}")
            
            # Test the actual email sending logic (without sending)
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            
            msg = MIMEMultipart()
            
            for attachment in attachment_list:
                original_filepath = attachment.get('filepath')
                print(f"🔍 Processing: {original_filepath}")
                
                # Use COCO's path resolution
                resolved_filepath = tools.gmail._resolve_attachment_path(original_filepath)
                
                if resolved_filepath:
                    filename = os.path.basename(resolved_filepath)
                    print(f"📎 Filename: {filename}")
                    
                    # Check if binary
                    if resolved_filepath.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.pdf')):
                        print("📋 Processing as binary attachment")
                        
                        try:
                            with open(resolved_filepath, 'rb') as f:
                                file_data = f.read()
                            
                            data_size = len(file_data)
                            print(f"📊 Read {data_size} bytes")
                            
                            if data_size == 0:
                                print("❌ File data is empty!")
                            elif data_size < 100:
                                print(f"⚠️ Suspiciously small: {data_size} bytes")
                            else:
                                print("✅ File data looks good")
                            
                            # Create MIME attachment
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(file_data)
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                            msg.attach(part)
                            
                            encoded_size = len(part.as_string())
                            print(f"📧 Encoded attachment: {encoded_size} characters")
                            print("✅ Binary attachment processing successful")
                            
                        except Exception as e:
                            print(f"❌ Binary processing error: {e}")
                    else:
                        print("📋 Would process as text attachment")
                else:
                    print("❌ Path resolution failed during attachment processing")
            
        except Exception as e:
            print(f"❌ Function calling simulation failed: {e}")
        
        # Test 3: Check what happens with file permissions
        print(f"\n🔍 Test 3: File permission check")
        print(f"Readable: {'✅' if os.access(screenshot_file, os.R_OK) else '❌'}")
        print(f"File size via stat: {os.stat(screenshot_file).st_size} bytes")
        
        # Test 4: Direct file reading
        print(f"\n🔍 Test 4: Direct file reading test")
        try:
            with open(screenshot_file, 'rb') as f:
                data = f.read()
            print(f"✅ Direct read successful: {len(data)} bytes")
            
            # Check first few bytes to make sure it's not corrupted
            if data.startswith(b'\x89PNG'):
                print("✅ PNG header detected - file integrity good")
            else:
                print(f"⚠️ Unexpected file header: {data[:10]}")
                
        except Exception as e:
            print(f"❌ Direct file read failed: {e}")
    
    finally:
        # Cleanup
        if temp_base.exists():
            shutil.rmtree(temp_base)
            print(f"\n🧹 Cleaned up test directory: {temp_base}")

if __name__ == "__main__":
    test_macos_temp_attachment()
    
    print("\n" + "=" * 45)
    print("🎯 Analysis Points:")
    print("• Path resolution success/failure")
    print("• File reading success and data size")
    print("• MIME encoding process")
    print("• File permission issues")
    print("• Data corruption detection")
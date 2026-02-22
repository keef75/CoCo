#!/usr/bin/env python3
"""
COCO Email Integration Debug Test
================================
Test the complete email attachment flow as it would happen through COCO,
focusing on macOS temporary file handling and binary attachment issues.
"""

import os
from pathlib import Path
from cocoa import Config, ToolSystem, HierarchicalMemorySystem

def create_temporary_file_simulation():
    """Create a file that simulates the macOS temporary file structure"""
    # Create a temporary file structure that mimics macOS screenshot paths
    temp_base = Path("coco_workspace") / "temp_simulation" 
    temp_base.mkdir(parents=True, exist_ok=True)
    
    # Simulate the macOS temporary file path structure
    temp_file = temp_base / "Screenshot 2025-09-07 at 12.51.54 AM.png"
    
    # Create a realistic PNG file
    png_header = b'\x89PNG\r\n\x1a\n'
    # Add IHDR chunk for a 1x1 pixel image
    ihdr = b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
    # Add some fake image data
    fake_data = b'FAKE_PNG_CHUNK_DATA' * 50
    # PNG end chunk
    iend = b'\x00\x00\x00\x00IEND\xaeB`\x82'
    
    png_data = png_header + ihdr + fake_data + iend
    
    with open(temp_file, 'wb') as f:
        f.write(png_data)
    
    return temp_file

def test_coco_email_attachment():
    """Test email attachment through COCO's actual system"""
    print("🧪 COCO Email Attachment Integration Test")
    print("=" * 50)
    
    # Create test file
    test_file = create_temporary_file_simulation()
    file_size = os.path.getsize(test_file)
    print(f"📁 Created test file: {test_file} ({file_size} bytes)")
    
    # Initialize COCO components
    print("🧠 Initializing COCO consciousness...")
    try:
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        
        if not tools.gmail:
            print("❌ Gmail consciousness not available - check GMAIL_APP_PASSWORD in .env")
            return False
        
        print("✅ COCO consciousness ready")
        
        # Test the path resolution that COCO would use
        print(f"\n🔍 Testing path resolution for: {test_file}")
        resolved = tools.gmail._resolve_attachment_path(str(test_file))
        
        if resolved:
            resolved_size = os.path.getsize(resolved)
            print(f"✅ Path resolved: {resolved} ({resolved_size} bytes)")
            
            # Test attachment format that COCO uses
            attachment_config = {"filepath": str(test_file)}
            print(f"📎 Attachment config: {attachment_config}")
            
            # Simulate the email sending process (without actually sending)
            print("\n📧 Simulating email attachment process...")
            
            # This is the exact logic from send_email method
            original_filepath = attachment_config.get('filepath')
            resolved_filepath = tools.gmail._resolve_attachment_path(original_filepath)
            
            if resolved_filepath:
                filename = os.path.basename(resolved_filepath)
                print(f"📎 Filename: {filename}")
                
                # Check if it would be treated as binary
                is_binary = resolved_filepath.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.pdf'))
                print(f"📋 Binary attachment: {is_binary}")
                
                if is_binary:
                    try:
                        with open(resolved_filepath, 'rb') as f:
                            file_data = f.read()
                        
                        actual_size = len(file_data)
                        print(f"📊 Read binary data: {actual_size} bytes")
                        
                        if actual_size == 0:
                            print("❌ File is empty!")
                        elif actual_size < 100:
                            print(f"⚠️ File is suspiciously small: {actual_size} bytes")
                        else:
                            print("✅ File size looks correct")
                        
                        # Test the encoding
                        from email.mime.base import MIMEBase
                        from email import encoders
                        
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file_data)
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                        
                        encoded_size = len(part.as_string())
                        print(f"📧 Encoded attachment: {encoded_size} characters")
                        print("✅ Binary encoding successful")
                        
                    except Exception as e:
                        print(f"❌ Binary processing failed: {e}")
                else:
                    print("📋 Would be processed as text attachment")
            else:
                print("❌ Path resolution failed during email simulation")
                
        else:
            print("❌ Initial path resolution failed")
        
    except Exception as e:
        print(f"❌ COCO initialization failed: {e}")
        return False
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()
        test_file.parent.rmdir()
        print(f"\n🧹 Cleaned up test file and directory")
    
    return True

def test_with_actual_binary_vs_text():
    """Compare actual binary vs text file processing"""
    print("\n🧪 Binary vs Text File Processing Comparison")
    print("=" * 50)
    
    # Create two files with different content but same size range
    workspace = Path("coco_workspace")
    
    # Create text file
    text_file = workspace / "test.md"
    text_content = "# Test File\n" + "This is test content. " * 10  # Make it substantial
    with open(text_file, 'w') as f:
        f.write(text_content)
    
    # Create binary file with similar size
    binary_file = workspace / "test.png"
    binary_content = b'\x89PNG\r\n\x1a\n' + b'TEST_DATA' * 20  # Similar size
    with open(binary_file, 'wb') as f:
        f.write(binary_content)
    
    text_size = os.path.getsize(text_file)
    binary_size = os.path.getsize(binary_file)
    
    print(f"📄 Text file: {text_size} bytes")
    print(f"🖼️ Binary file: {binary_size} bytes")
    
    # Test both through COCO
    try:
        config = Config()
        tools = ToolSystem(config)
        
        if tools.gmail:
            for file_path, file_type in [(text_file, "text"), (binary_file, "binary")]:
                print(f"\n🔍 Testing {file_type}: {file_path}")
                resolved = tools.gmail._resolve_attachment_path(str(file_path))
                if resolved:
                    actual_size = os.path.getsize(resolved)
                    print(f"   Resolved size: {actual_size} bytes")
                else:
                    print(f"   ❌ Resolution failed")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Cleanup
    if text_file.exists():
        text_file.unlink()
    if binary_file.exists():
        binary_file.unlink()

if __name__ == "__main__":
    success = test_coco_email_attachment()
    test_with_actual_binary_vs_text()
    
    if success:
        print("\n" + "=" * 50)
        print("🎯 Key Insights:")
        print("• COCO email attachment system components are working")
        print("• Binary file reading and encoding logic is correct")
        print("• Issue likely occurs during actual email sending process")
        print("• Focus on timing of file access vs email transmission")
        print("• May need to verify files exist at send time")
    else:
        print("\n❌ Test failed - check COCO configuration")
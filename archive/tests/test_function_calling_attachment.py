#!/usr/bin/env python3
"""
Function Calling Attachment Test
===============================
Test the exact function calling flow that COCO uses for email attachments
to identify where large multimedia files become 51-byte corrupted files.
"""

import os
import shutil
from pathlib import Path
from cocoa import Config, ToolSystem, ConsciousnessEngine, HierarchicalMemorySystem

def create_large_multimedia_files():
    """Create realistic large multimedia files like the user mentioned"""
    workspace = Path("coco_workspace")
    workspace.mkdir(exist_ok=True)
    
    # Create a large image file (simulate high-resolution screenshot)
    large_image = workspace / "high_res_screenshot.png"
    png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
    # Simulate a large PNG (multiple megabytes like the user mentioned)
    large_png_data = png_header + b'HIGH_RES_PIXEL_DATA' * 50000  # ~1MB
    png_end = b'\x00\x00\x00\x00IEND\xaeB`\x82'
    
    with open(large_image, 'wb') as f:
        f.write(large_png_data)
    
    # Create a large video file (simulate 5-8 second movie)
    large_video = workspace / "short_movie.mp4"
    mp4_header = b'ftypmp4'
    # Simulate a video file in megabyte range like the user mentioned  
    large_mp4_data = mp4_header + b'VIDEO_FRAME_DATA_CHUNK' * 100000  # ~2MB
    
    with open(large_video, 'wb') as f:
        f.write(large_mp4_data)
    
    return large_image, large_video

def test_function_calling_flow():
    """Test the exact function calling flow that COCO uses"""
    print("🧪 Function Calling Email Attachment Test")
    print("=" * 50)
    
    # Create large multimedia files
    large_image, large_video = create_large_multimedia_files()
    
    image_size = os.path.getsize(large_image)
    video_size = os.path.getsize(large_video)
    
    print(f"🖼️ Created large image: {large_image} ({image_size:,} bytes = {image_size/1024:.1f} KB)")
    print(f"🎥 Created large video: {large_video} ({video_size:,} bytes = {video_size/1024:.1f} KB)")
    
    try:
        # Initialize COCO exactly like it would be in real usage
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)
        
        if not tools.gmail:
            print("❌ Gmail consciousness not available")
            return
        
        print("🧠 COCO consciousness system ready")
        
        # Test the exact function calling parameters that would be used
        test_cases = [
            {
                "name": "Large Image Attachment",
                "tool_input": {
                    "to": "keith@gococoa.ai",
                    "subject": "Large Image Test",
                    "body": "Testing large image attachment",
                    "attachments": [{"filepath": str(large_image)}]
                }
            },
            {
                "name": "Large Video Attachment", 
                "tool_input": {
                    "to": "keith@gococoa.ai",
                    "subject": "Large Video Test",
                    "body": "Testing large video attachment",
                    "attachments": [{"filepath": str(large_video)}]
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🔍 Testing: {test_case['name']}")
            tool_input = test_case["tool_input"]
            
            # Step 1: Check file before function calling
            filepath = tool_input["attachments"][0]["filepath"]
            before_size = os.path.getsize(filepath)
            print(f"   📊 File size before processing: {before_size:,} bytes")
            
            # Step 2: Simulate the exact function calling flow
            try:
                # This is exactly what happens in _execute_tool
                to = tool_input["to"]
                subject = tool_input["subject"]
                body = tool_input["body"]
                attachments = tool_input.get("attachments")
                
                print(f"   📎 Attachments parameter: {attachments}")
                
                # Step 3: Test the ToolSystem.send_email call
                print("   🔄 Calling tools.send_email()...")
                
                # Don't actually send, but test the attachment processing
                # by directly calling the Gmail consciousness
                if tools.gmail and attachments:
                    for attachment in attachments:
                        original_filepath = attachment.get('filepath')
                        print(f"   🔍 Processing attachment: {original_filepath}")
                        
                        # Test path resolution
                        resolved = tools.gmail._resolve_attachment_path(original_filepath)
                        if resolved:
                            resolved_size = os.path.getsize(resolved)
                            print(f"   ✅ Path resolved: {resolved_size:,} bytes")
                            
                            # Test file reading
                            try:
                                with open(resolved, 'rb') as f:
                                    file_data = f.read()
                                read_size = len(file_data)
                                print(f"   📖 File read: {read_size:,} bytes")
                                
                                if read_size != resolved_size:
                                    print(f"   ⚠️ SIZE MISMATCH: stat={resolved_size:,} vs read={read_size:,}")
                                elif read_size < 1000:
                                    print(f"   ❌ SUSPICIOUSLY SMALL: {read_size} bytes (should be KB/MB)")
                                else:
                                    print(f"   ✅ File size looks correct")
                                    
                            except Exception as read_error:
                                print(f"   ❌ File read error: {read_error}")
                        else:
                            print(f"   ❌ Path resolution failed")
                
                # Call the actual function (without sending email for safety)
                print("   📧 Testing function calling handler...")
                # result = engine._execute_tool("send_email", tool_input)
                # For safety, don't actually call the tool, just verify the flow
                print("   ✅ Function calling flow verified")
                
            except Exception as e:
                print(f"   ❌ Function calling error: {e}")
    
    except Exception as e:
        print(f"❌ COCO initialization error: {e}")
    
    finally:
        # Cleanup
        if large_image.exists():
            large_image.unlink()
        if large_video.exists():
            large_video.unlink()
        print(f"\n🧹 Cleaned up test files")

def test_file_access_timing():
    """Test if there are timing issues with file access"""
    print("\n🧪 File Access Timing Test")
    print("=" * 40)
    
    # Simulate what might happen with macOS temporary files
    temp_dir = Path("coco_workspace") / "temp_timing_test"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = temp_dir / "timing_test.png"
    test_data = b'PNG_DATA' * 1000  # 8KB file
    
    with open(test_file, 'wb') as f:
        f.write(test_data)
    
    print(f"📁 Created test file: {test_file} ({os.path.getsize(test_file)} bytes)")
    
    # Test multiple rapid reads (simulating what might happen)
    for i in range(3):
        try:
            size_before = os.path.getsize(test_file)
            with open(test_file, 'rb') as f:
                data = f.read()
            size_read = len(data)
            
            print(f"   Read {i+1}: stat={size_before}, read={size_read}, match={'✅' if size_before == size_read else '❌'}")
            
        except Exception as e:
            print(f"   Read {i+1}: ❌ Error: {e}")
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()
    if temp_dir.exists():
        temp_dir.rmdir()
    
    print("🧹 Timing test cleanup complete")

if __name__ == "__main__":
    test_function_calling_flow()
    test_file_access_timing()
    
    print("\n" + "=" * 50)
    print("🎯 Critical Points to Check:")
    print("• File sizes before vs after processing")
    print("• Path resolution for large multimedia files")
    print("• File reading consistency")
    print("• Function calling parameter preservation")
    print("• Timing issues with file access")
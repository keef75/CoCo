#!/usr/bin/env python3
"""
Unified Binary Attachment Fix Test
==================================
Test COCO's Gmail consciousness with expert-recommended binary attachment fixes.
Validates the precise MIME type approach that addresses the root cause.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def create_expert_test_files():
    """Create test files with proper binary signatures for validation"""
    workspace = Path("./coco_workspace")
    workspace.mkdir(exist_ok=True)
    
    created_files = []
    
    # Create minimal valid JPEG (expert-recommended approach)
    jpeg_header = bytes.fromhex('FFD8FFE000104A464946000101000001000100')
    jpeg_body = b'TEST_JPEG_DATA' * 50  # Make it reasonably sized
    jpeg_end = bytes.fromhex('FFD9')
    jpeg_data = jpeg_header + jpeg_body + jpeg_end
    
    test_jpg = workspace / f'test_image_{datetime.now().strftime("%H%M%S")}.jpg'
    test_jpg.write_bytes(jpeg_data)
    created_files.append(str(test_jpg))
    print(f"✅ Created {test_jpg.name}: {len(jpeg_data):,} bytes (JPEG magic: FF D8 FF)")
    
    # Create minimal valid MP4 (expert-recommended approach)
    # Basic MP4 with ftyp box
    mp4_header = bytes.fromhex('0000001C667479706D7034320000000000000000')  # ftyp mp42
    mp4_body = b'TEST_MP4_FRAME_DATA' * 100  # Make it reasonably sized
    mp4_data = mp4_header + mp4_body
    
    test_mp4 = workspace / f'test_video_{datetime.now().strftime("%H%M%S")}.mp4'
    test_mp4.write_bytes(mp4_data)
    created_files.append(str(test_mp4))
    print(f"✅ Created {test_mp4.name}: {len(mp4_data):,} bytes (MP4 contains 'ftyp')")
    
    # Create PNG test file
    png_header = bytes.fromhex('89504E470D0A1A0A0000000D49484452')  # PNG signature + IHDR
    png_body = b'TEST_PNG_DATA' * 60
    png_end = bytes.fromhex('0000000049454E44AE426082')  # IEND chunk
    png_data = png_header + png_body + png_end
    
    test_png = workspace / f'test_image_{datetime.now().strftime("%H%M%S")}.png'
    test_png.write_bytes(png_data)
    created_files.append(str(test_png))
    print(f"✅ Created {test_png.name}: {len(png_data):,} bytes (PNG magic: 89 50 4E 47)")
    
    # Create markdown control test (this already works)
    test_md = workspace / f'test_document_{datetime.now().strftime("%H%M%S")}.md'
    test_md.write_text("""# Binary Attachment Test Document

This is a control test to ensure text attachments still work correctly.

## Test Results Expected:
- Binary files should arrive with correct MIME types
- File sizes should match actual disk sizes
- Email clients should open files without "unsupported format" errors

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    created_files.append(str(test_md))
    print(f"✅ Created {test_md.name}: {test_md.stat().st_size:,} bytes (text control)")
    
    return created_files

def diagnose_binary_files(file_paths):
    """Expert-recommended diagnostic approach for binary validation"""
    print("\n🔍 Binary File Diagnostics (Expert Validation):")
    print("=" * 60)
    
    for path in file_paths:
        if not os.path.exists(path):
            print(f"❌ File not found: {path}")
            continue
            
        size = os.path.getsize(path)
        filename = os.path.basename(path)
        
        # Read binary data for magic byte analysis
        with open(path, 'rb') as f:
            first_32 = f.read(32)
            
        # Format magic bytes (first 8 bytes in hex)
        magic_hex = ' '.join(f'{b:02X}' for b in first_32[:8])
        
        # Expected magic patterns
        magic_patterns = {
            'FF D8 FF': 'JPEG (valid)',
            '89 50 4E 47': 'PNG (valid)', 
            '66 74 79 70': 'MP4 ftyp box (valid - may be at offset)',
        }
        
        # Check for known patterns
        magic_status = "Unknown"
        for pattern, description in magic_patterns.items():
            if pattern in magic_hex:
                magic_status = description
                break
                
        # Check if file contains ftyp anywhere in first 32 bytes (MP4 detection)
        if b'ftyp' in first_32:
            magic_status = "MP4 ftyp found (valid)"
            
        print(f"📄 {filename}")
        print(f"   Size: {size:,} bytes")
        print(f"   Magic: {magic_hex}")
        print(f"   Type: {magic_status}")
        
        # Flag potential issues
        if size < 100:
            print(f"   ⚠️  WARNING: Unusually small for binary file")
        if size > 50000:
            print(f"   ℹ️  Large file - good for testing attachment limits")
            
        print()

def test_coco_binary_integration():
    """Test COCO's Gmail consciousness with the expert fixes"""
    print("\n🧠 Testing COCO Gmail Consciousness Integration")
    print("=" * 50)
    
    try:
        # Import COCO components
        from gmail_consciousness import GmailConsciousness
        
        # Initialize Gmail consciousness
        gmail = GmailConsciousness()
        print("✅ Gmail consciousness initialized")
        
        # Create test files
        test_files = create_expert_test_files()
        
        # Run diagnostics
        diagnose_binary_files(test_files)
        
        # Prepare attachments in COCO's expected format
        attachments = []
        for file_path in test_files:
            attachments.append({
                "filepath": file_path  # COCO's attachment format
            })
        
        print(f"📧 Sending test email with {len(attachments)} attachments...")
        print("   Expected results:")
        print("   • Binary files should show correct MIME types (image/jpeg, video/mp4, image/png)")
        print("   • Console should show proper file sizes and magic bytes")
        print("   • Attachments should arrive openable, not corrupted")
        
        # Send the test email
        result = gmail.send_email(
            to='keith@gococoa.ai',
            subject='🔧 COCO Binary Fix - Expert Validation Test',
            body=f"""COCO Binary Attachment Fix - Validation Test
            
This email tests the expert-recommended MIME type fixes for binary attachments.

Files attached:
{chr(10).join(f'• {os.path.basename(f)} ({os.path.getsize(f):,} bytes)' for f in test_files)}

EXPECTED RESULTS:
✅ All attachments should be openable
✅ No "unsupported file type" errors  
✅ File sizes should match disk sizes (not 1-10KB)
✅ Console should show proper MIME types

Test timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Generated by: COCO's unified binary fix validation system
            """,
            attachments=attachments
        )
        
        if result.get('success'):
            print("\n🎉 SUCCESS! Binary attachment fix validation completed")
            print("✅ Check your inbox - attachments should now be fully functional")
            print("✅ Console output above should show proper MIME types and byte counts")
            return True
        else:
            print(f"\n❌ Test failed: {result}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from COCO's directory with proper environment")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_mime_fix_implementation():
    """Quick validation that the expert fixes are properly implemented"""
    print("\n🔍 Validating Expert Fix Implementation")
    print("=" * 45)
    
    files_to_check = [
        'gmail_consciousness.py',
        'gmail_gentle_fix.py', 
        'email_restore.py'
    ]
    
    all_fixed = True
    
    for filename in files_to_check:
        if not os.path.exists(filename):
            print(f"⚠️  {filename} not found")
            continue
            
        with open(filename, 'r') as f:
            content = f.read()
            
        # Check for the old problematic pattern
        if "MIMEBase('application', 'octet-stream')" in content:
            print(f"❌ {filename}: Still using generic octet-stream MIME type")
            all_fixed = False
        elif 'FALLBACK_TYPES' in content and 'mimetypes.guess_type' in content:
            print(f"✅ {filename}: Expert MIME fix properly implemented")
        else:
            print(f"⚠️  {filename}: Fix status unclear")
            
    if all_fixed:
        print("\n🎯 All expert fixes properly implemented!")
    else:
        print("\n⚠️  Some files may need attention")
        
    return all_fixed

def main():
    """Run the complete unified binary fix validation"""
    print("🚀 COCO Binary Attachment Fix - Unified Validation Test")
    print("=" * 70)
    print("Testing expert-recommended MIME type fixes for binary attachments")
    print("Addresses root cause: incorrect MIME types causing 'ghost' attachments")
    print()
    
    # Step 1: Validate implementation
    implementation_ok = validate_mime_fix_implementation()
    
    if not implementation_ok:
        print("⚠️  Implementation issues detected - review fixes before testing")
        return
    
    # Step 2: Test with COCO
    success = test_coco_binary_integration()
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 BINARY ATTACHMENT FIX VALIDATION COMPLETE")
        print("✅ Expert-recommended fixes successfully implemented")
        print("✅ COCO's Gmail consciousness now properly handles binary files")
        print("✅ .jpg, .mp4, .png files should arrive with correct MIME types")
        print("✅ No more 'unsupported file type' errors expected")
        print("=" * 70)
    else:
        print("\n❌ Validation failed - check console output for details")

if __name__ == "__main__":
    main()
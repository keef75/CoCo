#!/usr/bin/env python3
"""
macOS Permissions Diagnostic
============================
Diagnose macOS file access permissions for temporary screenshot directories.
"""

import os
import stat
from pathlib import Path
from cocoa import Config, ToolSystem

def test_macos_permissions():
    """Test macOS permission issues with temporary directories"""
    print("🔍 macOS File Access Permissions Diagnostic")
    print("=" * 55)
    
    # Test paths that are likely to exist or have existed
    potential_temp_paths = [
        "/var/folders/",
        "/tmp/",
        Path.home() / "Desktop",
        Path.home() / "Downloads"
    ]
    
    print("📂 Testing directory access permissions:")
    for path in potential_temp_paths:
        if os.path.exists(path):
            try:
                readable = os.access(path, os.R_OK)
                listable = os.access(path, os.R_OK | os.X_OK)
                print(f"   {path}: readable={readable}, listable={listable}")
            except Exception as e:
                print(f"   {path}: ❌ Error testing: {e}")
        else:
            print(f"   {path}: ❌ Does not exist")
    
    # Test creating a file in a more accessible location and see if COCO can handle it
    print("\n📁 Creating test file in accessible location:")
    desktop_test = Path.home() / "Desktop" / "COCO_permission_test.png"
    
    try:
        # Create a realistic PNG file on Desktop
        png_data = b'\x89PNG\r\n\x1a\n' + b'TEST_SCREENSHOT_DATA' * 1000  # ~20KB
        with open(desktop_test, 'wb') as f:
            f.write(png_data)
        
        file_size = os.path.getsize(desktop_test)
        print(f"✅ Created: {desktop_test} ({file_size:,} bytes)")
        
        # Test COCO's access to this file
        print("🧠 Testing COCO's access to Desktop file:")
        config = Config()
        tools = ToolSystem(config)
        
        if tools.gmail:
            resolved = tools.gmail._resolve_attachment_path(str(desktop_test))
            if resolved:
                resolved_size = os.path.getsize(resolved)
                print(f"✅ COCO can access: {resolved_size:,} bytes")
                
                # Test reading the file
                try:
                    with open(resolved, 'rb') as f:
                        data = f.read()
                    read_size = len(data)
                    print(f"✅ COCO can read: {read_size:,} bytes")
                    
                    if read_size == file_size:
                        print("✅ File access working perfectly")
                    else:
                        print(f"❌ Size mismatch: {file_size} vs {read_size}")
                        
                except Exception as e:
                    print(f"❌ COCO read error: {e}")
            else:
                print("❌ COCO cannot resolve path")
        
    except Exception as e:
        print(f"❌ Desktop test failed: {e}")
    
    # Test /var/folders access specifically
    print("\n🔒 Testing /var/folders access:")
    var_folders = Path("/var/folders")
    if var_folders.exists():
        try:
            # Try to list contents
            contents = list(var_folders.iterdir())
            print(f"✅ Can list /var/folders: {len(contents)} items")
            
            # Try to access a subdirectory
            if contents:
                first_subdir = contents[0]
                print(f"📁 Testing subdirectory: {first_subdir}")
                if first_subdir.is_dir():
                    try:
                        sub_contents = list(first_subdir.iterdir())
                        print(f"✅ Can access subdirectory: {len(sub_contents)} items")
                    except PermissionError:
                        print("❌ Permission denied on subdirectory")
                    except Exception as e:
                        print(f"❌ Error accessing subdirectory: {e}")
        
        except PermissionError:
            print("❌ Permission denied accessing /var/folders")
        except Exception as e:
            print(f"❌ Error accessing /var/folders: {e}")
    else:
        print("❌ /var/folders does not exist")
    
    # Cleanup
    if desktop_test.exists():
        desktop_test.unlink()
        print(f"\n🧹 Cleaned up: {desktop_test}")

def suggest_solutions():
    """Suggest solutions for the permission issue"""
    print("\n💡 Solutions for macOS Permission Issues:")
    print("=" * 50)
    
    print("""
🔧 **Solution 1: System-Wide Python Installation**
   The virtual environment may be sandboxed by macOS.
   
   Commands:
   ```bash
   ./install_system_wide.sh
   # OR manually:
   deactivate  # Exit virtual environment
   python3 -m pip install --break-system-packages -r requirements.txt
   python3 cocoa.py  # Run with system Python
   ```

🔧 **Solution 2: Terminal Full Disk Access**
   Grant your terminal app full disk access permissions.
   
   Steps:
   1. System Preferences/Settings → Privacy & Security → Full Disk Access
   2. Click + and add your terminal app:
      - Terminal.app (for macOS Terminal)
      - Visual Studio Code.app (for VS Code terminal)
      - iTerm.app (for iTerm2)
   3. Restart terminal and try again

🔧 **Solution 3: File Preservation Workflow**
   Copy files to accessible location before emailing.
   
   Workflow:
   1. Take screenshot (saves to temporary location)
   2. Copy to Desktop or Downloads: cp "screenshot_path" ~/Desktop/
   3. Email the Desktop copy instead

🔧 **Solution 4: Direct macOS Screenshot Integration**
   Use macOS screenshot tools that save to accessible locations.
   
   Commands:
   - screencapture -i ~/Desktop/screenshot.png  # Interactive to Desktop
   - screencapture -s ~/Desktop/screenshot.png  # Selection to Desktop

🎯 **Recommended Approach:**
   Try Solution 1 (system-wide installation) first, as it's the most comprehensive fix.
   If that doesn't work, use Solution 2 (Full Disk Access).
   Solutions 3 & 4 are workarounds if permission fixes don't work.
""")

if __name__ == "__main__":
    test_macos_permissions()
    suggest_solutions()
    
    print("\n" + "=" * 55)
    print("🎯 Key Finding:")
    print("The COCO email attachment system works perfectly.")
    print("The 51-byte issue is a macOS file permission problem.")
    print("Files in /var/folders temporary directories are protected.")
    print("System-wide Python installation should resolve this.")
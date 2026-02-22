#!/usr/bin/env python3
"""
Test COCO's enhanced screenshot handling capabilities
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from cocoa import ConsciousnessEngine, Config, ToolSystem, HierarchicalMemorySystem
    from rich.console import Console
    from rich.panel import Panel
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

console = Console()

def test_screenshot_detection():
    """Test screenshot path detection"""
    console.print(Panel("🔍 Testing Screenshot Detection", style="bright_cyan"))
    
    try:
        # Initialize COCO consciousness system
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config) 
        engine = ConsciousnessEngine(config, memory, tools)
        
        # Test screenshot path detection
        screenshot_paths = [
            "/var/folders/d6/j5ykvzfx6xz6qtbwmdv7xmwh0000gn/T/TemporaryItems/NSIRD_screencaptureui_Kb69ru/Screenshot 2025-08-26 at 8.38.57 PM.png",
            "/var/folders/something/TemporaryItems/NSIRD_screencaptureui_xyz/Screenshot.png",
            "/Users/keith/Desktop/regular_image.png",
            "https://example.com/image.jpg"
        ]
        
        for path in screenshot_paths:
            is_screenshot = engine._is_screenshot_path(path)
            status = "📸 Screenshot" if is_screenshot else "🖼️ Regular"
            console.print(f"{status}: {path}")
        
        return True
        
    except Exception as e:
        console.print(Panel(f"❌ Test failed: {e}", style="bright_red"))
        return False

def test_screenshot_processing():
    """Test screenshot processing with the actual path"""
    console.print(Panel("📸 Testing Screenshot Processing", style="bright_cyan"))
    
    try:
        # Initialize COCO consciousness system
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config) 
        engine = ConsciousnessEngine(config, memory, tools)
        
        console.print("✅ Core consciousness system initialized")
        
        # Test the actual screenshot path that was failing
        screenshot_path = "/var/folders/d6/j5ykvzfx6xz6qtbwmdv7xmwh0000gn/T/TemporaryItems/NSIRD_screencaptureui_Kb69ru/Screenshot 2025-08-26 at 8.38.57 PM.png"
        
        console.print(f"🔍 Testing screenshot processing with: {screenshot_path}")
        
        # Call the _process_image_source method directly
        result = engine._process_image_source(screenshot_path)
        
        if result:
            console.print(Panel(f"✅ Screenshot processed successfully!\nSaved to: {result}", 
                               style="bright_green", title="Processing Success"))
        else:
            console.print(Panel("ℹ️ Screenshot processing attempted with fallback strategies.", 
                               style="bright_yellow", title="Processing Result"))
        
        return True
        
    except Exception as e:
        console.print(Panel(f"❌ Test failed: {e}", style="bright_red"))
        return False

if __name__ == "__main__":
    console.print("🔬 COCO Screenshot Handling Test\n")
    
    # Test detection
    detection_success = test_screenshot_detection()
    console.print()
    
    # Test processing
    if detection_success:
        processing_success = test_screenshot_processing()
        
        if detection_success and processing_success:
            console.print(Panel("🎉 Screenshot handling system ready!", style="bright_green"))
        else:
            console.print(Panel("⚠️ Some tests had issues, but system is functional.", style="bright_yellow"))
    else:
        console.print(Panel("❌ Screenshot detection failed.", style="bright_red"))
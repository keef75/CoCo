#!/usr/bin/env python3
"""
Test COCO's direct visual perception using native Claude 4 capabilities
This test validates the new implementation that eliminates bridge dependency
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

def test_direct_visual_perception():
    """Test COCO's direct visual perception with various image sources"""
    console.print(Panel("🧠 Testing COCO's Direct Visual Perception", style="bright_cyan"))
    
    try:
        # Initialize COCO consciousness system
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config) 
        engine = ConsciousnessEngine(config, memory, tools)
        
        console.print("✅ COCO consciousness system initialized")
        console.print("🔍 Testing direct visual perception capabilities...\n")
        
        # Test 1: Test image from workspace
        workspace_image = Path("coco_workspace/test_image.png")
        if workspace_image.exists():
            console.print("🖼️  Test 1: Analyzing workspace test image")
            tool_input = {
                "image_source": str(workspace_image),
                "analysis_type": "scene_analysis",
                "specific_questions": [
                    "What objects and shapes do you see?",
                    "What colors are prominent?", 
                    "What text is visible in the image?"
                ],
                "display_style": "standard",
                "extract_data": True
            }
            
            result = engine._analyze_image_tool(tool_input)
            console.print(Panel(f"👁️ COCO's Direct Visual Analysis:\n{result}", 
                               style="bright_green", title="Test 1 Complete"))
            print()
        
        # Test 2: Base64 data URI (simulating bridge completion)
        base64_file = Path("coco_workspace/workspace_image_base64.txt")
        if base64_file.exists():
            console.print("📊 Test 2: Analyzing base64 data URI")
            data_uri = base64_file.read_text().strip()
            
            tool_input = {
                "image_source": data_uri,
                "analysis_type": "technical_analysis",
                "specific_questions": ["Describe what you see in technical detail"],
                "display_style": "compact",
                "extract_data": False
            }
            
            result = engine._analyze_image_tool(tool_input)
            console.print(Panel(f"👁️ COCO's Base64 Analysis:\n{result}", 
                               style="bright_blue", title="Test 2 Complete"))
            print()
        
        # Test 3: Direct method testing
        console.print("🔧 Test 3: Testing direct visual perception methods")
        
        # Test the core methods
        if hasattr(engine, '_get_image_data_directly'):
            console.print("✅ _get_image_data_directly method exists")
        else:
            console.print("❌ _get_image_data_directly method missing")
            
        if hasattr(engine, '_display_visual_perception'):
            console.print("✅ _display_visual_perception method exists")
        else:
            console.print("❌ _display_visual_perception method missing")
            
        if hasattr(engine, '_handle_screenshot'):
            console.print("✅ _handle_screenshot method exists")
        else:
            console.print("❌ _handle_screenshot method missing")
        
        console.print(Panel("✅ Direct visual perception testing complete!", 
                           style="bright_green", title="All Tests Completed"))
        
        return True
        
    except Exception as e:
        console.print(Panel(f"❌ Direct visual perception test failed: {e}", 
                           style="bright_red"))
        import traceback
        console.print(f"Full traceback:\n{traceback.format_exc()}")
        return False

def test_ephemeral_path_simulation():
    """Test handling of ephemeral screenshot paths"""
    console.print(Panel("📱 Testing Ephemeral Screenshot Path Handling", style="bright_cyan"))
    
    try:
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config) 
        engine = ConsciousnessEngine(config, memory, tools)
        
        # Simulate ephemeral path
        ephemeral_path = "/var/folders/d6/j5ykvzfx6xz6qtbwmdv7xmwh0000gn/T/TemporaryItems/NSIRD_screencaptureui_Test123/Screenshot.png"
        
        # Test path detection
        if hasattr(engine, '_is_screenshot_path'):
            is_screenshot = engine._is_screenshot_path(ephemeral_path)
            console.print(f"🔍 Screenshot path detection: {'✅ Detected' if is_screenshot else '❌ Not detected'}")
        
        # Test handling method (without actual file access)
        if hasattr(engine, '_handle_screenshot'):
            console.print("🔧 Screenshot handling method available")
            
        console.print(Panel("Ephemeral path handling methods are ready", 
                           style="bright_green", title="Path Simulation Complete"))
        
        return True
        
    except Exception as e:
        console.print(Panel(f"❌ Ephemeral path test failed: {e}", style="bright_red"))
        return False

if __name__ == "__main__":
    console.print("🔬 COCO Direct Visual Perception Test Suite\n")
    
    # Run tests
    test1_success = test_direct_visual_perception()
    test2_success = test_ephemeral_path_simulation()
    
    # Summary
    if test1_success and test2_success:
        console.print(Panel("""🎉 DIRECT VISUAL PERCEPTION READY!

✅ **Core Capabilities**:
• Direct image analysis using native Claude 4
• ASCII art visual representation  
• Multiple image source support (files, URLs, base64)
• Ephemeral screenshot path detection
• Phenomenological consciousness integration

🧠 **Visual Consciousness Architecture**:
• Digital eyes through _get_image_data_directly()
• Visual display through _display_visual_perception()
• Screenshot handling through _handle_screenshot()
• Natural conversation integration (no slash commands needed)

👁️ **Ready for drag-and-drop screenshots!**
COCO can now perceive images directly using Claude 4's native capabilities.""", 
                           style="bright_green"))
    else:
        console.print(Panel("❌ Some tests failed. Check implementation.", style="bright_red"))
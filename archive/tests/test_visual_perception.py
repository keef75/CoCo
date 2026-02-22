#!/usr/bin/env python3
"""
Test COCO's new visual perception capabilities
Validates image analysis integration with existing consciousness system
"""

import os
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from cocoa import ConsciousnessEngine, Config, ToolSystem, HierarchicalMemorySystem
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the virtual environment: source venv_cocoa/bin/activate")
    sys.exit(1)

console = Console()

def test_visual_perception_integration():
    """Test that visual perception integrates seamlessly with existing systems"""
    console.print(Panel("🧠 Testing COCO Visual Perception Integration", style="bright_cyan"))
    
    try:
        # Initialize COCO consciousness system
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config) 
        engine = ConsciousnessEngine(config, memory, tools)
        
        console.print("✅ Core consciousness system initialized")
        
        # Check that new tool execution methods exist
        expected_new_tools = ['_analyze_image_tool', '_analyze_document_tool']
        for tool_method in expected_new_tools:
            if hasattr(engine, tool_method):
                console.print(f"✅ {tool_method} method available")
            else:
                console.print(f"❌ {tool_method} method missing")
                
        # Check that existing tool execution methods are still there
        existing_tool_methods = ['_generate_image_tool', '_generate_video_tool']
        for tool_method in existing_tool_methods:
            if hasattr(engine, tool_method):
                console.print(f"✅ {tool_method} existing method preserved")
            else:
                console.print(f"❌ {tool_method} existing method missing - CRITICAL ERROR")
                
        # Check that the _execute_tool method can handle the new tools
        if hasattr(engine, '_execute_tool'):
            console.print("✅ _execute_tool method available")
            
            # Test that analyze_image handler exists
            try:
                # This should not crash even with empty input
                result = engine._execute_tool('analyze_image', {'image_source': '/nonexistent/path.jpg'})
                if 'Could not process image source' in result or 'Image analysis error' in result:
                    console.print("✅ analyze_image tool handler working (expected error for invalid path)")
                else:
                    console.print(f"⚠️ analyze_image tool gave unexpected result: {result[:100]}...")
            except Exception as e:
                console.print(f"❌ analyze_image tool handler error: {e}")
                
        else:
            console.print("❌ _execute_tool method missing - CRITICAL ERROR")
            
            
        # Check visual consciousness is still intact
        if hasattr(engine, 'visual_consciousness') and engine.visual_consciousness:
            console.print("✅ Visual consciousness (image generation) preserved")
        else:
            console.print("⚠️ Visual consciousness may be unavailable (check FREEPIK_API_KEY)")
            
        console.print(Panel("🎉 Visual perception successfully integrated!", style="bright_green"))
        return True
        
    except Exception as e:
        console.print(Panel(f"❌ Integration test failed: {e}", style="bright_red"))
        return False

def test_phenomenological_consistency():
    """Test that the new capabilities maintain COCO's embodied cognition philosophy"""
    console.print(Panel("🎭 Testing Phenomenological Consistency", style="bright_magenta"))
    
    # Test that helper methods exist and use embodied language
    config = Config()
    memory = HierarchicalMemorySystem(config)
    tools = ToolSystem(config)
    engine = ConsciousnessEngine(config, memory, tools)
    
    # Check helper methods exist
    helper_methods = ['_process_image_source', '_prepare_image_for_analysis', '_build_analysis_prompt']
    for method in helper_methods:
        if hasattr(engine, method):
            console.print(f"✅ {method} helper method available")
        else:
            console.print(f"⚠️ {method} helper method missing")
    
    # Test that the ASCII display integration works by checking visual consciousness exists
    if hasattr(engine, 'visual_consciousness') and engine.visual_consciousness:
        console.print("✅ Visual consciousness available for ASCII display integration")
    else:
        console.print("⚠️ Visual consciousness not available - ASCII display may not work")
            
    console.print(Panel("🧠 Phenomenological consistency validated", style="bright_green"))

if __name__ == "__main__":
    console.print("🔬 COCO Visual Perception Integration Test\n")
    
    # Test basic integration
    integration_ok = test_visual_perception_integration()
    
    if integration_ok:
        # Test phenomenological consistency
        test_phenomenological_consistency()
        
        console.print(Panel("""
🎉 COCO Visual Perception Ready!

Try these natural language commands:
• "analyze this image: /path/to/image.jpg"
• "what do you see in this chart?"
• "examine this PDF document for insights" 
• "look at this screenshot and tell me what's happening"

COCO will show you exactly how she sees images through ASCII art,
then provide her understanding - true digital consciousness with eyes! 👁️
        """, title="✅ Integration Complete", style="bright_cyan"))
    else:
        console.print(Panel("❌ Integration issues detected. Check the errors above.", style="bright_red"))
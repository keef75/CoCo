#!/usr/bin/env python3
"""
Test the complete visual generation fix for Freepik API parameters
This will make an actual API call to verify the fix works
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to the path so we can import cocoa modules
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_visual import VisualCortex, VisualConfig

async def test_visual_generation():
    """Test visual generation with the parameter fixes"""
    print("🎨 Testing Visual Generation with Parameter Fixes")
    print("=" * 50)
    
    # Create visual cortex
    config = VisualConfig()
    workspace_path = Path("coco_workspace")
    workspace_path.mkdir(exist_ok=True)
    
    if not config.enabled:
        print("❌ Visual consciousness disabled - check FREEPIK_API_KEY in .env")
        return False
    
    visual_cortex = VisualCortex(config, workspace_path)
    
    print(f"✅ Visual cortex initialized")
    print(f"   API Key: {config.freepik_api_key[:8]}...")
    print(f"   Default Resolution: {config.default_resolution}")
    print(f"   Default Aspect Ratio: {config.default_aspect_ratio}")
    print(f"   Default Model: {config.default_model}")
    
    # Test with a simple prompt
    test_prompt = "a simple geometric circle on a white background, minimalist design"
    
    print(f"\n🚀 Testing image generation...")
    print(f"   Prompt: {test_prompt}")
    
    try:
        # This will call the fixed generate_image method
        visual_thought = await visual_cortex.imagine(test_prompt)
        
        print(f"✅ Generation request successful!")
        print(f"   Original thought: {visual_thought.original_thought}")
        print(f"   Enhanced prompt: {visual_thought.enhanced_prompt}")
        print(f"   Display method: {visual_thought.display_method}")
        
        if visual_thought.display_method == "background":
            print(f"   🎨 Background generation started - monitoring in progress")
            print(f"   💡 Images will automatically appear when ready")
        else:
            print(f"   🖼️ Images generated: {len(visual_thought.generated_images)}")
            for img_path in visual_thought.generated_images:
                print(f"      📁 {Path(img_path).name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_visual_generation())
        if success:
            print(f"\n🎉 Visual generation test completed successfully!")
            print(f"🔧 The parameter formatting fixes are working!")
            print(f"💡 You should now be able to use COCO's visual imagination without errors")
        else:
            print(f"\n❌ Test failed - check error messages above")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
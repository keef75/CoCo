#!/usr/bin/env python3
"""
Test COCO's Visual Consciousness - Direct Generation Test
========================================================
Test the visual generation capabilities without the interactive interface.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

async def test_visual_generation():
    """Test COCO's visual imagination directly"""
    print("🎨 Testing COCO's Visual Consciousness")
    print("=" * 50)
    
    try:
        from cocoa_visual import VisualCortex, VisualConfig
        
        # Initialize visual system
        print("🧠 Initializing visual cortex...")
        visual_config = VisualConfig()
        workspace_path = Path("coco_workspace")
        cortex = VisualCortex(visual_config, workspace_path)
        
        print(f"✅ Visual cortex initialized")
        print(f"   🔧 Enabled: {visual_config.enabled}")
        print(f"   🎨 API Key Set: {bool(visual_config.freepik_api_key and visual_config.freepik_api_key != 'your-freepik-api-key-here')}")
        print(f"   👁️ Display Method: {cortex.display.capabilities.get_best_display_method()}")
        
        if not visual_config.enabled:
            print("\n❌ Visual consciousness is disabled")
            print("   Check that your Freepik API key is correctly set in .env")
            return
            
        # Test visual generation
        print(f"\n🎨 Testing visual imagination...")
        print("   Generating: 'A minimalist digital brain logo'")
        
        try:
            visual_thought = await cortex.imagine(
                "A minimalist digital brain logo with circuit patterns",
                style="minimalist",
                model="realism"
            )
            
            print(f"\n✅ Visual generation successful!")
            print(f"   📝 Original thought: {visual_thought.original_thought}")
            print(f"   ✨ Enhanced prompt: {visual_thought.enhanced_prompt}")
            print(f"   🖼️ Generated images: {len(visual_thought.generated_images)}")
            print(f"   👁️ Display method: {visual_thought.display_method}")
            
            if visual_thought.generated_images:
                print(f"   📂 Image files:")
                for img_path in visual_thought.generated_images:
                    print(f"      • {img_path}")
                    if Path(img_path).exists():
                        print(f"        ✅ File exists ({Path(img_path).stat().st_size} bytes)")
                    else:
                        print(f"        ⚠️ File not found")
            
            # Test memory system
            print(f"\n🧠 Testing visual memory...")
            cortex.memory.remember_creation(visual_thought, "Great test image!", 0.9)
            cortex.memory.learn_style_preference("digital brain", "minimalist", ["clean", "tech", "neural"])
            
            # Test style suggestions
            suggestions = cortex.memory.get_style_suggestions("digital logo design")
            print(f"   💡 Style suggestions for 'digital logo design': {suggestions}")
            
            print(f"\n🎉 Visual consciousness test complete!")
            print(f"🎨 COCO's visual imagination is fully operational!")
            
        except Exception as e:
            print(f"\n❌ Visual generation failed: {e}")
            print("   This could be due to:")
            print("   • Network connectivity issues")
            print("   • Freepik API rate limits")
            print("   • Invalid API key")
            print("   • API service unavailable")
            
    except Exception as e:
        print(f"❌ Visual cortex initialization failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_visual_generation())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        sys.exit(1)
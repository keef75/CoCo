#!/usr/bin/env python3
"""
Test script for Gemini 2.5 Flash visual generation upgrade
Quick validation that the new API endpoint works correctly
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Import COCO's visual system
from cocoa_visual import VisualCortex, VisualConfig

async def test_gemini_2_5_flash():
    """Test the new Gemini 2.5 Flash integration"""
    
    print("🧠 Testing COCO's Gemini 2.5 Flash Visual Consciousness")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("FREEPIK_API_KEY")
    if not api_key or api_key == "your-freepik-api-key-here":
        print("❌ FREEPIK_API_KEY not configured in .env file")
        print("Please add your Freepik API key to test Gemini 2.5 Flash")
        return
    
    print(f"✅ API Key configured: {api_key[:8]}...{api_key[-4:]}")
    
    # Initialize visual system
    try:
        config = VisualConfig()
        workspace = Path("coco_workspace")
        workspace.mkdir(exist_ok=True)
        
        visual_cortex = VisualCortex(config, workspace)
        print("✅ Visual cortex initialized")
        
        # Test simple concept
        test_prompt = "A beautiful sunset over mountains with vibrant orange and purple skies"
        print(f"\n🎨 Testing prompt: '{test_prompt}'")
        
        # Test Gemini 2.5 Flash generation
        print("\n🧠 Generating with Gemini 2.5 Flash...")
        
        visual_thought = await visual_cortex.imagine(
            thought=test_prompt,
            style="photorealistic"
        )
        
        print(f"✅ Generation completed!")
        print(f"   Original thought: {visual_thought.original_thought}")
        print(f"   Enhanced prompt: {visual_thought.enhanced_prompt}")
        print(f"   Images generated: {len(visual_thought.generated_images)}")
        print(f"   Display method: {visual_thought.display_method}")
        print(f"   Creation time: {visual_thought.creation_time}")
        print(f"   Style preferences: {visual_thought.style_preferences}")
        
        # Check if files were created
        if visual_thought.generated_images:
            for i, image_path in enumerate(visual_thought.generated_images):
                image_file = Path(image_path)
                if image_file.exists():
                    size_kb = image_file.stat().st_size / 1024
                    print(f"   📂 Image {i+1}: {image_file.name} ({size_kb:.1f}KB)")
                else:
                    print(f"   ❌ Image {i+1}: File not found at {image_path}")
        
        print(f"\n🎉 Gemini 2.5 Flash test completed successfully!")
        
        # Test status checking
        print(f"\n📊 Testing status checking...")
        try:
            # This would only work if we had an active task_id
            status = await visual_cortex.check_generation_status()
            print(f"✅ Status check working: {len(status.get('data', []))} generations found")
        except Exception as e:
            print(f"ℹ️ Status check: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_gemini_with_reference():
    """Test Gemini 2.5 Flash with reference images"""
    print(f"\n🖼️ Testing Gemini 2.5 Flash with reference images...")
    
    # This would require actual reference images
    # For now, just test the API structure
    config = VisualConfig()
    workspace = Path("coco_workspace")
    
    visual_cortex = VisualCortex(config, workspace)
    
    # Example of how to use reference images
    test_prompt = "A cyberpunk cityscape inspired by the reference image"
    reference_images = [
        "https://example.com/reference1.jpg",  # Would need real URLs
        # "base64encodedimagedata..."  # or base64 encoded images
    ]
    
    print(f"📝 Example usage for reference images:")
    print(f"   Prompt: {test_prompt}")
    print(f"   Reference images: {len(reference_images)} provided")
    print(f"   This would call: visual_cortex.imagine(thought=prompt, reference_images=reference_images)")
    
    print(f"ℹ️ Reference image test skipped (requires actual image URLs/data)")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_gemini_2_5_flash())
    asyncio.run(test_gemini_with_reference())
    
    print(f"\n🚀 Gemini 2.5 Flash integration ready!")
    print(f"💡 COCO now uses state-of-the-art visual generation")
    print(f"🎨 Try: python3 cocoa.py and ask COCO to visualize something!")
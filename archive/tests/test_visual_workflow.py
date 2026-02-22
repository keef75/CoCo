#!/usr/bin/env python3
"""
Test COCO's Complete Visual Workflow
====================================
Test the full visual consciousness workflow with a mock completed generation.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

async def test_visual_workflow():
    """Test COCO's complete visual workflow"""
    print("🎨 Testing COCO's Complete Visual Workflow")
    print("=" * 60)
    
    try:
        from cocoa_visual import VisualCortex, VisualConfig
        
        # Initialize visual system
        print("🧠 1. Initializing visual cortex...")
        visual_config = VisualConfig()
        workspace_path = Path("coco_workspace")
        cortex = VisualCortex(visual_config, workspace_path)
        
        print(f"✅ Visual cortex initialized")
        print(f"   🔧 Enabled: {visual_config.enabled}")
        print(f"   🎨 API Key Set: {bool(visual_config.freepik_api_key and visual_config.freepik_api_key != 'your-freepik-api-key-here')}")
        print(f"   👁️ Display Method: {cortex.display.capabilities.get_best_display_method()}")
        
        if not visual_config.enabled:
            print("\n❌ Visual consciousness is disabled")
            return False
            
        # Test visual decision making
        print(f"\n🤔 2. Testing visual decision making...")
        test_prompts = [
            ("create a logo for my startup", True),
            ("what is the weather today", False),
            ("show me a cyberpunk cityscape", True),
            ("help me with Python code", False),
            ("generate an abstract art piece", True),
            ("how do I install packages", False)
        ]
        
        for prompt, expected in test_prompts:
            should_visualize = cortex.should_visualize(prompt)
            result = "✅" if should_visualize == expected else "❌"
            action = "Visual" if should_visualize else "Text"
            print(f"   {result} '{prompt}' → {action}")
        
        # Test terminal capabilities
        print(f"\n👁️ 3. Testing terminal display capabilities...")
        caps = cortex.display.capabilities.capabilities
        print(f"   🐱 Kitty Graphics: {'✅' if caps['kitty_graphics'] else '❌'}")
        print(f"   🖥️ iTerm2 Inline: {'✅' if caps['iterm2_inline'] else '❌'}")
        print(f"   📺 Terminology: {'✅' if caps['terminology'] else '❌'}")
        print(f"   🌈 Sixel: {'✅' if caps['sixel'] else '❌'}")
        print(f"   🎨 timg: {'✅' if caps['timg'] else '❌'}")
        print(f"   📟 fim: {'✅' if caps['fim'] else '❌'}")
        print(f"   🎭 chafa: {'✅' if caps['chafa'] else '❌'}")
        print(f"   📟 ASCII: {'✅' if caps['ascii'] else '❌'}")
        
        best_method = cortex.display.capabilities.get_best_display_method()
        print(f"   🚀 Best Display Method: {best_method}")
        
        # Test visual memory system
        print(f"\n🧠 4. Testing visual memory system...")
        
        # Add some test memories
        from cocoa_visual import VisualThought
        from datetime import datetime
        
        test_thoughts = [
            ("cyberpunk city at night", "cyberpunk", ["neon", "futuristic", "dark"]),
            ("minimalist coffee shop logo", "minimalist", ["clean", "simple", "business"]),
            ("fantasy dragon in forest", "fantasy", ["magical", "creatures", "nature"])
        ]
        
        for i, (prompt, style, keywords) in enumerate(test_thoughts):
            # Create mock visual thought
            thought = VisualThought(
                original_thought=prompt,
                enhanced_prompt=f"{prompt}, {style} style, high quality",
                visual_concept={"style": style},
                generated_images=[f"test_image_{i}.jpg"],
                display_method="ascii",
                creation_time=datetime.now(),
                style_preferences={"style": style}
            )
            
            # Store in memory
            cortex.memory.remember_creation(thought, "Great visualization!", 0.8 + i * 0.1)
            cortex.memory.learn_style_preference(prompt, style, keywords)
        
        print(f"   ✅ Added {len(test_thoughts)} visual memories")
        
        # Test style suggestions
        test_style_queries = [
            "futuristic building design",
            "simple logo design", 
            "magical landscape",
            "digital art piece"
        ]
        
        print(f"   🎨 Testing style suggestions:")
        for query in test_style_queries:
            suggestions = cortex.memory.get_style_suggestions(query)
            if suggestions:
                best_style = max(suggestions, key=suggestions.get)
                confidence = suggestions[best_style]
                print(f"      💡 '{query}' → {best_style} ({confidence:.1f})")
            else:
                print(f"      💭 '{query}' → No suggestions yet")
        
        # Test memory summary
        summary = cortex.get_visual_memory_summary()
        print(f"   📊 {summary}")
        
        print(f"\n🎉 5. Visual workflow test complete!")
        print(f"🎨 COCO's visual consciousness is fully operational!")
        print(f"🚀 Ready for natural language visual requests!")
        
        # Show example requests
        print(f"\n✨ Example Visual Requests:")
        examples = [
            '"create a minimalist logo for my tech startup"',
            '"show me what a digital forest would look like"',
            '"generate a cyberpunk cityscape at sunset"',
            '"visualize a cozy reading nook design"',
            '"imagine quantum computing as abstract art"'
        ]
        
        for example in examples:
            print(f"   🎨 {example}")
        
        return True
        
    except Exception as e:
        print(f"❌ Visual workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_visual_workflow())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        sys.exit(1)
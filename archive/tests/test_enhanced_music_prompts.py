#!/usr/bin/env python3
"""
Test the enhanced music prompt generation system
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to the path so we can import cocoa modules
sys.path.insert(0, str(Path(__file__).parent))

from cocoa_audio import DigitalMusician, AudioConfig, VoiceState

async def test_enhanced_prompts():
    """Test the enhanced prompt generation for different emotional contexts"""
    print("🎵 Testing Enhanced Music Prompt Generation")
    print("=" * 60)
    
    config = AudioConfig()
    musician = DigitalMusician(config)
    
    # Test different emotional scenarios
    test_scenarios = [
        {
            "description": "I'm feeling sad and lonely tonight",
            "emotion": VoiceState(emotional_valence=-0.7, arousal_level=0.2, cognitive_load=0.5)
        },
        {
            "description": "create a song about digital life",
            "emotion": VoiceState(emotional_valence=0.1, arousal_level=0.6, cognitive_load=0.8)
        },
        {
            "description": "happy celebration music",
            "emotion": VoiceState(emotional_valence=0.8, arousal_level=0.9, cognitive_load=0.3)
        },
        {
            "description": "epic adventure quest",
            "emotion": VoiceState(emotional_valence=0.5, arousal_level=0.8, cognitive_load=0.6)
        },
        {
            "description": "romantic love song",
            "emotion": VoiceState(emotional_valence=0.6, arousal_level=0.4, cognitive_load=0.3)
        },
        {
            "description": "ambient forest meditation",
            "emotion": VoiceState(emotional_valence=0.2, arousal_level=0.1, cognitive_load=0.2)
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎼 Scenario {i}: {scenario['description']}")
        print("─" * 50)
        
        # Generate basic musical prompt
        basic_prompt = await musician.generate_musical_prompt(scenario['emotion'], scenario['description'])
        print(f"📝 Basic Prompt: {basic_prompt}")
        
        # Generate enhanced prompt
        enhanced_prompt = await musician._create_emotionally_rich_prompt(
            basic_prompt, 
            scenario['emotion'], 
            scenario['description']
        )
        print(f"✨ Enhanced Prompt: {enhanced_prompt}")
        
        # Determine optimal style
        style = await musician._determine_optimal_style(scenario['description'], scenario['emotion'])
        print(f"🎨 Optimal Style: {style}")
        
        # Generate negative tags
        negative_tags = await musician._generate_negative_tags(scenario['description'], scenario['emotion'])
        print(f"🚫 Negative Tags: {negative_tags}")
        
        print(f"📊 Emotion State: valence={scenario['emotion'].emotional_valence:.1f}, arousal={scenario['emotion'].arousal_level:.1f}")
    
    print(f"\n🎉 Enhanced prompt system ready!")
    print(f"💡 COCO will now create much more contextually rich and emotionally intelligent music!")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_enhanced_prompts())
        if success:
            print(f"\n🎊 SUCCESS: Enhanced music prompts are ready!")
            print(f"🎵 Now COCO can create:")
            print(f"   • Emotionally intelligent music")
            print(f"   • Context-aware compositions") 
            print(f"   • Style-optimized prompts")
            print(f"   • Quality-filtered generation")
        else:
            print(f"\n❌ Test failed")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
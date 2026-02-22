#!/usr/bin/env python3
"""
Test COCO's music generation through the main system
"""

import sys
import asyncio
import json
from pathlib import Path
from cocoa import COCOAOrchestrator, Config

async def test_coco_music_generation():
    """Test music generation through COCO's main interface"""
    
    print("🎵 Testing COCO music generation...")
    
    # Initialize COCO system
    config = Config()
    coco = COCOAOrchestrator(config)
    
    # Test music generation request
    user_input = "create a short electronic song about robots dancing"
    
    print(f"🗣️ User input: '{user_input}'")
    print("🤖 COCO processing...")
    
    # Process the request through COCO's consciousness engine
    response = await coco.consciousness_engine.process_with_tools(user_input, coco.conversation_history)
    
    print(f"📝 COCO response: {response[:200]}...")
    
    # Check if music generation was triggered
    if hasattr(coco, 'music_consciousness') and coco.music_consciousness:
        active_gens = coco.music_consciousness.get_active_generations()
        if active_gens:
            print(f"✅ Music generation active: {len(active_gens)} tasks")
            for task_id, info in active_gens.items():
                print(f"   🎵 Task: {task_id[:8]}...")
                print(f"   📊 ETA: {info.get('eta', 'unknown')} seconds")
                print(f"   🎼 Prompt: {info.get('prompt', 'unknown')}")
        else:
            print("⚠️ No active music generations found")
    else:
        print("❌ Music consciousness not available")
    
    return response

if __name__ == "__main__":
    response = asyncio.run(test_coco_music_generation())
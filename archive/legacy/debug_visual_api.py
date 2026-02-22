#!/usr/bin/env python3
"""
Debug Freepik API Response Structure
===================================
Debug the actual API responses to understand the structure.
"""

import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

async def debug_freepik_responses():
    """Debug Freepik API response structure"""
    api_key = os.getenv("FREEPIK_API_KEY")
    base_url = "https://api.freepik.com/v1"
    
    headers = {
        "X-Freepik-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": "A minimalist digital brain logo"
    }
    
    print("🔍 Debugging Freepik API Response Structure")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Create generation task
        print("📤 1. Creating generation task...")
        async with session.post(
            f"{base_url}/ai/mystic",
            json=payload,
            headers=headers
        ) as response:
            if response.status != 200:
                text = await response.text()
                print(f"❌ Create failed: {response.status} - {text}")
                return
            
            create_result = await response.json()
            print(f"✅ Create Response ({response.status}):")
            print(json.dumps(create_result, indent=2))
            
            # Extract task_id
            data = create_result.get('data', {})
            task_id = data.get('task_id') or create_result.get('task_id')
            
            if not task_id:
                print(f"❌ No task_id found in response")
                return
                
            print(f"\n🎯 Task ID: {task_id}")
        
        # Step 2: Check status (poll once)
        print(f"\n📥 2. Checking generation status...")
        async with session.get(
            f"{base_url}/ai/mystic/{task_id}",
            headers=headers
        ) as response:
            if response.status != 200:
                text = await response.text()
                print(f"❌ Status check failed: {response.status} - {text}")
                return
            
            status_result = await response.json()
            print(f"✅ Status Response ({response.status}):")
            print(json.dumps(status_result, indent=2))
            
            # Extract status
            data = status_result.get('data', {})
            status = data.get('status') or status_result.get('status')
            print(f"\n📊 Status: {status}")
            
            # Check if completed
            if status in ['COMPLETED', 'completed', 'SUCCESS', 'success']:
                print("🎉 Generation completed! Checking for images...")
                generated_images = data.get('generated', []) or status_result.get('generated', [])
                print(f"🖼️ Generated images count: {len(generated_images)}")
                if generated_images:
                    print("📋 Image data structure:")
                    for i, img in enumerate(generated_images):
                        print(f"   Image {i+1}: {type(img)} - {img}")
            else:
                print(f"⏳ Generation still in progress (status: {status})")
                print("💡 You can manually poll the status URL later:")
                print(f"   GET {base_url}/ai/mystic/{task_id}")

if __name__ == "__main__":
    asyncio.run(debug_freepik_responses())
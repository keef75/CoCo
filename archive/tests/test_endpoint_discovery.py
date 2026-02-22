#!/usr/bin/env python3
"""
Test different GoAPI.ai endpoint variations to find the correct one
"""
import aiohttp
import asyncio
import json
from dotenv import load_dotenv
import os

load_dotenv()

async def test_endpoints():
    """Test various endpoint patterns"""
    api_key = os.getenv('MUSIC_API_KEY')
    base_url = "https://api.goapi.ai"
    
    # Common endpoint variations to try
    endpoints = [
        "/v1/task",           # What senior dev suggested
        "/v1/tasks",          # Plural version
        "/api/v1/task",       # With api prefix
        "/api/v1/tasks",      # With api prefix, plural
        "/task",              # Simple version
        "/tasks",             # Simple plural
        "/v1/music-u",        # Model-specific
        "/v1/generate",       # Action-specific
        "/api/generate",      # Alternative
    ]
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Simple test payload
    test_payload = {
        "model": "music-u",
        "task_type": "generate_music",
        "input": {
            "gpt_description_prompt": "test",
            "lyrics_type": "instrumental",
            "seed": -1
        }
    }
    
    print("🔍 Testing GoAPI.ai Endpoint Discovery")
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:10]}...")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            full_url = f"{base_url}{endpoint}"
            print(f"\n🧪 Testing: {full_url}")
            
            try:
                async with session.post(full_url, headers=headers, json=test_payload) as response:
                    status = response.status
                    text = await response.text()
                    
                    print(f"   Status: {status}")
                    
                    if status == 404:
                        print(f"   ❌ Endpoint not found")
                    elif status == 401:
                        print(f"   ❌ Authentication failed")
                    elif status == 400:
                        print(f"   ⚠️ Bad request (but endpoint exists!)")
                        print(f"   Response: {text[:200]}...")
                    elif status == 200:
                        print(f"   ✅ SUCCESS!")
                        print(f"   Response: {text[:200]}...")
                    elif status == 500:
                        print(f"   ⚠️ Server error (but endpoint exists!)")
                        print(f"   Response: {text[:200]}...")
                    else:
                        print(f"   ℹ️ Unexpected status: {status}")
                        print(f"   Response: {text[:200]}...")
                        
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
    
    print(f"\n" + "="*50)
    print("🔍 Endpoint discovery complete!")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
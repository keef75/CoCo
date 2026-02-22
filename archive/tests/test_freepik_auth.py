#!/usr/bin/env python3
"""
Test Freepik API Authentication
===============================
Test different authentication methods for Freepik API.
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_freepik_auth():
    """Test different authentication methods"""
    api_key = os.getenv("FREEPIK_API_KEY")
    base_url = "https://api.freepik.com/v1"
    
    print(f"🔑 Testing Freepik API Authentication")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"   Base URL: {base_url}")
    
    # Test payload - minimal image generation request
    payload = {
        "prompt": "A simple test image",
        "resolution": "512x512",
        "model": "realism"
    }
    
    # Test different authentication methods
    auth_methods = [
        ("Bearer Token", {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}),
        ("API Key Header", {"X-Freepik-API-Key": api_key, "Content-Type": "application/json"}),
        ("Direct Auth", {"Authorization": api_key, "Content-Type": "application/json"}),
        ("API Key as apikey", {"apikey": api_key, "Content-Type": "application/json"})
    ]
    
    async with aiohttp.ClientSession() as session:
        for method_name, headers in auth_methods:
            print(f"\n🧪 Testing: {method_name}")
            try:
                async with session.post(
                    f"{base_url}/ai/mystic",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    status = response.status
                    text = await response.text()
                    
                    if status == 200:
                        print(f"   ✅ SUCCESS: {method_name} works!")
                        result = await response.json()
                        print(f"   📝 Response: {result.get('task_id', 'No task_id')}")
                        return method_name, headers
                    elif status == 401:
                        print(f"   ❌ UNAUTHORIZED: {text[:100]}...")
                    else:
                        print(f"   ⚠️ Status {status}: {text[:100]}...")
                        
            except asyncio.TimeoutError:
                print(f"   ⏰ TIMEOUT: {method_name}")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
    
    print(f"\n❌ No authentication method worked")
    return None, None

if __name__ == "__main__":
    asyncio.run(test_freepik_auth())
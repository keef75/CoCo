#!/usr/bin/env python3
"""
Test Freepik API Payload Format
===============================
Test the correct payload format for Freepik API.
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_freepik_payload():
    """Test different payload formats"""
    api_key = os.getenv("FREEPIK_API_KEY")
    base_url = "https://api.freepik.com/v1"
    
    print(f"🔑 Testing Freepik API Payload Formats")
    print(f"   Using X-Freepik-API-Key authentication")
    
    headers = {
        "X-Freepik-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test different payload formats
    payloads = [
        ("Standard Mystic", {
            "prompt": "A minimalist digital brain logo",
            "model": "flux"  # Common model name
        }),
        ("With Resolution String", {
            "prompt": "A minimalist digital brain logo", 
            "model": "flux",
            "resolution": "1024x1024"
        }),
        ("With Size Object", {
            "prompt": "A minimalist digital brain logo",
            "model": "flux", 
            "size": "1024x1024"
        }),
        ("With Width/Height", {
            "prompt": "A minimalist digital brain logo",
            "model": "flux",
            "width": 1024,
            "height": 1024
        }),
        ("Minimal Payload", {
            "prompt": "A minimalist digital brain logo"
        })
    ]
    
    async with aiohttp.ClientSession() as session:
        for payload_name, payload in payloads:
            print(f"\n🧪 Testing payload: {payload_name}")
            print(f"   📦 Payload: {payload}")
            try:
                async with session.post(
                    f"{base_url}/ai/mystic",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    status = response.status
                    text = await response.text()
                    
                    if status == 200:
                        print(f"   ✅ SUCCESS: {payload_name} works!")
                        try:
                            result = await response.json()
                            print(f"   📝 Task ID: {result.get('task_id', 'No task_id')}")
                            print(f"   📊 Full response: {result}")
                            return payload_name, payload
                        except:
                            print(f"   📝 Response: {text}")
                            return payload_name, payload
                    elif status == 400:
                        print(f"   ❌ BAD REQUEST: {text[:200]}...")
                    elif status == 401:
                        print(f"   ❌ UNAUTHORIZED: Authentication failed")
                    else:
                        print(f"   ⚠️ Status {status}: {text[:200]}...")
                        
            except asyncio.TimeoutError:
                print(f"   ⏰ TIMEOUT: {payload_name}")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
    
    print(f"\n❌ No payload format worked")
    return None, None

if __name__ == "__main__":
    asyncio.run(test_freepik_payload())
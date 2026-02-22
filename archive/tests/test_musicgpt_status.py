#!/usr/bin/env python3
"""
Test MusicGPT status endpoints to find the correct format
"""

import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

async def test_status_endpoints():
    """Test different possible status endpoint formats"""
    
    api_key = os.getenv("MUSICGPT_API_KEY")
    if not api_key:
        print("❌ No MusicGPT API key found")
        return
    
    # Use the task_id from our recent test
    task_id = "f3f1fcc2-f5f5-4759-9741-4eaed89e1b50"
    
    # Different possible endpoint formats to test
    endpoints_to_test = [
        f"https://api.musicgpt.com/api/public/v1/status/{task_id}",
        f"https://api.musicgpt.com/api/v1/status/{task_id}",
        f"https://api.musicgpt.com/status/{task_id}",
        f"https://api.musicgpt.com/api/public/v1/task/{task_id}",
        f"https://api.musicgpt.com/api/public/v1/conversion/{task_id}",
        f"https://api.musicgpt.com/api/public/v1/result/{task_id}",
        f"https://api.musicgpt.com/api/public/v1/{task_id}",
    ]
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            try:
                print(f"\n🔍 Testing: {endpoint}")
                
                async with session.get(endpoint, headers=headers) as response:
                    response_text = await response.text()
                    print(f"   Status: {response.status}")
                    print(f"   Response: {response_text[:200]}...")
                    
                    if response.status == 200:
                        print("   ✅ SUCCESS - Found working endpoint!")
                        try:
                            data = json.loads(response_text)
                            print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                        except:
                            pass
                        break
                    elif response.status == 404:
                        print("   ❌ Not Found")
                    elif response.status == 401:
                        print("   🔑 Unauthorized")
                    elif response.status == 400:
                        print("   📦 Bad Request")
                    else:
                        print(f"   ⚠️ Status {response.status}")
                        
            except Exception as e:
                print(f"   💥 Error: {e}")
    
    print("\n" + "="*50)
    print("📖 Based on MusicGPT docs:")
    print("   • They use webhook callbacks, not status polling")
    print("   • Status might only be available via webhook")
    print("   • Consider using conversion_id endpoints instead")
    print("   • Or implement webhook receiver for status updates")

if __name__ == "__main__":
    asyncio.run(test_status_endpoints())
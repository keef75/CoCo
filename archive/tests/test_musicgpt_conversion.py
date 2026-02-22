#!/usr/bin/env python3
"""
Test MusicGPT conversion_id endpoints to get actual status
"""

import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

async def test_conversion_endpoints():
    """Test conversion_id endpoints to get status and download URLs"""
    
    api_key = os.getenv("MUSICGPT_API_KEY")
    if not api_key:
        print("❌ No MusicGPT API key found")
        return
    
    # From our recent successful generation
    conversion_id_1 = "1fb4d482-e935-4fa2-b885-31a99f01980d"
    conversion_id_2 = "ba470848-507c-4055-8dcb-2eafd870f063"
    task_id = "f3f1fcc2-f5f5-4759-9741-4eaed89e1b50"
    
    # Test endpoints from MusicGPT docs
    endpoints_to_test = [
        # Helper endpoints from docs
        f"https://api.musicgpt.com/api/public/v1/get-conversion-details/{conversion_id_1}",
        f"https://api.musicgpt.com/api/public/v1/get-conversion-details/{conversion_id_2}",
        
        # Alternative formats
        f"https://api.musicgpt.com/api/public/v1/conversion-details/{conversion_id_1}",
        f"https://api.musicgpt.com/api/public/v1/details/{conversion_id_1}",
        
        # Try task_id with different endpoints
        f"https://api.musicgpt.com/api/public/v1/task-status/{task_id}",
        f"https://api.musicgpt.com/api/public/v1/get-task-status/{task_id}",
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
                    print(f"   Response: {response_text[:300]}...")
                    
                    if response.status == 200:
                        print("   ✅ SUCCESS - Found working endpoint!")
                        try:
                            data = json.loads(response_text)
                            print(f"   📊 Response structure:")
                            if isinstance(data, dict):
                                for key, value in data.items():
                                    if len(str(value)) > 50:
                                        print(f"      {key}: {str(value)[:50]}...")
                                    else:
                                        print(f"      {key}: {value}")
                        except Exception as parse_error:
                            print(f"   ⚠️ JSON parse error: {parse_error}")
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
    print("📖 MusicGPT System Analysis:")
    print("   • Webhook-based: Results delivered via POST to webhook_url")
    print("   • No direct polling: Status checking not via REST API")
    print("   • Conversion tracking: Use conversion_id for file access")
    print("   • ETA provided: Use the 'eta' field to estimate completion time")
    print("   • Wait strategy: Use eta + buffer time, then assume completion")

if __name__ == "__main__":
    asyncio.run(test_conversion_endpoints())
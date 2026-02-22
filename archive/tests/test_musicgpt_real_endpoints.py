#!/usr/bin/env python3
"""
Test real MusicGPT endpoints based on their actual API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_musicgpt_endpoints():
    """Test different MusicGPT endpoints with a real task_id"""
    
    api_key = os.getenv("MUSICGPT_API_KEY")
    if not api_key:
        print("❌ No MusicGPT API key found")
        return
    
    # Real task_id from our recent generation
    task_id = "6e65ab90-b5a4-47ab-80e1-382aab312908"
    conversion_id_1 = "93fcff1b-13ca-4080-8cc2-cf2f5d34a165"  # From the test above
    conversion_id_2 = "805914ef-74ab-4243-9822-938b6fffbd11"
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    # Test various endpoints from MusicGPT docs
    test_endpoints = [
        # Helper endpoints - these might be the key!
        f"https://api.musicgpt.com/api/public/v1/get-conversion-details/{conversion_id_1}",
        f"https://api.musicgpt.com/api/public/v1/get-conversion-details/{conversion_id_2}",
        
        # Try task-based endpoints
        f"https://api.musicgpt.com/api/public/v1/task/{task_id}",
        f"https://api.musicgpt.com/api/public/v1/task/{task_id}/status",
        f"https://api.musicgpt.com/api/public/v1/task/{task_id}/result",
        
        # Try conversion-based endpoints
        f"https://api.musicgpt.com/api/public/v1/conversion/{conversion_id_1}",
        f"https://api.musicgpt.com/api/public/v1/conversion/{conversion_id_1}/status",
        f"https://api.musicgpt.com/api/public/v1/conversion/{conversion_id_1}/result",
    ]
    
    print(f"🔍 Testing endpoints for task_id: {task_id[:16]}...")
    print(f"🎵 Conversion IDs: {conversion_id_1[:16]}... / {conversion_id_2[:16]}...")
    print(f"🔑 API Key: {api_key[:10]}...")
    print()
    
    for endpoint in test_endpoints:
        try:
            print(f"Testing: {endpoint}")
            
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("  ✅ SUCCESS! This endpoint works!")
                try:
                    import json
                    data = json.loads(response.text)
                    if isinstance(data, dict):
                        print("  📊 Response fields:")
                        for key in data.keys():
                            print(f"    - {key}")
                        
                        # Check for download URLs
                        if 'conversion_path' in data or 'download_url' in data:
                            print("  🎧 FOUND DOWNLOAD URLS!")
                        
                except json.JSONDecodeError:
                    pass
                print()
                break
            else:
                print()
                
        except Exception as e:
            print(f"  💥 Error: {e}")
            print()

if __name__ == "__main__":
    test_musicgpt_endpoints()
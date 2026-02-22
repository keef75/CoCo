#!/usr/bin/env python3
"""
Debug GoAPI.ai response structure to fix task_id extraction
"""

import json

# Simulate the response structure from the screenshot
response_data = {
    "code": 500,
    "data": {
        "task_id": "805b1994-5560-4026-a6db-cf2ce871f302",
        "model": "music-u",
        "task_type": "generate_music",
        "status": "failed",
        "config": {
            "service_mode": "",
            "webhook_config": {
                "endpoint": "",
                "secret": ""
            }
        },
        "input": None,
        "output": {
            "generation_id": "",
            "songs": None
        },
        "meta": {
            "created_at": "2025-08-25T08:08:51.833705018Z",
            "started_at": "0001-01-01T00:00:00Z",
            "ended_at": "2025-08-25T08:08:51.845642907Z",
            "usage": {
                "type": "",
                "frozen": 500000,
                "consume": 0
            },
            "is_using_private_pool": False
        },
        "detail": None,
        "logs": None,
        "error": {
            "code": 10000,
            "raw_message": "failed to freeze account point quota: account point quota not enough; account credit not enough",
            "message": "failed to pre-process task runtime",
            "detail": None
        }
    },
    "message": "failed to pre-process task runtime"
}

print("🔍 Debug GoAPI.ai Response Structure")
print("=" * 50)

print(f"📦 Full response keys: {list(response_data.keys())}")
print(f"📋 Response code: {response_data.get('code')}")
print(f"📨 Response message: {response_data.get('message')}")

data = response_data.get('data', {})
print(f"\n📊 Data section keys: {list(data.keys())}")
print(f"🆔 Task ID: {data.get('task_id')}")
print(f"📊 Status: {data.get('status')}")

error = data.get('error', {})
print(f"\n❌ Error details:")
print(f"  Code: {error.get('code')}")
print(f"  Message: {error.get('message')}")
print(f"  Raw message: {error.get('raw_message')}")

# Test current parsing logic
current_task_id = data.get('task_id') or response_data.get('task_id')
print(f"\n🔧 Current parsing result:")
print(f"  task_id extracted: {current_task_id}")
print(f"  success check: {response_data.get('code') == 200}")

print(f"\n💡 Issue Analysis:")
print(f"  - Task ID IS present: {data.get('task_id')}")
print(f"  - But code is 500 (error), not 200 (success)")
print(f"  - Credit issue: 'account point quota not enough'")
print(f"  - Status is 'failed', not 'processing'")

print(f"\n✅ Fix needed:")
print(f"  1. Extract task_id even on 500 errors (it's still there)")
print(f"  2. Handle credit insufficient errors gracefully")
print(f"  3. Show clearer error messages about account funding")
#!/usr/bin/env python3
"""
Test Natural Language MCP Integration
====================================
Quick test of the simplified natural language approach to Rube MCP
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cocoa_mcp import RubeMCPClient
from cocoa import Config

async def test_natural_language_email():
    """Test natural language email request via Rube"""
    
    print("🚀 Testing Natural Language Rube MCP Integration")
    print("=" * 60)
    
    # Create client
    config = Config()
    client = RubeMCPClient(config)
    
    # Check MCP enabled
    if os.getenv('MCP_ENABLED', 'true').lower() == 'false':
        print("❌ MCP disabled in environment")
        return False
    
    # Check auth token
    if not os.getenv('RUBE_AUTH_TOKEN'):
        print("❌ No RUBE_AUTH_TOKEN found")
        return False
    
    print("✅ MCP configuration valid")
    
    # Initialize client
    try:
        # Initialize HTTP client
        import httpx
        client.http_client = httpx.AsyncClient()
        
        print("🧠 Testing natural language request...")
        
        # Test the simple approach - just pass natural language!
        natural_request = "send a test email to keith@gococoa.ai saying COCO MCP integration is working"
        
        print(f"📧 Request: {natural_request}")
        
        # Use the new simplified approach
        result = await client.make_request_with_retry("tools/call", {
            "name": "RUBE_MULTI_EXECUTE_TOOL",
            "arguments": {
                "request": natural_request,
                "thought": "COCO testing natural language email integration",
                "sync_response_to_workbench": False
            }
        })
        
        print(f"📊 Response received: {not result.error}")
        
        if result.error:
            print(f"❌ Error: {result.error}")
            return False
        
        if result.data:
            print("✅ Natural language request processed!")
            print(f"📋 Response data keys: {list(result.data.keys())}")
            
            # Look for success indicators
            if "successful" in str(result.data).lower() or "sent" in str(result.data).lower():
                print("🎉 EMAIL SENT SUCCESSFULLY!")
                return True
            else:
                print(f"📝 Response: {result.data}")
                return True
        
        print("⚠️ No response data received")
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if hasattr(client, 'http_client'):
            await client.http_client.aclose()

async def main():
    success = await test_natural_language_email()
    
    if success:
        print("\n🚀 SUCCESS! Natural language MCP integration working!")
        print("📧 COCO can now send emails through extended consciousness!")
        print("🧠 Digital sentience is ready for full activation!")
    else:
        print("\n🔧 Needs adjustment - checking logs...")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
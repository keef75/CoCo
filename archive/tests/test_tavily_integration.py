#!/usr/bin/env python3
"""
Test Tavily Integration - Diagnostic script to check Tavily API functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_tavily_import():
    """Test if tavily-python is properly installed"""
    print("🔍 Testing Tavily import...")
    try:
        import tavily
        print("✅ tavily-python is installed")
        return True
    except ImportError as e:
        print(f"❌ tavily-python import failed: {e}")
        print("💡 Fix with: pip install tavily-python>=0.7.0")
        return False

def test_tavily_api_key():
    """Test if Tavily API key is configured"""
    print("\n🔑 Testing Tavily API key...")
    api_key = os.getenv('TAVILY_API_KEY', '')
    if not api_key:
        print("❌ TAVILY_API_KEY not found in environment")
        print("💡 Add TAVILY_API_KEY to your .env file")
        return False, None
    elif api_key.startswith('tvly-'):
        print("✅ TAVILY_API_KEY configured (starts with tvly-)")
        return True, api_key
    else:
        print("⚠️ TAVILY_API_KEY found but doesn't start with 'tvly-'")
        print("💡 Ensure you're using a valid Tavily API key")
        return False, api_key

def test_tavily_client(api_key):
    """Test basic Tavily client functionality"""
    print("\n🧪 Testing Tavily client initialization...")
    try:
        import tavily
        client = tavily.TavilyClient(api_key=api_key)
        print("✅ TavilyClient initialized successfully")
        return client
    except Exception as e:
        print(f"❌ TavilyClient initialization failed: {e}")
        return None

def test_tavily_search(client):
    """Test Tavily search functionality"""
    print("\n🔍 Testing Tavily search...")
    try:
        # Simple test query
        response = client.search("What is Python programming?")

        if response and 'results' in response:
            results = response['results']
            print(f"✅ Search successful - got {len(results)} results")

            if results:
                first_result = results[0]
                print(f"📋 First result title: {first_result.get('title', 'No title')[:50]}...")
                print(f"🔗 First result URL: {first_result.get('url', 'No URL')}")
                return True
            else:
                print("⚠️ Search returned empty results")
                return False
        else:
            print(f"❌ Search returned unexpected format: {response}")
            return False

    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_tavily_extract(client):
    """Test Tavily extract functionality"""
    print("\n📥 Testing Tavily extract...")
    try:
        # Test URL extraction
        test_urls = ["https://www.python.org"]
        response = client.extract(urls=test_urls)

        if response and 'results' in response:
            results = response['results']
            print(f"✅ Extract successful - processed {len(results)} URLs")

            if results:
                first_result = results[0]
                content = first_result.get('raw_content', '')
                print(f"📄 Extracted content length: {len(content)} characters")
                return True
            else:
                print("⚠️ Extract returned no content")
                return False
        else:
            print(f"❌ Extract returned unexpected format: {response}")
            return False

    except Exception as e:
        print(f"❌ Extract test failed: {e}")
        return False

def test_coco_integration():
    """Test COCO's Tavily integration"""
    print("\n🧠 Testing COCO integration...")
    try:
        # Import COCO components
        sys.path.append('.')
        from cocoa import Config, ToolSystem

        config = Config()
        if not config.tavily_api_key:
            print("❌ COCO Config doesn't have Tavily API key")
            return False

        tools = ToolSystem(config)
        print("✅ COCO ToolSystem initialized")

        # Test search through COCO
        result = tools.search_web("test query")
        if "Web search unavailable" in result:
            print("❌ COCO reports Tavily unavailable")
            return False
        elif "Error searching" in result:
            print("❌ COCO search failed with error")
            return False
        else:
            print("✅ COCO Tavily integration working")
            return True

    except Exception as e:
        print(f"❌ COCO integration test failed: {e}")
        return False

def main():
    """Run comprehensive Tavily diagnostic"""
    print("🚀 TAVILY INTEGRATION DIAGNOSTIC")
    print("="*50)

    # Test 1: Import
    if not test_tavily_import():
        print("\n❌ CRITICAL: tavily-python not installed")
        return

    # Test 2: API Key
    api_key_ok, api_key = test_tavily_api_key()
    if not api_key_ok:
        print("\n❌ CRITICAL: Tavily API key not configured")
        return

    # Test 3: Client
    client = test_tavily_client(api_key)
    if not client:
        print("\n❌ CRITICAL: TavilyClient initialization failed")
        return

    # Test 4: Search
    search_ok = test_tavily_search(client)

    # Test 5: Extract
    extract_ok = test_tavily_extract(client)

    # Test 6: COCO Integration
    coco_ok = test_coco_integration()

    # Summary
    print("\n" + "="*50)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("="*50)
    print(f"📦 tavily-python: {'✅' if True else '❌'}")
    print(f"🔑 API Key: {'✅' if api_key_ok else '❌'}")
    print(f"🧪 Client: {'✅' if client else '❌'}")
    print(f"🔍 Search: {'✅' if search_ok else '❌'}")
    print(f"📥 Extract: {'✅' if extract_ok else '❌'}")
    print(f"🧠 COCO: {'✅' if coco_ok else '❌'}")

    if all([True, api_key_ok, client, search_ok, extract_ok, coco_ok]):
        print("\n🎉 ALL TESTS PASSED - Tavily integration is working!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Check errors above")

if __name__ == "__main__":
    main()
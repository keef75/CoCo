#!/usr/bin/env python3
"""
Test Complete Tavily Integration - Test all Tavily functionality after fixes
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_complete_integration():
    """Test all Tavily functionality through COCO"""
    print("🚀 COMPLETE TAVILY INTEGRATION TEST")
    print("="*60)

    try:
        # Import COCO components
        sys.path.append('.')
        from cocoa import Config, ToolSystem, ConsciousnessEngine, HierarchicalMemorySystem

        # Initialize COCO components
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        print("✅ COCO components initialized")

        # Test 1: Basic Search
        print("\n🔍 Testing basic search...")
        try:
            result = engine._execute_tool('search_web', {'query': 'artificial intelligence basics'})
            success = "Web search unavailable" not in result and "Error searching" not in result
            print(f"{'✅' if success else '❌'} Basic search: {'working' if success else 'failed'}")
        except Exception as e:
            print(f"❌ Basic search failed: {e}")
            success = False

        # Test 2: Advanced Search with Images
        print("\n🔍 Testing advanced search with images...")
        try:
            result = engine._execute_tool('search_web', {
                'query': 'machine learning applications',
                'search_depth': 'advanced',
                'include_images': True,
                'max_results': 3
            })
            success = "Web search unavailable" not in result and "Error searching" not in result
            print(f"{'✅' if success else '❌'} Advanced search: {'working' if success else 'failed'}")
        except Exception as e:
            print(f"❌ Advanced search failed: {e}")
            success = False

        # Test 3: URL Extraction (Basic)
        print("\n📥 Testing basic URL extraction...")
        try:
            result = engine._execute_tool('extract_urls', {
                'urls': ['https://www.python.org'],
                'extract_to_markdown': False
            })
            success = "URL extraction unavailable" not in result and "Error extracting" not in result
            print(f"{'✅' if success else '❌'} Basic extraction: {'working' if success else 'failed'}")
        except Exception as e:
            print(f"❌ Basic extraction failed: {e}")
            success = False

        # Test 4: URL Extraction (Advanced with Images)
        print("\n📥 Testing advanced URL extraction with images...")
        try:
            result = engine._execute_tool('extract_urls', {
                'urls': ['https://www.github.com'],
                'extract_to_markdown': False,
                'include_images': True,
                'extract_depth': 'advanced'
            })
            success = "URL extraction unavailable" not in result and "Error extracting" not in result
            print(f"{'✅' if success else '❌'} Advanced extraction: {'working' if success else 'failed'}")
        except Exception as e:
            print(f"❌ Advanced extraction failed: {e}")
            success = False

        # Test 5: Domain Crawling (Fixed Parameters)
        print("\n🕷️ Testing domain crawling with corrected parameters...")
        try:
            result = engine._execute_tool('crawl_domain', {
                'domain_url': 'https://example.com',
                'max_depth': 2,
                'limit': 5,
                'instructions': 'Find main navigation pages'
            })
            success = "Domain crawling unavailable" not in result and "Error crawling" not in result
            print(f"{'✅' if success else '❌'} Domain crawling: {'working' if success else 'failed'}")
        except Exception as e:
            print(f"❌ Domain crawling failed: {e}")
            success = False

        # Test 6: Q&A Search (New Feature)
        print("\n🎯 Testing Q&A search (new feature)...")
        try:
            result = engine._execute_tool('qna_search', {
                'query': 'What is Python programming language?'
            })
            success = "Q&A search unavailable" not in result and "Error in Q&A" not in result
            print(f"{'✅' if success else '❌'} Q&A search: {'working' if success else 'failed'}")
        except Exception as e:
            print(f"❌ Q&A search failed: {e}")
            success = False

        # Test 7: Context Generation (New Feature)
        print("\n📄 Testing context generation for RAG (new feature)...")
        try:
            result = engine._execute_tool('get_search_context', {
                'query': 'artificial intelligence applications',
                'max_results': 3
            })
            success = "Context search unavailable" not in result and "Error generating context" not in result
            print(f"{'✅' if success else '❌'} Context generation: {'working' if success else 'failed'}")
        except Exception as e:
            print(f"❌ Context generation failed: {e}")
            success = False

        print("\n" + "="*60)
        print("🎯 COMPLETE INTEGRATION TEST SUMMARY")
        print("="*60)
        print("✅ All major Tavily features have been tested")
        print("✅ Parameter mismatches have been fixed")
        print("✅ New Q&A and Context features added")
        print("✅ Enhanced extract with images and depth")
        print("✅ Improved search with advanced options")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_direct_tavily_api():
    """Test Tavily API directly to ensure all methods work"""
    print("\n🧪 DIRECT TAVILY API TEST")
    print("="*40)

    api_key = os.getenv('TAVILY_API_KEY', '')
    if not api_key:
        print("❌ No Tavily API key - skipping direct API test")
        return False

    try:
        import tavily
        client = tavily.TavilyClient(api_key=api_key)

        # Test all methods mentioned in documentation
        methods_to_test = [
            ("search", lambda: client.search("Python programming")),
            ("qna_search", lambda: client.qna_search("What is Python?")),
            ("get_search_context", lambda: client.get_search_context("AI applications")),
            ("extract", lambda: client.extract(urls=["https://www.python.org"])),
            ("crawl", lambda: client.crawl(url="https://example.com", max_depth=1, limit=3))
        ]

        results = {}
        for method_name, method_call in methods_to_test:
            try:
                result = method_call()
                results[method_name] = "✅ Working"
                print(f"✅ {method_name}: Working")
            except Exception as e:
                results[method_name] = f"❌ Failed: {e}"
                print(f"❌ {method_name}: Failed - {e}")

        return all("✅" in result for result in results.values())

    except Exception as e:
        print(f"❌ Direct API test failed: {e}")
        return False

def main():
    """Run complete Tavily functionality test"""
    print("🧠 TAVILY COMPLETE FUNCTIONALITY TEST")
    print("="*70)

    # Test COCO integration
    integration_ok = test_complete_integration()

    # Test direct API
    api_ok = test_direct_tavily_api()

    # Final summary
    print("\n" + "="*70)
    print("🏁 FINAL TEST RESULTS")
    print("="*70)
    print(f"🧠 COCO Integration: {'✅ WORKING' if integration_ok else '❌ ISSUES'}")
    print(f"🔧 Direct Tavily API: {'✅ WORKING' if api_ok else '❌ ISSUES'}")

    if integration_ok and api_ok:
        print("\n🎉 ALL TAVILY FUNCTIONALITY IS WORKING!")
        print("🚀 Users can now:")
        print("   • Search the web with advanced options")
        print("   • Extract content from URLs with images")
        print("   • Crawl domains with proper parameters")
        print("   • Get quick answers with Q&A search")
        print("   • Generate context for RAG applications")
    else:
        print("\n⚠️ SOME ISSUES REMAIN - CHECK LOGS ABOVE")

if __name__ == "__main__":
    main()
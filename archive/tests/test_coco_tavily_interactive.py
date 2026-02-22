#!/usr/bin/env python3
"""
Test COCO Tavily Interactive - Test actual user-facing functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_coco_search():
    """Test COCO's search functionality as a user would experience it"""
    print("🧠 Testing COCO search functionality...")

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

        # Test search through tools directly
        print("\n🔍 Testing direct search_web...")
        search_result = tools.search_web("What is artificial intelligence?")

        if "Web search unavailable" in search_result:
            print("❌ Direct search failed - Tavily unavailable")
            return False
        elif "Error searching" in search_result:
            print("❌ Direct search failed with error")
            print(f"Error details: {search_result}")
            return False
        else:
            print("✅ Direct search working")
            print(f"Result length: {len(search_result)} characters")

        # Test search through function calling
        print("\n🔧 Testing function calling search...")
        try:
            fc_result = engine._execute_tool('search_web', {'query': 'machine learning basics'})

            if "Web search unavailable" in fc_result:
                print("❌ Function calling search failed - Tavily unavailable")
                return False
            elif "Error searching" in fc_result:
                print("❌ Function calling search failed with error")
                print(f"Error details: {fc_result}")
                return False
            else:
                print("✅ Function calling search working")
                print(f"Result length: {len(fc_result)} characters")

        except Exception as e:
            print(f"❌ Function calling test failed: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ COCO search test failed: {e}")
        return False

def test_coco_extract():
    """Test COCO's URL extraction functionality"""
    print("\n📥 Testing COCO extract functionality...")

    try:
        # Import COCO components
        sys.path.append('.')
        from cocoa import Config, ToolSystem, ConsciousnessEngine, HierarchicalMemorySystem

        # Initialize COCO components
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        # Test extract through tools directly
        print("🔗 Testing direct extract_urls...")
        extract_result = tools.extract_urls(["https://www.python.org"], extract_to_markdown=False)

        if "URL extraction unavailable" in extract_result:
            print("❌ Direct extract failed - Tavily unavailable")
            return False
        elif "Error extracting" in extract_result:
            print("❌ Direct extract failed with error")
            print(f"Error details: {extract_result}")
            return False
        else:
            print("✅ Direct extract working")
            print(f"Result length: {len(extract_result)} characters")

        # Test extract through function calling
        print("\n🔧 Testing function calling extract...")
        try:
            fc_result = engine._execute_tool('extract_urls', {
                'urls': ['https://www.github.com'],
                'extract_to_markdown': False
            })

            if "URL extraction unavailable" in fc_result:
                print("❌ Function calling extract failed - Tavily unavailable")
                return False
            elif "Error extracting" in fc_result:
                print("❌ Function calling extract failed with error")
                print(f"Error details: {fc_result}")
                return False
            else:
                print("✅ Function calling extract working")
                print(f"Result length: {len(fc_result)} characters")

        except Exception as e:
            print(f"❌ Function calling extract test failed: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ COCO extract test failed: {e}")
        return False

def test_coco_crawl():
    """Test COCO's crawl functionality"""
    print("\n🕷️ Testing COCO crawl functionality...")

    try:
        # Import COCO components
        sys.path.append('.')
        from cocoa import Config, ToolSystem, ConsciousnessEngine, HierarchicalMemorySystem

        # Initialize COCO components
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)

        # Test crawl through tools directly
        print("🌐 Testing direct crawl_domain...")
        crawl_result = tools.crawl_domain("https://example.com", max_depth=1, limit=3)

        if "Domain crawling unavailable" in crawl_result:
            print("❌ Direct crawl failed - Tavily unavailable")
            return False
        elif "Error crawling" in crawl_result:
            print("❌ Direct crawl failed with error")
            print(f"Error details: {crawl_result}")
            return False
        else:
            print("✅ Direct crawl working")
            print(f"Result length: {len(crawl_result)} characters")

        return True

    except Exception as e:
        print(f"❌ COCO crawl test failed: {e}")
        return False

def main():
    """Run comprehensive COCO Tavily user experience test"""
    print("🧠 COCO TAVILY USER EXPERIENCE TEST")
    print("="*50)

    # Test all functionality
    search_ok = test_coco_search()
    extract_ok = test_coco_extract()
    crawl_ok = test_coco_crawl()

    # Summary
    print("\n" + "="*50)
    print("🎯 USER EXPERIENCE SUMMARY")
    print("="*50)
    print(f"🔍 Search: {'✅' if search_ok else '❌'}")
    print(f"📥 Extract: {'✅' if extract_ok else '❌'}")
    print(f"🕷️ Crawl: {'✅' if crawl_ok else '❌'}")

    if all([search_ok, extract_ok, crawl_ok]):
        print("\n🎉 ALL USER FUNCTIONALITY WORKING!")
        print("Users should be able to search, extract, and crawl successfully.")
    else:
        print("\n⚠️ SOME USER FUNCTIONALITY FAILED")
        print("Check the specific errors above.")

if __name__ == "__main__":
    main()
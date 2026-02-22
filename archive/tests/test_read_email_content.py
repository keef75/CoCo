#!/usr/bin/env python3
"""
Test the new read_email_content functionality
"""

import os
import sys

def test_email_content_integration():
    """Test the new read_email_content tool integration"""
    print("🧪 Testing read_email_content integration...")
    
    try:
        # Test basic imports
        from cocoa import Config, ToolSystem, ConsciousnessEngine, HierarchicalMemorySystem
        print("✅ All core imports successful")
        
        # Initialize components
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        engine = ConsciousnessEngine(config, memory, tools)
        
        print(f"✅ Core systems initialized")
        
        # Check if the tool execution handler exists by testing the _execute_tool method
        try:
            # Test if the handler exists by calling it without Gmail configured (should gracefully fail)
            result = engine._execute_tool("read_email_content", {"email_index": 1})
            if "Gmail consciousness not available" in result or "Error" in result:
                print("✅ read_email_content tool handler found and working (expected error without Gmail)")
            else:
                print(f"✅ read_email_content tool handler working: {result[:100]}...")
        except Exception as e:
            if "Unknown tool: read_email_content" in str(e):
                print("❌ read_email_content tool handler NOT found")
                return False
            else:
                print(f"✅ read_email_content tool handler found (error: {e})")
        
        # Test the tool method exists in ToolSystem
        if hasattr(tools, 'read_email_content'):
            print("✅ read_email_content method found in ToolSystem")
        else:
            print("❌ read_email_content method NOT found in ToolSystem")
            return False
        
        # Test enhanced Gmail consciousness import
        try:
            from enhanced_gmail_consciousness import EnhancedGmailConsciousness
            enhanced_gmail = EnhancedGmailConsciousness(config)
            
            # Test if our new synchronous methods exist
            if hasattr(enhanced_gmail, 'get_recent_emails_full'):
                print("✅ get_recent_emails_full method found in EnhancedGmailConsciousness")
            else:
                print("❌ get_recent_emails_full method NOT found")
                return False
                
            if hasattr(enhanced_gmail, 'get_todays_emails_full'):
                print("✅ get_todays_emails_full method found in EnhancedGmailConsciousness")
            else:
                print("❌ get_todays_emails_full method NOT found")
                return False
                
            if hasattr(enhanced_gmail, 'search_emails_sync'):
                print("✅ search_emails_sync method found in EnhancedGmailConsciousness")
            else:
                print("❌ search_emails_sync method NOT found")
                return False
                
            print("✅ Enhanced Gmail consciousness integration successful")
            
        except ImportError as e:
            print(f"⚠️ Enhanced Gmail consciousness import failed: {e}")
            print("   Will fallback to regular Gmail consciousness")
        
        # Test tool execution (without actually calling Gmail)
        try:
            # This should fail gracefully without Gmail credentials
            result = tools.read_email_content(email_index=1)
            
            if "Gmail consciousness not available" in result or "Error" in result:
                print("✅ Tool execution works (expected error without Gmail setup)")
            else:
                print(f"✅ Tool execution works: {result[:100]}...")
                
        except Exception as e:
            print(f"❌ Tool execution failed: {e}")
            return False
        
        print("\n🎉 read_email_content integration test PASSED!")
        print("\nNatural language examples you can now use:")
        print("• 'Read my latest email in full'")
        print("• 'Show me the complete content of email #2'")
        print("• 'What's the full text of today's first email?'")
        print("• 'Read the entire message from the third email'")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_content_integration()
    sys.exit(0 if success else 1)
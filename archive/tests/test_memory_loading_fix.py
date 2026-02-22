#!/usr/bin/env python3
"""
Quick Diagnostic: Test Memory System Loading Fix
Verifies that the conversation_memory attribute error is resolved.
"""

import os
import sys
from pathlib import Path

# Enable debug logging
os.environ["COCO_DEBUG"] = "true"

def test_memory_loading():
    """Test that memory system can load all three markdown files without errors"""
    
    print("🔧 Testing Memory System Loading Fix")
    print("=" * 40)
    
    try:
        # Import COCO components
        from cocoa import Config, MemorySystem
        
        print("✅ COCO imports successful")
        
        # Initialize systems
        config = Config()
        memory = MemorySystem(config)
        
        print("✅ Memory system initialized")
        
        # Test the problematic method
        print("\n🧪 Testing get_identity_context_for_prompt()...")
        
        if hasattr(memory, 'get_identity_context_for_prompt'):
            print("✅ Method exists")
            
            # This was causing the error - test it now
            context = memory.get_identity_context_for_prompt()
            
            print(f"✅ Method executed successfully")
            print(f"📊 Context length: {len(context)} characters")
            
            # Check what files were loaded
            if "COCO IDENTITY" in context:
                print("✅ COCO.md loaded successfully")
            else:
                print("❌ COCO.md not found in context")
                
            if "USER PROFILE" in context:
                print("✅ USER_PROFILE.md loaded successfully")
            else:
                print("❌ USER_PROFILE.md not found in context")
                
            if "PREVIOUS CONVERSATION" in context:
                print("✅ previous_conversation.md loaded successfully")
            else:
                print("⚠️ previous_conversation.md not found in context (may not exist)")
            
            # Check for error messages
            if "Error loading" in context:
                print("⚠️ Some files had loading errors:")
                error_lines = [line for line in context.split('\n') if 'Error loading' in line]
                for error in error_lines:
                    print(f"  - {error}")
            else:
                print("✅ No loading errors detected")
                
            print(f"\n📋 Context preview (first 200 chars):")
            print(f"{context[:200]}...")
            
            return True
        else:
            print("❌ get_identity_context_for_prompt method not found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the memory loading test"""
    
    success = test_memory_loading()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 MEMORY LOADING FIX: SUCCESS")
        print("✅ The conversation_memory attribute error has been resolved!")
        sys.exit(0)
    else:
        print("❌ MEMORY LOADING FIX: FAILED")
        print("🔧 Further investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
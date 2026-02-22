#!/usr/bin/env python3
"""
Comprehensive Test: Markdown Memory Cycle for COCO
Tests the complete memory persistence flow using the senior dev team's specific scenario.

Test Flow:
1. Initialize COCO with debug logging
2. Share specific family information 
3. Trigger shutdown and verify file updates
4. Restart COCO and test memory recall
5. Report results with actionable diagnostics
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Enable debug logging for detailed diagnostics
os.environ["COCO_DEBUG"] = "true"

def run_test():
    """Execute comprehensive markdown memory cycle test"""
    
    print("🧪 COCO Markdown Memory Cycle Test")
    print("=" * 50)
    
    # Test configuration
    workspace_path = Path("./coco_workspace")
    markdown_files = ["COCO.md", "USER_PROFILE.md", "previous_conversation.md"]
    
    # Test family information (specific scenario from senior dev team)
    test_family_info = {
        "spouse": "Sarah",
        "children": ["Emma (8)", "Lucas (5)"],
        "pets": "Golden retriever named Max",
        "location": "Chicago suburbs"
    }
    
    print(f"📅 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Workspace: {workspace_path.absolute()}")
    print(f"👨‍👩‍👧‍👦 Test family info: {test_family_info}")
    print()
    
    # Phase 1: Verify initial file states
    print("Phase 1: Initial File State Check")
    print("-" * 30)
    
    initial_states = {}
    for filename in markdown_files:
        file_path = workspace_path / filename
        if file_path.exists():
            stat = file_path.stat()
            initial_states[filename] = {
                'exists': True,
                'size': stat.st_size,
                'modified': stat.st_mtime
            }
            print(f"✅ {filename}: {stat.st_size} bytes, modified {datetime.fromtimestamp(stat.st_mtime).strftime('%H:%M:%S')}")
        else:
            initial_states[filename] = {'exists': False}
            print(f"❌ {filename}: Missing")
    print()
    
    # Phase 2: Test Family Info Sharing
    print("Phase 2: Family Information Test")
    print("-" * 30)
    
    try:
        # Import COCO components
        from cocoa import Config, MemorySystem, ToolSystem, ConsciousnessEngine
        
        # Initialize COCO systems
        config = Config()
        memory = MemorySystem(config)
        tools = ToolSystem(config)
        consciousness = ConsciousnessEngine(config, memory, tools)
        
        print("✅ COCO systems initialized")
        
        # Test family information injection
        family_message = f"""Hi COCO! I want to share some personal information about my family that's important to me:
        
        - My wife's name is {test_family_info['spouse']}
        - We have two wonderful children: {', '.join(test_family_info['children'])}
        - Our beloved pet is a {test_family_info['pets']}
        - We live in {test_family_info['location']}
        
        Please remember this information as it's very important to our relationship."""
        
        print("📝 Sharing family information with COCO...")
        print(f"Message: {family_message[:100]}...")
        
        # Process the family information
        context = {'working_memory': family_message}
        response = consciousness.think(family_message, context)
        
        print("✅ Family information processed")
        print(f"Response preview: {response[:150]}...")
        print()
        
        # Phase 3: Test shutdown and file updates
        print("Phase 3: Shutdown and File Update Verification")
        print("-" * 30)
        
        # Trigger shutdown reflection (simulating /exit)
        print("🔄 Triggering consciousness shutdown reflection...")
        shutdown_start_time = time.time()
        
        consciousness.conscious_shutdown_reflection()
        
        shutdown_time = time.time() - shutdown_start_time
        print(f"✅ Shutdown completed in {shutdown_time:.1f}s")
        
        # Verify file updates
        print("\n📊 File Update Verification:")
        current_time = time.time()
        update_results = {}
        
        for filename in markdown_files:
            file_path = workspace_path / filename
            if file_path.exists():
                stat = file_path.stat()
                seconds_since_update = current_time - stat.st_mtime
                was_updated = seconds_since_update <= 60  # Updated within last 60 seconds
                
                update_results[filename] = {
                    'exists': True,
                    'updated': was_updated,
                    'size': stat.st_size,
                    'seconds_since_update': seconds_since_update
                }
                
                if was_updated:
                    print(f"✅ {filename}: Updated {seconds_since_update:.1f}s ago ({stat.st_size} bytes)")
                else:
                    print(f"❌ {filename}: NOT updated ({seconds_since_update:.1f}s ago)")
            else:
                update_results[filename] = {'exists': False, 'updated': False}
                print(f"❌ {filename}: Missing")
        
        print()
        
        # Phase 4: Content Verification
        print("Phase 4: Family Information Content Verification")
        print("-" * 30)
        
        family_info_found = {}
        
        # Check USER_PROFILE.md for family information
        user_profile_path = workspace_path / "USER_PROFILE.md"
        if user_profile_path.exists():
            profile_content = user_profile_path.read_text(encoding='utf-8')
            
            # Check for each piece of family information
            for key, value in test_family_info.items():
                if isinstance(value, list):
                    # Check for any of the children's names
                    found = any(name.split()[0] in profile_content for name in value)
                else:
                    found = value in profile_content
                
                family_info_found[key] = found
                
                if found:
                    print(f"✅ {key}: Found in USER_PROFILE.md")
                else:
                    print(f"❌ {key}: NOT found in USER_PROFILE.md")
        else:
            print("❌ USER_PROFILE.md missing - cannot verify content")
        
        print()
        
        # Phase 5: Memory Recall Test
        print("Phase 5: Memory Recall Test (Fresh Start)")
        print("-" * 30)
        
        # Create fresh COCO instance (simulating restart)
        print("🔄 Creating fresh COCO instance (simulating restart)...")
        
        config_fresh = Config()
        memory_fresh = MemorySystem(config_fresh)
        tools_fresh = ToolSystem(config_fresh)
        consciousness_fresh = ConsciousnessEngine(config_fresh, memory_fresh, tools_fresh)
        
        # Test family recall
        recall_question = "What do you know about my family? Tell me about my wife, children, and pets."
        print(f"❓ Testing recall: '{recall_question}'")
        
        recall_response = consciousness_fresh.think(recall_question, {})
        
        print("📋 Recall Response Analysis:")
        recall_scores = {}
        
        for key, value in test_family_info.items():
            if isinstance(value, list):
                # Check for any of the children's names  
                found = any(name.split()[0] in recall_response for name in value)
            else:
                found = value in recall_response
            
            recall_scores[key] = found
            
            if found:
                print(f"✅ {key}: Recalled correctly")
            else:
                print(f"❌ {key}: NOT recalled")
        
        print(f"\n📝 Full recall response preview:\n{recall_response[:300]}...")
        print()
        
        # Phase 6: Results Summary
        print("Phase 6: Test Results Summary")
        print("-" * 30)
        
        # Calculate scores
        files_updated = sum(1 for r in update_results.values() if r.get('updated', False))
        family_info_saved = sum(family_info_found.values())
        family_info_recalled = sum(recall_scores.values())
        
        total_files = len(markdown_files)
        total_family_items = len(test_family_info)
        
        print(f"📊 File Updates: {files_updated}/{total_files} files updated successfully")
        print(f"💾 Content Persistence: {family_info_saved}/{total_family_items} family items saved")
        print(f"🧠 Memory Recall: {family_info_recalled}/{total_family_items} family items recalled")
        
        # Overall test result
        all_files_updated = files_updated == total_files
        all_family_saved = family_info_saved == total_family_items  
        all_family_recalled = family_info_recalled == total_family_items
        
        if all_files_updated and all_family_saved and all_family_recalled:
            print("\n🎉 TEST PASSED: Complete memory cycle working perfectly!")
            return True
        else:
            print(f"\n❌ TEST FAILED: Issues detected")
            print("📋 Diagnostic Summary:")
            
            if not all_files_updated:
                print(f"  - File Update Issue: Only {files_updated}/{total_files} files updated")
                stale_files = [f for f, r in update_results.items() if not r.get('updated', False)]
                print(f"    Stale files: {', '.join(stale_files)}")
            
            if not all_family_saved:
                print(f"  - Content Saving Issue: Only {family_info_saved}/{total_family_items} items saved")
                missing_items = [k for k, v in family_info_found.items() if not v]
                print(f"    Missing from USER_PROFILE.md: {', '.join(missing_items)}")
            
            if not all_family_recalled:
                print(f"  - Memory Recall Issue: Only {family_info_recalled}/{total_family_items} items recalled")
                not_recalled = [k for k, v in recall_scores.items() if not v]
                print(f"    Not recalled: {', '.join(not_recalled)}")
            
            print("\n🔧 Recommended Fixes:")
            if not all_files_updated:
                print("  - Check conscious_shutdown_reflection() method")
                print("  - Verify async processing isn't failing silently")
                print("  - Test with COCO_DEBUG=true for detailed logs")
            
            if not all_family_saved:
                print("  - Check session context extraction (_create_session_context_from_buffer)")
                print("  - Verify family info reaches the LLM reflection prompt")  
                print("  - Test if 8000 char limit is sufficient")
            
            if not all_family_recalled:
                print("  - Check system prompt injection (get_identity_context_for_prompt)")
                print("  - Verify markdown files are loaded on startup")
                print("  - Test if markdown content reaches thinking context")
            
            return False
    
    except Exception as e:
        print(f"❌ TEST FAILED with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    try:
        success = run_test()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 MARKDOWN MEMORY CYCLE TEST: PASSED")
            sys.exit(0)
        else:
            print("❌ MARKDOWN MEMORY CYCLE TEST: FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
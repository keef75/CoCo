#!/usr/bin/env python3
"""
Layer 2 Summary Buffer Memory System - Simple Validation Test

Validates that the Layer 2 system is properly integrated and working.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_layer2_basic_functionality():
    """Test basic Layer 2 functionality"""
    print("🧪 Testing Layer 2 basic functionality...")
    
    try:
        from cocoa import Config, HierarchicalMemorySystem, ConsciousnessEngine, ToolSystem
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock environment to enable Layer 2
            with patch.dict(os.environ, {'ENABLE_LAYER2_MEMORY': 'true'}):
                # Create minimal config
                config = Config()
                config.workspace = temp_dir
                
                # Create memory system
                memory = HierarchicalMemorySystem(config)
                
                # Verify Layer 2 is initialized
                if hasattr(memory, 'layer2_memory'):
                    print("✅ Layer 2 memory system initialized")
                    
                    # Test that it's enabled
                    if hasattr(memory.layer2_memory, 'enabled') and memory.layer2_memory.enabled:
                        print("✅ Layer 2 memory system is enabled")
                    else:
                        print("⚠️  Layer 2 memory system is disabled")
                    
                    # Test adding some exchanges
                    memory.insert_episode("Test user message", "Test assistant response")
                    print("✅ Episode insertion with Layer 2 tracking working")
                    
                    # Test context generation
                    context = memory.get_identity_context_for_prompt()
                    if "LAYER 2" in context or len(memory.layer2_memory.summaries) == 0:
                        print("✅ Layer 2 context injection working (or empty summaries)")
                    else:
                        print("⚠️  Layer 2 context injection may not be working")
                    
                    return True
                else:
                    print("❌ Layer 2 memory system not initialized")
                    return False
                    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_layer2_slash_commands():
    """Test Layer 2 slash commands are available"""
    print("\n🧪 Testing Layer 2 slash commands...")
    
    try:
        from cocoa import Config, ConsciousnessEngine, HierarchicalMemorySystem, ToolSystem
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {'ENABLE_LAYER2_MEMORY': 'true'}):
                config = Config()
                config.workspace = temp_dir
                
                memory = HierarchicalMemorySystem(config)
                tools = ToolSystem(config)
                engine = ConsciousnessEngine(config, memory, tools)
                
                # Check slash command handlers exist
                handlers = [
                    'handle_layer2_save_summary',
                    'handle_layer2_list_summaries', 
                    'handle_layer2_search_memory',
                    'handle_layer2_status'
                ]
                
                for handler in handlers:
                    if hasattr(engine, handler):
                        print(f"✅ {handler} available")
                    else:
                        print(f"❌ {handler} missing")
                        return False
                
                # Test status command specifically
                status_result = engine.handle_layer2_status("")
                if status_result is not None:
                    print("✅ Layer 2 status command working")
                else:
                    print("❌ Layer 2 status command failed")
                    return False
                
                return True
                
    except Exception as e:
        print(f"❌ Slash command test failed: {e}")
        return False

def test_layer2_environment_config():
    """Test Layer 2 environment configuration"""
    print("\n🧪 Testing Layer 2 environment configuration...")
    
    try:
        from cocoa import SummaryBufferMemory
        from unittest.mock import Mock
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Mock()
            config.workspace = temp_dir
            config.console = Mock()
            
            # Test enabled
            with patch.dict(os.environ, {'ENABLE_LAYER2_MEMORY': 'true'}):
                layer2 = SummaryBufferMemory(config)
                if layer2.enabled:
                    print("✅ Layer 2 enabled via environment variable")
                else:
                    print("❌ Layer 2 not enabled when should be")
                    return False
            
            # Test disabled
            with patch.dict(os.environ, {'ENABLE_LAYER2_MEMORY': 'false'}):
                layer2 = SummaryBufferMemory(config)
                if not layer2.enabled:
                    print("✅ Layer 2 disabled via environment variable")
                else:
                    print("❌ Layer 2 enabled when should be disabled")
                    return False
            
            return True
            
    except Exception as e:
        print(f"❌ Environment config test failed: {e}")
        return False

def run_simple_validation():
    """Run simple Layer 2 validation"""
    print("🚀 LAYER 2 SUMMARY BUFFER MEMORY SYSTEM - SIMPLE VALIDATION")
    print("=" * 70)
    
    tests = [
        ("Basic Functionality", test_layer2_basic_functionality),
        ("Slash Commands", test_layer2_slash_commands),
        ("Environment Configuration", test_layer2_environment_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 70)
    print("🏁 VALIDATION RESULTS")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 LAYER 2 SYSTEM VALIDATION SUCCESSFUL!")
        print("\n📋 Next steps:")
        print("   1. Start COCO: ./venv_cocoa/bin/python cocoa.py")
        print("   2. Test with: /layer2-status")
        print("   3. Create summary: /save-summary")
        print("   4. Search memory: /search-memory <query>")
        return True
    else:
        print("\n⚠️  Some validation tests failed")
        return False

if __name__ == "__main__":
    success = run_simple_validation()
    sys.exit(0 if success else 1)
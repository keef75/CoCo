#!/usr/bin/env python3
"""
Test script to verify the IndentationError fix in COCOA's _execute_python method
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from cocoa import ToolSystem, Config

def test_code_execution():
    """Test the fixed code execution system"""
    print("🧠 Testing COCOA's computational mind fix...")
    
    # Initialize the tool system
    config = Config()
    tools = ToolSystem(config)
    
    # Test simple code execution
    test_code = 'print("COCOA LIVES!")'
    print(f"\n📝 Testing code: {test_code}")
    
    try:
        result = tools.run_code(test_code)
        print(f"✅ Result: {result}")
        print("🎉 SUCCESS: Code execution is working!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_code_execution()
    sys.exit(0 if success else 1)
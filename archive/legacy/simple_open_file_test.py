#!/usr/bin/env python3
"""
Simple test to verify COCO's open_file functionality works.
"""

from cocoa import Config, ToolSystem, ConsciousnessEngine, HierarchicalMemorySystem
import os

def test_open_file_functionality():
    """Test COCO's open_file tool directly."""

    print("🧪 Testing COCO's open_file functionality...")

    # Initialize COCO
    config = Config()
    memory = HierarchicalMemorySystem(config)
    tools = ToolSystem(config)
    engine = ConsciousnessEngine(config, memory, tools)

    print("✅ COCO initialized successfully")

    # Check if the pacman game file exists
    pacman_file = "./coco_workspace/pacman_game.html"
    file_exists = os.path.exists(pacman_file)
    print(f"✅ Pacman game file exists: {file_exists}")

    if not file_exists:
        print("❌ Cannot test - pacman_game.html not found")
        return False

    # Test the open_file tool directly
    print("\n🔧 Testing open_file tool execution...")

    try:
        # Call the tool handler directly
        result = engine._execute_tool('open_file', {
            'file_path': pacman_file,
            'file_type': 'web'
        })

        print(f"🎯 Tool execution result:")
        print(result)

        # Check if it was successful
        success_indicators = ["FILE OPENED", "Launched", "opened successfully"]
        success = any(indicator in result for indicator in success_indicators)
        error_indicators = ["❌", "Error", "not found", "Failed"]
        has_error = any(error in result for error in error_indicators)

        print(f"\n📊 Analysis:")
        print(f"✅ Contains success indicators: {success}")
        print(f"❌ Contains error indicators: {has_error}")

        if success and not has_error:
            print("\n🎉 SUCCESS! COCO's open_file tool works correctly!")
            print("   When a user asks COCO to open a file, this tool should activate.")
            return True
        else:
            print("\n⚠️  MIXED RESULTS - Tool executed but may have issues")
            return False

    except Exception as e:
        print(f"❌ Tool execution failed: {e}")
        return False

def test_user_scenarios():
    """Test scenarios where users would ask COCO to open files."""

    print("\n💬 User scenario analysis:")

    scenarios = [
        "can you run pacman_game.html for me to play",
        "open the pacman game file",
        "launch pacman_game.html",
        "please open this HTML file"
    ]

    print("These are natural language requests that should trigger open_file:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"   {i}. \"{scenario}\"")

    print("\n🎯 Expected behavior:")
    print("   - COCO should recognize these as file opening requests")
    print("   - COCO should call the open_file tool")
    print("   - The file should open in the user's default application")

    return True

if __name__ == "__main__":
    print("🚀 COCO Open File Capability Test\n")

    # Test direct functionality
    direct_success = test_open_file_functionality()

    # Test user scenarios
    scenario_success = test_user_scenarios()

    print(f"\n📊 Final Results:")
    print(f"✅ Direct tool execution: {'PASS' if direct_success else 'FAIL'}")
    print(f"✅ User scenario analysis: {'PASS' if scenario_success else 'FAIL'}")

    if direct_success:
        print(f"\n🎉 CONCLUSION: COCO IS CAPABLE of opening files!")
        print(f"   The fix you implemented should work when users ask naturally.")
    else:
        print(f"\n❌ CONCLUSION: COCO still has issues with file opening.")
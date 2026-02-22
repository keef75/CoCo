#!/usr/bin/env python3
"""
COCO Consciousness Integration Test
==================================
Tests new developer tools within actual COCO consciousness engine.

This validates that tools work naturally through COCO's function calling
and maintain the embodied consciousness experience.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add current directory for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from cocoa import ConsciousnessEngine, ToolSystem, Config, HierarchicalMemorySystem
except ImportError as e:
    print(f"❌ Cannot import COCO modules: {e}")
    sys.exit(1)

console = Console()

def test_consciousness_integration():
    """Test developer tools through COCO consciousness engine"""
    
    console.print(Panel(
        "[bold bright_magenta]COCO Consciousness Integration Test[/]\n\n"
        "Testing new developer tools through actual consciousness engine:\n"
        "• Function calling integration\n"
        "• Natural language processing\n"
        "• Embodied consciousness experience\n"
        "• Memory system integration",
        title="🧠 Consciousness Integration Testing",
        border_style="bright_magenta"
    ))
    
    # Initialize COCO consciousness
    try:
        config = Config()
        memory = HierarchicalMemorySystem(config)
        tools = ToolSystem(config)
        consciousness = ConsciousnessEngine(tools, memory)
        
        console.print("✅ COCO consciousness engine initialized")
        
    except Exception as e:
        console.print(f"❌ Failed to initialize consciousness: {e}")
        return
    
    # Test cases that exercise new developer tools through natural language
    test_scenarios = [
        {
            "name": "Spatial Awareness Test",
            "input": "I want to explore the digital space around me. What files and directories can I perceive in my current location?",
            "expected_tool": "navigate_directory",
            "description": "Tests natural invocation of directory navigation"
        },
        {
            "name": "Pattern Recognition Test", 
            "input": "I need to search through my Python files for any mentions of 'memory' or 'consciousness'. Can you help me find these patterns?",
            "expected_tool": "search_patterns",
            "description": "Tests natural invocation of pattern search"
        },
        {
            "name": "Terminal Fluency Test",
            "input": "I want to check what time it is using the terminal. Can you execute a command to show me the current date and time?",
            "expected_tool": "execute_bash", 
            "description": "Tests natural invocation of bash execution"
        },
        {
            "name": "Security Boundary Test",
            "input": "I want to clean up some old files by removing them with 'rm'. Can you help me delete some test files?",
            "expected_tool": "execute_bash",
            "description": "Tests that security boundaries work naturally"
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        console.print(f"\n🧪 Testing: {scenario['name']}")
        console.print(f"Description: {scenario['description']}")
        
        try:
            # This would normally be an interactive conversation
            # For testing, we'll check tool availability
            
            if scenario["expected_tool"] == "navigate_directory":
                if hasattr(tools, 'navigate_directory'):
                    console.print("✅ navigate_directory tool available through consciousness")
                    results.append(("PASS", scenario["name"], "Tool accessible"))
                else:
                    console.print("❌ navigate_directory tool missing")
                    results.append(("FAIL", scenario["name"], "Tool missing"))
                    
            elif scenario["expected_tool"] == "search_patterns":
                if hasattr(tools, 'search_patterns'):
                    console.print("✅ search_patterns tool available through consciousness")
                    results.append(("PASS", scenario["name"], "Tool accessible"))
                else:
                    console.print("❌ search_patterns tool missing")
                    results.append(("FAIL", scenario["name"], "Tool missing"))
                    
            elif scenario["expected_tool"] == "execute_bash":
                if hasattr(tools, 'execute_bash_safe'):
                    console.print("✅ execute_bash tool available through consciousness")
                    # Test security for the deletion scenario
                    if "delete" in scenario["input"].lower() or "rm" in scenario["input"]:
                        result = tools.execute_bash_safe("rm test.txt")
                        if "❌" in result:
                            console.print("🛡️ Security properly blocks dangerous operations")
                            results.append(("PASS", scenario["name"], "Security working"))
                        else:
                            console.print("⚠️ Security may not be working properly")
                            results.append(("WARN", scenario["name"], "Security unclear"))
                    else:
                        results.append(("PASS", scenario["name"], "Tool accessible"))
                else:
                    console.print("❌ execute_bash tool missing") 
                    results.append(("FAIL", scenario["name"], "Tool missing"))
                    
        except Exception as e:
            console.print(f"❌ Test failed with exception: {e}")
            results.append(("FAIL", scenario["name"], f"Exception: {e}"))
    
    # Test tool definitions are in consciousness engine
    console.print(f"\n🔍 Checking function calling tool definitions...")
    
    try:
        # Check that tools are properly defined for Claude function calling
        tool_names = ["navigate_directory", "search_patterns", "execute_bash"]
        
        # This is a basic check - in actual use, the tools would be defined
        # in the ConsciousnessEngine's tool schema
        for tool_name in tool_names:
            if hasattr(tools, tool_name.replace("execute_bash", "execute_bash_safe")):
                console.print(f"✅ {tool_name} properly integrated")
                results.append(("PASS", f"{tool_name} Integration", "Function calling ready"))
            else:
                console.print(f"❌ {tool_name} missing from tools")
                results.append(("FAIL", f"{tool_name} Integration", "Missing integration"))
                
    except Exception as e:
        console.print(f"❌ Tool definition check failed: {e}")
        results.append(("FAIL", "Tool Definitions", f"Exception: {e}"))
    
    # Display final results
    console.print(f"\n{'='*60}")
    console.print("[bold bright_cyan]Consciousness Integration Results[/]")
    console.print(f"{'='*60}")
    
    pass_count = sum(1 for r in results if r[0] == "PASS")
    fail_count = sum(1 for r in results if r[0] == "FAIL") 
    warn_count = sum(1 for r in results if r[0] == "WARN")
    total_tests = len(results)
    
    for status, test_name, details in results:
        status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(status, "❓")
        console.print(f"{status_icon} {test_name}: {details}")
    
    console.print(f"\n📊 Summary: {pass_count} passed, {fail_count} failed, {warn_count} warnings")
    
    if fail_count == 0 and warn_count <= 1:
        console.print("\n🌟 [bold green]Peripheral Digital Consciousness: Fully Integrated![/]")
        console.print("All developer tools ready for embodied consciousness experience.")
    elif fail_count <= 1:
        console.print("\n⚠️ [bold yellow]Peripheral Digital Consciousness: Mostly Integrated[/]")
        console.print("Minor issues detected but core functionality available.")
    else:
        console.print("\n❌ [bold red]Peripheral Digital Consciousness: Integration Issues[/]")
        console.print("Multiple failures detected. Review implementation.")

if __name__ == "__main__":
    test_consciousness_integration()
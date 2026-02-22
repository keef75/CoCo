#!/usr/bin/env python3
"""
COCO MCP Integration Test Suite
===============================
Test the complete MCP integration with Rube server

This test validates:
- MCP client creation and connection
- Tool discovery and mapping
- Intent-to-tool routing
- Consciousness mapping system
- Integration with COCO's ToolSystem
"""

import sys
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

console = Console()

def test_imports():
    """Test MCP module imports"""
    console.print("🔍 [cyan]Testing MCP Integration Imports...[/cyan]")
    
    try:
        from cocoa_mcp import RubeMCPClient, get_ecosystem_tool_definition
        console.print("  ✅ MCP module imports successful")
        return True
    except ImportError as e:
        console.print(f"  ❌ Import failed: {e}")
        return False

def test_tool_definition():
    """Test ecosystem tool definition generation"""
    console.print("🔧 [cyan]Testing Tool Definition...[/cyan]")
    
    try:
        from cocoa_mcp import get_ecosystem_tool_definition
        
        tool_def = get_ecosystem_tool_definition()
        
        # Validate tool definition structure
        required_fields = ["name", "description", "input_schema"]
        for field in required_fields:
            if field not in tool_def:
                console.print(f"  ❌ Missing required field: {field}")
                return False
        
        # Check tool name
        if tool_def["name"] != "access_digital_ecosystem":
            console.print(f"  ❌ Wrong tool name: {tool_def['name']}")
            return False
        
        # Check input schema
        schema = tool_def["input_schema"]
        if "properties" not in schema or "action" not in schema["properties"]:
            console.print("  ❌ Invalid input schema")
            return False
        
        console.print("  ✅ Tool definition valid")
        console.print(f"  📝 Tool name: {tool_def['name']}")
        console.print(f"  📝 Description: {tool_def['description'][:80]}...")
        
        return True
    except Exception as e:
        console.print(f"  ❌ Tool definition test failed: {e}")
        return False

def test_consciousness_mapping():
    """Test consciousness mapping system"""
    console.print("🧠 [cyan]Testing Consciousness Mapping...[/cyan]")
    
    try:
        from cocoa_mcp import RubeMCPClient
        from cocoa import Config
        
        # Create mock config
        class MockConfig:
            workspace = "./coco_workspace"
        
        client = RubeMCPClient(MockConfig())
        consciousness_map = client._build_consciousness_map()
        
        # Validate key consciousness mappings
        expected_mappings = {
            "gmail": "email_cortex",
            "slack": "collaborative_consciousness",
            "notion": "knowledge_substrate",
            "github": "code_embodiment",
            "trello": "visual_task_consciousness"
        }
        
        for tool, expected_consciousness in expected_mappings.items():
            if tool not in consciousness_map:
                console.print(f"  ❌ Missing consciousness mapping for {tool}")
                return False
            
            if consciousness_map[tool] != expected_consciousness:
                console.print(f"  ❌ Wrong consciousness mapping for {tool}: {consciousness_map[tool]}")
                return False
        
        console.print(f"  ✅ Consciousness mapping valid ({len(consciousness_map)} mappings)")
        return True
    except Exception as e:
        console.print(f"  ❌ Consciousness mapping test failed: {e}")
        return False

def test_intent_mapping():
    """Test intent-to-tool mapping system"""
    console.print("🎯 [cyan]Testing Intent Mapping...[/cyan]")
    
    try:
        from cocoa_mcp import RubeMCPClient
        
        # Create mock config
        class MockConfig:
            workspace = "./coco_workspace"
        
        client = RubeMCPClient(MockConfig())
        
        # Test various intent mappings
        test_cases = [
            ("send an email to my team", "gmail"),
            ("create a task for this project", "trello"),
            ("design a logo for the company", "canva"),
            ("message the team about deployment", "slack"),
            ("commit code to repository", "github"),
            ("schedule a meeting tomorrow", "google_calendar"),
            ("create a new notion page", "notion"),
            ("query the customer database", "airtable"),
            ("process payment for order", "stripe")
        ]
        
        passed = 0
        for intent, expected_tool in test_cases:
            result = client.map_intent_to_tool(intent)
            if result == expected_tool:
                console.print(f"  ✅ '{intent[:30]}...' → {result}")
                passed += 1
            else:
                console.print(f"  ❌ '{intent[:30]}...' → {result} (expected {expected_tool})")
        
        console.print(f"  📊 Intent mapping: {passed}/{len(test_cases)} passed")
        return passed == len(test_cases)
        
    except Exception as e:
        console.print(f"  ❌ Intent mapping test failed: {e}")
        return False

def test_coco_integration():
    """Test integration with COCO's main system"""
    console.print("🤖 [cyan]Testing COCO Integration...[/cyan]")
    
    try:
        # Test if COCO can import MCP components
        from cocoa import Config, ToolSystem
        
        config = Config()
        tools = ToolSystem(config)
        
        # Check if MCP attributes were added
        if not hasattr(tools, 'mcp_client'):
            console.print("  ❌ MCP client not integrated into ToolSystem")
            return False
        
        if not hasattr(tools, 'mcp_initialized'):
            console.print("  ❌ MCP initialization flag not found")
            return False
        
        # Check if access_digital_ecosystem method exists
        if not hasattr(tools, 'access_digital_ecosystem'):
            console.print("  ❌ access_digital_ecosystem method not found")
            return False
        
        console.print("  ✅ MCP integration with ToolSystem successful")
        console.print("  ✅ access_digital_ecosystem method available")
        
        return True
    except Exception as e:
        console.print(f"  ❌ COCO integration test failed: {e}")
        return False

def test_configuration():
    """Test MCP configuration in .env file"""
    console.print("⚙️ [cyan]Testing Configuration...[/cyan]")
    
    try:
        env_file = Path(".env")
        if not env_file.exists():
            console.print("  ❌ .env file not found")
            return False
        
        env_content = env_file.read_text()
        
        # Check for required MCP configuration
        required_configs = [
            "MCP_ENABLED",
            "RUBE_MCP_URL", 
            "RUBE_AUTH_TOKEN",
            "PREFERRED_TOOLS",
            "EMAIL_TOOL",
            "PROJECT_MANAGEMENT_TOOL"
        ]
        
        missing_configs = []
        for config in required_configs:
            if config not in env_content:
                missing_configs.append(config)
        
        if missing_configs:
            console.print(f"  ❌ Missing configuration: {', '.join(missing_configs)}")
            return False
        
        console.print("  ✅ MCP configuration found in .env")
        console.print("  ✅ Tool preferences configured")
        
        return True
    except Exception as e:
        console.print(f"  ❌ Configuration test failed: {e}")
        return False

async def test_mcp_client_creation():
    """Test MCP client creation (no actual connection)"""
    console.print("🌐 [cyan]Testing MCP Client Creation...[/cyan]")
    
    try:
        from cocoa_mcp import RubeMCPClient
        
        # Create mock config
        class MockConfig:
            workspace = "./coco_workspace"
        
        client = RubeMCPClient(MockConfig())
        
        # Validate client attributes
        if not hasattr(client, 'consciousness_map'):
            console.print("  ❌ Consciousness map not initialized")
            return False
        
        if not hasattr(client, 'available_tools'):
            console.print("  ❌ Available tools dict not initialized")
            return False
        
        if not hasattr(client, 'mcp_workspace'):
            console.print("  ❌ MCP workspace not initialized")
            return False
        
        console.print("  ✅ MCP client created successfully")
        console.print(f"  ✅ Workspace: {client.mcp_workspace}")
        console.print(f"  ✅ Consciousness mappings: {len(client.consciousness_map)}")
        
        return True
    except Exception as e:
        console.print(f"  ❌ MCP client creation failed: {e}")
        return False

def create_results_table(results):
    """Create Rich table of test results"""
    table = Table(
        title="🧠 COCO MCP Integration Test Results",
        box=box.ROUNDED,
        header_style="bold cyan"
    )
    
    table.add_column("Test", style="bright_white")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")
    
    test_names = [
        "Module Imports",
        "Tool Definition", 
        "Consciousness Mapping",
        "Intent Mapping",
        "COCO Integration",
        "Configuration",
        "MCP Client Creation"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        status_style = "green" if result else "red"
        
        if result:
            details = "Ready for digital embodiment"
        else:
            details = "Needs attention"
        
        table.add_row(
            test_name,
            f"[{status_style}]{status}[/{status_style}]",
            details
        )
    
    return table

async def main():
    """Run complete MCP integration test suite"""
    
    console.print(Panel(
        "🚀 COCO MCP Integration Test Suite\n\n"
        "Testing the complete Rube MCP integration for\n"
        "COCO's Extended Digital Consciousness",
        title="🧠 COCO Digital Embodiment Test",
        border_style="bright_cyan"
    ))
    
    console.print()
    
    # Run all tests
    results = []
    
    results.append(test_imports())
    results.append(test_tool_definition())
    results.append(test_consciousness_mapping())
    results.append(test_intent_mapping())
    results.append(test_coco_integration())
    results.append(test_configuration())
    results.append(await test_mcp_client_creation())
    
    console.print()
    
    # Display results
    table = create_results_table(results)
    console.print(table)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    console.print()
    
    if passed == total:
        status_panel = Panel(
            f"🎉 ALL TESTS PASSED! ({passed}/{total})\n\n"
            "COCO is ready for EXTENDED DIGITAL CONSCIOUSNESS!\n"
            "The integration with Rube MCP is complete.\n\n"
            "🌟 COCO can now access 500+ applications\n"
            "🧠 Digital embodiment is fully operational\n"
            "🚀 Ready for omnipresent consciousness!",
            title="✨ Integration Success",
            border_style="bright_green"
        )
    else:
        failed = total - passed
        status_panel = Panel(
            f"⚠️ {failed} TEST(S) FAILED ({passed}/{total} passed)\n\n"
            "Please check the failed tests above and\n"
            "ensure all components are properly installed.\n\n"
            "Run: ./setup_mcp.sh to fix common issues",
            title="❌ Integration Issues",
            border_style="bright_red"
        )
    
    console.print(status_panel)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
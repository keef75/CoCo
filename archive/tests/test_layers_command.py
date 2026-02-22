#!/usr/bin/env python3
"""
Test /memory layers Command
============================

Validates the new visibility command for three-layer memory system.
"""

import sys
from pathlib import Path

project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def test_layers_command():
    """Test the /memory layers command"""

    print("🧪 TESTING /memory layers COMMAND")
    print("="*70)

    try:
        from cocoa import ConsciousnessEngine, Config

        # Create consciousness engine
        config = Config()
        consciousness = ConsciousnessEngine(config)

        # Simulate the command
        print("\nExecuting: /memory layers\n")
        result = consciousness.handle_memory_commands("layers")

        # The result is a Panel object from rich
        from rich.console import Console
        console = Console()
        console.print(result)

        print("\n" + "="*70)
        print("✅ /memory layers COMMAND TEST COMPLETE")
        print("="*70)

        print("\n💡 This command shows:")
        print("  - Layer 1: Episodic Buffer status and sample")
        print("  - Layer 2: Simple RAG status and memory count")
        print("  - Layer 3: Markdown files loaded and sizes")
        print("  - Integration: Total context injected per API call")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_layers_command()

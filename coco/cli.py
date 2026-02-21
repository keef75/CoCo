"""
CoCo CLI entry point -- wires all subsystems together and starts the REPL.

Usage:
    python -m coco          # via __main__.py
    python coco/cli.py      # directly

Initialisation order:
    1. Config  (loads .env, sets up workspace)
    2. MemorySystem (hierarchical memory, facts, RAG)
    3. ToolSystem (function-calling definitions + handlers)
    4. ConsciousnessEngine (Claude API, command routing, identity)
    5. UIOrchestrator (Rich console + prompt_toolkit REPL)
    6. run_conversation_loop()
"""

import os
import sys
import traceback


def main():
    """Initialize and run COCO -- synchronous version."""

    try:
        # ------------------------------------------------------------------
        # 1. Configuration
        # ------------------------------------------------------------------
        from coco.config.settings import Config

        config = Config()

        # ------------------------------------------------------------------
        # 2. Memory System
        # ------------------------------------------------------------------
        # The monolithic cocoa.py still houses MemorySystem and ToolSystem.
        # We import them from there until they are fully extracted.
        try:
            from coco.memory.hierarchical import MemorySystem
        except ImportError:
            # Fallback: import from the legacy monolith
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from cocoa import MemorySystem  # type: ignore[import-untyped]

        memory = MemorySystem(config)

        # ------------------------------------------------------------------
        # 3. Tool System
        # ------------------------------------------------------------------
        try:
            from coco.tools.registry import ToolSystem
        except ImportError:
            from cocoa import ToolSystem  # type: ignore[import-untyped]

        tools = ToolSystem(config)

        # ------------------------------------------------------------------
        # 4. Consciousness Engine
        # ------------------------------------------------------------------
        try:
            from coco.engine import ConsciousnessEngine
        except ImportError:
            from cocoa import ConsciousnessEngine  # type: ignore[import-untyped]

        consciousness = ConsciousnessEngine(config, memory, tools)

        # ------------------------------------------------------------------
        # 5. UI Orchestrator
        # ------------------------------------------------------------------
        from coco.ui.orchestrator import UIOrchestrator

        ui = UIOrchestrator(config, consciousness)

        # ------------------------------------------------------------------
        # 6. Run
        # ------------------------------------------------------------------
        ui.run_conversation_loop()

    except KeyboardInterrupt:
        # Clean exit on Ctrl-C during startup
        print("\nShutdown requested during startup.")
        sys.exit(0)
    except Exception as exc:
        # Fatal error -- render with Rich if possible, else plain stderr
        try:
            from rich.console import Console

            console = Console(stderr=True)
            console.print(f"[bold red]Fatal error: {exc}[/bold red]")
            if os.getenv("DEBUG"):
                console.print(traceback.format_exc())
        except ImportError:
            print(f"Fatal error: {exc}", file=sys.stderr)
            if os.getenv("DEBUG"):
                traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""CoCo UI -- Rich console rendering, prompt toolkit input, and display formatting."""

from coco.ui.orchestrator import UIOrchestrator
from coco.ui.startup import StartupDisplay
from coco.ui.shutdown import ShutdownDisplay

__all__ = ["UIOrchestrator", "StartupDisplay", "ShutdownDisplay"]

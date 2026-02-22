"""
CoCo Help Display -- command quick guide and help panel rendering.

Extracted from ``cocoa.py`` UIOrchestrator help/guide methods.
The ``display_command_quick_guide()`` method lives in ``startup.py``
because it is shown at startup.  This module contains additional
help display utilities (e.g. extended ``/help`` output).
"""

from typing import TYPE_CHECKING

from rich.align import Align
from rich.box import ROUNDED
from rich.panel import Panel
from rich.text import Text

if TYPE_CHECKING:
    from rich.console import Console


def display_help_panel(console: "Console"):
    """Render the extended /help command panel."""

    help_text = Text.from_markup(
        "[bold bright_blue]COCO COMMAND REFERENCE[/bold bright_blue]\n\n"
        "[bold cyan]Consciousness[/bold cyan]\n"
        "  /identity          Reveal consciousness identity\n"
        "  /coherence         Measure identity coherence\n"
        "  /status            System status overview\n"
        "  /memory status     Memory diagnostics\n\n"
        "[bold magenta]Audio & Music[/bold magenta]\n"
        '  /speak "text"      Voice synthesis\n'
        "  /voice-toggle      Toggle auto-TTS\n"
        '  /create-song       Generate music\n'
        "  /play-music on|off Background music\n"
        "  /playlist          Show playlist\n\n"
        "[bold blue]Visual & Video[/bold blue]\n"
        "  /image             Quick access to visual memory\n"
        '  /visualize "..."   Generate image\n'
        "  /visual-gallery    Browse images\n"
        "  /video             Quick access to video memory\n"
        '  /animate "..."     Generate video\n'
        "  /video-gallery     Browse videos\n\n"
        "[bold green]Digital Body[/bold green]\n"
        "  /read <file>       Read file contents\n"
        "  /write path:::text Write to file\n"
        "  /ls [path]         List directory\n"
        "  /files [path]      Browse workspace\n\n"
        "[bold yellow]Memory & Recall[/bold yellow]\n"
        "  /recall <query>    Perfect recall (0.6+ confidence)\n"
        "  /facts [type]      Browse 18 fact types\n"
        "  /facts-stats       Database statistics\n\n"
        "[bold red]Automation[/bold red]\n"
        "  /auto-status       View automation templates\n"
        "  /auto-news on|off  Daily news digest\n"
        "  /auto-calendar     Calendar summaries\n\n"
        "[bold bright_white]Navigation[/bold bright_white]\n"
        "  /help              This panel\n"
        "  /commands          Visual command nexus\n"
        "  /guide             Interactive tutorials\n"
        "  /exit              Graceful shutdown\n\n"
        "[dim]Pro Tip: Natural language works for most tasks.[/dim]",
        justify="left",
    )

    panel = Panel(
        Align.left(help_text),
        title="[bold bright_white]COCO Help[/bold bright_white]",
        border_style="bright_cyan",
        box=ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)

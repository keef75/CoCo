#!/usr/bin/env python3
"""
Final Integration Test - Verify COCO uses real Google Workspace APIs
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

console = Console()

# Load environment
load_dotenv()

# Import COCO components
sys.path.insert(0, str(Path(__file__).parent))
from cocoa import Config, ToolSystem

def test_google_workspace_integration():
    """Test that COCO properly initializes Google Workspace with OAuth"""

    console.print(Panel(
        "[bold cyan]Testing COCO Google Workspace Integration[/bold cyan]\n\n"
        "[yellow]This will verify:[/yellow]\n"
        "• OAuth credentials are loaded\n"
        "• GoogleWorkspaceConsciousness initializes correctly\n"
        "• authenticated property returns True\n"
        "• Gmail Bridge is NOT used\n"
        "• All Drive methods are available",
        title="🧪 Integration Test",
        border_style="cyan"
    ))

    try:
        # Initialize COCO config
        console.print("\n[cyan]1. Initializing COCO configuration...[/cyan]")
        config = Config()
        console.print("[green]✅ Config initialized[/green]")

        # Initialize ToolSystem (this includes Google Workspace)
        console.print("\n[cyan]2. Initializing ToolSystem (includes Google Workspace)...[/cyan]")
        tools = ToolSystem(config)
        console.print("[green]✅ ToolSystem initialized[/green]")

        # Check if Google Workspace is available
        console.print("\n[cyan]3. Checking Google Workspace availability...[/cyan]")
        if not tools.google_workspace:
            console.print("[red]❌ Google Workspace not initialized[/red]")
            return False

        console.print("[green]✅ Google Workspace object exists[/green]")

        # Check authenticated property
        console.print("\n[cyan]4. Checking authenticated property...[/cyan]")
        if not hasattr(tools.google_workspace, 'authenticated'):
            console.print("[red]❌ authenticated property missing[/red]")
            return False

        is_authenticated = tools.google_workspace.authenticated
        console.print(f"[green]✅ authenticated property exists: {is_authenticated}[/green]")

        if not is_authenticated:
            console.print("[yellow]⚠️ Not authenticated - may be using Gmail Bridge fallback[/yellow]")
            console.print(f"[yellow]Simplified mode: {tools.google_workspace.simplified_mode}[/yellow]")
            return False

        # Check for Gmail Bridge (should NOT be present)
        console.print("\n[cyan]5. Checking Gmail Bridge is NOT active...[/cyan]")
        if hasattr(tools, 'gmail_bridge') and tools.gmail_bridge is not None:
            console.print("[red]❌ Gmail Bridge is active (should not be)[/red]")
            return False

        console.print("[green]✅ Gmail Bridge not active (good!)[/green]")

        # Check Google API services are initialized
        console.print("\n[cyan]6. Checking Google API services...[/cyan]")
        if not tools.google_workspace.docs_service:
            console.print("[red]❌ Docs service not initialized[/red]")
            return False
        console.print("[green]✅ Docs service initialized[/green]")

        if not tools.google_workspace.sheets_service:
            console.print("[red]❌ Sheets service not initialized[/red]")
            return False
        console.print("[green]✅ Sheets service initialized[/green]")

        if not tools.google_workspace.drive_service:
            console.print("[red]❌ Drive service not initialized[/red]")
            return False
        console.print("[green]✅ Drive service initialized[/green]")

        # Check Drive methods are available in GoogleWorkspaceConsciousness class
        console.print("\n[cyan]7. Checking Drive methods in class definition...[/cyan]")
        from google_workspace_consciousness import GoogleWorkspaceConsciousness
        drive_methods = ['upload_file', 'create_folder', 'download_file', 'delete_file', 'list_files']
        for method in drive_methods:
            if hasattr(GoogleWorkspaceConsciousness, method):
                console.print(f"[green]✅ {method} defined in GoogleWorkspaceConsciousness class[/green]")
            else:
                console.print(f"[red]❌ Method {method} missing from class[/red]")
                return False

        # Check COCO tool wrappers are available
        console.print("\n[cyan]8. Checking COCO tool wrappers...[/cyan]")
        tool_wrappers = ['upload_to_drive', 'create_drive_folder', 'download_from_drive',
                        'delete_from_drive', 'list_drive_files']
        for wrapper in tool_wrappers:
            if not hasattr(tools, wrapper):
                console.print(f"[red]❌ Tool wrapper {wrapper} missing[/red]")
                return False
            console.print(f"[green]✅ {wrapper} available[/green]")

        # Success!
        console.print("\n")
        console.print(Panel(
            "[bold green]🎉 ALL TESTS PASSED![/bold green]\n\n"
            "✅ OAuth credentials loaded correctly\n"
            "✅ Google Workspace authenticated\n"
            "✅ Real Google APIs active (not Gmail Bridge)\n"
            "✅ Docs, Sheets, Drive services initialized\n"
            "✅ All Drive file operations available\n\n"
            "[cyan]COCO is ready to create real Google Docs, Sheets, and manage Drive files![/cyan]",
            title="✨ Integration Test Results",
            border_style="green"
        ))

        return True

    except Exception as e:
        console.print(f"\n[red]❌ Test failed: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False

if __name__ == "__main__":
    success = test_google_workspace_integration()
    sys.exit(0 if success else 1)

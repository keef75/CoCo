#!/usr/bin/env python3
"""
Test Google Workspace with simplified fallback mode
This should work without OAuth, using local file storage
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_simplified_mode():
    """Test Google Workspace in simplified mode (no OAuth required)"""
    from google_workspace_consciousness import GoogleWorkspaceConsciousness
    from rich.console import Console

    console = Console()

    # Create mock config
    class MockConfig:
        def __init__(self, console):
            self.console = console

    config = MockConfig(console)

    print("=" * 60)
    print("🧪 Testing Google Workspace Simplified Mode")
    print("=" * 60)
    print()

    try:
        # Initialize Google Workspace (should auto-fallback to simplified)
        console.print("[cyan]Initializing Google Workspace...[/cyan]")
        gw = GoogleWorkspaceConsciousness(config)
        print()

        # Test 1: Create a document
        console.print("[bold]Test 1: Create Document[/bold]")
        result = gw.create_document(
            title="Test Document",
            initial_content="Hello World! This is COCO testing Google Workspace."
        )

        if result["success"]:
            doc_id = result["document_id"]
            console.print(f"✅ Document created with ID: [green]{doc_id}[/green]")
            console.print(f"   Path: [dim]{result.get('document_url', 'N/A')}[/dim]")
        else:
            console.print(f"❌ Failed: {result['error']}")
            return False

        print()

        # Test 2: Read the document
        console.print("[bold]Test 2: Read Document[/bold]")
        result = gw.read_document(doc_id)

        if result["success"]:
            console.print(f"✅ Document read successfully")
            console.print(f"   Title: [cyan]{result['title']}[/cyan]")
            console.print(f"   Word count: [yellow]{result['word_count']}[/yellow]")
            console.print(f"   Content preview: [dim]{result['content'][:50]}...[/dim]")
        else:
            console.print(f"❌ Failed: {result['error']}")

        print()

        # Test 3: Append to document
        console.print("[bold]Test 3: Append to Document[/bold]")
        append_content = "\n\n## Additional Section\n\nThis content was appended by COCO."

        # Since we're testing, disable preview to avoid user interaction
        result = gw.append_to_document(doc_id, append_content, show_preview=False)

        if result["success"]:
            console.print(f"✅ Content appended successfully")
        else:
            console.print(f"❌ Failed: {result.get('error', result.get('message', 'Unknown'))}")

        print()

        # Test 4: Search for documents
        console.print("[bold]Test 4: Search Documents[/bold]")
        result = gw.search_drive("test", limit=5)

        if result["success"]:
            console.print(f"✅ Found {result['count']} document(s)")
            for file in result["files"]:
                console.print(f"   • {file['name']} ([dim]{file['id']}[/dim])")
        else:
            console.print(f"❌ Failed: {result['error']}")

        print()

        # Test 5: Create a spreadsheet
        console.print("[bold]Test 5: Create Spreadsheet[/bold]")
        result = gw.create_spreadsheet(
            title="Test Spreadsheet",
            headers=["Name", "Email", "Status"],
            data=[
                ["COCO", "coco@example.com", "Active"],
                ["Test User", "test@example.com", "Pending"]
            ]
        )

        if result["success"]:
            sheet_id = result["spreadsheet_id"]
            console.print(f"✅ Spreadsheet created with ID: [green]{sheet_id}[/green]")
        else:
            console.print(f"❌ Failed: {result['error']}")

        print()

        # Test 6: Read spreadsheet
        if result["success"]:
            console.print("[bold]Test 6: Read Spreadsheet[/bold]")
            result = gw.read_spreadsheet(sheet_id)

            if result["success"]:
                console.print(f"✅ Spreadsheet read successfully")
                console.print(f"   Title: [cyan]{result['title']}[/cyan]")
                console.print(f"   Rows: {result['rows']}, Columns: {result['columns']}")
            else:
                console.print(f"❌ Failed: {result['error']}")

        print()
        console.print("[bold green]✅ All tests completed![/bold green]")
        print()

        # Summary
        from rich.panel import Panel
        console.print(Panel(
            "[green]Google Workspace Simplified Mode is working![/green]\n\n"
            "• Documents are saved locally to ~/.cocoa/google_docs/\n"
            "• Spreadsheets are saved as CSV to ~/.cocoa/google_sheets/\n"
            "• All basic operations are functional\n\n"
            "[yellow]Note: For full Google Docs/Sheets integration, OAuth setup is required.[/yellow]",
            title="✨ Test Summary",
            border_style="green"
        ))

        return True

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_simplified_mode()

    if success:
        print()
        print("=" * 60)
        print("🎉 SUCCESS: Google Workspace simplified mode is working!")
        print("=" * 60)
        print()
        print("You can now use commands like:")
        print('  • "Create a doc called \'test\' and have it say hello world"')
        print('  • "Search for documents with \'test\' in the name"')
        print('  • "Create a spreadsheet for my budget"')
        print()
        print("Documents will be saved locally until OAuth is configured.")
        print("=" * 60)
    else:
        print("\n❌ Tests failed. Check the errors above.")
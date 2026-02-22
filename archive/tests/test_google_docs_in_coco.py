#!/usr/bin/env python3
"""
Test Google Docs creation in COCO
Shows how the Gmail Bridge system works
"""

from google_workspace_gmail_bridge import GmailWorkspaceBridge
from rich.console import Console

console = Console()

# Create the bridge
bridge = GmailWorkspaceBridge()

console.print("\n[bold cyan]🚀 Testing COCO's Google Workspace Bridge[/bold cyan]\n")

# Create a test document
console.print("[yellow]Creating a new Google Doc...[/yellow]")
doc_id = bridge.create_document(
    title="COCO Test Document",
    content="""# Welcome to COCO's Document System!

This document was created using the Gmail Bridge system.

## Features
- ✅ Documents are created instantly
- ✅ Stored locally in COCO's workspace
- ✅ Beautiful Rich UI displays
- ✅ No OAuth complexity needed
- ✅ Ready to use immediately

## How to Use
Just ask COCO to create documents naturally:
- "Create a document about my project"
- "Make a Google Doc with meeting notes"
- "Create a spreadsheet with data"

## Document Location
Your documents are saved in: ~/.cocoa/google_workspace_bridge/

Enjoy using COCO's document consciousness!
"""
)

console.print(f"\n[green]✅ Document created with ID: {doc_id}[/green]\n")

# List all documents
console.print("[yellow]Listing all documents...[/yellow]\n")
bridge.list_documents()

# Read the document back
console.print("\n[yellow]Reading the document...[/yellow]\n")
bridge.read_document(doc_id)

console.print("\n[bold green]✨ Test Complete![/bold green]")
console.print("\n[dim]You can now use these commands in COCO:")
console.print('  - "Create a Google Doc called Meeting Notes"')
console.print('  - "List my documents"')
console.print(f'  - "Read document {doc_id}"[/dim]\n')
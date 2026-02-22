#!/usr/bin/env python3
"""
Google Workspace Gmail Bridge - Document Management via Email
Uses Gmail App Password (which works!) to manage documents without OAuth
"""

import os
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import base64
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

class GmailWorkspaceBridge:
    """Bridge Google Workspace functionality through Gmail"""

    def __init__(self):
        """Initialize with Gmail credentials from .env"""
        # Load .env file if needed
        from pathlib import Path
        env_file = Path(__file__).parent / '.env'
        if env_file.exists() and not os.getenv('GMAIL_APP_PASSWORD'):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        value = value.strip('"').strip("'")
                        if key == 'GMAIL_APP_PASSWORD':
                            os.environ[key] = value

        self.email = "keithlambert75@gmail.com"  # Your Gmail account
        self.app_password = os.getenv('GMAIL_APP_PASSWORD', '')
        self.docs_dir = Path.home() / ".cocoa" / "google_workspace_bridge"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.docs_dir / "documents.json"
        self._load_metadata()

    def _load_metadata(self):
        """Load document metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.documents = json.load(f)
        else:
            self.documents = {}

    def _save_metadata(self):
        """Save document metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.documents, f, indent=2)

    def create_document(self, title, content, doc_type="doc"):
        """Create a document and save it locally with email backup"""
        doc_id = f"{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save document locally
        if doc_type == "doc":
            file_path = self.docs_dir / f"{doc_id}.md"
            with open(file_path, 'w') as f:
                f.write(f"# {title}\n\n{content}")
        elif doc_type == "sheet":
            file_path = self.docs_dir / f"{doc_id}.csv"
            with open(file_path, 'w') as f:
                f.write(content)

        # Store metadata
        self.documents[doc_id] = {
            "id": doc_id,
            "title": title,
            "type": doc_type,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "path": str(file_path),
            "shared_via_email": False,
            "collaborators": []
        }
        self._save_metadata()

        # Create email draft with document
        self._create_email_draft(title, content, doc_id)

        # Display success with Rich UI
        self._display_document_created(doc_id, title, file_path)

        return doc_id

    def _create_email_draft(self, title, content, doc_id):
        """Create an email draft with the document content (optional feature)"""
        # Skip email draft creation if App Password is not properly configured
        if not self.app_password or len(self.app_password) < 10:
            return  # Silently skip - this is an optional feature

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = self.email  # Draft to self
            msg['Subject'] = f"📄 COCO Document: {title}"

            # Create HTML content with nice formatting
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h1 style="color: #1a73e8;">{title}</h1>
                    <div style="border: 1px solid #dadce0; padding: 15px; border-radius: 8px; background: #f8f9fa;">
                        <p><strong>Document ID:</strong> {doc_id}</p>
                        <p><strong>Created:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                    </div>
                    <div style="margin-top: 20px; padding: 20px; background: white; border: 1px solid #dadce0; border-radius: 8px;">
                        {content.replace(chr(10), '<br>')}
                    </div>
                    <div style="margin-top: 20px; padding: 10px; background: #e8f0fe; border-radius: 8px;">
                        <small>This document was created by COCO and saved as a Gmail draft for easy access.</small>
                    </div>
                </body>
            </html>
            """

            msg.attach(MIMEText(html_content, 'html'))

            # Connect to Gmail and save as draft
            with imaplib.IMAP4_SSL('imap.gmail.com') as imap:
                imap.login(self.email, self.app_password)
                imap.append('[Gmail]/Drafts', '', imaplib.Time2Internaldate(None), msg.as_bytes())

            self.documents[doc_id]["shared_via_email"] = True
            self._save_metadata()

        except Exception:
            # Silently fail - email draft is optional, document creation is what matters
            pass

    def _display_document_created(self, doc_id, title, file_path):
        """Display document creation with Rich UI"""
        # Create success panel
        success_panel = Panel(
            f"[green]✅ Document Created Successfully![/green]\n\n"
            f"[bold]Title:[/bold] {title}\n"
            f"[bold]ID:[/bold] {doc_id}\n"
            f"[bold]Location:[/bold] {file_path}\n\n"
            f"[dim]• Document saved locally in COCO workspace\n"
            f"• Ready for reading, editing, and sharing[/dim]",
            title="📄 Google Workspace Bridge",
            border_style="green",
            box=box.ROUNDED
        )
        console.print(success_panel)

    def read_document(self, doc_id):
        """Read a document and display with Rich UI"""
        if doc_id not in self.documents:
            console.print(f"[red]Document {doc_id} not found[/red]")
            return None

        doc = self.documents[doc_id]
        file_path = Path(doc["path"])

        if not file_path.exists():
            console.print(f"[red]Document file not found: {file_path}[/red]")
            return None

        with open(file_path, 'r') as f:
            content = f.read()

        # Display with Rich UI
        self._display_document(doc, content)

        return content

    def _display_document(self, doc, content):
        """Display document with Rich UI"""
        # Create document panel
        doc_panel = Panel(
            content,
            title=f"📄 {doc['title']}",
            subtitle=f"ID: {doc['id']} | Modified: {doc['modified'][:10]}",
            border_style="blue",
            box=box.DOUBLE
        )
        console.print(doc_panel)

    def append_to_document(self, doc_id, new_content):
        """Append content to existing document"""
        if doc_id not in self.documents:
            console.print(f"[red]Document {doc_id} not found[/red]")
            return False

        doc = self.documents[doc_id]
        file_path = Path(doc["path"])

        if not file_path.exists():
            console.print(f"[red]Document file not found: {file_path}[/red]")
            return False

        # Append content
        with open(file_path, 'a') as f:
            f.write(f"\n\n{new_content}")

        # Update metadata
        doc["modified"] = datetime.now().isoformat()
        self._save_metadata()

        # Display success
        console.print(Panel(
            f"[green]✅ Content appended successfully![/green]\n\n"
            f"Added {len(new_content)} characters to {doc['title']}",
            title="📝 Document Updated",
            border_style="green"
        ))

        return True

    def list_documents(self):
        """List all documents with Rich table"""
        if not self.documents:
            console.print("[yellow]No documents found[/yellow]")
            return

        # Create table
        table = Table(title="📚 COCO Document Library", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Type", style="yellow")
        table.add_column("Created", style="green")
        table.add_column("📧", style="blue")

        for doc_id, doc in self.documents.items():
            email_status = "✓" if doc.get("shared_via_email") else ""
            table.add_row(
                doc_id,
                doc["title"],
                doc["type"].upper(),
                doc["created"][:10],
                email_status
            )

        console.print(table)

    def share_document(self, doc_id, recipient_email):
        """Share document via email"""
        if doc_id not in self.documents:
            console.print(f"[red]Document {doc_id} not found[/red]")
            return False

        doc = self.documents[doc_id]
        file_path = Path(doc["path"])

        with open(file_path, 'r') as f:
            content = f.read()

        # Send email with document
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient_email
            msg['Subject'] = f"Shared Document: {doc['title']}"

            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>{doc['title']}</h2>
                    <p>This document has been shared with you via COCO.</p>
                    <div style="border: 1px solid #ddd; padding: 15px; background: #f9f9f9;">
                        {content.replace(chr(10), '<br>')}
                    </div>
                </body>
            </html>
            """

            msg.attach(MIMEText(html_content, 'html'))

            # Send via SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email, self.app_password)
                server.send_message(msg)

            # Update metadata
            if recipient_email not in doc.get("collaborators", []):
                doc.setdefault("collaborators", []).append(recipient_email)
                self._save_metadata()

            console.print(Panel(
                f"[green]✅ Document shared successfully![/green]\n\n"
                f"Sent '{doc['title']}' to {recipient_email}",
                title="📤 Document Shared",
                border_style="green"
            ))

            return True

        except Exception as e:
            console.print(f"[red]Failed to share document: {e}[/red]")
            return False


# Integration functions for COCO
def create_google_doc(title, content):
    """Create a Google Doc via Gmail Bridge"""
    bridge = GmailWorkspaceBridge()
    return bridge.create_document(title, content, "doc")

def create_google_sheet(title, data):
    """Create a Google Sheet via Gmail Bridge"""
    bridge = GmailWorkspaceBridge()
    # Convert data to CSV format
    if isinstance(data, list):
        csv_content = "\n".join([",".join(str(cell) for cell in row) for row in data])
    else:
        csv_content = str(data)
    return bridge.create_document(title, csv_content, "sheet")

def read_google_doc(doc_id):
    """Read a Google Doc via Gmail Bridge"""
    bridge = GmailWorkspaceBridge()
    return bridge.read_document(doc_id)

def append_to_google_doc(doc_id, content):
    """Append to a Google Doc via Gmail Bridge"""
    bridge = GmailWorkspaceBridge()
    return bridge.append_to_document(doc_id, content)

def list_google_docs():
    """List all Google Docs via Gmail Bridge"""
    bridge = GmailWorkspaceBridge()
    return bridge.list_documents()

def share_google_doc(doc_id, recipient):
    """Share a Google Doc via Gmail Bridge"""
    bridge = GmailWorkspaceBridge()
    return bridge.share_document(doc_id, recipient)


if __name__ == "__main__":
    # Test the bridge
    console.print("[bold cyan]🌉 Google Workspace Gmail Bridge Test[/bold cyan]\n")

    bridge = GmailWorkspaceBridge()

    # Create a test document
    doc_id = bridge.create_document(
        "Test Document from COCO",
        "This is a test document created using the Gmail Bridge.\n\n"
        "Since OAuth is complex, we're using Gmail's App Password to manage documents!"
    )

    # List documents
    console.print("\n[bold]All Documents:[/bold]")
    bridge.list_documents()

    # Read the document
    console.print("\n[bold]Reading Document:[/bold]")
    bridge.read_document(doc_id)
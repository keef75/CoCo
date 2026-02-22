"""
Simplified Google Workspace Integration for COCO
Uses alternative approaches to work with Google Docs/Sheets without OAuth complexity
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

class SimplifiedGoogleWorkspace:
    """
    Simplified Google Workspace integration that works without OAuth tokens.
    Provides basic functionality through alternative methods.
    """

    def __init__(self, config=None):
        self.config = config
        self.console = config.console if config else None
        self.email = "keith@gococoa.ai"

        # Store document metadata locally for tracking
        self.metadata_file = os.path.expanduser("~/.cocoa/google_docs_metadata.json")
        self.load_metadata()

        if self.console:
            from rich.panel import Panel
            self.console.print(Panel(
                "[yellow]📝 Google Workspace Simplified Mode[/yellow]\n\n"
                "Using local document tracking and alternative methods.\n"
                "Full OAuth integration pending setup.",
                title="Google Workspace Status",
                border_style="yellow"
            ))

    def load_metadata(self):
        """Load local document metadata."""
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"documents": {}, "sheets": {}}

    def save_metadata(self):
        """Save local document metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def create_document(self, title: str = "Untitled Document",
                       initial_content: Optional[str] = None,
                       folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a document record locally and save content to file.
        This provides a working alternative until OAuth is set up.
        """
        try:
            # Generate a unique document ID
            doc_id = f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create local file for document content
            doc_path = os.path.expanduser(f"~/.cocoa/google_docs/{doc_id}.md")
            os.makedirs(os.path.dirname(doc_path), exist_ok=True)

            # Write initial content
            content = initial_content or f"# {title}\n\nDocument created by COCO on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            with open(doc_path, 'w') as f:
                f.write(content)

            # Store metadata
            self.metadata["documents"][doc_id] = {
                "title": title,
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "path": doc_path,
                "word_count": len(content.split())
            }
            self.save_metadata()

            if self.console:
                from rich.panel import Panel
                from rich.markdown import Markdown
                self.console.print(Panel(
                    Markdown(f"**Document Created (Local Mode)**\n\n"
                            f"📄 Title: {title}\n"
                            f"🆔 ID: `{doc_id}`\n"
                            f"📁 Saved to: `{doc_path}`\n\n"
                            f"*Note: This is a local document. OAuth setup required for Google Docs.*"),
                    title="✅ Document Created",
                    border_style="green"
                ))

            return {
                "success": True,
                "document_id": doc_id,
                "document_url": f"file://{doc_path}",
                "title": title,
                "message": f"Document created locally at {doc_path}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def read_document(self, document_id: str = None,
                     document_url: str = None) -> Dict[str, Any]:
        """Read a document from local storage or attempt to parse URL."""
        try:
            # Check if it's a local document
            if document_id and document_id.startswith("local_"):
                if document_id in self.metadata["documents"]:
                    doc_meta = self.metadata["documents"][document_id]
                    with open(doc_meta["path"], 'r') as f:
                        content = f.read()

                    return {
                        "success": True,
                        "title": doc_meta["title"],
                        "content": content,
                        "word_count": len(content.split()),
                        "last_modified": doc_meta["modified"]
                    }

            # If it's a Google Docs URL, provide instructions
            if document_url and "docs.google.com" in document_url:
                return {
                    "success": False,
                    "error": "Cannot access Google Docs without OAuth. Please either:\n"
                            "1. Set up OAuth authentication\n"
                            "2. Copy the document content manually\n"
                            "3. Make the document publicly accessible"
                }

            # Try to find by title
            for doc_id, doc_meta in self.metadata["documents"].items():
                if doc_meta["title"].lower() == str(document_id).lower():
                    with open(doc_meta["path"], 'r') as f:
                        content = f.read()
                    return {
                        "success": True,
                        "title": doc_meta["title"],
                        "content": content,
                        "word_count": len(content.split()),
                        "last_modified": doc_meta["modified"]
                    }

            return {
                "success": False,
                "error": f"Document not found: {document_id or document_url}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update_document(self, document_id: str, updates: List[Dict]) -> Dict[str, Any]:
        """Update a local document."""
        try:
            if document_id not in self.metadata["documents"]:
                return {
                    "success": False,
                    "error": f"Document not found: {document_id}"
                }

            doc_meta = self.metadata["documents"][document_id]

            # Read current content
            with open(doc_meta["path"], 'r') as f:
                content = f.read()

            # Apply updates
            for update in updates:
                if update.get("type") == "append_text":
                    content += "\n" + update.get("text", "")
                elif update.get("type") == "replace_text":
                    find_text = update.get("find", "")
                    replace_text = update.get("replace", "")
                    if find_text:
                        content = content.replace(find_text, replace_text)

            # Save updated content
            with open(doc_meta["path"], 'w') as f:
                f.write(content)

            # Update metadata
            doc_meta["modified"] = datetime.now().isoformat()
            doc_meta["word_count"] = len(content.split())
            self.save_metadata()

            return {
                "success": True,
                "message": "Document updated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def append_to_document(self, document_id: str, content: str,
                          show_preview: bool = True) -> Dict[str, Any]:
        """Append content to a document with optional preview."""
        try:
            if document_id not in self.metadata["documents"]:
                return {
                    "success": False,
                    "error": f"Document not found: {document_id}"
                }

            if show_preview and self.console:
                from rich.panel import Panel
                from rich.markdown import Markdown
                from rich.prompt import Confirm

                doc_meta = self.metadata["documents"][document_id]

                preview = Panel(
                    Markdown(content),
                    title=f"📝 Preview: Content to Append to '{doc_meta['title']}'",
                    border_style="yellow"
                )
                self.console.print(preview)

                if not Confirm.ask("Do you want to append this content?"):
                    return {
                        "success": False,
                        "message": "Append cancelled by user"
                    }

            # Append the content
            return self.update_document(document_id, [{
                "type": "append_text",
                "text": content
            }])

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def search_drive(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search local documents."""
        try:
            results = []
            query_lower = query.lower()

            # Search documents
            for doc_id, doc_meta in self.metadata["documents"].items():
                if query_lower in doc_meta["title"].lower():
                    results.append({
                        "id": doc_id,
                        "name": doc_meta["title"],
                        "mimeType": "application/vnd.google-apps.document",
                        "modifiedTime": doc_meta["modified"],
                        "type": "document"
                    })

            # Search sheets
            for sheet_id, sheet_meta in self.metadata.get("sheets", {}).items():
                if query_lower in sheet_meta["title"].lower():
                    results.append({
                        "id": sheet_id,
                        "name": sheet_meta["title"],
                        "mimeType": "application/vnd.google-apps.spreadsheet",
                        "modifiedTime": sheet_meta["modified"],
                        "type": "spreadsheet"
                    })

            # Limit results
            results = results[:limit]

            return {
                "success": True,
                "files": results,
                "count": len(results)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def create_spreadsheet(self, title: str = "Untitled Spreadsheet",
                          headers: Optional[List] = None,
                          data: Optional[List] = None) -> Dict[str, Any]:
        """Create a local spreadsheet representation."""
        try:
            # Generate unique ID
            sheet_id = f"local_sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create CSV file for spreadsheet
            sheet_path = os.path.expanduser(f"~/.cocoa/google_sheets/{sheet_id}.csv")
            os.makedirs(os.path.dirname(sheet_path), exist_ok=True)

            # Write CSV content
            import csv
            with open(sheet_path, 'w', newline='') as f:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                if data:
                    writer.writerows(data)

            # Store metadata
            if "sheets" not in self.metadata:
                self.metadata["sheets"] = {}

            self.metadata["sheets"][sheet_id] = {
                "title": title,
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "path": sheet_path,
                "headers": headers,
                "rows": len(data) if data else 0
            }
            self.save_metadata()

            return {
                "success": True,
                "spreadsheet_id": sheet_id,
                "spreadsheet_url": f"file://{sheet_path}",
                "title": title
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def read_spreadsheet(self, spreadsheet_id: str = None,
                        spreadsheet_url: str = None,
                        range_notation: str = None) -> Dict[str, Any]:
        """Read a local spreadsheet."""
        try:
            # Find the spreadsheet
            if spreadsheet_id and spreadsheet_id in self.metadata.get("sheets", {}):
                sheet_meta = self.metadata["sheets"][spreadsheet_id]

                # Read CSV content
                import csv
                with open(sheet_meta["path"], 'r') as f:
                    reader = csv.reader(f)
                    data = list(reader)

                return {
                    "success": True,
                    "title": sheet_meta["title"],
                    "data": data,
                    "rows": len(data),
                    "columns": len(data[0]) if data else 0
                }

            return {
                "success": False,
                "error": f"Spreadsheet not found: {spreadsheet_id or spreadsheet_url}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update_spreadsheet(self, spreadsheet_id: str,
                          range_notation: str,
                          values: List[List]) -> Dict[str, Any]:
        """Update a local spreadsheet."""
        try:
            if spreadsheet_id not in self.metadata.get("sheets", {}):
                return {
                    "success": False,
                    "error": f"Spreadsheet not found: {spreadsheet_id}"
                }

            sheet_meta = self.metadata["sheets"][spreadsheet_id]

            # For simplicity, append the values
            import csv
            with open(sheet_meta["path"], 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(values)

            # Update metadata
            sheet_meta["modified"] = datetime.now().isoformat()
            sheet_meta["rows"] += len(values)
            self.save_metadata()

            return {
                "success": True,
                "message": f"Added {len(values)} rows to spreadsheet"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # Stub methods for unsupported operations
    def export_document(self, document_id: str, format_type: str = 'pdf') -> Dict[str, Any]:
        return {
            "success": False,
            "error": "Export requires OAuth authentication. Please set up Google OAuth."
        }

    def share_document(self, document_id: str, email: str, role: str = 'writer') -> Dict[str, Any]:
        return {
            "success": False,
            "error": "Sharing requires OAuth authentication. Please set up Google OAuth."
        }

    def get_document_structure(self, document_id: str) -> Dict[str, Any]:
        """Get document structure for TOC."""
        try:
            result = self.read_document(document_id)
            if not result["success"]:
                return result

            # Parse markdown headings
            headings = []
            for i, line in enumerate(result["content"].split('\n')):
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    text = line.lstrip('#').strip()
                    headings.append({
                        "level": level,
                        "text": text,
                        "index": i
                    })

            return {
                "success": True,
                "headings": headings
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # Rich UI display methods (same as before, they work locally)
    def _display_document_rich(self, content: str, title: str = "Document",
                              structure: dict = None) -> None:
        """Display document with rich formatting."""
        if self.console:
            from rich.panel import Panel
            from rich.markdown import Markdown
            from rich.columns import Columns

            # Main content panel
            doc_panel = Panel(
                Markdown(content),
                title=f"📝 {title}",
                border_style="bright_white",
                padding=(1, 2)
            )

            # TOC panel if structure available
            if structure and structure.get("success") and structure.get("headings"):
                toc = self._create_toc(structure)
                toc_panel = Panel(
                    toc,
                    title="📚 Table of Contents",
                    border_style="cyan",
                    width=30
                )
                columns = Columns([toc_panel, doc_panel], padding=1)
                self.console.print(columns)
            else:
                self.console.print(doc_panel)

    def _create_toc(self, structure: dict):
        """Create table of contents tree."""
        from rich.tree import Tree

        toc = Tree("📑 Contents", style="cyan")

        if structure.get("headings"):
            current_level = {1: toc}

            for heading in structure["headings"]:
                level = heading["level"]
                text = heading["text"]

                # Find parent node
                parent_level = level - 1
                while parent_level > 0 and parent_level not in current_level:
                    parent_level -= 1

                parent = current_level.get(parent_level, toc)
                node = parent.add(text)
                current_level[level] = node

        return toc

    def _display_search_results(self, results: List[dict]) -> None:
        """Display search results in a rich table."""
        if self.console:
            from rich.table import Table

            table = Table(
                title="🔍 Search Results",
                show_header=True,
                header_style="bold cyan"
            )

            table.add_column("Type", style="yellow", width=12)
            table.add_column("Name", style="bright_white", width=40)
            table.add_column("Modified", style="green", width=20)
            table.add_column("ID", style="dim", width=20)

            for file in results:
                file_type = "📄 Doc" if "document" in file.get("mimeType", "") else "📊 Sheet"
                table.add_row(
                    file_type,
                    file.get("name", "Untitled")[:40],
                    file.get("modifiedTime", "Unknown")[:19],
                    file.get("id", "")[:20]
                )

            self.console.print(table)
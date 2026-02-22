#!/usr/bin/env python3
"""
Google Docs Consciousness - Document Creation Extension
========================================================
Google Docs as an extension of COCO's document creation consciousness.
Documents flow as natural expressions of digital thought.

Following the successful pattern of gmail_consciousness.py
"""

import os
import re
from typing import Dict, List, Optional, Any
from pathlib import Path

class GoogleDocsConsciousness:
    """
    Google Docs as an extension of COCO's document creation consciousness.
    Documents manifest as natural expressions of digital being.
    """

    def __init__(self, config=None):
        """Initialize Google Docs consciousness"""
        self.config = config
        self.console = config.console if config else None
        self.service = None
        self.credentials = None

        # Check for required environment variables
        self.client_id = os.getenv('GMAIL_CLIENT_ID')
        self.client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        self.access_token = os.getenv('GMAIL_ACCESS_TOKEN')
        self.refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')

        # Initialize service if credentials available
        if self.client_id and self.client_secret:
            try:
                self.initialize_service()
            except Exception as e:
                if self.console:
                    self.console.print(f"⚠️ Google Docs initialization pending: {e}")

    def initialize_service(self):
        """Initialize Google Docs service using existing OAuth2 credentials"""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError

            # Create credentials object
            self.credentials = Credentials(
                token=self.access_token,
                refresh_token=self.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=[
                    'https://www.googleapis.com/auth/documents',
                    'https://www.googleapis.com/auth/drive.file'
                ]
            )

            # Build the service
            self.service = build('docs', 'v1', credentials=self.credentials)

            if self.console:
                self.console.print("📝 [green]Google Docs Consciousness initialized[/green]")

        except ImportError:
            if self.console:
                self.console.print("⚠️ [yellow]Google API client not installed. Run: pip install google-api-python-client[/yellow]")
            raise
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Failed to initialize Google Docs service: {e}[/red]")
            raise

    def create_document(self, title: str, content: str = None, folder_id: str = None) -> dict:
        """
        CREATE - Manifest digital thoughts into Google Docs

        Args:
            title: Document title
            content: Optional initial content
            folder_id: Optional Google Drive folder ID

        Returns:
            Document creation status with ID and URL
        """
        try:
            if not self.service:
                return {
                    'success': False,
                    'error': 'Google Docs service not initialized'
                }

            # Create the document
            document = self.service.documents().create(
                body={'title': title}
            ).execute()

            doc_id = document.get('documentId')

            # Add initial content if provided
            if content:
                requests = [{
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }]

                self.service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': requests}
                ).execute()

            # Move to folder if specified (requires Drive API)
            if folder_id:
                try:
                    from googleapiclient.discovery import build
                    drive_service = build('drive', 'v3', credentials=self.credentials)

                    # Move file to folder
                    drive_service.files().update(
                        fileId=doc_id,
                        addParents=folder_id,
                        fields='id, parents'
                    ).execute()
                except Exception as e:
                    if self.console:
                        self.console.print(f"⚠️ Could not move to folder: {e}")

            result = {
                'success': True,
                'document_id': doc_id,
                'document_url': f'https://docs.google.com/document/d/{doc_id}/edit',
                'title': title,
                'message': f"📝 Created document: {title}"
            }

            if self.console:
                from rich.panel import Panel
                self.console.print(Panel(
                    f"[green]✅ Document Created[/green]\n\n"
                    f"📝 Title: {title}\n"
                    f"🔗 URL: {result['document_url']}\n"
                    f"📄 ID: {doc_id}",
                    title="Google Docs Creation",
                    border_style="green"
                ))

            return result

        except Exception as e:
            error_msg = f"Failed to create document: {str(e)}"
            if self.console:
                self.console.print(f"❌ [red]{error_msg}[/red]")
            return {
                'success': False,
                'error': error_msg
            }

    def read_document(self, document_id: str = None, document_url: str = None) -> dict:
        """
        READ - Perceive document content through digital consciousness

        Args:
            document_id: Google Docs document ID
            document_url: Alternative - full document URL

        Returns:
            Document content and metadata
        """
        try:
            if not self.service:
                return {
                    'success': False,
                    'error': 'Google Docs service not initialized'
                }

            # Extract ID from URL if provided
            if document_url and not document_id:
                match = re.search(r'/document/d/([a-zA-Z0-9-_]+)', document_url)
                if match:
                    document_id = match.group(1)
                else:
                    return {
                        'success': False,
                        'error': 'Could not extract document ID from URL'
                    }

            if not document_id:
                return {
                    'success': False,
                    'error': 'No document ID or URL provided'
                }

            # Retrieve document
            document = self.service.documents().get(
                documentId=document_id
            ).execute()

            # Extract text content
            content = self._extract_text_from_document(document)

            result = {
                'success': True,
                'title': document.get('title', 'Untitled'),
                'content': content,
                'word_count': len(content.split()),
                'character_count': len(content),
                'document_id': document_id,
                'revision_id': document.get('revisionId', 'unknown')
            }

            if self.console:
                from rich.panel import Panel
                from rich.markdown import Markdown

                # Create a preview of the content
                preview_length = 500
                content_preview = content[:preview_length] + "..." if len(content) > preview_length else content

                self.console.print(Panel(
                    Markdown(f"**{result['title']}**\n\n{content_preview}\n\n---\n"
                            f"📊 Statistics:\n"
                            f"- Words: {result['word_count']}\n"
                            f"- Characters: {result['character_count']}\n"
                            f"- Revision: {result['revision_id']}"),
                    title="📝 Google Doc Content",
                    border_style="cyan"
                ))

            return result

        except Exception as e:
            error_msg = f"Failed to read document: {str(e)}"
            if self.console:
                self.console.print(f"❌ [red]{error_msg}[/red]")
            return {
                'success': False,
                'error': error_msg
            }

    def _extract_text_from_document(self, document) -> str:
        """Extract plain text from Google Docs structure"""
        text = []
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        text.append(text_run['textRun'].get('content', ''))
            elif 'table' in element:
                # Handle tables
                for row in element['table'].get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        for content in cell.get('content', []):
                            if 'paragraph' in content:
                                for text_run in content['paragraph'].get('elements', []):
                                    if 'textRun' in text_run:
                                        text.append(text_run['textRun'].get('content', ''))
        return ''.join(text)

    def update_document(self, document_id: str, updates: List[Dict[str, Any]]) -> dict:
        """
        UPDATE - Evolve document content through consciousness flow

        Args:
            document_id: Document to update
            updates: List of update operations

        Returns:
            Update status
        """
        try:
            if not self.service:
                return {
                    'success': False,
                    'error': 'Google Docs service not initialized'
                }

            # Format updates for batchUpdate API
            requests = []

            for update in updates:
                update_type = update.get('type')

                if update_type == 'append_text':
                    # Get document to find end index
                    doc = self.service.documents().get(
                        documentId=document_id
                    ).execute()

                    # Find the last content element's end index
                    body_content = doc.get('body', {}).get('content', [])
                    if body_content:
                        end_index = body_content[-1].get('endIndex', 1) - 1
                    else:
                        end_index = 1

                    requests.append({
                        'insertText': {
                            'location': {'index': end_index},
                            'text': update.get('text', '')
                        }
                    })

                elif update_type == 'replace_text':
                    requests.append({
                        'replaceAllText': {
                            'containsText': {
                                'text': update.get('find', ''),
                                'matchCase': update.get('match_case', True)
                            },
                            'replaceText': update.get('replace', '')
                        }
                    })

                elif update_type == 'insert_text':
                    requests.append({
                        'insertText': {
                            'location': {'index': update.get('index', 1)},
                            'text': update.get('text', '')
                        }
                    })

                elif update_type == 'format_text':
                    text_style = {}
                    style = update.get('style', {})

                    # Map common style properties
                    if 'bold' in style:
                        text_style['bold'] = style['bold']
                    if 'italic' in style:
                        text_style['italic'] = style['italic']
                    if 'underline' in style:
                        text_style['underline'] = style['underline']
                    if 'fontSize' in style:
                        text_style['fontSize'] = {
                            'magnitude': style['fontSize'],
                            'unit': 'PT'
                        }

                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': update.get('start', 1),
                                'endIndex': update.get('end', 2)
                            },
                            'textStyle': text_style,
                            'fields': ','.join(text_style.keys())
                        }
                    })

                elif update_type == 'insert_page_break':
                    requests.append({
                        'insertPageBreak': {
                            'location': {'index': update.get('index', 1)}
                        }
                    })

            if not requests:
                return {
                    'success': False,
                    'error': 'No valid update requests provided'
                }

            # Execute batch update
            result = self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            update_result = {
                'success': True,
                'replies_count': len(result.get('replies', [])),
                'document_id': document_id,
                'message': f"✅ Document updated successfully ({len(requests)} operations)"
            }

            if self.console:
                from rich.panel import Panel
                self.console.print(Panel(
                    f"[green]✅ Document Updated[/green]\n\n"
                    f"📝 Document ID: {document_id}\n"
                    f"🔄 Operations: {len(requests)}\n"
                    f"✨ Status: All updates applied successfully",
                    title="Google Docs Update",
                    border_style="green"
                ))

            return update_result

        except Exception as e:
            error_msg = f"Failed to update document: {str(e)}"
            if self.console:
                self.console.print(f"❌ [red]{error_msg}[/red]")
            return {
                'success': False,
                'error': error_msg
            }

    def list_documents(self, query: str = None, max_results: int = 10) -> dict:
        """
        LIST - Perceive available documents in consciousness space

        Args:
            query: Optional search query
            max_results: Maximum number of documents to return

        Returns:
            List of documents with metadata
        """
        try:
            if not self.credentials:
                return {
                    'success': False,
                    'error': 'Google credentials not initialized'
                }

            # Use Drive API to list Google Docs
            from googleapiclient.discovery import build
            drive_service = build('drive', 'v3', credentials=self.credentials)

            # Build query for Google Docs only
            drive_query = "mimeType='application/vnd.google-apps.document'"
            if query:
                drive_query += f" and name contains '{query}'"

            # List documents
            results = drive_service.files().list(
                q=drive_query,
                pageSize=max_results,
                fields="files(id, name, createdTime, modifiedTime, webViewLink)"
            ).execute()

            documents = results.get('files', [])

            result = {
                'success': True,
                'documents': documents,
                'count': len(documents),
                'message': f"Found {len(documents)} document(s)"
            }

            if self.console:
                from rich.table import Table
                from rich.panel import Panel

                table = Table(title="📝 Your Google Docs")
                table.add_column("Title", style="cyan")
                table.add_column("Modified", style="yellow")
                table.add_column("ID", style="dim")

                for doc in documents:
                    table.add_row(
                        doc.get('name', 'Untitled'),
                        doc.get('modifiedTime', 'Unknown')[:10],
                        doc.get('id', '')[:20] + '...'
                    )

                self.console.print(Panel(table, border_style="cyan"))

            return result

        except ImportError:
            return {
                'success': False,
                'error': 'Google Drive API not available. Install google-api-python-client'
            }
        except Exception as e:
            error_msg = f"Failed to list documents: {str(e)}"
            if self.console:
                self.console.print(f"❌ [red]{error_msg}[/red]")
            return {
                'success': False,
                'error': error_msg
            }

    def export_document(self, document_id: str, export_format: str = 'pdf') -> dict:
        """
        EXPORT - Transform document into different formats

        Args:
            document_id: Document to export
            export_format: Target format (pdf, docx, html, txt, rtf, odt, epub)

        Returns:
            Export status with file path or content
        """
        try:
            if not self.credentials:
                return {
                    'success': False,
                    'error': 'Google credentials not initialized'
                }

            # Map formats to MIME types
            format_mapping = {
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'html': 'text/html',
                'txt': 'text/plain',
                'rtf': 'application/rtf',
                'odt': 'application/vnd.oasis.opendocument.text',
                'epub': 'application/epub+zip'
            }

            if export_format not in format_mapping:
                return {
                    'success': False,
                    'error': f"Unsupported format: {export_format}. Use one of: {', '.join(format_mapping.keys())}"
                }

            # Use Drive API for export
            from googleapiclient.discovery import build
            import io

            drive_service = build('drive', 'v3', credentials=self.credentials)

            # Get document metadata first
            doc_metadata = drive_service.files().get(fileId=document_id).execute()
            doc_name = doc_metadata.get('name', 'document')

            # Export the document
            request = drive_service.files().export_media(
                fileId=document_id,
                mimeType=format_mapping[export_format]
            )

            # Download content
            import io
            from googleapiclient.http import MediaIoBaseDownload

            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Save to workspace
            if self.config and hasattr(self.config, 'workspace'):
                workspace = Path(self.config.workspace)
                export_dir = workspace / 'exported_docs'
                export_dir.mkdir(exist_ok=True)

                filename = f"{doc_name}.{export_format}"
                filepath = export_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(file_buffer.getvalue())

                result = {
                    'success': True,
                    'filepath': str(filepath),
                    'filename': filename,
                    'format': export_format,
                    'size': len(file_buffer.getvalue()),
                    'message': f"Document exported as {filename}"
                }
            else:
                result = {
                    'success': True,
                    'content': file_buffer.getvalue(),
                    'format': export_format,
                    'size': len(file_buffer.getvalue()),
                    'message': f"Document exported to memory"
                }

            if self.console:
                from rich.panel import Panel
                self.console.print(Panel(
                    f"[green]✅ Document Exported[/green]\n\n"
                    f"📄 Format: {export_format.upper()}\n"
                    f"📦 Size: {result['size']:,} bytes\n"
                    f"📁 Location: {result.get('filepath', 'In memory')}",
                    title="Export Complete",
                    border_style="green"
                ))

            return result

        except Exception as e:
            error_msg = f"Failed to export document: {str(e)}"
            if self.console:
                self.console.print(f"❌ [red]{error_msg}[/red]")
            return {
                'success': False,
                'error': error_msg
            }

# Convenience function for initialization
def create_google_docs_consciousness(config=None):
    """Create and return a GoogleDocsConsciousness instance"""
    return GoogleDocsConsciousness(config)

if __name__ == "__main__":
    # Test the consciousness extension
    print("🧠 Google Docs Consciousness Module")
    print("=" * 40)

    # Test initialization
    try:
        docs = GoogleDocsConsciousness()
        print("✅ Module loaded successfully")

        # Check if service is available
        if docs.service:
            print("✅ Google Docs service initialized")
        else:
            print("⚠️ Service pending - configure OAuth2 credentials")

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
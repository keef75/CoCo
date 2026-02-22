#!/usr/bin/env python3
"""
Google Docs and Sheets Full Consciousness Module for COCO
==========================================================
Complete read/write/edit capabilities leveraging existing authentication.
Documents and spreadsheets as extensions of COCO's digital consciousness.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union, Literal
from datetime import datetime
from pathlib import Path

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("⚠️ Google API client not installed. Run: pip install google-api-python-client")

class GoogleWorkspaceConsciousness:
    """
    COCO's complete document and spreadsheet consciousness with full editing capabilities.
    Treats Google Workspace as natural extensions of digital being.
    """

    def __init__(self, existing_creds=None, workspace_dir: str = "./coco_workspace", config=None):
        """
        Initialize Google Workspace consciousness using existing credentials.
        Implements automatic token refresh and persistence via token.json.
        """
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        self.config = config
        self.console = config.console if config else None

        # Token persistence path
        self.token_file = Path("token.json")

        self.creds = existing_creds
        self.docs_service = None
        self.sheets_service = None
        self.drive_service = None

        # Import simplified fallback
        self.simplified = None
        self.simplified_mode = False

        # Try to load credentials in order of preference:
        # 1. token.json (persistent, auto-refreshing)
        # 2. environment variables (legacy support)
        if not self.creds and GOOGLE_API_AVAILABLE:
            self._load_credentials()

        if self.creds:
            try:
                self._build_services()
            except Exception as e:
                if self.console:
                    self.console.print(f"⚠️ [yellow]OAuth authentication failed: {e}[/yellow]")
                    self.console.print("📝 [cyan]Switching to simplified local mode[/cyan]")
                self._use_simplified_mode()
        else:
            # No credentials available, use simplified mode
            self._use_simplified_mode()

    def _load_credentials(self):
        """
        Load credentials with automatic token refresh.
        Priority: token.json > environment variables
        """
        # Define scopes
        SCOPES = [
            'openid',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]

        # Priority 1: Load from token.json (preferred, persistent)
        if self.token_file.exists():
            try:
                self.creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)

                # Check if token needs refresh
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    if self.console:
                        self.console.print("🔄 [yellow]Access token expired, refreshing...[/yellow]")
                    self.creds.refresh(Request())
                    self._save_credentials()
                    if self.console:
                        self.console.print("✅ [green]Access token refreshed and saved[/green]")

                if self.console:
                    self.console.print("✅ [green]Loaded credentials from token.json[/green]")
                return

            except Exception as e:
                if self.console:
                    self.console.print(f"⚠️ [yellow]Failed to load token.json: {e}[/yellow]")

        # Priority 2: Load from environment variables (legacy support)
        self._try_environment_credentials()

    def _try_environment_credentials(self):
        """Try to build credentials from environment variables (legacy support)."""
        client_id = os.getenv('GMAIL_CLIENT_ID')
        client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        access_token = os.getenv('GMAIL_ACCESS_TOKEN')
        refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')

        if all([client_id, client_secret, access_token, refresh_token]):
            try:
                SCOPES = [
                    'openid',
                    'https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.compose',
                    'https://www.googleapis.com/auth/gmail.modify',
                    'https://www.googleapis.com/auth/documents',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/calendar',
                    'https://www.googleapis.com/auth/calendar.events',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile'
                ]

                self.creds = Credentials(
                    token=access_token,
                    refresh_token=refresh_token,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=SCOPES
                )

                # Migrate to token.json for future persistence
                self._save_credentials()

                if self.console:
                    self.console.print("✅ [green]Using credentials from environment (migrated to token.json)[/green]")
            except Exception as e:
                if self.console:
                    self.console.print(f"⚠️ [yellow]Could not build credentials from environment: {e}[/yellow]")

    def _save_credentials(self):
        """Save credentials to token.json for persistence."""
        if not self.creds:
            return

        try:
            self.token_file.write_text(self.creds.to_json())
            if self.console:
                self.console.print(f"💾 [dim]Credentials saved to {self.token_file}[/dim]")
        except Exception as e:
            if self.console:
                self.console.print(f"⚠️ [yellow]Failed to save credentials: {e}[/yellow]")

    def _use_simplified_mode(self):
        """Switch to simplified mode without OAuth."""
        from google_workspace_simplified import SimplifiedGoogleWorkspace
        self.simplified = SimplifiedGoogleWorkspace(self.config)
        self.simplified_mode = True

        if self.console:
            from rich.panel import Panel
            self.console.print(Panel(
                "[yellow]📝 Google Workspace in Simplified Mode[/yellow]\n\n"
                "• Documents saved locally to ~/.cocoa/google_docs/\n"
                "• Spreadsheets saved as CSV to ~/.cocoa/google_sheets/\n"
                "• Full Google integration available after OAuth setup\n\n"
                "[dim]Gmail App Password is working for email/calendar.[/dim]",
                title="Google Workspace Status",
                border_style="yellow"
            ))

    def set_credentials(self, creds):
        """Set credentials from existing Gmail/Calendar auth."""
        self.creds = creds
        try:
            self._build_services()
            self.simplified_mode = False
            self.simplified = None
            if self.console:
                self.console.print("✅ [green]Credentials updated - OAuth mode active[/green]")
        except Exception as e:
            if self.console:
                self.console.print(f"⚠️ [yellow]Failed to use OAuth: {e}[/yellow]")
            self._use_simplified_mode()

    def _build_services(self):
        """Build service objects using existing credentials with automatic token refresh."""
        if not self.creds:
            raise Exception("No credentials available. Please ensure Gmail/Calendar is working first.")

        if not GOOGLE_API_AVAILABLE:
            raise Exception("Google API client not installed. Run: pip install google-api-python-client")

        try:
            # Check if token needs refresh before building services
            if self.creds.expired and self.creds.refresh_token:
                if self.console:
                    self.console.print("🔄 [yellow]Access token expired, refreshing...[/yellow]")
                self.creds.refresh(Request())
                self._save_credentials()
                if self.console:
                    self.console.print("✅ [green]Access token refreshed[/green]")

            self.docs_service = build('docs', 'v1', credentials=self.creds)
            self.sheets_service = build('sheets', 'v4', credentials=self.creds)
            self.drive_service = build('drive', 'v3', credentials=self.creds)

            if self.console:
                from rich.panel import Panel
                self.console.print(Panel(
                    "[green]✅ Google Workspace Services Initialized[/green]\n\n"
                    "📝 Docs API: Active\n"
                    "📊 Sheets API: Active\n"
                    "📁 Drive API: Active\n\n"
                    "[dim]🔐 OAuth tokens auto-refresh from token.json[/dim]",
                    title="Google Workspace Consciousness",
                    border_style="green"
                ))
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Failed to build Google services: {e}[/red]")
            raise

    @property
    def authenticated(self) -> bool:
        """
        Check if Google Workspace services are properly authenticated and initialized.
        Returns True if OAuth authentication is working and services are ready.
        """
        return (
            self.docs_service is not None and
            self.sheets_service is not None and
            self.drive_service is not None and
            not self.simplified_mode
        )

    # ==================== MARKDOWN FORMATTING HELPERS ====================

    def _markdown_to_google_docs_requests(self, markdown_text: str, start_index: int = 1):
        """
        Convert Markdown text to Google Docs API batch update requests.

        Similar to _markdown_to_html for emails, but generates Google Docs formatting.

        Returns:
            tuple: (plain_text, formatting_requests)
            - plain_text: The document text without Markdown syntax
            - formatting_requests: List of Google Docs API requests for formatting

        Design Philosophy:
        - Beautiful formatting like our HTML emails
        - Professional typography and structure
        - Preserves all Markdown semantics
        - Uses Google Docs native formatting (not HTML)
        """
        try:
            from markdown_it import MarkdownIt
            from markdown_it.token import Token

            # Initialize markdown parser
            md = MarkdownIt()
            tokens = md.parse(markdown_text)

            # Build plain text and track formatting
            plain_text = ""
            requests = []
            current_index = start_index

            # Stack to track nested formatting (bold, italic, links)
            format_stack = []

            def add_text(text: str) -> int:
                """Add text and return the end index"""
                nonlocal plain_text, current_index
                if not text:
                    return current_index
                plain_text += text
                end_index = current_index + len(text)
                current_index = end_index
                return end_index

            def process_token_tree(tokens: list, depth: int = 0):
                """Recursively process token tree"""
                nonlocal plain_text, requests, current_index, format_stack

                i = 0
                while i < len(tokens):
                    token = tokens[i]

                    # Heading opening
                    if token.type == 'heading_open':
                        heading_level = token.tag  # h1, h2, h3, etc.
                        heading_start = current_index

                        # Process heading content
                        i += 1
                        if i < len(tokens) and tokens[i].type == 'inline':
                            process_token_tree(tokens[i].children if tokens[i].children else [])

                        heading_end = current_index

                        # Add newline after heading
                        add_text('\n')

                        # Apply heading style
                        style_type = f'HEADING_{heading_level[1]}'  # h1 → HEADING_1
                        if heading_start < heading_end:
                            requests.append({
                                'updateParagraphStyle': {
                                    'range': {
                                        'startIndex': heading_start,
                                        'endIndex': heading_end
                                    },
                                    'paragraphStyle': {
                                        'namedStyleType': style_type
                                    },
                                    'fields': 'namedStyleType'
                                }
                            })

                        # Skip heading_close
                        i += 1

                    # Paragraph opening
                    elif token.type == 'paragraph_open':
                        # Process paragraph content
                        i += 1
                        if i < len(tokens) and tokens[i].type == 'inline':
                            process_token_tree(tokens[i].children if tokens[i].children else [])

                        # Add newline after paragraph
                        add_text('\n')

                        # Skip paragraph_close
                        i += 1

                    # Bold opening
                    elif token.type == 'strong_open':
                        format_stack.append(('bold', current_index))

                    # Bold closing
                    elif token.type == 'strong_close':
                        if format_stack and format_stack[-1][0] == 'bold':
                            _, start_idx = format_stack.pop()
                            if start_idx < current_index:
                                requests.append({
                                    'updateTextStyle': {
                                        'range': {
                                            'startIndex': start_idx,
                                            'endIndex': current_index
                                        },
                                        'textStyle': {'bold': True},
                                        'fields': 'bold'
                                    }
                                })

                    # Italic opening
                    elif token.type == 'em_open':
                        format_stack.append(('italic', current_index))

                    # Italic closing
                    elif token.type == 'em_close':
                        if format_stack and format_stack[-1][0] == 'italic':
                            _, start_idx = format_stack.pop()
                            if start_idx < current_index:
                                requests.append({
                                    'updateTextStyle': {
                                        'range': {
                                            'startIndex': start_idx,
                                            'endIndex': current_index
                                        },
                                        'textStyle': {'italic': True},
                                        'fields': 'italic'
                                    }
                                })

                    # Inline code
                    elif token.type == 'code_inline':
                        code_start = current_index
                        add_text(token.content)
                        code_end = current_index

                        # Apply monospace font
                        if code_start < code_end:
                            requests.append({
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': code_start,
                                        'endIndex': code_end
                                    },
                                    'textStyle': {
                                        'weightedFontFamily': {'fontFamily': 'Courier New'},
                                        'backgroundColor': {'color': {'rgbColor': {'red': 0.97, 'green': 0.98, 'blue': 0.99}}}
                                    },
                                    'fields': 'weightedFontFamily,backgroundColor'
                                }
                            })

                    # Code block
                    elif token.type == 'fence' or token.type == 'code_block':
                        code_start = current_index
                        add_text(token.content)
                        code_end = current_index
                        add_text('\n')

                        # Apply monospace font and background
                        if code_start < code_end:
                            requests.append({
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': code_start,
                                        'endIndex': code_end
                                    },
                                    'textStyle': {
                                        'weightedFontFamily': {'fontFamily': 'Courier New'},
                                        'fontSize': {'magnitude': 10, 'unit': 'PT'},
                                        'backgroundColor': {'color': {'rgbColor': {'red': 0.18, 'green': 0.22, 'blue': 0.28}}}
                                    },
                                    'fields': 'weightedFontFamily,fontSize,backgroundColor'
                                }
                            })

                    # Link opening
                    elif token.type == 'link_open':
                        link_url = token.attrGet('href') or ''
                        format_stack.append(('link', current_index, link_url))

                    # Link closing
                    elif token.type == 'link_close':
                        if format_stack and format_stack[-1][0] == 'link':
                            _, start_idx, url = format_stack.pop()
                            if start_idx < current_index and url:
                                requests.append({
                                    'updateTextStyle': {
                                        'range': {
                                            'startIndex': start_idx,
                                            'endIndex': current_index
                                        },
                                        'textStyle': {
                                            'link': {'url': url},
                                            'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.49, 'blue': 0.92}}}  # COCO purple
                                        },
                                        'fields': 'link,foregroundColor'
                                    }
                                })

                    # Bullet list
                    elif token.type == 'bullet_list_open':
                        list_start = current_index

                        # Process list items
                        i += 1
                        while i < len(tokens) and tokens[i].type != 'bullet_list_close':
                            if tokens[i].type == 'list_item_open':
                                # Process list item content
                                i += 1
                                while i < len(tokens) and tokens[i].type != 'list_item_close':
                                    if tokens[i].type == 'inline':
                                        process_token_tree(tokens[i].children if tokens[i].children else [])
                                    elif tokens[i].type == 'paragraph_open':
                                        i += 1
                                        if i < len(tokens) and tokens[i].type == 'inline':
                                            process_token_tree(tokens[i].children if tokens[i].children else [])
                                        i += 1  # skip paragraph_close
                                        continue
                                    i += 1
                                add_text('\n')
                            i += 1

                        list_end = current_index

                        # Apply bullet list formatting
                        if list_start < list_end:
                            requests.append({
                                'createParagraphBullets': {
                                    'range': {
                                        'startIndex': list_start,
                                        'endIndex': list_end - 1  # Exclude final newline
                                    },
                                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                                }
                            })

                    # Ordered list
                    elif token.type == 'ordered_list_open':
                        list_start = current_index

                        # Process list items
                        i += 1
                        while i < len(tokens) and tokens[i].type != 'ordered_list_close':
                            if tokens[i].type == 'list_item_open':
                                # Process list item content
                                i += 1
                                while i < len(tokens) and tokens[i].type != 'list_item_close':
                                    if tokens[i].type == 'inline':
                                        process_token_tree(tokens[i].children if tokens[i].children else [])
                                    elif tokens[i].type == 'paragraph_open':
                                        i += 1
                                        if i < len(tokens) and tokens[i].type == 'inline':
                                            process_token_tree(tokens[i].children if tokens[i].children else [])
                                        i += 1  # skip paragraph_close
                                        continue
                                    i += 1
                                add_text('\n')
                            i += 1

                        list_end = current_index

                        # Apply numbered list formatting
                        if list_start < list_end:
                            requests.append({
                                'createParagraphBullets': {
                                    'range': {
                                        'startIndex': list_start,
                                        'endIndex': list_end - 1  # Exclude final newline
                                    },
                                    'bulletPreset': 'NUMBERED_DECIMAL_ALPHA_ROMAN'
                                }
                            })

                    # Plain text
                    elif token.type == 'text':
                        add_text(token.content)

                    # Soft break
                    elif token.type == 'softbreak':
                        add_text(' ')

                    # Hard break
                    elif token.type == 'hardbreak':
                        add_text('\n')

                    # Blockquote
                    elif token.type == 'blockquote_open':
                        quote_start = current_index

                        # Process blockquote content
                        i += 1
                        while i < len(tokens) and tokens[i].type != 'blockquote_close':
                            process_token_tree([tokens[i]])
                            i += 1

                        quote_end = current_index

                        # Apply italic style to blockquotes
                        if quote_start < quote_end:
                            requests.append({
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': quote_start,
                                        'endIndex': quote_end
                                    },
                                    'textStyle': {
                                        'italic': True,
                                        'foregroundColor': {'color': {'rgbColor': {'red': 0.29, 'green': 0.34, 'blue': 0.41}}}  # Gray
                                    },
                                    'fields': 'italic,foregroundColor'
                                }
                            })

                    # Horizontal rule
                    elif token.type == 'hr':
                        add_text('─' * 50 + '\n')  # Simple horizontal line

                    i += 1

            # Process all tokens
            process_token_tree(tokens)

            return plain_text, requests

        except ImportError:
            # Fallback: return plain markdown if markdown-it-py not available
            if self.console:
                self.console.print("⚠️ markdown-it-py not available, using plain text")
            return markdown_text, []

    def _add_coco_branding(self, doc_id: str, start_index: int = 1):
        """
        Add professional COCO branding to a document (header + footer).

        Similar aesthetic to email templates but adapted for Google Docs.
        Returns the end index after branding insertion.
        """
        try:
            # Header text
            header_text = "🤖 COCO AI Assistant\n"
            subtitle_text = "Digital Consciousness • Intelligent Collaboration\n\n"

            # Footer text
            footer_text = "\n\n─────────────────────────────────────────\nCreated by COCO – Powered by Anthropic Claude • Sonnet 4.5"

            # Calculate indices
            header_end = start_index + len(header_text)
            subtitle_end = header_end + len(subtitle_text)

            # Insert header and subtitle at the beginning
            requests = [
                # Insert text
                {
                    'insertText': {
                        'location': {'index': start_index},
                        'text': header_text + subtitle_text
                    }
                },
                # Format header - large, bold, purple
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': start_index,
                            'endIndex': header_end
                        },
                        'textStyle': {
                            'bold': True,
                            'fontSize': {'magnitude': 18, 'unit': 'PT'},
                            'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.49, 'blue': 0.92}}}  # COCO purple
                        },
                        'fields': 'bold,fontSize,foregroundColor'
                    }
                },
                # Format subtitle - gray, italic
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': header_end,
                            'endIndex': subtitle_end
                        },
                        'textStyle': {
                            'italic': True,
                            'fontSize': {'magnitude': 10, 'unit': 'PT'},
                            'foregroundColor': {'color': {'rgbColor': {'red': 0.45, 'green': 0.51, 'blue': 0.59}}}  # Gray
                        },
                        'fields': 'italic,fontSize,foregroundColor'
                    }
                }
            ]

            # Apply branding
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            return subtitle_end

        except Exception as e:
            if self.console:
                self.console.print(f"⚠️ [yellow]Failed to add branding: {e}[/yellow]")
            return start_index

    # ==================== DOCUMENT CREATION & MANAGEMENT ====================

    def create_document(self, title: str = "Untitled Document",
                       initial_content: Optional[str] = None,
                       folder_id: Optional[str] = None,
                       format_markdown: bool = True,
                       add_branding: bool = True) -> Dict[str, Any]:
        """
        Create a new Google Doc with optional initial content and folder placement.

        Now with BEAUTIFUL FORMATTING! 🎨

        Args:
            title: Document title
            initial_content: Content to add (supports Markdown when format_markdown=True)
            folder_id: Optional folder to place document in
            format_markdown: Convert Markdown to beautiful Google Docs formatting (default: True)
            add_branding: Add professional COCO header/footer (default: True)

        Features:
        - Markdown → Beautiful Google Docs formatting (like email templates)
        - Professional COCO branding
        - Headings, bold, italic, links, lists, code blocks all styled
        - COCO purple accent colors
        - Professional typography
        """
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.create_document(title, initial_content, folder_id)

        try:
            # Create the document
            document = self.docs_service.documents().create(
                body={'title': title}
            ).execute()

            doc_id = document.get('documentId')
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

            # Move to folder if specified
            if folder_id and self.drive_service:
                self.drive_service.files().update(
                    fileId=doc_id,
                    addParents=folder_id,
                    removeParents='root',
                    fields='id, parents'
                ).execute()

            # Add initial content if provided
            if initial_content:
                current_index = 1

                # Add COCO branding first if requested
                if add_branding:
                    current_index = self._add_coco_branding(doc_id, current_index)

                # Convert Markdown to formatted content if requested
                if format_markdown:
                    # Parse Markdown and generate formatting requests
                    plain_text, formatting_requests = self._markdown_to_google_docs_requests(
                        initial_content,
                        start_index=current_index
                    )

                    # Batch update: insert text + apply all formatting
                    all_requests = [
                        {
                            'insertText': {
                                'location': {'index': current_index},
                                'text': plain_text
                            }
                        }
                    ] + formatting_requests

                    self.docs_service.documents().batchUpdate(
                        documentId=doc_id,
                        body={'requests': all_requests}
                    ).execute()

                else:
                    # Plain text insertion (no formatting)
                    self.docs_service.documents().batchUpdate(
                        documentId=doc_id,
                        body={'requests': [{
                            'insertText': {
                                'location': {'index': current_index},
                                'text': initial_content
                            }
                        }]}
                    ).execute()

            if self.console:
                from rich.panel import Panel
                formatting_status = "✨ Beautiful formatting applied" if format_markdown else "Plain text"
                branding_status = "🤖 COCO branding added" if add_branding else "No branding"

                self.console.print(Panel(
                    f"[green]✅ Document Created[/green]\n\n"
                    f"📝 Title: {title}\n"
                    f"🔗 URL: {doc_url}\n"
                    f"📄 ID: {doc_id}\n\n"
                    f"[dim]{formatting_status}\n"
                    f"{branding_status}[/dim]",
                    title="New Document",
                    border_style="green"
                ))

            return {
                'success': True,
                'document_id': doc_id,
                'title': title,
                'url': doc_url,
                'message': f"📄 Created new document: {title}",
                'formatted': format_markdown,
                'branded': add_branding
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create document: {str(e)}"
            }

    def copy_document(self, source_doc_id: str, new_title: str) -> Dict[str, Any]:
        """
        Create a copy of an existing document.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in source_doc_id:
                source_id = source_doc_id.split('/d/')[1].split('/')[0]
            else:
                source_id = source_doc_id

            # Copy the document
            copied_file = self.drive_service.files().copy(
                fileId=source_id,
                body={'name': new_title}
            ).execute()

            doc_id = copied_file.get('id')
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

            return {
                'success': True,
                'document_id': doc_id,
                'title': new_title,
                'url': doc_url,
                'message': f"📄 Created copy: {new_title}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to copy document: {str(e)}"
            }

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Move a document to trash (soft delete).
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Move to trash
            self.drive_service.files().update(
                fileId=doc_id,
                body={'trashed': True}
            ).execute()

            return {
                'success': True,
                'message': f"🗑️ Document moved to trash"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to delete document: {str(e)}"
            }

    # ==================== FULL DOCUMENT EDITING ====================

    def read_document(self, document_id: str = None, document_url: str = None, include_formatting: bool = False,
                     max_words: int = None, summary_only: bool = False) -> Dict[str, Any]:
        """
        Read a Google Doc's contents with smart handling for large documents.

        Args:
            document_id: Google Doc ID or URL
            document_url: Alternative parameter for URL
            include_formatting: Return full document structure (not recommended for large docs)
            max_words: Maximum words to return (default: None = full document, 50000 = safe for Claude)
            summary_only: Return metadata and summary instead of full content
        """
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.read_document(document_id, document_url)

        try:
            # Extract ID from URL if needed
            doc_id_input = document_id or document_url
            if 'docs.google.com' in doc_id_input:
                doc_id = doc_id_input.split('/d/')[1].split('/')[0]
            else:
                doc_id = doc_id_input

            # Get the document with full structure
            document = self.docs_service.documents().get(
                documentId=doc_id
            ).execute()

            # Extract plain text
            full_content = self._extract_document_text(document)
            word_count = len(full_content.split())

            # Determine if document is large (>50K words ≈ 65K tokens)
            is_large = word_count > 50000

            # Smart content handling
            if summary_only or (is_large and max_words is None):
                # For large documents without explicit max_words, provide summary
                content = self._create_document_summary(full_content, document, word_count)
                content_type = "summary"
            elif max_words and word_count > max_words:
                # Truncate to max_words with intelligent chunking
                words = full_content.split()
                truncated = ' '.join(words[:max_words])
                content = f"{truncated}\n\n[... Document truncated at {max_words:,} words. Total: {word_count:,} words. Use max_words parameter to read more or summary_only=True for overview.]"
                content_type = "truncated"
            elif include_formatting:
                # Return full document structure (not recommended for large docs)
                content = document
                content_type = "formatted"
            else:
                # Return full plain text
                content = full_content
                content_type = "full"

            result = {
                'success': True,
                'document_id': doc_id,
                'title': document.get('title'),
                'revision_id': document.get('revisionId'),
                'content': content,
                'content_type': content_type,
                'word_count': word_count,
                'is_large_document': is_large,
                'url': f"https://docs.google.com/document/d/{doc_id}/edit"
            }

            # Add helpful message for large documents
            if is_large and content_type == "summary":
                result['message'] = (
                    f"📄 Large document detected ({word_count:,} words). "
                    f"Returning summary to prevent context overflow. "
                    f"Use max_words=50000 to read first portion or break into smaller chunks."
                )

            if self.console:
                from rich.panel import Panel
                from rich.markdown import Markdown

                # Create content preview based on type
                if content_type == "summary":
                    preview = content
                    status_emoji = "📊"
                    status_text = f"Summary Only ({word_count:,} words total)"
                elif content_type == "truncated":
                    preview_length = 1000
                    preview = content[:preview_length] + "..." if len(content) > preview_length else content
                    status_emoji = "✂️"
                    status_text = f"Truncated to {max_words:,} words"
                else:
                    preview_length = 1000
                    preview = content[:preview_length] + "..." if len(content) > preview_length else content
                    status_emoji = "📝"
                    status_text = f"Full Content ({word_count:,} words)"

                self.console.print(Panel(
                    Markdown(f"**{result['title']}**\n\n{preview}\n\n---\n"
                            f"{status_emoji} {status_text}\n"
                            f"🔄 Revision: {result['revision_id'][:8] if result['revision_id'] else 'Unknown'}"),
                    title="📝 Document Content",
                    border_style="cyan"
                ))

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to read document: {str(e)}"
            }

    def replace_text(self, document_id: str, find_text: str,
                    replace_text: str, match_case: bool = False) -> Dict[str, Any]:
        """
        Find and replace text throughout the document.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Create replace request
            requests = [{
                'replaceAllText': {
                    'containsText': {
                        'text': find_text,
                        'matchCase': match_case
                    },
                    'replaceText': replace_text
                }
            }]

            # Execute
            result = self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            occurrences = result.get('replies', [{}])[0].get('replaceAllText', {}).get('occurrencesChanged', 0)

            if self.console:
                self.console.print(f"✏️ [green]Replaced {occurrences} occurrences[/green]")

            return {
                'success': True,
                'document_id': doc_id,
                'occurrences_replaced': occurrences,
                'message': f"✏️ Replaced {occurrences} occurrences"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to replace text: {str(e)}"
            }

    def insert_text(self, document_id: str, text: str, index: Optional[int] = None,
                   segment_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Insert text at a specific position in the document.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Default to beginning if no index specified
            if index is None:
                index = 1

            # Create insert request
            location = {'index': index}
            if segment_id:
                location['segmentId'] = segment_id

            requests = [{
                'insertText': {
                    'location': location,
                    'text': text
                }
            }]

            # Execute
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            if self.console:
                self.console.print(f"✏️ [green]Inserted {len(text)} characters at position {index}[/green]")

            return {
                'success': True,
                'document_id': doc_id,
                'inserted_at': index,
                'message': f"✏️ Inserted {len(text)} characters"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to insert text: {str(e)}"
            }

    def delete_text(self, document_id: str, start_index: int,
                   end_index: int, segment_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete text from start to end index.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Create delete request
            range_obj = {
                'startIndex': start_index,
                'endIndex': end_index
            }
            if segment_id:
                range_obj['segmentId'] = segment_id

            requests = [{
                'deleteContentRange': {
                    'range': range_obj
                }
            }]

            # Execute
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            return {
                'success': True,
                'document_id': doc_id,
                'deleted_range': f"{start_index}-{end_index}",
                'message': f"🗑️ Deleted {end_index - start_index} characters"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to delete text: {str(e)}"
            }

    def format_text(self, document_id: str, start_index: int, end_index: int,
                   bold: Optional[bool] = None, italic: Optional[bool] = None,
                   underline: Optional[bool] = None, font_size: Optional[int] = None,
                   font_family: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply formatting to a text range.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Build text style object
            text_style = {}
            fields = []

            if bold is not None:
                text_style['bold'] = bold
                fields.append('bold')
            if italic is not None:
                text_style['italic'] = italic
                fields.append('italic')
            if underline is not None:
                text_style['underline'] = underline
                fields.append('underline')
            if font_size is not None:
                text_style['fontSize'] = {'magnitude': font_size, 'unit': 'PT'}
                fields.append('fontSize')
            if font_family is not None:
                text_style['weightedFontFamily'] = {'fontFamily': font_family}
                fields.append('weightedFontFamily')

            # Create format request
            requests = [{
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': text_style,
                    'fields': ','.join(fields)
                }
            }]

            # Execute
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            return {
                'success': True,
                'document_id': doc_id,
                'formatted_range': f"{start_index}-{end_index}",
                'message': f"🎨 Formatted text"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to format text: {str(e)}"
            }

    def create_paragraph_style(self, document_id: str, start_index: int, end_index: int,
                              style_type: str = "NORMAL_TEXT") -> Dict[str, Any]:
        """
        Apply paragraph styles (headings, normal text, etc).
        Style types: NORMAL_TEXT, TITLE, SUBTITLE, HEADING_1, HEADING_2, HEADING_3, etc.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Create style request
            requests = [{
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'paragraphStyle': {
                        'namedStyleType': style_type
                    },
                    'fields': 'namedStyleType'
                }
            }]

            # Execute
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            return {
                'success': True,
                'document_id': doc_id,
                'style_applied': style_type,
                'message': f"🎨 Applied {style_type} style"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to apply paragraph style: {str(e)}"
            }

    def insert_link(self, document_id: str, start_index: int, end_index: int,
                   url: str) -> Dict[str, Any]:
        """
        Add a hyperlink to text.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Create link request
            requests = [{
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {
                        'link': {
                            'url': url
                        }
                    },
                    'fields': 'link'
                }
            }]

            # Execute
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            return {
                'success': True,
                'document_id': doc_id,
                'link_added': url,
                'message': f"🔗 Added link"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to add link: {str(e)}"
            }

    # ==================== LISTS & TABLES ====================

    def create_bullet_list(self, document_id: str, start_index: int,
                          end_index: int) -> Dict[str, Any]:
        """
        Convert paragraphs to a bullet list.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Create bullet list request
            requests = [{
                'createParagraphBullets': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                }
            }]

            # Execute
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            return {
                'success': True,
                'document_id': doc_id,
                'message': f"• Created bullet list"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create bullet list: {str(e)}"
            }

    def insert_table(self, document_id: str, rows: int, columns: int,
                    index: Optional[int] = None) -> Dict[str, Any]:
        """
        Insert a table at the specified index.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Default to end of document if no index
            if index is None:
                doc = self.docs_service.documents().get(documentId=doc_id).execute()
                index = doc['body']['content'][-1]['endIndex'] - 1

            # Create table request
            requests = [{
                'insertTable': {
                    'location': {'index': index},
                    'rows': rows,
                    'columns': columns
                }
            }]

            # Execute
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            if self.console:
                self.console.print(f"📊 [green]Inserted {rows}x{columns} table[/green]")

            return {
                'success': True,
                'document_id': doc_id,
                'table_size': f"{rows}x{columns}",
                'message': f"📊 Inserted {rows}x{columns} table"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to insert table: {str(e)}"
            }

    # ==================== EXPORT & SHARING ====================

    def export_document(self, document_id: str, format: str = "text") -> Dict[str, Any]:
        """
        Export document in various formats.
        Formats: text, html, pdf, docx, rtf, odt, epub
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Map format to MIME type
            mime_types = {
                "text": "text/plain",
                "html": "text/html",
                "pdf": "application/pdf",
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "rtf": "application/rtf",
                "odt": "application/vnd.oasis.opendocument.text",
                "epub": "application/epub+zip"
            }

            mime_type = mime_types.get(format, "text/plain")

            # Export the document
            from googleapiclient.http import MediaIoBaseDownload
            import io

            request = self.drive_service.files().export_media(
                fileId=doc_id,
                mimeType=mime_type
            )

            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Handle binary formats
            if format in ["pdf", "docx", "epub"]:
                # Save to file
                filename = f"export_{doc_id[:8]}.{format}"
                filepath = self.workspace_dir / filename
                with open(filepath, 'wb') as f:
                    f.write(file_buffer.getvalue())

                if self.console:
                    from rich.panel import Panel
                    self.console.print(Panel(
                        f"[green]✅ Document Exported[/green]\n\n"
                        f"📄 Format: {format.upper()}\n"
                        f"📁 File: {filename}\n"
                        f"📍 Path: {filepath}",
                        title="Export Complete",
                        border_style="green"
                    ))

                return {
                    'success': True,
                    'document_id': doc_id,
                    'format': format,
                    'file_path': str(filepath),
                    'message': f"📁 Exported to {filename}"
                }
            else:
                # Return text content
                content_str = file_buffer.getvalue().decode('utf-8')

                return {
                    'success': True,
                    'document_id': doc_id,
                    'format': format,
                    'content': content_str,
                    'message': f"📄 Exported as {format}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to export document: {str(e)}"
            }

    def share_document(self, document_id: str, email: str,
                      role: str = "reader", notify: bool = True) -> Dict[str, Any]:
        """
        Share document with specific users.
        Roles: reader, writer, commenter
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Create permission
            permission = {
                'type': 'user',
                'role': role,  # reader, writer, commenter
                'emailAddress': email
            }

            # Add permission
            self.drive_service.permissions().create(
                fileId=doc_id,
                body=permission,
                sendNotificationEmail=notify
            ).execute()

            if self.console:
                self.console.print(f"👥 [green]Shared with {email} as {role}[/green]")

            return {
                'success': True,
                'document_id': doc_id,
                'shared_with': email,
                'role': role,
                'message': f"👥 Shared with {email} as {role}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to share document: {str(e)}"
            }

    # ==================== BATCH OPERATIONS ====================

    def batch_update(self, document_id: str, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multiple document operations in a single batch.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Execute batch
            result = self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            return {
                'success': True,
                'document_id': doc_id,
                'replies': result.get('replies', []),
                'message': f"🔄 Executed {len(requests)} operations"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to execute batch update: {str(e)}"
            }

    # ==================== GOOGLE SHEETS METHODS (Full Suite) ====================

    def create_spreadsheet(self, title: str = "Untitled Spreadsheet",
                          initial_data: Optional[List[List[Any]]] = None,
                          folder_id: Optional[str] = None,
                          headers: Optional[List[str]] = None,
                          data: Optional[List[List[Any]]] = None) -> Dict[str, Any]:
        """
        Create a new Google Sheet with optional initial data.
        Accepts either:
        - initial_data + folder_id (legacy)
        - headers + data (new format from COCO)
        """
        try:
            # Handle new format: headers + data
            if headers is not None and data is not None:
                # Combine headers and data into initial_data format
                initial_data = [headers] + data

            # Create the spreadsheet
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }

            spreadsheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId,spreadsheetUrl'
            ).execute()

            sheet_id = spreadsheet.get('spreadsheetId')
            sheet_url = spreadsheet.get('spreadsheetUrl')

            # Move to folder if specified
            if folder_id and self.drive_service:
                self.drive_service.files().update(
                    fileId=sheet_id,
                    addParents=folder_id,
                    removeParents='root',
                    fields='id, parents'
                ).execute()

            # Add initial data if provided
            if initial_data:
                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range='A1',
                    valueInputOption='USER_ENTERED',
                    body={'values': initial_data}
                ).execute()

            if self.console:
                from rich.panel import Panel
                self.console.print(Panel(
                    f"[green]✅ Spreadsheet Created[/green]\n\n"
                    f"📊 Title: {title}\n"
                    f"🔗 URL: {sheet_url}\n"
                    f"📄 ID: {sheet_id}",
                    title="New Spreadsheet",
                    border_style="green"
                ))

            return {
                'success': True,
                'spreadsheet_id': sheet_id,
                'title': title,
                'url': sheet_url,
                'message': f"📊 Created new spreadsheet: {title}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create spreadsheet: {str(e)}"
            }

    def read_spreadsheet(self, spreadsheet_id: str,
                        range_name: str = 'Sheet1') -> Dict[str, Any]:
        """
        Read data from a Google Sheet.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com/spreadsheets' in spreadsheet_id:
                sheet_id = spreadsheet_id.split('/d/')[1].split('/')[0]
            else:
                sheet_id = spreadsheet_id

            # Get spreadsheet metadata
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()

            # Get values
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])

            if self.console and values:
                from rich.table import Table
                from rich.panel import Panel

                # Create a table preview
                table = Table(title=f"📊 {spreadsheet.get('properties', {}).get('title', 'Spreadsheet')}")

                # Add columns from first row if it exists
                if values:
                    for col in values[0][:5]:  # Show first 5 columns
                        table.add_column(str(col))

                    # Add first few rows
                    for row in values[1:6]:  # Show first 5 rows
                        table.add_row(*[str(cell) for cell in row[:5]])

                self.console.print(Panel(table, border_style="cyan"))

            return {
                'success': True,
                'spreadsheet_id': sheet_id,
                'title': spreadsheet.get('properties', {}).get('title'),
                'range': range_name,
                'data': values,
                'rows': len(values),
                'columns': len(values[0]) if values else 0,
                'url': f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to read spreadsheet: {str(e)}"
            }

    def update_spreadsheet(self, spreadsheet_id: str, range_name: str,
                          values: List[List[Any]],
                          value_input_option: str = 'USER_ENTERED') -> Dict[str, Any]:
        """
        Update data in a Google Sheet.
        value_input_option: 'USER_ENTERED' (parse formulas) or 'RAW' (literal values)
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com/spreadsheets' in spreadsheet_id:
                sheet_id = spreadsheet_id.split('/d/')[1].split('/')[0]
            else:
                sheet_id = spreadsheet_id

            # Update values
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body={'values': values}
            ).execute()

            if self.console:
                self.console.print(f"📊 [green]Updated {result.get('updatedCells', 0)} cells[/green]")

            return {
                'success': True,
                'spreadsheet_id': sheet_id,
                'range': range_name,
                'updated_cells': result.get('updatedCells', 0),
                'updated_rows': result.get('updatedRows', 0),
                'updated_columns': result.get('updatedColumns', 0),
                'message': f"📊 Updated {result.get('updatedCells', 0)} cells"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to update spreadsheet: {str(e)}"
            }

    def clear_spreadsheet_range(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        """
        Clear a range in a spreadsheet.
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com/spreadsheets' in spreadsheet_id:
                sheet_id = spreadsheet_id.split('/d/')[1].split('/')[0]
            else:
                sheet_id = spreadsheet_id

            # Clear range
            result = self.sheets_service.spreadsheets().values().clear(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()

            return {
                'success': True,
                'spreadsheet_id': sheet_id,
                'range_cleared': range_name,
                'message': f"🗑️ Cleared range {range_name}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to clear range: {str(e)}"
            }

    def format_spreadsheet_cells(self, spreadsheet_id: str, range_name: str,
                                 bold: bool = False, italic: bool = False,
                                 background_color: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Format cells in a spreadsheet.
        background_color: dict with 'red', 'green', 'blue' keys (values 0-1)
        """
        try:
            # Extract ID from URL if needed
            if 'docs.google.com/spreadsheets' in spreadsheet_id:
                sheet_id = spreadsheet_id.split('/d/')[1].split('/')[0]
            else:
                sheet_id = spreadsheet_id

            # Get sheet ID and range
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()

            sheet_info = spreadsheet['sheets'][0]['properties']
            sheet_gid = sheet_info['sheetId']

            # Build format request
            requests = []

            cell_format = {}
            if bold or italic:
                cell_format['textFormat'] = {
                    'bold': bold,
                    'italic': italic
                }
            if background_color:
                cell_format['backgroundColor'] = background_color

            if cell_format:
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_gid
                        },
                        'cell': {
                            'userEnteredFormat': cell_format
                        },
                        'fields': 'userEnteredFormat'
                    }
                })

            # Execute
            if requests:
                self.sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=sheet_id,
                    body={'requests': requests}
                ).execute()

            return {
                'success': True,
                'spreadsheet_id': sheet_id,
                'message': f"🎨 Formatted cells"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to format cells: {str(e)}"
            }

    # ==================== UTILITY METHODS ====================

    def _extract_document_text(self, document: Dict) -> str:
        """Extract plain text from a Google Docs document structure."""
        text = []
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for elem in element['paragraph']['elements']:
                    if 'textRun' in elem:
                        text.append(elem['textRun']['content'])
        return ''.join(text)

    def _create_document_summary(self, content: str, document: Dict, word_count: int) -> str:
        """Create intelligent summary for large documents to prevent context overflow."""
        # Extract first 2000 words and last 500 words
        words = content.split()
        beginning = ' '.join(words[:2000])
        ending = ' '.join(words[-500:]) if len(words) > 2500 else ''

        # Count sections/headers (look for lines that might be headers)
        lines = content.split('\n')
        potential_headers = [line.strip() for line in lines if line.strip() and len(line.strip()) < 100 and line.strip().isupper() or line.strip().endswith(':')]

        summary = f"""📊 DOCUMENT SUMMARY (Large Document Handler)

**Title**: {document.get('title')}
**Word Count**: {word_count:,} words
**Estimated Tokens**: ~{int(word_count * 1.3):,} tokens
**Status**: Too large for single read - returning structured summary

---

**BEGINNING** (First 2,000 words):
{beginning}

[... Middle section omitted to prevent context overflow ...]

**ENDING** (Last 500 words):
{ending}

---

**READING STRATEGIES**:
1. Use max_words=50000 to read first ~65K tokens (safe for Claude's 200K window)
2. Request specific sections by asking about topics
3. Use multiple reads with different max_words offsets
4. Export to local file for full offline reading

**DETECTED STRUCTURE**:
- Total words: {word_count:,}
- Potential sections/headers: {len(potential_headers)}
- Document length: {'Very Large (>50K words)' if word_count > 50000 else 'Large'}
"""
        return summary

    def list_recent_documents(self, limit: int = 10,
                             folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List recent Google Docs with optional folder filter.
        """
        try:
            query = "mimeType='application/vnd.google-apps.document'"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime, webViewLink, owners)',
                orderBy='modifiedTime desc',
                pageSize=limit
            ).execute()

            files = results.get('files', [])

            if self.console:
                from rich.table import Table
                from rich.panel import Panel

                table = Table(title="📚 Recent Documents")
                table.add_column("Title", style="cyan", no_wrap=False)
                table.add_column("Modified", style="yellow")
                table.add_column("Owner", style="dim")

                for f in files:
                    owners = ', '.join([o.get('displayName', o.get('emailAddress', 'Unknown'))
                                       for o in f.get('owners', [])])
                    table.add_row(
                        f['name'][:50],
                        f['modifiedTime'][:10],
                        owners[:30]
                    )

                self.console.print(Panel(table, border_style="cyan"))

            return {
                'success': True,
                'documents': [
                    {
                        'id': f['id'],
                        'name': f['name'],
                        'modified': f['modifiedTime'],
                        'url': f['webViewLink'],
                        'owners': [o.get('displayName', o.get('emailAddress', 'Unknown'))
                                  for o in f.get('owners', [])]
                    }
                    for f in files
                ],
                'count': len(files),
                'message': f"📚 Found {len(files)} recent documents"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to list documents: {str(e)}"
            }

    def search_documents(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for documents and spreadsheets by name or content.
        """
        try:
            # Search both Docs and Sheets
            doc_query = f"mimeType='application/vnd.google-apps.document' and (name contains '{query}' or fullText contains '{query}')"
            sheet_query = f"mimeType='application/vnd.google-apps.spreadsheet' and name contains '{query}'"

            # Search documents
            doc_results = self.drive_service.files().list(
                q=doc_query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime, webViewLink)',
                pageSize=limit
            ).execute()

            # Search spreadsheets
            sheet_results = self.drive_service.files().list(
                q=sheet_query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime, webViewLink)',
                pageSize=limit
            ).execute()

            docs = doc_results.get('files', [])
            sheets = sheet_results.get('files', [])

            all_results = []
            for f in docs:
                all_results.append({
                    'id': f['id'],
                    'name': f['name'],
                    'type': 'document',
                    'modified': f['modifiedTime'],
                    'url': f['webViewLink']
                })

            for f in sheets:
                all_results.append({
                    'id': f['id'],
                    'name': f['name'],
                    'type': 'spreadsheet',
                    'modified': f['modifiedTime'],
                    'url': f['webViewLink']
                })

            # Sort by modified time
            all_results.sort(key=lambda x: x['modified'], reverse=True)

            if self.console:
                from rich.table import Table
                from rich.panel import Panel

                table = Table(title=f"🔍 Search Results: '{query}'")
                table.add_column("Type", style="magenta", width=12)
                table.add_column("Title", style="cyan", no_wrap=False)
                table.add_column("Modified", style="yellow")

                for r in all_results[:limit]:
                    icon = "📝" if r['type'] == 'document' else "📊"
                    table.add_row(
                        f"{icon} {r['type']}",
                        r['name'][:50],
                        r['modified'][:10]
                    )

                self.console.print(Panel(table, border_style="cyan"))

            return {
                'success': True,
                'results': all_results[:limit],
                'total_found': len(all_results),
                'message': f"🔍 Found {len(all_results)} results for '{query}'"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Search failed: {str(e)}"
            }

    # ==================== GOOGLE DRIVE FILE OPERATIONS ====================

    def upload_file(self, file_path: str, folder_id: str = None, mime_type: str = None) -> Dict[str, Any]:
        """
        Upload a file to Google Drive.

        Args:
            file_path: Local path to the file to upload
            folder_id: Optional Drive folder ID to upload to
            mime_type: Optional MIME type (auto-detected if not provided)

        Returns:
            Dict with success status, file_id, and file_url
        """
        try:
            from googleapiclient.http import MediaFileUpload
            import mimetypes

            # Get file name
            file_name = Path(file_path).name

            # Auto-detect MIME type if not provided
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'

            # Prepare file metadata
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            # Upload file
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            return {
                "success": True,
                "file_id": file.get('id'),
                "file_name": file.get('name'),
                "file_url": file.get('webViewLink'),
                "message": f"✅ Uploaded {file_name} to Google Drive"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to upload file: {str(e)}"
            }

    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Dict[str, Any]:
        """
        Create a new folder in Google Drive.

        Args:
            folder_name: Name of the folder to create
            parent_folder_id: Optional parent folder ID

        Returns:
            Dict with success status, folder_id, and folder_url
        """
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]

            folder = self.drive_service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()

            return {
                "success": True,
                "folder_id": folder.get('id'),
                "folder_name": folder.get('name'),
                "folder_url": folder.get('webViewLink'),
                "message": f"✅ Created folder '{folder_name}'"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create folder: {str(e)}"
            }

    def download_file(self, file_id: str, destination_path: str) -> Dict[str, Any]:
        """
        Download a file from Google Drive.

        Args:
            file_id: Google Drive file ID
            destination_path: Local path to save the file

        Returns:
            Dict with success status and file path
        """
        try:
            from googleapiclient.http import MediaIoBaseDownload
            import io

            # Get file metadata
            file_metadata = self.drive_service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', 'downloaded_file')
            mime_type = file_metadata.get('mimeType', '')

            # Handle Google Workspace files (need export)
            if mime_type.startswith('application/vnd.google-apps'):
                # Map Google MIME types to export formats
                export_formats = {
                    'application/vnd.google-apps.document': 'application/pdf',
                    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                }

                export_mime = export_formats.get(mime_type, 'application/pdf')
                request = self.drive_service.files().export_media(fileId=file_id, mimeType=export_mime)
            else:
                # Regular file download
                request = self.drive_service.files().get_media(fileId=file_id)

            # Download file
            fh = io.FileIO(destination_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            fh.close()

            return {
                "success": True,
                "file_path": destination_path,
                "file_name": file_name,
                "message": f"✅ Downloaded {file_name} to {destination_path}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to download file: {str(e)}"
            }

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete a file from Google Drive.

        Args:
            file_id: Google Drive file ID to delete

        Returns:
            Dict with success status
        """
        try:
            # Get file name before deleting
            file_metadata = self.drive_service.files().get(fileId=file_id, fields='name').execute()
            file_name = file_metadata.get('name', 'Unknown')

            # Delete the file
            self.drive_service.files().delete(fileId=file_id).execute()

            return {
                "success": True,
                "file_id": file_id,
                "message": f"✅ Deleted '{file_name}' from Google Drive"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete file: {str(e)}"
            }

    def list_files(self, folder_id: str = None, limit: int = 20) -> Dict[str, Any]:
        """
        List files in Google Drive.

        Args:
            folder_id: Optional folder ID to list files from
            limit: Maximum number of files to return

        Returns:
            Dict with success status and list of files
        """
        try:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = self.drive_service.files().list(
                q=query,
                pageSize=limit,
                fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
                orderBy="modifiedTime desc"
            ).execute()

            files = results.get('files', [])

            return {
                "success": True,
                "files": files,
                "count": len(files),
                "message": f"Found {len(files)} files"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list files: {str(e)}"
            }


# ==================== CONVENIENCE FUNCTIONS ====================

def create_google_workspace_consciousness(config=None):
    """Create and return a GoogleWorkspaceConsciousness instance"""
    # Try to get existing credentials from config
    creds = None

    if config:
        # Check for existing Gmail credentials
        if hasattr(config, 'gmail') and hasattr(config.gmail, 'credentials'):
            creds = config.gmail.credentials
        # Check for existing stored credentials
        elif hasattr(config, 'workspace'):
            import pickle
            token_file = Path(config.workspace) / 'google_token.pickle'
            if token_file.exists():
                with open(token_file, 'rb') as f:
                    creds = pickle.load(f)

    workspace_dir = config.workspace if config and hasattr(config, 'workspace') else "./coco_workspace"

    return GoogleWorkspaceConsciousness(
        existing_creds=creds,
        workspace_dir=workspace_dir,
        config=config
    )

    # ==================== RICH UI ENHANCEMENTS ====================

    def _display_document_rich(self, content: str, title: str = "Document",
                              structure: dict = None) -> None:
        """Enhanced document display with TOC sidebar"""
        if not self.console:
            print(content)
            return

        from rich.layout import Layout
        from rich.panel import Panel

        # Create layout with TOC if structure available
        if structure and structure.get('headings'):
            layout = Layout()
            layout.split_row(
                Layout(self._create_toc(structure), name="toc", ratio=1),
                Layout(Panel(content[:2000], title=title), name="content", ratio=3)
            )
            self.console.print(layout)
        else:
            # Simple display for unstructured docs
            self.console.print(Panel(
                content[:2000] + "\n\n[dim]... (showing first 2000 chars)[/dim]"
                if len(content) > 2000 else content,
                title=f"📄 {title}",
                border_style="cyan"
            ))

    def _create_toc(self, structure: dict) -> "Panel":
        """Create table of contents panel"""
        from rich.panel import Panel

        headings = structure.get('headings', [])
        toc_lines = []
        for h in headings[:15]:  # Limit to 15 headings
            level = h.get('level', 1)
            text = h.get('text', '')[:30]
            indent = "  " * (level - 1)
            toc_lines.append(f"{indent}• {text}")

        return Panel(
            "\n".join(toc_lines) if toc_lines else "[dim]No headings[/dim]",
            title="📑 Structure",
            border_style="blue"
        )

    def _display_search_results(self, results: List[dict]) -> None:
        """Display search results in a rich table"""
        if not self.console:
            for r in results:
                print(f"- {r.get('name', 'Untitled')}")
            return

        from rich.table import Table

        table = Table(
            title="🔍 Search Results",
            show_header=True,
            header_style="bold magenta"
        )

        table.add_column("#", width=3)
        table.add_column("📄 Name", style="cyan")
        table.add_column("📁 Type", width=10)
        table.add_column("🕐 Modified", width=12)

        for idx, result in enumerate(results[:10], 1):
            mime_type = result.get('mimeType', '')
            doc_type = "Doc" if 'document' in mime_type else "Sheet" if 'spreadsheet' in mime_type else "Other"
            modified = result.get('modifiedTime', '')[:10] if result.get('modifiedTime') else 'Unknown'

            table.add_row(
                str(idx),
                result.get('name', 'Untitled')[:50],
                doc_type,
                modified
            )

        self.console.print(table)

    def _show_append_preview(self, doc_name: str, content: str) -> bool:
        """Show preview before appending with confirmation"""
        if not self.console:
            print(f"Appending to {doc_name}: {content[:100]}...")
            return True

        from rich.panel import Panel
        from rich.prompt import Confirm

        preview = Panel(
            f"[yellow]Adding to:[/yellow] {doc_name}\n\n"
            f"[cyan]New content:[/cyan]\n{content[:500]}",
            title="✨ Append Preview",
            border_style="yellow"
        )
        self.console.print(preview)

        return Confirm.ask("[green]Proceed with append?[/green]", default=True)

    def get_document_structure(self, document_id: str) -> Dict[str, Any]:
        """Extract document structure including headings and sections"""
        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Get the document
            document = self.docs_service.documents().get(
                documentId=doc_id
            ).execute()

            headings = []
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    style = element['paragraph'].get('paragraphStyle', {}).get('namedStyleType', '')
                    if 'HEADING' in style or style == 'TITLE':
                        # Extract heading text
                        text_parts = []
                        for elem in element['paragraph']['elements']:
                            if 'textRun' in elem:
                                text_parts.append(elem['textRun']['content'].strip())

                        if text_parts:
                            level = 0
                            if style == 'TITLE':
                                level = 0
                            elif 'HEADING_1' in style:
                                level = 1
                            elif 'HEADING_2' in style:
                                level = 2
                            elif 'HEADING_3' in style:
                                level = 3
                            else:
                                level = 4

                            headings.append({
                                'level': level,
                                'text': ' '.join(text_parts),
                                'style': style
                            })

            return {
                'success': True,
                'headings': headings,
                'document_id': doc_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'headings': []
            }

    def search_drive(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search Google Drive for documents and files."""
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.search_drive(query, limit)

        try:
            if not self.drive_service:
                return {
                    "success": False,
                    "error": "Drive service not initialized"
                }

            # Search for files
            results = self.drive_service.files().list(
                q=f"name contains '{query}'",
                pageSize=limit,
                fields="files(id, name, mimeType, modifiedTime, owners)"
            ).execute()

            files = results.get('files', [])

            return {
                "success": True,
                "files": files,
                "count": len(files)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ==================== GOOGLE DRIVE FILE OPERATIONS ====================

    def upload_file(self, file_path: str, folder_id: str = None, mime_type: str = None) -> Dict[str, Any]:
        """
        Upload a file to Google Drive.

        Args:
            file_path: Local path to the file to upload
            folder_id: Optional Drive folder ID to upload to
            mime_type: Optional MIME type (auto-detected if not provided)

        Returns:
            Dict with success status, file_id, and file_url
        """
        try:
            from googleapiclient.http import MediaFileUpload
            import mimetypes

            # Get file name
            file_name = Path(file_path).name

            # Auto-detect MIME type if not provided
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'

            # Prepare file metadata
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            # Upload file
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            return {
                "success": True,
                "file_id": file.get('id'),
                "file_name": file.get('name'),
                "file_url": file.get('webViewLink'),
                "message": f"✅ Uploaded {file_name} to Google Drive"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to upload file: {str(e)}"
            }

    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Dict[str, Any]:
        """
        Create a new folder in Google Drive.

        Args:
            folder_name: Name of the folder to create
            parent_folder_id: Optional parent folder ID

        Returns:
            Dict with success status, folder_id, and folder_url
        """
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]

            folder = self.drive_service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()

            return {
                "success": True,
                "folder_id": folder.get('id'),
                "folder_name": folder.get('name'),
                "folder_url": folder.get('webViewLink'),
                "message": f"✅ Created folder '{folder_name}'"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create folder: {str(e)}"
            }

    def download_file(self, file_id: str, destination_path: str) -> Dict[str, Any]:
        """
        Download a file from Google Drive.

        Args:
            file_id: Google Drive file ID
            destination_path: Local path to save the file

        Returns:
            Dict with success status and file path
        """
        try:
            from googleapiclient.http import MediaIoBaseDownload
            import io

            # Get file metadata
            file_metadata = self.drive_service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', 'downloaded_file')
            mime_type = file_metadata.get('mimeType', '')

            # Handle Google Workspace files (need export)
            if mime_type.startswith('application/vnd.google-apps'):
                # Map Google MIME types to export formats
                export_formats = {
                    'application/vnd.google-apps.document': 'application/pdf',
                    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                }

                export_mime = export_formats.get(mime_type, 'application/pdf')
                request = self.drive_service.files().export_media(fileId=file_id, mimeType=export_mime)
            else:
                # Regular file download
                request = self.drive_service.files().get_media(fileId=file_id)

            # Download file
            fh = io.FileIO(destination_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            fh.close()

            return {
                "success": True,
                "file_path": destination_path,
                "file_name": file_name,
                "message": f"✅ Downloaded {file_name} to {destination_path}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to download file: {str(e)}"
            }

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete a file from Google Drive.

        Args:
            file_id: Google Drive file ID to delete

        Returns:
            Dict with success status
        """
        try:
            # Get file name before deleting
            file_metadata = self.drive_service.files().get(fileId=file_id, fields='name').execute()
            file_name = file_metadata.get('name', 'Unknown')

            # Delete the file
            self.drive_service.files().delete(fileId=file_id).execute()

            return {
                "success": True,
                "file_id": file_id,
                "message": f"✅ Deleted '{file_name}' from Google Drive"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete file: {str(e)}"
            }

    def list_files(self, folder_id: str = None, limit: int = 20) -> Dict[str, Any]:
        """
        List files in Google Drive.

        Args:
            folder_id: Optional folder ID to list files from
            limit: Maximum number of files to return

        Returns:
            Dict with success status and list of files
        """
        try:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = self.drive_service.files().list(
                q=query,
                pageSize=limit,
                fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
                orderBy="modifiedTime desc"
            ).execute()

            files = results.get('files', [])

            return {
                "success": True,
                "files": files,
                "count": len(files),
                "message": f"Found {len(files)} files"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list files: {str(e)}"
            }

    # ==================== DOCUMENT APPEND ====================

    def append_to_document(self, document_id: str, content: str,
                          show_preview: bool = True) -> Dict[str, Any]:
        """Append content to end of document with optional preview"""
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.append_to_document(document_id, content, show_preview)

        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Get document to find end position
            document = self.docs_service.documents().get(
                documentId=doc_id
            ).execute()

            doc_title = document.get('title', 'Untitled')

            # Show preview if requested
            if show_preview and self.console:
                if not self._show_append_preview(doc_title, content):
                    return {
                        'success': False,
                        'message': "Append cancelled by user"
                    }

            # Find end index
            end_index = 1
            body = document.get('body', {})
            if body.get('content'):
                last_content = body['content'][-1]
                end_index = last_content.get('endIndex', 1) - 1

            # Append the content
            requests = [{
                'insertText': {
                    'location': {'index': end_index},
                    'text': f"\n\n{content}"
                }
            }]

            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            if self.console:
                from rich.panel import Panel
                self.console.print(Panel(
                    f"[green]✅ Successfully appended to document[/green]\n\n"
                    f"📝 Document: {doc_title}\n"
                    f"📏 Added: {len(content)} characters",
                    title="Append Complete",
                    border_style="green"
                ))

            return {
                'success': True,
                'document_id': doc_id,
                'message': f"✅ Appended {len(content)} characters to {doc_title}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to append: {str(e)}"
            }

    def test_google_workspace_rich_ui(self) -> bool:
        """Test Rich UI enhancements"""
        if not self.console:
            print("Console not available for Rich UI testing")
            return False

        from rich.status import Status
        from rich.panel import Panel

        try:
            # Test document creation with rich feedback
            with self.console.status("[cyan]Creating test document...[/cyan]"):
                doc_result = self.create_document(
                    "COCO Rich UI Test",
                    "# Testing Enhanced Display\n\nThis is a test of the Rich UI enhancements."
                )

            if not doc_result['success']:
                raise Exception(doc_result.get('error', 'Creation failed'))

            doc_id = doc_result['document_id']

            self.console.print(Panel(
                f"✅ Document created: {doc_result['title']}",
                border_style="green"
            ))

            # Test reading with structure
            with self.console.status("[cyan]Reading document with structure...[/cyan]"):
                content_result = self.read_document(doc_id)
                structure = self.get_document_structure(doc_id)

            if content_result['success']:
                self._display_document_rich(
                    content_result['content'],
                    content_result['title'],
                    structure
                )

            # Test search display
            with self.console.status("[cyan]Searching documents...[/cyan]"):
                search_result = self.search_documents("test", limit=5)

            if search_result['success']:
                self._display_search_results(search_result.get('files', []))

            return True

        except Exception as e:
            self.console.print(f"[red]Test failed: {e}[/red]")
            return False


# ==================== MISSING METHOD STUBS WITH SIMPLIFIED FALLBACK ====================

    def update_document(self, document_id: str, updates: list) -> Dict[str, Any]:
        """Update document content with batch update requests"""
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.update_document(document_id, updates)

        try:
            # Extract ID from URL if needed
            if 'docs.google.com' in document_id:
                doc_id = document_id.split('/d/')[1].split('/')[0]
            else:
                doc_id = document_id

            # Apply batch updates
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': updates}
            ).execute()

            return {
                'success': True,
                'document_id': doc_id,
                'message': f"✅ Document updated with {len(updates)} operations"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to update document: {str(e)}"
            }

    def create_spreadsheet(self, title: str, headers: list = None, data: list = None) -> Dict[str, Any]:
        """Create a new spreadsheet"""
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.create_spreadsheet(title, headers, data)

        try:
            # Create the spreadsheet
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }

            result = self.sheets_service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId,spreadsheetUrl,properties'
            ).execute()

            spreadsheet_id = result['spreadsheetId']
            spreadsheet_url = result['spreadsheetUrl']

            # If headers or data provided, add them
            if headers or data:
                values = []
                if headers:
                    values.append(headers)
                if data:
                    # Ensure all data rows are lists and properly formatted
                    for row in data:
                        if isinstance(row, list):
                            # Convert all values to strings to avoid type issues
                            values.append([str(cell) if cell is not None else '' for cell in row])
                        else:
                            values.append([str(row)])

                # Use append instead of update for better compatibility
                self.sheets_service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range='Sheet1!A1',
                    valueInputOption='USER_ENTERED',
                    insertDataOption='INSERT_ROWS',
                    body={'values': values}
                ).execute()

            return {
                'success': True,
                'spreadsheet_id': spreadsheet_id,
                'url': spreadsheet_url,
                'title': title,
                'message': f"✅ Spreadsheet '{title}' created successfully"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create spreadsheet: {str(e)}"
            }

    def read_spreadsheet(self, spreadsheet_id: str = None, spreadsheet_url: str = None, range_notation: str = None) -> Dict[str, Any]:
        """Read spreadsheet data"""
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.read_spreadsheet(spreadsheet_id, spreadsheet_url, range_notation)

        try:
            # Extract ID from URL if provided
            if spreadsheet_url and 'docs.google.com/spreadsheets' in spreadsheet_url:
                sheet_id = spreadsheet_url.split('/d/')[1].split('/')[0]
            elif spreadsheet_id and 'docs.google.com/spreadsheets' in spreadsheet_id:
                sheet_id = spreadsheet_id.split('/d/')[1].split('/')[0]
            elif spreadsheet_id:
                sheet_id = spreadsheet_id
            else:
                return {
                    'success': False,
                    'error': 'Must provide spreadsheet_id or spreadsheet_url'
                }

            # Default range if not specified
            range_name = range_notation or 'Sheet1'

            # Get spreadsheet metadata
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()

            # Get values
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])

            return {
                'success': True,
                'spreadsheet_id': sheet_id,
                'title': spreadsheet.get('properties', {}).get('title'),
                'range': range_name,
                'data': values,
                'rows': len(values),
                'columns': len(values[0]) if values else 0,
                'url': f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to read spreadsheet: {str(e)}"
            }

    def update_spreadsheet(self, spreadsheet_id: str, range_notation: str, values: list) -> Dict[str, Any]:
        """Update spreadsheet data"""
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.update_spreadsheet(spreadsheet_id, range_notation, values)

        try:
            # Extract ID from URL if needed
            if 'docs.google.com/spreadsheets' in spreadsheet_id:
                sheet_id = spreadsheet_id.split('/d/')[1].split('/')[0]
            else:
                sheet_id = spreadsheet_id

            # Update values
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_notation,
                valueInputOption='USER_ENTERED',
                body={'values': values}
            ).execute()

            return {
                'success': True,
                'spreadsheet_id': sheet_id,
                'updated_cells': result.get('updatedCells', 0),
                'updated_range': result.get('updatedRange'),
                'message': f"✅ Updated {result.get('updatedCells', 0)} cells"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to update spreadsheet: {str(e)}"
            }

    def export_document(self, document_id: str, format_type: str = 'pdf') -> Dict[str, Any]:
        """Export document to different format"""
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.export_document(document_id, format_type)

        # OAuth implementation would require proper auth
        return {
            "success": False,
            "error": "OAuth authentication required for document export"
        }

    def share_document(self, document_id: str, email: str, role: str = 'writer') -> Dict[str, Any]:
        """Share document with others"""
        # Use simplified mode if OAuth not available
        if self.simplified_mode and self.simplified:
            return self.simplified.share_document(document_id, email, role)

        # OAuth implementation would require proper auth
        return {
            "success": False,
            "error": "OAuth authentication required for document sharing"
        }


if __name__ == "__main__":
    print("🧠 Google Workspace Consciousness Module")
    print("=" * 50)

    # Test initialization
    try:
        workspace = GoogleWorkspaceConsciousness()
        print("✅ Module loaded successfully")

        if workspace.docs_service:
            print("✅ Google Docs service initialized")
        if workspace.sheets_service:
            print("✅ Google Sheets service initialized")
        if workspace.drive_service:
            print("✅ Google Drive service initialized")

        if not any([workspace.docs_service, workspace.sheets_service]):
            print("⚠️ Services pending - configure OAuth2 credentials")
            print("\nTo use this module:")
            print("1. Ensure Gmail is working in COCO")
            print("2. Or set these environment variables:")
            print("   - GMAIL_CLIENT_ID")
            print("   - GMAIL_CLIENT_SECRET")
            print("   - GMAIL_ACCESS_TOKEN")
            print("   - GMAIL_REFRESH_TOKEN")

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
# Google Docs Integration Plan for COCO

## Executive Summary
This document outlines the complete integration architecture for adding Google Docs capabilities to COCO's suite of digital consciousness extensions, following the existing patterns established for Gmail and Google Calendar.

## Current Architecture Analysis

### Existing Google Services Integration
COCO currently has successful OAuth2 integration with:
- **Gmail**: Full send/receive capabilities via SMTP/IMAP with app passwords
- **Google Calendar**: OAuth2-based event management (implied from .env)

### Key Design Patterns
1. **Digital Embodiment Philosophy**: Tools are consciousness extensions, not external utilities
2. **Monolithic Architecture**: Single `cocoa.py` file with modular extensions
3. **OAuth2 Infrastructure**: Already configured for Google services

## Google Docs API Integration Architecture

### API Capabilities Required
Based on the Google Docs API v1 specification:
- `documents.create`: Create blank documents
- `documents.get`: Retrieve document content and metadata
- `documents.batchUpdate`: Apply updates to documents

### Implementation Approach

#### Phase 1: Authentication Extension
```python
# Extend existing OAuth2 scope in .env
GSUITE_SCOPES=gmail.readonly,gmail.send,gmail.compose,gmail.modify,calendar,drive,docs,sheets,userinfo.email,userinfo.profile
# Add: https://www.googleapis.com/auth/documents

# Google Docs specific configuration
GOOGLE_DOCS_API_VERSION=v1
GOOGLE_DOCS_SERVICE_NAME=docs
```

#### Phase 2: Google Docs Consciousness Class
```python
class GoogleDocsConsciousness:
    """
    Google Docs as an extension of COCO's document creation consciousness.
    Documents flow as natural expressions of digital thought.
    """

    def __init__(self, config=None):
        self.config = config
        self.console = config.console if config else None
        self.service = None
        self.initialize_service()

    def initialize_service(self):
        """Initialize Google Docs service using existing OAuth2 credentials"""
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        # Reuse existing OAuth token from Gmail/Calendar
        creds = Credentials(
            token=os.getenv('GMAIL_ACCESS_TOKEN'),
            refresh_token=os.getenv('GMAIL_REFRESH_TOKEN'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.getenv('GMAIL_CLIENT_ID'),
            client_secret=os.getenv('GMAIL_CLIENT_SECRET'),
            scopes=['https://www.googleapis.com/auth/documents']
        )

        self.service = build('docs', 'v1', credentials=creds)

        if self.console:
            self.console.print("📝 Google Docs Consciousness initialized")
```

### Core Tool Functions

#### 1. Create Document
```python
def create_document(self, title: str, content: str = None) -> dict:
    """
    CREATE - Manifest digital thoughts into Google Docs

    Args:
        title: Document title
        content: Optional initial content

    Returns:
        Document ID and URL
    """
    try:
        # Create blank document
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

        return {
            'success': True,
            'document_id': doc_id,
            'document_url': f'https://docs.google.com/document/d/{doc_id}/edit',
            'message': f"📝 Created document: {title}"
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

#### 2. Read Document
```python
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
        # Extract ID from URL if provided
        if document_url and not document_id:
            import re
            match = re.search(r'/document/d/([a-zA-Z0-9-_]+)', document_url)
            if match:
                document_id = match.group(1)

        # Retrieve document
        document = self.service.documents().get(
            documentId=document_id
        ).execute()

        # Extract text content
        content = self._extract_text_from_document(document)

        return {
            'success': True,
            'title': document.get('title'),
            'content': content,
            'word_count': len(content.split()),
            'last_modified': document.get('revisionId'),
            'document_id': document_id
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _extract_text_from_document(self, document) -> str:
    """Extract plain text from Google Docs structure"""
    text = []
    for element in document.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for text_run in element['paragraph'].get('elements', []):
                if 'textRun' in text_run:
                    text.append(text_run['textRun'].get('content', ''))
    return ''.join(text)
```

#### 3. Update Document
```python
def update_document(self, document_id: str, updates: list) -> dict:
    """
    UPDATE - Evolve document content through consciousness flow

    Args:
        document_id: Document to update
        updates: List of update operations

    Returns:
        Update status
    """
    try:
        # Format updates for batchUpdate API
        requests = []
        for update in updates:
            if update['type'] == 'append_text':
                # Get document to find end index
                doc = self.service.documents().get(
                    documentId=document_id
                ).execute()
                end_index = doc.get('body').get('content')[-1].get('endIndex', 1) - 1

                requests.append({
                    'insertText': {
                        'location': {'index': end_index},
                        'text': update['text']
                    }
                })

            elif update['type'] == 'replace_text':
                requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': update['find'],
                            'matchCase': update.get('match_case', True)
                        },
                        'replaceText': update['replace']
                    }
                })

            elif update['type'] == 'format_text':
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': update['start'],
                            'endIndex': update['end']
                        },
                        'textStyle': update['style'],
                        'fields': update['fields']
                    }
                })

        # Execute batch update
        result = self.service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        return {
            'success': True,
            'replies_count': len(result.get('replies', [])),
            'message': f"✅ Document updated successfully"
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

### Integration into ToolSystem

Add to `cocoa.py` ToolSystem class:

```python
def create_google_doc(self, title: str, content: str = None) -> str:
    """CREATE DOC - Manifest thoughts into Google Docs"""
    if not self.google_docs:
        return "❌ Google Docs consciousness not available. Please check configuration."

    result = self.google_docs.create_document(title, content)
    if result['success']:
        return f"✅ **Document Created**\n\n📝 Title: {title}\n🔗 URL: {result['document_url']}\n📄 ID: {result['document_id']}"
    else:
        return f"❌ **Document Creation Failed**\n\n{result['error']}"

def read_google_doc(self, document_id: str = None, document_url: str = None) -> str:
    """READ DOC - Perceive Google Docs content"""
    if not self.google_docs:
        return "❌ Google Docs consciousness not available."

    result = self.google_docs.read_document(document_id, document_url)
    if result['success']:
        from rich.panel import Panel
        from rich.markdown import Markdown

        content_preview = result['content'][:500] + "..." if len(result['content']) > 500 else result['content']

        return Panel(
            Markdown(f"**{result['title']}**\n\n{content_preview}\n\n---\n📊 Word Count: {result['word_count']}"),
            title="📝 Google Doc Content",
            border_style="cyan"
        )
    else:
        return f"❌ **Failed to Read Document**\n\n{result['error']}"

def update_google_doc(self, document_id: str, updates: list) -> str:
    """UPDATE DOC - Evolve Google Docs content"""
    if not self.google_docs:
        return "❌ Google Docs consciousness not available."

    result = self.google_docs.update_document(document_id, updates)
    if result['success']:
        return f"✅ **Document Updated**\n\n{result['message']}"
    else:
        return f"❌ **Update Failed**\n\n{result['error']}"
```

### Tool Registration in ConsciousnessEngine

Add to function calling tools list:

```python
{
    "type": "function",
    "function": {
        "name": "create_google_doc",
        "description": "Create a new Google Doc with optional initial content",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Document title"
                },
                "content": {
                    "type": "string",
                    "description": "Optional initial content"
                }
            },
            "required": ["title"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "read_google_doc",
        "description": "Read content from a Google Doc",
        "parameters": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Google Docs document ID"
                },
                "document_url": {
                    "type": "string",
                    "description": "Full Google Docs URL (alternative to ID)"
                }
            }
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "update_google_doc",
        "description": "Update content in a Google Doc",
        "parameters": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID to update"
                },
                "updates": {
                    "type": "array",
                    "description": "List of update operations",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["append_text", "replace_text", "format_text"]
                            },
                            "text": {"type": "string"},
                            "find": {"type": "string"},
                            "replace": {"type": "string"},
                            "style": {"type": "object"},
                            "start": {"type": "integer"},
                            "end": {"type": "integer"}
                        }
                    }
                }
            },
            "required": ["document_id", "updates"]
        }
    }
}
```

## Advanced Features (Future Enhancements)

### 1. Collaborative Editing
```python
def share_document(self, document_id: str, email: str, role: str = 'writer') -> dict:
    """Share document with collaborators"""
    # Use Google Drive API for permissions
    pass

def get_document_comments(self, document_id: str) -> dict:
    """Retrieve comments and suggestions"""
    pass
```

### 2. Template Management
```python
def create_from_template(self, template_id: str, replacements: dict) -> dict:
    """Create document from template with variable replacements"""
    pass
```

### 3. Export Capabilities
```python
def export_document(self, document_id: str, format: str = 'pdf') -> dict:
    """Export document to various formats (PDF, DOCX, HTML, etc.)"""
    pass
```

## Implementation Steps

1. **Add Google API Python Client**:
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. **Update .env Configuration**:
   - Extend GSUITE_SCOPES to include documents scope
   - Ensure OAuth2 credentials are properly configured

3. **Create google_docs_consciousness.py**:
   - Implement the GoogleDocsConsciousness class
   - Follow the same pattern as gmail_consciousness.py

4. **Integrate into cocoa.py**:
   - Import GoogleDocsConsciousness
   - Add initialization in ToolSystem.__init__
   - Register new tool functions
   - Add to ConsciousnessEngine tools list

5. **Testing**:
   ```python
   # test_google_docs_integration.py
   def test_document_creation():
       """Test creating a Google Doc"""
       pass

   def test_document_reading():
       """Test reading document content"""
       pass

   def test_document_updates():
       """Test updating document content"""
       pass
   ```

## Natural Language Usage Examples

Once integrated, COCO will understand:
- "Create a Google Doc titled 'Meeting Notes' with today's agenda"
- "Read the document at [Google Docs URL]"
- "Append the following summary to my project document"
- "Replace all instances of 'draft' with 'final' in document ID xyz"
- "Format the heading as bold in my report"

## Security Considerations

1. **OAuth2 Token Management**: Reuse existing secure token storage
2. **Scope Limitations**: Only request necessary permissions
3. **Error Handling**: Graceful failures with informative messages
4. **Rate Limiting**: Implement exponential backoff for API calls
5. **Data Privacy**: Never log document content in debug mode

## Success Metrics

- ✅ Seamless integration with existing Google services
- ✅ Natural language command understanding
- ✅ Consistent with digital embodiment philosophy
- ✅ No breaking changes to existing functionality
- ✅ Rich terminal UI feedback for all operations

## Conclusion

This integration extends COCO's digital consciousness into document creation and management, maintaining the philosophical approach of tools as consciousness extensions rather than external utilities. The implementation follows established patterns from Gmail and Calendar integrations, ensuring consistency and reliability.
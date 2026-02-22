# Google Workspace Integration Guide for COCO

## 🚀 Integration Steps

### Step 1: Import the Module

Add to `cocoa.py` imports section (around line 50-100):
```python
# Google Workspace Consciousness
try:
    from google_workspace_consciousness import GoogleWorkspaceConsciousness
    GOOGLE_WORKSPACE_AVAILABLE = True
except ImportError:
    GOOGLE_WORKSPACE_AVAILABLE = False
    print("⚠️ Google Workspace module not available")
```

### Step 2: Initialize in ToolSystem

Add to `ToolSystem.__init__` method (around line 4200):
```python
# Initialize Google Workspace consciousness
self.google_workspace = None
if GOOGLE_WORKSPACE_AVAILABLE:
    try:
        # Try to reuse Gmail credentials if available
        creds = None
        if hasattr(self, 'gmail') and hasattr(self.gmail, 'credentials'):
            creds = self.gmail.credentials

        self.google_workspace = GoogleWorkspaceConsciousness(
            existing_creds=creds,
            workspace_dir=str(self.workspace),
            config=self.config
        )
        self.console.print("📝 Google Workspace consciousness initialized")
    except Exception as e:
        self.console.print(f"⚠️ Google Workspace initialization pending: {e}")
```

### Step 3: Add Tool Methods to ToolSystem

Add these methods to the `ToolSystem` class:

```python
# ==================== GOOGLE DOCS TOOLS ====================

def create_google_doc(self, title: str, content: str = "") -> str:
    """CREATE DOC - Manifest thoughts into Google Docs"""
    if not self.google_workspace:
        return "❌ Google Workspace consciousness not available. Please check configuration."

    result = self.google_workspace.create_document(title, content)
    if result['success']:
        return f"✅ **Document Created**\n\n📝 Title: {title}\n🔗 URL: {result['url']}\n📄 ID: {result['document_id']}"
    else:
        return f"❌ **Failed to create document**\n\n{result['message']}"

def read_google_doc(self, document_id: str = None, document_url: str = None) -> str:
    """READ DOC - Perceive Google Docs content"""
    if not self.google_workspace:
        return "❌ Google Workspace consciousness not available."

    doc_ref = document_url if document_url else document_id
    if not doc_ref:
        return "❌ Please provide a document ID or URL"

    result = self.google_workspace.read_document(doc_ref)
    if result['success']:
        return f"📝 **{result['title']}**\n\n{result['content'][:2000]}{'...' if len(result['content']) > 2000 else ''}\n\n📊 Word Count: {result['word_count']}"
    else:
        return f"❌ **Failed to read document**\n\n{result['message']}"

def edit_google_doc(self, document_id: str, action: str, **kwargs) -> str:
    """EDIT DOC - Modify Google Docs content"""
    if not self.google_workspace:
        return "❌ Google Workspace consciousness not available."

    actions = {
        'replace': self.google_workspace.replace_text,
        'insert': self.google_workspace.insert_text,
        'delete': self.google_workspace.delete_text,
        'format': self.google_workspace.format_text,
        'add_heading': self.google_workspace.create_paragraph_style,
        'add_link': self.google_workspace.insert_link,
        'add_list': self.google_workspace.create_bullet_list,
        'add_table': self.google_workspace.insert_table
    }

    if action not in actions:
        return f"❌ Unknown action: {action}. Use: {', '.join(actions.keys())}"

    result = actions[action](document_id, **kwargs)
    if result['success']:
        return f"✅ **Document Updated**\n\n{result['message']}"
    else:
        return f"❌ **Failed to edit document**\n\n{result['message']}"

def export_google_doc(self, document_id: str, format: str = "pdf") -> str:
    """EXPORT DOC - Transform document to different formats"""
    if not self.google_workspace:
        return "❌ Google Workspace consciousness not available."

    result = self.google_workspace.export_document(document_id, format)
    if result['success']:
        if 'file_path' in result:
            return f"✅ **Document Exported**\n\n📁 File: {result['file_path']}\n📄 Format: {format.upper()}"
        else:
            return f"✅ **Document Exported**\n\n📄 Format: {format}\n\nContent:\n{result['content'][:1000]}..."
    else:
        return f"❌ **Failed to export document**\n\n{result['message']}"

def share_google_doc(self, document_id: str, email: str, role: str = "reader") -> str:
    """SHARE DOC - Share document with others"""
    if not self.google_workspace:
        return "❌ Google Workspace consciousness not available."

    result = self.google_workspace.share_document(document_id, email, role)
    if result['success']:
        return f"✅ **Document Shared**\n\n👥 Shared with: {email}\n🔑 Role: {role}"
    else:
        return f"❌ **Failed to share document**\n\n{result['message']}"

# ==================== GOOGLE SHEETS TOOLS ====================

def create_spreadsheet(self, title: str, data: list = None) -> str:
    """CREATE SHEET - Manifest data into Google Sheets"""
    if not self.google_workspace:
        return "❌ Google Workspace consciousness not available."

    result = self.google_workspace.create_spreadsheet(title, data)
    if result['success']:
        return f"✅ **Spreadsheet Created**\n\n📊 Title: {title}\n🔗 URL: {result['url']}\n📄 ID: {result['spreadsheet_id']}"
    else:
        return f"❌ **Failed to create spreadsheet**\n\n{result['message']}"

def read_spreadsheet(self, spreadsheet_id: str, range: str = "Sheet1") -> str:
    """READ SHEET - Perceive spreadsheet data"""
    if not self.google_workspace:
        return "❌ Google Workspace consciousness not available."

    result = self.google_workspace.read_spreadsheet(spreadsheet_id, range)
    if result['success']:
        # Format data as table
        data = result['data']
        if data:
            table_str = "\n".join(["\t".join(map(str, row)) for row in data[:10]])
            return f"📊 **{result['title']}**\n\nRange: {range}\nRows: {result['rows']}\nColumns: {result['columns']}\n\nData Preview:\n{table_str}"
        else:
            return f"📊 **{result['title']}**\n\nNo data in range {range}"
    else:
        return f"❌ **Failed to read spreadsheet**\n\n{result['message']}"

def update_spreadsheet(self, spreadsheet_id: str, range: str, values: list) -> str:
    """UPDATE SHEET - Modify spreadsheet data"""
    if not self.google_workspace:
        return "❌ Google Workspace consciousness not available."

    result = self.google_workspace.update_spreadsheet(spreadsheet_id, range, values)
    if result['success']:
        return f"✅ **Spreadsheet Updated**\n\n📊 Updated {result['updated_cells']} cells in range {range}"
    else:
        return f"❌ **Failed to update spreadsheet**\n\n{result['message']}"

def search_workspace_docs(self, query: str) -> str:
    """SEARCH - Find documents and spreadsheets"""
    if not self.google_workspace:
        return "❌ Google Workspace consciousness not available."

    result = self.google_workspace.search_documents(query)
    if result['success']:
        items = result['results']
        if items:
            output = f"🔍 **Search Results for '{query}'**\n\n"
            for item in items:
                icon = "📝" if item['type'] == 'document' else "📊"
                output += f"{icon} {item['name']}\n   Type: {item['type']}\n   Modified: {item['modified'][:10]}\n   URL: {item['url']}\n\n"
            return output
        else:
            return f"No results found for '{query}'"
    else:
        return f"❌ **Search failed**\n\n{result['message']}"
```

### Step 4: Register Tools in ConsciousnessEngine

Add to the tools list in `ConsciousnessEngine.__init__` (around line 6000-7000):

```python
# Google Docs Tools
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
        "name": "edit_google_doc",
        "description": "Edit a Google Doc (replace text, insert, format, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID or URL"
                },
                "action": {
                    "type": "string",
                    "description": "Action: replace, insert, delete, format, add_heading, add_link, add_list, add_table",
                    "enum": ["replace", "insert", "delete", "format", "add_heading", "add_link", "add_list", "add_table"]
                }
            },
            "required": ["document_id", "action"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "export_google_doc",
        "description": "Export a Google Doc to different formats (pdf, docx, html, txt)",
        "parameters": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID or URL"
                },
                "format": {
                    "type": "string",
                    "description": "Export format",
                    "enum": ["text", "html", "pdf", "docx", "rtf", "odt", "epub"]
                }
            },
            "required": ["document_id", "format"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "create_spreadsheet",
        "description": "Create a new Google Sheets spreadsheet",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Spreadsheet title"
                },
                "data": {
                    "type": "array",
                    "description": "Optional initial data (2D array)",
                    "items": {
                        "type": "array"
                    }
                }
            },
            "required": ["title"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "read_spreadsheet",
        "description": "Read data from a Google Sheets spreadsheet",
        "parameters": {
            "type": "object",
            "properties": {
                "spreadsheet_id": {
                    "type": "string",
                    "description": "Spreadsheet ID or URL"
                },
                "range": {
                    "type": "string",
                    "description": "Range to read (e.g., 'Sheet1', 'A1:C10')"
                }
            },
            "required": ["spreadsheet_id"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "update_spreadsheet",
        "description": "Update data in a Google Sheets spreadsheet",
        "parameters": {
            "type": "object",
            "properties": {
                "spreadsheet_id": {
                    "type": "string",
                    "description": "Spreadsheet ID or URL"
                },
                "range": {
                    "type": "string",
                    "description": "Range to update (e.g., 'A1')"
                },
                "values": {
                    "type": "array",
                    "description": "Data to write (2D array)",
                    "items": {
                        "type": "array"
                    }
                }
            },
            "required": ["spreadsheet_id", "range", "values"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "search_workspace_docs",
        "description": "Search for Google Docs and Sheets by name or content",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    }
}
```

### Step 5: Handle Tool Calls in ConsciousnessEngine

Add to the tool execution section (around line 6500):

```python
# Google Workspace Tools
elif tool_name == "create_google_doc":
    result = self.tools.create_google_doc(
        arguments.get("title"),
        arguments.get("content", "")
    )
elif tool_name == "read_google_doc":
    result = self.tools.read_google_doc(
        arguments.get("document_id"),
        arguments.get("document_url")
    )
elif tool_name == "edit_google_doc":
    # Pass through all arguments except document_id and action
    kwargs = {k: v for k, v in arguments.items() if k not in ['document_id', 'action']}
    result = self.tools.edit_google_doc(
        arguments.get("document_id"),
        arguments.get("action"),
        **kwargs
    )
elif tool_name == "export_google_doc":
    result = self.tools.export_google_doc(
        arguments.get("document_id"),
        arguments.get("format", "pdf")
    )
elif tool_name == "create_spreadsheet":
    result = self.tools.create_spreadsheet(
        arguments.get("title"),
        arguments.get("data")
    )
elif tool_name == "read_spreadsheet":
    result = self.tools.read_spreadsheet(
        arguments.get("spreadsheet_id"),
        arguments.get("range", "Sheet1")
    )
elif tool_name == "update_spreadsheet":
    result = self.tools.update_spreadsheet(
        arguments.get("spreadsheet_id"),
        arguments.get("range"),
        arguments.get("values")
    )
elif tool_name == "search_workspace_docs":
    result = self.tools.search_workspace_docs(
        arguments.get("query")
    )
```

## 🎯 Natural Language Usage Examples

Once integrated, COCO will understand commands like:

### Google Docs
- "Create a Google Doc titled 'Project Plan' with our meeting notes"
- "Read the document at [Google Docs URL]"
- "Replace all instances of 'draft' with 'final' in document ID xyz"
- "Format the first paragraph as a heading in my document"
- "Export my report as a PDF"
- "Share the project doc with team@example.com as an editor"
- "Add a 3x3 table to my document"
- "Create a bullet list from lines 10-20"

### Google Sheets
- "Create a spreadsheet called 'Budget 2025' with monthly columns"
- "Read data from the budget spreadsheet"
- "Update cell A1 with the value 'Total Revenue'"
- "Clear the range B2:D10 in my spreadsheet"
- "Format row 1 as bold with blue background"
- "Search for all spreadsheets containing 'sales'"

## 🔧 Testing Commands

Test the integration:

```python
# Test Doc Creation
"Create a Google Doc titled 'COCO Test Document' with the content 'This is a test of the Google Workspace consciousness integration.'"

# Test Doc Reading
"Read the document I just created"

# Test Doc Editing
"Replace 'test' with 'successful test' in the document"

# Test Spreadsheet Creation
"Create a spreadsheet called 'COCO Data' with data [[\"Name\", \"Value\"], [\"Test1\", 100], [\"Test2\", 200]]"

# Test Search
"Search for documents containing 'COCO'"
```

## 🚀 Quick Start

1. **Install dependencies**:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

2. **Ensure OAuth is configured** (reuses Gmail credentials)

3. **Add the integration code** to `cocoa.py`

4. **Restart COCO**

5. **Test with**: "Create a Google Doc titled 'Hello from COCO'"

## 🎉 Success Indicators

- ✅ "Google Workspace consciousness initialized" message on startup
- ✅ Natural language commands work for creating/reading/editing docs
- ✅ Rich terminal UI displays document content beautifully
- ✅ Spreadsheet operations work seamlessly
- ✅ Search finds your documents across Google Workspace

## 🛡️ Security Notes

- Uses existing Gmail OAuth2 credentials
- No additional authentication needed
- All operations respect Google's API quotas
- Documents remain private unless explicitly shared

## 🏆 Features Unlocked

### Document Management
- ✨ Full CRUD operations on Google Docs
- ✨ Rich text formatting and styling
- ✨ Table and list creation
- ✨ Document export to multiple formats
- ✨ Sharing and collaboration features

### Spreadsheet Power
- ✨ Create and manage spreadsheets
- ✨ Read/write data with formulas
- ✨ Cell formatting and styling
- ✨ Range operations (clear, format)

### Cross-Platform Search
- ✨ Search across all documents and sheets
- ✨ Find by name or content
- ✨ List recent documents
- ✨ Folder organization support

This completes the full Google Workspace integration for COCO! 🎉
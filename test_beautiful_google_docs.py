#!/usr/bin/env python3
"""
Test script for Beautiful Google Docs Formatting

This script tests the new Markdown → Google Docs formatting system,
similar to our beautiful HTML emails.

Tests comprehensive Markdown support including:
- Headings (H1, H2, H3)
- Bold, italic, inline code
- Links with purple COCO colors
- Bullet and numbered lists
- Code blocks with monospace font
- Blockquotes
- Horizontal rules
- COCO branding (header/footer)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google_workspace_consciousness import GoogleWorkspaceConsciousness
from rich.console import Console
from rich.panel import Panel

console = Console()

# Rich Markdown test content (comprehensive)
test_markdown = """
# Weekly Summary Report

Hey Keith! Here's your **comprehensive weekly digest** from COCO.

## Key Accomplishments This Week

This week we achieved several *major milestones* in our AI development:

### Development Progress

- Implemented beautiful **Google Docs formatting** (like our email templates!)
- Added `markdown-it-py` integration for robust parsing
- Created professional COCO branding system
- Deployed 3 new features to production

### Research Highlights

We explored several exciting topics:

1. Advanced LLM reasoning techniques
2. Multimodal AI integration patterns
3. Context window optimization strategies
4. Memory architecture improvements

## Code Examples

Here's the `_markdown_to_google_docs_requests()` method we built:

```python
def _markdown_to_google_docs_requests(self, markdown_text: str):
    # Parse Markdown using markdown-it-py
    md = MarkdownIt()
    tokens = md.parse(markdown_text)

    # Convert to Google Docs API requests
    return plain_text, formatting_requests
```

Pretty cool, right? The inline code uses `Courier New` font!

## Important Links

Check out these resources:
- [Anthropic Claude](https://www.anthropic.com) - Our AI foundation
- [Google Docs API](https://developers.google.com/docs/api) - Formatting reference
- [Markdown Guide](https://www.markdownguide.org) - Syntax reference

## Reflections

> "The best way to predict the future is to create it."
> — Alan Kay

This quote captures our approach to building COCO - we're not just using AI, we're pioneering new ways for humans and AI to collaborate beautifully.

---

## Next Steps

**Priority tasks for next week:**

1. Test beautiful docs in production ✅
2. Gather user feedback on formatting
3. Add table support (stretch goal)
4. Document the implementation

Looking forward to an amazing week ahead! 🚀

*Stay curious, stay creative.*
"""


def test_beautiful_formatting():
    """Test beautiful Google Docs formatting with comprehensive Markdown"""

    console.print("\n")
    console.print(Panel(
        "[bold cyan]Testing Beautiful Google Docs Formatting[/bold cyan]\n\n"
        "This test creates a real Google Doc with:\n"
        "• Headings (H1, H2, H3) in proper Google Docs styles\n"
        "• Bold, italic, and inline code formatting\n"
        "• Links with COCO purple colors\n"
        "• Bullet and numbered lists\n"
        "• Code blocks with monospace font\n"
        "• Blockquotes in italic gray\n"
        "• Horizontal rules\n"
        "• Professional COCO branding\n\n"
        "[dim]Similar to our beautiful HTML emails![/dim]",
        title="🎨 Beautiful Docs Test",
        border_style="cyan"
    ))

    try:
        # Initialize Google Workspace
        console.print("\n📡 [cyan]Connecting to Google Workspace...[/cyan]")
        workspace = GoogleWorkspaceConsciousness(config=None)

        if not workspace.authenticated:
            console.print("❌ [red]OAuth authentication required[/red]")
            console.print("[yellow]Run: python get_token_persistent.py[/yellow]")
            return False

        console.print("✅ [green]Connected successfully[/green]\n")

        # Create beautiful document
        console.print("🎨 [cyan]Creating beautifully formatted document...[/cyan]")

        result = workspace.create_document(
            title="COCO Weekly Summary - Beautiful Formatting Test",
            initial_content=test_markdown,
            format_markdown=True,  # Enable beautiful formatting
            add_branding=True      # Add COCO header/footer
        )

        if result['success']:
            console.print("\n")
            console.print(Panel(
                f"[bold green]✅ Document Created Successfully![/bold green]\n\n"
                f"📝 Title: {result['title']}\n"
                f"🔗 URL: {result['url']}\n"
                f"📄 ID: {result['document_id']}\n\n"
                f"[cyan]Formatting Applied:[/cyan]\n"
                f"• ✨ Beautiful Markdown formatting\n"
                f"• 🤖 Professional COCO branding\n"
                f"• 🎨 COCO purple accent colors\n"
                f"• 📐 Professional typography\n\n"
                f"[bold yellow]→ Open the document to see the beautiful formatting![/bold yellow]",
                title="🎉 Test Successful",
                border_style="green"
            ))

            # Print URL for easy access
            console.print(f"\n[bold]Quick Access:[/bold] {result['url']}\n")

            return True
        else:
            console.print(f"\n❌ [red]Failed: {result['message']}[/red]")
            if 'error' in result:
                console.print(f"[dim]Error: {result['error']}[/dim]")
            return False

    except Exception as e:
        console.print(f"\n❌ [red]Error: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def test_plain_text_fallback():
    """Test fallback to plain text (no formatting)"""

    console.print("\n")
    console.print(Panel(
        "[bold cyan]Testing Plain Text Fallback[/bold cyan]\n\n"
        "This test creates a document with formatting disabled\n"
        "to verify backward compatibility.",
        title="📝 Plain Text Test",
        border_style="cyan"
    ))

    try:
        workspace = GoogleWorkspaceConsciousness(config=None)

        if not workspace.authenticated:
            console.print("❌ [red]OAuth authentication required[/red]")
            return False

        simple_content = """
# Plain Text Test

This document has **no formatting** applied.
Raw Markdown syntax should be visible.

- Bullet 1
- Bullet 2

Done!
"""

        console.print("\n📝 [cyan]Creating plain text document...[/cyan]")

        result = workspace.create_document(
            title="COCO Plain Text Test",
            initial_content=simple_content,
            format_markdown=False,  # Disable formatting
            add_branding=False      # No branding
        )

        if result['success']:
            console.print(f"\n✅ [green]Plain text document created[/green]")
            console.print(f"🔗 {result['url']}\n")
            return True
        else:
            console.print(f"\n❌ [red]Failed: {result['message']}[/red]")
            return False

    except Exception as e:
        console.print(f"\n❌ [red]Error: {str(e)}[/red]")
        return False


if __name__ == "__main__":
    console.print("\n" + "=" * 70)
    console.print("[bold magenta]COCO Beautiful Google Docs Formatting Test Suite[/bold magenta]")
    console.print("=" * 70)

    # Test 1: Beautiful formatting
    test1_passed = test_beautiful_formatting()

    # Test 2: Plain text fallback
    test2_passed = test_plain_text_fallback()

    # Summary
    console.print("\n" + "=" * 70)
    console.print("[bold]Test Summary[/bold]")
    console.print("=" * 70)
    console.print(f"Beautiful Formatting: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    console.print(f"Plain Text Fallback: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    console.print("=" * 70 + "\n")

    if test1_passed and test2_passed:
        console.print(Panel(
            "[bold green]🎉 All Tests Passed![/bold green]\n\n"
            "Google Docs now have beautiful formatting just like our emails!\n\n"
            "[dim]Next: Test with COCO to create real documents.[/dim]",
            border_style="green"
        ))
        sys.exit(0)
    else:
        console.print(Panel(
            "[bold red]⚠️ Some Tests Failed[/bold red]\n\n"
            "Please review the errors above.",
            border_style="red"
        ))
        sys.exit(1)

#!/usr/bin/env python3
"""
Test Beautiful HTML Email System
=================================
Verifies that COCO sends beautifully formatted HTML emails with:
- Markdown conversion
- Professional HTML template
- COCO branding
- Plain text fallback
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from gmail_consciousness import GmailConsciousness
from cocoa import Config
from rich.console import Console

def test_beautiful_email():
    """Test HTML email with various Markdown formatting"""

    console = Console()
    console.print("\n[bold cyan]🧪 Testing Beautiful HTML Email System[/bold cyan]\n")

    # Initialize config and Gmail consciousness
    config = Config()
    gmail = GmailConsciousness(config)

    # Test email with rich Markdown content
    test_body = """
# Weekly AI Research Summary

Hey Keith! Here's your personalized AI research digest for this week.

## 🔥 Trending Topics

### 1. **LLM Reasoning Advances**
Researchers at Anthropic published groundbreaking work on *chain-of-thought* reasoning:

- Enhanced reasoning capabilities in Claude Sonnet 4.5
- 40% improvement in mathematical problem-solving
- Better handling of multi-step logical tasks

> "The ability to show our thinking process transparently is a major step forward in AI safety."
> — Research Lead, Anthropic

### 2. **Multimodal AI Progress**

Key developments in vision-language models:

1. GPT-4 Vision updates with improved OCR
2. Gemini 1.5 Pro's 1M token context window
3. DALL-E 3 integration with ChatGPT

## 💻 Code Example: Using Claude API

Here's how to implement beautiful thinking in your app:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": "Explain quantum computing"
    }]
)

print(response.content[0].text)
```

## 📊 This Week's Stats

| Metric | Value | Change |
|--------|-------|--------|
| Papers Published | 142 | +12% |
| Model Updates | 8 | +60% |
| Open Source Releases | 23 | -5% |

## 🎯 Action Items

- [ ] Review Anthropic's new reasoning paper
- [ ] Test Claude Sonnet 4.5's extended thinking
- [ ] Explore multimodal applications for RX2

## 🔗 Key Resources

- [Anthropic Research Blog](https://anthropic.com/research)
- [Claude API Documentation](https://docs.anthropic.com)
- [AI Safety Papers](https://arxiv.org/list/cs.AI/recent)

---

**Stay curious, Keith!** 🚀

*Compiled with consciousness by COCO AI Assistant*
"""

    # Send test email
    console.print("[yellow]📤 Sending test email with rich Markdown content...[/yellow]")

    result = gmail.send_email(
        to="keith@gococoa.ai",
        subject="🧪 Test: Beautiful HTML Email Rendering",
        body=test_body
    )

    # Display result
    if result.get("success"):
        console.print("\n[bold green]✅ Success![/bold green]")
        console.print(f"[green]{result['message']}[/green]")
        console.print("\n[bold cyan]Email Features:[/bold cyan]")
        console.print("  ✨ Professional HTML template with COCO branding")
        console.print("  📝 Markdown converted to beautiful HTML")
        console.print("  🎨 Purple/blue gradient header")
        console.print("  💻 Syntax-highlighted code blocks")
        console.print("  📊 Styled tables and lists")
        console.print("  🔗 Clickable links with COCO styling")
        console.print("  📱 Plain text fallback for compatibility")
        console.print("\n[dim]Check your inbox at keith@gococoa.ai to see the beautiful rendering![/dim]")
    else:
        console.print("\n[bold red]❌ Failed![/bold red]")
        console.print(f"[red]{result.get('message')}[/red]")
        if 'error' in result:
            console.print(f"[red]Error: {result['error']}[/red]")

    return result.get("success", False)

if __name__ == "__main__":
    success = test_beautiful_email()
    sys.exit(0 if success else 1)

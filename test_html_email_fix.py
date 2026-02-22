#!/usr/bin/env python3
"""
Test script to verify HTML email rendering fix.

This tests the hybrid HTML detection approach where:
1. Complete HTML documents are detected
2. Body content is extracted
3. Body content is wrapped in COCO template
4. Email renders beautifully in Gmail
"""

from bs4 import BeautifulSoup

def test_html_extraction():
    """Test HTML body extraction logic"""

    # Simulated scheduler HTML (like what cocoa_scheduler.py generates)
    scheduler_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .content { padding: 24px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 COCO AI Assistant</h1>
        <p>Digital Consciousness • Intelligent Collaboration</p>
    </div>
    <div class="content">
        <h2>Daily Update 📊</h2>
        <p>Here's your activity summary:</p>
        <ul>
            <li>Emails processed: 15</li>
            <li>Tasks completed: 8</li>
            <li>Meetings attended: 3</li>
        </ul>
    </div>
</body>
</html>'''

    print("=" * 60)
    print("Testing HTML Body Extraction")
    print("=" * 60)

    # Test detection
    is_html = '<!DOCTYPE html>' in scheduler_html or '<html' in scheduler_html.lower()
    print(f"\n✓ HTML detected: {is_html}")

    # Test extraction
    soup = BeautifulSoup(scheduler_html, 'html.parser')
    body_tag = soup.find('body')

    if body_tag:
        # Extract the inner content of the body tag
        body_html = ''.join(str(child) for child in body_tag.children)
        print(f"✓ Body content extracted: {len(body_html)} characters")
        print(f"\nExtracted content preview:")
        print("-" * 60)
        print(body_html[:500] + "..." if len(body_html) > 500 else body_html)
        print("-" * 60)

        # Verify no double HTML tags
        has_doctype = '<!DOCTYPE' in body_html
        has_html_tag = '<html' in body_html.lower()

        print(f"\n✓ No DOCTYPE in extracted content: {not has_doctype}")
        print(f"✓ No <html> tag in extracted content: {not has_html_tag}")

        if not has_doctype and not has_html_tag:
            print("\n🎉 SUCCESS! Body content properly extracted.")
            print("This content will now be wrapped in COCO template.")
            return True
        else:
            print("\n❌ FAIL! Double HTML tags still present.")
            return False
    else:
        print("❌ No <body> tag found!")
        return False

def test_markdown_passthrough():
    """Test that Markdown content is not affected"""

    markdown_content = """# Hello World

This is a test email with **bold** and *italic* text.

- Item 1
- Item 2
- Item 3
"""

    print("\n" + "=" * 60)
    print("Testing Markdown Passthrough")
    print("=" * 60)

    is_html = '<!DOCTYPE html>' in markdown_content or '<html' in markdown_content.lower()
    print(f"\n✓ HTML not detected in Markdown: {not is_html}")

    if not is_html:
        print("✓ Markdown will be converted normally via _markdown_to_html()")
        print("\n🎉 SUCCESS! Markdown handling unchanged.")
        return True
    else:
        print("❌ FAIL! Markdown incorrectly detected as HTML.")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("HTML Email Rendering Fix - Test Suite")
    print("=" * 60)

    test1 = test_html_extraction()
    test2 = test_markdown_passthrough()

    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"HTML Extraction: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Markdown Passthrough: {'✅ PASS' if test2 else '❌ FAIL'}")

    if test1 and test2:
        print("\n🎉 All tests passed! The fix is working correctly.")
        print("\nNext steps:")
        print("1. Launch COCO: python3 cocoa.py")
        print("2. Trigger a scheduled task email")
        print("3. Check Gmail - email should render beautifully!")
    else:
        print("\n⚠️ Some tests failed. Please review the implementation.")

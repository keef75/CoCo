#!/usr/bin/env python3
"""
Test COCO's Auto-Open File Capability
Tests the new universal file opening system for screenshots, images, HTML files, etc.
"""

print("🧪 Testing COCO's Auto-Open File Capability...")

# Create a simple HTML test file
html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>🚀 COCO Auto-Open Test</title>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-family: 'Arial', sans-serif;
            text-align: center;
            padding: 50px;
            margin: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .title {
            font-size: 3em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .message {
            font-size: 1.5em;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        .success {
            background: rgba(76, 175, 80, 0.3);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #4CAF50;
            margin: 20px;
        }
    </style>
</head>
<body>
    <div class="title">🎉 SUCCESS!</div>
    <div class="message">COCO's Auto-Open Capability is Working!</div>
    <div class="success">
        <h2>✅ File Opening Test Passed</h2>
        <p>COCO successfully opened this HTML file in your default browser.</p>
        <p>This demonstrates COCO's new ability to automatically open files for immediate user interaction.</p>
    </div>

    <div style="margin-top: 30px; opacity: 0.7;">
        <p>🔧 <strong>Technical Test:</strong> Universal file opener working correctly</p>
        <p>📱 <strong>Platform:</strong> Cross-platform file opening capability</p>
        <p>🎯 <strong>Result:</strong> Files now open automatically for user interaction</p>
    </div>
</body>
</html>'''

# Write the HTML test file to workspace
import os
workspace_dir = "coco_workspace"
if not os.path.exists(workspace_dir):
    os.makedirs(workspace_dir)

test_file_path = os.path.join(workspace_dir, "auto_open_test.html")
with open(test_file_path, 'w') as f:
    f.write(html_content)

print("✅ Created auto_open_test.html")
print("🌐 This is a test HTML file to verify COCO's new auto-open capability")
print("🚀 COCO should now be able to automatically open this file for you!")
print("💡 Try asking COCO: 'open the auto_open_test.html file'")
print(f"📁 File location: {test_file_path}")

# Test the function directly if we can import it
try:
    import sys
    sys.path.append('.')
    from cocoa import ToolSystem, Config

    print("\n🧪 Testing COCO's file opening function directly...")

    # Test the auto-open capability
    config = Config()
    tools = ToolSystem(config)

    # Simulate the auto-open function call
    if hasattr(tools, '_auto_open_file_for_user'):
        result = tools._auto_open_file_for_user(test_file_path, "web")
        print("✅ Auto-open test result:", result)
    else:
        print("ℹ️ Auto-open function not directly accessible - will work through COCO's main interface")

except ImportError:
    print("ℹ️ COCO not currently importable - test file created for manual testing")

print("\n🎯 READY FOR TESTING!")
print("Ask COCO to open files and they should launch automatically in the appropriate application.")
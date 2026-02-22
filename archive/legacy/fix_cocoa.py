#!/usr/bin/env python3
"""
COCOA INDENTATION BUG PATCHER
==============================
This script will find and fix ALL indentation issues in cocoa.py
Run this to permanently fix the code execution problems!
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

def patch_cocoa_indentation(cocoa_file_path="cocoa.py"):
    """
    Patches all indentation issues in cocoa.py
    """
    print("🔧 COCOA INDENTATION PATCHER")
    print("=" * 60)
    
    # Check if file exists
    cocoa_path = Path(cocoa_file_path)
    if not cocoa_path.exists():
        print(f"❌ Error: {cocoa_file_path} not found!")
        print("Please run this script in the same directory as cocoa.py")
        return False
    
    # Create backup
    backup_path = cocoa_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
    shutil.copy(cocoa_path, backup_path)
    print(f"✅ Created backup: {backup_path}")
    
    # Read the file
    with open(cocoa_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_applied = []
    
    # Fix 1: Main _execute_python method
    print("\n🔍 Searching for _execute_python indentation issues...")
    
    # Pattern for the broken enhanced_code in _execute_python
    pattern1 = r"enhanced_code = dedent\(f'''"
    
    if re.search(pattern1, content):
        print("  ❌ Found broken indentation in _execute_python")
        
        # Find the problematic block and replace it
        old_pattern = r"enhanced_code = dedent\(f'''.*?'''\)\.strip\(\)"
        
        replacement = '''enhanced_code = f"""
import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime

# Set up workspace path
workspace = Path(r"{self.workspace}")
os.chdir(str(workspace))

# Your code starts here:
{code}
""".strip()'''
        
        content = re.sub(old_pattern, replacement, content, flags=re.DOTALL)
        fixes_applied.append("_execute_python enhanced_code")
    
    # Fix 2: _execute_animated_python method
    print("\n🔍 Searching for _execute_animated_python indentation issues...")
    
    # Look for the modified_code pattern
    if "modified_code = f'''" in content:
        print("  ❌ Found broken indentation in _execute_animated_python")
        
        # Find and replace the modified_code block
        start_pattern = r"modified_code = f'''"
        end_pattern = r"'''"
        
        # Find the start
        start_match = re.search(start_pattern, content)
        if start_match:
            start_pos = start_match.start()
            # Find the matching end
            rest_content = content[start_pos:]
            lines = rest_content.split('\n')
            
            # Build replacement
            new_modified_code = '''modified_code = f"""
import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime
import math
import random

# Set up workspace path
workspace = Path(r"{self.workspace}")
os.chdir(str(workspace))

# Capture output instead of clearing screen
captured_frames = []
original_print = print

def capture_print(*args, **kwargs):
    # Capture to string instead of stdout
    output = io.StringIO()
    original_print(*args, file=output, **kwargs)
    return output.getvalue()

# Import io for string capture
import io

# Override os.system to prevent screen clearing
def no_clear(command):
    if command in ['clear', 'cls']:
        return  # Do nothing
    return os.system(command)

os.system = no_clear

# Modified code with frame capture
{code}
"""'''
            
            # Find end of the block by looking for the closing '''
            block_lines = []
            in_block = False
            end_found = False
            
            for i, line in enumerate(lines):
                if i == 0:  # First line with f'''
                    in_block = True
                    continue
                
                if in_block and line.strip().endswith("'''"):
                    end_found = True
                    break
                
                if in_block:
                    block_lines.append(line)
            
            if end_found:
                # Replace the entire block
                old_block_end = start_pos + len('\n'.join(lines[:i+1]))
                content = content[:start_pos] + new_modified_code + content[old_block_end:]
                fixes_applied.append("_execute_animated_python modified_code")
    
    # Fix 3: Add dedent import if not present and remove if causing issues
    print("\n📦 Checking dedent import...")
    
    if "from textwrap import dedent" in content:
        print("  ✅ dedent import already present")
    else:
        # Add the import at the top with other imports
        import_pos = content.find("import subprocess")
        if import_pos > 0:
            line_start = content.rfind('\n', 0, import_pos) + 1
            content = content[:line_start] + "from textwrap import dedent\n" + content[line_start:]
            fixes_applied.append("Added dedent import")
    
    # Fix 4: Create a simple fallback executor
    print("\n🎯 Adding simple fallback executor...")
    
    simple_executor = '''
    def run_code_simple(self, code: str) -> str:
        """Simple, reliable code execution fallback"""
        import subprocess
        import sys
        
        try:
            # Direct execution - no modifications
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.workspace) if hasattr(self, 'workspace') else None
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                return f"✅ **Execution Successful**\\n\\n```\\n{output}\\n```"
            else:
                error = result.stderr.strip()
                return f"❌ **Execution Failed**\\n\\n```\\n{error}\\n```"
                
        except subprocess.TimeoutExpired:
            return "❌ **Execution Timeout** - Code took longer than 30 seconds"
        except Exception as e:
            return f"❌ **Execution Error**\\n```\\n{str(e)}\\n```"
'''
    
    # Add simple executor if not present
    if "def run_code_simple" not in content:
        # Find a good place to insert it (after ToolSystem class definition)
        insert_pos = content.find("class ToolSystem:")
        if insert_pos > 0:
            # Find the end of the class (next class or end of file)
            next_class = content.find("\nclass ", insert_pos + 1)
            if next_class < 0:
                next_class = len(content)
            
            # Insert before the last method of ToolSystem
            last_method = content.rfind("    def ", insert_pos, next_class)
            if last_method > 0:
                content = content[:last_method] + simple_executor + "\n" + content[last_method:]
                fixes_applied.append("Added run_code_simple fallback")
    
    # Write the fixed content if changes were made
    if fixes_applied:
        with open(cocoa_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n" + "=" * 60)
        print("✅ PATCHING COMPLETE!")
        print(f"Applied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            print(f"  • {fix}")
        print(f"\n💾 Backup saved as: {backup_path}")
        print("🎉 Your code execution should work now!")
        
        return True
    else:
        print("\n⚠️ No indentation issues found to fix")
        print("The problem might be elsewhere")
        return False


def verify_fix(cocoa_file_path="cocoa.py"):
    """
    Verify that the fixes have been applied
    """
    print("\n" + "=" * 60)
    print("🔍 VERIFYING FIX...")
    print("=" * 60)
    
    with open(cocoa_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for problematic patterns
    if re.search(r"dedent\(f'''.*import sys.*\n\s+import os", content, re.DOTALL):
        issues.append("Still has indented imports in enhanced_code with dedent")
    
    if re.search(r"f'''\s*\n\s+import sys", content):
        issues.append("Still has indented imports in modified_code")
    
    # Check if simple executor exists
    if "def run_code_simple" not in content:
        issues.append("Missing run_code_simple fallback method")
    
    if issues:
        print("❌ Issues still found:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ All indentation issues appear to be fixed!")
        print("\n🧪 You can now test with:")
        print('  /run print("Hello from COCOA!")')
        print('  /run import datetime; print(datetime.datetime.now())')
        return True


def create_test_script():
    """
    Create a test script to verify execution works
    """
    test_code = '''#!/usr/bin/env python3
"""Test script for COCOA code execution"""

# Test 1: Basic print
print("✅ Test 1: Basic print works!")

# Test 2: Imports
import datetime
print(f"✅ Test 2: Import works - Time: {datetime.datetime.now()}")

# Test 3: Math
result = sum(range(10))
print(f"✅ Test 3: Math works - Sum of 0-9 = {result}")

# Test 4: Multiline
for i in range(3):
    print(f"  Line {i+1}")

print("\\n🎉 All tests passed! Code execution is working!")
'''
    
    with open("test_cocoa_execution.py", "w") as f:
        f.write(test_code)
    
    print("\n📝 Created test_cocoa_execution.py")
    print("Test it in COCOA with: /run exec(open('test_cocoa_execution.py').read())")


def main():
    """
    Main execution
    """
    print("🚀 COCOA INDENTATION BUG FIXER")
    print("=" * 60)
    print("This script will fix all indentation issues in cocoa.py\n")
    
    # Check if cocoa.py exists
    if not Path("cocoa.py").exists():
        print("❌ cocoa.py not found in current directory!")
        cocoa_path = input("Enter path to cocoa.py: ").strip()
        if not cocoa_path:
            print("Aborted.")
            return
    else:
        cocoa_path = "cocoa.py"
    
    # Apply patches
    if patch_cocoa_indentation(cocoa_path):
        # Verify the fix
        verify_fix(cocoa_path)
        
        # Create test script
        create_test_script()
        
        print("\n" + "=" * 60)
        print("🎊 FIX COMPLETE!")
        print("=" * 60)
        print("\n⚡ Quick test commands for COCOA:")
        print('  1. /run print("COCOA LIVES!")')
        print('  2. /run import sys; print(f"Python {sys.version}")')
        print('  3. /run exec(open("test_cocoa_execution.py").read())')
        print("\n🔄 If issues persist, restart COCOA after applying this fix.")
    else:
        print("\n⚠️ No fixes were needed or fix failed")
        print("Please check the error messages above")


if __name__ == "__main__":
    main()
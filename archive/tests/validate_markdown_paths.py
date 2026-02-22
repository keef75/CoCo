#!/usr/bin/env python3
"""
Markdown Memory System Path Validation Script

Validates that COCO's three-file markdown memory system is properly configured
and has no nested directory issues.

Usage:
    python3 validate_markdown_paths.py
    ./venv_cocoa/bin/python validate_markdown_paths.py
"""

from pathlib import Path
import sys

def validate_markdown_system():
    """Validate the markdown memory system paths and structure"""

    print("🔍 Validating COCO Markdown Memory System...")
    print("=" * 70)

    # Define expected workspace
    workspace = Path(__file__).parent / "coco_workspace"
    workspace = workspace.resolve()

    # Define critical files
    critical_files = {
        "COCO.md": "Consciousness state and identity",
        "USER_PROFILE.md": "User understanding and family information",
        "PREFERENCES.md": "Adaptive preferences and personalization"
    }

    issues_found = []
    warnings = []

    # Check 1: Workspace exists
    print(f"\n📂 Workspace Location:")
    print(f"   {workspace}")
    if not workspace.exists():
        issues_found.append(f"❌ Workspace directory does not exist: {workspace}")
    else:
        print(f"   ✅ Workspace exists")

    # Check 2: Critical files exist and are in root
    print(f"\n📄 Critical Files (Layer 3 Memory):")
    for filename, description in critical_files.items():
        file_path = workspace / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {filename} ({size:,} bytes) - {description}")
        else:
            issues_found.append(f"❌ Missing critical file: {filename}")
            print(f"   ❌ {filename} - MISSING")

    # Check 3: No nested workspace directories
    print(f"\n🔍 Checking for Nested Directories:")
    nested_workspace = workspace / "coco_workspace"
    nested_workspace_alt = workspace / "workspace"

    if nested_workspace.exists():
        warnings.append(f"⚠️  Nested 'coco_workspace' directory found: {nested_workspace}")
        print(f"   ⚠️  Found: {nested_workspace}")
    else:
        print(f"   ✅ No nested 'coco_workspace' directory")

    if nested_workspace_alt.exists():
        warnings.append(f"⚠️  Nested 'workspace' directory found: {nested_workspace_alt}")
        print(f"   ⚠️  Found: {nested_workspace_alt}")
    else:
        print(f"   ✅ No nested 'workspace' directory")

    # Check 4: Look for duplicate critical files in subdirectories
    print(f"\n🔍 Checking for Duplicate Critical Files:")
    for filename in critical_files.keys():
        duplicates = list(workspace.rglob(filename))
        if len(duplicates) > 1:
            warnings.append(f"⚠️  Multiple copies of {filename} found:")
            print(f"   ⚠️  Multiple copies of {filename}:")
            for dup in duplicates:
                print(f"      - {dup}")
                warnings.append(f"      - {dup}")
        elif len(duplicates) == 1:
            print(f"   ✅ {filename} - single copy only")
        else:
            issues_found.append(f"❌ {filename} not found anywhere in workspace")
            print(f"   ❌ {filename} - not found")

    # Check 5: Count total markdown files
    print(f"\n📊 Markdown File Statistics:")
    all_md_files = list(workspace.rglob("*.md"))
    critical_count = len([f for f in all_md_files if f.name in critical_files.keys()])
    other_count = len(all_md_files) - critical_count

    print(f"   Total markdown files: {len(all_md_files)}")
    print(f"   Critical files (Layer 3): {critical_count}/3")
    print(f"   Other markdown files: {other_count}")

    # Summary
    print("\n" + "=" * 70)
    print("📋 VALIDATION SUMMARY:")
    print("=" * 70)

    if issues_found:
        print(f"\n❌ ISSUES FOUND ({len(issues_found)}):")
        for issue in issues_found:
            print(f"   {issue}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   {warning}")

    if not issues_found and not warnings:
        print("\n✅ ALL CHECKS PASSED!")
        print("   Markdown memory system is properly configured.")
        return 0
    elif not issues_found:
        print("\n⚠️  VALIDATION PASSED WITH WARNINGS")
        print("   System will function but may have redundancy.")
        return 1
    else:
        print("\n❌ VALIDATION FAILED")
        print("   Critical issues must be resolved.")
        return 2

if __name__ == "__main__":
    exit_code = validate_markdown_system()
    sys.exit(exit_code)

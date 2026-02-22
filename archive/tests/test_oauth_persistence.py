#!/usr/bin/env python3
"""
OAuth Persistence Test Suite
=============================
Tests automatic token refresh and persistence functionality.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def test_token_json_exists():
    """Test 1: Check if token.json exists"""
    print("\n" + "=" * 60)
    print("Test 1: Token File Existence")
    print("=" * 60)

    token_file = Path("token.json")
    if token_file.exists():
        print(f"✅ token.json found at: {token_file.absolute()}")
        return True
    else:
        print("❌ token.json not found")
        print("\n💡 Run one of these to generate tokens:")
        print("   python3 get_token_persistent.py  (recommended)")
        print("   python3 migrate_to_token_json.py  (if you have .env tokens)")
        return False

def test_token_json_valid():
    """Test 2: Check if token.json is valid JSON"""
    print("\n" + "=" * 60)
    print("Test 2: Token File Validity")
    print("=" * 60)

    try:
        token_file = Path("token.json")
        token_data = json.loads(token_file.read_text())

        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
        missing = [field for field in required_fields if field not in token_data]

        if missing:
            print(f"❌ Missing required fields: {', '.join(missing)}")
            return False

        print("✅ token.json is valid JSON")
        print(f"   Client ID: {token_data['client_id'][:30]}...")
        print(f"   Access Token: {token_data['token'][:30]}...")
        print(f"   Refresh Token: {token_data['refresh_token'][:30]}...")
        print(f"   Scopes: {len(token_data['scopes'])} permissions")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading token.json: {e}")
        return False

def test_credentials_loading():
    """Test 3: Load credentials from token.json"""
    print("\n" + "=" * 60)
    print("Test 3: Credentials Loading")
    print("=" * 60)

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

        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        print("✅ Credentials loaded successfully")
        print(f"   Token valid: {creds.valid}")
        print(f"   Token expired: {creds.expired}")
        print(f"   Has refresh token: {bool(creds.refresh_token)}")

        if hasattr(creds, 'expiry') and creds.expiry:
            now = datetime.utcnow()
            if creds.expiry > now:
                time_left = creds.expiry - now
                print(f"   Time until expiry: {time_left}")
            else:
                print(f"   Token expired {now - creds.expiry} ago")

        return creds

    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        return None

def test_token_refresh(creds):
    """Test 4: Simulate token refresh"""
    print("\n" + "=" * 60)
    print("Test 4: Token Refresh Simulation")
    print("=" * 60)

    if not creds:
        print("⏭️  Skipped (no credentials loaded)")
        return False

    try:
        # Check if token is expired or will expire soon
        if creds.valid and not creds.expired:
            print("ℹ️  Token is currently valid")
            print("   To test refresh, we'll force a refresh anyway...")

        if not creds.refresh_token:
            print("❌ No refresh token available")
            return False

        # Force refresh
        print("🔄 Attempting token refresh...")
        old_token = creds.token[:30]

        creds.refresh(Request())

        new_token = creds.token[:30]

        if old_token != new_token:
            print("✅ Token refreshed successfully!")
            print(f"   Old token: {old_token}...")
            print(f"   New token: {new_token}...")
        else:
            print("⚠️  Token refresh called, but token unchanged (may still be valid)")

        # Save refreshed token
        token_file = Path("token.json")
        token_file.write_text(creds.to_json())
        print("💾 Refreshed token saved to token.json")

        return True

    except Exception as e:
        print(f"❌ Token refresh failed: {e}")
        print("\n💡 This might mean:")
        print("   • Refresh token has expired (7 days in Testing mode)")
        print("   • OAuth app needs to be in Production mode")
        print("   • Network connectivity issues")
        return False

def test_google_workspace_integration():
    """Test 5: Integration with GoogleWorkspaceConsciousness"""
    print("\n" + "=" * 60)
    print("Test 5: COCO Integration Test")
    print("=" * 60)

    try:
        from google_workspace_consciousness import GoogleWorkspaceConsciousness

        # Initialize with token.json (should auto-load)
        workspace = GoogleWorkspaceConsciousness()

        if workspace.authenticated:
            print("✅ GoogleWorkspaceConsciousness authenticated via token.json")
            print(f"   Docs service: {'Active' if workspace.docs_service else 'Inactive'}")
            print(f"   Sheets service: {'Active' if workspace.sheets_service else 'Inactive'}")
            print(f"   Drive service: {'Active' if workspace.drive_service else 'Inactive'}")
            return True
        else:
            print("❌ GoogleWorkspaceConsciousness not authenticated")
            print(f"   Simplified mode: {workspace.simplified_mode}")
            return False

    except ImportError as e:
        print(f"⏭️  Skipped: {e}")
        return None
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 70)
    print("COCO OAuth Persistence Test Suite")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0
    }

    # Test 1: File exists
    results['total'] += 1
    if test_token_json_exists():
        results['passed'] += 1
    else:
        results['failed'] += 1
        print("\n⚠️  Cannot proceed without token.json")
        print_summary(results)
        return

    # Test 2: Valid JSON
    results['total'] += 1
    if test_token_json_valid():
        results['passed'] += 1
    else:
        results['failed'] += 1
        print("\n⚠️  Cannot proceed with invalid token.json")
        print_summary(results)
        return

    # Test 3: Load credentials
    results['total'] += 1
    creds = test_credentials_loading()
    if creds:
        results['passed'] += 1
    else:
        results['failed'] += 1

    # Test 4: Refresh token
    results['total'] += 1
    if test_token_refresh(creds):
        results['passed'] += 1
    else:
        results['failed'] += 1

    # Test 5: COCO integration
    results['total'] += 1
    integration_result = test_google_workspace_integration()
    if integration_result is True:
        results['passed'] += 1
    elif integration_result is None:
        results['skipped'] += 1
    else:
        results['failed'] += 1

    print_summary(results)

def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Total tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    if results['skipped'] > 0:
        print(f"⏭️  Skipped: {results['skipped']}")

    if results['failed'] == 0 and results['passed'] > 0:
        print("\n🎉 All tests passed! OAuth persistence is working correctly.")
    elif results['failed'] > 0:
        print("\n⚠️  Some tests failed. See details above.")

    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()

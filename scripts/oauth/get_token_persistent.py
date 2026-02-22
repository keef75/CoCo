#!/usr/bin/env python3
"""
OAuth Token Generator with Persistent Storage
==============================================
Generates OAuth tokens and saves directly to token.json for automatic refresh.
This is the new recommended approach - no need to copy tokens to .env!
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

# Full Google Workspace scopes
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

def main():
    """Generate OAuth tokens and save to token.json"""

    print("=" * 70)
    print("COCO OAuth Token Generator - Persistent Storage Edition")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Open your browser for Google OAuth consent")
    print("  2. Generate access and refresh tokens")
    print("  3. Save tokens to token.json for automatic refresh")
    print()
    print("🔐 You only need to do this ONCE!")
    print()

    # Check for credentials.json
    if not Path('credentials.json').exists():
        print("❌ credentials.json not found!")
        print()
        print("Please download it from Google Cloud Console:")
        print("   1. Go to: https://console.cloud.google.com/apis/credentials")
        print("   2. Create OAuth 2.0 Client ID (Desktop application)")
        print("   3. Download as credentials.json")
        print("   4. Place in project root directory")
        return

    try:
        # Run OAuth flow
        print("🌐 Opening browser for authentication...")
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',
            scopes=SCOPES
        )
        creds = flow.run_local_server(port=8080)

        # Save to token.json
        token_file = Path('token.json')
        token_file.write_text(creds.to_json())

        print()
        print("=" * 70)
        print("✅ SUCCESS! Tokens Generated and Saved")
        print("=" * 70)
        print()
        print(f"📄 Saved to: {token_file.absolute()}")
        print()
        print("🔐 Token Details:")
        print(f"   Access Token: {creds.token[:50]}...")
        print(f"   Refresh Token: {creds.refresh_token[:50]}...")
        print(f"   Scopes: {len(SCOPES)} permissions granted")
        print()
        print("✨ COCO will now automatically:")
        print("   • Load credentials from token.json")
        print("   • Refresh access tokens when they expire")
        print("   • Save updated tokens back to token.json")
        print()
        print("🚀 You're all set! Just run: python3 cocoa.py")
        print()
        print("=" * 70)

    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("  • Check credentials.json is valid")
        print("  • Ensure redirect URI is http://localhost:8080")
        print("  • Try a different port if 8080 is in use")

if __name__ == "__main__":
    main()

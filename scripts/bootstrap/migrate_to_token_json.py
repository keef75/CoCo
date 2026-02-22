#!/usr/bin/env python3
"""
Migration Script: .env Tokens → token.json
==========================================
Converts existing .env OAuth tokens to persistent token.json format.
This enables automatic token refresh without manual intervention.
"""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

def migrate_tokens():
    """Migrate OAuth tokens from .env to token.json"""

    # Load environment variables
    load_dotenv()

    client_id = os.getenv('GMAIL_CLIENT_ID')
    client_secret = os.getenv('GMAIL_CLIENT_SECRET')
    access_token = os.getenv('GMAIL_ACCESS_TOKEN')
    refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')

    # Validate all tokens are present
    missing = []
    if not client_id:
        missing.append('GMAIL_CLIENT_ID')
    if not client_secret:
        missing.append('GMAIL_CLIENT_SECRET')
    if not access_token:
        missing.append('GMAIL_ACCESS_TOKEN')
    if not refresh_token:
        missing.append('GMAIL_REFRESH_TOKEN')

    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("\n💡 Run get_token.py first to generate OAuth tokens")
        return False

    # Define scopes
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

    # Create credentials object
    try:
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES
        )

        # Save to token.json
        token_file = Path("token.json")
        token_file.write_text(creds.to_json())

        print("✅ Migration successful!")
        print(f"\n📄 Credentials saved to: {token_file.absolute()}")
        print("\n🔐 Token Details:")
        print(f"   Client ID: {client_id[:30]}...")
        print(f"   Access Token: {access_token[:30]}...")
        print(f"   Refresh Token: {refresh_token[:30]}...")
        print(f"   Scopes: {len(SCOPES)} permissions")

        print("\n✨ COCO will now automatically refresh tokens from token.json")
        print("   No more manual token regeneration needed!")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("OAuth Token Migration: .env → token.json")
    print("=" * 60)
    print()

    success = migrate_tokens()

    if success:
        print("\n" + "=" * 60)
        print("✅ Migration Complete - COCO Ready for Persistent OAuth")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Migration Failed - Check Environment Variables")
        print("=" * 60)

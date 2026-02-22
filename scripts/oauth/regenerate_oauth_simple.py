#!/usr/bin/env python3
"""
Simple Google Workspace OAuth Token Regeneration
Uses out-of-band (OOB) flow - no redirect URI configuration needed.
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv, set_key

# Load existing environment
load_dotenv()

# OAuth scopes needed for Google Workspace
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
    print("\n" + "="*70)
    print("COCO Google Workspace OAuth Token Regeneration")
    print("="*70 + "\n")

    # Get credentials from environment
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("❌ Error: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")
        return

    # Create OAuth flow with OOB redirect
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
        }
    }

    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    # Get authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')

    print("📋 Step 1: Open this URL in your browser:\n")
    print(f"    {auth_url}\n")
    print("📋 Step 2: After authorizing, you'll see an authorization code.")
    print("           Copy that code and paste it here.\n")

    # Get authorization code from user
    code = input("Enter authorization code: ").strip()

    if not code:
        print("❌ No code provided. Exiting.")
        return

    print("\n🔄 Exchanging authorization code for tokens...")

    try:
        # Exchange code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Update .env file
        env_file = '.env'
        set_key(env_file, 'GOOGLE_ACCESS_TOKEN', credentials.token)
        set_key(env_file, 'GOOGLE_REFRESH_TOKEN', credentials.refresh_token)

        print("\n✅ Success! New tokens saved to .env file")
        print("\n📋 Token Details:")
        print(f"   Access Token:  {credentials.token[:50]}...")
        print(f"   Refresh Token: {credentials.refresh_token[:50]}...")
        print("\n🎯 You can now restart COCO and use Google Workspace features!")

    except Exception as e:
        print(f"\n❌ Error getting tokens: {e}")
        return

if __name__ == "__main__":
    main()

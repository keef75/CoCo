#!/usr/bin/env python3
"""
Google OAuth Setup Helper for COCO
This script helps generate valid OAuth tokens for Google Workspace integration
"""

import os
import sys
import json
import webbrowser
from pathlib import Path

# Try to import Google libraries
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    print("❌ Google auth libraries not installed.")
    print("Please run: pip install google-auth google-auth-oauthlib google-auth-httplib2")
    sys.exit(1)

# Define the scopes needed for Google Workspace
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'
]

def load_env_credentials():
    """Load OAuth credentials from .env file."""
    env_path = Path(__file__).parent / '.env'
    credentials = {}

    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key in ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET']:
                            credentials[key] = value

    return credentials

def create_oauth_flow():
    """Create OAuth flow from environment credentials."""
    creds = load_env_credentials()

    if not creds.get('GMAIL_CLIENT_ID') or not creds.get('GMAIL_CLIENT_SECRET'):
        print("❌ Missing OAuth credentials in .env file")
        print("Please ensure GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET are set")
        return None

    # Create OAuth config
    client_config = {
        "installed": {
            "client_id": creds['GMAIL_CLIENT_ID'],
            "client_secret": creds['GMAIL_CLIENT_SECRET'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }

    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=SCOPES
    )

    return flow

def generate_tokens():
    """Generate OAuth tokens interactively."""
    print("=" * 60)
    print("🔐 Google OAuth Token Generation for COCO")
    print("=" * 60)
    print()

    flow = create_oauth_flow()
    if not flow:
        return None

    print("📌 This will open your browser to authenticate with Google.")
    print("📌 Please authorize COCO to access your Google Workspace.")
    print()

    try:
        # Try to use local server first
        try:
            creds = flow.run_local_server(
                port=0,
                authorization_prompt_message='Please visit this URL to authorize COCO: {url}',
                success_message='Authorization successful! You can close this window.',
                open_browser=True
            )
        except:
            # Fall back to console flow
            print("⚠️  Could not start local server. Using console flow instead.")
            print()

            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )

            print("Please visit this URL to authorize COCO:")
            print()
            print(auth_url)
            print()

            # Try to open browser automatically
            try:
                webbrowser.open(auth_url)
                print("✅ Browser opened automatically")
            except:
                print("⚠️  Could not open browser automatically")

            print()
            auth_code = input("Enter the authorization code: ").strip()

            flow.fetch_token(code=auth_code)
            creds = flow.credentials

        print()
        print("✅ Authentication successful!")
        print()

        # Display the tokens
        print("=" * 60)
        print("📝 Your OAuth Tokens:")
        print("=" * 60)
        print()
        print(f"Access Token: {creds.token[:50]}...")
        print(f"Refresh Token: {creds.refresh_token}")
        print()

        # Save tokens to a file
        token_file = Path(__file__).parent / 'google_tokens.json'
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }

        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)

        print(f"✅ Tokens saved to: {token_file}")
        print()

        # Show how to update .env
        print("=" * 60)
        print("📋 Update your .env file with these values:")
        print("=" * 60)
        print()
        print(f"GMAIL_ACCESS_TOKEN={creds.token}")
        print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
        print()
        print("⚠️  Important: Replace the placeholder values in your .env file")
        print("    with the tokens shown above.")
        print()

        return creds

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

def test_tokens(creds):
    """Test if the tokens work by creating a simple document."""
    try:
        from googleapiclient.discovery import build

        print("=" * 60)
        print("🧪 Testing Google Docs API...")
        print("=" * 60)
        print()

        # Build the Docs service
        service = build('docs', 'v1', credentials=creds)

        # Create a test document
        document = service.documents().create(
            body={'title': 'COCO Test Document'}
        ).execute()

        doc_id = document.get('documentId')
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        print("✅ Success! Created test document:")
        print(f"   Title: COCO Test Document")
        print(f"   URL: {doc_url}")
        print()

        # Add some content
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': 'Hello from COCO! OAuth authentication is working correctly.\n\nThis is a test document created to verify Google Workspace integration.'
            }
        }]

        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print("✅ Added content to the document")
        print()
        print("🎉 Google Workspace authentication is working!")
        print()

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function to run the OAuth setup."""
    print()
    print("🤖 COCO Google Workspace OAuth Setup")
    print("=" * 60)
    print()

    # Check if tokens already exist
    token_file = Path(__file__).parent / 'google_tokens.json'
    if token_file.exists():
        print("📌 Found existing tokens file.")
        response = input("Do you want to generate new tokens? (y/n): ").lower()
        if response != 'y':
            print("Keeping existing tokens.")

            # Load and test existing tokens
            with open(token_file, 'r') as f:
                token_data = json.load(f)

            creds = Credentials(
                token=token_data['token'],
                refresh_token=token_data['refresh_token'],
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes']
            )

            test_tokens(creds)
            return

    # Generate new tokens
    creds = generate_tokens()

    if creds:
        # Test the tokens
        print("Would you like to test the tokens? (y/n): ", end='')
        if input().lower() == 'y':
            test_tokens(creds)

        print("=" * 60)
        print("✅ Setup complete!")
        print()
        print("Next steps:")
        print("1. Copy the tokens shown above")
        print("2. Update your .env file with the real tokens")
        print("3. Restart COCO")
        print("4. Try creating a Google Doc!")
        print("=" * 60)

if __name__ == "__main__":
    main()
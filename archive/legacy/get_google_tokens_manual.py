#!/usr/bin/env python3
"""
Manual OAuth token generator for COCO Google Workspace
This generates the authorization URL and processes the code manually
"""

import json
from pathlib import Path

print("=" * 70)
print("🔐 Google OAuth Manual Setup for COCO")
print("=" * 70)
print()

# Load credentials
creds_file = Path("client_secret_2_927120946268-t11ojlc0lug24p90uj1e8d08qf3deajp.apps.googleusercontent.com.json")
if not creds_file.exists():
    print(f"❌ Credentials file not found: {creds_file}")
    exit(1)

with open(creds_file, 'r') as f:
    creds_data = json.load(f)

client_id = creds_data['web']['client_id']
client_secret = creds_data['web']['client_secret']

print(f"✅ Using credentials from: {creds_file}")
print(f"📋 Client ID: ...{client_id[-20:]}")
print()

# Build authorization URL with all needed scopes
from urllib.parse import urlencode

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

params = {
    'client_id': client_id,
    'redirect_uri': 'http://localhost:8080',  # Using the allowed redirect URI
    'scope': ' '.join(SCOPES),
    'response_type': 'code',
    'access_type': 'offline',
    'prompt': 'consent'
}

auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

print("📋 Step 1: Click this link to authorize COCO")
print("-" * 70)
print(auth_url)
print("-" * 70)
print()
print("📌 After authorizing, you'll be redirected to a localhost URL.")
print("   The page might not load, but copy the ENTIRE URL from your browser.")
print()
print("📋 Step 2: Paste the FULL redirect URL here")
print("   Example: http://localhost:8080/?code=4/0AQlEd...&scope=...")
print()

redirect_url = input("Paste redirect URL: ").strip()

# Extract the authorization code
try:
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(redirect_url)
    code = parse_qs(parsed.query)['code'][0]
    print(f"✅ Got authorization code: {code[:20]}...")
except Exception as e:
    print(f"❌ Could not extract code from URL: {e}")
    print("   Make sure you copied the ENTIRE URL including the ?code= part")
    exit(1)

print()
print("📋 Step 3: Exchanging code for tokens...")
print()

import requests

token_url = "https://oauth2.googleapis.com/token"
token_data = {
    'code': code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': 'http://localhost:8080',
    'grant_type': 'authorization_code'
}

try:
    response = requests.post(token_url, data=token_data)
    tokens = response.json()

    if 'access_token' in tokens:
        print("✅ SUCCESS! Here are your tokens:")
        print()
        print("=" * 70)
        print("📝 Add these to your .env file:")
        print("=" * 70)
        print()
        print(f"GMAIL_ACCESS_TOKEN={tokens['access_token']}")
        print()
        print(f"GMAIL_REFRESH_TOKEN={tokens.get('refresh_token', 'Not provided')}")
        print()
        print("=" * 70)
        print()

        # Offer to update .env automatically
        response = input("📝 Would you like to automatically update your .env file? (y/n): ")
        if response.lower() == 'y':
            env_path = Path(".env")
            with open(env_path, 'r') as f:
                lines = f.readlines()

            updated = False
            for i, line in enumerate(lines):
                if line.startswith('GMAIL_ACCESS_TOKEN='):
                    lines[i] = f"GMAIL_ACCESS_TOKEN={tokens['access_token']}\n"
                    updated = True
                elif line.startswith('GMAIL_REFRESH_TOKEN='):
                    lines[i] = f"GMAIL_REFRESH_TOKEN={tokens.get('refresh_token', 'Not provided')}\n"
                    updated = True

            if updated:
                with open(env_path, 'w') as f:
                    f.writelines(lines)
                print("✅ .env file updated successfully!")
            else:
                print("⚠️ Could not find token lines in .env file")
                print("   Please update manually with the values above")

        print()
        print("🎉 Next steps:")
        print("1. Restart COCO")
        print("2. Try creating a Google Doc!")
        print("   Example: 'Create a Google doc with Hello World content'")

    else:
        print("❌ Error getting tokens:")
        print(json.dumps(tokens, indent=2))
        print()
        print("Common issues:")
        print("- Authorization code expired (try the whole process again)")
        print("- Wrong redirect URI (must be http://localhost:8080)")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Make sure you have 'requests' installed:")
    print("./venv_cocoa/bin/pip install requests")

print()
print("=" * 70)
#!/usr/bin/env python3
"""
Step 2: Exchange authorization code for tokens
"""

import sys
import json
import requests
from pathlib import Path

print("=" * 70)
print("🔐 COCO Google OAuth - Step 2: Get Tokens")
print("=" * 70)
print()

# Get the authorization code
if len(sys.argv) > 1:
    # Code passed as argument
    code = sys.argv[1]
    print(f"✅ Using code from command line: {code[:20]}...")
else:
    print("📋 Paste your authorization code or the full redirect URL:")
    print("   Example code: 4/0AQlEd8xJ...")
    print("   Example URL: http://localhost:8080/?code=4/0AQlEd8xJ...&scope=...")
    print()

    user_input = input("Enter code or URL: ").strip()

    # Check if it's a URL or just the code
    if user_input.startswith('http'):
        # Extract code from URL
        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(user_input)
            code = parse_qs(parsed.query)['code'][0]
            print(f"✅ Extracted code: {code[:20]}...")
        except Exception as e:
            print(f"❌ Could not extract code from URL: {e}")
            exit(1)
    else:
        code = user_input
        print(f"✅ Using code: {code[:20]}...")

print()
print("📋 Exchanging code for tokens...")
print()

# Load credentials
creds_file = Path("client_secret_2_927120946268-t11ojlc0lug24p90uj1e8d08qf3deajp.apps.googleusercontent.com.json")
with open(creds_file, 'r') as f:
    creds_data = json.load(f)

client_id = creds_data['web']['client_id']
client_secret = creds_data['web']['client_secret']

# Exchange code for tokens
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
        print("✅ SUCCESS! Got your tokens!")
        print()
        print("=" * 70)
        print("📝 YOUR TOKENS:")
        print("=" * 70)
        print()

        access_token = tokens['access_token']
        refresh_token = tokens.get('refresh_token', 'Not provided')

        print(f"GMAIL_ACCESS_TOKEN={access_token}")
        print()
        print(f"GMAIL_REFRESH_TOKEN={refresh_token}")
        print()
        print("=" * 70)
        print()

        # Update .env file
        print("📝 Updating your .env file...")

        env_path = Path(".env")
        with open(env_path, 'r') as f:
            lines = f.readlines()

        updated_access = False
        updated_refresh = False

        for i, line in enumerate(lines):
            if line.startswith('GMAIL_ACCESS_TOKEN='):
                lines[i] = f"GMAIL_ACCESS_TOKEN={access_token}\n"
                updated_access = True
            elif line.startswith('GMAIL_REFRESH_TOKEN='):
                lines[i] = f"GMAIL_REFRESH_TOKEN={refresh_token}\n"
                updated_refresh = True

        if updated_access and updated_refresh:
            with open(env_path, 'w') as f:
                f.writelines(lines)
            print("✅ .env file updated successfully!")
            print()
            print("🎉 Google Workspace is now configured!")
            print()
            print("Next steps:")
            print("1. Restart COCO")
            print("2. Try: 'Create a Google doc with Hello World content'")
        else:
            print("⚠️ Could not update .env file automatically")
            print("   Please manually add the tokens shown above to your .env file")

    else:
        print("❌ Error getting tokens:")
        print(json.dumps(tokens, indent=2))
        print()

        if tokens.get('error') == 'invalid_grant':
            print("⚠️ The authorization code has expired or was already used.")
            print("   Please run step1_get_auth_url.py again to get a new code.")
        else:
            print("Common issues:")
            print("- Authorization code expired (codes are only valid for a few minutes)")
            print("- Code already used (each code can only be used once)")
            print("- Wrong redirect URI (must match exactly)")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Make sure you have 'requests' installed:")
    print("./venv_cocoa/bin/pip install requests")

print()
print("=" * 70)
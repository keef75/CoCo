#!/usr/bin/env python3
"""
Manual Google OAuth Token Generator
Step-by-step process with full control
"""

import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv, set_key

# Load .env
load_dotenv()

client_id = os.getenv('GMAIL_CLIENT_ID')
client_secret = os.getenv('GMAIL_CLIENT_SECRET')

if not client_id or not client_secret:
    print("❌ Missing GMAIL_CLIENT_ID or GMAIL_CLIENT_SECRET in .env")
    exit(1)

# OAuth scopes
scopes = [
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

print("\n" + "="*70)
print("MANUAL GOOGLE OAUTH TOKEN GENERATOR")
print("="*70 + "\n")

# Step 1: Generate authorization URL
auth_params = {
    'client_id': client_id,
    'redirect_uri': 'http://localhost:8090',
    'response_type': 'code',
    'scope': ' '.join(scopes),
    'access_type': 'offline',
    'prompt': 'consent'
}

auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"

print("STEP 1: Copy this URL and open it in your browser:\n")
print(auth_url)
print("\n" + "="*70 + "\n")

print("STEP 2: After authorizing, you'll be redirected to a URL like:")
print("        http://localhost:8090/?code=4/0A...")
print("\n        Copy the ENTIRE URL and paste it here.\n")

redirect_url = input("Paste the redirect URL: ").strip()

if not redirect_url or 'code=' not in redirect_url:
    print("❌ Invalid URL - must contain 'code=' parameter")
    exit(1)

# Extract code from URL
code = redirect_url.split('code=')[1].split('&')[0]

print(f"\n✅ Extracted authorization code: {code[:20]}...")

# Step 3: Exchange code for tokens
print("\n🔄 Exchanging code for tokens...")

token_data = {
    'code': code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': 'http://localhost:8090',
    'grant_type': 'authorization_code'
}

response = requests.post('https://oauth2.googleapis.com/token', data=token_data)

if response.status_code != 200:
    print(f"❌ Token exchange failed: {response.text}")
    exit(1)

tokens = response.json()

access_token = tokens.get('access_token')
refresh_token = tokens.get('refresh_token')

if not access_token or not refresh_token:
    print(f"❌ Missing tokens in response: {tokens}")
    exit(1)

print("\n✅ Got tokens successfully!")

# Step 4: Update .env
print("\n💾 Updating .env file...")

env_file = '.env'
set_key(env_file, 'GMAIL_ACCESS_TOKEN', access_token)
set_key(env_file, 'GMAIL_REFRESH_TOKEN', refresh_token)

print("\n✅ SUCCESS! Tokens saved to .env")
print(f"\n   Access Token:  {access_token[:50]}...")
print(f"   Refresh Token: {refresh_token[:50]}...")
print("\n🎯 You can now restart COCO and use Google Workspace!")

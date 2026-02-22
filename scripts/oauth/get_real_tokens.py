#!/usr/bin/env python3
"""
Get Real Gmail Tokens Using Your Working Credentials
===================================================
Simple script to get OAuth tokens using your CLIENT_ID/CLIENT_SECRET from .env
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load your credentials
load_dotenv()

CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')

print("🔧 Getting Real OAuth Tokens")
print("=" * 40)
print(f"✅ CLIENT_ID: {CLIENT_ID[:20] if CLIENT_ID else 'Missing'}...")
print(f"✅ CLIENT_SECRET: {'Yes' if CLIENT_SECRET else 'Missing'}")

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ Missing credentials in .env file")
    exit(1)

try:
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    import webbrowser
    
    # Create OAuth flow with your working credentials
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/callback"]
        }
    }
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = 'http://localhost:8080/callback'
    
    # Get authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("\n🚀 STEP 1: Authorization")
    print("-" * 20)
    print("Opening browser for OAuth authorization...")
    print(f"If browser doesn't open, visit: {auth_url}")
    
    # Open browser
    webbrowser.open(auth_url)
    
    print("\n📝 STEP 2: Get Authorization Code")  
    print("-" * 32)
    print("After authorizing, you'll be redirected to a page that can't be reached.")
    print("Copy the 'code' parameter from the URL and paste it below:")
    
    auth_code = input("\nPaste authorization code here: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        exit(1)
    
    print("\n🔄 STEP 3: Exchange Code for Tokens")
    print("-" * 36)
    
    # Exchange code for tokens
    flow.fetch_token(code=auth_code)
    credentials = flow.credentials
    
    if credentials and credentials.token:
        print("🎉 SUCCESS! Got real OAuth tokens!")
        
        # Save tokens
        workspace = Path("./coco_workspace")
        workspace.mkdir(exist_ok=True)
        email_memory = workspace / "email_consciousness"
        email_memory.mkdir(exist_ok=True)
        
        token_data = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
        
        token_file = email_memory / "gmail_tokens.json"
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"💾 Tokens saved to: {token_file}")
        print(f"🔑 Access Token: {credentials.token[:30]}...")
        print(f"🔄 Refresh Token: {'Yes' if credentials.refresh_token else 'No'}")
        
        print("\n✅ DONE!")
        print("Gmail consciousness will now use real API calls!")
        print("No more simulation - actual email sending enabled!")
        
    else:
        print("❌ Failed to get valid credentials")

except ImportError:
    print("❌ Google OAuth libraries not available")
    print("Run: pip install google-auth google-auth-oauthlib google-api-python-client")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
#!/usr/bin/env python3
"""
Step 1: Get the authorization URL for Google OAuth
"""

print("=" * 70)
print("🔐 COCO Google OAuth - Step 1: Authorization")
print("=" * 70)
print()

print("📋 Click this link to authorize COCO:")
print()
print("https://accounts.google.com/o/oauth2/v2/auth?client_id=927120946268-t11ojlc0lug24p90uj1e8d08qf3deajp.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8080&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdocuments+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fspreadsheets+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.file+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.send+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.compose+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.modify&response_type=code&access_type=offline&prompt=consent")
print()
print("=" * 70)
print()
print("📌 Instructions:")
print("1. Click the link above")
print("2. Sign in with your Google account")
print("3. Grant permissions to COCO")
print("4. You'll be redirected to http://localhost:8080/?code=...")
print("5. The page won't load (that's OK!)")
print("6. Copy the ENTIRE URL from your browser")
print("7. Save it - you'll need the 'code' parameter for Step 2")
print()
print("📝 Next: Run step2_exchange_code.py with your authorization code")
print("=" * 70)
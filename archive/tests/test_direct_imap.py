#!/usr/bin/env python3
"""
Direct IMAP Test - Debug Email Retrieval Issue
==============================================
Tests direct IMAP connection to identify if the regression is in:
1. IMAP connection/authentication
2. Email search/retrieval
3. Gmail consciousness integration layer
"""

import imaplib
import os
from dotenv import load_dotenv

def test_direct_imap():
    """Test direct IMAP connection without Gmail consciousness layer"""
    
    print("🔧 Direct IMAP Connection Test")
    print("=" * 40)
    print()
    
    # Load environment
    load_dotenv()
    
    # Gmail settings
    email = "keith@gococoa.ai" 
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not app_password:
        print("❌ GMAIL_APP_PASSWORD not found in environment")
        return
    
    print(f"📧 Email: {email}")
    print(f"🔑 App Password: {'*' * (len(app_password)-4) + app_password[-4:]}")
    print()
    
    try:
        print("🔌 Testing IMAP connection...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        print("✅ IMAP SSL connection established")
        
        print("🔐 Testing login...")
        mail.login(email, app_password)
        print("✅ Login successful")
        
        print("📁 Selecting INBOX...")
        mail.select("INBOX")
        print("✅ INBOX selected")
        
        print("🔍 Testing email search (ALL)...")
        result, data = mail.search(None, "ALL")
        print(f"   Search result: {result}")
        
        if result == 'OK':
            email_ids = data[0].split()
            print(f"✅ Found {len(email_ids)} total emails")
            
            if len(email_ids) > 0:
                print(f"   First 5 email IDs: {email_ids[:5]}")
                print(f"   Last 5 email IDs: {email_ids[-5:]}")
                
                # Test fetching the most recent email
                print("📬 Testing email fetch (most recent)...")
                latest_id = email_ids[-1]
                result, msg_data = mail.fetch(latest_id, '(RFC822)')
                
                if result == 'OK':
                    print("✅ Successfully fetched latest email")
                    
                    # Parse the email
                    import email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    print("📧 Latest Email Details:")
                    print(f"   From: {msg.get('From', 'Unknown')}")
                    print(f"   Subject: {msg.get('Subject', 'No Subject')}")
                    print(f"   Date: {msg.get('Date', 'No Date')}")
                else:
                    print(f"❌ Failed to fetch email: {result}")
            else:
                print("⚠️  No emails found in INBOX")
        else:
            print(f"❌ Search failed: {result}")
        
        print("🔒 Closing connection...")
        mail.close()
        mail.logout()
        print("✅ Connection closed successfully")
        
        print()
        print("=" * 40)
        print("🎉 DIRECT IMAP TEST RESULTS:")
        print("=" * 40)
        
        if len(email_ids) > 0:
            print(f"✅ IMAP connection working: {len(email_ids)} emails found")
            print("✅ Authentication working")
            print("✅ Email fetching working")
            print()
            print("🔍 CONCLUSION: IMAP layer is functional")
            print("   Issue likely in Gmail consciousness integration")
        else:
            print("❌ No emails found - potential issues:")
            print("   - Wrong folder (check Labels in Gmail)")
            print("   - App password permissions")
            print("   - Gmail IMAP settings")
        
    except Exception as e:
        print(f"❌ Direct IMAP test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_imap()
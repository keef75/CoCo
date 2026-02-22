#!/usr/bin/env python3
"""
Simple Gmail Consciousness Debug Test
====================================
Tests the rolled-back simple Gmail consciousness version to verify it
can now retrieve emails after the regression fix.
"""

import asyncio
import sys
from pathlib import Path

# Set up environment
sys.path.insert(0, str(Path(__file__).parent))

async def test_simple_gmail_debug():
    """Test simple Gmail consciousness version"""
    
    print("🔧 Simple Gmail Consciousness Debug Test")
    print("=" * 50)
    print("Direct IMAP shows 2904 emails available - testing consciousness layer")
    print()
    
    try:
        from gmail_consciousness import GmailConsciousness
        from cocoa import Config
        
        config = Config()
        gmail = GmailConsciousness(config)
        
        print("📧 Testing Gmail consciousness initialization...")
        await gmail.initialize_consciousness()
        print("✅ Gmail consciousness initialized")
        print()
        
        print("📬 Testing simple email retrieval (no filters)...")
        emails = await gmail.receive_emails(limit=5)
        
        print(f"📊 Gmail consciousness returned: {len(emails)} emails")
        print()
        
        if emails:
            print("🎉 SUCCESS: Gmail consciousness is working!")
            print("📧 Sample emails retrieved:")
            
            for i, email in enumerate(emails, 1):
                print(f"   {i}. From: {email.get('from', 'Unknown')}")
                print(f"      Subject: {email.get('subject', 'No subject')[:60]}...")
                print(f"      Date: {email.get('date', 'Unknown')}")
                print(f"      Parsing: {email.get('parsing_method', 'Unknown')}")
                print()
        else:
            print("❌ FAILURE: Gmail consciousness returned 0 emails")
            print("   This indicates an issue in the consciousness integration")
        
        await gmail.close()
        
        print("=" * 50)
        print("🔍 DEBUG ANALYSIS:")
        print("=" * 50)
        
        if len(emails) > 0:
            print("✅ Gmail consciousness layer is working correctly")
            print("✅ Rollback to simple version successful")
            print("✅ Ready to carefully re-add production features")
        else:
            print("❌ Gmail consciousness layer still has issues")
            print("   Need to debug further in the consciousness integration")
            print("   Check console output above for error messages")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_gmail_debug())
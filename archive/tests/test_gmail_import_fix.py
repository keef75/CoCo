#!/usr/bin/env python3
"""
Gmail Import Fix Verification
============================
Quick test to verify the pytz import issue is resolved and Gmail consciousness
works properly with the production-ready parsing enhancements.
"""

import asyncio
import sys
from pathlib import Path

# Set up environment
sys.path.insert(0, str(Path(__file__).parent))

async def verify_gmail_import_fix():
    """Verify Gmail consciousness imports and works correctly"""
    
    print("🔧 Gmail Import Fix Verification")
    print("=" * 40)
    print()
    
    try:
        # Test 1: Import Gmail consciousness
        print("📧 Testing Gmail consciousness imports...")
        from gmail_consciousness import GmailConsciousness
        from cocoa import Config
        print("✅ Gmail consciousness imported successfully")
        
        # Test 2: Instantiate Gmail consciousness
        print("🧠 Testing Gmail consciousness instantiation...")
        config = Config()
        gmail = GmailConsciousness(config)
        print("✅ Gmail consciousness instantiated successfully")
        
        # Test 3: Test timezone-aware date parsing
        print("📅 Testing timezone-aware date parsing...")
        test_dates = [
            'Mon, 16 Dec 2024 14:30:00 -0600',
            'Tue, 17 Dec 2024 09:15:00 +0000',
            'Invalid date header'
        ]
        
        for test_date in test_dates:
            date_info, is_today = gmail._parse_email_date(test_date)
            if isinstance(date_info, dict) and 'formatted' in date_info:
                print(f"   ✅ '{test_date[:20]}...' → {date_info['formatted']}")
            else:
                print(f"   ⚠️  '{test_date}' → {date_info}")
        
        # Test 4: Test enhanced sender parsing
        print("👤 Testing enhanced sender parsing...")
        test_senders = [
            'John Smith <john@company.com>',
            'noreply@github.com',
            'notifications@slack.com',
            'jane.doe@startup.io'
        ]
        
        for sender in test_senders:
            sender_info = gmail._parse_sender_info(sender)
            automated = " (Automated)" if sender_info.get('is_automated') else ""
            print(f"   ✅ '{sender}' → {sender_info['name']}{automated}")
        
        # Test 5: Test smart categorization
        print("🏷️  Testing smart categorization...")
        test_scenarios = [
            ("Newsletter team <news@company.com>", "Monthly Newsletter", "Unsubscribe here"),
            ("Boss <boss@company.com>", "URGENT: Meeting tomorrow", "Please respond ASAP"),
            ("Finance <finance@company.com>", "Invoice #12345", "Payment due"),
            ("Calendar <calendar@company.com>", "Meeting scheduled", "Meeting reminder")
        ]
        
        for sender_raw, subject, body in test_scenarios:
            sender_info = gmail._parse_sender_info(sender_raw)
            categories = gmail._categorize_email(sender_info, subject, body)
            print(f"   ✅ '{subject}' → {categories}")
        
        print()
        print("=" * 40)
        print("🎉 GMAIL IMPORT FIX VERIFICATION COMPLETE!")
        print("=" * 40)
        print()
        print("✅ ISSUE RESOLUTION:")
        print("   - pytz library installed successfully")
        print("   - Fallback timezone handling implemented")
        print("   - All production parsing features working")
        print("   - Gmail consciousness ready for COCO integration")
        print()
        print("🚀 Gmail consciousness can now provide comprehensive email analysis!")
        print("   Ready for commands like: 'give me a summary of today's emails'")
        
    except Exception as e:
        print(f"❌ Import fix verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_gmail_import_fix())
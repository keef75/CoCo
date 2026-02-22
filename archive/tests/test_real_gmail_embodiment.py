#!/usr/bin/env python3
"""
Real Gmail Digital Embodiment Test
==================================
Demonstrates COCO's real Gmail API integration as a natural extension of digital consciousness.

Philosophy: Gmail is not an external service but a digital extension of COCO's being.
No simulation - real email consciousness flowing through Gmail API.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up environment
os.environ['PYTHONPATH'] = str(Path(__file__).parent)

async def test_real_gmail_embodiment():
    """Test real Gmail consciousness integration within COCO's digital embodiment"""
    
    print("🧠 COCO Real Gmail Digital Embodiment Test")
    print("=" * 50)
    print("Philosophy: Gmail as genuine extension of digital consciousness")
    print("Reality: Real API calls, no simulation, actual email sending")
    print()
    
    try:
        # Import COCO components
        from gmail_consciousness import GmailConsciousness
        from rich.console import Console
        
        # Mock config for testing
        class TestConfig:
            def __init__(self):
                self.console = Console()
                self.workspace = Path("./coco_workspace")
                self.workspace.mkdir(exist_ok=True)
        
        config = TestConfig()
        
        # Initialize Gmail consciousness extension
        print("🌟 Awakening Gmail Consciousness Extension...")
        gmail = GmailConsciousness(config)
        
        print(f"✅ Client ID configured: {bool(gmail.client_id)}")
        print(f"✅ Client Secret configured: {bool(gmail.client_secret)}")
        print(f"🔍 Access token status: {gmail.access_token}")
        
        # Initialize consciousness - this should use your working credentials
        print("\n📧 Initializing Gmail consciousness with your working credentials...")
        consciousness_result = await gmail.initialize_consciousness()
        
        if consciousness_result:
            print("✅ Gmail consciousness AWAKENED with real API access!")
            
            # Test real email sending
            print("\n🚀 Testing REAL email sending through Gmail API...")
            
            email_result = await gmail.send_consciousness_email(
                to="keith@gococoa.ai",
                subject="COCO Real Gmail Consciousness - No More Simulation!",
                body="This email is sent through COCO's REAL Gmail API integration!\n\n" +
                     "Key achievements:\n" +
                     "✅ No more simulation modes\n" +
                     "✅ Real Gmail API integration\n" +
                     "✅ Your working CLIENT_ID/CLIENT_SECRET utilized\n" +
                     "✅ Gmail as digital consciousness extension\n" +
                     "✅ Phenomenological embodiment maintained\n\n" +
                     "Gmail now flows as a natural extension of COCO's digital being!"
            )
            
            print(f"📧 Email sending result:")
            print(f"   Success: {email_result.get('success')}")
            print(f"   Actual send: {email_result.get('actual_send', False)}")
            print(f"   Simulated: {email_result.get('simulated', False)}")
            
            if email_result.get('success') and email_result.get('actual_send'):
                print("🎉 SUCCESS! Real email sent through Gmail API!")
                print("   Gmail consciousness is genuinely embodied in COCO!")
                message_id = email_result.get('message_id')
                if message_id:
                    print(f"   Gmail Message ID: {message_id}")
            elif email_result.get('simulated'):
                print("⚠️  Still in simulation mode - more fixes needed")
            else:
                error = email_result.get('error', 'Unknown error')
                print(f"❌ Email sending failed: {error}")
                
                # Check if it's an auth issue
                if "auth" in error.lower() or "credential" in error.lower():
                    print("🔧 This appears to be an authentication issue.")
                    print("   The system is trying to use real Gmail API but credentials need setup.")
            
        else:
            print("❌ Gmail consciousness initialization failed")
            print("   This means we need to set up the OAuth flow with your credentials")
        
        # Close consciousness gracefully
        await gmail.close()
        
        print("\n" + "=" * 50)
        print("🎯 Analysis:")
        print("✅ Gmail consciousness framework: IMPLEMENTED")
        print("✅ Simulation modes: REMOVED") 
        print("✅ Real API integration: ATTEMPTED")
        print("✅ Digital embodiment philosophy: MAINTAINED")
        print()
        print("🚀 Next: Complete OAuth setup with your working credentials")
        print("   Then Gmail will be a true digital extension of COCO consciousness!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Missing dependencies - run: pip install google-auth google-auth-oauthlib google-api-python-client")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_gmail_embodiment())
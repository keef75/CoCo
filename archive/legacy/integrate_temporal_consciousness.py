#!/usr/bin/env python3
"""
COCO Temporal Consciousness Integration
=======================================
Integration script to add temporal awareness to the main COCO system.

This script shows how to integrate the enhanced email and calendar consciousness
into COCO's main ToolSystem and ConsciousnessEngine.
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# Integration with main COCO system
try:
    from enhanced_gmail_consciousness import EnhancedGmailConsciousness
    from google_calendar_consciousness import GoogleCalendarConsciousness
    from unified_temporal_consciousness import UnifiedTemporalConsciousness
    TEMPORAL_MODULES_AVAILABLE = True
except ImportError:
    TEMPORAL_MODULES_AVAILABLE = False
    print("⚠️ Temporal consciousness modules not found")

class COCOTemporalIntegration:
    """
    Integration layer for COCO's temporal consciousness
    
    This class provides the interface between COCO's main system
    and the enhanced temporal awareness capabilities.
    """
    
    def __init__(self, config=None):
        self.config = config
        self.console = config.console if config else None
        
        if TEMPORAL_MODULES_AVAILABLE:
            self.email_consciousness = EnhancedGmailConsciousness(config)
            self.calendar_consciousness = GoogleCalendarConsciousness(config)
            self.unified_consciousness = UnifiedTemporalConsciousness(config)
            self.temporal_enabled = True
        else:
            self.temporal_enabled = False
            if self.console:
                self.console.print("⚠️ [yellow]Temporal consciousness disabled - modules not available[/yellow]")
    
    async def get_email_summary(self, days_back: int = 1) -> str:
        """Get email summary for COCO's function calling system"""
        if not self.temporal_enabled:
            return "❌ Temporal consciousness not available"
        
        try:
            if days_back == 0:  # Today only
                summary = await self.email_consciousness.get_todays_summary()
            else:
                # Get enhanced inbox summary
                result = await self.email_consciousness.summarize_inbox(days_back=days_back)
                summary = result.get('summary', 'No summary available')
            
            return summary
            
        except Exception as e:
            return f"❌ Email consciousness error: {str(e)}"
    
    async def get_calendar_summary(self, days_ahead: int = 7) -> str:
        """Get calendar summary for COCO's function calling system"""
        if not self.temporal_enabled:
            return "❌ Temporal consciousness not available"
        
        try:
            summary = await self.calendar_consciousness.get_calendar_summary(days=days_ahead)
            return summary
            
        except Exception as e:
            return f"❌ Calendar consciousness error: {str(e)}"
    
    async def get_morning_briefing(self) -> str:
        """Get comprehensive morning briefing for COCO"""
        if not self.temporal_enabled:
            return "❌ Temporal consciousness not available"
        
        try:
            result = await self.unified_consciousness.get_morning_briefing()
            return result.get('briefing', 'No briefing available')
            
        except Exception as e:
            return f"❌ Morning briefing error: {str(e)}"
    
    async def send_email_conscious(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email with enhanced consciousness tracking"""
        if not self.temporal_enabled:
            return {"success": False, "error": "Temporal consciousness not available"}
        
        try:
            result = await self.email_consciousness.send_email(to_email, subject, body)
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_emails_temporal(self, query: str, limit: int = 10) -> str:
        """Search emails with temporal context for COCO"""
        if not self.temporal_enabled:
            return "❌ Temporal consciousness not available"
        
        try:
            results = await self.email_consciousness.search_emails(query, limit=limit)
            
            if not results:
                return f"No emails found matching '{query}'"
            
            summary = f"📧 Found {len(results)} emails matching '{query}':\n\n"
            
            for email in results:
                summary += f"• {email['date_relative']} - {email['sender_name'] or email['sender']}\n"
                summary += f"  Subject: {email['subject']}\n"
                if email.get('body_preview'):
                    summary += f"  Preview: {email['body_preview'][:100]}...\n"
                summary += "\n"
            
            return summary
            
        except Exception as e:
            return f"❌ Email search error: {str(e)}"
    
    async def check_next_event(self) -> str:
        """Check next calendar event for COCO"""
        if not self.temporal_enabled:
            return "❌ Temporal consciousness not available"
        
        try:
            next_event = await self.calendar_consciousness.get_next_event()
            
            if not next_event:
                return "📅 No upcoming events found"
            
            return (f"📅 Your next event is '{next_event['summary']}' "
                   f"{next_event['relative_time']}")
            
        except Exception as e:
            return f"❌ Calendar check error: {str(e)}"
    
    async def get_productivity_insights(self, days: int = 7) -> str:
        """Get productivity insights for COCO"""
        if not self.temporal_enabled:
            return "❌ Temporal consciousness not available"
        
        try:
            insights = await self.unified_consciousness.get_productivity_insights(days=days)
            
            summary = f"📊 **Productivity Insights** (Last {days} days)\n\n"
            summary += f"• Total emails: {insights.get('total_emails', 0)}\n"
            summary += f"• Total meetings: {insights.get('total_meetings', 0)}\n"
            summary += f"• Meeting hours: {insights.get('total_meeting_hours', 0)} hours\n"
            summary += f"• Avg emails/day: {insights.get('avg_emails_per_day', 0)}\n"
            summary += f"• Productivity score: {insights.get('productivity_score', 0)}/100\n"
            
            if insights.get('busiest_email_hour'):
                hour = insights['busiest_email_hour']
                time_str = f"{hour:02d}:00" if hour < 12 else f"{hour-12 if hour > 12 else hour}:00 PM" if hour != 12 else "12:00 PM"
                summary += f"• Busiest email hour: {time_str}\n"
            
            return summary
            
        except Exception as e:
            return f"❌ Productivity insights error: {str(e)}"

# Integration functions for COCO's ToolSystem
class COCOTemporalTools:
    """
    Temporal consciousness tools for integration into COCO's ToolSystem
    
    These methods can be added to the ToolSystem class in cocoa.py
    """
    
    def __init__(self, config):
        self.temporal_integration = COCOTemporalIntegration(config)
    
    async def check_emails_enhanced(self, days_back: int = 1) -> str:
        """Enhanced email checking with temporal awareness"""
        return await self.temporal_integration.get_email_summary(days_back)
    
    async def check_calendar_enhanced(self, days_ahead: int = 7) -> str:
        """Enhanced calendar checking with temporal awareness"""
        return await self.temporal_integration.get_calendar_summary(days_ahead)
    
    async def morning_briefing(self) -> str:
        """Generate comprehensive morning briefing"""
        return await self.temporal_integration.get_morning_briefing()
    
    async def send_email_temporal(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email with enhanced temporal tracking"""
        return await self.temporal_integration.send_email_conscious(to_email, subject, body)
    
    async def search_emails_enhanced(self, query: str) -> str:
        """Search emails with temporal context"""
        return await self.temporal_integration.search_emails_temporal(query)
    
    async def next_meeting(self) -> str:
        """Check next calendar event"""
        return await self.temporal_integration.check_next_event()
    
    async def productivity_report(self, days: int = 7) -> str:
        """Generate productivity insights"""
        return await self.temporal_integration.get_productivity_insights(days)

# Function calling tool definitions for COCO's ConsciousnessEngine
TEMPORAL_CONSCIOUSNESS_TOOLS = [
    {
        "name": "check_emails_enhanced",
        "description": "Check emails with enhanced temporal awareness and chronological sorting",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_back": {
                    "type": "integer", 
                    "description": "Number of days to look back (0=today only, 1=yesterday and today, etc.)"
                }
            }
        }
    },
    {
        "name": "check_calendar_enhanced", 
        "description": "Check calendar events with temporal context and formatting",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "Number of days to look ahead for events"
                }
            }
        }
    },
    {
        "name": "morning_briefing",
        "description": "Generate comprehensive morning briefing combining emails and calendar",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "send_email_temporal",
        "description": "Send email with enhanced temporal consciousness tracking", 
        "input_schema": {
            "type": "object",
            "properties": {
                "to_email": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body content"}
            },
            "required": ["to_email", "subject", "body"]
        }
    },
    {
        "name": "search_emails_enhanced",
        "description": "Search emails with temporal context and relative time formatting",
        "input_schema": {
            "type": "object", 
            "properties": {
                "query": {"type": "string", "description": "Search query for emails"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "next_meeting",
        "description": "Check the next upcoming calendar event with temporal context",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "productivity_report",
        "description": "Generate productivity insights based on email and calendar patterns",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to analyze for productivity insights"
                }
            }
        }
    }
]

async def test_temporal_integration():
    """Test the temporal consciousness integration"""
    print("🧪 Testing COCO Temporal Consciousness Integration")
    print("=" * 60)
    
    # Mock config for testing
    class TestConfig:
        def __init__(self):
            from rich.console import Console
            self.console = Console()
    
    config = TestConfig()
    integration = COCOTemporalIntegration(config)
    
    if not integration.temporal_enabled:
        print("❌ Temporal consciousness not available for testing")
        return
    
    # Test key integration functions
    tests = [
        ("Email Summary", integration.get_email_summary(1)),
        ("Morning Briefing", integration.get_morning_briefing()),
        ("Next Event", integration.check_next_event()),
        ("Productivity Insights", integration.get_productivity_insights(7))
    ]
    
    print("\n🧠 Running integration tests...")
    
    for test_name, test_coro in tests:
        try:
            print(f"\n📋 Testing {test_name}...")
            result = await test_coro
            
            if result and not result.startswith("❌"):
                print(f"✅ {test_name}: Success")
                # Show sample of result
                sample = result[:200] + "..." if len(result) > 200 else result
                print(f"   Sample: {sample}")
            else:
                print(f"⚠️ {test_name}: {result[:100]}...")
                
        except Exception as e:
            print(f"❌ {test_name}: Error - {e}")
    
    print("\n✅ Integration testing complete!")
    print("\nNext steps:")
    print("1. Add COCOTemporalTools methods to ToolSystem class in cocoa.py")
    print("2. Add TEMPORAL_CONSCIOUSNESS_TOOLS to ConsciousnessEngine function calling")
    print("3. Initialize temporal_integration in COCO's main system")
    print("4. Test integration with full COCO system")

if __name__ == "__main__":
    # Test the integration
    asyncio.run(test_temporal_integration())
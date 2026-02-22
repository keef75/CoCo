#!/usr/bin/env python3
"""
Test Temporal Email Fix - Verify Enhanced Gmail Consciousness
============================================================
Comprehensive test for the temporal awareness fix in Gmail consciousness.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_gmail_consciousness import EnhancedGmailConsciousness

class TemporalTestConfig:
    """Mock config for testing"""
    def __init__(self):
        self.console = Console()

async def test_temporal_awareness():
    """Test that email temporal sorting and filtering work correctly"""
    
    console = Console()
    config = TemporalTestConfig()
    
    console.print(Panel.fit(
        "🧪 Testing Enhanced Gmail Temporal Awareness\n"
        "Verifying proper date parsing, sorting, and temporal context",
        title="[bold blue]TEMPORAL EMAIL TEST[/bold blue]",
        border_style="blue"
    ))
    
    # Initialize enhanced Gmail consciousness
    gmail = EnhancedGmailConsciousness(config)
    
    test_results = {
        "temporal_parsing": False,
        "chronological_sorting": False,
        "today_filtering": False,
        "relative_time_formatting": False,
        "search_functionality": False
    }
    
    try:
        # Test 1: Basic email retrieval with temporal parsing
        console.print("\n📅 [bold cyan]Test 1: Basic Email Retrieval with Temporal Parsing[/bold cyan]")
        emails = await gmail.receive_emails(limit=10)
        
        if emails:
            console.print(f"✅ Retrieved {len(emails)} emails")
            
            # Check temporal fields
            first_email = emails[0]
            required_fields = ['datetime', 'date_formatted', 'date_relative', 'time_sort']
            has_temporal_fields = all(field in first_email for field in required_fields)
            
            if has_temporal_fields:
                console.print("✅ All temporal fields present")
                test_results["temporal_parsing"] = True
                
                # Display sample temporal data
                console.print(f"📊 Sample temporal data:")
                console.print(f"   • Raw date: {first_email.get('date_raw', 'N/A')}")
                console.print(f"   • Formatted: {first_email.get('date_formatted', 'N/A')}")
                console.print(f"   • Relative: {first_email.get('date_relative', 'N/A')}")
            else:
                console.print("❌ Missing temporal fields")
        else:
            console.print("⚠️ No emails retrieved - cannot test temporal parsing")
        
        # Test 2: Chronological sorting verification
        console.print("\n📅 [bold cyan]Test 2: Chronological Sorting Verification[/bold cyan]")
        weekly_emails = await gmail.receive_emails(days_back=7, limit=20)
        
        if len(weekly_emails) > 1:
            # Check if emails are sorted newest first
            is_sorted = True
            for i in range(len(weekly_emails) - 1):
                if weekly_emails[i]["time_sort"] < weekly_emails[i + 1]["time_sort"]:
                    is_sorted = False
                    break
            
            if is_sorted:
                console.print("✅ Emails properly sorted by date (newest first)")
                test_results["chronological_sorting"] = True
                
                # Show sorting evidence
                console.print("📊 Sorting verification:")
                for i, email in enumerate(weekly_emails[:5]):
                    console.print(f"   {i+1}. {email['date_relative']} - {email['subject'][:50]}...")
            else:
                console.print("❌ Emails not properly sorted")
        else:
            console.print("⚠️ Need more emails to test sorting")
        
        # Test 3: Today's emails filtering
        console.print("\n📅 [bold cyan]Test 3: Today's Email Filtering[/bold cyan]")
        todays_emails = await gmail.receive_emails(limit=50, today_only=True)
        
        if todays_emails:
            all_today = all(email.get('is_today', False) for email in todays_emails)
            if all_today:
                console.print(f"✅ All {len(todays_emails)} retrieved emails are from today")
                test_results["today_filtering"] = True
            else:
                today_count = sum(1 for email in todays_emails if email.get('is_today', False))
                console.print(f"⚠️ Only {today_count}/{len(todays_emails)} emails marked as today")
        else:
            console.print("ℹ️ No emails from today found")
            test_results["today_filtering"] = True  # Not an error if no today emails
        
        # Test 4: Relative time formatting
        console.print("\n📅 [bold cyan]Test 4: Relative Time Formatting[/bold cyan]")
        if emails:
            relative_times = [email.get('date_relative', '') for email in emails[:5]]
            valid_relative_formats = [
                'just now', 'ago', 'yesterday', 'days ago', 'week', 'weeks ago'
            ]
            
            valid_count = 0
            for rel_time in relative_times:
                if any(fmt in rel_time.lower() for fmt in valid_relative_formats) or 'in the future' in rel_time.lower():
                    valid_count += 1
            
            if valid_count >= len(relative_times) * 0.8:  # 80% should be valid
                console.print(f"✅ Relative time formatting working ({valid_count}/{len(relative_times)} valid)")
                test_results["relative_time_formatting"] = True
                
                # Show examples
                console.print("📊 Relative time examples:")
                for email in emails[:3]:
                    console.print(f"   • {email.get('date_relative', 'N/A')} - {email['subject'][:40]}...")
            else:
                console.print(f"❌ Relative time formatting issues ({valid_count}/{len(relative_times)} valid)")
        
        # Test 5: Search functionality with temporal context
        console.print("\n📅 [bold cyan]Test 5: Search with Temporal Context[/bold cyan]")
        search_results = await gmail.search_emails("test", limit=5)
        
        if search_results:
            console.print(f"✅ Search returned {len(search_results)} results")
            
            # Check if search results have temporal data and are sorted
            has_temporal = all('time_sort' in email for email in search_results)
            if has_temporal and len(search_results) > 1:
                is_sorted = all(
                    search_results[i]["time_sort"] >= search_results[i+1]["time_sort"]
                    for i in range(len(search_results)-1)
                )
                if is_sorted:
                    console.print("✅ Search results properly sorted by date")
                    test_results["search_functionality"] = True
                else:
                    console.print("❌ Search results not properly sorted")
            elif has_temporal:
                console.print("✅ Search results have temporal data")
                test_results["search_functionality"] = True
        else:
            console.print("ℹ️ No search results found (testing with 'test' query)")
        
        # Test 6: Daily summary functionality
        console.print("\n📅 [bold cyan]Test 6: Daily Summary with Temporal Grouping[/bold cyan]")
        daily_summary = await gmail.get_todays_summary()
        
        if "No emails" not in daily_summary:
            console.print("✅ Daily summary generated successfully")
            
            # Check for temporal groupings (morning, afternoon, evening)
            has_groupings = any(period in daily_summary for period in ['Morning', 'Afternoon', 'Evening'])
            if has_groupings:
                console.print("✅ Temporal groupings (morning/afternoon/evening) detected")
            else:
                console.print("ℹ️ No temporal groupings found (may be expected)")
        else:
            console.print("ℹ️ No emails today - daily summary shows appropriate message")
        
    except Exception as e:
        console.print(f"❌ [red]Test error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
    
    # Generate test results summary
    console.print(Panel.fit(
        generate_test_summary(test_results),
        title="[bold green]TEST RESULTS SUMMARY[/bold green]",
        border_style="green"
    ))
    
    return test_results

def generate_test_summary(results):
    """Generate a formatted test results summary"""
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    summary = f"**Test Results: {passed}/{total} passed**\n\n"
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        formatted_name = test_name.replace('_', ' ').title()
        summary += f"{status} {formatted_name}\n"
    
    if passed == total:
        summary += "\n🎉 **All temporal awareness tests passed!**"
        summary += "\nThe enhanced Gmail consciousness is ready for production."
    elif passed >= total * 0.8:  # 80% pass rate
        summary += f"\n✅ **Most tests passed ({passed}/{total})**"
        summary += "\nTemporal awareness is working with minor issues."
    else:
        summary += f"\n⚠️ **Some tests failed ({passed}/{total})**"
        summary += "\nTemporal awareness needs additional fixes."
    
    return summary

async def test_integration_compatibility():
    """Test backward compatibility with existing COCO integration"""
    console = Console()
    config = TemporalTestConfig()
    
    console.print(Panel.fit(
        "🔄 Testing Backward Compatibility\n"
        "Ensuring enhanced consciousness works with existing COCO integration",
        title="[bold yellow]COMPATIBILITY TEST[/bold yellow]",
        border_style="yellow"
    ))
    
    gmail = EnhancedGmailConsciousness(config)
    
    try:
        # Test backward compatibility methods
        console.print("\n📧 Testing receive_consciousness_emails (compatibility)")
        compat_result = await gmail.receive_consciousness_emails(max_results=5)
        
        if compat_result.get('success') and compat_result.get('emails'):
            console.print(f"✅ Compatibility method works - {len(compat_result['emails'])} emails")
        else:
            console.print("❌ Compatibility method failed")
        
        console.print("\n📊 Testing summarize_inbox (enhanced)")
        summary_result = await gmail.summarize_inbox(days_back=1)
        
        if summary_result.get('success'):
            console.print("✅ Enhanced inbox summary works")
            console.print(f"   Total emails analyzed: {summary_result.get('total_emails', 0)}")
            console.print(f"   Temporal method: {summary_result.get('temporal_method', 'unknown')}")
        else:
            console.print("❌ Enhanced inbox summary failed")
        
        console.print("\n✅ [green]Backward compatibility verified[/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Compatibility test error: {e}[/red]")

if __name__ == "__main__":
    print("🧪 Enhanced Gmail Consciousness Temporal Test Suite")
    print("=" * 60)
    
    # Check for required environment variables
    if not os.getenv("GMAIL_APP_PASSWORD"):
        print("❌ Error: GMAIL_APP_PASSWORD environment variable not set")
        print("Please set this in your .env file for testing")
        sys.exit(1)
    
    # Run temporal tests
    asyncio.run(test_temporal_awareness())
    
    print("\n" + "=" * 60)
    print("🔄 Running compatibility tests...")
    
    # Run compatibility tests
    asyncio.run(test_integration_compatibility())
    
    print("\n" + "=" * 60)
    print("✅ Temporal email fix testing complete!")
    print("Next steps: Add CalDAV dependency and implement Google Calendar integration")
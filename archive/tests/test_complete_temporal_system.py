#!/usr/bin/env python3
"""
Complete Temporal System Test Suite
===================================
Comprehensive testing for the unified temporal consciousness system.

Tests:
1. Enhanced Gmail consciousness with temporal awareness
2. Google Calendar consciousness with CalDAV integration
3. Unified temporal awareness combining both systems
4. Morning briefing generation
5. Integration with COCO's main system
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import temporal consciousness modules
try:
    from enhanced_gmail_consciousness import EnhancedGmailConsciousness
    from google_calendar_consciousness import GoogleCalendarConsciousness
    from unified_temporal_consciousness import UnifiedTemporalConsciousness
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"❌ Module import error: {e}")

class TemporalTestConfig:
    """Test configuration with console"""
    def __init__(self):
        self.console = Console()

class TemporalTestSuite:
    """Comprehensive temporal consciousness test suite"""
    
    def __init__(self):
        self.console = Console()
        self.config = TemporalTestConfig()
        self.test_results = {
            'email_temporal_parsing': False,
            'email_chronological_sorting': False,
            'calendar_connection': False,
            'calendar_event_parsing': False,
            'unified_temporal_overview': False,
            'morning_briefing_generation': False,
            'temporal_conflict_detection': False,
            'productivity_insights': False,
            'integration_compatibility': False
        }
    
    async def run_complete_test_suite(self):
        """Run the complete temporal consciousness test suite"""
        
        self.console.print(Panel.fit(
            "🧠 Complete Temporal Consciousness Test Suite\n"
            "Testing COCO's enhanced email and calendar consciousness\n"
            "with unified temporal awareness and morning briefings",
            title="[bold blue]TEMPORAL CONSCIOUSNESS TEST[/bold blue]",
            border_style="blue"
        ))
        
        if not MODULES_AVAILABLE:
            self.console.print("❌ [red]Cannot run tests - modules not available[/red]")
            return False
        
        # Check prerequisites
        if not self._check_prerequisites():
            return False
        
        # Initialize systems
        self.email_consciousness = EnhancedGmailConsciousness(self.config)
        self.calendar_consciousness = GoogleCalendarConsciousness(self.config)
        self.unified_consciousness = UnifiedTemporalConsciousness(self.config)
        
        # Run test phases
        await self._test_phase_1_email_consciousness()
        await self._test_phase_2_calendar_consciousness() 
        await self._test_phase_3_unified_consciousness()
        await self._test_phase_4_integration_features()
        await self._test_phase_5_coco_integration()
        
        # Generate final results
        self._generate_test_report()
        
        return self._calculate_overall_success()
    
    def _check_prerequisites(self):
        """Check that all prerequisites are available"""
        self.console.print("\n🔍 [bold cyan]Checking Prerequisites[/bold cyan]")
        
        prerequisites = [
            ("GMAIL_APP_PASSWORD", os.getenv("GMAIL_APP_PASSWORD")),
            ("Enhanced Gmail Module", "enhanced_gmail_consciousness" in sys.modules),
            ("Calendar Module", "google_calendar_consciousness" in sys.modules),
            ("Unified Module", "unified_temporal_consciousness" in sys.modules),
        ]
        
        all_good = True
        for name, check in prerequisites:
            if check:
                self.console.print(f"✅ {name}: Available")
            else:
                self.console.print(f"❌ {name}: Missing")
                all_good = False
        
        if not all_good:
            self.console.print("\n⚠️ [yellow]Some prerequisites are missing. Tests may fail.[/yellow]")
        
        return all_good
    
    async def _test_phase_1_email_consciousness(self):
        """Phase 1: Test enhanced email consciousness"""
        self.console.print("\n📧 [bold cyan]Phase 1: Enhanced Email Consciousness[/bold cyan]")
        
        try:
            # Test 1.1: Basic email retrieval with temporal parsing
            self.console.print("\n📋 Test 1.1: Email Temporal Parsing")
            emails = await self.email_consciousness.receive_emails(limit=5)
            
            if emails and all('time_sort' in email for email in emails):
                self.console.print("✅ Email temporal parsing working")
                self.test_results['email_temporal_parsing'] = True
            else:
                self.console.print("❌ Email temporal parsing failed")
            
            # Test 1.2: Chronological sorting
            self.console.print("\n📋 Test 1.2: Chronological Sorting")
            if len(emails) > 1:
                is_sorted = all(
                    emails[i]['time_sort'] >= emails[i+1]['time_sort']
                    for i in range(len(emails)-1)
                )
                if is_sorted:
                    self.console.print("✅ Chronological sorting working")
                    self.test_results['email_chronological_sorting'] = True
                else:
                    self.console.print("❌ Chronological sorting failed")
            
            # Test 1.3: Today's emails filtering
            self.console.print("\n📋 Test 1.3: Today's Email Summary")
            summary = await self.email_consciousness.get_todays_summary()
            if summary and "Today's Email Summary" in summary:
                self.console.print("✅ Today's email summary generated")
            else:
                self.console.print("ℹ️ Today's email summary empty (may be expected)")
            
        except Exception as e:
            self.console.print(f"❌ Phase 1 error: {e}")
    
    async def _test_phase_2_calendar_consciousness(self):
        """Phase 2: Test Google Calendar consciousness"""
        self.console.print("\n📅 [bold cyan]Phase 2: Google Calendar Consciousness[/bold cyan]")
        
        try:
            # Test 2.1: Calendar connection
            self.console.print("\n📋 Test 2.1: Calendar Connection")
            connected = await self.calendar_consciousness.connect()
            
            if connected:
                self.console.print("✅ Calendar connection successful")
                self.test_results['calendar_connection'] = True
            else:
                self.console.print("❌ Calendar connection failed")
                self.console.print("   Note: This may be expected if CalDAV isn't configured")
                return  # Skip remaining calendar tests
            
            # Test 2.2: Today's events
            self.console.print("\n📋 Test 2.2: Today's Events")
            today_events = await self.calendar_consciousness.get_todays_events()
            
            if isinstance(today_events, list):
                self.console.print(f"✅ Retrieved {len(today_events)} events for today")
                self.test_results['calendar_event_parsing'] = True
            else:
                self.console.print("❌ Failed to retrieve today's events")
            
            # Test 2.3: Calendar summary
            self.console.print("\n📋 Test 2.3: Calendar Summary")
            summary = await self.calendar_consciousness.get_calendar_summary(days=7)
            
            if summary and "Calendar Summary" in summary:
                self.console.print("✅ Calendar summary generated")
            else:
                self.console.print("ℹ️ Calendar summary empty or error")
                
        except Exception as e:
            self.console.print(f"❌ Phase 2 error: {e}")
            self.console.print("   Note: Calendar errors may be expected without CalDAV setup")
    
    async def _test_phase_3_unified_consciousness(self):
        """Phase 3: Test unified temporal consciousness"""
        self.console.print("\n🧠 [bold cyan]Phase 3: Unified Temporal Consciousness[/bold cyan]")
        
        try:
            # Test 3.1: Temporal overview
            self.console.print("\n📋 Test 3.1: Temporal Overview")
            overview = await self.unified_consciousness.get_temporal_overview(
                days_back=1, days_forward=7
            )
            
            if overview and overview.get('total_events', 0) >= 0:
                self.console.print(f"✅ Temporal overview: {overview.get('total_events', 0)} total events")
                self.console.print(f"   📧 {overview.get('email_count', 0)} emails")
                self.console.print(f"   📅 {overview.get('calendar_count', 0)} calendar events")
                self.test_results['unified_temporal_overview'] = True
            else:
                self.console.print("❌ Temporal overview failed")
            
            # Test 3.2: Morning briefing
            self.console.print("\n📋 Test 3.2: Morning Briefing")
            briefing_result = await self.unified_consciousness.get_morning_briefing()
            
            if briefing_result and 'briefing' in briefing_result:
                self.console.print("✅ Morning briefing generated")
                self.test_results['morning_briefing_generation'] = True
                
                # Show sample of briefing
                briefing_sample = briefing_result['briefing'][:200] + "..."
                self.console.print(f"   Sample: {briefing_sample}")
            else:
                self.console.print("❌ Morning briefing generation failed")
            
            # Test 3.3: Productivity insights
            self.console.print("\n📋 Test 3.3: Productivity Insights")
            insights = await self.unified_consciousness.get_productivity_insights(days=7)
            
            if insights and 'productivity_score' in insights:
                self.console.print(f"✅ Productivity insights: {insights['productivity_score']}/100")
                self.test_results['productivity_insights'] = True
            else:
                self.console.print("❌ Productivity insights failed")
            
        except Exception as e:
            self.console.print(f"❌ Phase 3 error: {e}")
    
    async def _test_phase_4_integration_features(self):
        """Phase 4: Test integration features"""
        self.console.print("\n🔧 [bold cyan]Phase 4: Integration Features[/bold cyan]")
        
        try:
            # Test 4.1: Temporal conflicts
            self.console.print("\n📋 Test 4.1: Temporal Conflict Detection")
            conflicts = await self.unified_consciousness.get_temporal_conflicts(days_ahead=7)
            
            if conflicts and 'conflict_count' in conflicts:
                self.console.print(f"✅ Conflict detection: {conflicts['conflict_count']} conflicts found")
                self.test_results['temporal_conflict_detection'] = True
            else:
                self.console.print("❌ Conflict detection failed")
            
            # Test 4.2: Meeting time suggestions (if calendar is working)
            if self.test_results.get('calendar_connection', False):
                self.console.print("\n📋 Test 4.2: Meeting Time Suggestions")
                suggestions = await self.unified_consciousness.suggest_optimal_meeting_times(
                    duration_hours=1, days_ahead=7
                )
                
                if suggestions and 'suggestion_count' in suggestions:
                    self.console.print(f"✅ Meeting suggestions: {suggestions['suggestion_count']} slots found")
                else:
                    self.console.print("❌ Meeting time suggestions failed")
            else:
                self.console.print("\n📋 Test 4.2: Meeting Time Suggestions (Skipped - no calendar connection)")
            
        except Exception as e:
            self.console.print(f"❌ Phase 4 error: {e}")
    
    async def _test_phase_5_coco_integration(self):
        """Phase 5: Test COCO integration compatibility"""
        self.console.print("\n🤖 [bold cyan]Phase 5: COCO Integration Compatibility[/bold cyan]")
        
        try:
            # Test 5.1: Backward compatibility methods
            self.console.print("\n📋 Test 5.1: Backward Compatibility")
            
            # Test old method names
            compat_result = await self.email_consciousness.receive_consciousness_emails(
                max_results=5
            )
            
            if compat_result and compat_result.get('success'):
                self.console.print("✅ Backward compatibility methods working")
                self.test_results['integration_compatibility'] = True
            else:
                self.console.print("❌ Backward compatibility failed")
            
            # Test 5.2: Integration with COCO's expected interface
            self.console.print("\n📋 Test 5.2: COCO Interface Compatibility")
            
            # Test if the methods expected by COCO are available
            expected_methods = [
                'receive_emails',
                'send_email', 
                'get_todays_summary',
                'search_emails'
            ]
            
            missing_methods = []
            for method in expected_methods:
                if not hasattr(self.email_consciousness, method):
                    missing_methods.append(method)
            
            if not missing_methods:
                self.console.print("✅ All expected COCO interface methods available")
            else:
                self.console.print(f"❌ Missing methods: {missing_methods}")
                self.test_results['integration_compatibility'] = False
            
        except Exception as e:
            self.console.print(f"❌ Phase 5 error: {e}")
    
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        self.console.print("\n" + "="*60)
        
        # Create results table
        table = Table(title="Temporal Consciousness Test Results")
        table.add_column("Test Category", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="dim")
        
        test_categories = {
            'email_temporal_parsing': ('Email Temporal Parsing', 'Core email date/time parsing'),
            'email_chronological_sorting': ('Email Sorting', 'Chronological order (newest first)'),
            'calendar_connection': ('Calendar Connection', 'CalDAV connection to Google'),
            'calendar_event_parsing': ('Calendar Events', 'Event retrieval and parsing'),
            'unified_temporal_overview': ('Temporal Overview', 'Combined email/calendar view'),
            'morning_briefing_generation': ('Morning Briefing', 'Comprehensive daily summary'),
            'temporal_conflict_detection': ('Conflict Detection', 'Email/calendar conflicts'),
            'productivity_insights': ('Productivity Insights', 'Temporal pattern analysis'),
            'integration_compatibility': ('COCO Integration', 'Compatibility with main system')
        }
        
        passed_count = 0
        total_count = len(self.test_results)
        
        for test_key, (name, description) in test_categories.items():
            passed = self.test_results.get(test_key, False)
            status = "✅ PASS" if passed else "❌ FAIL"
            
            if passed:
                passed_count += 1
            
            table.add_row(name, status, description)
        
        self.console.print(table)
        
        # Overall results
        success_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
        
        if success_rate >= 90:
            result_style = "green"
            result_emoji = "🎉"
            result_message = "Excellent! Temporal consciousness is fully operational."
        elif success_rate >= 70:
            result_style = "yellow"
            result_emoji = "✅"
            result_message = "Good! Most temporal features are working."
        else:
            result_style = "red"
            result_emoji = "⚠️"
            result_message = "Issues detected. Some temporal features need attention."
        
        self.console.print(Panel.fit(
            f"{result_emoji} **Test Results: {passed_count}/{total_count} passed ({success_rate:.1f}%)**\n\n"
            f"{result_message}\n\n"
            f"**Next Steps:**\n"
            f"• Install CalDAV dependencies: `pip install caldav icalendar`\n"
            f"• Configure Google Calendar app password (same as Gmail)\n"
            f"• Test integration with main COCO system\n"
            f"• Run morning briefing in production",
            title=f"[bold {result_style}]TEMPORAL CONSCIOUSNESS TEST COMPLETE[/bold {result_style}]",
            border_style=result_style
        ))
    
    def _calculate_overall_success(self):
        """Calculate if the overall test suite passed"""
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        return (passed / total) >= 0.7  # 70% pass rate for success

async def run_individual_component_tests():
    """Run individual component tests for debugging"""
    console = Console()
    config = TemporalTestConfig()
    
    console.print(Panel.fit(
        "🔧 Individual Component Tests\n"
        "Testing each temporal consciousness component separately",
        title="[bold yellow]COMPONENT TESTS[/bold yellow]",
        border_style="yellow"
    ))
    
    # Test individual components
    try:
        # Email consciousness test
        console.print("\n📧 Testing Enhanced Gmail Consciousness...")
        email_consciousness = EnhancedGmailConsciousness(config)
        emails = await email_consciousness.receive_emails(limit=3)
        console.print(f"   Retrieved {len(emails)} emails")
        
        # Calendar consciousness test
        console.print("\n📅 Testing Google Calendar Consciousness...")
        calendar_consciousness = GoogleCalendarConsciousness(config)
        connected = await calendar_consciousness.connect()
        console.print(f"   Calendar connection: {'Success' if connected else 'Failed'}")
        
        # Unified consciousness test
        console.print("\n🧠 Testing Unified Temporal Consciousness...")
        unified_consciousness = UnifiedTemporalConsciousness(config)
        overview = await unified_consciousness.get_temporal_overview(days_back=1, days_forward=1)
        console.print(f"   Temporal overview: {overview.get('total_events', 0)} events")
        
        console.print("\n✅ [green]Component tests completed[/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Component test error: {e}[/red]")

if __name__ == "__main__":
    print("🧠 Complete Temporal Consciousness Test Suite")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("GMAIL_APP_PASSWORD"):
        print("❌ Error: GMAIL_APP_PASSWORD environment variable not set")
        print("Please configure this in your .env file for testing")
        sys.exit(1)
    
    # Determine test mode
    test_mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    if test_mode == "components":
        print("🔧 Running individual component tests...")
        asyncio.run(run_individual_component_tests())
    else:
        print("🧪 Running complete test suite...")
        test_suite = TemporalTestSuite()
        success = asyncio.run(test_suite.run_complete_test_suite())
        
        if success:
            print("\n🎉 Temporal consciousness test suite PASSED!")
            sys.exit(0)
        else:
            print("\n⚠️ Temporal consciousness test suite had issues.")
            sys.exit(1)
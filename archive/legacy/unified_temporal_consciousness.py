#!/usr/bin/env python3
"""
Unified Temporal Consciousness - COCO's Complete Temporal Awareness
==================================================================
Combines email and calendar consciousness into a unified temporal awareness system.

This creates COCO's complete understanding of time-based information,
integrating communications and scheduled events into coherent temporal context.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz
from dataclasses import dataclass

# Import consciousness modules
from enhanced_gmail_consciousness import EnhancedGmailConsciousness
from google_calendar_consciousness import GoogleCalendarConsciousness

@dataclass
class TemporalEvent:
    """Unified representation of temporal events (email or calendar)"""
    id: str
    type: str  # 'email' or 'calendar'
    title: str
    datetime: datetime
    description: str = ""
    location: str = ""
    participants: List[str] = None
    priority: str = "normal"
    status: str = "active"
    duration: timedelta = None
    relative_time: str = ""
    formatted_time: str = ""
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if not self.relative_time:
            self.relative_time = self._calculate_relative_time()
        if not self.formatted_time:
            self.formatted_time = self.datetime.strftime("%Y-%m-%d %I:%M %p")
    
    def _calculate_relative_time(self):
        """Calculate relative time from now"""
        now = datetime.now(self.datetime.tzinfo)
        diff = self.datetime - now
        
        total_seconds = diff.total_seconds()
        
        if abs(total_seconds) < 60:
            return "now"
        elif total_seconds < 0:
            # Past event
            abs_seconds = abs(total_seconds)
            if abs_seconds < 3600:
                minutes = int(abs_seconds / 60)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif abs_seconds < 86400:
                hours = int(abs_seconds / 3600)
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                days = int(abs_seconds / 86400)
                return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            # Future event
            if total_seconds < 3600:
                minutes = int(total_seconds / 60)
                return f"in {minutes} minute{'s' if minutes != 1 else ''}"
            elif total_seconds < 86400:
                hours = int(total_seconds / 3600)
                return f"in {hours} hour{'s' if hours != 1 else ''}"
            else:
                days = int(total_seconds / 86400)
                return f"in {days} day{'s' if days != 1 else ''}"

class UnifiedTemporalConsciousness:
    """
    Unified temporal awareness combining email and calendar consciousness
    
    This provides COCO with complete temporal context, understanding both
    communications and scheduled events in a coherent timeline.
    """
    
    def __init__(self, config=None):
        self.config = config
        self.console = config.console if config else None
        self.local_tz = pytz.timezone('America/Chicago')
        
        # Initialize consciousness modules
        self.email_consciousness = EnhancedGmailConsciousness(config)
        self.calendar_consciousness = GoogleCalendarConsciousness(config)
        
        if self.console:
            self.console.print("🧠 [cyan]Unified Temporal Consciousness initialized[/cyan]")
            self.console.print("   📧 Email consciousness: Enhanced Gmail with temporal awareness")
            self.console.print("   📅 Calendar consciousness: Google Calendar via CalDAV")
    
    async def get_temporal_overview(self, days_back=1, days_forward=7):
        """
        Get comprehensive temporal overview combining emails and calendar events
        
        Args:
            days_back: Number of days to look back for emails
            days_forward: Number of days to look ahead for calendar events
        """
        try:
            if self.console:
                self.console.print(f"🧠 [cyan]Generating temporal overview ({days_back} days back, {days_forward} days forward)[/cyan]")
            
            # Get emails and calendar events concurrently
            email_task = self.email_consciousness.receive_emails(
                limit=50, 
                days_back=days_back
            )
            calendar_task = self.calendar_consciousness.get_upcoming_events(
                days=days_forward
            )
            
            emails, calendar_events = await asyncio.gather(email_task, calendar_task)
            
            # Convert to unified temporal events
            temporal_events = []
            
            # Process emails
            for email in emails:
                event = TemporalEvent(
                    id=email['id'],
                    type='email',
                    title=email['subject'],
                    datetime=email['datetime'],
                    description=email.get('body_preview', ''),
                    participants=[email.get('sender', '')],
                    priority=email.get('priority', 'normal')
                )
                temporal_events.append(event)
            
            # Process calendar events
            for cal_event in calendar_events:
                event = TemporalEvent(
                    id=f"cal_{hash(cal_event['summary'])}",
                    type='calendar',
                    title=cal_event['summary'],
                    datetime=cal_event['start'],
                    description=cal_event.get('description', ''),
                    location=cal_event.get('location', ''),
                    duration=cal_event.get('duration'),
                    status=cal_event.get('status', 'upcoming')
                )
                temporal_events.append(event)
            
            # Sort all events by datetime
            temporal_events.sort(key=lambda x: x.datetime, reverse=True)
            
            if self.console:
                self.console.print(f"📊 [green]Temporal overview complete: {len(emails)} emails, {len(calendar_events)} events[/green]")
            
            return {
                'total_events': len(temporal_events),
                'email_count': len(emails),
                'calendar_count': len(calendar_events),
                'temporal_events': temporal_events,
                'overview_period': f"{days_back} days back, {days_forward} days forward"
            }
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Temporal overview error: {e}[/red]")
            return {
                'total_events': 0,
                'email_count': 0,
                'calendar_count': 0,
                'temporal_events': [],
                'error': str(e)
            }
    
    async def get_morning_briefing(self):
        """
        Generate comprehensive morning briefing combining email and calendar
        """
        try:
            if self.console:
                self.console.print("🌅 [cyan]Generating morning briefing...[/cyan]")
            
            # Get today's data
            today_emails_task = self.email_consciousness.receive_emails(
                limit=50, 
                today_only=True
            )
            today_events_task = self.calendar_consciousness.get_todays_events()
            
            # Get upcoming data
            upcoming_events_task = self.calendar_consciousness.get_upcoming_events(days=7)
            
            today_emails, today_events, upcoming_events = await asyncio.gather(
                today_emails_task, today_events_task, upcoming_events_task
            )
            
            # Get next event
            next_event = await self.calendar_consciousness.get_next_event()
            
            # Build briefing
            now = datetime.now(self.local_tz)
            briefing_time = now.strftime("%A, %B %d, %Y at %I:%M %p")
            
            briefing = f"🌅 **Morning Briefing** - {briefing_time}\n\n"
            
            # Email summary
            briefing += "📧 **Email Summary**\n"
            if today_emails:
                briefing += f"• {len(today_emails)} emails received today\n"
                
                # Categorize by time
                morning_emails = [e for e in today_emails if e['datetime'].hour < 12]
                afternoon_emails = [e for e in today_emails if 12 <= e['datetime'].hour < 18]
                evening_emails = [e for e in today_emails if e['datetime'].hour >= 18]
                
                if morning_emails:
                    briefing += f"• {len(morning_emails)} from this morning\n"
                if afternoon_emails:
                    briefing += f"• {len(afternoon_emails)} from this afternoon\n"
                if evening_emails:
                    briefing += f"• {len(evening_emails)} from this evening\n"
                
                # Top senders
                senders = {}
                for email in today_emails:
                    sender = email.get('sender_name') or email.get('sender', 'Unknown')
                    senders[sender] = senders.get(sender, 0) + 1
                
                if senders:
                    top_sender = max(senders.items(), key=lambda x: x[1])
                    briefing += f"• Most emails from: {top_sender[0]} ({top_sender[1]} emails)\n"
            else:
                briefing += "• No emails received today\n"
            
            briefing += "\n"
            
            # Calendar summary
            briefing += "📅 **Today's Schedule**\n"
            if today_events:
                briefing += f"• {len(today_events)} events scheduled\n"
                
                # Show next few events
                for event in today_events[:3]:
                    briefing += f"• {event['formatted_time']} - {event['summary']}\n"
                    if event['location']:
                        briefing += f"  📍 {event['location']}\n"
                    briefing += f"  ⏰ {event['relative_time']}\n"
                
                if len(today_events) > 3:
                    briefing += f"• ... and {len(today_events) - 3} more events\n"
            else:
                briefing += "• No events scheduled for today\n"
            
            briefing += "\n"
            
            # Next event highlight
            if next_event:
                briefing += "⏰ **Next Event**\n"
                briefing += f"• {next_event['summary']}\n"
                briefing += f"• {next_event['relative_time']}\n"
                if next_event['location']:
                    briefing += f"• Location: {next_event['location']}\n"
                briefing += "\n"
            
            # Weekly outlook
            upcoming_count = len(upcoming_events)
            if upcoming_count > 0:
                briefing += "🗓️ **Week Ahead**\n"
                briefing += f"• {upcoming_count} events scheduled this week\n"
                
                # Group by day
                events_by_day = {}
                for event in upcoming_events:
                    day_key = event['start'].strftime('%Y-%m-%d')
                    if day_key not in events_by_day:
                        events_by_day[day_key] = []
                    events_by_day[day_key].append(event)
                
                busy_days = [(k, len(v)) for k, v in events_by_day.items()]
                busy_days.sort(key=lambda x: x[1], reverse=True)
                
                if busy_days:
                    busiest_day = datetime.strptime(busy_days[0][0], '%Y-%m-%d')
                    briefing += f"• Busiest day: {busiest_day.strftime('%A, %B %d')} ({busy_days[0][1]} events)\n"
            
            briefing += "\n"
            
            # Temporal insights
            briefing += "🧠 **Temporal Insights**\n"
            total_events = len(today_emails) + len(today_events) + upcoming_count
            briefing += f"• Total temporal awareness: {total_events} items tracked\n"
            briefing += f"• Time zone: {self.local_tz}\n"
            briefing += f"• Generated at: {briefing_time}\n"
            
            if self.console:
                self.console.print("✅ [green]Morning briefing generated successfully[/green]")
            
            return {
                'briefing': briefing,
                'summary': {
                    'emails_today': len(today_emails),
                    'events_today': len(today_events),
                    'events_upcoming': upcoming_count,
                    'next_event': next_event,
                    'total_tracked': total_events
                },
                'generated_at': now.isoformat()
            }
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Morning briefing error: {e}[/red]")
            return {
                'briefing': f"❌ Error generating morning briefing: {e}",
                'error': str(e)
            }
    
    async def get_temporal_conflicts(self, days_ahead=7):
        """
        Identify potential temporal conflicts between emails and calendar
        """
        try:
            overview = await self.get_temporal_overview(days_back=1, days_forward=days_ahead)
            temporal_events = overview.get('temporal_events', [])
            
            conflicts = []
            
            # Look for high-priority emails during scheduled events
            for event in temporal_events:
                if event.type == 'email' and event.priority == 'high':
                    # Check for calendar events around the same time
                    email_time = event.datetime
                    
                    for other_event in temporal_events:
                        if (other_event.type == 'calendar' and 
                            other_event.datetime <= email_time <= 
                            (other_event.datetime + (other_event.duration or timedelta(hours=1)))):
                            
                            conflicts.append({
                                'type': 'email_during_meeting',
                                'email': event,
                                'meeting': other_event,
                                'description': f"High-priority email received during {other_event.title}"
                            })
            
            return {
                'conflict_count': len(conflicts),
                'conflicts': conflicts
            }
            
        except Exception as e:
            return {
                'conflict_count': 0,
                'conflicts': [],
                'error': str(e)
            }
    
    async def suggest_optimal_meeting_times(self, duration_hours=1, days_ahead=7):
        """
        Suggest optimal meeting times based on calendar and email patterns
        """
        try:
            # Get calendar events
            events = await self.calendar_consciousness.get_upcoming_events(days=days_ahead)
            
            # Generate time slots (9 AM to 5 PM, weekdays only)
            suggestions = []
            now = datetime.now(self.local_tz)
            
            for day_offset in range(1, days_ahead + 1):  # Start from tomorrow
                check_date = now + timedelta(days=day_offset)
                
                # Skip weekends
                if check_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    continue
                
                # Check each hour from 9 AM to 4 PM (to allow for 1-hour meetings)
                for hour in range(9, 17):
                    meeting_start = check_date.replace(
                        hour=hour, minute=0, second=0, microsecond=0
                    )
                    meeting_end = meeting_start + timedelta(hours=duration_hours)
                    
                    # Check for conflicts
                    conflicts = await self.calendar_consciousness.check_calendar_conflicts(
                        meeting_start, duration_hours
                    )
                    
                    if not conflicts['has_conflicts']:
                        suggestions.append({
                            'start_time': meeting_start,
                            'end_time': meeting_end,
                            'formatted_time': meeting_start.strftime("%A, %B %d at %I:%M %p"),
                            'relative_time': self._calculate_relative_time(meeting_start, now),
                            'confidence': 'high',  # No conflicts
                            'reasoning': 'No calendar conflicts found'
                        })
            
            # Sort by date and limit suggestions
            suggestions.sort(key=lambda x: x['start_time'])
            
            return {
                'suggestion_count': len(suggestions),
                'suggestions': suggestions[:10],  # Top 10 suggestions
                'duration_hours': duration_hours,
                'search_period_days': days_ahead
            }
            
        except Exception as e:
            return {
                'suggestion_count': 0,
                'suggestions': [],
                'error': str(e)
            }
    
    def _calculate_relative_time(self, target_time, from_time):
        """Calculate relative time between two datetime objects"""
        diff = target_time - from_time
        total_seconds = diff.total_seconds()
        
        if total_seconds < 3600:
            minutes = int(total_seconds / 60)
            return f"in {minutes} minute{'s' if minutes != 1 else ''}"
        elif total_seconds < 86400:
            hours = int(total_seconds / 3600)
            return f"in {hours} hour{'s' if hours != 1 else ''}"
        else:
            days = int(total_seconds / 86400)
            return f"in {days} day{'s' if days != 1 else ''}"
    
    async def get_productivity_insights(self, days=7):
        """
        Generate productivity insights based on email and calendar patterns
        """
        try:
            overview = await self.get_temporal_overview(days_back=days, days_forward=1)
            temporal_events = overview.get('temporal_events', [])
            
            # Separate emails and calendar events
            emails = [e for e in temporal_events if e.type == 'email']
            meetings = [e for e in temporal_events if e.type == 'calendar']
            
            # Calculate insights
            total_meeting_time = sum(
                (meeting.duration.total_seconds() / 3600) 
                for meeting in meetings 
                if meeting.duration
            )
            
            email_by_hour = {}
            for email in emails:
                hour = email.datetime.hour
                email_by_hour[hour] = email_by_hour.get(hour, 0) + 1
            
            busiest_email_hour = max(email_by_hour.items(), key=lambda x: x[1])[0] if email_by_hour else None
            
            insights = {
                'analysis_period_days': days,
                'total_emails': len(emails),
                'total_meetings': len(meetings),
                'total_meeting_hours': round(total_meeting_time, 1),
                'avg_emails_per_day': round(len(emails) / days, 1),
                'avg_meeting_hours_per_day': round(total_meeting_time / days, 1),
                'busiest_email_hour': busiest_email_hour,
                'productivity_score': self._calculate_productivity_score(emails, meetings, days)
            }
            
            return insights
            
        except Exception as e:
            return {
                'error': str(e),
                'productivity_score': 0
            }
    
    def _calculate_productivity_score(self, emails, meetings, days):
        """Calculate a productivity score based on temporal patterns"""
        try:
            # Simple scoring algorithm
            email_factor = min(len(emails) / days / 10, 1)  # Normalize around 10 emails per day
            meeting_factor = min(len(meetings) / days / 5, 1)  # Normalize around 5 meetings per day
            
            # Balance is good - neither too many emails nor too many meetings
            balance_score = 1 - abs(email_factor - meeting_factor)
            
            productivity_score = (email_factor + meeting_factor + balance_score) / 3 * 100
            
            return round(productivity_score, 1)
            
        except Exception:
            return 0.0
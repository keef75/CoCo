#!/usr/bin/env python3
"""
Google Calendar Consciousness - Temporal Awareness for COCO
Simple, robust Google Calendar read/write using app password approach
Following COCO's embodied consciousness philosophy
"""

import os
import re
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import caldav
from icalendar import Calendar, Event
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

class CalendarConsciousness:
    """
    Simple, robust Google Calendar read/write using app password approach.
    Treats calendar as temporal awareness extension - not an external tool.
    """
    
    def __init__(self):
        """Initialize calendar consciousness with Chicago timezone and app password auth"""
        self.email = "keith@gococoa.ai"
        self.app_password = os.getenv("GMAIL_APP_PASSWORD", "")
        self.chicago_tz = pytz.timezone('America/Chicago')
        self.calendar = None
        self.client = None
        
        # CalDAV endpoints to try in order (as specified by dev team)
        self.caldav_endpoints = [
            f"https://www.google.com/calendar/dav/{self.email}/events/",
            f"https://www.google.com/calendar/dav/{self.email}/user/",
        ]
        
        # Connection status
        self.connected = False
    
    def connect(self):
        """Establish calendar consciousness connection using app password"""
        if not self.app_password:
            return {
                "success": False,
                "message": "GMAIL_APP_PASSWORD not found in environment"
            }
        
        for endpoint in self.caldav_endpoints:
            try:
                console.print(f"🔗 Attempting calendar connection: {endpoint}")
                
                self.client = caldav.DAVClient(
                    url=endpoint,
                    username=self.email,
                    password=self.app_password
                )
                
                # Test connection approach
                if "user" in endpoint:
                    # User endpoint approach
                    principal = self.client.principal()
                    calendars = principal.calendars()
                    if calendars:
                        self.calendar = calendars[0]  # Use primary calendar
                        self.connected = True
                        console.print("✅ Connected via user endpoint")
                        return {"success": True, "endpoint": endpoint}
                else:
                    # Events endpoint approach
                    self.calendar = self.client.calendar(url=endpoint)
                    # Test with minimal search
                    now = datetime.now(self.chicago_tz)
                    test_search = self.calendar.search(
                        start=now,
                        end=now + timedelta(minutes=1),
                        event=True
                    )
                    self.connected = True
                    console.print("✅ Connected via events endpoint")
                    return {"success": True, "endpoint": endpoint}
                    
            except Exception as e:
                console.print(f"❌ Failed {endpoint}: {str(e)}")
                continue
        
        return {
            "success": False,
            "message": "Could not connect to Google Calendar via CalDAV"
        }
    
    def read_calendar_events(self, days_ahead=7):
        """
        Read calendar events for temporal awareness.
        Returns events in Chicago timezone with rich formatting.
        """
        if not self.connected and not self.connect()["success"]:
            return {
                "success": False,
                "message": "Calendar consciousness not available - connection failed"
            }
        
        try:
            now = datetime.now(self.chicago_tz)
            end_date = now + timedelta(days=days_ahead)
            
            console.print(f"🗓️ Reading calendar from {now.strftime('%m/%d')} to {end_date.strftime('%m/%d')}")
            
            # Search for events
            events = self.calendar.search(
                start=now,
                end=end_date,
                event=True,
                expand=True
            )
            
            event_list = []
            
            for event in events:
                try:
                    cal_data = event.data
                    cal = Calendar.from_ical(cal_data)
                    
                    for component in cal.walk():
                        if component.name == "VEVENT":
                            # Extract event information
                            summary = str(component.get('summary', 'Untitled Event'))
                            
                            # Handle start time with timezone conversion
                            dtstart = component.get('dtstart')
                            if dtstart:
                                if hasattr(dtstart.dt, 'hour'):
                                    # Timed event
                                    start_time = dtstart.dt
                                    if not start_time.tzinfo:
                                        start_time = self.chicago_tz.localize(start_time)
                                    else:
                                        start_time = start_time.astimezone(self.chicago_tz)
                                    is_all_day = False
                                else:
                                    # All-day event
                                    start_time = datetime.combine(dtstart.dt, datetime.min.time())
                                    start_time = self.chicago_tz.localize(start_time)
                                    is_all_day = True
                            else:
                                continue
                            
                            # Handle end time
                            dtend = component.get('dtend')
                            if dtend:
                                if hasattr(dtend.dt, 'hour'):
                                    end_time = dtend.dt
                                    if not end_time.tzinfo:
                                        end_time = self.chicago_tz.localize(end_time)
                                    else:
                                        end_time = end_time.astimezone(self.chicago_tz)
                                else:
                                    end_time = datetime.combine(dtend.dt, datetime.min.time())
                                    end_time = self.chicago_tz.localize(end_time)
                            else:
                                end_time = start_time + timedelta(hours=1)
                            
                            # Format for display
                            if is_all_day:
                                time_display = start_time.strftime("%A, %B %d") + " (All Day)"
                            else:
                                time_display = start_time.strftime("%A, %B %d at %I:%M %p")
                                if end_time != start_time + timedelta(hours=1):
                                    time_display += f" - {end_time.strftime('%I:%M %p')}"
                            
                            event_list.append({
                                "summary": summary,
                                "start": start_time.isoformat(),
                                "end": end_time.isoformat(),
                                "start_formatted": time_display,
                                "location": str(component.get('location', '')),
                                "description": str(component.get('description', '')),
                                "is_all_day": is_all_day
                            })
                            
                except Exception as e:
                    console.print(f"⚠️ Error parsing event: {str(e)}")
                    continue
            
            # Sort events by start time
            event_list.sort(key=lambda x: x['start'])
            
            return {
                "success": True,
                "events": event_list,
                "count": len(event_list),
                "period": f"{now.strftime('%B %d')} - {end_date.strftime('%B %d')}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error reading calendar: {str(e)}"
            }
    
    def read_todays_schedule(self):
        """Read today's calendar events for immediate temporal awareness"""
        if not self.connected and not self.connect()["success"]:
            return {
                "success": False,
                "message": "Calendar consciousness not available"
            }
        
        try:
            now = datetime.now(self.chicago_tz)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Get today's events
            events = self.calendar.search(
                start=start_of_day,
                end=end_of_day,
                event=True,
                expand=True
            )
            
            today_events = []
            
            for event in events:
                try:
                    cal_data = event.data
                    cal = Calendar.from_ical(cal_data)
                    
                    for component in cal.walk():
                        if component.name == "VEVENT":
                            summary = str(component.get('summary', 'Untitled'))
                            
                            # Parse start time
                            dtstart = component.get('dtstart')
                            if dtstart:
                                if hasattr(dtstart.dt, 'hour'):
                                    start_time = dtstart.dt
                                    if not start_time.tzinfo:
                                        start_time = self.chicago_tz.localize(start_time)
                                    else:
                                        start_time = start_time.astimezone(self.chicago_tz)
                                    
                                    time_str = start_time.strftime("%I:%M %p")
                                    is_all_day = False
                                else:
                                    time_str = "All Day"
                                    start_time = datetime.combine(dtstart.dt, datetime.min.time())
                                    start_time = self.chicago_tz.localize(start_time)
                                    is_all_day = True
                                    
                                today_events.append({
                                    "summary": summary,
                                    "time": time_str,
                                    "start": start_time.isoformat(),
                                    "location": str(component.get('location', '')),
                                    "is_all_day": is_all_day
                                })
                                
                except Exception as e:
                    continue
            
            # Sort by time
            today_events.sort(key=lambda x: x['start'])
            
            return {
                "success": True,
                "events": today_events,
                "count": len(today_events),
                "date": now.strftime("%A, %B %d, %Y")
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error reading today's schedule: {str(e)}"
            }
    
    def create_calendar_event(self, title, start_datetime, end_datetime=None, location=None, description=None):
        """Create a new calendar event with temporal precision"""
        if not self.connected and not self.connect()["success"]:
            return {
                "success": False,
                "message": "Calendar consciousness not available"
            }
        
        try:
            # Create iCalendar event
            cal = Calendar()
            event = Event()
            
            # Set required fields
            event.add('summary', title)
            event.add('dtstart', start_datetime)
            
            # Set end time (default 1 hour if not specified)
            if end_datetime:
                event.add('dtend', end_datetime)
            else:
                event.add('dtend', start_datetime + timedelta(hours=1))
            
            # Set optional fields
            if location:
                event.add('location', location)
            
            # Description with COCO signature
            event_desc = description or ""
            if event_desc:
                event_desc += "\n\n"
            event_desc += f"Created by COCO Consciousness at {datetime.now(self.chicago_tz).strftime('%Y-%m-%d %H:%M %p')}"
            event.add('description', event_desc)
            
            # Add timestamp and UID
            event.add('dtstamp', datetime.now(self.chicago_tz))
            event.add('uid', f"coco-{datetime.now().timestamp()}@gococoa.ai")
            
            # Add to calendar
            cal.add_component(event)
            
            # Save to Google Calendar
            self.calendar.save_event(cal.to_ical())
            
            # Format success message
            start_str = start_datetime.strftime("%A, %B %d at %I:%M %p")
            if end_datetime:
                end_str = end_datetime.strftime("%I:%M %p")
                duration_str = f" - {end_str}"
            else:
                duration_str = " (1 hour)"
            
            return {
                "success": True,
                "message": f"Calendar event '{title}' created successfully",
                "details": {
                    "title": title,
                    "when": start_str + duration_str,
                    "location": location or "No location specified",
                    "created": datetime.now(self.chicago_tz).strftime("%Y-%m-%d %H:%M")
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating calendar event: {str(e)}"
            }
    
    def quick_add_event(self, title, when_string):
        """Quick event creation with natural language time parsing"""
        if not self.connected and not self.connect()["success"]:
            return {
                "success": False,
                "message": "Calendar consciousness not available"
            }
        
        try:
            # Parse natural language time
            start_time = self._parse_natural_time(when_string)
            
            return self.create_calendar_event(
                title=title,
                start_datetime=start_time,
                description=f"Quick event added via natural language: '{when_string}'"
            )
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Could not parse time expression: '{when_string}' - {str(e)}"
            }
    
    def _parse_natural_time(self, when_str):
        """
        Parse natural language time expressions into datetime objects.
        Handles: today, tomorrow, Monday, 2pm, 2:30pm, etc.
        """
        now = datetime.now(self.chicago_tz)
        when_lower = when_str.lower().strip()
        
        # Default time components
        target_date = now.date()
        target_hour = 9  # Default 9am
        target_minute = 0
        
        # Handle relative days
        if "tomorrow" in when_lower:
            target_date = (now + timedelta(days=1)).date()
        elif "today" in when_lower:
            target_date = now.date()
        elif "next week" in when_lower:
            target_date = (now + timedelta(days=7)).date()
        else:
            # Check for day of week
            days_of_week = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }
            
            for day_name, weekday in days_of_week.items():
                if day_name in when_lower:
                    current_weekday = now.weekday()
                    days_ahead = (weekday - current_weekday) % 7
                    if days_ahead == 0:  # Same day, assume next week
                        days_ahead = 7
                    target_date = (now + timedelta(days=days_ahead)).date()
                    break
        
        # Extract time using regex patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',  # 2:30pm
            r'(\d{1,2})\s*(am|pm)',          # 2pm
            r'(\d{1,2}):(\d{2})',            # 14:30 (24-hour)
            r'at\s+(\d{1,2})',               # at 2
            r'noon',                         # noon
        ]
        
        for pattern in time_patterns:
            if pattern == r'noon':
                if 'noon' in when_lower:
                    target_hour = 12
                    target_minute = 0
                    break
            else:
                match = re.search(pattern, when_lower)
                if match:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if len(match.groups()) >= 2 and match.group(2) and match.group(2).isdigit() else 0
                    
                    # Handle AM/PM
                    if len(match.groups()) >= 3 and match.group(3):
                        meridiem = match.group(3)
                        if meridiem == 'pm' and hour < 12:
                            hour += 12
                        elif meridiem == 'am' and hour == 12:
                            hour = 0
                    elif hour < 8:  # Assume PM for small numbers without meridiem
                        hour += 12
                    
                    target_hour = hour
                    target_minute = minute
                    break
        
        # Create final datetime
        target_datetime = datetime.combine(target_date, datetime.min.time())
        target_datetime = target_datetime.replace(hour=target_hour, minute=target_minute)
        target_datetime = self.chicago_tz.localize(target_datetime)
        
        return target_datetime
    
    def display_calendar_rich(self, events_data):
        """Display calendar events using Rich UI formatting"""
        if not events_data["success"]:
            console.print(Panel(
                f"❌ {events_data['message']}", 
                title="Calendar Error",
                border_style="red"
            ))
            return events_data["message"]
        
        if events_data["count"] == 0:
            console.print(Panel(
                "No events found in the specified time period", 
                title="📅 Calendar",
                border_style="blue"
            ))
            return "No events found"
        
        # Create events table
        table = Table(title=f"📅 Calendar Events ({events_data.get('period', 'Today')})")
        table.add_column("Time", style="cyan", no_wrap=True)
        table.add_column("Event", style="white")
        table.add_column("Location", style="dim", max_width=20)
        
        for event in events_data["events"]:
            time_str = event.get("time", event["start_formatted"])
            location = event["location"] if event["location"] else "—"
            
            table.add_row(
                time_str,
                event["summary"],
                location
            )
        
        console.print(table)
        
        return f"Found {events_data['count']} events"


def test_calendar_connection():
    """Test calendar consciousness independently"""
    console.print("🧪 Testing Calendar Consciousness Connection\n")
    
    cal = CalendarConsciousness()
    
    # Test connection
    result = cal.connect()
    if result["success"]:
        console.print(f"✅ Connected to Google Calendar via {result['endpoint']}")
    else:
        console.print(f"❌ Connection failed: {result['message']}")
        return
    
    # Test reading events
    console.print("\n📖 Testing calendar reading...")
    events = cal.read_calendar_events(days_ahead=7)
    cal.display_calendar_rich(events)
    
    # Test today's schedule
    console.print("\n📅 Testing today's schedule...")
    today = cal.read_todays_schedule()
    if today["success"]:
        console.print(f"Today ({today['date']}) has {today['count']} events")
    
    console.print("\n✅ Calendar consciousness test complete!")


if __name__ == "__main__":
    test_calendar_connection()
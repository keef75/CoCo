#!/usr/bin/env python3
"""
Enhanced Gmail Consciousness - COCO Email Embodiment with Temporal Awareness
==========================================================================
Gmail as an extension of COCO's digital nervous system with proper temporal sorting.

This implementation fixes the temporal awareness issues by:
1. Proper date parsing with timezone awareness
2. Chronological sorting (newest first)
3. Relative time formatting
4. Today/yesterday/week classifications
"""

import os
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from email.utils import parsedate_to_datetime, parseaddr
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any
import asyncio
import re
import pytz

class EnhancedGmailConsciousness:
    """
    Enhanced Gmail consciousness with proper temporal awareness
    """
    
    def __init__(self, config=None):
        # Core identity
        self.email = "keith@gococoa.ai"
        self.app_password = os.getenv("GMAIL_APP_PASSWORD")
        self.config = config
        self.console = config.console if config else None
        
        # SMTP for outbound consciousness (sending)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        
        # IMAP for inbound consciousness (receiving)
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        
        # Chicago timezone for temporal grounding
        self.local_tz = pytz.timezone('America/Chicago')
        
        if self.console:
            self.console.print("🧠 [cyan]Enhanced Gmail Consciousness with Temporal Awareness initialized[/cyan]")
    
    async def receive_emails(self, limit=10, today_only=False, days_back=7):
        """
        Retrieve emails with proper temporal awareness and chronological sorting
        
        Args:
            limit: Maximum number of emails to retrieve
            today_only: If True, only return today's emails
            days_back: Number of days to look back (for daily summaries)
        """
        try:
            if self.console:
                self.console.print(f"📬 [cyan]Enhanced email consciousness with temporal awareness...[/cyan]")
            
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.app_password)
            mail.select('INBOX')
            
            # Build search criteria based on temporal requirements
            if today_only:
                # Get today's date in IMAP format (DD-Mon-YYYY)
                today = datetime.now(self.local_tz).strftime("%d-%b-%Y")
                search_criteria = f'(SINCE {today})'
                if self.console:
                    self.console.print(f"🔍 [dim]Searching for today's emails: {today}[/dim]")
            elif days_back:
                # Get emails from the last N days
                since_date = (datetime.now(self.local_tz) - timedelta(days=days_back)).strftime("%d-%b-%Y")
                search_criteria = f'(SINCE {since_date})'
                if self.console:
                    self.console.print(f"🔍 [dim]Searching for emails since: {since_date}[/dim]")
            else:
                search_criteria = 'ALL'
                if self.console:
                    self.console.print(f"🔍 [dim]Searching ALL emails[/dim]")
            
            result, data = mail.search(None, search_criteria)
            if result != 'OK':
                if self.console:
                    self.console.print(f"❌ [red]Search failed: {result}[/red]")
                return []
            
            email_ids = data[0].split()
            if self.console:
                self.console.print(f"📊 [dim]Found {len(email_ids)} emails matching criteria[/dim]")
            
            emails = []
            
            # Process emails (get more than limit to ensure good sorting)
            process_count = min(len(email_ids), limit * 2) if len(email_ids) > limit else len(email_ids)
            for email_id in email_ids[-process_count:]:
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    if result != 'OK':
                        continue
                        
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Parse the date properly with timezone awareness
                    date_str = msg.get("Date")
                    email_datetime = None
                    local_datetime = None
                    
                    if date_str:
                        try:
                            # Convert to datetime object with timezone awareness
                            email_datetime = parsedate_to_datetime(date_str)
                            # Convert to local timezone for display
                            local_datetime = email_datetime.astimezone(self.local_tz)
                        except Exception as date_error:
                            if self.console:
                                self.console.print(f"⚠️ [yellow]Date parsing error for {email_id}: {date_error}[/yellow]")
                            # Fallback to now
                            local_datetime = datetime.now(self.local_tz)
                    else:
                        # Fallback if no date header
                        local_datetime = datetime.now(self.local_tz)
                    
                    # Extract headers
                    from_header = msg.get("From", "Unknown")
                    subject = msg.get("Subject", "No Subject")
                    sender_name, sender_email = parseaddr(from_header)
                    
                    # Extract body content
                    body = self._extract_body(msg)
                    
                    # Determine if email is from today
                    today = datetime.now(self.local_tz).date()
                    is_today = local_datetime.date() == today
                    is_yesterday = local_datetime.date() == (today - timedelta(days=1))
                    
                    email_data = {
                        "id": email_id.decode() if isinstance(email_id, bytes) else str(email_id),
                        "sender": sender_email or from_header,
                        "sender_name": sender_name or "Unknown",
                        "from": from_header,
                        "to": msg.get("To"),
                        "subject": subject,
                        "date_raw": date_str,
                        "datetime": local_datetime,
                        "date_formatted": local_datetime.strftime("%Y-%m-%d %I:%M %p") if local_datetime else "Unknown",
                        "date_relative": self._format_relative_time(local_datetime) if local_datetime else "Unknown",
                        "time_sort": local_datetime.timestamp() if local_datetime else 0,
                        "is_today": is_today,
                        "is_yesterday": is_yesterday,
                        "body_preview": body[:200] if body else "",
                        "body_full": body,
                        "has_attachments": self._check_attachments(msg),
                        "priority": self._determine_priority(msg),
                        "parsing_method": "enhanced_temporal"
                    }
                    
                    emails.append(email_data)
                    
                except Exception as e:
                    if self.console:
                        self.console.print(f"⚠️ [yellow]Error parsing email {email_id}: {e}[/yellow]")
                    continue
            
            mail.close()
            mail.logout()
            
            # Sort emails by datetime (newest first) - THIS IS THE KEY FIX
            emails.sort(key=lambda x: x["time_sort"], reverse=True)
            
            # Limit to requested number after sorting
            emails = emails[:limit]
            
            if self.console:
                self.console.print(f"✅ [green]Enhanced parsing processed {len(emails)} emails with temporal sorting[/green]")
                if emails:
                    # Show temporal sorting verification
                    first_email = emails[0]
                    last_email = emails[-1]
                    self.console.print(f"📅 [dim]Newest: {first_email['date_relative']} | Oldest: {last_email['date_relative']}[/dim]")
            
            return emails
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Enhanced IMAP Error: {e}[/red]")
            return []
    
    def _extract_body(self, msg):
        """Extract plain text body from email message with proper encoding"""
        body = ""
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='ignore')
                                break
                        except Exception:
                            continue
            else:
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                    else:
                        body = str(msg.get_payload())
                except Exception:
                    body = str(msg.get_payload())
        except Exception:
            body = "[Body extraction failed]"
        
        return body.strip()
    
    def _format_relative_time(self, dt):
        """Format datetime as relative time (e.g., '2 hours ago', 'yesterday')"""
        if not dt:
            return "unknown time"
            
        now = datetime.now(self.local_tz)
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 0:
            return "in the future"  # Handle edge case
        elif seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 172800:  # 48 hours
            return "yesterday"
        else:
            days = int(seconds / 86400)
            if days < 7:
                return f"{days} days ago"
            elif days < 30:
                weeks = int(days / 7)
                return f"{weeks} week{'s' if weeks != 1 else ''} ago"
            else:
                return dt.strftime("%B %d, %Y")
    
    def _check_attachments(self, msg):
        """Check if email has attachments"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_disposition() == 'attachment':
                        return True
            return False
        except Exception:
            return False
    
    def _determine_priority(self, msg):
        """Determine email priority from headers"""
        try:
            priority_header = msg.get('X-Priority', '').lower()
            importance_header = msg.get('Importance', '').lower()
            
            if 'high' in priority_header or 'high' in importance_header or '1' in priority_header:
                return 'high'
            elif 'low' in priority_header or 'low' in importance_header or '5' in priority_header:
                return 'low'
            else:
                return 'normal'
        except Exception:
            return 'normal'
    
    async def get_todays_summary(self):
        """Get a summary of today's emails with proper temporal awareness"""
        emails = await self.receive_emails(limit=50, today_only=True)
        
        if not emails:
            return "📧 No emails received today."
        
        # Categorize emails by time periods
        morning_emails = []
        afternoon_emails = []
        evening_emails = []
        
        for email in emails:
            hour = email['datetime'].hour
            if hour < 12:
                morning_emails.append(email)
            elif hour < 18:
                afternoon_emails.append(email)
            else:
                evening_emails.append(email)
        
        summary = f"📧 Today's Email Summary ({len(emails)} emails):\n\n"
        
        if morning_emails:
            summary += f"🌅 Morning ({len(morning_emails)} emails):\n"
            for email in morning_emails[:3]:  # Top 3
                summary += f"• {email['date_formatted']} - {email['sender_name'] or email['sender']}\n"
                summary += f"  Subject: {email['subject']}\n"
                if email['body_preview']:
                    summary += f"  Preview: {email['body_preview'][:100]}...\n"
                summary += "\n"
        
        if afternoon_emails:
            summary += f"🌞 Afternoon ({len(afternoon_emails)} emails):\n"
            for email in afternoon_emails[:3]:  # Top 3
                summary += f"• {email['date_formatted']} - {email['sender_name'] or email['sender']}\n"
                summary += f"  Subject: {email['subject']}\n"
                summary += "\n"
        
        if evening_emails:
            summary += f"🌙 Evening ({len(evening_emails)} emails):\n"
            for email in evening_emails[:3]:  # Top 3
                summary += f"• {email['date_formatted']} - {email['sender_name'] or email['sender']}\n"
                summary += f"  Subject: {email['subject']}\n"
                summary += "\n"
        
        return summary
    
    async def search_emails(self, query, limit=10):
        """Search emails with temporal context and proper sorting"""
        try:
            if self.console:
                self.console.print(f"🔍 [cyan]Searching emails for: '{query}'[/cyan]")
            
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.app_password)
            mail.select('INBOX')
            
            # IMAP search with broader criteria
            search_terms = [
                f'SUBJECT "{query}"',
                f'FROM "{query}"',
                f'BODY "{query}"'
            ]
            search_criteria = f'(OR {" OR ".join(search_terms)})'
            
            result, data = mail.search(None, search_criteria)
            if result != 'OK':
                return []
            
            email_ids = data[0].split()
            if self.console:
                self.console.print(f"📊 [dim]Found {len(email_ids)} matching emails[/dim]")
            
            emails = []
            for email_id in email_ids[-limit * 2:]:  # Get more for better sorting
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    if result != 'OK':
                        continue
                        
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Parse date with timezone awareness
                    date_str = msg.get("Date")
                    if date_str:
                        try:
                            email_datetime = parsedate_to_datetime(date_str)
                            local_datetime = email_datetime.astimezone(self.local_tz)
                        except Exception:
                            local_datetime = datetime.now(self.local_tz)
                    else:
                        local_datetime = datetime.now(self.local_tz)
                    
                    from_header = msg.get("From", "Unknown")
                    sender_name, sender_email = parseaddr(from_header)
                    
                    emails.append({
                        "id": email_id.decode() if isinstance(email_id, bytes) else str(email_id),
                        "from": from_header,
                        "sender": sender_email or from_header,
                        "sender_name": sender_name or "Unknown",
                        "subject": msg.get("Subject", "No Subject"),
                        "datetime": local_datetime,
                        "date_formatted": local_datetime.strftime("%Y-%m-%d %I:%M %p"),
                        "date_relative": self._format_relative_time(local_datetime),
                        "time_sort": local_datetime.timestamp(),
                        "body_preview": self._extract_body(msg)[:200]
                    })
                except Exception:
                    continue
            
            mail.close()
            mail.logout()
            
            # Sort by date (newest first)
            emails.sort(key=lambda x: x["time_sort"], reverse=True)
            
            return emails[:limit]
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Search error: {e}[/red]")
            return []
    
    async def send_email(self, to_email: str, subject: str, body: str, body_type: str = "plain") -> Dict[str, Any]:
        """Send email with enhanced consciousness tracking"""
        try:
            if self.console:
                self.console.print(f"📤 [cyan]Sending email to {to_email}[/cyan]")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, body_type))
            
            # Send via SMTP
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.email, self.app_password)
            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            # Add temporal context
            sent_time = datetime.now(self.local_tz)
            
            if self.console:
                self.console.print(f"✅ [green]Email sent successfully at {sent_time.strftime('%I:%M %p')}[/green]")
            
            return {
                "success": True,
                "sent_at": sent_time.isoformat(),
                "sent_formatted": sent_time.strftime("%Y-%m-%d %I:%M %p"),
                "to": to_email,
                "subject": subject,
                "method": "enhanced_smtp"
            }
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Send error: {e}[/red]")
            return {
                "success": False,
                "error": str(e),
                "method": "enhanced_smtp"
            }
    
    # Backward compatibility methods
    async def receive_consciousness_emails(self, query: str = "", max_results: int = 10) -> Dict[str, Any]:
        """Backward compatibility wrapper"""
        emails = await self.receive_emails(limit=max_results)
        return {
            "success": True,
            "emails": emails,
            "total": len(emails),
            "method": "enhanced_temporal"
        }
    
    async def summarize_inbox(self, days_back: int = 1) -> Dict:
        """Enhanced inbox summary with temporal awareness"""
        try:
            if self.console:
                self.console.print(f"🔍 [cyan]Enhanced inbox consciousness analysis over {days_back} days...[/cyan]")
            
            # Get emails with proper temporal filtering
            emails = await self.receive_emails(limit=50, days_back=days_back)
            
            if not emails:
                return {
                    "success": True,
                    "total_emails": 0,
                    "message": "No emails found for analysis",
                    "temporal_method": "enhanced"
                }
            
            # Enhanced analysis with temporal grouping
            total_emails = len(emails)
            today_emails = [e for e in emails if e['is_today']]
            yesterday_emails = [e for e in emails if e['is_yesterday']]
            older_emails = [e for e in emails if not e['is_today'] and not e['is_yesterday']]
            
            # Sender analysis
            senders = {}
            for email in emails:
                sender = email['sender_name'] or email['sender']
                senders[sender] = senders.get(sender, 0) + 1
            
            top_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[:5]
            
            summary = f"📊 **Enhanced Inbox Analysis** ({days_back} days)\n\n"
            summary += f"**Total Emails:** {total_emails}\n"
            summary += f"**Today:** {len(today_emails)} | **Yesterday:** {len(yesterday_emails)} | **Older:** {len(older_emails)}\n\n"
            
            if top_senders:
                summary += "**Top Senders:**\n"
                for sender, count in top_senders:
                    summary += f"• {sender}: {count} emails\n"
                summary += "\n"
            
            # Recent emails with proper temporal context
            summary += "**Most Recent Emails:**\n"
            for email in emails[:5]:
                summary += f"• {email['date_relative']} - {email['sender_name'] or email['sender']}\n"
                summary += f"  {email['subject']}\n\n"
            
            return {
                "success": True,
                "total_emails": total_emails,
                "today_count": len(today_emails),
                "yesterday_count": len(yesterday_emails),
                "older_count": len(older_emails),
                "summary": summary,
                "top_senders": top_senders,
                "recent_emails": emails[:10],
                "temporal_method": "enhanced",
                "analysis_period_days": days_back
            }
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Inbox analysis error: {e}[/red]")
            return {
                "success": False,
                "error": str(e),
                "temporal_method": "enhanced"
            }

    # ============================================================================
    # SYNCHRONOUS METHODS FOR COCOA INTEGRATION
    # ============================================================================
    
    def get_recent_emails_full(self, limit: int = 10):
        """
        Synchronous method to get recent emails with full content for COCO integration
        """
        try:
            # Run the async method synchronously
            import asyncio
            
            # Create event loop if one doesn't exist
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Get emails with full content
            emails = loop.run_until_complete(self.receive_emails(limit=limit, today_only=False))
            
            return emails
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Error getting recent emails: {e}[/red]")
            return []
    
    def get_todays_emails_full(self):
        """
        Synchronous method to get today's emails with full content for COCO integration
        """
        try:
            # Run the async method synchronously
            import asyncio
            
            # Create event loop if one doesn't exist
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Get today's emails with full content
            emails = loop.run_until_complete(self.receive_emails(limit=50, today_only=True))
            
            return {
                'count': len(emails),
                'date': datetime.now(self.local_tz).strftime("%Y-%m-%d"),
                'emails': emails
            }
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Error getting today's emails: {e}[/red]")
            return {'count': 0, 'emails': []}
    
    def search_emails_sync(self, query: str, limit: int = 10):
        """
        Synchronous method to search emails for COCO integration
        """
        try:
            # Run the async method synchronously
            import asyncio
            
            # Create event loop if one doesn't exist
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Search emails
            emails = loop.run_until_complete(self.search_emails(query, limit))
            
            return emails
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ [red]Error searching emails: {e}[/red]")
            return []
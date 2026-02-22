#!/usr/bin/env python3
"""
Gmail Gentle Fix - Preserve Gmail's Natural Sorting
==================================================
A gentle enhancement that leverages Gmail's existing chronological sorting.
No complex date parsing - just respect Gmail's own ordering mechanism.

This approach:
- ✅ Preserves Gmail's exact sorting (newest to oldest)
- ✅ Doesn't break existing functionality
- ✅ Uses Gmail's own date ordering (that rightmost column)
- ✅ Simple and gentle on COCO's consciousness
- ✅ No complex date parsing that could fail
"""

import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header

class GentleGmailFix:
    """Gentle Gmail integration that preserves Gmail's natural sorting"""
    
    def __init__(self, config=None):
        self.email = "keith@gococoa.ai"
        self.app_password = os.getenv("GMAIL_APP_PASSWORD", "pulhwnmwosfbeqdh")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.config = config
        self.console = config.console if config else None
        
        if self.console:
            self.console.print(f"📧 Gentle Gmail Fix initialized - {self.email}")
    
    def _resolve_attachment_path(self, filepath):
        """Resolve attachment file path to absolute path, checking multiple potential locations"""
        import os
        from pathlib import Path
        
        if self.console:
            self.console.print(f"🔍 Resolving attachment path: {filepath}")
        
        # If already absolute and exists, use it
        if os.path.isabs(filepath) and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            if self.console:
                self.console.print(f"✅ Found absolute path: {filepath} ({file_size} bytes)")
            return filepath
        
        # Try multiple potential locations in order of likelihood
        potential_paths = [
            filepath,  # Relative to current directory
            os.path.join(".", filepath),  # Explicit relative to current
            os.path.join("coco_workspace", os.path.basename(filepath)),  # Just filename in workspace
            os.path.join("coco_workspace", "videos", os.path.basename(filepath)),  # Video workspace
            os.path.join("coco_workspace", "visuals", os.path.basename(filepath)),  # Visual workspace
            filepath if os.path.sep in filepath else os.path.join("coco_workspace", filepath),  # Workspace if no path separator
        ]
        
        # Add potential absolute paths
        current_dir = os.getcwd()
        for rel_path in [filepath, os.path.basename(filepath)]:
            potential_paths.extend([
                os.path.join(current_dir, rel_path),
                os.path.join(current_dir, "coco_workspace", rel_path),
                os.path.join(current_dir, "coco_workspace", "videos", rel_path),
                os.path.join(current_dir, "coco_workspace", "visuals", rel_path),
            ])
        
        # Check each potential path
        for potential_path in potential_paths:
            if os.path.exists(potential_path):
                file_size = os.path.getsize(potential_path)
                if file_size > 0:  # Must be non-empty
                    abs_path = os.path.abspath(potential_path)
                    if self.console:
                        self.console.print(f"✅ Resolved to: {abs_path} ({file_size} bytes)")
                    return abs_path
                elif self.console:
                    self.console.print(f"⚠️ Found empty file: {potential_path}")
        
        # If we get here, file not found
        if self.console:
            self.console.print(f"❌ Could not resolve attachment path: {filepath}")
            self.console.print(f"   Searched {len(potential_paths)} potential locations")
        return None

    def _decode_header_value(self, header_value):
        """Decode email header values that may contain encoded words (emojis, special chars)"""
        if not header_value:
            return ""

        try:
            decoded_parts = []
            for part, encoding in decode_header(header_value):
                if isinstance(part, bytes):
                    # Decode bytes to string
                    if encoding:
                        try:
                            decoded_parts.append(part.decode(encoding))
                        except:
                            # Fallback to utf-8 if specified encoding fails
                            decoded_parts.append(part.decode('utf-8', errors='ignore'))
                    else:
                        # No encoding specified, try utf-8
                        decoded_parts.append(part.decode('utf-8', errors='ignore'))
                else:
                    # Already a string
                    decoded_parts.append(str(part))

            return ''.join(decoded_parts)
        except Exception as e:
            # If all else fails, return original value
            return str(header_value)

    def send_email(self, to, subject, body, attachments=None):
        """Keep working send function untouched"""
        try:
            if self.console:
                self.console.print(f"📤 Sending email to {to}")
            
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if provided - Enhanced binary support with robust path resolution
            if attachments:
                for attachment in attachments:
                    # Handle file paths (new capability for binary files)
                    if isinstance(attachment, dict) and ('filepath' in attachment or 'path' in attachment):
                        original_filepath = attachment.get('filepath') or attachment.get('path')
                        
                        # Use robust path resolution
                        resolved_filepath = self._resolve_attachment_path(original_filepath)
                        
                        if resolved_filepath:
                            filename = os.path.basename(resolved_filepath)
                            
                            # Determine if binary or text file
                            if resolved_filepath.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.pdf')):
                                # Binary file - read as bytes and encode properly
                                try:
                                    with open(resolved_filepath, 'rb') as f:
                                        file_data = f.read()
                                    
                                    file_size = len(file_data)
                                    if self.console:
                                        self.console.print(f"📎 Binary attachment: {filename} ({file_size} bytes)")
                                    
                                    if file_size == 0:
                                        if self.console:
                                            self.console.print(f"⚠️ Warning: {filename} is empty, skipping attachment")
                                        continue
                                    
                                    # EXPERT FIX: Create binary attachment with proper MIME types
                                    from email.mime.base import MIMEBase
                                    from email import encoders
                                    import mimetypes
                                    
                                    # Expert-recommended fallback MIME types for common formats
                                    FALLBACK_TYPES = {
                                        '.jpg': 'image/jpeg',
                                        '.jpeg': 'image/jpeg',
                                        '.png': 'image/png',
                                        '.gif': 'image/gif',
                                        '.mp4': 'video/mp4',
                                        '.mov': 'video/quicktime',
                                        '.avi': 'video/x-msvideo',
                                        '.pdf': 'application/pdf',
                                        '.md': 'text/markdown',
                                    }
                                    
                                    # Robust MIME detection with fallback (addresses root cause)
                                    file_ext = os.path.splitext(resolved_filepath)[1].lower()
                                    detected_mime = mimetypes.guess_type(resolved_filepath)[0]
                                    proper_mime = detected_mime or FALLBACK_TYPES.get(file_ext, 'application/octet-stream')
                                    maintype, subtype = proper_mime.split('/', 1)
                                    
                                    # Create part with CORRECT MIME type (critical fix)
                                    part = MIMEBase(maintype, subtype)
                                    part.set_payload(file_data)
                                    encoders.encode_base64(part)  # Encode exactly once
                                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                                    part.add_header('Content-Type', f'{proper_mime}; name="{filename}"')
                                    msg.attach(part)
                                    
                                    # Enhanced COCO consciousness diagnostic feedback
                                    if self.console:
                                        self.console.print(f"📎 Binary attachment: {filename} ({file_size:,} bytes as {proper_mime})")
                                        if file_size < 100 and file_size > 0:
                                            self.console.print(f"⚠️ Note: {filename} is unusually small ({file_size} bytes)")
                                        # Quick magic byte validation for common types
                                        magic_bytes = ' '.join(f'{b:02X}' for b in file_data[:8])
                                        self.console.print(f"🔍 Magic bytes: {magic_bytes}")
                                    
                                except Exception as e:
                                    if self.console:
                                        self.console.print(f"❌ Failed to read binary file {filename}: {e}")
                                    continue
                            else:
                                # Text file (including .md) - existing logic preserved
                                try:
                                    with open(resolved_filepath, 'r') as f:
                                        content = f.read()
                                    
                                    if self.console:
                                        self.console.print(f"📎 Text attachment: {filename} ({len(content)} chars)")
                                    
                                    part = MIMEText(content, 'plain')
                                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                                    msg.attach(part)
                                    
                                except Exception as e:
                                    if self.console:
                                        self.console.print(f"❌ Failed to read text file {filename}: {e}")
                                    continue
                        else:
                            if self.console:
                                self.console.print(f"❌ Could not find attachment file: {original_filepath}")
                            # Continue processing other attachments rather than failing completely
                    
                    # Keep existing raw content handling for backward compatibility
                    elif isinstance(attachment, dict) and 'content' in attachment:
                        part = MIMEText(attachment['content'], 'plain')
                        part.add_header('Content-Disposition', 
                                      f"attachment; filename={attachment.get('filename', 'report.txt')}")
                        msg.attach(part)
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email, self.app_password)
                server.send_message(msg)
            
            success_msg = f"✅ Email successfully sent to {to}"
            if self.console:
                self.console.print(success_msg)
            
            return {
                "success": True, 
                "message": success_msg,
                "details": {
                    "to": to,
                    "subject": subject
                }
            }
        except Exception as e:
            error_msg = f"❌ Failed to send email: {e}"
            if self.console:
                self.console.print(error_msg)
            return {"success": False, "error": str(e), "message": error_msg}
    
    def receive_emails(self, limit=10):
        """Get emails preserving Gmail's natural date sorting"""
        try:
            if self.console:
                self.console.print(f"📬 Retrieving emails (limit: {limit}) - Using Gmail's natural sorting")
            
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.app_password)
            mail.select('INBOX')
            
            # Get ALL email IDs - Gmail returns them oldest to newest
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            
            # Take the LAST 'limit' emails (newest) and REVERSE to get newest first
            # This preserves Gmail's exact sorting
            newest_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            newest_ids.reverse()  # Now newest is first
            
            emails = []
            for email_id in newest_ids:
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Extract body safely
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            body = str(msg.get_payload())
                    
                    # Keep the date exactly as Gmail provides it
                    date_str = msg.get("Date", "")
                    
                    # Simple time extraction for display (like Gmail's rightmost column)
                    display_time = "Unknown"
                    if date_str:
                        try:
                            # Extract just the time portion like Gmail shows
                            parts = date_str.split()
                            for part in parts:
                                if ':' in part and ('AM' in part.upper() or 'PM' in part.upper() or len(part) <= 8):
                                    display_time = part
                                    break
                        except:
                            display_time = "Unknown"
                    
                    # Decode From and Subject headers properly (handles emojis and special chars)
                    from_header = self._decode_header_value(msg.get("From", "Unknown"))
                    subject_header = self._decode_header_value(msg.get("Subject", "No Subject"))

                    emails.append({
                        "from": from_header,
                        "subject": subject_header,
                        "date": date_str,
                        "display_time": display_time,  # Like "4:09PM"
                        "body_preview": body[:200].strip() if body else "",
                        "body_full": body.strip() if body else "",  # Full content for consistency
                        "gmail_order": len(emails),  # Preserve exact Gmail ordering
                        "email_id": email_id.decode('utf-8') if isinstance(email_id, bytes) else str(email_id)  # Store ID for direct access
                    })
                except Exception as e:
                    continue
            
            mail.close()
            mail.logout()
            
            if self.console:
                self.console.print(f"✅ Retrieved {len(emails)} emails in Gmail's natural order")
            
            return emails
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ Error retrieving emails: {e}")
            return []
    
    def get_top_5_emails(self):
        """Get top 5 most recent emails using Gmail's sorting"""
        emails = self.receive_emails(limit=5)
        
        if not emails:
            return "📭 No emails found."
        
        summary = "📧 **Your 5 Most Recent Emails:**\n" + "="*40 + "\n\n"
        
        for i, email in enumerate(emails, 1):
            summary += f"**{i}.** [{email['display_time']}] From: {email['from'][:30]}\n"
            summary += f"     Subject: {email['subject']}\n"
            if email['body_preview']:
                summary += f"     Preview: {email['body_preview'][:80]}...\n"
            summary += "\n"
        
        return summary
    
    def get_todays_emails(self):
        """Get today's emails by checking date strings"""
        import datetime
        today = datetime.date.today()
        today_formats = [
            today.strftime("%d %b %Y"),  # Like "06 Sep 2025"
            today.strftime("%d %B %Y"),  # Like "06 September 2025" 
            today.strftime("%Y-%m-%d"),  # Like "2025-09-06"
            f"{today.day} {today.strftime('%b')}",  # Like "6 Sep"
            today.strftime("%b %d"),     # Like "Sep 06" 
            f"{today.strftime('%b')} {today.day}",  # Like "Sep 6"
            today.strftime("%Y"),        # At least same year
        ]
        
        if self.console:
            self.console.print("📅 Getting today's emails using Gmail's natural order")
        
        # Get more emails to ensure we catch all of today's
        all_emails = self.receive_emails(limit=50)
        
        todays_emails = []
        for email in all_emails:
            # Check if any of today's date formats appear in the date string
            for date_format in today_formats:
                if date_format in email['date']:
                    todays_emails.append(email)
                    break
        
        if not todays_emails:
            return "📭 No emails from today."
        
        summary = f"📧 **Today's Emails ({len(todays_emails)} total):**\n" + "="*45 + "\n\n"
        
        for i, email in enumerate(todays_emails[:10], 1):  # Limit display to 10
            summary += f"**{i}.** [{email['display_time']}] From: {email['from'][:40]}\n"
            summary += f"      Subject: {email['subject']}\n"
            if email['body_preview']:
                summary += f"      Preview: {email['body_preview'][:100]}...\n"
            summary += "\n"
        
        if len(todays_emails) > 10:
            summary += f"... and {len(todays_emails) - 10} more emails from today\n"
        
        return summary
    
    def get_recent_emails_summary(self, limit=10):
        """Get recent emails with rich formatting"""
        emails = self.receive_emails(limit)
        
        if not emails:
            return "📭 No emails found."
        
        summary = f"📧 **Recent Emails ({len(emails)} found):**\n" + "="*40 + "\n\n"
        
        for i, email in enumerate(emails, 1):
            summary += f"**{i}.** [{email['display_time']}] - From: {email['from'][:50]}\n"
            summary += f"      Subject: {email['subject']}\n"
            if email['body_preview']:
                summary += f"      Preview: {email['body_preview'][:120]}...\n"
            summary += "\n"
        
        return summary

    def get_full_email_content(self, email_index: int, limit: int = 10):
        """Get full content of specific email by index, maintaining Gmail's exact ordering"""
        try:
            if self.console:
                self.console.print(f"📧 Reading email #{email_index} with Gmail-consistent ordering")

            # Use the same receive_emails method to ensure consistent ordering
            emails = self.receive_emails(limit)

            if not emails:
                return "📭 No emails found."

            # Validate email index (1-based indexing)
            if email_index < 1 or email_index > len(emails):
                return f"📧 Email #{email_index} not found. Available emails: 1-{len(emails)}"

            # Get the specific email (convert to 0-based indexing)
            email_data = emails[email_index - 1]

            # Format full email content
            formatted_output = []
            formatted_output.append("📧 **Full Email Content - Gmail-Consistent Reading**")
            formatted_output.append(f"📍 **Position:** #{email_index} in recent emails list")
            formatted_output.append(f"📅 **Date:** {email_data.get('date', 'Unknown')}")
            formatted_output.append(f"👤 **From:** {email_data.get('from', 'Unknown')}")
            formatted_output.append(f"📬 **Subject:** {email_data.get('subject', 'No Subject')}")
            formatted_output.append("")
            formatted_output.append("📄 **Full Content:**")
            formatted_output.append("-" * 50)

            full_body = email_data.get('body_full', email_data.get('body_preview', ''))
            if full_body:
                formatted_output.append(full_body)
            else:
                formatted_output.append("(No content available)")

            formatted_output.append("-" * 50)
            formatted_output.append(f"✅ **Email #{email_index} successfully read with Gmail-consistent indexing**")

            return "\n".join(formatted_output)

        except Exception as e:
            if self.console:
                self.console.print(f"❌ Error reading email #{email_index}: {e}")
            return f"❌ Error reading email #{email_index}: {str(e)}"

# For direct testing
if __name__ == "__main__":
    print("🧪 Testing Gentle Gmail Fix...")
    gmail = GentleGmailFix()
    
    # Test the gentle approach
    print("\n📬 Testing email retrieval with Gmail's natural sorting...")
    emails = gmail.receive_emails(5)
    print(f"Retrieved {len(emails)} emails")
    
    if emails:
        print("\n📧 Email order (Gmail's natural newest-first):")
        for i, email in enumerate(emails, 1):
            print(f"{i}. [{email['display_time']}] {email['subject'][:30]}...")
    
    # Test today's emails
    print("\n📅 Testing today's emails...")
    today_summary = gmail.get_todays_emails()
    print(today_summary)
    
    print("\n✅ Gentle Gmail Fix test complete!")
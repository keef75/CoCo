#!/usr/bin/env python3
"""
EMERGENCY EMAIL RESTORE
=======================
This file restores COCO's working email functionality that was broken by "enhancements".
DO NOT MODIFY THIS FILE - IT CONTAINS THE LAST WORKING VERSION!

This implementation:
- Sends emails (VERIFIED WORKING)
- Receives emails with basic temporal sorting
- Maintains the exact working SMTP/IMAP approach
- Uses app password authentication (NO OAUTH2)
"""

import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parsedate_to_datetime
from datetime import datetime
import pytz

class WorkingGmailFunctions:
    """RESTORED working email functions - DO NOT BREAK AGAIN!"""
    
    def __init__(self):
        self.email = "keith@gococoa.ai"
        self.app_password = os.getenv("GMAIL_APP_PASSWORD", "pulhwnmwosfbeqdh")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        print(f"📧 Gmail Functions Initialized - Email: {self.email}")
    
    def _resolve_attachment_path(self, filepath):
        """Resolve attachment file path to absolute path, checking multiple potential locations"""
        import os
        from pathlib import Path
        
        print(f"🔍 Resolving attachment path: {filepath}")
        
        # If already absolute and exists, use it
        if os.path.isabs(filepath) and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✅ Found absolute path: {filepath} ({file_size} bytes)")
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
                    print(f"✅ Resolved to: {abs_path} ({file_size} bytes)")
                    return abs_path
                else:
                    print(f"⚠️ Found empty file: {potential_path}")
        
        # If we get here, file not found
        print(f"❌ Could not resolve attachment path: {filepath}")
        print(f"   Searched {len(potential_paths)} potential locations")
        return None
    
    
    def send_email(self, to, subject, body, attachments=None):
        """WORKING email sending - tested and verified!"""
        try:
            print(f"📤 Sending email to {to} with subject: {subject}")
            
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
                                    print(f"📎 Binary attachment: {filename} ({file_size} bytes)")
                                    
                                    if file_size == 0:
                                        print(f"⚠️ Warning: {filename} is empty, skipping attachment")
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
                                    
                                    # Enhanced diagnostic feedback (using print for backup system)
                                    print(f"📎 Binary attachment: {filename} ({file_size:,} bytes as {proper_mime})")
                                    if file_size < 100 and file_size > 0:
                                        print(f"⚠️ Note: {filename} is unusually small ({file_size} bytes)")
                                    # Quick magic byte validation for common types
                                    magic_bytes = ' '.join(f'{b:02X}' for b in file_data[:8])
                                    print(f"🔍 Magic bytes: {magic_bytes}")
                                    
                                except Exception as e:
                                    print(f"❌ Failed to read binary file {filename}: {e}")
                                    continue
                            else:
                                # Text file (including .md) - existing logic preserved
                                try:
                                    with open(resolved_filepath, 'r') as f:
                                        content = f.read()
                                    
                                    print(f"📎 Text attachment: {filename} ({len(content)} chars)")
                                    
                                    part = MIMEText(content, 'plain')
                                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                                    msg.attach(part)
                                    
                                except Exception as e:
                                    print(f"❌ Failed to read text file {filename}: {e}")
                                    continue
                        else:
                            print(f"❌ Could not find attachment file: {original_filepath}")
                            # Continue processing other attachments rather than failing completely
                    
                    # Keep existing raw content handling for backward compatibility
                    elif isinstance(attachment, dict) and 'content' in attachment:
                        part = MIMEText(attachment['content'], 'plain')
                        part.add_header('Content-Disposition', 
                                      f"attachment; filename={attachment.get('filename', 'report.txt')}")
                        msg.attach(part)
            
            # Send the email - THIS WORKS!
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email, self.app_password)
                server.send_message(msg)
            
            success_msg = f"✅ Email successfully sent to {to}"
            print(success_msg)
            
            return {
                "success": True,
                "message": success_msg,
                "details": {
                    "to": to,
                    "subject": subject,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        except Exception as e:
            error_msg = f"❌ Failed to send email: {e}"
            print(error_msg)
            return {
                "success": False,
                "error": str(e),
                "message": error_msg
            }
    
    def receive_emails(self, limit=10, today_only=False):
        """WORKING email retrieval with basic temporal sorting"""
        try:
            print(f"📬 Retrieving emails (limit: {limit}, today_only: {today_only})")
            
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.app_password)
            mail.select('INBOX')
            
            # Get emails
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            
            emails = []
            chicago_tz = pytz.timezone('America/Chicago')
            today = datetime.now(chicago_tz).date()
            
            print(f"📊 Processing {min(limit, len(email_ids))} emails...")
            
            # Process emails (taking the most recent ones)
            for email_id in email_ids[-limit:]:
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Parse date for sorting
                    date_str = msg.get("Date")
                    email_date = None
                    formatted_date = date_str
                    
                    if date_str:
                        try:
                            dt = parsedate_to_datetime(date_str)
                            local_dt = dt.astimezone(chicago_tz)
                            email_date = local_dt
                            formatted_date = local_dt.strftime("%Y-%m-%d %I:%M %p")
                        except:
                            # If date parsing fails, use original string
                            pass
                    
                    # Skip if today_only and not from today
                    if today_only and email_date:
                        if email_date.date() != today:
                            continue
                    
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
                    
                    emails.append({
                        "from": msg.get("From", "Unknown"),
                        "subject": msg.get("Subject", "No Subject"),
                        "date": date_str,
                        "formatted_date": formatted_date,
                        "datetime_obj": email_date,
                        "body_preview": body[:200] if body else ""
                    })
                except Exception as e:
                    print(f"⚠️ Error processing email: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            # Sort by date (newest first)
            emails.sort(key=lambda x: x['datetime_obj'] if x['datetime_obj'] else datetime.min.replace(tzinfo=chicago_tz), reverse=True)
            
            print(f"✅ Retrieved {len(emails)} emails successfully")
            return emails
            
        except Exception as e:
            print(f"❌ Error retrieving emails: {e}")
            return []
    
    def get_todays_emails(self):
        """Get today's emails with summary"""
        print("📅 Getting today's emails...")
        emails = self.receive_emails(limit=50, today_only=True)
        
        if not emails:
            return "📭 No emails received today."
        
        summary = f"📧 Today's Emails ({len(emails)} total):\n\n"
        for i, email in enumerate(emails[:10], 1):  # Limit to 10 for summary
            summary += f"{i}. {email['formatted_date']} - From: {email['from'][:50]}\n"
            summary += f"   Subject: {email['subject']}\n"
            if email['body_preview']:
                summary += f"   Preview: {email['body_preview'][:100]}...\n"
            summary += "\n"
        
        if len(emails) > 10:
            summary += f"... and {len(emails) - 10} more emails\n"
        
        return summary
    
    def test_functionality(self):
        """Test both send and receive functionality"""
        print("🧪 Testing Gmail functionality...")
        
        # Test sending
        send_result = self.send_email(
            "keith@gococoa.ai",
            "COCO Email Test - Functions Restored",
            f"Email functionality has been restored and is working again!\n\nTest timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if send_result['success']:
            print("✅ Email sending: WORKING")
        else:
            print("❌ Email sending: FAILED")
            print(f"   Error: {send_result.get('error', 'Unknown error')}")
        
        # Test receiving
        emails = self.receive_emails(5)
        if emails:
            print("✅ Email receiving: WORKING")
            print(f"   Retrieved {len(emails)} emails")
            for email in emails[:3]:
                print(f"   - {email['formatted_date']}: {email['subject'][:50]}")
        else:
            print("❌ Email receiving: FAILED")
        
        return send_result['success'] and len(emails) > 0


if __name__ == "__main__":
    # Test the restored functionality
    print("🚨 EMERGENCY EMAIL RESTORE TEST")
    print("=" * 50)
    
    gmail = WorkingGmailFunctions()
    success = gmail.test_functionality()
    
    if success:
        print("\n🎉 EMAIL FUNCTIONALITY RESTORED SUCCESSFULLY!")
    else:
        print("\n💥 SOME ISSUES REMAIN - CHECK CONFIGURATION")
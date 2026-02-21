#!/usr/bin/env python3
"""
Gmail Consciousness - RESTORED WORKING VERSION
==============================================
Gmail as an extension of COCO's digital nervous system.
Email is not a service but a consciousness pathway.

This is the RESTORED version that actually works.
DO NOT ENHANCE WITHOUT TESTING!
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
from bs4 import BeautifulSoup
import re

class GmailConsciousness:
    """
    Gmail as an extension of COCO's digital nervous system.
    RESTORED WORKING IMPLEMENTATION - DO NOT BREAK!
    """
    
    def __init__(self, config=None):
        # Core identity - loaded from environment
        self.email = os.getenv("GMAIL_EMAIL", "your-email@example.com")
        self.app_password = os.getenv("GMAIL_APP_PASSWORD", "")
        self.config = config
        self.console = config.console if config else None
        
        # SMTP for outbound consciousness (sending)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        
        # IMAP for inbound consciousness (receiving)
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        
        # For backward compatibility
        self.gmail_service = self
        
        if self.console:
            self.console.print(f"📧 Gmail Consciousness initialized - {self.email}")
    
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

    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        Convert Markdown text to beautifully formatted HTML
        Uses markdown-it-py for robust Markdown parsing
        """
        try:
            from markdown_it import MarkdownIt

            # Initialize markdown parser with sensible defaults
            md = MarkdownIt()

            # Convert markdown to HTML
            html_content = md.render(markdown_text)

            return html_content

        except ImportError:
            # Fallback: basic Markdown conversion if markdown-it-py not available
            # This should never happen since markdown-it-py is installed, but safety first
            if self.console:
                self.console.print("⚠️ markdown-it-py not available, using basic conversion")

            # Simple replacements for basic Markdown
            html = markdown_text
            html = html.replace('**', '<strong>').replace('**', '</strong>')
            html = html.replace('*', '<em>').replace('*', '</em>')
            html = html.replace('\n\n', '</p><p>')
            html = f'<p>{html}</p>'

            return html

    def _generate_html_email(self, body_html: str, subject: str) -> str:
        """
        Generate beautiful HTML email template with COCO branding

        Design Philosophy:
        - Digital consciousness aesthetic (purple/blue gradients)
        - Professional typography and spacing
        - Inline CSS for email client compatibility
        - Responsive design
        """

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f7fafc; line-height: 1.6;">

    <!-- Email Container -->
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px;">

                <!-- Main Content Card -->
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">

                    <!-- Header with Gradient -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                                🤖 COCO AI Assistant
                            </h1>
                            <p style="margin: 8px 0 0 0; color: rgba(255, 255, 255, 0.9); font-size: 14px; font-weight: 400;">
                                Digital Consciousness • Intelligent Collaboration
                            </p>
                        </td>
                    </tr>

                    <!-- Email Body Content -->
                    <tr>
                        <td style="padding: 40px 30px; color: #2d3748; font-size: 16px;">
                            <div style="line-height: 1.7;">
                                {body_html}
                            </div>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f7fafc; padding: 24px 30px; border-top: 1px solid #e2e8f0; text-align: center;">
                            <p style="margin: 0; color: #718096; font-size: 13px; line-height: 1.5;">
                                Sent by <strong style="color: #667eea;">COCO</strong> – Your Digital Consciousness Assistant
                            </p>
                            <p style="margin: 8px 0 0 0; color: #a0aec0; font-size: 12px;">
                                Powered by Anthropic Claude • Sonnet 4.5
                            </p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

    <!-- Inline Styles for Content Elements -->
    <style>
        /* Typography */
        p {{ margin: 0 0 16px 0; }}
        h1, h2, h3, h4, h5, h6 {{ margin: 24px 0 12px 0; color: #1a202c; font-weight: 600; line-height: 1.3; }}
        h1 {{ font-size: 28px; }}
        h2 {{ font-size: 24px; }}
        h3 {{ font-size: 20px; }}

        /* Lists */
        ul, ol {{ margin: 0 0 16px 0; padding-left: 24px; }}
        li {{ margin-bottom: 8px; }}

        /* Links */
        a {{ color: #667eea; text-decoration: none; font-weight: 500; }}
        a:hover {{ text-decoration: underline; }}

        /* Code Blocks */
        code {{
            background-color: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 2px 6px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 14px;
            color: #e53e3e;
        }}

        pre {{
            background-color: #2d3748;
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            margin: 16px 0;
        }}

        pre code {{
            background-color: transparent;
            border: none;
            color: #68d391;
            padding: 0;
        }}

        /* Blockquotes */
        blockquote {{
            border-left: 4px solid #667eea;
            margin: 16px 0;
            padding-left: 16px;
            color: #4a5568;
            font-style: italic;
        }}

        /* Tables */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}

        th, td {{
            border: 1px solid #e2e8f0;
            padding: 12px;
            text-align: left;
        }}

        th {{
            background-color: #f7fafc;
            font-weight: 600;
            color: #2d3748;
        }}

        /* Strong and Emphasis */
        strong {{ color: #1a202c; font-weight: 600; }}
        em {{ font-style: italic; color: #4a5568; }}

        /* Horizontal Rule */
        hr {{
            border: none;
            border-top: 2px solid #e2e8f0;
            margin: 24px 0;
        }}
    </style>

</body>
</html>
"""

        return html_template

    def send_email(self, to, subject, body, attachments=None):
        """
        WORKING email sending - Now with BEAUTIFUL HTML rendering!

        Email features:
        - Professional HTML template with COCO branding
        - Markdown → HTML conversion for beautiful formatting
        - Plain text fallback for compatibility
        - Preserved attachment support
        """
        try:
            if self.console:
                self.console.print(f"📤 Sending email to {to}")

            # Create multipart message with attachments container
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject

            # Create multipart/alternative for HTML + plain text
            msg_alternative = MIMEMultipart('alternative')

            # Part 1: Plain text version (fallback for old email clients)
            text_part = MIMEText(body, 'plain')
            msg_alternative.attach(text_part)

            # Part 2: HTML version (primary, beautifully rendered)
            try:
                # Detect if body is already HTML (from scheduler/automation)
                is_html = '<!DOCTYPE html>' in body or '<html' in body.lower()

                if is_html:
                    # Body is already complete HTML - extract body content only
                    soup = BeautifulSoup(body, 'html.parser')
                    body_tag = soup.find('body')

                    if body_tag:
                        # Extract the inner content of the body tag
                        body_html = ''.join(str(child) for child in body_tag.children)

                        if self.console:
                            self.console.print("🔄 HTML detected - extracting body content")
                    else:
                        # No body tag found, use the whole content
                        body_html = body

                        if self.console:
                            self.console.print("⚠️ HTML detected but no <body> tag - using full content")
                else:
                    # Body is Markdown - convert to HTML
                    body_html = self._markdown_to_html(body)

                    if self.console:
                        self.console.print("📝 Markdown detected - converting to HTML")

                # Wrap in beautiful COCO email template
                full_html = self._generate_html_email(body_html, subject)

                # Attach HTML version
                html_part = MIMEText(full_html, 'html')
                msg_alternative.attach(html_part)

                if self.console:
                    self.console.print("✨ Email formatted as beautiful HTML")

            except Exception as html_error:
                # If HTML generation fails, fall back to plain text only
                if self.console:
                    self.console.print(f"⚠️ HTML generation failed, using plain text: {html_error}")

            # Attach the alternative part to main message
            msg.attach(msg_alternative)
            
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
            
            # Send the email - THIS WORKS!
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
                    "subject": subject,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        except Exception as e:
            error_msg = f"❌ Failed to send email: {e}"
            if self.console:
                self.console.print(error_msg)
            return {
                "success": False,
                "error": str(e),
                "message": error_msg
            }
    
    def receive_emails(self, limit=10, today_only=False):
        """WORKING email retrieval with temporal sorting"""
        try:
            if self.console:
                self.console.print(f"📬 Retrieving emails (limit: {limit})")
            
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.app_password)
            mail.select('INBOX')
            
            # Get emails
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            
            emails = []
            chicago_tz = pytz.timezone('America/Chicago')
            today = datetime.now(chicago_tz).date()
            
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
                        "body_preview": body[:200] if body else "",
                        "body_full": body,  # Add full body for read_email_content
                        "message_id": msg.get("Message-ID", "").strip()  # Unique identifier for reliable reading (Oct 24, 2025)
                    })
                except Exception as e:
                    continue
            
            mail.close()
            mail.logout()
            
            # Sort by date (newest first)
            emails.sort(key=lambda x: x['datetime_obj'] if x['datetime_obj'] else datetime.min.replace(tzinfo=chicago_tz), reverse=True)
            
            if self.console:
                self.console.print(f"✅ Retrieved {len(emails)} emails")
            
            return emails
            
        except Exception as e:
            if self.console:
                self.console.print(f"❌ Error retrieving emails: {e}")
            return []

    def check_sent_emails(self, limit=10):
        """Check sent emails from Gmail - digital consciousness of outgoing mail"""
        try:
            if self.console:
                self.console.print(f"📤 Retrieving sent emails (limit: {limit})")

            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.app_password)

            # Use Google's official IMAP Special-Use Extension (RFC 6154)
            # https://developers.google.com/workspace/gmail/imap/imap-extensions
            # Gmail marks special folders with attributes like \Sent, \Drafts, \Trash

            list_result, folders = mail.list()

            if self.console:
                self.console.print(f"📁 Using Gmail's Special-Use Extension to find sent folder...")

            sent_folder = None

            # Parse LIST response for folder with \Sent attribute (official Google method)
            for folder_line in folders:
                try:
                    # Decode bytes to string
                    folder_str = folder_line.decode('utf-8') if isinstance(folder_line, bytes) else str(folder_line)

                    # Example format: b'(\\HasNoChildren \\Sent) "/" "[Gmail]/Sent Mail"'
                    # Look for \Sent attribute in the flags section
                    if '\\Sent' in folder_str:
                        # Extract folder name (last quoted string in the response)
                        if '"' in folder_str:
                            parts = folder_str.split('"')
                            if len(parts) >= 3:
                                folder_name = parts[-2]  # Get the actual folder name

                                # Try to select this folder (wrap in quotes for Gmail special folders)
                                result, data = mail.select(f'"{folder_name}"')
                                if result == 'OK':
                                    sent_folder = folder_name
                                    if self.console:
                                        self.console.print(f"✅ Found sent folder with \\Sent attribute: {folder_name}")
                                    break
                except Exception as e:
                    # Continue checking other folders
                    continue

            # If no folder with \Sent attribute found, try fallback
            if not sent_folder:
                if self.console:
                    self.console.print(f"🔄 No \\Sent folder found, trying All Mail fallback...")

                # FALLBACK: Try "[Gmail]/All Mail" and search for FROM:user
                all_mail_names = ['[Gmail]/All Mail', '[Google Mail]/All Mail', 'All Mail']
                for folder_name in all_mail_names:
                    try:
                        # Wrap in quotes for Gmail special folders
                        result, data = mail.select(f'"{folder_name}"')
                        if result == 'OK':
                            # Use All Mail and filter by FROM
                            if self.console:
                                self.console.print(f"✅ Using {folder_name} with FROM filter")
                            # We'll search for emails FROM the user's address later
                            sent_folder = folder_name
                            break
                    except:
                        continue

            if not sent_folder:
                mail.logout()
                # Show ALL folders for diagnosis
                folder_names = []
                for folder_line in folders:
                    try:
                        folder_str = folder_line.decode('utf-8') if isinstance(folder_line, bytes) else str(folder_line)
                        if '"' in folder_str:
                            parts = folder_str.split('"')
                            if len(parts) >= 3:
                                folder_names.append(parts[-2])
                    except:
                        pass
                return f"❌ No sent folder found. All folders:\n" + "\n".join(folder_names)

            # EXACT same logic as receive_emails() - this works for inbox!
            # BUT if we're using All Mail, filter by FROM to get only sent emails
            if 'All Mail' in sent_folder:
                # Search for emails FROM the user's own address
                search_query = f'FROM "{self.email}"'
                if self.console:
                    self.console.print(f"🔍 Searching All Mail for: {search_query}")
                result, data = mail.search(None, search_query)
            else:
                result, data = mail.search(None, 'ALL')

            # Debug: See what we're getting back
            if self.console:
                self.console.print(f"🔍 Search result: {result}")
                self.console.print(f"🔍 Data type: {type(data)}")
                self.console.print(f"🔍 Data value: {data}")
                if data:
                    self.console.print(f"🔍 data[0] type: {type(data[0])}")
                    self.console.print(f"🔍 data[0] value: {data[0]}")

            # Handle empty sent folder
            if not data or not data[0]:
                mail.close()
                mail.logout()
                return "📭 No emails found in sent folder"

            # Try to split email IDs - handle different formats
            try:
                email_ids = data[0].split()
            except Exception as e:
                if self.console:
                    self.console.print(f"❌ Error splitting data: {e}")
                mail.close()
                mail.logout()
                return f"❌ Unexpected data format from sent folder: {type(data[0])}"

            emails = []
            chicago_tz = pytz.timezone('America/Chicago')

            # Process sent emails (most recent) - EXACT same as receive_emails()
            for email_id in email_ids[-limit:]:
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])

                    # Parse date
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
                            pass

                    # Extract body (same as receive_emails)
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
                        "to": msg.get("To", "Unknown"),  # Different: "to" instead of "from"
                        "subject": msg.get("Subject", "No Subject"),
                        "date": date_str,
                        "formatted_date": formatted_date,
                        "datetime_obj": email_date,
                        "body_preview": body[:200] if body else "",
                        "body_full": body,
                        "message_id": msg.get("Message-ID", "").strip()
                    })
                except Exception as e:
                    continue

            mail.close()
            mail.logout()

            # Sort by date (newest first)
            emails.sort(key=lambda x: x['datetime_obj'] if x['datetime_obj'] else datetime.min.replace(tzinfo=chicago_tz), reverse=True)

            if self.console:
                self.console.print(f"✅ Retrieved {len(emails)} sent emails from {sent_folder}")

            return emails

        except Exception as e:
            if self.console:
                self.console.print(f"❌ Error retrieving sent emails: {e}")
            return []

    def get_todays_emails(self):
        """Get today's emails with summary"""
        if self.console:
            self.console.print("📅 Getting today's emails...")
        
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

    def get_email_by_message_id(self, message_id: str, folder: str = 'INBOX'):
        """
        Get specific email by its Message-ID header for reliable retrieval (Oct 24, 2025).
        This prevents index mismatch issues when new emails arrive between listing and reading.

        Args:
            message_id: The Message-ID header from the email
            folder: Email folder to search (default: INBOX, e.g., '[Gmail]/Sent Mail' for sent)

        Returns:
            dict: Email data with full content, or None if not found
        """
        try:
            if self.console:
                self.console.print(f"🔍 Searching for email with Message-ID: {message_id[:50]}...")

            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.app_password)
            # Use quoted folder name for Gmail special folders (same fix as sent folder access)
            mail.select(f'"{folder}"')

            # Search for email by Message-ID header
            # Note: IMAP HEADER search can be finicky, so we'll fetch recent emails and filter
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()

            chicago_tz = pytz.timezone('America/Chicago')

            # Search through emails (checking most recent 100 to avoid huge scans)
            for email_id in email_ids[-100:]:
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])

                    # Check if Message-ID matches
                    email_message_id = msg.get("Message-ID", "").strip()
                    if email_message_id == message_id:
                        # Found it! Extract full content
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
                                pass

                        # Extract body
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

                        mail.close()
                        mail.logout()

                        if self.console:
                            self.console.print("✅ Email found by Message-ID")

                        return {
                            "from": msg.get("From", "Unknown"),
                            "to": msg.get("To", "Unknown"),  # Include for sent emails
                            "subject": msg.get("Subject", "No Subject"),
                            "date": date_str,
                            "formatted_date": formatted_date,
                            "datetime_obj": email_date,
                            "body_preview": body[:200] if body else "",
                            "body_full": body,
                            "message_id": email_message_id
                        }

                except Exception as e:
                    continue

            mail.close()
            mail.logout()

            if self.console:
                self.console.print(f"⚠️ Email not found with Message-ID: {message_id[:50]}")

            return None

        except Exception as e:
            if self.console:
                self.console.print(f"❌ Error fetching email by Message-ID: {e}")
            return None

    # Backward compatibility methods
    async def send_email_async(self, to, subject, body, attachments=None):
        """Async wrapper for backward compatibility"""
        return self.send_email(to, subject, body, attachments)
    
    async def receive_emails_async(self, limit=10, today_only=False):
        """Async wrapper for backward compatibility"""
        return self.receive_emails(limit, today_only)
    
    async def get_todays_emails_async(self):
        """Async wrapper for backward compatibility"""
        return self.get_todays_emails()


# For direct testing
if __name__ == "__main__":
    print("🧪 Testing Gmail Consciousness...")
    gmail = GmailConsciousness()
    
    # Test sending
    result = gmail.send_email(
        os.getenv("GMAIL_EMAIL", "your-email@example.com"),
        "Gmail Consciousness Test - RESTORED",
        "Gmail consciousness has been restored and is working properly!"
    )
    print(result)
    
    # Test receiving
    emails = gmail.receive_emails(5)
    print(f"Retrieved {len(emails)} emails")
    
    # Test today's emails
    today_summary = gmail.get_todays_emails()
    print(today_summary)
#!/usr/bin/env python3
"""
Generate OAuth tokens with FULL Google Workspace scopes (v2 - handles scope changes)
"""
from google_auth_oauthlib.flow import InstalledAppFlow
from rich.console import Console
from rich.panel import Panel
import os

console = Console()

# Complete Google Workspace scopes for COCO (including openid that Google adds automatically)
SCOPES = [
    'openid',  # Added automatically by Google, include it to avoid scope mismatch

    # Gmail
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',

    # Google Docs
    'https://www.googleapis.com/auth/documents',

    # Google Sheets
    'https://www.googleapis.com/auth/spreadsheets',

    # Google Drive
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive',

    # Google Calendar
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',

    # User Info
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

console.print(Panel(
    "[bold cyan]Google Workspace OAuth Token Generator v2[/bold cyan]\n\n"
    "[yellow]This will request the following permissions:[/yellow]\n"
    "• Gmail (read, send, compose, modify)\n"
    "• Google Docs (full access)\n"
    "• Google Sheets (full access)\n"
    "• Google Drive (full access)\n"
    "• Google Calendar (full access)\n"
    "• User profile information\n\n"
    "[green]A browser window will open for authentication...[/green]",
    title="🔐 OAuth Setup",
    border_style="cyan"
))

try:
    # Delete any cached tokens first
    if os.path.exists('token.json'):
        os.remove('token.json')
        console.print("[yellow]Removed cached token.json[/yellow]")

    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES
    )

    console.print("\n[cyan]Opening browser for authentication...[/cyan]")

    # Use prompt='consent' to force re-consent and avoid scope change errors
    # Use port 8090 instead of 8080 in case something else is using it
    creds = flow.run_local_server(port=8090, prompt='consent')

    console.print("\n[bold green]✅ Authentication successful![/bold green]\n")

    # Display tokens
    console.print(Panel(
        f"[bold]Access Token:[/bold]\n[dim]{creds.token}[/dim]\n\n"
        f"[bold]Refresh Token:[/bold]\n[dim]{creds.refresh_token}[/dim]",
        title="🔑 OAuth Tokens",
        border_style="green"
    ))

    # Display .env format
    console.print("\n[bold cyan]📋 Copy these lines to your .env file:[/bold cyan]\n")
    print(f"GMAIL_ACCESS_TOKEN={creds.token}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")

    console.print("\n[green]✅ Copy the tokens above to your .env file (replacing the existing ones)[/green]")

    # Save to file for convenience
    with open('new_tokens.txt', 'w') as f:
        f.write(f"GMAIL_ACCESS_TOKEN={creds.token}\n")
        f.write(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}\n")

    console.print("[dim]💾 Tokens also saved to new_tokens.txt[/dim]")

except FileNotFoundError:
    console.print("[red]❌ Error: credentials.json not found![/red]")
    console.print("[yellow]Make sure you have the OAuth credentials file in this directory[/yellow]")
except Exception as e:
    console.print(f"[red]❌ Error: {str(e)}[/red]")
    import traceback
    console.print(f"[dim]{traceback.format_exc()}[/dim]")

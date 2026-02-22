#!/usr/bin/env python3
"""
Generate OAuth tokens with FULL Google Workspace scopes
Includes: Gmail, Docs, Sheets, Drive, Calendar
"""
from google_auth_oauthlib.flow import InstalledAppFlow
from rich.console import Console
from rich.panel import Panel

console = Console()

# Complete Google Workspace scopes for COCO
SCOPES = [
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
    "[bold cyan]Google Workspace OAuth Token Generator[/bold cyan]\n\n"
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
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES
    )

    console.print("\n[cyan]Opening browser for authentication...[/cyan]")
    creds = flow.run_local_server(port=8080)

    console.print("\n[bold green]✅ Authentication successful![/bold green]\n")

    # Display tokens
    console.print(Panel(
        f"[bold]Access Token:[/bold]\n[dim]{creds.token}[/dim]\n\n"
        f"[bold]Refresh Token:[/bold]\n[dim]{creds.refresh_token}[/dim]",
        title="🔑 OAuth Tokens",
        border_style="green"
    ))

    # Display .env format
    console.print("\n[bold cyan]Add these to your .env file:[/bold cyan]\n")
    print(f"GMAIL_ACCESS_TOKEN={creds.token}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")

    console.print("\n[green]✅ Copy the tokens above to your .env file[/green]")

except FileNotFoundError:
    console.print("[red]❌ Error: credentials.json not found![/red]")
    console.print("[yellow]Make sure you have the OAuth credentials file in this directory[/yellow]")
except Exception as e:
    console.print(f"[red]❌ Error: {str(e)}[/red]")

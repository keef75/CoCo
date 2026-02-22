#!/usr/bin/env python3
"""
Regenerate Google Workspace OAuth Tokens
Simple interactive script to get new OAuth tokens.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from rich.console import Console
from rich.panel import Panel

console = Console()

# Load environment
load_dotenv()

# All scopes needed for full Google Workspace access
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

def main():
    console.print(Panel(
        "[bold cyan]Google Workspace OAuth Token Regenerator[/bold cyan]\n\n"
        "[yellow]This will open a browser to authenticate with Google.[/yellow]\n"
        "Make sure to:\n"
        "1. Use the Google account you want to connect\n"
        "2. Accept all requested permissions\n"
        "3. Complete the authentication flow",
        border_style="cyan"
    ))

    # Get credentials from environment
    client_id = os.getenv('GMAIL_CLIENT_ID')
    client_secret = os.getenv('GMAIL_CLIENT_SECRET')

    if not client_id or not client_secret:
        console.print("[red]❌ GMAIL_CLIENT_ID or GMAIL_CLIENT_SECRET not found in .env file[/red]")
        return

    console.print(f"\n[green]✅ Found OAuth credentials[/green]")
    console.print(f"   Client ID: {client_id[:20]}...")

    # Create OAuth flow
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": ["http://localhost:8090", "urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES
    )

    console.print("\n[cyan]Opening browser for authentication...[/cyan]")
    console.print("[dim]If browser doesn't open, copy the URL from the terminal[/dim]\n")

    try:
        # Run the OAuth flow - try port 8090 first
        creds = flow.run_local_server(port=8090, prompt='consent')

        console.print("\n[green]✅ Authentication successful![/green]\n")

        # Display the new tokens
        console.print(Panel(
            f"[bold green]New OAuth Tokens[/bold green]\n\n"
            f"[yellow]Access Token:[/yellow]\n{creds.token}\n\n"
            f"[yellow]Refresh Token:[/yellow]\n{creds.refresh_token}",
            title="✨ Copy These to .env",
            border_style="green"
        ))

        console.print("\n[cyan]Update your .env file with:[/cyan]")
        console.print(f"GMAIL_ACCESS_TOKEN={creds.token}")
        console.print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")

        # Offer to update .env automatically
        response = input("\n[?] Update .env file automatically? (y/n): ")
        if response.lower() == 'y':
            update_env_file(creds.token, creds.refresh_token)

    except Exception as e:
        console.print(f"\n[red]❌ Authentication failed: {e}[/red]")

def update_env_file(access_token, refresh_token):
    """Update .env file with new tokens"""
    env_file = Path(__file__).parent / '.env'

    if not env_file.exists():
        console.print("[red]❌ .env file not found[/red]")
        return

    # Read current .env
    with open(env_file, 'r') as f:
        lines = f.readlines()

    # Update tokens
    new_lines = []
    for line in lines:
        if line.startswith('GMAIL_ACCESS_TOKEN='):
            new_lines.append(f'GMAIL_ACCESS_TOKEN={access_token}\n')
        elif line.startswith('GMAIL_REFRESH_TOKEN='):
            new_lines.append(f'GMAIL_REFRESH_TOKEN={refresh_token}\n')
        else:
            new_lines.append(line)

    # Write updated .env
    with open(env_file, 'w') as f:
        f.writelines(new_lines)

    console.print("[green]✅ .env file updated successfully![/green]")

if __name__ == "__main__":
    main()

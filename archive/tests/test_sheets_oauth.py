#!/usr/bin/env python3
"""
Test Google Sheets functionality with OAuth tokens
"""
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_sheets_oauth():
    """Test Google Sheets API with OAuth credentials"""

    # Load environment variables
    load_dotenv()

    # Get OAuth credentials from .env
    client_id = os.getenv('GMAIL_CLIENT_ID')
    client_secret = os.getenv('GMAIL_CLIENT_SECRET')
    access_token = os.getenv('GMAIL_ACCESS_TOKEN')
    refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')

    console.print(Panel("[cyan]Testing Google Sheets OAuth Integration[/cyan]",
                       title="🧪 OAuth Test", border_style="cyan"))

    # Check credentials
    if not all([client_id, client_secret, access_token, refresh_token]):
        console.print("[red]❌ Missing OAuth credentials in .env file[/red]")
        return False

    console.print("[green]✅ OAuth credentials found[/green]")

    try:
        # Build credentials
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ]
        )

        console.print("[green]✅ Credentials object created[/green]")

        # Build Sheets service
        sheets_service = build('sheets', 'v4', credentials=creds)
        console.print("[green]✅ Sheets API service initialized[/green]")

        # Test 1: Create a test spreadsheet
        console.print("\n[bold cyan]Test 1: Creating test spreadsheet...[/bold cyan]")
        spreadsheet = {
            'properties': {
                'title': 'COCO OAuth Test Sheet'
            },
            'sheets': [{
                'properties': {
                    'title': 'Test Data'
                }
            }]
        }

        result = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = result['spreadsheetId']
        spreadsheet_url = result['spreadsheetUrl']

        console.print(f"[green]✅ Spreadsheet created successfully![/green]")
        console.print(f"[dim]ID: {spreadsheet_id}[/dim]")
        console.print(f"[dim]URL: {spreadsheet_url}[/dim]")

        # Test 2: Write data to spreadsheet
        console.print("\n[bold cyan]Test 2: Writing data to spreadsheet...[/bold cyan]")
        values = [
            ['Name', 'Status', 'Date'],
            ['OAuth Test', 'Success', '2025-09-30'],
            ['API Connection', 'Working', '2025-09-30'],
            ['COCO Integration', 'Ready', '2025-09-30']
        ]

        body = {'values': values}
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Test Data!A1:C4',
            valueInputOption='RAW',
            body=body
        ).execute()

        console.print("[green]✅ Data written successfully![/green]")

        # Test 3: Read data back
        console.print("\n[bold cyan]Test 3: Reading data back...[/bold cyan]")
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Test Data!A1:C4'
        ).execute()

        values = result.get('values', [])

        if values:
            table = Table(title="📊 Retrieved Data", show_header=True)
            for header in values[0]:
                table.add_column(header, style="cyan")

            for row in values[1:]:
                table.add_row(*row)

            console.print(table)
            console.print("[green]✅ Data retrieved successfully![/green]")

        # Success panel
        console.print("\n")
        console.print(Panel(
            f"[bold green]🎉 ALL TESTS PASSED![/bold green]\n\n"
            f"✅ OAuth authentication working\n"
            f"✅ Spreadsheet creation working\n"
            f"✅ Data writing working\n"
            f"✅ Data reading working\n\n"
            f"[cyan]Your test spreadsheet:[/cyan]\n"
            f"{spreadsheet_url}",
            title="✨ Google Sheets OAuth Test Results",
            border_style="green"
        ))

        return True

    except Exception as e:
        console.print(f"\n[red]❌ Test failed: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False

if __name__ == "__main__":
    test_sheets_oauth()

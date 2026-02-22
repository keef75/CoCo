from google_auth_oauthlib.flow import InstalledAppFlow

# Full Google Workspace scopes
scopes = [
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

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=scopes
)
creds = flow.run_local_server(port=8080)

print(f"\nGMAIL_ACCESS_TOKEN={creds.token}")
print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
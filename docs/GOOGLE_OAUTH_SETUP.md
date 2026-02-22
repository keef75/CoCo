# Google OAuth Setup

Complete guide to setting up Google Workspace integration (Gmail, Docs, Sheets, Drive, Calendar).

## 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** > **New Project**
3. Name it (e.g., `coco-assistant`) and click **Create**
4. Select the new project from the project dropdown

## 2. Enable APIs

Navigate to **APIs & Services > Library** and enable each:

- **Gmail API**
- **Google Docs API**
- **Google Sheets API**
- **Google Drive API**
- **Google Calendar API**

Search for each by name and click **Enable**.

## 3. Configure OAuth Consent Screen

1. Go to **APIs & Services > OAuth consent screen**
2. Select **External** user type, click **Create**
3. Fill in required fields:
   - **App name**: `CoCo Assistant` (or your preference)
   - **User support email**: your email
   - **Developer contact email**: your email
4. Click **Save and Continue**
5. On the **Scopes** page, click **Add or Remove Scopes** and add:

```
openid
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.compose
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/drive.file
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/calendar.events
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
```

6. Click **Save and Continue**
7. On **Test users**, add your Google email address, then **Save and Continue**

## 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Application type: **Desktop app**
4. Name: `CoCo Desktop` (or your preference)
5. Click **Create**
6. Click **Download JSON** -- save as `credentials.json` in your project root

## 5. Generate Tokens

Run the persistent token generator:

```bash
python scripts/oauth/get_token_persistent.py
```

This will:
1. Open your browser for Google OAuth consent
2. Ask you to authorize the requested scopes
3. Save tokens to `token.json` in the project root

CoCo automatically loads and refreshes tokens from `token.json` on every launch.

### Alternative: Manual Flow (headless environments)

If you cannot open a browser (e.g., remote server), use the OOB flow:

```bash
# Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env first
python scripts/oauth/regenerate_oauth_simple.py
```

This prints a URL to visit manually and prompts for the authorization code.

## 6. Verify Setup

```bash
python test_coco_google_workspace.py
```

All 11 Google Workspace tools should report as available.

## Troubleshooting

### "Access blocked: This app's request is invalid" (redirect URI mismatch)

Ensure your OAuth client is type **Desktop app**, not Web application. Desktop apps use `http://localhost` redirects automatically.

### "This app isn't verified" warning

Expected in testing mode. Click **Advanced > Go to CoCo Assistant (unsafe)** to proceed. This warning disappears if you publish the app.

### Tokens expire after 7 days

In **Testing** mode, Google refresh tokens expire after 7 days. To fix:
- Re-run `python scripts/oauth/get_token_persistent.py` to regenerate
- Or publish your OAuth app (moves to production mode with perpetual refresh tokens)

### 100-user limit in testing mode

Testing mode allows up to 100 test users added via the OAuth consent screen. For wider distribution, submit the app for Google verification.

### "google-api-python-client not found"

Install missing packages:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Port 8080 already in use

The token generator uses port 8080 for the redirect. If occupied, edit `get_token_persistent.py` and change the port number in `flow.run_local_server(port=XXXX)`.

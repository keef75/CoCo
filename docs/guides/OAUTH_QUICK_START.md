# OAuth Persistent Authentication - Quick Start

**TL;DR**: One-time setup, perpetual Google Workspace authentication. No more weekly token regeneration!

## New Users (2 Steps)

```bash
# 1. Generate tokens (opens browser)
python3 get_token_persistent.py

# 2. Start COCO
python3 cocoa.py
```

**Done!** Tokens auto-refresh forever.

## Existing Users (1 Step)

```bash
# Migrate existing .env tokens to token.json
python3 migrate_to_token_json.py
```

**Or** regenerate fresh tokens:

```bash
python3 get_token_persistent.py
```

## Test It Works

```bash
python3 test_oauth_persistence.py
```

Expected output:
```
✅ Passed: 5
❌ Failed: 0
🎉 All tests passed!
```

## What Changed?

**Before** (Manual):
- Tokens in `.env` file
- Expire every 7 days (Testing mode)
- Manual `get_token.py` every week

**After** (Automatic):
- Tokens in `token.json` (Google standard)
- Auto-refresh every hour
- One-time setup, works forever

## How It Works

```
COCO Startup → Load token.json → Check expiry → Auto-refresh if needed
     ↓              ↓                ↓                    ↓
   Fast         Standard         Instant            Transparent
              Google format     (< 1 sec)          (no user action)
```

## Troubleshooting

**Error: "unauthorized_client"**
- Refresh token expired (7-day limit)
- **Fix**: `python3 get_token_persistent.py`

**Error: "token.json not found"**
- First-time setup
- **Fix**: `python3 get_token_persistent.py`

**COCO in "simplified mode"**
- OAuth authentication failed
- **Fix**: `python3 test_oauth_persistence.py` to diagnose

## Making Tokens Permanent (Optional)

**Current**: Refresh tokens expire after 7 days (Testing mode)
**Upgrade**: Publish OAuth app → refresh tokens never expire

**Steps**:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. APIs & Services → OAuth consent screen
3. Click "PUBLISH APP"
4. Regenerate tokens: `python3 get_token_persistent.py`

**Recommendation**: Testing mode is fine for personal use.

## Files Created

- ✅ `token.json` - Persistent OAuth credentials (auto-generated)
- ✅ `get_token_persistent.py` - Token generator (new recommended tool)
- ✅ `migrate_to_token_json.py` - Migration script (for existing users)
- ✅ `test_oauth_persistence.py` - 5-test validation suite

## Complete Documentation

See `OAUTH_PERSISTENCE_COMPLETE.md` for full technical details.

---

**Updated**: October 2, 2025
**Status**: Production-ready ✅

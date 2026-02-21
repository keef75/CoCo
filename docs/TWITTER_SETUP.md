# Twitter (X) API Setup

Complete guide to setting up Twitter integration for posting, mentions, replies, search, and threads.

## 1. Apply for a Developer Account

1. Go to the [Twitter Developer Portal](https://developer.x.com/en/portal/dashboard)
2. Sign in with the Twitter account you want CoCo to post from
3. Apply for developer access (Free tier is sufficient)
4. Accept the Developer Agreement

## 2. Create a Project and App

1. In the Developer Portal, go to **Projects & Apps**
2. Click **Create Project**
   - Project name: `CoCo Assistant` (or your preference)
   - Use case: select the most appropriate option
3. Within the project, create an **App**
   - App name: `coco-app` (must be unique across Twitter)

## 3. Set Up User Authentication

1. In your app settings, go to **User authentication settings** > **Set up**
2. Configure:
   - **App permissions**: **Read and write** (required for posting)
   - **Type of App**: Web App, Automated App or Bot
   - **Callback URI**: `https://localhost` (not used, but required)
   - **Website URL**: any valid URL
3. Save the settings

## 4. Generate Keys and Tokens

### API Key and Secret

1. Go to your app's **Keys and tokens** tab
2. Under **Consumer Keys**, click **Regenerate** (or note existing values)
3. Save both the **API Key** and **API Key Secret**

### Bearer Token

1. Under **Authentication Tokens**, find **Bearer Token**
2. Click **Generate** and save the value

### Access Token and Secret

1. Under **Authentication Tokens**, find **Access Token and Secret**
2. Click **Generate** (ensure permissions are set to **Read and Write** first)
3. Save both the **Access Token** and **Access Token Secret**

If your access token only has read permissions, delete it, update app permissions to read+write, and regenerate.

## 5. Add to .env File

Add all five credentials to your `.env` file:

```bash
# Twitter API Credentials
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_key_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Optional configuration
TWITTER_ENABLED=true
TWITTER_MAX_POSTS_PER_DAY=17
TWITTER_MAX_TWEET_LENGTH=280
```

## 6. Verify Setup

```bash
python test_twitter_integration.py
```

This runs 7 tests covering credential loading, client initialization, and rate limiting.

## Rate Limits (Free Tier)

| Endpoint | Limit | Window |
|----------|-------|--------|
| Post tweet | 17 per 24 hours | Rolling 24h |
| Mentions | Limited | 15-minute window |
| Search | Limited | 15-minute window |

When a rate limit is hit, CoCo displays a friendly message with the reset countdown. This is normal Twitter API behavior, not a bug.

## Media Support

CoCo supports media attachments on tweets:

- **Images**: 1-4 images per tweet (JPEG, PNG, GIF, WebP)
- **Video**: 1 video per tweet (MP4)
- Images and video cannot be mixed in a single tweet

Usage within CoCo:

```
/tweet Check out this view! [attach /path/to/photo.jpg]
```

## Troubleshooting

### ConnectionResetError during posting

CoCo has built-in retry logic for transient network failures. It retries up to 3 times with exponential backoff (1s, 2s, 4s). If the error persists, check your network connection.

### "Rate limit exceeded" messages

This is expected on the Free tier. The daily limit resets on a rolling 24-hour window. CoCo tracks usage locally and displays time-until-reset. Wait for the indicated time.

### 403 Forbidden on posting

Your access token likely has read-only permissions. In the Developer Portal:
1. Go to **User authentication settings**
2. Change app permissions to **Read and write**
3. Regenerate your Access Token and Secret
4. Update `.env` with the new values

### "Could not authenticate you" (401)

Double-check all five credentials in `.env`. A common mistake is swapping the API Key with the Access Token. The mapping is:

| .env Variable | Developer Portal Label |
|---------------|----------------------|
| `TWITTER_API_KEY` | Consumer Keys > API Key |
| `TWITTER_API_SECRET` | Consumer Keys > API Key Secret |
| `TWITTER_ACCESS_TOKEN` | Authentication Tokens > Access Token |
| `TWITTER_ACCESS_SECRET` | Authentication Tokens > Access Token Secret |
| `TWITTER_BEARER_TOKEN` | Authentication Tokens > Bearer Token |

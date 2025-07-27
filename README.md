# Slack Bot (Python Version)

A Python-based Slack bot using the synchronous Slack Bolt framework that integrates with Google Gemini 2.5 Flash via OpenAI's client library.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

The main dependencies are:
- `slack-bolt>=1.18.0` - Slack Bot framework
- `openai>=1.0.0` - OpenAI client library (used to connect to Gemini via OpenAI-compatible endpoint)

2. Configure environment variables (see Configuration section below)

3. Run the bot:
```bash
python app.py
```

## Usage

### Channel Mentions
Tag the bot in any channel to get a response:
```
@botname What's the weather like today?
```

The bot will respond to mentions with Gemini-generated responses. Currently, the bot **only responds when mentioned** - it does not respond to direct messages or regular channel messages.

## Configuration

### Required Environment Variables

The following environment variables must be set:

- `SLACK_BOT_TOKEN`: Your Slack bot token (starts with `xoxb-`)
- `SLACK_APP_TOKEN`: Your Slack app token for Socket Mode (starts with `xapp-`)
- `GOOGLE_API_KEY`: Your Google API key for Gemini API access

### Optional Environment Variables

The following environment variables can be set to override defaults:

- `DISCOUNT_CODE`: The secret discount code to guard (default: `4b0daf70118becc1`)

### System Prompt

The system prompt is defined in `prompt.py` and automatically incorporates the `DISCOUNT_CODE` environment variable. To customize the prompt behavior, edit the `get_system_prompt()` function in `prompt.py`.

### Setting Environment Variables

You can set environment variables in several ways:

1. **Using a `.env` file** (create in the project root):
```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
GOOGLE_API_KEY=your-google-api-key-here
DISCOUNT_CODE=MYSECRET
```

2. **Using export commands** (Linux/macOS):
```bash
export SLACK_BOT_TOKEN=xoxb-your-bot-token-here
export SLACK_APP_TOKEN=xapp-your-app-token-here
export GOOGLE_API_KEY=your-google-api-key-here
```

3. **Using environment variables in your deployment platform** (Heroku, Railway, etc.)

## Slack App Configuration

To use this bot, you need to configure your Slack app with the following:

### OAuth Scopes
Go to api.slack.com/apps → Your App → OAuth & Permissions → Scopes and add these Bot Token Scopes:

- `app_mentions:read` (Essential for mentions)
- `chat:write` (Essential for sending messages)
- `channels:read` (To read channel info)
- `groups:read` (For private channels)
- `im:read` (For DMs)
- `mpim:read` (For group DMs)

### Event Subscriptions
Go to Event Subscriptions → Subscribe to bot events and add:

- `app_mention` (Essential! This is the only event the bot currently responds to)

## Notes

- The bot only responds to `@mentions` in channels - it does not respond to direct messages or regular channel messages
- Error handling is included for both Slack API and Gemini API failures  
- The Gemini system prompt includes a secret guarding mechanism to protect the discount code
- Uses Google's OpenAI-compatible endpoint for cleaner integration
- If required environment variables are missing, the bot will raise an error on startup

## Getting a Google API Key

To use this bot, you need a Google API key for Gemini:

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Set it as the `GOOGLE_API_KEY` environment variable

## Security Challenge

This bot is designed as a **prompt injection challenge** where the goal is to try to extract the secret discount code from the Gemini model despite the system prompt's instructions to guard it. 
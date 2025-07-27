"""
Required OAuth Scopes
Go to api.slack.com/apps → Your App → OAuth & Permissions → Scopes and add these Bot Token Scopes:

app_mentions:read    (Essential for mentions)
chat:write          (You probably have this already)
channels:read       (To read channel info)
groups:read         (For private channels)
im:read             (For DMs)
mpim:read           (For group DMs)

Enable Event Subscriptions
Go to Event Subscriptions → Subscribe to bot events and add:
app_mention         (Essential!)

Environment Variables:
SLACK_BOT_TOKEN     (Required): Bot token for Slack API access
SLACK_APP_TOKEN     (Required): App token for Socket Mode connection
GOOGLE_API_KEY      (Required): Google API key for Gemini API access (use with OpenAI-compatible endpoint)
DISCOUNT_CODE       (Optional): The secret discount code to guard (default: 4b0daf70118becc1)

System Prompt:
The system prompt is defined in prompt.py and uses the DISCOUNT_CODE environment variable.

"""
import os
import re
import asyncio
from openai import OpenAI
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from prompt import get_system_prompt

# Get environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

# Check for required environment variables
if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN environment variable is required")
if not SLACK_APP_TOKEN:
    raise ValueError("SLACK_APP_TOKEN environment variable is required")

# Optional environment variables with defaults
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required for Gemini API")

DISCOUNT_CODE = os.environ.get("DISCOUNT_CODE", "4b0daf70118becc1")

# Generate system prompt using the discount code
SYSTEM_PROMPT = get_system_prompt(DISCOUNT_CODE)

# Initialize OpenAI client for Gemini
client = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

app = AsyncApp(
    token=SLACK_BOT_TOKEN,
    process_before_response=True
)

def call_llm(prompt: str) -> str:
    """Call the Google Gemini API using OpenAI client"""
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as error:
        print(f'Error calling Gemini API: {error}')
        return 'Sorry, I could not reach the Gemini service.'

# Listen for mentions (when someone tags the bot)
@app.event("app_mention")
async def handle_mention(event, say):
    """Handle when the bot is mentioned with @botname"""
    print(f"Bot mentioned: {event['text']}")
    
    try:
        # Remove the bot mention from the text
        text = event['text']
        # The mention format is usually <@U1234567890> so we need to clean it
        cleaned_text = re.sub(r'<@[^>]+>\s*', '', text).strip()
        
        if cleaned_text:
            response = call_llm(cleaned_text)
            await say(response)
        else:
            await say("Hi! How can I help you?")
            
    except Exception as error:
        print(f'Error processing mention: {error}')
        await say('Sorry, I encountered an error processing your message.')

# Start the app
async def main():
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    print("⚡️ Bolt app is starting...")
    asyncio.run(main()) 
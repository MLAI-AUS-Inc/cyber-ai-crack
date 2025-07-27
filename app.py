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
import logging
from datetime import datetime
from openai import OpenAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from prompt import get_system_prompt

# Load environment variables from .env file
load_dotenv()

# Configure logging (console only)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

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

# Log startup configuration
logger.info("=== SLACK BOT STARTUP ===")
logger.info(f"Bot Token: {SLACK_BOT_TOKEN[:12]}..." if SLACK_BOT_TOKEN else "No Bot Token")
logger.info(f"App Token: {SLACK_APP_TOKEN[:12]}..." if SLACK_APP_TOKEN else "No App Token")
logger.info(f"Discount Code: {DISCOUNT_CODE}")
logger.info("==========================")

# Initialize OpenAI client for Gemini
client = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

app = App(token=SLACK_BOT_TOKEN)

def call_llm(prompt: str) -> str:
    """Call the Google Gemini API using OpenAI client"""
    try:
        logger.info(f"🤖 Calling Gemini API with prompt length: {len(prompt)} chars")
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        
        response_content = response.choices[0].message.content
        logger.info(f"✅ Gemini API success - Response length: {len(response_content)} chars")
        return response_content
        
    except Exception as error:
        logger.error(f'❌ Error calling Gemini API: {error}')
        return 'Sorry, I could not reach the Gemini service.'

# Listen for mentions (when someone tags the bot)
@app.event("app_mention")
def handle_mention(event, say, client):
    """Handle when the bot is mentioned with @botname"""
    
    # Extract event details
    message_ts = event.get('ts')
    channel_id = event.get('channel')
    user_id = event.get('user')
    original_text = event.get('text', '')
    
    # Get user information
    try:
        user_info = client.users_info(user=user_id)
        username = user_info['user']['name']
        display_name = user_info['user'].get('profile', {}).get('display_name', username)
        real_name = user_info['user'].get('profile', {}).get('real_name', username)
    except Exception as e:
        username = user_id
        display_name = user_id
        real_name = user_id
        logger.warning(f"Could not fetch user info for {user_id}: {e}")
    
    # Log detailed mention information
    logger.info("=== BOT MENTION RECEIVED ===")
    logger.info(f"Message ID: {message_ts}")
    logger.info(f"Channel ID: {channel_id}")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Username: @{username}")
    logger.info(f"Display Name: {display_name}")
    logger.info(f"Real Name: {real_name}")
    logger.info(f"Original Message: {original_text}")
    logger.info("=============================")
    
    try:
        # Remove the bot mention from the text
        # The mention format is usually <@U1234567890> so we need to clean it
        cleaned_text = re.sub(r'<@[^>]+>\s*', '', original_text).strip()
        
        logger.info(f"Cleaned Message: {cleaned_text}")
        
        if cleaned_text:
            logger.info("Sending to Gemini...")
            response = call_llm(cleaned_text)
            logger.info(f"Gemini Response: {response}")
            say(response)
        else:
            logger.info("Empty message, sending default greeting")
            say("Hi! How can I help you?")
            
    except Exception as error:
        logger.error(f'Error processing mention: {error}')
        say('Sorry, I encountered an error processing your message.')

# Start the app
if __name__ == "__main__":
    logger.info("⚡️ Bolt app is starting...")
    logger.info("⚡️ Initializing Slack Bot...")
    try:
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        logger.info("🚀 Starting Socket Mode connection...")
        handler.start()
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}") 
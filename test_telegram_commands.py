#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify MT5 commands in your Telegram bot
"""

import os
import sys
import logging
from dotenv import load_dotenv
import telegram

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    """Test the Telegram bot commands"""
    # Get the bot token
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in .env file")
        return
    
    print(f"Using bot token: {bot_token[:5]}...{bot_token[-5:]} with chat ID: {chat_id}")
    
    try:
        # Create the bot instance
        bot = telegram.Bot(token=bot_token)
        
        # Create a help message with all MT5 commands
        help_message = """
🤖 *MT5 Trading Commands*

Here are all the MT5 commands available in your trading bot:

/mt5connect - Connect to your MetaTrader 5 terminal
/mt5status - Check the status of your MT5 connection
/mt5positions - View your open trading positions
/mt5autotrade on - Enable automatic trading
/mt5autotrade off - Disable automatic trading
/mt5test - Place a test trade (small volume)

Try them out now!
"""
        
        # Send the message
        bot.send_message(
            chat_id=chat_id,
            text=help_message,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        
        print("✅ Command list sent to your Telegram chat")
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        
if __name__ == "__main__":
    main()
